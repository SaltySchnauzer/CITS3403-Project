from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime




# Association table for sharing preferences (users who share sessions with other users)
share_associations = db.Table(
    'share_associations',
    db.Column('sharer_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('shared_with_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)




@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))

# Table stores account user information such as a user id, username and password. 
class User(UserMixin, db.Model): 
    id = db.Column(db.Integer, primary_key=True) # internal primary key - not set by user
    username = db.Column(db.String(50), nullable=False) # not unique - duplicates possible within database, but not through submission (you can add dupes through python shell for instance)
    password_hash = db.Column(db.String(256)) # unreadable, secure password storage hash


    # One-to-many: a user has many study sessions
    sessions = db.relationship(
        'Session', back_populates='user', cascade='all, delete-orphan', lazy='dynamic'
    )

    # Many-to-many: users this user shares with
    shared_with = db.relationship(
        'User',
        secondary=share_associations,
        primaryjoin=(share_associations.c.sharer_id == id),
        secondaryjoin=(share_associations.c.shared_with_id == id),
        backref=db.backref('shared_by', lazy='dynamic'),
        lazy='dynamic'
    )


    # For setting password
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # For checking if password is correct
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # For printing to console
    def __repr__(self):
        return "<User: {}>".format(self.username)
    

class Session(db.Model):
    __tablename__ = 'session'

    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(100), nullable=True)  # Subject studied
    started_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    ended_at   = db.Column(db.DateTime, nullable=False)
    duration   = db.Column(db.Integer, nullable=False)  # in milliseconds
    productivity = db.Column(db.Integer, nullable=True)  # 0, 25, 50, 75, 100
    mood         = db.Column(db.String(10), nullable=True)  # 'sad', 'neutral', 'happy'

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user    = db.relationship('User', back_populates='sessions')

    def to_dict(self):
        return {
            'id':           self.id,
            'name':         self.name,
            'started_at':   self.started_at.isoformat(),
            'ended_at':     self.ended_at.isoformat(),
            'duration':     self.duration,
            'user_id':      self.user_id,
            'productivity': self.productivity,
            'mood':         self.mood
        }
