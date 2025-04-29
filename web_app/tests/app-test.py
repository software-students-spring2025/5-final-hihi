import pytest
import sys
import os
from unittest.mock import patch, MagicMock
from bson import ObjectId

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Patch the RecipeDatabase before importing app
db_patch = patch('front_end.app.RecipeDatabase')
mock_db_class = db_patch.start()

# Now import the app module
from front_end.app import app


@pytest.fixture
def client():
    """Create a test client for the app with mocked database"""
    # Set up mock database
    mock_db = MagicMock()
    mock_db.connect.return_value = True
    mock_db_class.return_value = mock_db
    
    # Set up mock collections
    mock_db.db = MagicMock()
    mock_recipes = MagicMock()
    mock_users = MagicMock()
    mock_saved = MagicMock()
    
    mock_db.collection = mock_recipes
    mock_db.db.__getitem__.side_effect = lambda x: {
        'recipes': mock_recipes,
        'user_information': mock_users,
        'saved_recipes': mock_saved
    }.get(x, MagicMock())
    
    # Sample recipes
    vegetarian_recipe = {
        '_id': ObjectId('507f1f77bcf86cd799439011'),
        'name': 'Vegetarian Pasta',
        'minutes': 30,
        'nutrition': {'calories': 500},
        'tags': ['vegetarian', 'main-dish', 'dinner'],
        'ingredients': ['pasta', 'tomato sauce', 'cheese'],
        'steps': ['Boil pasta', 'Add sauce'],
    }
    
    # Configure mock methods
    mock_recipes.find_one.return_value = vegetarian_recipe
    mock_recipes.find.return_value = [vegetarian_recipe]
    mock_users.find_one.return_value = {'username': 'testuser', 'password': 'password'}
    
    # Configure app for testing
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    # Create test client
    with app.test_client() as client:
        with app.app_context():
            yield client

    # Clean up
    db_patch.stop()


def test_home_redirect(client):
    """Test that home redirects to main if logged in"""
    with client.session_transaction() as sess:
        sess['username'] = 'testuser'
    
    response = client.get('/')
    assert response.status_code == 302
    assert response.location.endswith('/main')


def test_login_page(client):
    """Test that login page loads correctly"""
    response = client.get('/login')
    assert response.status_code == 200
    assert b'login' in response.data.lower()


def test_login_post_success(client):
    """Test successful login"""
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'password'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'logged in successfully' in response.data.lower()


def test_login_post_failure(client):
    """Test failed login"""
    mock_user_coll = client.application.config.get('user_coll', None) or app.user_coll
    mock_user_coll.find_one.return_value = None
    
    response = client.post('/login', data={
        'username': 'wronguser',
        'password': 'wrongpass'
    })
    
    assert response.status_code == 200
    assert b'invalid username or password' in response.data.lower()


def test_logout(client):
    """Test logout functionality"""
    with client.session_transaction() as sess:
        sess['username'] = 'testuser'
    
    response = client.get('/logout', follow_redirects=True)
    
    assert response.status_code == 200
    assert b'logged out' in response.data.lower()
    
    with client.session_transaction() as sess:
        assert 'username' not in sess


@patch('front_end.app.RecipeRecommendationSystem')
def test_results_with_recommendations(mock_rec_sys_class, client):
    """Test results page with recommendations"""
    # Log in first
    with client.session_transaction() as sess:
        sess['username'] = 'testuser'
        sess['response1'] = ['vegetarian']
        sess['response2'] = '3'
        sess['response3'] = '1'
        sess['response4'] = ['italian']
        sess['response5'] = '1'
        sess['response6'] = ['breakfast']
        sess['response7'] = ['main_dish']
    
    # Mock recommendation system
    mock_rec_sys = MagicMock()
    mock_rec_sys_class.return_value = mock_rec_sys
    mock_rec_sys.connected = True
    
    # Sample recommendations to return
    mock_recommendations = {
        'breakfast': [{
            '_id': ObjectId('507f1f77bcf86cd799439011'),
            'name': 'Breakfast Omelette',
            'minutes': 15,
            'nutrition': {'calories': 300},
            'tags': ['breakfast', 'main-dish', 'easy'],
            'ingredients': ['eggs', 'cheese', 'vegetables'],
            'steps': ['Beat eggs', 'Cook in pan'],
        }]
    }
    mock_rec_sys.get_recommendations.return_value = mock_recommendations
    
    # Test results page
    response = client.get('/results')
    
    assert response.status_code == 200
    assert b'breakfast' in response.data.lower()
    assert b'breakfast omelette' in response.data.lower()


def test_view_recipe(client):
    """Test viewing a recipe"""
    # Log in first
    with client.session_transaction() as sess:
        sess['username'] = 'testuser'
    
    recipe_id = '507f1f77bcf86cd799439011'
    response = client.get(f'/view_recipe/{recipe_id}')
    
    assert response.status_code == 200
    assert b'vegetarian pasta' in response.data.lower()
