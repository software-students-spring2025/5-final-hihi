import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from back_end.mongo_connection import RecipeDatabase, JSONEncoder
from bson import ObjectId
import json

class TestJSONEncoder:
    def test_default_with_object_id(self):
        # Test that ObjectId is converted to string
        encoder = JSONEncoder()
        obj_id = ObjectId('507f1f77bcf86cd799439011')
        result = encoder.default(obj_id)
        assert result == '507f1f77bcf86cd799439011'
        
    def test_default_with_other_object(self):
        # Test that other objects are handled by the parent class
        encoder = JSONEncoder()
        with pytest.raises(TypeError):
            encoder.default('not an ObjectId')

class TestRecipeDatabase:
    @patch('back_end.mongo_connection.MongoClient')
    def test_connect_success(self, mock_mongo_client):
        # Setup mock
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_collection.count_documents.return_value = 5
        
        mock_client.__getitem__.return_value = mock_db
        mock_db.__getitem__.return_value = mock_collection
        mock_mongo_client.return_value = mock_client
        
        # Test connect method
        db = RecipeDatabase(uri="mongodb://test_uri")
        result = db.connect()
        
        # Assertions
        assert result is True
        mock_mongo_client.assert_called_once_with(
            "mongodb://test_uri",
            connectTimeoutMS=30000,
            socketTimeoutMS=30000,
            retryWrites=True,
            tls=True
        )
        assert db.client == mock_client
        assert db.db == mock_db
        assert db.collection == mock_collection
        mock_collection.count_documents.assert_called_once_with({})
    
    @patch('back_end.mongo_connection.MongoClient')
    def test_connect_failure(self, mock_mongo_client):
        # Setup mock to raise exception
        mock_mongo_client.side_effect = Exception("Connection error")
        
        # Test connect method
        db = RecipeDatabase(uri="mongodb://test_uri")
        result = db.connect()
        
        # Assertions
        assert result is False
        mock_mongo_client.assert_called_once()
    
    def test_close(self):
        # Setup
        db = RecipeDatabase()
        db.client = MagicMock()
        
        # Test close method
        db.close()
        
        # Assertions
        db.client.close.assert_called_once()
    
    @patch('back_end.mongo_connection.ObjectId')
    def test_find_recipe_by_id_string(self, mock_object_id):
        # Setup
        db = RecipeDatabase()
        db.collection = MagicMock()
        mock_recipe = {'name': 'Test Recipe'}
        db.collection.find_one.return_value = mock_recipe
        mock_obj_id = MagicMock()
        mock_object_id.return_value = mock_obj_id
        
        # Test find_recipe_by_id with string
        result = db.find_recipe_by_id('507f1f77bcf86cd799439011')
        
        # Assertions
        mock_object_id.assert_called_once_with('507f1f77bcf86cd799439011')
        db.collection.find_one.assert_called_once_with({"_id": mock_obj_id})
        assert result == mock_recipe
    
    def test_find_recipe_by_id_object_id(self):
        # Setup
        db = RecipeDatabase()
        db.collection = MagicMock()
        mock_recipe = {'name': 'Test Recipe'}
        db.collection.find_one.return_value = mock_recipe
        obj_id = ObjectId('507f1f77bcf86cd799439011')
        
        # Test find_recipe_by_id with ObjectId
        result = db.find_recipe_by_id(obj_id)
        
        # Assertions
        db.collection.find_one.assert_called_once_with({"_id": obj_id})
        assert result == mock_recipe
    
    def test_find_recipes(self):
        # Setup
        db = RecipeDatabase()
        db.collection = MagicMock()
        mock_recipes = [{'name': 'Recipe 1'}, {'name': 'Recipe 2'}]
        mock_cursor = MagicMock()
        mock_cursor.limit.return_value = mock_recipes
        db.collection.find.return_value = mock_cursor
        
        # Test find_recipes
        result = db.find_recipes({'tags': 'vegetarian'}, 5)
        
        # Assertions
        db.collection.find.assert_called_once_with({'tags': 'vegetarian'})
        mock_cursor.limit.assert_called_once_with(5)
        assert result == mock_recipes
    
    def test_to_json(self):
        # Setup
        db = RecipeDatabase()
        test_data = {'_id': ObjectId('507f1f77bcf86cd799439011'), 'name': 'Test Recipe'}
        
        # Test to_json
        result = db.to_json(test_data)
        
        # Parse the result back to ensure it's valid JSON
        parsed = json.loads(result)
        
        # Assertions
        assert parsed['_id'] == '507f1f77bcf86cd799439011'
        assert parsed['name'] == 'Test Recipe'
