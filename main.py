from production_input import log_production, invoice_input, add_recipe, view_recipe_details
from storage import load_stock
from stock_logic import check_reorder_needed

while True:
    print("\n1. Log production")
    print("2. Log invoice")
    print("3. Add new recipe")
    print("4. Check reorder needed")
    print("5. Search recipe")
    print("6. Exit")

    choice = input("\nChoose an option: ")

    if choice == "1":
        log_production()
    elif choice == "2":
        invoice_input()
    elif choice == "3":
        add_recipe()
    elif choice == "4":
        stock = load_stock("data/stock.json")
        minimum_stock = load_stock("data/minimum_stock.json")
        result = check_reorder_needed(stock, minimum_stock)
        if len(result) == 0:
            print("Nothing needs to be reorder")
        else:
            for ingredient, shortfall in result.items():
                print(f"{ingredient} is below minimum stock by {shortfall}")
    elif choice == "5":
        view_recipe_details()
    elif choice == "6":
        break
    else:
        print("Not a valid option, try again")