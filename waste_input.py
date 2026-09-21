from utils import normalize
from models import WasteEntry
from storage import load_waste_log, log_change
import datetime
import json

def log_waste():
    product_name = normalize(input("Which product was made: "))
    while True:
        try:
            quantity_made = float(input("How much was made: "))
            quantity_left = float(input("How much was left over: "))
            break
        except ValueError:
            print("That's not a valid number, please try again")
    new_entry = WasteEntry(product_name, quantity_made, quantity_left, date)
    date = str(datetime.date.today())
    with open("data/waste_log.json", "r") as file:
        waste_log = json.load(file)
    waste_log.append(new_entry.to_dict())
    with open("data/waste_log.json", "w") as file:
        json.dump(waste_log, file, indent = 4)
    log_change("waste_logged", f"{quantity_left} x {product_name} wasted out of {quantity_made} made", "data/audit_log.json")
    print(f"{quantity_made} {product_name} made, {quantity_left} wasted")

def waste_summary():
    waste_log = load_waste_log()
    total_made = {}
    total_wasted = {}
    for entry in waste_log:
        product = entry.product_name
        if product in total_made:
            total_made[product] = total_made[product] + entry.quantity_made
        else:
            total_made[product] = entry.quantity_made
        if product in total_wasted:
            total_wasted[product] = total_wasted[product] + entry.quantity_left
        else:
            total_wasted[product] = entry.quantity_left
    for product, quantity_made in total_made.items():
        waste = total_wasted[product]
        if quantity_made > 0:
            waste_percent = round(((waste/quantity_made)*100), 2)
            print(f"{product}: {waste} wasted out of {total_made} made ({waste_percent}% wasted)")
        else:
            print(f"{product}: quantity of product made = 0")
    