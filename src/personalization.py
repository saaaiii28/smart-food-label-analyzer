def get_personalized_insights(nutrition, ingredients, profile):
    insights = []
    conditions = profile.get("conditions", [])
    goal = profile.get("goal", "")
    diet = profile.get("diet", "")

    sugar = float(nutrition.get("sugar", 0))
    sat_fat = float(nutrition.get("sat_fat", 0))
    sodium = float(nutrition.get("sodium", 0))
    trans_fat = float(nutrition.get("trans_fat", 0))

    if "Diabetes" in conditions and sugar > 10:
        insights.append("Not suitable for diabetes (high sugar)")
    if "Heart Disease" in conditions and (sat_fat > 5 or trans_fat > 0):
        insights.append("Risky for heart patients (high fat)")
    if "Hypertension" in conditions and sodium > 300:
        insights.append("High sodium not recommended for hypertension")

    if goal == "Weight Loss" and (sugar > 15 or sat_fat > 5):
        insights.append("Not ideal for weight loss (high sugar/fat)")
    
    non_veg_keywords = ["chicken", "beef", "pork", "meat", "fish", "gelatin", "egg"]
    dairy_keywords = ["milk", "cheese", "butter", "whey", "lactose"]
    
    ingredients_text = " ".join(ingredients).lower()
    has_meat = any(w in ingredients_text for w in non_veg_keywords)
    has_dairy = any(w in ingredients_text for w in dairy_keywords)

    if diet == "Vegetarian" and has_meat:
        insights.append("Warning: Contains non-vegetarian ingredients")
    if diet == "Vegan" and (has_meat or has_dairy):
        insights.append("Warning: Contains non-vegan ingredients")

    if not insights:
        insights.append("Aligns well with your health profile")

    return insights

def get_combination_insights(nut_a, nut_b, all_ingredients, profile):
    combined = {
        "sugar": float(nut_a.get("sugar", 0)) + float(nut_b.get("sugar", 0)),
        "sat_fat": float(nut_a.get("sat_fat", 0)) + float(nut_b.get("sat_fat", 0)),
        "sodium": float(nut_a.get("sodium", 0)) + float(nut_b.get("sodium", 0)),
        "trans_fat": float(nut_a.get("trans_fat", 0)) + float(nut_b.get("trans_fat", 0))
    }
    
    insights = []
    conditions = profile.get("conditions", [])
    goal = profile.get("goal", "")
    diet = profile.get("diet", "")

    if "Diabetes" in conditions and combined["sugar"] > 20:
        insights.append("Not suitable for diabetes (very high combined sugar)")
    if "Heart Disease" in conditions and (combined["sat_fat"] > 10 or combined["trans_fat"] > 0):
        insights.append("Risky for heart patients (high fat combination)")
    if "Hypertension" in conditions and combined["sodium"] > 600:
        insights.append("Dangerous sodium load for hypertension")

    if goal == "Weight Loss" and (combined["sugar"] > 25 or combined["sat_fat"] > 10):
        insights.append("Not ideal for weight loss")

    non_veg_keywords = ["chicken", "beef", "pork", "meat", "fish", "gelatin", "egg"]
    dairy_keywords = ["milk", "cheese", "butter", "whey", "lactose"]
    
    ingredients_text = " ".join(all_ingredients).lower()
    has_meat = any(w in ingredients_text for w in non_veg_keywords)
    has_dairy = any(w in ingredients_text for w in dairy_keywords)

    if diet == "Vegetarian" and has_meat:
        insights.append("Warning: Combination contains non-vegetarian ingredients")
    if diet == "Vegan" and (has_meat or has_dairy):
        insights.append("Warning: Combination contains non-vegan ingredients")

    if not insights:
        insights.append("This combination is generally safe for your profile")

    return insights