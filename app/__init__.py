# This initialises the flask instance
# Because it's labelled as __init__ it gets run on package start

from flask import Flask

app = Flask(__name__)

from app import routes # This is imported later to avoid circular referencing issues with Flask