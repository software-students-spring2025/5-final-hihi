import os
from dotenv import load_dotenv
from pymongo import MongoClient
import json
from bson import ObjectId

# Load .env into os.environ
load_dotenv()

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return super().default(o)

class RecipeDatabase:
    def __init__(self, uri: str = None):
        # 1) explicit URI argument
        # 2) or from .env: MONGO_URI
        # 3) or fall back to your old hard-coded string
        self.uri = (
            uri
            or os.environ.get("MONGO_URI")
            or "mongodb+srv://test_user:IQ2he1ZHq3mkLJNX@cluster0.cogqyqp.mongodb.net/recipe_database?retryWrites=true&w=majority"
        )
        self.client = None
        self.db = None
        self.collection = None

    def connect(self) -> bool:
        """Connect to MongoDB Atlas"""
        try:
            self.client = MongoClient(
                self.uri,
                connectTimeoutMS=30000,
                socketTimeoutMS=30000,
                retryWrites=True,
                tls=True
            )
            # Access your database and collection
            self.db = self.client["recipe_database"]
            self.collection = self.db["recipes"]

            # Test connection by getting a count
            count = self.collection.count_documents({})
            print(f"Successfully connected! Found {count} recipes in the database.")
            return True

        except Exception as e:
            print(f"Error connecting to MongoDB Atlas: {e}")
            return False

    def close(self):
        """Close the MongoDB connection"""
        if self.client:
            self.client.close()
            print("Connection closed.")

    def find_recipe_by_id(self, recipe_id):
        """Find a recipe by its ObjectId"""
        try:
            if isinstance(recipe_id, str):
                recipe_id = ObjectId(recipe_id)
            return self.collection.find_one({"_id": recipe_id})
        except Exception as e:
            print(f"Error finding recipe: {e}")
            return None

    def find_recipes(self, query: dict = {}, limit: int = 10):
        """Find recipes matching the query"""
        try:
            return list(self.collection.find(query).limit(limit))
        except Exception as e:
            print(f"Error finding recipes: {e}")
            return []

    def get_sample_recipes(self, count: int = 5):
        """Get a random sample of recipes"""
        try:
            pipeline = [{"$sample": {"size": count}}]
            return list(self.collection.aggregate(pipeline))
        except Exception as e:
            print(f"Error getting sample recipes: {e}")
            return []

    def search_recipes_by_name(self, name_query: str, limit: int = 10):
        """Case-insensitive name search"""
        try:
            query = {"name": {"$regex": name_query, "$options": "i"}}
            return list(self.collection.find(query).limit(limit))
        except Exception as e:
            print(f"Error searching recipes: {e}")
            return []

    def find_recipes_by_tags(self, tags: list, limit: int = 10):
        """Find recipes containing *all* specified tags"""
        try:
            query = {"tags": {"$all": tags}}
            return list(self.collection.find(query).limit(limit))
        except Exception as e:
            print(f"Error finding recipes by tags: {e}")
            return []

    def find_recipes_by_ingredients(self, ingredients: list, limit: int = 10):
        """Find recipes containing *all* specified ingredients"""
        try:
            patterns = [
                {"ingredients": {"$regex": ingr, "$options": "i"}}
                for ingr in ingredients
            ]
            query = {"$and": patterns}
            return list(self.collection.find(query).limit(limit))
        except Exception as e:
            print(f"Error finding recipes by ingredients: {e}")
            return []

    def pretty_print_recipe(self, recipe: dict):
        """Console-print a recipe nicely"""
        if not recipe:
            print("No recipe found.")
            return
        print("\n" + "="*40)
        print(f"Recipe: {recipe.get('name','')}")
        print("="*40)
        print(f"Cooking Time: {recipe.get('minutes','')} minutes")
        print(f"\nDescription: {recipe.get('description','')}")
        print("\nIngredients:")
        for i, ing in enumerate(recipe.get('ingredients',[]),1):
            print(f"  {i}. {ing}")
        print("\nSteps:")
        for i, step in enumerate(recipe.get('steps',[]),1):
            print(f"  {i}. {step}")
        print("\nNutrition:")
        for k,v in recipe.get('nutrition',{}).items():
            print(f"  {k.replace('_',' ').title()}: {v}")
        print(f"\nTags: {', '.join(recipe.get('tags',[]))}")
        print("="*40 + "\n")

    def to_json(self, data):
        """Convert MongoDB data to JSON-safe string"""
        return json.dumps(data, cls=JSONEncoder, indent=2)


# Example usage when run directly
if __name__ == "__main__":
    db = RecipeDatabase()
    if db.connect():
        samples = db.get_sample_recipes(3)
        print(f"Found {len(samples)} sample recipes.")
        if samples:
            db.pretty_print_recipe(samples[0])
        db.close()
