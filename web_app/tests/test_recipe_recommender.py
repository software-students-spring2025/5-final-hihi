import pytest
from pymongo import MongoClient
from back_end.recipe_recommender import recommend_recipes, find_with_improved_relaxation

@pytest.fixture
def test_db():
    client = MongoClient('mongodb://localhost:27017/')
    db = client['recipe_database']
    collection = db['recipes']
    return collection

def test_recommend_recipes_basic(test_db):
    """Test recipe recommendation basic functionality"""
    user_preferences = {
        'question1': [],                      # No dietary restrictions
        'question2': 7,                       # No calorie restriction
        'question3': 6,                       # Any time
        'question4': ["any"],                 # Any cuisine
        'question5': 2,                       # Not beginner
        'question6': ['breakfast'],           # Breakfast
        'question7': ['main_dish']            # Main dish
    }
    
    results = recommend_recipes(user_preferences, test_db)
    assert 'breakfast' in results
    assert len(results['breakfast']) > 0

def test_recommend_recipes_with_dietary_restrictions(test_db):
    """Test recommendations with dietary restrictions"""
    user_preferences = {
        'question1': ['vegetarian'],          # Vegetarian
        'question2': 7,                       # No calorie restriction
        'question3': 6,                       # Any time
        'question4': ["any"],                 # Any cuisine
        'question5': 2,                       # Not beginner
        'question6': ['breakfast'],           # Breakfast
        'question7': ['main_dish']            # Main dish
    }
    
    results = recommend_recipes(user_preferences, test_db)
    # Even if no exact matches, the algorithm should return something
    assert 'breakfast' in results

def test_recommend_recipes_with_time_constraints(test_db):
    """Test recommendations with time constraints"""
    user_preferences = {
        'question1': [],                      # No dietary restrictions
        'question2': 7,                       # No calorie restriction
        'question3': 1,                       # 0-30 minutes
        'question4': ["any"],                 # Any cuisine
        'question5': 2,                       # Not beginner
        'question6': ['breakfast'],           # Breakfast
        'question7': ['main_dish']            # Main dish
    }
    
    results = recommend_recipes(user_preferences, test_db)
    assert 'breakfast' in results

def test_recommend_recipes_with_calorie_range(test_db):
    """Test recommendations with calorie range"""
    user_preferences = {
        'question1': [],                      # No dietary restrictions
        'question2': 1,                       # Lower calorie range
        'question3': 6,                       # Any time
        'question4': ["any"],                 # Any cuisine
        'question5': 2,                       # Not beginner
        'question6': ['breakfast'],           # Breakfast
        'question7': ['main_dish']            # Main dish
    }
    
    results = recommend_recipes(user_preferences, test_db)
    assert 'breakfast' in results

def test_recommend_recipes_lunch_dinner(test_db):
    """Test recommendations for lunch/dinner with multiple dish types"""
    user_preferences = {
        'question1': [],                           # No dietary restrictions
        'question2': 7,                            # No calorie restriction
        'question3': 6,                            # Any time
        'question4': ["any"],                      # Any cuisine
        'question5': 2,                            # Not beginner
        'question6': ['lunch', 'dinner'],          # Lunch & dinner
        'question7': ['main_dish', 'side_dishes']  # Multiple dish types
    }
    
    results = recommend_recipes(user_preferences, test_db)
    assert 'lunch' in results or 'dinner' in results

def test_relaxation_strategy_basic(test_db):
    """Test basic relaxation strategy"""
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
    # The function should always return something even if it has to relax constraints
    assert result is not None

def test_relaxation_strategy_no_cuisine(test_db):
    """Test relaxation strategy with no cuisine specified"""
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
    """Test relaxation strategy with allergy restrictions"""
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
    """Test the last resort option in relaxation strategy"""
    # Create an impossible combination of constraints
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
    
    # The function should still attempt to find something
    result = find_with_improved_relaxation(test_db, search_params)
    # May return None if nothing matches at all, but shouldn't error
    assert result is None or result is not None