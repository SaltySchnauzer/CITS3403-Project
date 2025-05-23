from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone



# -- Association table for “sharing” (i.e. adding friends) --

share_associations = db.Table(
    'share_associations',
    db.Column('sharer_id',      db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('shared_with_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))





# -- User Model--

class User(UserMixin, db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(50), nullable=False)
    password_hash = db.Column(db.String(256))

    # your own study sessions
    sessions = db.relationship(
        'Session',
        back_populates='user',
        cascade='all, delete-orphan',
        lazy='dynamic'
    )

    # people you’ve “added” (shared your data with)
    shared_with = db.relationship(
        'User',
        secondary=share_associations,
        primaryjoin=(share_associations.c.sharer_id == id),
        secondaryjoin=(share_associations.c.shared_with_id == id),
        backref=db.backref('shared_by', lazy='dynamic'),
        lazy='dynamic'
    )

    @property
    def friends(self):
        """Alias for users you’ve added."""
        return self.shared_with

    def add_friend(self, user):
        """Share your sessions with another user."""
        if not self.shared_with.filter_by(id=user.id).first():
            self.shared_with.append(user)

    def remove_friend(self, user):
        """Stop sharing with a user."""
        if self.shared_with.filter_by(id=user.id).first():
            self.shared_with.remove(user)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"

# -- Made with the assistance of Copilot --








# -- Session Model --

class Session(db.Model):
    __tablename__ = 'session'
    id              = db.Column(db.Integer, primary_key=True)
    name            = db.Column(db.String(100), nullable=True)  # Subject studied
    description     = db.Column(db.String(256), nullable=True)  # User entered description
    task_type       = db.Column(db.String(32), nullable=True)
    started_at      = db.Column(db.DateTime, nullable=False)
    ended_at        = db.Column(db.DateTime, nullable=True)
    duration        = db.Column(db.Integer, nullable=True)  # in milliseconds
    productivity    = db.Column(db.Float, nullable=True)  # 0, 25, 50, 75, 100
    mood            = db.Column(db.String(10), nullable=True)  # 'sad', 'neutral', 'happy'



    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user    = db.relationship('User', back_populates='sessions')
    
    def set_end(self, time):
        self.ended_at = time
        self.duration = (self.ended_at.replace(tzinfo=timezone.utc) - self.started_at.replace(tzinfo=timezone.utc)).total_seconds()
        self.productivity = 50

    def to_dict(self):
        try:
            t_end = self.ended_at.isoformat() # Has a chance to not exist - this is a safeguard to stop to_dict from failing
        except:
            t_end = ""
        return {
            'id':           self.id,
            'name':         self.name,
            'description':  self.description,
            'task_type':    self.task_type,
            'started_at':   self.started_at.isoformat(),
            'ended_at':     t_end,
            'duration':     self.duration,
            'user_id':      self.user_id,
            'productivity': self.productivity,
            'mood':         self.mood
        }
    

# -- Made with a little! assistance from Copilot --
