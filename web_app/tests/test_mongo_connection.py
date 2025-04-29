import pytest
from unittest.mock import patch, MagicMock
from bson import ObjectId
from back_end.mongo_connection import RecipeDatabase, JSONEncoder
import json

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

# Patch the MongoClient at the module level to avoid actual MongoDB connections
@pytest.fixture(autouse=True)
def mock_mongo_client():
    with patch('back_end.mongo_connection.MongoClient') as mock_client:
        # Setup mock collection
        mock_collection = MagicMock()
        mock_collection.count_documents.return_value = 5
        mock_collection.find_one.return_value = SAMPLE_RECIPE
        
        # Configure find to return our sample recipe
        mock_cursor = MagicMock()
        mock_cursor.limit.return_value = [SAMPLE_RECIPE]
        mock_collection.find.return_value = mock_cursor
        
        # Configure aggregate to return our sample recipe
        mock_collection.aggregate.return_value = [SAMPLE_RECIPE]
        
        # Setup mock database
        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_collection
        mock_db.name = 'recipe_database'
        
        # Setup mock client
        mock_client_instance = MagicMock()
        mock_client_instance.__getitem__.return_value = mock_db
        mock_client.return_value = mock_client_instance
        
        yield mock_client

def test_mongo_connection():
    """Test connection to MongoDB"""
    db = RecipeDatabase("mongodb://localhost:27017/")
    # Test the connection
    assert db.connect() == True
    # Test database and collection access
    assert db.db.name == 'recipe_database'
    assert hasattr(db, 'collection')

def test_find_recipes():
    """Test finding recipes"""
    db = RecipeDatabase("mongodb://localhost:27017/")
    db.connect()
    recipes = db.find_recipes(limit=5)
    assert len(recipes) > 0
    assert 'name' in recipes[0]
    assert 'ingredients' in recipes[0]
    assert recipes[0]['name'] == "Test Recipe"

def test_find_recipe_by_id():
    """Test finding a recipe by ID"""
    db = RecipeDatabase("mongodb://localhost:27017/")
    db.connect()
    
    # Test with ObjectId
    recipe_id = SAMPLE_RECIPE['_id']
    found_recipe = db.find_recipe_by_id(recipe_id)
    assert found_recipe is not None
    assert found_recipe['_id'] == recipe_id
    
    # Test with string ID
    str_id = str(recipe_id)
    found_recipe = db.find_recipe_by_id(str_id)
    assert found_recipe is not None
    assert str(found_recipe['_id']) == str_id
    
    # Test with non-existent ID - mock to return None
    with patch.object(db.collection, 'find_one', return_value=None):
        non_existent_id = ObjectId()
        not_found = db.find_recipe_by_id(non_existent_id)
        assert not_found is None

def test_search_recipes_by_name():
    """Test search by name functionality"""
    db = RecipeDatabase("mongodb://localhost:27017/")
    db.connect()
    recipes = db.search_recipes_by_name("Test Recipe")
    assert len(recipes) > 0
    assert recipes[0]['name'] == "Test Recipe"

def test_find_recipes_by_tags():
    """Test find by tags functionality"""
    db = RecipeDatabase("mongodb://localhost:27017/")
    db.connect()
    recipes = db.find_recipes_by_tags(['breakfast'])
    assert len(recipes) > 0
    assert 'breakfast' in recipes[0]['tags']

def test_find_recipes_by_ingredients():
    """Test find by ingredients functionality"""
    db = RecipeDatabase("mongodb://localhost:27017/")
    db.connect()
    recipes = db.find_recipes_by_ingredients(['eggs'])
    assert len(recipes) > 0
    assert 'eggs' in recipes[0]['ingredients']

def test_get_sample_recipes():
    """Test getting sample recipes"""
    db = RecipeDatabase("mongodb://localhost:27017/")
    db.connect()
    samples = db.get_sample_recipes(2)
    assert len(samples) == 1  # Our mock returns just one sample
    assert samples[0]['name'] == "Test Recipe"

def test_json_encoder():
    """Test JSONEncoder for ObjectId serialization"""
    obj_id = ObjectId("507f1f77bcf86cd799439011")
    data = {"id": obj_id, "name": "test"}
    
    # Test serialization works without errors
    encoder = JSONEncoder()
    json_str = encoder.encode(data)
    assert "507f1f77bcf86cd799439011" in json_str
    
    # Test with json.dumps
    json_str = json.dumps(data, cls=JSONEncoder)
    assert json_str is not None
    assert "507f1f77bcf86cd799439011" in json_str
    
    # Verify the serialized data can be parsed back
    parsed = json.loads(json_str)
    assert parsed['id'] == "507f1f77bcf86cd799439011"
    assert parsed['name'] == 'test'

def test_to_json():
    """Test to_json method"""
    db = RecipeDatabase("mongodb://localhost:27017/")
    db.connect()
    json_str = db.to_json(SAMPLE_RECIPE)
    assert json_str is not None
    assert SAMPLE_RECIPE['name'] in json_str
    
    # Verify we can parse the JSON string back
    parsed = json.loads(json_str)
    assert parsed['name'] == SAMPLE_RECIPE['name']
    assert parsed['_id'] == str(SAMPLE_RECIPE['_id'])

def test_exception_handling():
    """Test exception handling in methods"""
    # Test connection failure
    with patch('back_end.mongo_connection.MongoClient', side_effect=Exception("Connection failed")):
        db = RecipeDatabase("mongodb://invalid:27017/")
        assert db.connect() == False
    
    # Test find_recipe_by_id exception handling
    db = RecipeDatabase("mongodb://localhost:27017/")
    db.connect()
    with patch.object(db.collection, 'find_one', side_effect=Exception("Database error")):
        assert db.find_recipe_by_id("invalid_id") is None
    
    # Test find_recipes exception handling
    with patch.object(db.collection, 'find', side_effect=Exception("Database error")):
        assert db.find_recipes() == []
    
    # Test get_sample_recipes exception handling
    with patch.object(db.collection, 'aggregate', side_effect=Exception("Database error")):
        assert db.get_sample_recipes() == []
    
    # Test search_recipes_by_name exception handling
    with patch.object(db.collection, 'find', side_effect=Exception("Database error")):
        assert db.search_recipes_by_name("test") == []
    
    # Test find_recipes_by_tags exception handling
    with patch.object(db.collection, 'find', side_effect=Exception("Database error")):
        assert db.find_recipes_by_tags(["breakfast"]) == []
    
    # Test find_recipes_by_ingredients exception handling
    with patch.object(db.collection, 'find', side_effect=Exception("Database error")):
        assert db.find_recipes_by_ingredients(["eggs"]) == []

def test_pretty_print_recipe(capfd):
    """Test pretty_print_recipe method"""
    db = RecipeDatabase("mongodb://localhost:27017/")
    
    # Call the actual method
    db.pretty_print_recipe(SAMPLE_RECIPE)
    out, err = capfd.readouterr()
    
    # Verify the output contains expected content
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
