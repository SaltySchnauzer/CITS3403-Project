# The actual .py that is run

from app import app
# This imports app, which runs __init__.py
# Which itself imports routes.py and initialises that

import sqlalchemy as sa
import sqlalchemy.orm as so
from app import app, db
from app.models import User

# Provide context for the shell when interacting with the database
@app.shell_context_processor
def make_shell_context():
    return {'sa': sa, 'so': so, 'db': db, 'User': User}