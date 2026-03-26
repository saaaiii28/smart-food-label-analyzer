def calculate_scores(data):

    rule_cols = [
        "rule_high_sugar_fat",
        "rule_high_sodium",
        "rule_transfat_sugar",
        "rule_low_fiber_sugar"
    ]

    data["interaction_score"] = data[rule_cols].sum(axis=1)

    def assign_label(score):
        if score >= 3:
            return "Risky"
        elif score >= 1:
            return "Moderate"
        else:
            return "Safe"

    data["risk_label"] = data["interaction_score"].apply(assign_label)

    def map_score(label):
        if label == "Safe":
            return 90
        elif label == "Moderate":
            return 65
        else:
            return 40

    data["health_score"] = data["risk_label"].apply(map_score)

    return data