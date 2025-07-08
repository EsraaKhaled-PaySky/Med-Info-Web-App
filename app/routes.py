from flask import Blueprint, render_template, request, redirect, url_for, flash
from . import mongo, bcrypt
from flask_login import login_user, logout_user, login_required, current_user
from .models import User
from bson.objectid import ObjectId

# ✅ DEFINE BLUEPRINT
main = Blueprint('main', __name__)

# ✅ HOME
@main.route('/')
def home():
    return render_template('home.html')

# ✅ SIGNUP
@main.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        mongo.db.users.insert_one({'username': username, 'password': password})
        flash("Signup successful! Please log in.", "success")
        return redirect(url_for('main.login'))
    return render_template('signup.html')

# ✅ LOGIN
@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = mongo.db.users.find_one({'username': request.form['username']})
        if user and bcrypt.check_password_hash(user['password'], request.form['password']):
            user_obj = User(user)
            login_user(user_obj)
            flash("Logged in successfully!", "success")
            return redirect(url_for('main.dashboard'))
        flash("Invalid credentials.", "danger")
    return render_template('login.html')

# ✅ DASHBOARD (updated to redirect to medicine search)
@main.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if request.method == 'POST':
        query = request.form.get('medicine', '').strip()
        if query:
            # Redirect to medicine search with query parameter
            return redirect(url_for('medicine.search', query=query))
        else:
            flash("Please enter a drug name to search.", "warning")
    
    return render_template('dashboard.html', user=current_user)

# ✅ LOGOUT
@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('main.login'))

# ✅ SEARCH - Updated to redirect to medicine search
@main.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    if request.method == 'POST':
        query = request.form.get('query', '').strip()
        if query:
            # Redirect to medicine search with query parameter
            return redirect(url_for('medicine.search', query=query))
        else:
            flash("Please enter a drug name to search.", "warning")
    
    return redirect(url_for('main.dashboard'))



# from flask import Blueprint, render_template, request, redirect, url_for, flash
# from . import mongo, bcrypt
# from flask_login import login_user, logout_user, login_required, current_user
# from .models import User
# from bson.objectid import ObjectId

# # ✅ DEFINE BLUEPRINT
# main = Blueprint('main', __name__)

# # ✅ HOME
# @main.route('/')
# def home():
#     return render_template('home.html')

# # ✅ SIGNUP
# @main.route('/signup', methods=['GET', 'POST'])
# def signup():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
#         mongo.db.users.insert_one({'username': username, 'password': password})
#         flash("Signup successful! Please log in.", "success")
#         return redirect(url_for('main.login'))
#     return render_template('signup.html')

# # ✅ LOGIN
# @main.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         user = mongo.db.users.find_one({'username': request.form['username']})
#         if user and bcrypt.check_password_hash(user['password'], request.form['password']):
#             user_obj = User(user)
#             login_user(user_obj)
#             flash("Logged in successfully!", "success")
#             return redirect(url_for('main.dashboard'))
#         flash("Invalid credentials.", "danger")
#     return render_template('login.html')

# # ✅ DASHBOARD (same as your medicine search)
# @main.route('/dashboard', methods=['GET', 'POST'])
# @login_required
# def dashboard():
#     medicine = None
#     searched = False
#     if request.method == 'POST':
#         searched = True
#         query = request.form['medicine']
#         medicine = mongo.db.medicines.find_one({"name": {"$regex": query, "$options": "i"}})
#     return render_template('dashboard.html', user=current_user, medicine=medicine, searched=searched)

# # ✅ LOGOUT
# @main.route('/logout')
# @login_required
# def logout():
#     logout_user()
#     flash("You have been logged out.", "info")
#     return redirect(url_for('main.login'))

# @main.route('/search', methods=['GET', 'POST'])
# @login_required
# def search():
#     results = []
#     query = ''
#     if request.method == 'POST':
#         query = request.form.get('query', '').strip()
#         if query:
#             results = list(mongo.db.medicines.find({
#                 "name": {"$regex": query, "$options": "i"}
#             }))
#         return render_template('search_results.html', results=results, query=query)
#     return redirect(url_for('main.dashboard'))
