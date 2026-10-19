from utils import get_unit_type, convert_to_base

def calculate_cost_update(ingredients, name, price, quantity, unit):
    if quantity <=0:
        raise ValueError("Quantitiy muts be more than zero")
    if price < 0: 
        raise ValueError("Price can't be negative")
    
    unit_type = get_unit_type(unit)
    existing = ingredients.get(name)
    if existing is not None and existing["unit"] is not None and existing["unit"] != unit_type:
        raise ValueError(f"{name} is tracked in {existing['unit']}, but you entered {unit_type}")
    cost_per_unit = price / convert_to_base(quantity, unit)
    updated = dict(ingredients)
    updated[name] = {"unit": unit_type, "cost_per_unit": cost_per_unit}
    return updated