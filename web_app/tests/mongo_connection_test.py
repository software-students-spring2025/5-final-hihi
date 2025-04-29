import pytest
from bson import ObjectId
from web_app.back_end.mongo_connection import RecipeDatabase, JSONEncoder
import json
from unittest.mock import MagicMock, patch

@patch("web_app.back_end.mongo_connection.MongoClient")
def test_mongo_connection(mock_mongo):
    mock_client = MagicMock()
    mock_db = MagicMock()
    mock_collection = MagicMock()
    mock_db.__getitem__.return_value = mock_collection
    mock_client.__getitem__.return_value = mock_db
    mock_mongo.return_value = mock_client

    db = RecipeDatabase("mongodb://localhost:27017/")
    assert db.connect() is True
    assert db.db == mock_db
    assert db.collection == mock_collection

@patch("web_app.back_end.mongo_connection.MongoClient")
def test_find_recipes(mock_mongo):
    mock_collection = MagicMock()
    mock_collection.find.return_value.limit.return_value = [{"name": "Mock Recipe", "ingredients": ["egg"]}]
    mock_db = MagicMock()
    mock_db.__getitem__.return_value = mock_collection
    mock_client = MagicMock()
    mock_client.__getitem__.return_value = mock_db
    mock_mongo.return_value = mock_client

    db = RecipeDatabase()
    db.connect()
    recipes = db.find_recipes(limit=5)
    assert len(recipes) > 0
    assert 'name' in recipes[0]
    assert 'ingredients' in recipes[0]

@patch("web_app.back_end.mongo_connection.MongoClient")
def test_find_recipe_by_id(mock_mongo):
    mock_client = MagicMock()
    mock_db = MagicMock()
    mock_collection = MagicMock()
    mock_collection.find_one.return_value = {'_id': 1, 'name': 'Test'}
    mock_db.__getitem__.return_value = mock_collection
    mock_client.__getitem__.return_value = mock_db
    mock_mongo.return_value = mock_client

    db = RecipeDatabase()
    db.connect()
    recipe = db.find_recipe_by_id('64e768aa0123456789abcdef')
    assert recipe['name'] == 'Test'

@patch("web_app.back_end.mongo_connection.MongoClient")
def test_find_recipe_by_id_invalid(mock_mongo):
    mock_collection = MagicMock()
    mock_collection.find_one.side_effect = Exception("Invalid ID")
    mock_db = MagicMock()
    mock_db.__getitem__.return_value = mock_collection
    mock_client = MagicMock()
    mock_client.__getitem__.return_value = mock_db
    mock_mongo.return_value = mock_client

    db = RecipeDatabase()
    db.connect()
    recipe = db.find_recipe_by_id(None)
    assert recipe is None

@patch("web_app.back_end.mongo_connection.MongoClient")
def test_search_recipes_by_name(mock_mongo):
    mock_collection = MagicMock()
    mock_collection.find.return_value.limit.return_value = [{"name": "Test Recipe"}]
    mock_db = MagicMock()
    mock_db.__getitem__.return_value = mock_collection
    mock_client = MagicMock()
    mock_client.__getitem__.return_value = mock_db
    mock_mongo.return_value = mock_client

    db = RecipeDatabase()
    db.connect()
    recipes = db.search_recipes_by_name("Test Recipe")
    assert len(recipes) > 0
    assert "Test Recipe" in recipes[0]['name']

@patch("web_app.back_end.mongo_connection.MongoClient")
def test_search_recipes_by_name_error(mock_mongo):
    mock_collection = MagicMock()
    mock_collection.find.side_effect = Exception("Error")
    mock_db = MagicMock()
    mock_db.__getitem__.return_value = mock_collection
    mock_client = MagicMock()
    mock_client.__getitem__.return_value = mock_db
    mock_mongo.return_value = mock_client

    db = RecipeDatabase()
    db.connect()
    results = db.search_recipes_by_name("Anything")
    assert results == []

@patch("web_app.back_end.mongo_connection.MongoClient")
def test_find_recipes_by_tags(mock_mongo):
    mock_collection = MagicMock()
    mock_collection.find.return_value.limit.return_value = [{"tags": ["breakfast"]}]
    mock_db = MagicMock()
    mock_db.__getitem__.return_value = mock_collection
    mock_client = MagicMock()
    mock_client.__getitem__.return_value = mock_db
    mock_mongo.return_value = mock_client

    db = RecipeDatabase()
    db.connect()
    recipes = db.find_recipes_by_tags(['breakfast'])
    assert len(recipes) > 0
    assert 'breakfast' in recipes[0]['tags']

@patch("web_app.back_end.mongo_connection.MongoClient")
def test_find_recipes_by_ingredients(mock_mongo):
    mock_collection = MagicMock()
    mock_collection.find.return_value.limit.return_value = [{"ingredients": ["eggs"]}]
    mock_db = MagicMock()
    mock_db.__getitem__.return_value = mock_collection
    mock_client = MagicMock()
    mock_client.__getitem__.return_value = mock_db
    mock_mongo.return_value = mock_client

    db = RecipeDatabase()
    db.connect()
    recipes = db.find_recipes_by_ingredients(['eggs'])
    assert len(recipes) > 0
    assert any('eggs' in ingredient.lower() for ingredient in recipes[0]['ingredients'])

@patch("web_app.back_end.mongo_connection.MongoClient")
def test_find_recipes_by_ingredients_error(mock_mongo):
    mock_collection = MagicMock()
    mock_collection.find.side_effect = Exception("Ingredient error")
    mock_db = MagicMock()
    mock_db.__getitem__.return_value = mock_collection
    mock_client = MagicMock()
    mock_client.__getitem__.return_value = mock_db
    mock_mongo.return_value = mock_client

    db = RecipeDatabase()
    db.connect()
    results = db.find_recipes_by_ingredients(['onion'])
    assert results == []

@patch("web_app.back_end.mongo_connection.MongoClient")
def test_get_sample_recipes(mock_mongo):
    mock_collection = MagicMock()
    mock_collection.aggregate.return_value = [{"name": "Sample"}]
    mock_db = MagicMock()
    mock_db.__getitem__.return_value = mock_collection
    mock_client = MagicMock()
    mock_client.__getitem__.return_value = mock_db
    mock_mongo.return_value = mock_client

    db = RecipeDatabase()
    db.connect()
    samples = db.get_sample_recipes(2)
    assert len(samples) > 0
    assert len(samples) <= 2

@patch("web_app.back_end.mongo_connection.MongoClient")
def test_pretty_print_recipe_empty(mock_mongo):
    db = RecipeDatabase()
    db.pretty_print_recipe(None)  # Should print 'No recipe found.' and return

@patch("web_app.back_end.mongo_connection.MongoClient")
def test_to_json(mock_mongo):
    mock_collection = MagicMock()
    mock_collection.find_one.return_value = {'name': 'Test'}
    mock_db = MagicMock()
    mock_db.__getitem__.return_value = mock_collection
    mock_client = MagicMock()
    mock_client.__getitem__.return_value = mock_db
    mock_mongo.return_value = mock_client

    db = RecipeDatabase()
    db.connect()
    recipe = db.collection.find_one()
    json_str = db.to_json(recipe)
    assert json_str is not None
    assert recipe['name'] in json_str

def test_json_encoder():
    obj_id = ObjectId()
    data = {"id": obj_id, "name": "test"}
    json_str = json.dumps(data, cls=JSONEncoder)
    assert json_str is not None
    assert str(obj_id) in json_str

def test_json_encoder_fallback_to_super():
    class UnserializableObject:
        pass

    obj = {"custom": UnserializableObject()}

    with pytest.raises(TypeError):
        json.dumps(obj, cls=JSONEncoder)

@patch("web_app.back_end.mongo_connection.MongoClient", side_effect=Exception("Mock connection error"))
def test_connect_exception(mock_mongo):
    db = RecipeDatabase("mongodb://invalid-uri")
    success = db.connect()
    assert success is False

def test_close_connection(capsys):
    db = RecipeDatabase()
    mock_client = MagicMock()
    db.client = mock_client

    db.close()

    # Check that close() was called
    mock_client.close.assert_called_once()

    # Capture and assert the print output
    captured = capsys.readouterr()
    assert "Connection closed." in captured.out

@patch("web_app.back_end.mongo_connection.MongoClient")
def test_find_recipes_error(mock_mongo, capsys):
    # Setup mock to raise an exception
    mock_collection = MagicMock()
    mock_collection.find.side_effect = Exception("Mock query failure")
    mock_db = MagicMock()
    mock_db.__getitem__.return_value = mock_collection
    mock_client = MagicMock()
    mock_client.__getitem__.return_value = mock_db
    mock_mongo.return_value = mock_client

    # Create instance and trigger the error path
    db = RecipeDatabase()
    db.connect()
    results = db.find_recipes(query={"tags": "lunch"}, limit=3)

    # Verify fallback behavior
    assert results == []

    # Check that error message was printed
    captured = capsys.readouterr()
    assert "Error finding recipes: Mock query failure" in captured.out

@patch("web_app.back_end.mongo_connection.MongoClient")
def test_get_sample_recipes_error(mock_mongo, capsys):
    # Simulate error in aggregate call
    mock_collection = MagicMock()
    mock_collection.aggregate.side_effect = Exception("Aggregation failed")
    mock_db = MagicMock()
    mock_db.__getitem__.return_value = mock_collection
    mock_client = MagicMock()
    mock_client.__getitem__.return_value = mock_db
    mock_mongo.return_value = mock_client

    db = RecipeDatabase()
    db.connect()
    samples = db.get_sample_recipes(3)

    assert samples == []

    captured = capsys.readouterr()
    assert "Error getting sample recipes: Aggregation failed" in captured.out

@patch("web_app.back_end.mongo_connection.MongoClient")
def test_find_recipes_by_tags_error(mock_mongo, capsys):
    # Mock collection to raise an error
    mock_collection = MagicMock()
    mock_collection.find.side_effect = Exception("Tag query failed")
    mock_db = MagicMock()
    mock_db.__getitem__.return_value = mock_collection
    mock_client = MagicMock()
    mock_client.__getitem__.return_value = mock_db
    mock_mongo.return_value = mock_client

    db = RecipeDatabase()
    db.connect()
    results = db.find_recipes_by_tags(["vegan"])

    assert results == []

    captured = capsys.readouterr()
    assert "Error finding recipes by tags: Tag query failed" in captured.out

def test_pretty_print_recipe_none(capsys):
    db = RecipeDatabase()
    db.pretty_print_recipe(None)
    captured = capsys.readouterr()
    assert "No recipe found." in captured.out

def test_pretty_print_recipe_full(capsys):
    db = RecipeDatabase()
    recipe = {
        "name": "Test Recipe",
        "minutes": 30,
        "description": "A tasty test recipe.",
        "ingredients": ["egg", "milk", "flour"],
        "steps": ["Mix ingredients", "Bake for 30 minutes"],
        "nutrition": {"calories": 300, "protein": "10g"},
        "tags": ["breakfast", "easy"]
    }
    db.pretty_print_recipe(recipe)
    captured = capsys.readouterr()
    assert "Recipe: Test Recipe" in captured.out
    assert "Cooking Time: 30 minutes" in captured.out
    assert "1. egg" in captured.out
    assert "2. Bake for 30 minutes" in captured.out
    assert "Calories: 300" in captured.out
    assert "Tags: breakfast, easy" in captured.out