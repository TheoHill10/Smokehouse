import json
import datetime
from models import Product, AuditEntry, WasteEntry

def save_stock(stock_levels, filepath):
    with open(filepath, "w") as file:
        json.dump(stock_levels, file, indent=4)

def load_stock(filepath):
    with open(filepath, "r") as file:
        return json.load(file)

def save_all_products(products, filepath):
    all_products_data = {}
    for name, product in products.items():
        all_products_data[name] = product.to_dict()
    with open(filepath, "w") as file:
        json.dump(all_products_data, file, indent = 4)

def load_all_products(filepath):
    with open(filepath, "r") as file:
        raw_data = json.load(file)
    products = {}
    for name, product_data in raw_data.items():
        products[name] = Product.from_dict(product_data)
    return products

def log_change(action, details, filepath, date=None):
    if date is None:
        date = str(datetime.date.today())
    with open(filepath, "r") as file:
        audit_log = json.load(file)
    new_entry = AuditEntry(action, details, date)
    audit_log.append(new_entry.to_dict())
    with open(filepath, "w") as file:
        json.dump(audit_log, file, indent = 4)

def load_audit_log(filepath):
    with open(filepath, "r") as file:
        raw = json.load(file)
    entries = []
    for entry_data in raw:
        entries.append(AuditEntry.from_dict(entry_data))
    return entries

def load_waste_log(filepath):
    with open(filepath, "r") as file:
        raw = json.load(file)
    entries = []
    for entry_data in raw:
        entries.append(WasteEntry.from_dict(entry_data))
    return entries