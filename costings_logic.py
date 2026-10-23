from utils import get_unit_type, convert_to_base
from storage import load_all_products

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

def calculate_price_update(prices, product_name, price):
    if price < 0: 
        raise ValueError("Price can't be negative")
    updated_prices = dict(prices)
    updated_prices[product_name] = price
    return updated_prices

def calculate_recipe_cost(recipe, ingredients):
    cost = 0
    missing = []
    load_all_products('data/recipes.json')
    for name, quantity in recipe.items():
        if name not in ingredients: 
            missing.append(name)
            continue
        if ingredients[name]["cost_per_unit"] == None:
            missing.append(name)
            continue
        cost += quantity*ingredients[name]["cost_per_unit"]
    return cost, missing

def calculate_margin(price, cost):
    if price is None:
        return None, None
    margin = price - cost
    if price == 0:
        return margin, None
    percent = margin /price*100
    return margin, percent

def build_margin_table(products, ingredients, prices):
    table = {}
    for name, product in products.items():
        current_recipe = product.recipe_history[-1].ingredients
        cost, missing = calculate_recipe_cost(current_recipe, ingredients)
        price = prices.get(name)
        margin, percent = calculate_margin(price, cost)
        table[name] = {'price': price, 'cost': cost, 'missing': missing, 'margin': margin, 'margin_percent': percent}
    return table