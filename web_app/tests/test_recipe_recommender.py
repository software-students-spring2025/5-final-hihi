import pytest
import sys
import os
import random
from unittest.mock import patch, MagicMock

# Add the parent directory to path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Test for recipe recommender with mocks
class TestRecipeRecommender:
    
    @staticmethod
    def create_mock_collection():
        """Create a mock collection for testing"""
        mock_collection = MagicMock()
        
        # Create sample recipes
        breakfast_recipe = {
            "_id": "123",
            "name": "Test Breakfast",
            "minutes": 15,
            "nutrition": {"calories": 200},
            "ingredients": ["eggs", "toast"],
            "tags": ["breakfast", "main-dish", "easy", "vegetarian"]
        }
        
        lunch_recipe = {
            "_id": "456",
            "name": "Test Lunch",
            "minutes": 30,
            "nutrition": {"calories": 400},
            "ingredients": ["chicken", "rice"],
            "tags": ["lunch", "dinner", "main-dish"]
        }
        
        veg_recipe = {
            "_id": "789",
            "name": "Vegetarian Dinner",
            "minutes": 45,
            "nutrition": {"calories": 350},
            "ingredients": ["tofu", "vegetables"],
            "tags": ["dinner", "main-dish", "vegetarian"]
        }
        
        # Setup find method
        class MockCursor:
            def __init__(self, recipes):
                self.recipes = recipes
            
            def limit(self, n):
                return self
                
            def __iter__(self):
                return iter(self.recipes)
        
        # Default recipes to return
        recipes = [breakfast_recipe, lunch_recipe, veg_recipe]
        mock_cursor = MockCursor(recipes)
        
        # Configure find method behavior
        def mock_find(query=None):
            if query is None:
                return MockCursor(recipes)
                
            # Filter based on query
            if isinstance(query, dict):
                if 'tags' in query:
                    if isinstance(query['tags'], dict):
                        # Handle $all and $in operators
                        if '$all' in query['tags']:
                            filtered = []
                            for recipe in recipes:
                                if all(tag in recipe['tags'] for tag in query['tags']['$all']):
                                    filtered.append(recipe)
                            return MockCursor(filtered)
                        elif '$in' in query['tags']:
                            filtered = []
                            for recipe in recipes:
                                if any(tag in recipe['tags'] for tag in query['tags']['$in']):
                                    filtered.append(recipe)
                            return MockCursor(filtered)
                        elif '$nin' in query['tags']:
                            filtered = []
                            for recipe in recipes:
                                if not any(tag in recipe['tags'] for tag in query['tags']['$nin']):
                                    filtered.append(recipe)
                            return MockCursor(filtered)
                    else:
                        # Handle direct tag matching
                        filtered = []
                        for recipe in recipes:
                            if query['tags'] in recipe['tags']:
                                filtered.append(recipe)
                        return MockCursor(filtered)
                        
                # Handle minutes filter
                if 'minutes' in query:
                    if isinstance(query['minutes'], dict):
                        filtered = []
                        for recipe in recipes:
                            include = True
                            
                            if '$gte' in query['minutes']:
                                if recipe['minutes'] < query['minutes']['$gte']:
                                    include = False
                                    
                            if '$lte' in query['minutes']:
                                if recipe['minutes'] > query['minutes']['$lte']:
                                    include = False
                                    
                            if include:
                                filtered.append(recipe)
                        return MockCursor(filtered)
                
                # Handle complex $and queries
                if '$and' in query:
                    # Just return a subset for simplicity
                    return MockCursor(recipes[:1])
            
            # Default return all recipes
            return MockCursor(recipes)
        
        # Setup find_one behavior
        def mock_find_one(query=None):
            cursor = mock_find(query)
            for recipe in cursor:
                return recipe
            return None
            
        # Assign mocked methods
        mock_collection.find = mock_find
        mock_collection.find_one = mock_find_one
        
        return mock_collection
    
    @staticmethod
    def test_recommend_recipes_basic():
        """Test basic functionality of recommend_recipes"""
        try:
            # Mock random functions
            random_uniform_patch = patch('random.uniform', return_value=1.0)
            random_choice_patch = patch('random.choice', side_effect=lambda x: x[0])
            
            # Apply patches
            random_uniform_patch.start()
            random_choice_patch.start()
            
            # Import the function to test
            from back_end.recipe_recommender import recommend_recipes
            
            # Create mock collection
            mock_collection = TestRecipeRecommender.create_mock_collection()
            
            # Test with basic preferences
            user_preferences = {
                'question1': [],                      # No dietary restrictions
                'question2': 7,                       # No calorie restriction
                'question3': 6,                       # Any time
                'question4': ["any"],                 # Any cuisine
                'question5': 2,                       # Not beginner
                'question6': ['breakfast'],           # Breakfast
                'question7': ['main_dish']            # Main dish
            }
            
            results = recommend_recipes(user_preferences, mock_collection)
            
            # Check results
            assert 'breakfast' in results
            assert len(results['breakfast']) > 0
            assert results['breakfast'][0]['name'] in ["Test Breakfast", "Test Lunch", "Vegetarian Dinner"]
            
            # Clean up patches
            random_uniform_patch.stop()
            random_choice_patch.stop()
            
        except ImportError:
            pytest.skip("Module could not be imported")
    
    @staticmethod
    def test_recommend_recipes_with_diet():
        """Test recipe recommendations with dietary restrictions"""
        try:
            # Mock random functions
            random_uniform_patch = patch('random.uniform', return_value=1.0)
            random_choice_patch = patch('random.choice', side_effect=lambda x: x[0])
            
            # Apply patches
            random_uniform_patch.start()
            random_choice_patch.start()
            
            # Import the function to test
            from back_end.recipe_recommender import recommend_recipes
            
            # Create mock collection
            mock_collection = TestRecipeRecommender.create_mock_collection()
            
            # Test with vegetarian preference
            user_preferences = {
                'question1': ['vegetarian'],          # Vegetarian
                'question2': 7,                       # No calorie restriction
                'question3': 6,                       # Any time
                'question4': ["any"],                 # Any cuisine
                'question5': 2,                       # Not beginner
                'question6': ['breakfast'],           # Breakfast
                'question7': ['main_dish']            # Main dish
            }
            
            results = recommend_recipes(user_preferences, mock_collection)
            
            # Check results - should include vegetarian recipes
            assert 'breakfast' in results
            assert len(results['breakfast']) > 0
            
            # Clean up patches
            random_uniform_patch.stop()
            random_choice_patch.stop()
            
        except ImportError:
            pytest.skip("Module could not be imported")
    
    @staticmethod
    def test_recommend_recipes_with_time():
        """Test recommendations with time constraints"""
        try:
            # Mock random functions
            random_uniform_patch = patch('random.uniform', return_value=1.0)
            random_choice_patch = patch('random.choice', side_effect=lambda x: x[0])
            
            # Apply patches
            random_uniform_patch.start()
            random_choice_patch.start()
            
            # Import the function to test
            from back_end.recipe_recommender import recommend_recipes
            
            # Create mock collection
            mock_collection = TestRecipeRecommender.create_mock_collection()
            
            # Test with time constraints
            user_preferences = {
                'question1': [],                      # No dietary restrictions
                'question2': 7,                       # No calorie restriction
                'question3': 1,                       # 0-30 minutes
                'question4': ["any"],                 # Any cuisine
                'question5': 2,                       # Not beginner
                'question6': ['breakfast'],           # Breakfast
                'question7': ['main_dish']            # Main dish
            }
            
            results = recommend_recipes(user_preferences, mock_collection)
            
            # Check results - should include short recipes
            assert 'breakfast' in results
            assert len(results['breakfast']) > 0
            
            # Clean up patches
            random_uniform_patch.stop()
            random_choice_patch.stop()
            
        except ImportError:
            pytest.skip("Module could not be imported")
    
    @staticmethod
    def test_recommend_recipes_with_cuisine():
        """Test recommendations with cuisine preferences"""
        try:
            # Mock random functions
            random_uniform_patch = patch('random.uniform', return_value=1.0)
            random_choice_patch = patch('random.choice', side_effect=lambda x: x[0])
            
            # Apply patches
            random_uniform_patch.start()
            random_choice_patch.start()
            
            # Import the function to test
            from back_end.recipe_recommender import recommend_recipes
            
            # Create mock collection
            mock_collection = TestRecipeRecommender.create_mock_collection()
            
            # Test with cuisine preferences
            user_preferences = {
                'question1': [],                      # No dietary restrictions
                'question2': 7,                       # No calorie restriction
                'question3': 6,                       # Any time
                'question4': ["italian"],             # Italian cuisine
                'question5': 2,                       # Not beginner
                'question6': ['dinner'],              # Dinner
                'question7': ['main_dish']            # Main dish
            }
            
            results = recommend_recipes(user_preferences, mock_collection)
            
            # Check results
            assert 'dinner' in results
            assert len(results['dinner']) > 0
            
            # Clean up patches
            random_uniform_patch.stop()
            random_choice_patch.stop()
            
        except ImportError:
            pytest.skip("Module could not be imported")
    
    @staticmethod
    def test_find_with_improved_relaxation():
        """Test relaxation strategy"""
        try:
            # Import the function to test
            from back_end.recipe_recommender import find_with_improved_relaxation
            
            # Create mock collection
            mock_collection = TestRecipeRecommender.create_mock_collection()
            
            # Test with complex search parameters
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
            
            result = find_with_improved_relaxation(mock_collection, search_params)
            
            # Check result - should find something
            assert result is not None
            assert isinstance(result, dict)
            assert "_id" in result
            assert "name" in result
            
            # Test with baseline only
            simple_params = {
                "query": {"tags": "main-dish"},
                "cuisine_tags": [],
                "has_calorie": False,
                "has_time": False,
                "has_diet": False,
                "diet_tags": [],
                "allergy_tags": [],
                "meal_tags": ["breakfast"],
                "dish_tags": ["main-dish"]
            }
            
            result = find_with_improved_relaxation(mock_collection, simple_params)
            assert result is not None
            
            # Test final resort
            very_specific_params = {
                "query": {"tags": "non-existent-tag"},
                "cuisine_tags": ["non-existent"],
                "has_calorie": False,
                "has_time": False,
                "has_diet": False,
                "diet_tags": [],
                "allergy_tags": [],
                "meal_tags": ["non-existent"],
                "dish_tags": ["non-existent"]
            }
            
            # This should still return something or None if nothing matches
            result = find_with_improved_relaxation(mock_collection, very_specific_params)
            assert result is None or isinstance(result, dict)
            
        except ImportError:
            pytest.skip("Module could not be imported")
