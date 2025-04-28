from mongo_connection import RecipeDatabase

def test_recipe_queries():
    # Initialize database connection
    db = RecipeDatabase()
    
    if not db.connect():
        print("Failed to connect to the database!")
        return
    
    try:
        # Test 1: Search for a recipe by name
        print("\nTEST 1: Search for recipes containing 'chicken' in the name")
        chicken_recipes = db.search_recipes_by_name("chicken", limit=3)
        print(f"Found {len(chicken_recipes)} chicken recipes")
        
        if chicken_recipes:
            print("First recipe:")
            db.pretty_print_recipe(chicken_recipes[0])
        
        # Test 2: Find vegetarian recipes
        print("\nTEST 2: Find vegetarian recipes")
        vegetarian_recipes = db.find_recipes_by_tags(["vegetarian"], limit=3)
        print(f"Found {len(vegetarian_recipes)} vegetarian recipes")
        
        if vegetarian_recipes:
            print("First vegetarian recipe:")
            db.pretty_print_recipe(vegetarian_recipes[0])
        
        # Test 3: Find recipes with specific ingredients
        print("\nTEST 3: Find recipes with garlic and tomato")
        ingredient_recipes = db.find_recipes_by_ingredients(["garlic", "tomato"], limit=3)
        print(f"Found {len(ingredient_recipes)} recipes with garlic and tomato")
        
        if ingredient_recipes:
            print("First matching recipe:")
            db.pretty_print_recipe(ingredient_recipes[0])
        
        # Test 4: More complex query - find easy desserts under 30 minutes
        print("\nTEST 4: Find easy desserts that take less than 30 minutes")
        query = {
            "tags": {"$all": ["dessert", "easy"]},
            "minutes": {"$lte": 30}
        }
        
        quick_desserts = db.find_recipes(query, limit=3)
        print(f"Found {len(quick_desserts)} easy desserts under 30 minutes")
        
        if quick_desserts:
            print("First quick dessert recipe:")
            db.pretty_print_recipe(quick_desserts[0])
    
    except Exception as e:
        print(f"Error executing queries: {e}")
    
    finally:
        # Close the connection
        db.close()
        print("\nConnection closed.")

if __name__ == "__main__":
    test_recipe_queries()