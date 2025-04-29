import pytest
import sys
import os
from unittest.mock import MagicMock
from bson import ObjectId

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture
def sample_recipes():
    """Fixture providing sample recipe data for tests"""
    return [
        {
            '_id': ObjectId('507f1f77bcf86cd799439011'),
            'name': 'Vegetarian Pasta',
            'minutes': 30,
            'nutrition': {'calories': 500},
            'tags': ['vegetarian', 'main-dish', 'dinner', 'italian'],
            'ingredients': ['pasta', 'tomato sauce', 'cheese'],
            'steps': ['Boil pasta', 'Add sauce'],
        },
        {
            '_id': ObjectId('507f1f77bcf86cd799439012'),
            'name': 'Breakfast Omelette',
            'minutes': 15,
            'nutrition': {'calories': 300},
            'tags': ['breakfast', 'main-dish', 'easy'],
            'ingredients': ['eggs', 'cheese', 'vegetables'],
            'steps': ['Beat eggs', 'Cook in pan'],
        },
        {
            '_id': ObjectId('507f1f77bcf86cd799439013'),
            'name': 'Chicken Dinner',
            'minutes': 45,
            'nutrition': {'calories': 650},
            'tags': ['dinner', 'main-dish', 'poultry'],
            'ingredients': ['chicken', 'potatoes', 'vegetables', 'herbs'],
            'steps': ['Season chicken', 'Roast in oven', 'Serve hot'],
        },
    ]


@pytest.fixture
def mock_mongo_collection():
    """Create a mock MongoDB collection for testing"""
    mock_collection = MagicMock()
    
    def find_side_effect(query=None, *args, **kwargs):
        mock_cursor = MagicMock()
        mock_cursor.limit.return_value = sample_recipes()
        return mock_cursor
    
    mock_collection.find = MagicMock(side_effect=find_side_effect)
    mock_collection.find_one = MagicMock(return_value=sample_recipes()[0])
    mock_collection.count_documents = MagicMock(return_value=3)
    
    return mock_collection


@pytest.fixture
def user_preferences():
    """Sample user preferences for testing recommendation system"""
    return {
        'question1': ['vegetarian'],  # Diet selection
        'question2': '3',             # Calorie option
        'question3': '1',             # Time option
        'question4': ['italian'],     # Cuisine
        'question5': '1',             # Beginner cook
        'question6': ['breakfast', 'dinner'],  # Meal type
        'question7': ['main_dish', 'side_dishes']  # Dish type
    }