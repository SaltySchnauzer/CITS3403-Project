from flask import Flask

#SQL Database imports
from flask_migrate import Migrate 
from flask_sqlalchemy import SQLAlchemy 
from app.config import Config 

app = Flask(__name__)
app.secret_key = 'your_secret_key_here' #secret key added for session cookies
app.config.from_object(Config) 
db = SQLAlchemy(app) 
migrate = Migrate(app, db) 


from app import routes # This is imported later to avoid circular referencing issues with Flask
