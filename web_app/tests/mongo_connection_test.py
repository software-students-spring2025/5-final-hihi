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
