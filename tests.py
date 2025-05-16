from app import create_app, db
from app.config import TestConfig
from app.models import User, Session
from unittest import TestCase
import datetime

testApp = create_app(TestConfig)

def add_test_data():
    db.session.add(User(id='0', username='Test Dummy'))
    s = Session(
        id = 0,
        started_at = datetime.datetime(2025, 1, 1, 10, 0, 0, 0),
        user_id = 0
    )
    s.set_end(datetime.datetime(2025, 1, 1, 11, 0, 0, 0))
    db.session.add(s)
    db.session.commit()

class BasicTests(TestCase):
    def setUp(self):
        testApp = create_app(TestConfig)
        self.app_context = testApp.app_context()
        self.app_context.push()
        db.create_all()
        add_test_data()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # Do passwords hash correctly?
    def test_password_hashing(self):
        u = db.session.get(User, 0)
        u.set_password("unit testing")
        self.assertTrue(u.check_password("unit testing"))
        self.assertFalse(u.check_password("no unit testing cursed forever into development hell"))

    # Do the relationships between user and session operate as expected?
    def test_relationship(self):
        u = db.session.get(User, 0)
        s = u.sessions.where(Session.id == '0').first() 
        self.assertFalse(u is None)
        self.assertFalse(s is None)

    # Do sessions get updated with end times and calculate their duration correctly?
    def test_check_duration(self):
        u = db.session.get(User, 0)
        s = u.sessions.where(Session.id == '0').first()
        print(s.duration)
        self.assertTrue(s.duration == 3600)