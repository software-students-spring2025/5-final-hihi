import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Add the parent directory to path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Test for RecipeRecommendationSystem with mocks
class TestRecipeSystem:
    
    @staticmethod
    def create_mock_db():
        """Create a mock database for testing"""
        mock_db = MagicMock()
        mock_collection = MagicMock()
        
        # Setup mock recipes
        mock_recipe = {
            "_id": "mock_id",
            "name": "Test Recipe",
            "minutes": 30,
            "ingredients": ["ingredient1", "ingredient2"],
            "steps": ["step1", "step2"],
            "nutrition": {"calories": 300},
            "tags": ["breakfast", "easy"]
        }
        
        # Setup find_one, find, etc
        mock_collection.find_one.return_value = mock_recipe
        
        # For find
        class MockCursor:
            def __init__(self, recipes):
                self.recipes = recipes
            
            def limit(self, n):
                return self
                
            def __iter__(self):
                return iter(self.recipes)
                
        mock_cursor = MockCursor([mock_recipe])
        mock_collection.find.return_value = mock_cursor
        
        # Setup mock db
        mock_db.collection = mock_collection
        mock_db.connect.return_value = True
        mock_db.db = {"recipes": mock_collection}
        mock_db.find_recipe_by_id.return_value = mock_recipe
        mock_db.search_recipes_by_name.return_value = [mock_recipe]
        mock_db.find_recipes_by_tags.return_value = [mock_recipe]
        mock_db.find_recipes_by_ingredients.return_value = [mock_recipe]
        
        return mock_db
        
    @staticmethod
    def mock_recommend_recipes(user_preferences, database):
        """Mock recommendation function"""
        return {
            "breakfast": [
                {
                    "_id": "123",
                    "name": "Test Breakfast",
                    "minutes": 15,
                    "nutrition": {"calories": 200},
                    "ingredients": ["eggs", "toast"],
                    "tags": ["breakfast", "easy"]
                }
            ],
            "lunch": [
                {
                    "_id": "456",
                    "name": "Test Lunch",
                    "minutes": 30,
                    "nutrition": {"calories": 400},
                    "ingredients": ["chicken", "rice"],
                    "tags": ["lunch", "main-dish"]
                }
            ]
        }
    
    @staticmethod
    def test_init():
        """Test system initialization"""
        try:
            # Import module with mocked dependencies
            with patch('back_end.mongo_connection.RecipeDatabase') as MockDB:
                # Setup mock
                mock_db = TestRecipeSystem.create_mock_db()
                MockDB.return_value = mock_db
                
                # Import the system
                from back_end.recipe_system import RecipeRecommendationSystem
                
                # Test initialization
                system = RecipeRecommendationSystem()
                assert system.connected == True
                assert system.db is not None
        except ImportError:
            pytest.skip("Module could not be imported")
    
    @staticmethod
    def test_get_recommendations():
        """Test getting recommendations"""
        try:
            # Import with mocked dependencies
            with patch('back_end.mongo_connection.RecipeDatabase') as MockDB:
                # Setup mock db
                mock_db = TestRecipeSystem.create_mock_db()
                MockDB.return_value = mock_db
                
                # Mock the recipe_recommender
                with patch('back_end.recipe_recommender.recommend_recipes', 
                           side_effect=TestRecipeSystem.mock_recommend_recipes):
                    
                    # Import the system
                    from back_end.recipe_system import RecipeRecommendationSystem
                    
                    # Test get_recommendations
                    system = RecipeRecommendationSystem()
                    user_prefs = {
                        'question1': [],
                        'question2': 7,
                        'question3': 6,
                        'question4': ["any"],
                        'question5': 2,
                        'question6': ['breakfast'],
                        'question7': ['main_dish']
                    }
                    
                    results = system.get_recommendations(user_prefs)
                    assert 'breakfast' in results
                    assert len(results['breakfast']) > 0
                    assert results['breakfast'][0]['name'] == "Test Breakfast"
                    
                    # Test error when not connected
                    system.connected = False
                    results = system.get_recommendations(user_prefs)
                    assert results == {}
        except ImportError:
            pytest.skip("Module could not be imported")
    
    @staticmethod
    def test_display_recommendations(capsys):
        """Test displaying recommendations to console"""
        try:
            # Import with mocked dependencies
            with patch('back_end.mongo_connection.RecipeDatabase') as MockDB:
                # Setup mock db
                mock_db = TestRecipeSystem.create_mock_db()
                MockDB.return_value = mock_db
                
                # Import the system
                from back_end.recipe_system import RecipeRecommendationSystem
                
                # Test display_recommendations
                system = RecipeRecommendationSystem()
                recommendations = {
                    'breakfast': [
                        {
                            "_id": "123",
                            "name": "Test Breakfast",
                            "minutes": 15,
                            "nutrition": {"calories": 200},
                            "ingredients": ["eggs", "toast", "avocado"],
                            "tags": ["breakfast", "vegetarian", "easy"]
                        }
                    ]
                }
                
                system.display_recommendations(recommendations)
                
                # Check that output contains expected information
                captured = capsys.readouterr()
                assert "BREAKFAST RECOMMENDATIONS" in captured.out
                assert "Test Breakfast" in captured.out
                assert "15 minutes" in captured.out
                assert "calories: 200" in captured.out
        except ImportError:
            pytest.skip("Module could not be imported")
    
    @staticmethod
    def test_get_recipe_details():
        """Test getting recipe details"""
        try:
            # Import with mocked dependencies
            with patch('back_end.mongo_connection.RecipeDatabase') as MockDB:
                # Setup mock db
                mock_db = TestRecipeSystem.create_mock_db()
                MockDB.return_value = mock_db
                
                # Import the system
                from back_end.recipe_system import RecipeRecommendationSystem
                
                # Test get_recipe_details
                system = RecipeRecommendationSystem()
                recipe = system.get_recipe_details("123")
                
                # Check result
                assert recipe is not None
                assert recipe['name'] == "Test Recipe"
                mock_db.find_recipe_by_id.assert_called_with("123")
        except ImportError:
            pytest.skip("Module could not be imported")
    
    @staticmethod
    def test_search_methods():
        """Test various search methods"""
        try:
            # Import with mocked dependencies
            with patch('back_end.mongo_connection.RecipeDatabase') as MockDB:
                # Setup mock db
                mock_db = TestRecipeSystem.create_mock_db()
                MockDB.return_value = mock_db
                
                # Import the system
                from back_end.recipe_system import RecipeRecommendationSystem
                
                # Initialize system
                system = RecipeRecommendationSystem()
                
                # Test search_by_name
                results = system.search_by_name("pancakes")
                assert len(results) > 0
                mock_db.search_recipes_by_name.assert_called_with("pancakes", 10)
                
                # Test search_by_tags
                results = system.search_by_tags(["breakfast", "easy"])
                assert len(results) > 0
                mock_db.find_recipes_by_tags.assert_called_with(["breakfast", "easy"], 10)
                
                # Test search_by_ingredients
                results = system.search_by_ingredients(["eggs", "flour"])
                assert len(results) > 0
                mock_db.find_recipes_by_ingredients.assert_called_with(["eggs", "flour"], 10)
        except ImportError:
            pytest.skip("Module could not be imported")
    
    @staticmethod
    def test_export_recommendations(tmpdir):
        """Test exporting recommendations to JSON"""
        try:
            # Import with mocked dependencies
            with patch('back_end.mongo_connection.RecipeDatabase') as MockDB:
                # Setup mock db
                mock_db = TestRecipeSystem.create_mock_db()
                MockDB.return_value = mock_db
                
                # Import the system
                from back_end.recipe_system import RecipeRecommendationSystem
                
                # Test export function
                system = RecipeRecommendationSystem()
                recommendations = {
                    'breakfast': [
                        {
                            "_id": "123",
                            "name": "Test Breakfast",
                            "minutes": 15,
                            "nutrition": {"calories": 200},
                            "ingredients": ["eggs", "toast"],
                            "tags": ["breakfast", "easy"]
                        }
                    ]
                }
                
                file_path = os.path.join(tmpdir, "test_recommendations.json")
                result = system.export_recommendations_to_json(recommendations, file_path)
                
                # Check result
                assert result == True
                assert os.path.exists(file_path)
                
                # Check file content
                with open(file_path, 'r') as f:
                    content = f.read()
                    assert "Test Breakfast" in content
                    assert "eggs" in content
                    
                # Test export failure
                with patch('builtins.open', side_effect=Exception("Error")):
                    result = system.export_recommendations_to_json(recommendations, "bad_path.json")
                    assert result == False
        except ImportError:
            pytest.skip("Module could not be imported")
