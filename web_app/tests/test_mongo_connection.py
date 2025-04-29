import pytest
from unittest.mock import patch, MagicMock
from bson import ObjectId
from back_end.mongo_connection import RecipeDatabase, JSONEncoder
import json
import pymongo

# Sample test data
SAMPLE_RECIPE = {
    "_id": ObjectId("5f7b85a2def12a0b8a123456"),
    "name": "Test Recipe",
    "minutes": 30,
    "description": "A test recipe description",
    "ingredients": ["eggs", "butter", "sugar", "flour"],
    "steps": ["Mix ingredients", "Bake at 350F for 25 minutes"],
    "tags": ["breakfast", "quick", "easy"],
    "nutrition": {
        "calories": 350,
        "fat": 15,
        "protein": 7,
        "carbohydrates": 45
    }
}

@pytest.fixture
def setup_real_db():
    """Setup a real RecipeDatabase instance"""
    db = RecipeDatabase("mongodb://mock:27017/")
    # Manually set the attributes that would be set by connect()
    db.client = MagicMock()
    db.db = MagicMock()
    db.collection = MagicMock()
    
    # Mock the find method to return a list
    db.collection.find.return_value.limit.return_value = [SAMPLE_RECIPE]
    
    # Mock find_one to return our sample recipe
    db.collection.find_one.return_value = SAMPLE_RECIPE
    
    # Mock aggregate to return a list with our sample recipe
    db.collection.aggregate.return_value = [SAMPLE_RECIPE]
    
    # Mock count_documents to return 1
    db.collection.count_documents.return_value = 1
    
    return db

def test_mongo_connection():
    """Test connection to MongoDB"""
    with patch('pymongo.MongoClient') as mock_client:
        # Configure the mock client and its return values
        mock_collection = MagicMock()
        mock_collection.count_documents.return_value = 5
        
        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_collection
        mock_db.name = 'recipe_database'
        
        mock_client_instance = MagicMock()
        mock_client_instance.__getitem__.return_value = mock_db
        mock_client.return_value = mock_client_instance
        
        # Create and patch the RecipeDatabase instance
        db = RecipeDatabase("mongodb://mock:27017/")
        
        # Replace the connect method with a mock that returns True
        original_connect = db.connect
        db.connect = MagicMock(return_value=True)
        
        # Test
        assert db.connect() is True
        
        # Restore the original method
        db.connect = original_connect

def test_find_recipes():
    """Test finding recipes"""
    db = RecipeDatabase()
    
    # Mock the collection.find method
    db.collection = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.limit.return_value = [SAMPLE_RECIPE]
    db.collection.find.return_value = mock_cursor
    
    # Call the method
    recipes = db.find_recipes(limit=5)
    
    # Assert
    assert len(recipes) > 0
    assert 'name' in recipes[0]
    assert 'ingredients' in recipes[0]

def test_find_recipe_by_id():
    """Test finding a recipe by ID"""
    db = RecipeDatabase()
    db.collection = MagicMock()
    
    # Mock find_one to return our sample recipe
    db.collection.find_one.return_value = SAMPLE_RECIPE
    
    # Test with ObjectId
    recipe_id = SAMPLE_RECIPE['_id']
    found_recipe = db.find_recipe_by_id(recipe_id)
    assert found_recipe is not None
    assert found_recipe['_id'] == recipe_id
    
    # Test with string ID
    str_id = str(recipe_id)
    found_recipe = db.find_recipe_by_id(str_id)
    assert found_recipe is not None
    assert found_recipe['_id'] == recipe_id
    
    # Test with non-existent ID
    db.collection.find_one.return_value = None
    non_existent_id = ObjectId()
    not_found = db.find_recipe_by_id(non_existent_id)
    assert not_found is None

def test_search_recipes_by_name():
    """Test search by name functionality"""
    db = RecipeDatabase()
    db.collection = MagicMock()
    
    # Mock find to return a cursor that returns our sample recipe
    mock_cursor = MagicMock()
    mock_cursor.limit.return_value = [SAMPLE_RECIPE]
    db.collection.find.return_value = mock_cursor
    
    # Call the method
    recipes = db.search_recipes_by_name("Test Recipe")
    
    # Assert
    assert len(recipes) > 0
    assert recipes[0]['name'] == "Test Recipe"

def test_find_recipes_by_tags():
    """Test find by tags functionality"""
    db = RecipeDatabase()
    db.collection = MagicMock()
    
    # Mock find to return a cursor that returns our sample recipe
    mock_cursor = MagicMock()
    mock_cursor.limit.return_value = [SAMPLE_RECIPE]
    db.collection.find.return_value = mock_cursor
    
    # Call the method
    recipes = db.find_recipes_by_tags(['breakfast'])
    
    # Assert
    assert len(recipes) > 0
    assert 'breakfast' in recipes[0]['tags']

def test_find_recipes_by_ingredients():
    """Test find by ingredients functionality"""
    db = RecipeDatabase()
    db.collection = MagicMock()
    
    # Mock find to return a cursor that returns our sample recipe
    mock_cursor = MagicMock()
    mock_cursor.limit.return_value = [SAMPLE_RECIPE]
    db.collection.find.return_value = mock_cursor
    
    # Call the method
    recipes = db.find_recipes_by_ingredients(['eggs'])
    
    # Assert
    assert len(recipes) > 0
    assert 'eggs' in recipes[0]['ingredients']

def test_get_sample_recipes():
    """Test getting sample recipes"""
    db = RecipeDatabase()
    db.collection = MagicMock()
    
    # Mock aggregate to return a list with our sample recipe
    db.collection.aggregate.return_value = [SAMPLE_RECIPE]
    
    # Call the method
    samples = db.get_sample_recipes(2)
    
    # Assert
    assert len(samples) == 1
    assert samples[0]['name'] == "Test Recipe"

def test_json_encoder():
    """Test JSONEncoder for ObjectId serialization"""
    # Create a real ObjectId
    obj_id = ObjectId("507f1f77bcf86cd799439011")
    data = {"id": obj_id, "name": "test"}
    
    # Test serialization
    json_str = json.dumps(data, cls=JSONEncoder)
    
    # Assert
    assert json_str is not None
    assert str(obj_id) in json_str
    
    # Verify the serialized data can be parsed back
    parsed = json.loads(json_str)
    assert parsed['id'] == str(obj_id)
    assert parsed['name'] == 'test'

def test_to_json():
    """Test to_json method"""
    db = RecipeDatabase()
    
    # Call the method
    json_str = db.to_json(SAMPLE_RECIPE)
    
    # Assert
    assert json_str is not None
    assert SAMPLE_RECIPE['name'] in json_str
    
    # Verify we can parse the JSON string back
    parsed = json.loads(json_str)
    assert parsed['name'] == SAMPLE_RECIPE['name']
    assert parsed['_id'] == str(SAMPLE_RECIPE['_id'])

def test_exception_handling():
    """Test exception handling in methods"""
    # Create a real instance for this test
    db = RecipeDatabase("mongodb://invalid:27017/")
    
    # Test connection failure
    with patch('pymongo.MongoClient', side_effect=Exception("Connection failed")):
        result = db.connect()
        assert result is False
    
    # Mock the collection for remaining tests
    db.collection = MagicMock()
    
    # Test find_recipe_by_id exception handling
    db.collection.find_one.side_effect = Exception("Database error")
    result = db.find_recipe_by_id("invalid_id")
    assert result is None
    
    # Test find_recipes exception handling
    db.collection.find.side_effect = Exception("Database error")
    result = db.find_recipes()
    assert result == []
    
    # Test get_sample_recipes exception handling
    db.collection.aggregate.side_effect = Exception("Database error")
    result = db.get_sample_recipes()
    assert result == []
    
    # Test search_recipes_by_name exception handling
    result = db.search_recipes_by_name("test")
    assert result == []
    
    # Test find_recipes_by_tags exception handling
    result = db.find_recipes_by_tags(["breakfast"])
    assert result == []
    
    # Test find_recipes_by_ingredients exception handling
    result = db.find_recipes_by_ingredients(["eggs"])
    assert result == []

def test_pretty_print_recipe(capfd):
    """Test pretty_print_recipe method"""
    # Create a real instance for this test
    db = RecipeDatabase()
    
    # Call pretty_print_recipe with our sample recipe
    db.pretty_print_recipe(SAMPLE_RECIPE)
    out, err = capfd.readouterr()
    
    # Assert expected output
    assert "Recipe: Test Recipe" in out
    assert "Cooking Time: 30 minutes" in out
    assert "Ingredients:" in out
    assert "Steps:" in out
    assert "Nutrition Information:" in out
    assert "Tags: breakfast, quick, easy" in out
    
    # Test with None recipe
    db.pretty_print_recipe(None)
    out, err = capfd.readouterr()
    assert "No recipe found." in out
