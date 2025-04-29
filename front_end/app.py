import os
import sys
from flask import (
    Flask, render_template, request,
    session, redirect, url_for, flash
)

# ── import back_end packages ──
sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..')
    )
)

# use RecipeDatabase abstraction
from back_end.mongo_connection import RecipeDatabase

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "change_me")

# initialize and connect once at startup
db = RecipeDatabase()
if not db.connect():
    raise RuntimeError("Failed to connect to MongoDB Atlas!")

# authentication collection
user_coll = db.db['user_information']


# -------- LOGIN ROUTE --------
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        u = request.form['username'].strip()
        p = request.form['password']
        user = user_coll.find_one({"username": u})
        if user and user.get('password') == p:
            session['username'] = u
            flash("Logged in successfully.", "success")
            return redirect(url_for('page1'))
        else:
            flash("Invalid username or password", "danger")
    return render_template('login.html')


# -------- SIGNUP ROUTE --------
@app.route('/signup', methods=['GET','POST'])
def sign_up():
    if request.method == 'POST':
        u = request.form['username'].strip()
        p = request.form['password']
        user_coll.insert_one({"username": u, "password": p})
        session['username'] = u
        return redirect(url_for('page1'))
    return render_template('signup.html')


# -------- LOGOUT ROUTE --------
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))


# protect quiz & results
@app.before_request
def require_login():
    allowed = ('login','signup','static','logout')
    if request.endpoint not in allowed and 'username' not in session:
        return redirect(url_for('login'))


@app.route('/', methods=['GET'])
def home():
    return redirect(url_for('page1'))


@app.route('/page1', methods=['GET', 'POST'])
def page1():
    if request.method == 'POST':
        session['response1'] = request.form['response1']
        return redirect(url_for('page2'))
    return render_template('page1.html', response1=session.get('response1',''))


@app.route('/page2', methods=['GET', 'POST'])
def page2():
    if request.method == 'POST':
        if 'previous' in request.form:
            return redirect(url_for('page1'))
        session['response2'] = request.form['response2']
        return redirect(url_for('page3'))
    return render_template('page2.html', response2=session.get('response2',''))


@app.route('/page3', methods=['GET', 'POST'])
def page3():
    if request.method == 'POST':
        if 'previous' in request.form:
            return redirect(url_for('page2'))
        session['response3'] = request.form['response3']
        return redirect(url_for('results'))
    return render_template('page3.html', response3=session.get('response3',''))


@app.route('/results')
def results():
    # TODO: translate session answers into a real Mongo query
    # For now we’ll just fetch a sample of 10 recipes:
    recipes = db.get_sample_recipes(count=10)
    return render_template('results.html', recipes=recipes)


if __name__ == "__main__":
    app.run(debug=True)
