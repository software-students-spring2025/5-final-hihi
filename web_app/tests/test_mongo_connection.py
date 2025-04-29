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
def mock_db():
    """Setup mock database with test data"""
    with patch('pymongo.MongoClient') as mock_client:
        # Mock the collection
        mock_collection = MagicMock()
        
        # Configure mock find_one to return our sample recipe
        mock_collection.find_one.return_value = SAMPLE_RECIPE
        
        # Configure mock find to return a cursor with our sample recipe
        mock_cursor = MagicMock()
        mock_cursor.__iter__.return_value = iter([SAMPLE_RECIPE])
        mock_cursor.limit.return_value = mock_cursor
        mock_collection.find.return_value = mock_cursor
        
        # Mock the aggregation pipeline
        mock_collection.aggregate.return_value = iter([SAMPLE_RECIPE])
        
        # Mock count_documents
        mock_collection.count_documents.return_value = 1
        
        # Setup the database mock
        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_collection
        
        # Configure the client mock
        mock_client_instance = MagicMock()
        mock_client_instance.__getitem__.return_value = mock_db
        mock_client.return_value = mock_client_instance
        
        # Create the database instance
        db = RecipeDatabase("mongodb://mock:27017/")
        db.connect()
        
        yield db

def test_mongo_connection():
    """Test connection to MongoDB"""
    with patch('pymongo.MongoClient') as mock_client:
        # Configure the mock
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_collection.count_documents.return_value = 5
        
        mock_db.__getitem__.return_value = mock_collection
        mock_db.name = 'recipe_database'
        
        mock_client_instance = MagicMock()
        mock_client_instance.__getitem__.return_value = mock_db
        mock_client.return_value = mock_client_instance
        
        # Test the connection
        db = RecipeDatabase("mongodb://mock:27017/")
        assert db.connect() == True
        assert db.db.name == 'recipe_database'
        
        # Verify the connection was attempted correctly
        mock_client.assert_called_once()
        
def test_find_recipes(mock_db):
    """Test finding recipes"""
    recipes = mock_db.find_recipes(limit=5)
    assert len(recipes) > 0
    assert 'name' in recipes[0]
    assert 'ingredients' in recipes[0]
    assert recipes[0]['name'] == "Test Recipe"

def test_find_recipe_by_id(mock_db):
    """Test finding a recipe by ID"""
    # Test with ObjectId
    recipe_id = SAMPLE_RECIPE['_id']
    found_recipe = mock_db.find_recipe_by_id(recipe_id)
    assert found_recipe is not None
    assert found_recipe['_id'] == recipe_id
    
    # Test with string ID
    str_id = str(recipe_id)
    found_recipe = mock_db.find_recipe_by_id(str_id)
    assert found_recipe is not None
    assert str(found_recipe['_id']) == str_id
    
    # Test with non-existent ID - mock to return None
    with patch.object(mock_db.collection, 'find_one', return_value=None):
        non_existent_id = ObjectId()
        not_found = mock_db.find_recipe_by_id(non_existent_id)
        assert not_found is None

def test_search_recipes_by_name(mock_db):
    """Test search by name functionality"""
    recipes = mock_db.search_recipes_by_name("Test Recipe")
    assert len(recipes) > 0
    assert recipes[0]['name'] == "Test Recipe"
    
    # Verify the query was formed correctly
    mock_db.collection.find.assert_called_with(
        {"name": {"$regex": "Test Recipe", "$options": "i"}}
    )

def test_find_recipes_by_tags(mock_db):
    """Test find by tags functionality"""
    recipes = mock_db.find_recipes_by_tags(['breakfast'])
    assert len(recipes) > 0
    assert 'breakfast' in recipes[0]['tags']
    
    # Verify the query was formed correctly
    mock_db.collection.find.assert_called_with(
        {"tags": {"$all": ['breakfast']}}
    )

def test_find_recipes_by_ingredients(mock_db):
    """Test find by ingredients functionality"""
    recipes = mock_db.find_recipes_by_ingredients(['eggs'])
    assert len(recipes) > 0
    assert 'eggs' in recipes[0]['ingredients']
    
    # Verify the query structure
    call_args = mock_db.collection.find.call_args[0][0]
    assert '$and' in call_args
    assert len(call_args['$and']) == 1
    assert '$regex' in call_args['$and'][0]['ingredients']

def test_get_sample_recipes(mock_db):
    """Test getting sample recipes"""
    samples = mock_db.get_sample_recipes(2)
    assert len(samples) == 1  # Our mock returns just one sample
    assert samples[0]['name'] == "Test Recipe"
    
    # Verify the aggregation pipeline
    mock_db.collection.aggregate.assert_called_with(
        [{"$sample": {"size": 2}}]
    )

def test_json_encoder():
    """Test JSONEncoder for ObjectId serialization"""
    obj_id = ObjectId()
    data = {"id": obj_id, "name": "test"}
    
    # Test serialization works without errors
    json_str = json.dumps(data, cls=JSONEncoder)
    assert json_str is not None
    assert str(obj_id) in json_str
    
    # Verify the serialized data can be parsed back
    parsed = json.loads(json_str)
    assert parsed['id'] == str(obj_id)
    assert parsed['name'] == 'test'

def test_to_json(mock_db):
    """Test to_json method"""
    json_str = mock_db.to_json(SAMPLE_RECIPE)
    assert json_str is not None
    assert SAMPLE_RECIPE['name'] in json_str
    
    # Verify we can parse the JSON string back
    parsed = json.loads(json_str)
    assert parsed['name'] == SAMPLE_RECIPE['name']
    assert parsed['_id'] == str(SAMPLE_RECIPE['_id'])

def test_exception_handling():
    """Test exception handling in methods"""
    db = RecipeDatabase("mongodb://invalid:27017/")
    
    # Test connection failure
    with patch('pymongo.MongoClient', side_effect=Exception("Connection failed")):
        assert db.connect() == False
    
    # Test find_recipe_by_id exception handling
    db.collection = MagicMock()
    db.collection.find_one.side_effect = Exception("Database error")
    assert db.find_recipe_by_id("invalid_id") is None
    
    # Test find_recipes exception handling
    db.collection.find.side_effect = Exception("Database error")
    assert db.find_recipes() == []
    
    # Test get_sample_recipes exception handling
    db.collection.aggregate.side_effect = Exception("Database error")
    assert db.get_sample_recipes() == []
    
    # Test search_recipes_by_name exception handling
    assert db.search_recipes_by_name("test") == []
    
    # Test find_recipes_by_tags exception handling
    assert db.find_recipes_by_tags(["breakfast"]) == []
    
    # Test find_recipes_by_ingredients exception handling
    assert db.find_recipes_by_ingredients(["eggs"]) == []

def test_pretty_print_recipe(mock_db, capfd):
    """Test pretty_print_recipe method"""
    mock_db.pretty_print_recipe(SAMPLE_RECIPE)
    out, err = capfd.readouterr()
    
    # Verify the output contains expected content
    assert "Recipe: Test Recipe" in out
    assert "Cooking Time: 30 minutes" in out
    assert "Ingredients:" in out
    assert "Steps:" in out
    assert "Nutrition Information:" in out
    assert "Tags: breakfast, quick, easy" in out
    
    # Test with None recipe
    mock_db.pretty_print_recipe(None)
    out, err = capfd.readouterr()
    assert "No recipe found." in out
