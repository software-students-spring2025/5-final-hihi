import pytest
import os
from web_app.back_end.recipe_system import RecipeRecommendationSystem

def test_recipe_system_connection():
    """Test connection through recipe system"""
    system = RecipeRecommendationSystem()
    assert system.connected == True

def test_get_recommendations():
    """Test getting recommendations"""
    system = RecipeRecommendationSystem()
    
    # Simple preferences
    user_preferences = {
        'question1': [],                       # No dietary restrictions
        'question2': 7,                        # No calorie restriction
        'question3': 6,                        # Any time
        'question4': ["any"],                  # Any cuisine
        'question5': 2,                        # Not beginner
        'question6': ['breakfast'],            # Breakfast
        'question7': ['main_dish']             # Main dish
    }
    
    recommendations = system.get_recommendations(user_preferences)
    assert 'breakfast' in recommendations
    assert len(recommendations['breakfast']) > 0

def test_display_recommendations(capsys):
    """Test display_recommendations method"""
    system = RecipeRecommendationSystem()
    
    # Create a simple recommendations structure
    recommendations = {
        'breakfast': [
            {
                'name': 'Test Breakfast',
                'minutes': 15,
                'nutrition': {'calories': 250},
                'ingredients': ['eggs', 'toast', 'avocado'],
                'tags': ['breakfast', 'vegetarian', 'easy']
            }
        ]
    }
    
    # Call the method
    system.display_recommendations(recommendations)
    
    # Capture the output
    captured = capsys.readouterr()
    output = captured.out
    
    # Assert output contains expected data
    assert 'BREAKFAST RECOMMENDATIONS' in output
    assert 'Test Breakfast' in output
    assert '15 minutes' in output
    assert '250' in output
    assert 'eggs, toast, avocado' in output or 'eggs, toast' in output
    assert 'vegetarian, easy' in output or 'vegetarian' in output or 'easy' in output

def test_get_recipe_details():
    """Test get_recipe_details method"""
    system = RecipeRecommendationSystem()
    
    # First get any recipe ID
    recipe = system.db.collection.find_one()
    recipe_id = recipe['_id']
    
    # Test the method
    details = system.get_recipe_details(recipe_id)
    assert details is not None
    assert details['_id'] == recipe_id
    assert 'name' in details
    assert 'ingredients' in details

def test_search_methods():
    system = RecipeRecommendationSystem()
    
    # Insert mock recipe directly (if using live DB)
    system.db.collection.insert_one({
        'name': 'Test Recipe',
        'minutes': 10,
        'tags': ['test'],
        'ingredients': ['test'],
        'nutrition': {'calories': 100},
        'description': '',
        'steps': ['']
    })

    name_results = system.search_by_name('Test Recipe')
    assert len(name_results) > 0

def test_export_recommendations(tmpdir):
    """Test exporting recommendations to JSON"""
    system = RecipeRecommendationSystem()
    
    # Create a simple recommendations structure
    recommendations = {
        'breakfast': [
            {
                'name': 'Test Breakfast',
                'minutes': 15,
                'nutrition': {'calories': 250},
                'ingredients': ['eggs', 'toast', 'avocado'],
                'tags': ['breakfast', 'vegetarian', 'easy']
            }
        ]
    }
    
    # Create a temporary file path
    file_path = os.path.join(tmpdir, 'test_recommendations.json')
    
    # Test the export method
    success = system.export_recommendations_to_json(recommendations, file_path)
    assert success == True
    assert os.path.exists(file_path)
    
    # Check file content
    with open(file_path, 'r') as f:
        content = f.read()
        assert 'Test Breakfast' in content
        assert 'eggs' in content

def test_get_recommendations_not_connected(capsys):
    system = RecipeRecommendationSystem()
    system.connected = False  # Force disconnected state
    results = system.get_recommendations(user_preferences={})

    captured = capsys.readouterr()
    assert results == {}
    assert "Error: Not connected to database" in captured.out

def test_display_recommendations_skips_empty(capsys):
    system = RecipeRecommendationSystem()
    system.connected = True  # Avoid connection check

    recommendations = {
        "breakfast": [],
        "lunch": [{"name": "Grilled Cheese", "minutes": 10, "nutrition": {"calories": 300}, "ingredients": ["bread", "cheese"], "tags": ["easy", "main-dish"]}]
    }

    system.display_recommendations(recommendations)
    output = capsys.readouterr().out

    assert "BREAKFAST RECOMMENDATIONS" not in output
    assert "LUNCH RECOMMENDATIONS" in output
    assert "Grilled Cheese" in output

def test_search_by_tags_returns_expected_results():
    system = RecipeRecommendationSystem()
    system.db = type('', (), {})()  # Dummy object

    # Mock the method
    def mock_find_recipes_by_tags(tags, limit):
        return [{"name": "Avocado Toast", "tags": tags}]
    system.db.find_recipes_by_tags = mock_find_recipes_by_tags

    tags = ['breakfast']
    results = system.search_by_tags(tags)

    assert isinstance(results, list)
    assert results[0]['name'] == 'Avocado Toast'
    assert tags[0] in results[0]['tags']

def test_search_by_ingredients_returns_expected_results():
    system = RecipeRecommendationSystem()
    system.db = type('', (), {})()  # Dummy object

    def mock_find_recipes_by_ingredients(ingredients, limit):
        return [{"name": "Egg Sandwich", "ingredients": ingredients}]
    
    system.db.find_recipes_by_ingredients = mock_find_recipes_by_ingredients

    ingredients = ['egg']
    results = system.search_by_ingredients(ingredients)

    assert isinstance(results, list)
    assert results[0]['name'] == 'Egg Sandwich'
    assert ingredients[0] in results[0]['ingredients']

def test_export_recommendations_to_json_error(monkeypatch):
    system = RecipeRecommendationSystem()

    # Simulate a recommendation dictionary
    recommendations = {"lunch": [{"name": "Mock Recipe"}]}

    # Patch built-in open to raise an exception
    def mock_open(*args, **kwargs):
        raise IOError("Mocked file write error")

    monkeypatch.setattr("builtins.open", mock_open)

    # Should catch the exception and return False
    result = system.export_recommendations_to_json(recommendations, "invalid/path.json")
    assert result is False
