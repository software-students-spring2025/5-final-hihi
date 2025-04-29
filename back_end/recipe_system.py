import json
import random
from pprint import pprint
from .mongo_connection import RecipeDatabase
from .mongo_connection import JSONEncoder
from .recipe_recommender import recommend_recipes

class RecipeRecommendationSystem:
    def __init__(self):
        self.db = RecipeDatabase()
        self.connected = self.db.connect()
        
    def __del__(self):
        try:
            self.db_connection.close()
        except Exception:
            pass  # Ignore shutdown errors

    
    def get_recommendations(self, user_preferences):
        """Get recipe recommendations based on user preferences"""
        if not self.connected:
            print("Error: Not connected to database")
            return {}
            
        # Use the recommend_recipes function from recipe_recommender.py
        recommendations = recommend_recipes(user_preferences, self.db.collection)
        # print(user_preferences)
        return recommendations
    
    def display_recommendations(self, recommendations):
        """Display the recommended recipes in a readable format"""
        print("\n" + "=" * 50)
        print("RECIPE RECOMMENDATIONS")
        print("=" * 50)
        
        for meal_type, recipes in recommendations.items():
            if not recipes:
                continue
                
            print(f"\n{meal_type.upper()} RECOMMENDATIONS:")
            print("-" * 30)
            
            for i, recipe in enumerate(recipes, 1):
                print(f"\n{i}. {recipe['name']}")
                print(f"   Time: {recipe['minutes']} minutes")
                print(f"   Calories: {recipe['nutrition']['calories']}")
                
                # Show first 3 ingredients as preview
                ingredients_preview = ", ".join(recipe['ingredients'][:3])
                if len(recipe['ingredients']) > 3:
                    ingredients_preview += "..."
                print(f"   Ingredients: {ingredients_preview}")
                
                # Show key tags
                important_tags = [tag for tag in recipe['tags'] if tag in 
                                 ['vegetarian', 'vegan', 'gluten-free', 'easy', 
                                  'beginner-cook', 'low-calorie', 'high-protein']]
                if important_tags:
                    print(f"   Key Features: {', '.join(important_tags)}")
            
            print("\n" + "-" * 30)
    
    def get_recipe_details(self, recipe_id):
        """Get detailed information about a specific recipe"""
        recipe = self.db.find_recipe_by_id(recipe_id)
        return recipe
    
    def search_by_name(self, name_query, limit=10):
        """Search recipes by name"""
        return self.db.search_recipes_by_name(name_query, limit)
    
    def search_by_tags(self, tags, limit=10):
        """Search recipes by tags"""
        return self.db.find_recipes_by_tags(tags, limit)
    
    def search_by_ingredients(self, ingredients, limit=10):
        """Search recipes by ingredients"""
        return self.db.find_recipes_by_ingredients(ingredients, limit)
    
    def export_recommendations_to_json(self, recommendations, filename):
        """Export recommendations to a JSON file"""
        from bson import json_util

        try:
            with open(filename, 'w') as f:
                f.write(json_util.dumps(recommendations, indent=2))
            print(f"Recommendations exported to {filename}")
            return True
        except Exception as e:
            print(f"Error exporting recommendations: {e}")
            return False



# Example usage
if __name__ == "__main__":
    # Create an instance of the recommendation system
    system = RecipeRecommendationSystem()
    
    # Example user preferences
    user_preferences = {
        'question1': [1],  # Vegetarian
        'question2': 4,     # Moderate calories (1600-1800)
        'question3': 4,     # 30 minutes to 1 hour
        'question4': [1],   # Italian cuisine
        'question5': 2,     # Beginner cook
        'question6': [2, 4], # Lunch and dinner
        'question7': [1, 3, 5]  # Main dish and dessert
    }
    
    # Get recommendations based on user preferences
    recommendations = system.get_recommendations(user_preferences)
    
    # Display the recommendations
    system.display_recommendations(recommendations)
    
    # Export the recommendations to a JSON file
    system.export_recommendations_to_json(recommendations, "recommendations.json")