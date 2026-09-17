granary_recipe = {
    "Strong White Flour": 10,
    "Water": 2,
    "Yeast": 0.5,
    "Salt": 0.1,
    "Molasses": 1
}

sourdough_recipe = {
    "Strong White Flour": 10,
    "Water": 2,
    "Yeast": 0.5,
    "Salt": 0.1
}

recipes = {
    "Sourdough": sourdough_recipe,
    "Granary": granary_recipe 
}

products_made = {
    "Sourdough": 20,
    "Granary": 15
}

starting_stock = {
    "Strong White Flour": 500,
    "Water": 100000000,
    "Yeast": 20,
    "Salt": 10,
    "Molasses": 20
}

actual_stock = {
    "Strong White Flour": 550,
    "Water": 10000000,
    "Yeast": 21,
    "Salt": 10,
    "Molasses": 20
}

class RecipeVersion:
    def __init__(self, ingredients, date_created):
        self.ingredients = ingredients
        self.date_created = date_created

class Product:
    def __init__(self, name, recipe, date_created):
        self.name = name
        self.recipe_histroy = [RecipeVersion(recipe, date_created)]


    def calculate_ingredients_used(self, quantity_made):
        current_recipe = self.recipe_histroy[-1].ingredients
        total_ingredients = {}
        for ingredients, quantity in current_recipe.items():
            total_ingredients[ingredients] = quantity*quantity_made
        return total_ingredients

    def update_recipe(self, new_recipe, date_created):
        self.recipe_histroy.append(RecipeVersion(new_recipe, date_created))

sourdough = Product("Sourdough", sourdough_recipe, "26-01-01")
#granary = Product("Granary", granary_recipe)
usage_2 = sourdough.calculate_ingredients_used(20)

sourdough.update_recipe({"Strong White Flour": 15, "Water": 2, "Yeast": 1, "Salt": 0.2}, "26-03-01")
usage_3 = sourdough.calculate_ingredients_used(20)

#usage = granary.calculate_ingredients_used(15)
#print("Stock used in granary:", usage)
#print("Stock used in sourdough:", usage_2)
#print("Stock used in new sourdough:", usage_3)

def calculate_total_stock_used(products_made, recipes):
    total_stock = {}
    for product, quantity_made in products_made.items():
        recipe = recipes[product]
        for ingredient, quantity_per_item in recipe.items():
            amount = quantity_made*quantity_per_item
            if ingredient in total_stock:
                total_stock[ingredient] = total_stock[ingredient] + amount
            else:
                total_stock[ingredient] = amount
    return total_stock

used = calculate_total_stock_used(products_made, recipes)
#print("Total stock used:", used)

def calculate_theoretical_stock(starting_stock, ingredients_used):
    remaining_stock = {}
    for ingredient, quantity in starting_stock.items():
        used_amount = ingredients_used[ingredient]
        remaining_stock[ingredient] = quantity - used_amount
    return remaining_stock

left = calculate_theoretical_stock(starting_stock, used)
#print("Stock left:",left)

def calculate_stock_variance(actual_stock, theoretical_stock):
    stock_variance = {}
    for ingredients, quantity in actual_stock.items():
        theoretical_amount = theoretical_stock[ingredients]
        stock_variance[ingredients] = quantity - theoretical_amount
    return stock_variance

variance = calculate_stock_variance(actual_stock, left)
#print("Variance between actual stock and theoretical stock is:", variance)

stock_levels = {
    "Strong White Flour": 500,
    "Water": 100,
    "Yeast": 20,
    "Salt": 10
}

import json

with open("data/stock.json", "w") as file:
    json.dump(stock_levels, file, indent=4)

with open("data/stock.json", "r") as file:
    loaded_stock = json.load(file)

#print(loaded_stock)


#name = input("Enter your name: ")
#print(f"Hello, {name}")

#quanity_made = float(input("How many loaves were made? "))
#print(quanity_made*2)

from production_input import log_production
from utils import normalize
from storage import load_all_products, load_stock
#log_production()

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
    print(f"Current recipe for {actual_product}: {current_recipe}")
    if len(flagged_allergens) > 0:
        print(f"Contains allergens: {flagged_allergens}")
    else:
        print("No allegens flagged")

view_recipe_details()