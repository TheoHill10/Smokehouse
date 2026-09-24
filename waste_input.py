from utils import normalize
from models import WasteEntry
from storage import load_waste_log, log_change
import datetime
import json

def calculate_waste_update(product_name, quantity_made, quantity_left, waste_log):
    date = str(datetime.date.today())  
    new_entry = WasteEntry(product_name, quantity_made, quantity_left, date)
    updated_waste_log = list(waste_log)
    updated_waste_log.append(new_entry.to_dict())
    return updated_waste_log
def log_waste():
    product_name = normalize(input("Which product was made: "))
    while True:
        try:
            quantity_made = float(input("How much was made: "))
            quantity_left = float(input("How much was left over: "))
            break
        except ValueError:
            print("That's not a valid number, please try again")
    with open("data/waste_log.json", "r") as file:
        waste_log = json.load(file)
    updated_waste_log = calculate_waste_update(product_name, quantity_made, quantity_left, waste_log)
    with open("data/waste_log.json", "w") as file:
        json.dump(updated_waste_log, file, indent = 4)
    log_change("waste_logged", f"{quantity_left} x {product_name} wasted out of {quantity_made} made", "data/audit_log.json")
    print(f"{quantity_made} {product_name} made, {quantity_left} wasted")

def calcualte_waste_summary(waste_log):
    total_made = {}
    total_wasted = {}
    for entry in waste_log:
        product = entry.product_name
        total_made[product] = total_made.get(product, 0) + entry.quantity_made
        total_wasted[product] = total_wasted.get(product, 0) + entry.quantity_left
    summary = {}
    for product, made in total_made.items():
            wasted = total_wasted[product]
            percent = round(((wasted/made)*100), 2) if made > 0 else None
            summary[product] = {"made": made, "wasted": wasted, "percent": percent}
    return summary
def waste_summary():
    waste_log = load_waste_log("data/waste_log.json")
    summary = calcualte_waste_summary(waste_log)
    for product, data in summary.items():
        if data["percent"] is not None:
            print(f"{product}: {data['wasted']} wasted out of {data['made']} made, {data['percent']}% wasted")
        else:
            print(f"{product}: quantitiy made is 0, cannot calculate percentage")