import os
from flask import Flask
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Initialize extensions
mongo = PyMongo()
bcrypt = Bcrypt()
login_manager = LoginManager()

def create_app():
    # Create the Flask app, and point to the top-level 'templates/' directory
    app = Flask(__name__, template_folder="templates")

    # Configuration
    app.config['MONGO_URI'] = os.getenv('MONGO_URI')
    app.secret_key = os.getenv('SECRET_KEY')

    # Initialize extensions with app
    mongo.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # User loader for Flask-Login
    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        user = mongo.db.users.find_one({"_id": user_id})
        return User(user) if user else None

    # Register routes
    from .routes import main
    app.register_blueprint(main)

    return app

