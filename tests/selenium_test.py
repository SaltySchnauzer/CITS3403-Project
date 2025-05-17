from unittest import TestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from multiprocessing import Process
import time
from app.config import TestConfig
from app import create_app, db
from app.models import User

base_url = ""

def add_test_data():
        # Create a test user
        user = User(username='testuser')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()

class SeleniumTestCase(TestCase):
    def setUp(self):
        # Configure app in testing mode
        self.testApp = create_app(TestConfig)
        self.app_context = self.testApp.app_context()
        self.app_context.push()
        db.create_all()
        add_test_data()

        self.server_thread = Process(target=self.testApp.run)
        self.server_thread.start()

        # Set up headless Chrome browser
        foxOptions = Options()
        foxOptions.add_argument('-headless')
        self.driver = webdriver.Firefox(options=foxOptions)

    def tearDown(self):
        self.server_thread.terminate()
        self.driver.close()
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_signin_button(self):
        self.driver.get("http://127.0.0.1:5000/")
        self.driver.find_element(By.LINK_TEXT, "Log In").click()
        assert self.driver.current_url == "http://127.0.0.1:5000/signin"

    def test_login_required(self):
        self.driver.get("http://127.0.0.1:5000/")
        self.driver.find_element(By.LINK_TEXT, "History").click()
        assert self.driver.current_url == "http://127.0.0.1:5000/signin?next=%2Fhistory"

    def test_login(self):
        self.driver.get("http://127.0.0.1:5000/")
        self.driver.find_element(By.LINK_TEXT, "Log In").click()
        self.driver.find_element(By.ID, "username").send_keys("testuser")
        self.driver.find_element(By.ID, "password").send_keys("password123")
        self.driver.find_element(By.ID, "submit").click()
        assert self.driver.current_url == "http://127.0.0.1:5000/index"
    
    def test_gated_buttons(self):
        self.driver.get("http://127.0.0.1:5000/signin")
        self.driver.find_element(By.ID, "username").send_keys("testuser")
        self.driver.find_element(By.ID, "password").send_keys("password123")
        self.driver.find_element(By.ID, "submit").click()
        self.driver.find_element(By.LINK_TEXT, "Friends").click()
        assert self.driver.current_url == "http://127.0.0.1:5000/friends"
        self.driver.find_element(By.LINK_TEXT, "History").click()
        assert self.driver.current_url == "http://127.0.0.1:5000/history"
  
    def test_signup(self):
        self.driver.get("http://127.0.0.1:5000/signup")
        self.driver.find_element(By.ID, "username").send_keys("newuser")
        self.driver.find_element(By.ID, "password").send_keys("newpwd")
        self.driver.find_element(By.ID, "password2").send_keys("newpwd")
        self.driver.find_element(By.ID, "submit").click()
        assert self.driver.current_url == "http://127.0.0.1:5000/index"