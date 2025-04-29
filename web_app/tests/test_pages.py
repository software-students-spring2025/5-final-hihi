# tests/test_integration.py
import pytest
from front_end.app import app

@pytest.fixture
def client():
    app.testing = True
    with app.test_client() as client:
        yield client

def test_full_quiz_flow_renders_html(client):
    # 1) Go to /login page (must sign in first)
    rv = client.get('/login')
    assert rv.status_code == 200
    # login form should have username/password
    assert b'Username' in rv.data and b'Password' in rv.data

    # 2) Sign up or log in
    rv = client.post(
        '/signup',
        data={'username':'tester','password':'testpw'},
        follow_redirects=True
    )
    # After signup you should land on first question
    assert b'Question 1:' in rv.data

    # 3) Answer Q1
    rv = client.post(
        '/page1',
        data={'response1':'less_than_30'},
        follow_redirects=True
    )
    assert b'Question 2:' in rv.data

    # 4) Answer Q2
    rv = client.post(
        '/page2',
        data={'response2':'low'},
        follow_redirects=True
    )
    assert b'Question 3:' in rv.data

    # 5) Answer Q3
    rv = client.post(
        '/page3',
        data={'response3':'main_dish'},
        follow_redirects=True
    )
    # Should land on /results
    assert rv.request.path == '/results'
    assert b'Your Recommended Recipes' in rv.data

    # 6) Check that at least one recipe “card” is in the HTML
    assert b'class="card"' in rv.data
