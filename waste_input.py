from utils import normalize
import datetime

def log_waste():
    product_name = normalize(input("Which product was made "))
    try:
        quantity_made = input("How much was made: ")
        quantity_left = input("How much was left over: ")
    except ValueError:
        print("That's not a valid number, please try again")
    waste = quantity_made - quantity_left