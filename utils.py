def normalize(name):
    return name.strip().title()

UNIT_CONVERSION = {"kg": 1, "g": 0.001, "L": 1, "ml": 0.001, "each": 1}
def convert_to_base(quantity, unit):
    unit = unit.lower().strip()
    if unit not in UNIT_CONVERSION:
        raise ValueError(f"Unkown unit: {unit}")
    return quantity*UNIT_CONVERSION[unit]