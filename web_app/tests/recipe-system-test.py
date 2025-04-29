import pytest
import os
from back_end.recipe_system import RecipeRecommendationSystem

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
    """Test various search methods"""
    system = RecipeRecommendationSystem()
    
    # Test search by name
    name_results = system.search_by_name('Test Recipe')
    assert len(name_results) > 0
    
    # Test search by tags
    tag_results = system.search_by_tags(['breakfast'])
    assert len(tag_results) >= 0  # May be empty but shouldn't error
    
    # Test search by ingredients
    ingredient_results = system.search_by_ingredients(['eggs'])
    assert len(ingredient_results) >= 0  # May be empty but shouldn't error

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
