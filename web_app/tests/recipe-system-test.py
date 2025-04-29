import pytest
import sys
import os
from unittest.mock import patch, MagicMock
import tempfile
import json

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from back_end.recipe_system import RecipeRecommendationSystem


@pytest.fixture
def mock_database_connection():
    """Create a mock database connection for testing"""
    with patch('back_end.recipe_system.RecipeDatabase') as mock_db_class:
        mock_db = MagicMock()
        mock_db.connect.return_value = True
        mock_db_class.return_value = mock_db
        
        # Setup mock collection
        mock_collection = MagicMock()
        mock_db.collection = mock_collection
        
        # Sample recipes
        vegetarian_recipe = {
            '_id': '1',
            'name': 'Vegetarian Pasta',
            'minutes': 30,
            'nutrition': {'calories': 500},
            'tags': ['vegetarian', 'main-dish', 'dinner'],
            'ingredients': ['pasta', 'tomato sauce', 'cheese'],
            'steps': ['Boil pasta', 'Add sauce'],
        }
        
        breakfast_recipe = {
            '_id': '2',
            'name': 'Breakfast Omelette',
            'minutes': 15,
            'nutrition': {'calories': 300},
            'tags': ['breakfast', 'main-dish', 'easy'],
            'ingredients': ['eggs', 'cheese', 'vegetables'],
            'steps': ['Beat eggs', 'Cook in pan'],
        }
        
        mock_collection.find.return_value.limit.return_value = [vegetarian_recipe]
        mock_db.find_recipe_by_id.return_value = breakfast_recipe
        mock_db.search_recipes_by_name.return_value = [vegetarian_recipe]
        mock_db.find_recipes_by_tags.return_value = [vegetarian_recipe]
        mock_db.find_recipes_by_ingredients.return_value = [vegetarian_recipe]
        
        yield mock_db_class, mock_db


@patch('back_end.recipe_system.recommend_recipes')
def test_get_recommendations(mock_recommend_recipes, mock_database_connection):
    """Test getting recommendations"""
    # Unpack the fixture
    mock_db_class, mock_db = mock_database_connection
    
    # Configure the mock
    mock_recommendations = {
        'breakfast': [{
            '_id': '2',
            'name': 'Breakfast Omelette',
            'minutes': 15,
            'nutrition': {'calories': 300},
            'tags': ['breakfast', 'main-dish', 'easy'],
            'ingredients': ['eggs', 'cheese', 'vegetables'],
            'steps': ['Beat eggs', 'Cook in pan'],
        }]
    }
    mock_recommend_recipes.return_value = mock_recommendations
    
    # Create system and test
    system = RecipeRecommendationSystem()
    user_prefs = {'question1': ['vegetarian']}
    
    result = system.get_recommendations(user_prefs)
    
    # Verify results
    mock_recommend_recipes.assert_called_once_with(user_prefs, mock_db.collection)
    assert result == mock_recommendations


def test_search_by_name(mock_database_connection):
    """Test searching recipes by name"""
    # Unpack the fixture
    mock_db_class, mock_db = mock_database_connection
    
    # Create system and test
    system = RecipeRecommendationSystem()
    
    result = system.search_by_name("pasta", 5)
    
    # Verify results
    mock_db.search_recipes_by_name.assert_called_once_with("pasta", 5)
    assert len(result) == 1
    assert result[0]['name'] == 'Vegetarian Pasta'


def test_search_by_tags(mock_database_connection):
    """Test searching recipes by tags"""
    # Unpack the fixture
    mock_db_class, mock_db = mock_database_connection
    
    # Create system and test
    system = RecipeRecommendationSystem()
    
    result = system.search_by_tags(["vegetarian", "main-dish"], 5)
    
    # Verify results
    mock_db.find_recipes_by_tags.assert_called_once_with(["vegetarian", "main-dish"], 5)
    assert len(result) == 1
    assert result[0]['name'] == 'Vegetarian Pasta'


def test_search_by_ingredients(mock_database_connection):
    """Test searching recipes by ingredients"""
    # Unpack the fixture
    mock_db_class, mock_db = mock_database_connection
    
    # Create system and test
    system = RecipeRecommendationSystem()
    
    result = system.search_by_ingredients(["pasta", "tomato sauce"], 5)
    
    # Verify results
    mock_db.find_recipes_by_ingredients.assert_called_once_with(["pasta", "tomato sauce"], 5)
    assert len(result) == 1
    assert result[0]['name'] == 'Vegetarian Pasta'


def test_export_recommendations_to_json(mock_database_connection):
    """Test exporting recommendations to JSON"""
    # Unpack the fixture
    mock_db_class, mock_db = mock_database_connection
    
    # Create temp file for testing
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
        tmp_name = tmp.name
    
    try:
        # Create system and test data
        system = RecipeRecommendationSystem()
        recommendations = {
            'breakfast': [{
                '_id': '2',
                'name': 'Breakfast Omelette',
                'minutes': 15,
                'nutrition': {'calories': 300},
                'tags': ['breakfast', 'main-dish', 'easy'],
                'ingredients': ['eggs', 'cheese', 'vegetables'],
                'steps': ['Beat eggs', 'Cook in pan'],
            }]
        }
        
        # Test export
        result = system.export_recommendations_to_json(recommendations, tmp_name)
        
        # Verify results
        assert result is True
        
        # Verify file contents
        with open(tmp_name, 'r') as f:
            data = json.loads(f.read())
            assert 'breakfast' in data
            assert data['breakfast'][0]['name'] == 'Breakfast Omelette'
    
    finally:
        # Clean up
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)
