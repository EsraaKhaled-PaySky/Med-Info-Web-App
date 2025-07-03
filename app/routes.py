from flask import Blueprint, render_template, request, redirect, url_for, flash
from . import mongo, bcrypt
from flask_login import login_user, logout_user, login_required
from .models import User
from bson.objectid import ObjectId

# ✅ DEFINE BLUEPRINT FIRST
main = Blueprint('main', __name__)

# ✅ NOW USE ROUTES
@main.route('/')
def home():
    return render_template('home.html')  
@main.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        mongo.db.users.insert_one({'username': username, 'password': password})
        return redirect(url_for('main.login'))
    return render_template('signup.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = mongo.db.users.find_one({'username': request.form['username']})
        if user and bcrypt.check_password_hash(user['password'], request.form['password']):
            user_obj = User(user)
            login_user(user_obj)
            return redirect(url_for('main.dashboard'))
        flash("Invalid credentials.")
    return render_template('login.html')

@main.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

