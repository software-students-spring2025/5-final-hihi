import pytest
from bson import ObjectId
from back_end.mongo_connection import RecipeDatabase, JSONEncoder
import json

def test_mongo_connection():
    """Test connection to MongoDB"""
    db = RecipeDatabase("mongodb://localhost:27017/")
    assert db.connect() == True
    assert db.db.name == 'recipe_database'
    assert db.collection.name == 'recipes'

def test_find_recipes():
    """Test finding recipes"""
    db = RecipeDatabase("mongodb://localhost:27017/")
    db.connect()
    recipes = db.find_recipes(limit=5)
    assert len(recipes) > 0
    assert 'name' in recipes[0]
    assert 'ingredients' in recipes[0]

def test_find_recipe_by_id():
    """Test finding a recipe by ID"""
    db = RecipeDatabase("mongodb://localhost:27017/")
    db.connect()
    # First get a recipe to get a valid ID
    recipe = db.collection.find_one()
    recipe_id = recipe['_id']
    
    # Now test finding by ID
    found_recipe = db.find_recipe_by_id(recipe_id)
    assert found_recipe is not None
    assert found_recipe['_id'] == recipe_id
    
    # Test with string ID
    str_id = str(recipe_id)
    found_recipe = db.find_recipe_by_id(str_id)
    assert found_recipe is not None
    assert str(found_recipe['_id']) == str_id
    
    # Test with non-existent ID
    non_existent_id = ObjectId()
    not_found = db.find_recipe_by_id(non_existent_id)
    assert not_found is None

def test_search_recipes_by_name():
    """Test search by name functionality"""
    db = RecipeDatabase("mongodb://localhost:27017/")
    db.connect()
    recipes = db.search_recipes_by_name("Test Recipe")
    assert len(recipes) > 0
    assert "Test Recipe" in recipes[0]['name']

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
    assert any('eggs' in ingredient.lower() for ingredient in recipes[0]['ingredients'])

def test_get_sample_recipes():
    """Test getting sample recipes"""
    db = RecipeDatabase("mongodb://localhost:27017/")
    db.connect()
    samples = db.get_sample_recipes(2)
    assert len(samples) > 0
    assert len(samples) <= 2

def test_json_encoder():
    """Test JSONEncoder for ObjectId serialization"""
    obj_id = ObjectId()
    data = {"id": obj_id, "name": "test"}
    
    # Test serialization works without errors
    json_str = json.dumps(data, cls=JSONEncoder)
    assert json_str is not None
    assert str(obj_id) in json_str

def test_to_json():
    """Test to_json method"""
    db = RecipeDatabase("mongodb://localhost:27017/")
    db.connect()
    recipe = db.collection.find_one()
    json_str = db.to_json(recipe)
    assert json_str is not None
    assert recipe['name'] in json_str
