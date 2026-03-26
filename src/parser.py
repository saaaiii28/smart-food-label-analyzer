import re

def extract_value(patterns, text):
    text = text.lower()
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            try:
                return float(match.group(1))
            except:
                continue
    return 0

def parse_nutrition(text):
    return {
        "sugar": extract_value([r'sugars?\D*?(\d+\.?\d*)'], text),
        "sat_fat": extract_value([r'(?:saturated|sat)\s*fat\D*?(\d+\.?\d*)'], text),
        "sodium": extract_value([r'sodium\D*?(\d+\.?\d*)'], text),
        "fiber": extract_value([r'(?:dietary\s*)?fiber\D*?(\d+\.?\d*)'], text),
        "trans_fat": extract_value([r'trans\s*fat\D*?(\d+\.?\d*)'], text),
        "additive_count": 2
    }

def extract_ingredients(text):
    match = re.search(r'ingredients?\D*?(.*)', text.lower())
    if match:
        return [i.strip() for i in match.group(1).split(",")]
    return []