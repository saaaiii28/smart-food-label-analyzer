from flask import Flask, render_template, request, jsonify
import pandas as pd
from rules import apply_rules
from scoring import calculate_scores

app = Flask(
    __name__,
    template_folder="../templates",
    static_folder="../static"
)

# ============================
# Load Dataset
# ============================
data = pd.read_csv("data/food_dataset.csv", encoding="latin1")

# Apply Rule Engine
data = apply_rules(data)

# Apply Scoring System
data = calculate_scores(data)


# ============================
# Home Route
# ============================
@app.route("/")
def home():
    products = data["food"].head(100).tolist()
    return render_template("index.html", products=products)


# ============================
# Analyze Route
# ============================
@app.route("/analyze", methods=["POST"])
def analyze():

    product_name = request.json["food"]

    product = data[data["food"] == product_name]

    if product.empty:
        return jsonify({"error": "Product not found"}), 404

    product = product.iloc[0]

    explanations = []

    # Rule 1
    if product["rule1_high_sugar_satfat"] == 1:
        explanations.append(
            "Interaction: High Sugar + High Saturated Fat may increase insulin resistance and long-term cardiovascular risk."
        )

    # Rule 2
    if product["rule2_high_sodium"] == 1:
        explanations.append(
            "Elevated Sodium levels may contribute to hypertension and increased cardiovascular strain."
        )

    # Rule 3
    if product["rule3_transfat_sugar"] == 1:
        explanations.append(
            "Trans Fat combined with Sugar significantly increases risk of metabolic imbalance and arterial inflammation."
        )

    # Rule 4
    if product["rule4_low_fiber_high_sugar"] == 1:
        explanations.append(
            "Low Fiber reduces digestive regulation, and when combined with High Sugar may cause rapid blood glucose spikes."
        )

    # Rule 5
    if product["rule5_ultra_processed"] == 1:
        explanations.append(
            "High Additive count suggests ultra-processed food profile, which is associated with long-term metabolic stress."
        )

    # If no harmful interactions
    if len(explanations) == 0:
        explanations.append(
            "No major harmful nutrient interaction patterns detected."
        )

    return jsonify({
        "health_score": int(product["health_score"]),
        "risk_label": product["risk_label"],
        "explanations": explanations
    })


# ============================
# Run App
# ============================
if __name__ == "__main__":
    app.run(debug=True)
