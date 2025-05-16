from flask import Flask


from flask_sqlalchemy import SQLAlchemy # Database and configuration
from flask_migrate import Migrate
from app.config import Config

from flask_login import LoginManager    # User session management

app = Flask(__name__)                   # Initialize Flask app
app.config.from_object(Config)

db = SQLAlchemy(app)                    # Initialize database and migration manager
migrate = Migrate(app, db)

login = LoginManager(app)               # Initialize login manager
login.login_view = 'signin'             # Redirect unauthorized users to the 'signin' route

from app import routes                  # This is imported later to avoid circular referencing issues with Flask

