def apply_rules(data):

    # Rule 1: High Sugar + High Saturated Fat
    data["rule1_high_sugar_satfat"] = (
        (data["sugar"] > 15) &
        (data["sat_fat"] > 5)
    ).astype(int)

    # Rule 2: High Sodium
    data["rule2_high_sodium"] = (
        (data["sodium"] > 500)
    ).astype(int)

    # Rule 3: Trans Fat + Sugar
    data["rule3_transfat_sugar"] = (
        (data["trans_fat"] > 0) &
        (data["sugar"] > 10)
    ).astype(int)

    # Rule 4: Low Fiber + High Sugar
    data["rule4_low_fiber_high_sugar"] = (
        (data["fiber"] < 2) &
        (data["sugar"] > 15)
    ).astype(int)

    # Rule 5: High Additives + Sugar
    data["rule5_ultra_processed"] = (
        (data["additive_count"] >= 3) &
        (data["sugar"] > 5)
    ).astype(int)

    return data
