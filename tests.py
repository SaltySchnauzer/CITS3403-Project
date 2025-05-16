from app import create_app, db
from app.config import TestConfig
from app.models import User
from unittest import TestCase

testApp = create_app(TestConfig)

def add_test_data():
    u = User(id='0', username='Test Dummy')
    db.session.add(u)
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

    def test_password_hashing(self):
        u = User.query.get("0")
        u.set_password("unit testing")
        self.assertTrue(u.check_password("unit testing"))
        self.assertFalse(u.check_password("no unit testing cursed forever into development hell"))