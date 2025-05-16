from flask import Flask

#SQL Database imports
from flask_migrate import Migrate 
from flask_sqlalchemy import SQLAlchemy 
from app.config import Config
from flask_login import LoginManager


db = SQLAlchemy()
login = LoginManager()
login.login_view = 'main.signin'

def create_app(config):
    flaskApp = Flask(__name__)
    flaskApp.config.from_object(config)
    
    db.init_app(flaskApp)
    login.init_app(flaskApp)

    from app.blueprints import main
    flaskApp.register_blueprint(main)

    return flaskApp

