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
    text = text.lower()
    
    def get_val(keywords, text):
        fuzzy_map = {
            's': '[s5]', 'o': '[o0]', 'i': '[i1l|]', 'l': '[l1i|]', 
            'g': '[gq9]', 'a': '[a4]', 't': '[t7]', 'b': '[b66]', 'e': '[e3]'
        }
        
        for kw in keywords:
            fuzzy_kw = "".join(fuzzy_map.get(c, c) for c in kw)
            # Include € and b in the numeric capture group so we can convert them to 6
            pattern = rf'{fuzzy_kw}[^\d]*?([€b]?\d+)'
            match = re.search(pattern, text)
            
            if match:
                val_str = match.group(1).replace('€', '6').replace('b', '6').replace('o', '0')
                
                if len(val_str) >= 2:
                    # Strip misread units or %DV from the end
                    if val_str.endswith(('39', '49', '38', '48', '98', '88', '28')): 
                        if len(val_str) > 2: val_str = val_str[:-2]
                        else: val_str = val_str[:-1]
                    
                    # Further cleanup for g/mg misreads at the end
                    if val_str[-1] in '936' and len(val_str) > 1:
                        if not any(k in kw for k in ['sodium', 'sodiu', 'calor']):
                            val_str = val_str[:-1]
                
                try:
                    val = float(val_str)
                    # Safety: Fiber and Sugar are rarely > 100 in a serving
                    if any(k in kw for k in ['fiber', 'fibr', 'sugar', 'suqar']) and val > 60:
                        # Grab first digit (e.g. 6080 -> 6.0)
                        return float(str(int(val))[0])
                    return val
                except: continue
        return 0

    return {
        "calories": get_val(['calories', 'calor', 'cor'], text),
        "sugar": get_val(['sugar', 'suqar', 'sugr', 'suzar'], text),
        "sat_fat": get_val(['saturated fat', 'sat fat', 'safura', 'saturu', 'saiuru', 'saiur'], text),
        "sodium": get_val(['sodium', 'sodiu', 'sodiun', '5odlum'], text),
        "fiber": get_val(['dietary fiber', 'fiber', 'fibre', 'fibr', 'oio1nyy', 'oiolnyy'], text),
        "trans_fat": get_val(['trans fat', 'tran fat', '1rans fat', 'f7o', 'fto', 'f10', 'ft0'], text),
        "total_fat": get_val(['total fat', 'lotal fat', 'f0t'], text),
        "additive_count": 2
    }

def extract_ingredients(text):
    text = text.lower().replace('|', 'i').replace('0', 'o')
    markers = ['ingredients:', 'ingredients', 'ingredienls', '1ngredients', 'inqredients', 'in6redients', 'ingreoients']
    for marker in markers:
        if marker in text:
            start = text.find(marker) + len(marker)
            rest = text[start:]
            # Stop if we see a nutrient word followed by a number
            nutrients = ['total fat', 'sodium', 'sugar', 'protein', 'calories', 'sodlum', 'suqar']
            end_pos = len(rest)
            for nut in nutrients:
                m = re.search(rf'{nut}\D*?\d+', rest)
                if m and m.start() < end_pos:
                    end_pos = m.start()
            
            end_markers = ['nutrition facts', 'distributed by', 'contains:', 'warnings:']
            for em in end_markers:
                idx = rest.find(em)
                if idx != -1 and idx < end_pos:
                    end_pos = idx
            
            blob = rest[0:end_pos].strip()
            if ',' in blob:
                return [i.strip() for i in blob.split(",") if len(i.strip()) > 1]
            else:
                return [i.strip() for i in blob.split()[:20] if len(i.strip()) > 2]
    return []