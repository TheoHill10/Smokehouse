from flask import Flask, render_template, request, redirect
import datetime
from storage import load_stock, load_all_products, save_stock, log_change, load_waste_log, save_all_products, load_production_log
from stock_logic import check_reorder_needed
from production_input import get_recipe_allergen, calculate_invoice_update, calculate_production_update, calculate_recipe_updated, calculate_production_log_entry
from waste_input import calculate_waste_update, calculate_waste_summary, calculate_todays_production, calculate_todays_unit_values
from utils import normalize, convert_to_base, recipe_to_text
from dashboard_logic import find_highest, calculate_total_production
from costings_logic import calculate_cost_update, build_margin_table, calculate_price_update, calculate_recipe_cost


app = Flask(__name__)
@app.route("/")
def home():
    stock = load_stock("data/stock.json")
    minimum_stock = load_stock("data/minimum_stock.json")
    reorder = check_reorder_needed(stock, minimum_stock)
    recipes = load_all_products("data/recipes.json")
    production_log = load_production_log("data/production_log.json")
    waste_log = load_waste_log("data/waste_log.json")
    today = str(datetime.date.today())
    today_production_total = calculate_total_production(production_log, today)
    today_waste_summary = calculate_waste_summary(waste_log, start_date=today, end_date=today)
    total_made_today, total_wasted_today = 0, 0
    for details in today_waste_summary.values():
        total_made_today += details["made"]
        total_wasted_today += details["wasted"]
    waste_percent_today = round((total_wasted_today / total_made_today) * 100, 2) if total_made_today > 0 else None
    all_time_waste_summary = calculate_waste_summary(waste_log)
    most_wasted_product, most_wasted_value = find_highest(all_time_waste_summary, "wasted")
    stock_preview = dict(list(stock.items())[:5])
    return render_template("dashboard.html", reorder_count=len(reorder), recipe_count=len(recipes), today_production_total=today_production_total, waste_percent_today=waste_percent_today, stock_preview=stock_preview, most_wasted_product=most_wasted_product, most_wasted_value=most_wasted_value)

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
            registry = load_stock("data/ingredients.json")
            prices = load_stock("data/prices.json")
            recipe = product_object.recipe_history[-1].ingredients
            unit_cost, missing_costs = calculate_recipe_cost(recipe, registry)
            unit_price = prices.get(product_name)
            raw_production_log = load_stock("data/production_log.json")
            updated_production_log = calculate_production_log_entry(product_name, amount, raw_production_log, unit_cost=unit_cost, unit_price=unit_price, missing_costs=missing_costs)
            save_stock(updated_stock, "data/stock.json")
            save_stock(updated_production_log, "data/production_log.json")
            log_change("production_logged", f"{amount} x {product_name} made, stock updated", "data/audit_log.json")
        except KeyError:
            error = "No product found with that name"
        except ValueError:
            error = "Please enter a valid number amount"
    products = load_all_products("data/recipes.json")
    return render_template("production.html", product_name=sorted(products), error=error)

@app.route("/waste", methods=["GET", "POST"])
def waste_log():
    error = None
    products = load_all_products("data/recipes.json")
    if request.method == "POST":
        try:
            product_name = normalize(request.form["product_name"])
            if product_name not in products:
                raise KeyError
            quantity_left = float(request.form["quantity_left"])
            production_log = load_production_log("data/production_log.json")
            todays_production, found = calculate_todays_production(product_name, production_log)
            if not found: 
                error = "No production logged for this product today - log production first"
            else:
                unit_cost, unit_price = calculate_todays_unit_values(product_name, production_log)
                raw_waste_log = load_stock("data/waste_log.json")
                updated_waste_log = calculate_waste_update(product_name, todays_production, quantity_left, raw_waste_log, unit_cost=unit_cost, unit_price=unit_price)
                save_stock(updated_waste_log, "data/waste_log.json")
                log_change("waste_logged", f"{quantity_left} x {product_name} wasted out of {todays_production} made", "data/audit_log.json")
        except KeyError:
            error = "No product found with that name"
        except ValueError:
            error = "Please enter a valid number amount"
    waste_log = load_waste_log("data/waste_log.json")
    today = str(datetime.date.today())
    summary_all_time = calculate_waste_summary(waste_log)
    summary_today = calculate_waste_summary(waste_log, start_date=today, end_date=today)
    return render_template("waste.html", product_name=sorted(products), summary_today=summary_today, summary_all_time=summary_all_time, error=error)

@app.route("/recipes", methods=["GET", "POST"])
def recipes_page():
    error = None
    if request.method == "POST":
        try:
            recipe_name = request.form["recipe_name"]
            ingredient_text = request.form["ingredient_text"]
            products = load_all_products("data/recipes.json")
            minimum_stock = load_stock("data/minimum_stock.json")
            recipe = {}
            for line in ingredient_text.strip().split("\n"):
                parts = line.split(",")
                ingredient = normalize(parts[0])
                raw_quantity = float(parts[1])
                unit = parts[2].strip()
                recipe[ingredient] = convert_to_base(raw_quantity, unit)
            updated_products, updated_minimum_stock = calculate_recipe_updated(recipe_name, recipe, products, minimum_stock)
            price_text = request.form["price"].strip()
            updated_prices = None
            if price_text:
                price = float(price_text)
                prices = load_stock("data/prices.json")
                updated_prices = calculate_price_update(prices, recipe_name, price)
            save_all_products(updated_products, "data/recipes.json")
            save_stock(updated_minimum_stock, "data/minimum_stock.json")
            if updated_prices is not None:
                save_stock(updated_prices, "data/prices.json")
            log_change("Recipe added", f":New recipe added: {recipe_name} - {recipe}", "data/audit_log.json")
            return redirect(f"/recipes/{recipe_name}")
        except (IndexError, ValueError):
            error = "Check your ingredient list is formatted as ingredient, quanity, unit. One per line"
    search = request.args.get("search","").lower()
    all_recipes = load_all_products("data/recipes.json")
    return render_template("recipes.html", recipe_names=sorted(all_recipes), error=error, search=search)

@app.route("/recipes/<name>")
def recipe_details(name):
    recipes = load_all_products("data/recipes.json")
    allergens = load_stock("data/allergens_keywords.json")
    prices = load_stock("data/prices.json")
    price=prices.get(name)
    product_object = recipes[name]
    current_recipe = product_object.recipe_history[-1].ingredients
    allergens = get_recipe_allergen(current_recipe, allergens)
    return render_template("recipe_details.html", name=name, current_recipe=current_recipe, allergens=allergens, price=price)

@app.route("/recipes/<name>/update", methods=["GET", "POST"])
def update_recipes_page(name):
    error = None
    products = load_all_products("data/recipes.json")
    product_object = products[name]
    prices = load_stock('data/prices.json')
    if request.method == "POST":
        try:
            ingredient_text = request.form["ingredient_text"]
            recipe = {}
            for line in ingredient_text.strip().split("\n"):
                parts = line.split(",")
                ingredient = normalize(parts[0])
                raw_quantity = float(parts[1])
                unit = parts[2].strip()
                recipe[ingredient] = convert_to_base(raw_quantity, unit)
            current_recipe = product_object.recipe_history[-1].ingredients
            if recipe != current_recipe:
                date = str(datetime.date.today())
                product_object.update_recipe(recipe, date)
                products[name] = product_object
                save_all_products(products, "data/recipes.json")
            price_text = request.form['price'].strip()
            if price_text:
                price = float(price_text)
                updated_prices = calculate_price_update(prices, name, price)
                save_stock(updated_prices, "data/prices.json")
                prices = updated_prices
            log_change("Recipe added", f":Recipe updated: {name} recipe updated - {recipe}", "data/audit_log.json")
            return redirect(f"/recipes/{name}")
        except (IndexError, ValueError):
            error = "Check your ingredient list is formatted as ingredient, quanity, unit. One per line"
    current_recipe = product_object.recipe_history[-1].ingredients
    prefill_text = recipe_to_text(current_recipe)
    return render_template("update_recipes.html", name=name, prefill_text=prefill_text, price=prices.get(name), error=error)

@app.route("/costings", methods=["GET", "POST"])
def costings_page():
    error = None
    ingredients = load_stock("data/ingredients.json")
    if request.method == 'POST':
        try:
            name = normalize(request.form["ingredient"])
            if name not in ingredients:
                raise ValueError(f"'{name}' isn't a known ingredient - pick one from the list")
            price = float(request.form["price"])
            quantitiy = float(request.form["quantity"])
            unit = request.form["unit"]
            ingredients = calculate_cost_update(ingredients, name, price, quantitiy, unit)
            save_stock(ingredients, "data/ingredients.json")
            record = ingredients[name]
            log_change("cost_updated", f"{name} set to £{record['cost_per_unit']:.3f} per {record['unit']}", "data/audit_log.json")
        except ValueError as e:
            error = str(e)
    products = load_all_products('data/recipes.json')
    prices = load_stock('data/prices.json')
    margins = build_margin_table(products, ingredients, prices)
    return render_template("costings.html", ingredients=ingredients, ingredient_names =sorted(ingredients), margins=margins, error=error)


if __name__ == "__main__":
    app.run(debug=True)