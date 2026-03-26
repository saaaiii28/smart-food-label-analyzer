def apply_rules(data):

    data["rule_high_sugar_fat"] = ((data["sugar"] > 15) & (data["sat_fat"] > 5)).astype(int)

    data["rule_high_sodium"] = (data["sodium"] > 500).astype(int)

    data["rule_transfat_sugar"] = ((data["trans_fat"] > 0) & (data["sugar"] > 10)).astype(int)

    data["rule_low_fiber_sugar"] = ((data["fiber"] < 2) & (data["sugar"] > 10)).astype(int)

    return data