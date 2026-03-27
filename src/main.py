from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import pandas as pd

from flask_dance.contrib.google import make_google_blueprint, google

from parser import *
from ocr import *
from rules import *
from scoring import *
from ingredient import *
from model import load_model

import os

app = Flask(__name__, template_folder="../templates", static_folder="../static")
app.secret_key = "supersecretkey"
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# 🔐 GOOGLE LOGIN (SECURE VERSION)
google_bp = make_google_blueprint(
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    scope=[
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile"
    ]
)

# ✅ Safety check
if not os.getenv("GOOGLE_CLIENT_ID") or not os.getenv("GOOGLE_CLIENT_SECRET"):
    raise Exception("Google OAuth credentials not set in environment variables")

app.register_blueprint(google_bp, url_prefix="/login")

model, scaler = load_model()

from personalization import *

# LOGIN PAGE
@app.route("/login-page")
def login_page():
    return render_template("login.html")

# HOME (Redirects based on profile setup)
@app.route("/")
def home():
    if not google.authorized:
        return redirect("/login-page")

    from oauthlib.oauth2.rfc6749.errors import TokenExpiredError
    try:
        resp = google.get("/oauth2/v2/userinfo")
        user_info = resp.json()
    except TokenExpiredError:
        session.clear()
        return redirect(url_for("google.login"))

    email = user_info.get("email", "")
    if not email.endswith("@gmail.com"):
        return "Only Gmail allowed"

    session["user"] = email
    
    if "profile" not in session:
        return redirect("/profile")
    return redirect("/dashboard")

# PROFILE SETUP
@app.route("/profile")
def profile_page():
    if "user" not in session: 
        return redirect("/login-page")
    return render_template("profile.html", user=session["user"])

@app.route("/api/save-profile", methods=["POST"])
def save_profile():
    if "user" not in session: 
        return jsonify({"error": "Not logged in"})
    session["profile"] = request.json
    return jsonify({"success": True})

# DASHBOARD
@app.route("/dashboard")
def dashboard():
    if "user" not in session: 
        return redirect("/login-page")
    if "profile" not in session: 
        return redirect("/profile")
    return render_template("dashboard.html", user=session["user"])

# SINGLE PRODUCT ANALYSIS VIEW
@app.route("/single")
def single_product():
    if "user" not in session: 
        return redirect("/login-page")
    return render_template("index.html", user=session["user"])

# COMBINED PRODUCT ANALYSIS VIEW
@app.route("/compare")
def compare_page():
    if "user" not in session: 
        return redirect("/login-page")
    return render_template("compare.html", user=session["user"])

# LOGIN TRIGGER
@app.route("/login")
def login():
    return redirect(url_for("google.login"))

# LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login-page")

# STEP 1: OCR
@app.route("/extract-text", methods=["POST"])
def extract_text_api():
    if "user" not in session:
        return jsonify({"error": "Not logged in"})

    file = request.files["image"]
    file.save("temp.jpg")

    text = extract_text("temp.jpg")

    if text == "Image is too blurry":
        return jsonify({"error": "Image is too blurry"}), 400

    nutrition = parse_nutrition(text)
    ingredients = extract_ingredients(text)

    return jsonify({
        "nutrition": {
            **nutrition,
            "ingredients": ", ".join(ingredients)
        },
        "raw_text": text
    })

# STEP 2: SINGLE ANALYSIS
@app.route("/analyze-nutrition", methods=["POST"])
def analyze_nutrition():
    if "user" not in session:
        return jsonify({"error": "Not logged in"})

    data = request.json
    nutrition = data["nutrition"]

    df = pd.DataFrame([{
        "sugar": float(nutrition.get("sugar", 0)),
        "sat_fat": float(nutrition.get("sat_fat", 0)),
        "sodium": float(nutrition.get("sodium", 0)),
        "fiber": float(nutrition.get("fiber", 0)),
        "trans_fat": float(nutrition.get("trans_fat", 0)),
        "additive_count": 2
    }])

    df = apply_rules(df)
    df = calculate_scores(df)
    result = df.iloc[0]

    # ML
    X = [[
        df["sugar"][0], df["sat_fat"][0], df["sodium"][0],
        df["fiber"][0], df["trans_fat"][0]
    ]]
    X_scaled = scaler.transform(X)
    ml_prediction = model.predict(X_scaled)[0]
    ml_confidence = min(float(model.predict_proba(X_scaled)[0].max()), 0.92)

    # INGREDIENTS
    ingredients_list = [i.strip() for i in nutrition.get("ingredients", "").lower().split(",")]
    ingredient_insights = []
    for ing in ingredients_list:
        for key in ingredient_risks:
            if key in ing:
                ingredient_insights.append({
                    "ingredient": ing,
                    "risk": ingredient_risks[key]
                })

    # EXPLANATIONS
    explanations = []
    if result["rule_high_sugar_fat"]: explanations.append("High sugar + high fat combination")
    if result["rule_high_sodium"]: explanations.append("High sodium level")
    if result["rule_transfat_sugar"]: explanations.append("Trans fat + sugar risk")
    if result["rule_low_fiber_sugar"]: explanations.append("Low fiber + sugar risk")
    if not explanations: explanations.append("No major harmful interactions")

    # PERSONALIZED
    profile = session.get("profile", {})
    personalized = get_personalized_insights(nutrition, ingredients_list, profile)

    return jsonify({
        "health_score": int(result["health_score"]),
        "rule_based": result["risk_label"],
        "ml_prediction": ml_prediction,
        "ml_confidence": round(ml_confidence * 100, 2),
        "explanations": explanations,
        "ingredient_insights": ingredient_insights,
        "personalized_insights": personalized
    })

# COMBINATION ANALYSIS
@app.route("/analyze-combination", methods=["POST"])
def analyze_combination():
    if "user" not in session: 
        return jsonify({"error": "Not logged in"})
    
    data = request.json
    item_a = data.get("item_a", {})
    item_b = data.get("item_b", {})
    
    def process_item(nut):
        df = pd.DataFrame([{
            "sugar": float(nut.get("sugar", 0)),
            "sat_fat": float(nut.get("sat_fat", 0)),
            "sodium": float(nut.get("sodium", 0)),
            "fiber": float(nut.get("fiber", 0)),
            "trans_fat": float(nut.get("trans_fat", 0)),
            "additive_count": 2
        }])
        df = apply_rules(df)
        df = calculate_scores(df)
        return df.iloc[0]["risk_label"]

    verdict_a = process_item(item_a)
    verdict_b = process_item(item_b)

    combined_nut = {
        "sugar": float(item_a.get("sugar", 0)) + float(item_b.get("sugar", 0)),
        "sat_fat": float(item_a.get("sat_fat", 0)) + float(item_b.get("sat_fat", 0)),
        "sodium": float(item_a.get("sodium", 0)) + float(item_b.get("sodium", 0)),
        "fiber": float(item_a.get("fiber", 0)) + float(item_b.get("fiber", 0)),
        "trans_fat": float(item_a.get("trans_fat", 0)) + float(item_b.get("trans_fat", 0)),
        "additive_count": 4
    }
    
    df_c = pd.DataFrame([combined_nut])
    df_c = apply_rules(df_c)
    df_c = calculate_scores(df_c)
    combined_result = df_c.iloc[0]
    
    ing_a = [i.strip() for i in item_a.get("ingredients", "").lower().split(",") if i.strip()]
    ing_b = [i.strip() for i in item_b.get("ingredients", "").lower().split(",") if i.strip()]
    all_ingredients = list(set(ing_a + ing_b))

    ingredient_insights = []
    for ing in all_ingredients:
        for key in ingredient_risks:
            if key in ing:
                ingredient_insights.append({"ingredient": ing, "risk": ingredient_risks[key]})
                
    profile = session.get("profile", {})
    combo_insights = get_combination_insights(item_a, item_b, all_ingredients, profile)
    
    explanations = []
    if combined_result["rule_high_sugar_fat"]: explanations.append("High combined sugar + high fat")
    if combined_result["rule_high_sodium"]: explanations.append("High combined sodium load")
    if combined_result["rule_transfat_sugar"]: explanations.append("Trans fat + sugar risk in combination")
    if combined_result["rule_low_fiber_sugar"]: explanations.append("Low fiber + sugar risk in combination")
    if not explanations: explanations.append("No major harmful combined interactions")

    return jsonify({
        "verdict_a": verdict_a,
        "verdict_b": verdict_b,
        "combined_verdict": combined_result["risk_label"],
        "combined_score": int(combined_result["health_score"]),
        "explanations": explanations,
        "ingredient_insights": ingredient_insights,
        "personalized_insights": combo_insights
    })

if __name__ == "__main__":
    app.run(debug=True)