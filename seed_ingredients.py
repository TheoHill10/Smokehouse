from storage import load_stock, load_all_products, save_stock

names = set()
stock = load_stock("data/stock.json")
for ingredient in stock:
    names.add(ingredient)

recipes = load_all_products("data/recipes.json")
for product in recipes.values():
    for ingredient in product.recipe_history[-1].ingredients:
        names.add(ingredient)

registry = load_stock('data/ingredients.json')
for name in sorted(names):
    if name not in registry:
        registry[name] = {"unit": None, "cost_per_unit": None}
        print ("Added:", name)

save_stock(registry, "data/ingredients.json")
