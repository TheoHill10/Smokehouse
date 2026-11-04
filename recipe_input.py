import math
from utils import normalize, convert_to_base, get_unit_type

def parse_ingredient_list(items):
    if not isinstance(items, list) or not items:
        raise ValueError("Add at least one ingredient")
    recipe = {}
    ingredient_units = {}
    for item in items:
        try:
            raw_name = item["name"]
            raw_quantity = item["quantity"]
            unit = item["unit"]
        except (KeyError, TypeError):
            raise ValueError("Each ingredient needs a name, quantity and unit")
        if not isinstance(raw_name, str) or not isinstance(unit, str):
            raise ValueError("Each ingredient needs a name, quantity and unit")

        name = normalize(raw_name)
        if name == "":
            raise ValueError("Every ingredient needs a name")
        try: 
            quantity = float(raw_quantity)
        except (TypeError, ValueError):
            raise ValueError(f"Quantity for {name} must be a number")
        if not math.isfinite(quantity) or quantity <=0:
            raise ValueError(f"Quantity for {name} must be more than zero")

        unit_type = get_unit_type(unit)
        if name in ingredient_units and ingredient_units[name] !=unit_type:
            raise ValueError(f"{name} is entered in both {ingredient_units[name]} and {unit_type}")
        recipe[name] = recipe.get(name, 0) + convert_to_base(quantity, unit)
        ingredient_units[name] = unit_type
    return recipe, ingredient_units