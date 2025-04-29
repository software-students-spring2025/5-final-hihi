import pytest
import sys
import os
import json
from unittest.mock import patch, MagicMock

# Add the parent directory to path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Test for direct class and function tests with mocks
class TestRecipeDatabase:
    
    @staticmethod
    def create_mock_client():
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_collection = MagicMock()
        
        # Setup mock find_one
        mock_recipe = {
            "_id": "mock_id",
            "name": "Test Recipe",
            "minutes": 30,
            "ingredients": ["ingredient1", "ingredient2"],
            "steps": ["step1", "step2"],
            "nutrition": {"calories": 300},
            "tags": ["breakfast", "easy"]
        }
        mock_collection.find_one.return_value = mock_recipe
        
        # Setup mock find
        class MockCursor:
            def __init__(self, recipes):
                self.recipes = recipes
            
            def limit(self, n):
                return self
                
            def __iter__(self):
                return iter(self.recipes)
                
        mock_cursor = MockCursor([mock_recipe])
        mock_collection.find.return_value = mock_cursor
        
        # Setup mock count_documents
        mock_collection.count_documents.return_value = 1
        
        # Setup mock aggregate
        mock_collection.aggregate.return_value = [mock_recipe]
        
        # Connect the mocks
        mock_db["recipes"] = mock_collection
        mock_client["recipe_database"] = mock_db
        mock_db.name = "recipe_database"
        mock_collection.name = "recipes"
        
        return mock_client, mock_db, mock_collection
    
    @staticmethod
    def test_connect():
        # Import module
        try:
            from back_end.mongo_connection import RecipeDatabase
            
            # Create test instance
            with patch('pymongo.MongoClient') as mock_client_class:
                mock_client, mock_db, mock_collection = TestRecipeDatabase.create_mock_client()
                mock_client_class.return_value = mock_client
                
                # Test connection
                db = RecipeDatabase("mongodb://test:1234@localhost")
                result = db.connect()
                
                # Verify it works
                assert result == True
                assert db.db.name == "recipe_database"
                assert db.collection.name == "recipes"
                
                # Test with failure
                mock_client_class.side_effect = Exception("Connection failed")
                db = RecipeDatabase("mongodb://bad:1234@localhost")
                result = db.connect()
                assert result == False
                
        except ImportError:
            pytest.skip("Module could not be imported")
    
    @staticmethod
    def test_close():
        # Import module
        try:
            from back_end.mongo_connection import RecipeDatabase
            
            # Create test instance
            with patch('pymongo.MongoClient') as mock_client_class:
                mock_client, mock_db, mock_collection = TestRecipeDatabase.create_mock_client()
                mock_client_class.return_value = mock_client
                
                # Test close
                db = RecipeDatabase("mongodb://test")
                db.client = mock_client
                db.close()
                
                # Verify it works
                mock_client.close.assert_called_once()
                
        except ImportError:
            pytest.skip("Module could not be imported")
    
    @staticmethod
    def test_find_recipe_by_id():
        # Import module
        try:
            from back_end.mongo_connection import RecipeDatabase
            from bson import ObjectId
            
            # Create test instance
            with patch('pymongo.MongoClient') as mock_client_class:
                mock_client, mock_db, mock_collection = TestRecipeDatabase.create_mock_client()
                mock_client_class.return_value = mock_client
                
                # Setup instance
                db = RecipeDatabase("mongodb://test")
                db.client = mock_client
                db.db = mock_db
                db.collection = mock_collection
                
                # Test with string ID
                result = db.find_recipe_by_id("123")
                assert result == mock_collection.find_one.return_value
                mock_collection.find_one.assert_called_with({"_id": ObjectId("123")})
                
                # Test with error
                mock_collection.find_one.side_effect = Exception("Error")
                result = db.find_recipe_by_id("123")
                assert result is None
                
        except ImportError:
            pytest.skip("Module could not be imported")
    
    @staticmethod
    def test_find_recipes():
        # Import module
        try:
            from back_end.mongo_connection import RecipeDatabase
            
            # Create test instance
            with patch('pymongo.MongoClient') as mock_client_class:
                mock_client, mock_db, mock_collection = TestRecipeDatabase.create_mock_client()
                mock_client_class.return_value = mock_client
                
                # Setup instance
                db = RecipeDatabase("mongodb://test")
                db.client = mock_client
                db.db = mock_db
                db.collection = mock_collection
                
                # Test find_recipes
                results = db.find_recipes(query={"tags": "breakfast"}, limit=5)
                assert len(results) > 0
                mock_collection.find.assert_called_with({"tags": "breakfast"})
                
                # Test with error
                mock_collection.find.side_effect = Exception("Error")
                results = db.find_recipes(query={"tags": "breakfast"}, limit=5)
                assert results == []
                
        except ImportError:
            pytest.skip("Module could not be imported")

    @staticmethod
    def test_get_sample_recipes():
        # Import module
        try:
            from back_end.mongo_connection import RecipeDatabase
            
            # Create test instance
            with patch('pymongo.MongoClient') as mock_client_class:
                mock_client, mock_db, mock_collection = TestRecipeDatabase.create_mock_client()
                mock_client_class.return_value = mock_client
                
                # Setup instance
                db = RecipeDatabase("mongodb://test")
                db.client = mock_client
                db.db = mock_db
                db.collection = mock_collection
                
                # Test get_sample_recipes
                results = db.get_sample_recipes(count=3)
                assert len(results) > 0
                mock_collection.aggregate.assert_called_with([{"$sample": {"size": 3}}])
                
                # Test with error
                mock_collection.aggregate.side_effect = Exception("Error")
                results = db.get_sample_recipes(count=3)
                assert results == []
                
        except ImportError:
            pytest.skip("Module could not be imported")
            
    @staticmethod
    def test_search_recipes_by_name():
        # Import module
        try:
            from back_end.mongo_connection import RecipeDatabase
            
            # Create test instance
            with patch('pymongo.MongoClient') as mock_client_class:
                mock_client, mock_db, mock_collection = TestRecipeDatabase.create_mock_client()
                mock_client_class.return_value = mock_client
                
                # Setup instance
                db = RecipeDatabase("mongodb://test")
                db.client = mock_client
                db.db = mock_db
                db.collection = mock_collection
                
                # Test search_recipes_by_name
                results = db.search_recipes_by_name("pancakes", limit=5)
                assert len(results) > 0
                mock_collection.find.assert_called_with({"name": {"$regex": "pancakes", "$options": "i"}})
                
                # Test with error
                mock_collection.find.side_effect = Exception("Error")
                results = db.search_recipes_by_name("pancakes", limit=5)
                assert results == []
                
        except ImportError:
            pytest.skip("Module could not be imported")

    @staticmethod
    def test_JSONEncoder():
        # Import module
        try:
            from back_end.mongo_connection import JSONEncoder
            from bson import ObjectId
            
            # Test encoding ObjectId
            encoder = JSONEncoder()
            obj_id = ObjectId()
            result = encoder.default(obj_id)
            assert result == str(obj_id)
            
            # Test with non-ObjectId
            with pytest.raises(TypeError):
                encoder.default(complex(1, 2))
                
        except ImportError:
            pytest.skip("Module could not be imported")
            
    @staticmethod
    def test_to_json():
        # Import module
        try:
            from back_end.mongo_connection import RecipeDatabase
            
            # Create test instance
            with patch('pymongo.MongoClient') as mock_client_class:
                mock_client, mock_db, mock_collection = TestRecipeDatabase.create_mock_client()
                mock_client_class.return_value = mock_client
                
                # Setup instance
                db = RecipeDatabase("mongodb://test")
                db.client = mock_client
                db.db = mock_db
                db.collection = mock_collection
                
                # Test to_json
                data = {"_id": "123", "name": "Test"}
                json_str = db.to_json(data)
                assert json_str is not None
                assert "123" in json_str
                assert "Test" in json_str
                
        except ImportError:
            pytest.skip("Module could not be imported")
