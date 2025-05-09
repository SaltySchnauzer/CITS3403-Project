from flask import Flask

#SQL Database imports
from flask_migrate import Migrate 
from flask_sqlalchemy import SQLAlchemy 
from app.config import Config
from flask_login import LoginManager

app = Flask(__name__)

app.config.from_object(Config) 
db = SQLAlchemy(app) # Iniitalise database object
migrate = Migrate(app, db) # Initialise migration manager

login = LoginManager(app)
login.login_view = 'signin'

from app import routes # This is imported later to avoid circular referencing issues with Flask

