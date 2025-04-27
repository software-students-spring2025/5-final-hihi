from recipe_system import RecipeRecommendationSystem

def test_recipe_recommendations():
    print("Creating recommendation system...")
    system = RecipeRecommendationSystem()
    
    if not system.connected:
        print("Failed to connect to the database!")
        return
    
    try:
        print("\nTesting recipe recommendations...")
        
        # Create user preference scenarios
        scenarios = [
            {
                "name": "Vegetarian Italian",
                "preferences": {
                    'question1': [1],  # Vegetarian
                    'question2': 4,    # Balanced calories
                    'question3': 2,    # 30-60 minutes
                    'question4': [4],  # Italian cuisine
                    'question5': 2,    # Not beginner
                    'question6': [3, 4],  # Lunch and dinner
                    'question7': [1, 3]   # Main dish and dessert
                }
            },
            {
                "name": "Quick Breakfast for Beginners",
                "preferences": {
                    'question1': [10],  # No dietary restrictions
                    'question2': 7,     # No calorie preference
                    'question3': 1,     # Under 30 minutes
                    'question4': [15],  # No cuisine preference
                    'question5': 1,     # Beginner
                    'question6': [1],   # Breakfast
                    'question7': [1]    # Main dish
                }
            },
            {
                "name": "Gluten-Free Asian Dinner",
                "preferences": {
                    'question1': [4],   # Gluten-free
                    'question2': 3,     # Moderate calories
                    'question3': 3,     # 1-1.5 hours
                    'question4': [3, 14],  # Asian, Chinese
                    'question5': 2,     # Not beginner
                    'question6': [4],   # Dinner
                    'question7': [1, 2, 5]  # Main dish, side dish, soup
                }
            }
        ]
        
        # Test each scenario
        for scenario in scenarios:
            print(f"\n{'=' * 50}")
            print(f"SCENARIO: {scenario['name']}")
            print(f"{'=' * 50}")
            
            # Get recommendations
            recommendations = system.get_recommendations(scenario['preferences'])
            
            # Display recommendations
            system.display_recommendations(recommendations)
            
            # Count total recipes recommended
            total_recipes = sum(len(recipes) for recipes in recommendations.values())
            print(f"\nTotal recipes recommended: {total_recipes}")
    
    except Exception as e:
        print(f"Error getting recommendations: {e}")
    
    # Connection is closed automatically when the system is destroyed

if __name__ == "__main__":
    test_recipe_recommendations()