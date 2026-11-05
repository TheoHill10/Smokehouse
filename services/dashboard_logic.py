import datetime

def calculate_total_production(production_log, date=None):
    if date is None:
        date = str(datetime.date.today())
    total = 0
    for entry in production_log:
        if entry.date == date:
            total += entry.quantity_made
    return total
    

def find_highest(summary, field):
    best_product, best_value = None, None
    for product, details in summary.items():
        if best_value is None or details[field] > best_value:
            best_product, best_value = product, details[field]
        return best_product, best_value