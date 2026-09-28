from flask import Flask, render_template
from storage import load_stock, load_all_products
from stock_logic import check_reorder_needed
from production_input import view_recipe_details, get_recipe_allergen

app = Flask(__name__)
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/stock")
def stock_page():
    stock = load_stock("data/stock.json")
    minimum_stock = load_stock("data/minimum_stock.json")
    reorder = check_reorder_needed(stock, minimum_stock)
    return render_template("stock.html", stock=stock, reorder=reorder)

@app.route("/recipes")
def recipes_page():
    recipes = load_all_products("data/recipes.json")
    return render_template("recipes.html", recipes=recipes)

@app.route("/recipes/<name>")
def recipe_details(name):
    recipes = load_all_products("data/recipes.json")
    allergens = load_stock("data/allergens_keywords.json")
    product_object = recipes[name]
    current_recipe = product_object.recipe_history[-1].ingredients
    allergens = get_recipe_allergen(current_recipe, allergens)
    return render_template("recipe_details.html", name=name, current_recipe=current_recipe, allergens=allergens)

if __name__ == "__main__":
    app.run(debug=True)