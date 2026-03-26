ingredient_risks = {
    "palm oil": "High saturated fat source",
    "hydrogenated oil": "Trans fat risk",
    "ins 211": "Preservative (Sodium Benzoate)",
    "artificial color": "Artificial additive",
    "msg": "Flavor enhancer"
}

def analyze_ingredients(ingredients):

    warnings = []

    for ing in ingredients:
        for key in ingredient_risks:
            if key in ing:
                warnings.append(ingredient_risks[key])

    return warnings