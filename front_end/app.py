import os
import sys
import json
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import pymongo

# ── allow imports from the sibling back_end folder ──
sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..')
    )
)
from back_end import MongoDBConnection as db


app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "change_me")

# grab your user_information collection
user_coll = db.client['recipe_database']['user_information']


# -------- LOGIN ROUTE --------
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        user = user_coll.find_one({"username": username})
        if user and user.get('password') == password:
            session['username'] = username
            flash("Logged in successfully.", "success")
            return redirect(url_for('page1'))
        else:
            flash("Invalid username or password", "danger")
    return render_template('login.html')

# -------- SIGNUP ROUTE --------
@app.route('/signup', methods=['GET','POST'])
def sign_up():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        user = {"username": username, "password": password}
        user = db.client['recipe_database']['user_information'].insert_one(user)
        session['username'] = username
        return redirect(url_for('page1'))
    return render_template('signup.html')

# -------- LOGOUT ROUTE --------
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))


# protect all quiz & results pages
@app.before_request
def require_login():
    allowed = ('login','static','logout')
    if request.endpoint not in allowed and 'username' not in session:
        return redirect(url_for('login'))


@app.route('/', methods=['GET', 'POST'])
def home():
    return redirect(url_for('page1'))


@app.route('/page1', methods=['GET', 'POST'])
def page1():
    if request.method == 'POST':
        session['response1'] = request.form['response1']
        return redirect(url_for('page2'))
    return render_template("page1.html", response1=session.get('response1',''))


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
    recipes = db.collection.find(
        {"cuisine": session.get('selected_cuisine', 'asian')}
    ).limit(10)
    recipes_list = list(recipes)
    return render_template('results.html', recipes=recipes_list)


if __name__ == "__main__":
    app.run(debug=True)
