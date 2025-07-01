import os
from flask import Flask
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from dotenv import load_dotenv

mongo = PyMongo()
bcrypt = Bcrypt()
login_manager = LoginManager()

def create_app():
    load_dotenv()
    app = Flask(__name__, template_folder=os.path.join(os.pardir, 'templates'))  # For Replit or sandbox use
    app.config['MONGO_URI'] = os.getenv('MONGO_URI')
    app.secret_key = os.getenv('SECRET_KEY')

    mongo.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    from .routes import main
    app.register_blueprint(main)

    return app

