import pytest
import sys
from unittest.mock import MagicMock

# This file contains fixtures and configuration for pytest

def pytest_configure(config):
    """
    Called at the start of the testing session.
    Setup any global test configurations here.
    """
    # Set up environment variables or other configurations
    pass

@pytest.fixture
def mock_db():
    """Fixture for a mock database"""
    class MockCollection:
        def __init__(self):
            self.data = [{
                "_id": "123",
                "name": "Test Recipe",
                "minutes": 30,
                "ingredients": ["ingredient1", "ingredient2"],
                "nutrition": {"calories": 100},
                "tags": ["breakfast", "easy"]
            }]
        
        def find_one(self, query=None):
            return self.data[0]
        
        def find(self, query=None):
            class Cursor:
                def __init__(self, data):
                    self.data = data
                
                def limit(self, n):
                    return self
                
                def __iter__(self):
                    return iter(self.data)
            
            return Cursor(self.data)
    
    return MockCollection()

@pytest.fixture
def mock_flask_app():
    """Fixture for a mock Flask app"""
    class MockApp:
        def __init__(self):
            self.routes = {}
            self.before_request_funcs = []
            self.secret_key = "test_key"

        def route(self, rule, **options):
            def decorator(f):
                self.routes[rule] = f
                return f
            return decorator

        def before_request(self, f):
            self.before_request_funcs.append(f)
            return f
            
    return MockApp()

@pytest.fixture
def mock_flask_request():
    """Fixture for a mock Flask request"""
    class MockRequest:
        def __init__(self):
            self.method = "GET"
            self.form = {}
            self.endpoint = "main"
    
    return MockRequest()

@pytest.fixture
def mock_recipe_system():
    """Fixture for a mock recipe system"""
    class MockSystem:
        def __init__(self):
            self.connected = True
            self.db = MagicMock()
        
        def get_recommendations(self, preferences):
            return {
                'breakfast': [{
                    "_id": "123", 
                    "name": "Test Breakfast", 
                    "minutes": 15,
                    "nutrition": {"calories": 200},
                    "ingredients": ["eggs", "bread"],
                    "tags": ["breakfast", "easy"]
                }]
            }
    
    return MockSystem()
