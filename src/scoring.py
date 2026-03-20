def calculate_scores(data):

    rule_columns = [
        "rule1_high_sugar_satfat",
        "rule2_high_sodium",
        "rule3_transfat_sugar",
        "rule4_low_fiber_high_sugar",
        "rule5_ultra_processed"
    ]

    # Count triggered rules
    data["interaction_score"] = data[rule_columns].sum(axis=1)

    # Assign risk label
    def assign_risk(score):
        if score >= 3:
            return "Risky"
        elif score >= 1:
            return "Moderate"
        else:
            return "Safe"

    data["risk_label"] = data["interaction_score"].apply(assign_risk)

    # Health score (out of 100)
    data["health_score"] = 100 - (data["interaction_score"] * 15)

    # Prevent negative scores
    data["health_score"] = data["health_score"].clip(lower=0)

    return data
