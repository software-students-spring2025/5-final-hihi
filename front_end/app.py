import os
import json
import requests
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import pymongo
from back_end import MongoDBConnection as db



app = Flask(__name__)
app.secret_key = "your_secret_key"

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template("page1.html")

@app.route('/page1', methods=['GET', 'POST'])
def page1():
    if request.method == 'POST':
        session['response1'] = request.form['response1']
        return redirect(url_for('page2'))
    return render_template("page1.html",response1=session.get('response1',''))


@app.route('/page2', methods=['GET', 'POST'])
def page2():

    
    if request.method == 'POST':
        if 'previous' in request.form:
            return redirect(url_for('page1'))
        session['response2'] = request.form['response2']
        return redirect(url_for('page3'))
    return render_template('page2.html',response2 = session.get('response2',''))

@app.route('/page3', methods=['GET', 'POST'])
def page3():

    
    if request.method == 'POST':
        if 'previous' in request.form:
            return redirect(url_for('page2'))
        session['response3'] = request.form['response3']
        return redirect(url_for('results'))
    return render_template('page3.html',response2 = session.get('response3',''))

@app.route('/results')
def results():
    # to do: process data
    return render_template('results.html')

