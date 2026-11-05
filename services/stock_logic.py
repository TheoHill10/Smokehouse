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

def calculate_theoretical_stock(starting_stock, ingredients_used):
    remaining_stock = {}
    for ingredient, quantity in starting_stock.items():
        used_amount = ingredients_used[ingredient]
        remaining_stock[ingredient] = quantity - used_amount
    return remaining_stock

def calculate_stock_variance(actual_stock, theoretical_stock):
    stock_variance = {}
    for ingredients, quantity in actual_stock.items():
        theoretical_amount = theoretical_stock[ingredients]
        stock_variance[ingredients] = quantity - theoretical_amount
    return stock_variance

def check_reorder_needed(stock, minimum_stock):
    below_minimum = {}
    for ingredient, quantity in stock.items():
        if ingredient not in minimum_stock:
            continue
        minimum = minimum_stock[ingredient]
        if quantity < minimum:
            below_minimum[ingredient] = minimum - quantity
    return below_minimum
