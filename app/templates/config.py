import os 


# SQL database stored in root 

basedir = os.path.abspath(os.path.dirname(__file__))
default_database_location = 'sqlite:///' + os.path.join(basedir, 'app.db')

class Config: 
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or default_database_location
    # Secret Key needs to be set here (e.g. SECRET_KEY = ... )

