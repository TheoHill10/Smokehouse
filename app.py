from flask import Flask, render_template, request, redirect
from storage import load_stock, load_all_products, save_stock, log_change, load_waste_log, save_all_products
from stock_logic import check_reorder_needed
from production_input import get_recipe_allergen, calculate_invoice_update, calculate_production_update, calculate_recipe_updated
from waste_input import calculate_waste_update, calcualte_waste_summary
from utils import normalize, convert_to_base

app = Flask(__name__)
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/stock", methods=["GET", "POST"])
def stock_page():
    error = None
    if request.method == 'POST':
        try:
            ingredient = normalize(request.form["ingredient"])
            raw_quantitiy = float(request.form["quantity"])
            unit = request.form["unit"]
            quantity = convert_to_base(raw_quantitiy, unit)
            stock = load_stock("data/stock.json")
            minimum_stock = load_stock("data/minimum_stock.json")
            invoice_items = {ingredient: quantity}
            updated_stock, updated_minimum_stock = calculate_invoice_update(invoice_items, stock, minimum_stock)
            save_stock(updated_stock, "data/stock.json")
            save_stock(updated_minimum_stock, "data/minimum_stock.json")
            log_change("invoice_logged", f"Invoice processed: {invoice_items}", "data/audit_log.json")
        except ValueError:
            error = "Please enter a valid number amount"
    stock = load_stock("data/stock.json")
    minimum_stock = load_stock("data/minimum_stock.json")
    reorder = check_reorder_needed(stock, minimum_stock)
    return render_template("stock.html", stock=stock, reorder=reorder, error=error)

@app.route("/production", methods=["GET", "POST"])
def production_log():
    error = None
    if request.method == "POST":
        try:
            product_name = normalize(request.form["product_name"])
            amount = float(request.form["amount"])
            products = load_all_products("data/recipes.json")
            stock = load_stock("data/stock.json")
            product_object = products[product_name]
            ingredients_used, updated_stock = calculate_production_update(product_object, amount, stock)
            save_stock(updated_stock, "data/stock.json")
            log_change("production_logged", f"{amount} x {product_name} made, stock updated", "data/audit_log.json")
        except KeyError:
            error = "No product found with that name"
        except ValueError:
            error = "Please enter a valid number amount"
    products = load_all_products("data/recipes.json")
    return render_template("production.html", products=products, error=error)

@app.route("/waste", methods=["GET", "POST"])
def waste_log():
    error = None
    if request.method == "POST":
        try:
            product_name = normalize(request.form["product_name"])
            quantity_made = float(request.form["quantity_made"])
            quantity_left = float(request.form["quantity_left"])
            raw_waste_log = load_stock("data/waste_log.json")
            updated_waste_log = calculate_waste_update(product_name, quantity_made, quantity_left, raw_waste_log)
            save_stock(updated_waste_log, "data/waste_log.json")
            log_change("waste_logged", f"{quantity_left} x {product_name} wasted out of {quantity_made} made", "data/audit_log.json")
        except ValueError:
            error = "Please enter a valid number amount"
    waste_log = load_waste_log("data/waste_log.json")
    summary = calcualte_waste_summary(waste_log)
    return render_template("waste.html", summary=summary, error=error)

@app.route("/recipes", methods=["GET", "POST"])
def recipes_page():
    error = None
    if request.method == "POST":
        try:
            recipe_name = request.form["recipe_name"]
            ingredient_text = request.form["ingredient_text"]
            products = load_all_products("data/recipes.json")
            recipe = {}
            for line in ingredient_text.strip().split("\n"):
                parts = line.split(",")
                ingredient = normalize(parts[0])
                raw_quantity = float(parts[1])
                unit = parts[2].strip()
                recipe[ingredient] = convert_to_base(raw_quantity, unit)
            updated_products = calculate_recipe_updated(recipe_name, recipe, products)
            save_all_products(updated_products, "data/recipes.json")
            log_change("Recipe added", f":New recipe added: {recipe_name} - {recipe}", "data/audit_log.json")
            return redirect(f"/recipes/{recipe_name}")
        except (IndexError, ValueError):
            error = "Check your ingredient list is formatted as ingredient, quanity, unit. One per line"
    search = request.args.get("search","").lower()
    all_recipes = load_all_products("data/recipes.json")
    if search:
        recipes = {}
        for name, product in all_recipes.items():
            if search in name.lower():
                recipes[name] = product
    else:
        recipes = all_recipes
    return render_template("recipes.html", recipes=recipes, error=error, search=search)

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