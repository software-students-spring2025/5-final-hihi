import pytest
import os
import sys
from pymongo import MongoClient

# Add pytest configuration here to ensure proper imports for all tests
pytest_plugins = []

def seed_test_database():
    """Create test data in MongoDB for testing"""
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['recipe_database']
        
        # Only seed if the DB is empty (avoid duplicates during test runs)
        if db['recipes'].count_documents({}) == 0:
            # Add test recipes
            db['recipes'].insert_many([
                {
                    'name': 'Test Recipe 1',
                    'minutes': 30,
                    'tags': ['breakfast', 'main-dish', 'easy'],
                    'nutrition': {'calories': 300},
                    'ingredients': ['eggs', 'milk', 'flour'],
                    'steps': ['mix', 'cook', 'serve'],
                    'description': 'A test breakfast recipe'
                },
                {
                    'name': 'Test Recipe 2',
                    'minutes': 60,
                    'tags': ['lunch', 'dinner', 'main-dish', 'vegetarian'],
                    'nutrition': {'calories': 500},
                    'ingredients': ['pasta', 'tomato', 'cheese'],
                    'steps': ['boil pasta', 'make sauce', 'combine', 'serve'],
                    'description': 'A test dinner recipe'
                },
                {
                    'name': 'Test Recipe 3',
                    'minutes': 15,
                    'tags': ['breakfast', 'easy', 'beginner-cook'],
                    'nutrition': {'calories': 200},
                    'ingredients': ['bread', 'avocado', 'salt'],
                    'steps': ['toast bread', 'mash avocado', 'combine', 'add salt'],
                    'description': 'A quick breakfast recipe'
                },
                {
                    'name': 'Test Recipe 4',
                    'minutes': 45,
                    'tags': ['dinner', 'side-dishes', 'vegetarian'],
                    'nutrition': {'calories': 300},
                    'ingredients': ['potatoes', 'olive oil', 'rosemary', 'salt'],
                    'steps': ['cut potatoes', 'season', 'roast'],
                    'description': 'A side dish recipe'
                }
            ])
            
            # Add test users
            if db['user_information'].count_documents({}) == 0:
                db['user_information'].insert_one({
                    'username': 'testuser',
                    'password': 'password'
                })
        
        return True
    except Exception as e:
        print(f"Error seeding database: {e}")
        return False

# Seed the database before tests run
seed_test_database()