from storage import load_all_products, load_stock, save_stock, log_change, save_all_products
from models import Product
import datetime
from utils import normalize

def log_production():
    products = load_all_products("data/recipes.json")
    stock = load_stock("data/stock.json")
    while True:
        product_name = normalize(input("Which product was made: "))
        try:
            product_object = products[product_name]
            break
        except KeyError:
            print("No product found with that name, please try again")
    while True:
        try:
            amount = int(input("How many were made: "))
            break
        except ValueError:
            print("That's not a valid number, please try again")
    ingredients_used = product_object.calculate_ingredients_used(amount)
    for ingredient, quantity in ingredients_used.items():
        if ingredient in stock:
            stock[ingredient] = stock[ingredient] - quantity
        else:
            stock[ingredient] = -quantity
    save_stock(stock, "data/stock.json")
    print(f"\nProduct made: {product_name}")
    print(f"Quantity made: {amount}")
    print(f"Ingredients used: {ingredients_used}")
    log_change("production_logged", f"{amount} x {product_name} made, stock updated", "data/audit_log.json")

def invoice_input():
    stock = load_stock("data/stock.json")
    invoice_items = {}
    while True:
        ingredient_order = normalize(input("\nIngredient delivered (or 'done' to finish): "))
        if ingredient_order.lower() == 'done':
            break
        while True:
            try:
                quantity_order = float(input(f"Quantity of {ingredient_order} delivered: "))
                break
            except ValueError:
                print("That's not a valid number, please try again")
        invoice_items[ingredient_order] = quantity_order
        print(f"You entered: {ingredient_order}: {quantity_order}")
    for ingredient, quantity in invoice_items.items():
        if ingredient in stock:
            stock[ingredient] = stock[ingredient] + quantity
        else:
            stock[ingredient] = quantity
    save_stock(stock, "data/stock.json")
    log_change("invoice_logged", f"Invoice processed: {invoice_items}", "data/audit_log.json")

def add_recipe():
    allergens = load_stock("data/allergens.json")
    products = load_all_products("data/recipes.json")
    recipe_name = input("Recipe name: ")
    recipe = {}
    flagged_allergens = []
    while True:
        recipe_ingredient = normalize(input("\nIngredient used (or 'done' to finish): "))
        if recipe_ingredient.lower() == 'done':
            break
        while True:
            try:
                recipe_quantity = float(input(f"Amount of {recipe_ingredient} used: "))
                break
            except ValueError:
                print("That's not a valid number, please try again")
        recipe[recipe_ingredient] = recipe_quantity
        if recipe_ingredient in allergens:
            flagged_allergens.append(recipe_ingredient)
            print(f"Flagged allergen: {recipe_ingredient}")
    if len(flagged_allergens) > 0:
        print(f"Contains allergens: {flagged_allergens}")
    print(f"New recipe for {recipe_name}: {recipe}")
    date_created = str(datetime.date.today())
    new_product = Product(recipe_name, recipe, date_created)
    products[recipe_name] = new_product
    save_all_products(products, "data/recipes.json")
    log_change("Recipe added", f":New recipe added: {recipe_name} - {recipe}", "data/audit_log.json")

def search_recipes():
    products = load_all_products("data/recipes.json")
    search = input("Search recipe: ").lower()
    possible_items = []
    for name in products:
        if search in name.lower():
            possible_items.append(name)
    if len(possible_items) == 0:
        print("No recipes found")
    else:
        print("Matches found:", possible_items)
    return possible_items

def view_recipe_details():
    allergens = load_stock("data/allergens.json")
    all_products = load_all_products("data/recipes.json")
    flagged_allergens = []
    matches = search_recipes()
    if len(matches) == 0:
        return
    while True:
        actual_product = input("Type the exact name of product: ")
        try:
            product_object = all_products[actual_product]
            break
        except KeyError:
            print("No product found with that name, please try again")
    current_recipe = product_object.recipe_history[-1].ingredients
    for ingredient, quantity in current_recipe.items():
        if ingredient in allergens:
            flagged_allergens.append(ingredient)
    print(f"\nCurrent recipe for {actual_product}: {current_recipe}")
    if len(flagged_allergens) > 0:
        print(f"Contains allergens: {flagged_allergens}")
    else:
        print("No allegens flagged")

