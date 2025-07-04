import os
from flask import Flask
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from bson.objectid import ObjectId
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize extensions
mongo = PyMongo()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = "main.login"

def create_app():
    app = Flask(__name__, template_folder="templates")
    app.config['MONGO_URI'] = os.getenv('MONGO_URI')
    app.secret_key = os.getenv('SECRET_KEY')

    # Initialize with app
    mongo.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # User loader for Flask-Login
    from .models import User
    @login_manager.user_loader
    def load_user(user_id):
        user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        return User(user) if user else None

    # Register blueprints
    from .routes import main
    app.register_blueprint(main)

    from .medicine_routes import medicine_bp
    app.register_blueprint(medicine_bp)

    return app
