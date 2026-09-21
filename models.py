class RecipeVersion:
    def __init__(self, ingredients, date_created):
        self.ingredients = ingredients
        self.date_created = date_created

    def to_dict(self):
        return {
            "ingredients": self.ingredients,
            "date_created": self.date_created
        }

    @staticmethod
    def from_dict(data):
        return RecipeVersion(data["ingredients"], data["date_created"])

class Product:
    def __init__(self, name, recipe, date_created):
        self.name = name
        self.recipe_history = [RecipeVersion(recipe, date_created)]

    def calculate_ingredients_used(self, quantity_made):
        current_recipe = self.recipe_history[-1].ingredients
        total_ingredients = {}
        for ingredients, quantity in current_recipe.items():
            total_ingredients[ingredients] = quantity*quantity_made
        return total_ingredients

    def update_recipe(self, new_recipe, date_created):
        self.recipe_history.append(RecipeVersion(new_recipe, date_created))

    def to_dict(self):
        return {
            "name": self.name,
            "recipe_history": [version.to_dict() for version in self.recipe_history]
        }

    @staticmethod
    def from_dict(data):
        first_version = data["recipe_history"][0]
        product = Product(data["name"], first_version["ingredients"], first_version["date_created"])
        product.recipe_history = [RecipeVersion.from_dict(v) for v in data["recipe_history"]]
        return product

class AuditEntry:
    def __init__(self, action, details, date):
        self.action = action
        self.details = details
        self.date = date

    def to_dict(self):
        return {
            "action": self.action,
            "details": self.details,
            "date": self.date
        }

    @staticmethod
    def from_dict(data):
        return AuditEntry(data["action"], data["details"], data["date"])

class WasteEntry:
    def __init__(self, product_name, quantity_made, quantity_left, date):
        self.product_name = product_name
        self.quantity_made = quantity_made
        self.quantity_left = quantity_left
        self.date = date

    def to_dict(self):
        return {
            "product_name": self.product_name,
            "quantity_made": self.quantity_made,
            "quantity_left": self.quantity_left,
            "date": self.date
        }

    @staticmethod
    def from_dict(data):
        return WasteEntry(data["product_name"], data["quantity_made"], data["quantity_left"], data["date"])