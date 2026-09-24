from storage import load_all_products, load_stock, save_stock, log_change, save_all_products
from models import Product
import datetime
from utils import normalize, convert_to_base, find_allergens

def calculate_production_update(product_object, amount, stock):
    ingredients_used = product_object.calculate_ingredients_used(amount)
    updated_stock = dict(stock)
    for ingredients, quantity in ingredients_used.items():
        if ingredients in updated_stock:
            updated_stock[ingredients] = updated_stock[ingredients] - quantity
        else:
            updated_stock[ingredients] = -quantity
    return ingredients_used, updated_stock
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
    ingredients_used, updated_stock = calculate_production_update(product_object, amount, stock)
    save_stock(updated_stock, "data/stock.json")
    print(f"\nProduct made: {product_name}, Quantity made: {amount}")
    print(f"Ingredients used: {ingredients_used}")
    log_change("production_logged", f"{amount} x {product_name} made, stock updated", "data/audit_log.json")

def calculate_invoice_update(invoice_items, stock, minimum_stock):
    updated_stock = dict(stock)
    updated_minimum_stock = dict(minimum_stock)
    for ingredient, quantity in invoice_items.items():
        if ingredient in updated_stock:
            updated_stock[ingredient] = updated_stock[ingredient] + quantity
        else:
            updated_stock[ingredient] = quantity
        if ingredient not in updated_minimum_stock:
            updated_minimum_stock[ingredient] = 0
    return updated_stock, updated_minimum_stock
def invoice_input():
    stock = load_stock("data/stock.json")
    minimum_stock = load_stock("data/minimum_stock.json")
    invoice_items = {}
    while True:
        ingredient_order = normalize(input("\nIngredient delivered (or 'done' to finish): "))
        if ingredient_order.lower() == 'done':
            break
        while True:
            try:
                raw_quantity = float(input(f"Quantity of {ingredient_order} delivered: "))
                unit = input("Unit (kg/g/L/ml/each): ")
                quantity_order = convert_to_base(raw_quantity, unit)
                break
            except ValueError as error:
                print(f"Invalid entry ({error}), please try again")
        invoice_items[ingredient_order] = quantity_order
        print(f"You entered: {ingredient_order}: {quantity_order}")
    updated_stock, updated_minimum_stock = calculate_invoice_update(invoice_items, stock, minimum_stock)
    save_stock(updated_stock, "data/stock.json")
    save_stock(updated_minimum_stock, "data/minimum_stock.json")
    log_change("invoice_logged", f"Invoice processed: {invoice_items}", "data/audit_log.json")

def calculate_recipe_updated(recipe_name, recipe, products, minimum_stock):
    updated_products = dict(products)
    updated_minimum_stock = dict(minimum_stock)
    date_created = str(datetime.date.today())
    new_product = Product(recipe_name, recipe, date_created)
    updated_products[recipe_name] = new_product
    for ingredient in recipe:
        if ingredient not in updated_minimum_stock:
            updated_minimum_stock[ingredient] = 0
    return updated_products, updated_minimum_stock
def get_recipe_allergen(recipe, allergen_keywords):
    flagged = []
    for ingredient in recipe:
        for allergen in find_allergens(ingredient, allergen_keywords):
            if allergen not in flagged:
                flagged.append(allergen)
    return flagged
def add_recipe():
    allergens_keywords = load_stock("data/allergens_keywords.json")
    products = load_all_products("data/recipes.json")
    minimum_stock = load_stock("data/minimum_stock.json")
    recipe_name = input("Recipe name: ")
    recipe = {}
    while True:
        recipe_ingredient = normalize(input("\nIngredient used (or 'done' to finish): "))
        if recipe_ingredient.lower() == 'done':
            break
        while True:
            try:
                raw_quantity = float(input(f"Amount of {recipe_ingredient} used: "))
                unit = input("Unit (kg/g/L/ml/each): ")
                recipe_quantity = convert_to_base(raw_quantity, unit)
                break
            except ValueError:
                print("That's not a valid number, please try again")
        recipe[recipe_ingredient] = recipe_quantity
    flagged_allergens = get_recipe_allergen(recipe, allergens_keywords)
    print(f"New recipe for {recipe_name}: {recipe}")
    if len(flagged_allergens) > 0:
        print(f"Contains allergens: {flagged_allergens}")
    updated_products, updated_minimum_stock = calculate_recipe_updated(recipe_name, recipe, products, minimum_stock)
    save_stock(updated_minimum_stock, "data/minimum_stock.json")
    save_all_products(updated_products, "data/recipes.json")
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
    allergens = load_stock("data/allergens_keywords.json")
    all_products = load_all_products("data/recipes.json")
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
    flagged_allergens = get_recipe_allergen(current_recipe, allergens)
    print(f"\nCurrent recipe for {actual_product}: {current_recipe}")
    if len(flagged_allergens) > 0:
        print(f"Contains allergens: {flagged_allergens}")
    else:
        print("No allegens flagged")

