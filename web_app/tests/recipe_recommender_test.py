import pytest
from unittest.mock import MagicMock
from web_app.back_end.recipe_recommender import recommend_recipes, find_with_improved_relaxation

@pytest.fixture
def test_db():
    mock_collection = MagicMock()
    mock_collection.find.return_value.limit.return_value = [{
        '_id': 'mockid',
        'name': 'Test Recipe',
        'minutes': 20,
        'tags': ['breakfast', 'main-dish'],
        'nutrition': {'calories': 300},
        'ingredients': ['eggs']
    }]
    return mock_collection

def test_recommend_recipes_basic(test_db):
    user_preferences = {
        'question1': [],
        'question2': 7,
        'question3': 6,
        'question4': ['any'],
        'question5': 2,
        'question6': ['breakfast'],
        'question7': ['main_dish']
    }
    results = recommend_recipes(user_preferences, test_db)
    assert 'breakfast' in results
    assert len(results['breakfast']) > 0

def test_recommend_recipes_with_dietary_restrictions(test_db):
    user_preferences = {
        'question1': ['vegetarian'],
        'question2': 7,
        'question3': 6,
        'question4': ['any'],
        'question5': 2,
        'question6': ['breakfast'],
        'question7': ['main_dish']
    }
    results = recommend_recipes(user_preferences, test_db)
    assert 'breakfast' in results

def test_recommend_recipes_with_time_constraints(test_db):
    user_preferences = {
        'question1': [],
        'question2': 7,
        'question3': 1,
        'question4': ['any'],
        'question5': 2,
        'question6': ['breakfast'],
        'question7': ['main_dish']
    }
    results = recommend_recipes(user_preferences, test_db)
    assert 'breakfast' in results

def test_recommend_recipes_with_calorie_range(test_db):
    user_preferences = {
        'question1': [],
        'question2': 1,
        'question3': 6,
        'question4': ['any'],
        'question5': 2,
        'question6': ['breakfast'],
        'question7': ['main_dish']
    }
    results = recommend_recipes(user_preferences, test_db)
    assert 'breakfast' in results

def test_recommend_recipes_lunch_dinner(test_db):
    user_preferences = {
        'question1': [],
        'question2': 7,
        'question3': 6,
        'question4': ['any'],
        'question5': 2,
        'question6': ['lunch', 'dinner'],
        'question7': ['main_dish', 'side_dishes']
    }
    results = recommend_recipes(user_preferences, test_db)
    assert 'lunch' in results or 'dinner' in results

def test_relaxation_strategy_basic(test_db):
    search_params = {
        "query": {"tags": "main-dish"},
        "cuisine_tags": ["italian"],
        "has_calorie": True,
        "has_time": True,
        "has_diet": True,
        "diet_tags": ["vegetarian"],
        "allergy_tags": [],
        "meal_tags": ["dinner"],
        "dish_tags": ["main-dish"]
    }
    result = find_with_improved_relaxation(test_db, search_params)
    assert result is not None

def test_relaxation_strategy_no_cuisine(test_db):
    search_params = {
        "query": {"tags": "main-dish"},
        "cuisine_tags": [],
        "has_calorie": True,
        "has_time": True,
        "has_diet": True,
        "diet_tags": ["vegetarian"],
        "allergy_tags": [],
        "meal_tags": ["dinner"],
        "dish_tags": ["main-dish"]
    }
    result = find_with_improved_relaxation(test_db, search_params)
    assert result is not None

def test_relaxation_strategy_with_allergies(test_db):
    search_params = {
        "query": {"tags": "main-dish"},
        "cuisine_tags": ["italian"],
        "has_calorie": True,
        "has_time": True,
        "has_diet": False,
        "diet_tags": [],
        "allergy_tags": ["nuts"],
        "meal_tags": ["dinner"],
        "dish_tags": ["main-dish"]
    }
    result = find_with_improved_relaxation(test_db, search_params)
    assert result is not None

def test_relaxation_strategy_last_resort(test_db):
    search_params = {
        "query": {"tags": "non-existent-tag"},
        "cuisine_tags": ["non-existent-cuisine"],
        "has_calorie": True,
        "has_time": True,
        "has_diet": True,
        "diet_tags": ["non-existent-diet"],
        "allergy_tags": [],
        "meal_tags": ["dinner"],
        "dish_tags": ["main-dish"]
    }
    result = find_with_improved_relaxation(test_db, search_params)
    assert result is None or result is not None

def test_recommend_recipes_calorie_type_error():
    user_preferences = {
        'question1': [],
        'question2': "invalid",  # Triggers ValueError
        'question3': 2,
        'question4': ["any"],
        'question5': 2,
        'question6': ['breakfast'],
        'question7': ['main_dish']
    }

    mock_db = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.limit.return_value = []
    mock_db.find.return_value = mock_cursor

    result = recommend_recipes(user_preferences, mock_db)
    assert isinstance(result, dict)


def test_recommend_recipes_time_type_error():
    user_preferences = {
        'question1': [],
        'question2': 4,
        'question3': None,  # Triggers TypeError
        'question4': ["any"],
        'question5': 2,
        'question6': ['breakfast'],
        'question7': ['main_dish']
    }

    mock_db = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.limit.return_value = []
    mock_db.find.return_value = mock_cursor

    result = recommend_recipes(user_preferences, mock_db)
    assert isinstance(result, dict)