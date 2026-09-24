def normalize(name):
    return name.strip().title()

UNIT_CONVERSION = {"kg": 1, "g": 0.001, "L": 1, "ml": 0.001, "each": 1}
def convert_to_base(quantity, unit):
    unit = unit.lower().strip()
    if unit not in UNIT_CONVERSION:
        raise ValueError(f"Unkown unit: {unit}")
    return quantity*UNIT_CONVERSION[unit]

def find_allergens(ingredient_name, allergen_keywords):
    found = []
    name_lower = ingredient_name.lower()
    for allergen, keywords in allergen_keywords.items():
        for keyword in keywords:
            if keyword in name_lower:
                found.append(allergen)
                break
    return found