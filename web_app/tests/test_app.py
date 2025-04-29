import pytest
from flask import session
from front_end.app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SERVER_NAME'] = 'localhost'
    
    with app.test_client() as client:
        with app.app_context():
            yield client

def test_login_page(client):
    """Test that login page loads"""
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Login' in response.data

def test_login_success(client):
    """Test successful login"""
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'password'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Logged in successfully' in response.data

def test_login_failure(client):
    """Test failed login"""
    response = client.post('/login', data={
        'username': 'wronguser',
        'password': 'wrongpass'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Invalid username or password' in response.data

def test_signup_page(client):
    """Test signup page loads"""
    response = client.get('/sign_up')
    assert response.status_code == 200
    assert b'Create Account' in response.data or b'Sign Up' in response.data

def test_signup_functionality(client):
    """Test user signup"""
    response = client.post('/sign_up', data={
        'username': 'newuser',
        'password': 'password123'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Account created' in response.data

def test_logout(client):
    """Test logout functionality"""
    # First login
    client.post('/login', data={
        'username': 'testuser',
        'password': 'password'
    })
    # Then logout
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'You have been logged out' in response.data

def test_require_login(client):
    """Test that routes require login"""
    response = client.get('/main', follow_redirects=True)
    assert response.status_code == 200
    assert b'Login' in response.data

def test_quiz_page1(client):
    """Test quiz page 1"""
    # First login
    client.post('/login', data={
        'username': 'testuser',
        'password': 'password'
    })
    response = client.get('/page1')
    assert response.status_code == 200

def test_quiz_navigation(client):
    """Test quiz navigation"""
    # Login
    client.post('/login', data={
        'username': 'testuser',
        'password': 'password'
    })
    # Submit page 1
    response = client.post('/page1', data={
        'response1': ['vegetarian']
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'page2' in response.data.lower()
