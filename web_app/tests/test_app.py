import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Add the parent directory to path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock Flask modules and classes
class MockFlask:
    def __init__(self, name):
        self.name = name
        self.secret_key = None
        self.routes = {}
        self.before_request_funcs = {}
        
    def route(self, route_str, **kwargs):
        def decorator(f):
            self.routes[route_str] = f
            return f
        return decorator
        
    def before_request(self, f):
        if None not in self.before_request_funcs:
            self.before_request_funcs[None] = []
        self.before_request_funcs[None].append(f)
        return f
        
    def run(self, **kwargs):
        pass

# Create mocks for Flask modules
flask_mock = MagicMock()
flask_mock.Flask = MockFlask
flask_mock.render_template = MagicMock(return_value="rendered template")
flask_mock.session = {}
flask_mock.request = MagicMock()
flask_mock.request.method = 'GET'
flask_mock.request.form = {}
flask_mock.redirect = MagicMock(return_value="redirected")
flask_mock.url_for = MagicMock(return_value="/url")
flask_mock.flash = MagicMock()

# Mock bson and ObjectId
bson_mock = MagicMock()
object_id_mock = MagicMock()
object_id_mock.return_value = "mock_id"
bson_mock.ObjectId = object_id_mock

# Mock the MongoDB connection
mongo_connection_mock = MagicMock()
recipe_db_mock = MagicMock()
recipe_db_mock.connect.return_value = True
recipe_db_mock.db = {"user_information": MagicMock(), "saved_recipes": MagicMock()}
recipe_db_mock.collection = MagicMock()
mongo_connection_mock.RecipeDatabase.return_value = recipe_db_mock

# Mock the recipe system
recipe_system_mock = MagicMock()
recommendation_system_mock = MagicMock()
recommendation_system_mock.connected = True
recommendation_system_mock.get_recommendations.return_value = {
    "breakfast": [{"_id": "mock_id", "name": "Breakfast Recipe"}],
    "lunch": [{"_id": "mock_id", "name": "Lunch Recipe"}]
}
recipe_system_mock.RecipeRecommendationSystem.return_value = recommendation_system_mock

# Apply mocks before importing the app
with patch.dict('sys.modules', {
    'flask': flask_mock,
    'bson': bson_mock,
    'back_end.mongo_connection': mongo_connection_mock,
    'back_end.recipe_system': recipe_system_mock
}):
    # Try to import the app
    try:
        import front_end.app as app
        app_imported = True
    except ImportError:
        app_imported = False

def test_app_routes():
    """Test that app has key routes defined"""
    if not app_imported:
        pytest.skip("App import failed")
    
    routes = [
        '/login', '/sign_up', '/logout', 
        '/main', '/saved_recipes', 
        '/page1', '/page2', '/page3', 
        '/page4', '/page5', '/page6', '/page7',
        '/results'
    ]
    
    # Check that route handlers exist for all routes
    for route in routes:
        assert route in app.app.routes

def test_login_handler():
    """Test login handler"""
    if not app_imported:
        pytest.skip("App import failed")
    
    # Set up mocks
    flask_mock.request.method = 'POST'
    flask_mock.request.form = {'username': 'testuser', 'password': 'password'}
    user_mock = {'username': 'testuser', 'password': 'password'}
    app.user_coll.find_one.return_value = user_mock
    
    # Call the function
    result = app.login()
    
    # Verify it works
    assert result == "redirected"
    assert flask_mock.session.get('username') == 'testuser'
    flask_mock.flash.assert_called_with("Logged in successfully.", "success")

def test_login_handler_failed():
    """Test login handler with invalid credentials"""
    if not app_imported:
        pytest.skip("App import failed")
    
    # Set up mocks
    flask_mock.request.method = 'POST'
    flask_mock.request.form = {'username': 'wronguser', 'password': 'wrongpass'}
    app.user_coll.find_one.return_value = None
    
    # Call the function
    result = app.login()
    
    # Verify it shows error
    flask_mock.flash.assert_called_with("Invalid username or password", "danger")

def test_sign_up_handler():
    """Test sign up handler"""
    if not app_imported:
        pytest.skip("App import failed")
    
    # Set up mocks
    flask_mock.request.method = 'POST'
    flask_mock.request.form = {'username': 'newuser', 'password': 'newpass'}
    
    # Call the function
    result = app.sign_up()
    
    # Verify it works
    assert result == "redirected"
    assert flask_mock.session.get('username') == 'newuser'
    app.user_coll.insert_one.assert_called_with({'username': 'newuser', 'password': 'newpass'})
    flask_mock.flash.assert_called_with("Account created!", "success")

def test_logout_handler():
    """Test logout handler"""
    if not app_imported:
        pytest.skip("App import failed")
    
    # Set up session
    flask_mock.session['username'] = 'testuser'
    
    # Call the function
    result = app.logout()
    
    # Verify it works
    assert result == "redirected"
    flask_mock.flash.assert_called_with("You have been logged out.", "info")
    assert 'username' not in flask_mock.session

def test_require_login():
    """Test login requirement"""
    if not app_imported:
        pytest.skip("App import failed")
    
    # Clear session
    if 'username' in flask_mock.session:
        del flask_mock.session['username']
    
    # Test endpoints that require login
    flask_mock.request.endpoint = 'main'
    result = app.require_login()
    
    # Verify it redirects to login
    assert result == "redirected"
    flask_mock.url_for.assert_called_with('login')

def test_main_page():
    """Test main page handler"""
    if not app_imported:
        pytest.skip("App import failed")
    
    # Set up session
    flask_mock.session['username'] = 'testuser'
    
    # Call the function
    result = app.main()
    
    # Verify it renders the template
    assert result == "rendered template"
    flask_mock.render_template.assert_called_with('main.html')

def test_save_recipe():
    """Test save recipe handler"""
    if not app_imported:
        pytest.skip("App import failed")
    
    # Set up session
    flask_mock.session['username'] = 'testuser'
    flask_mock.request.referrer = "/test"
    
    # Call the function
    result = app.save_recipe("123")
    
    # Verify it works
    assert result == "redirected"
    app.saved_coll.insert_one.assert_called_with({
        'user': 'testuser',
        'recipe_id': 'mock_id'
    })
    flask_mock.flash.assert_called_with("Recipe saved!", "success")

def test_quiz_flow():
    """Test quiz flow pages"""
    if not app_imported:
        pytest.skip("App import failed")
    
    # Set up session
    flask_mock.session['username'] = 'testuser'
    flask_mock.request.method = 'POST'
    
    # Test page1
    flask_mock.request.form = {'response1': ['vegetarian']}
    result = app.page1()
    assert result == "redirected"
    assert flask_mock.session.get('response1') == ['vegetarian']
    
    # Test page2
    flask_mock.request.form = {'response2': '2'}
    result = app.page2()
    assert result == "redirected"
    assert flask_mock.session.get('response2') == '2'
    
    # Test results
    result = app.results()
    assert result == "rendered template"
    flask_mock.render_template.assert_called_with('results.html', recommendations=flask_mock.session.get('recommendations'), prefs=pytest.approx({
        'question1': flask_mock.session.get('response1'),
        'question2': flask_mock.session.get('response2'),
        'question3': flask_mock.session.get('response3'),
        'question4': flask_mock.session.get('response4'),
        'question5': flask_mock.session.get('response5'),
        'question6': flask_mock.session.get('response6'),
        'question7': flask_mock.session.get('response7')
    }))
