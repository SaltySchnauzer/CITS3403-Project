from app import db, login

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))

# Table stores account user information such as a user id, username and password. 
class User(UserMixin, db.Model): 
    id = db.Column(db.Integer, primary_key=True) # internal primary key - not set by user
    username = db.Column(db.String(50), nullable=False) # not unique - duplicates possible within database, but not through submission (you can add dupes through python shell for instance)
    password_hash = db.Column(db.String(256)) # unreadable, secure password storage hash

    # For setting password
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # For checking if password is correct
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # For printing to console
    def __repr__(self):
        return "<User: {}>".format(self.username)
