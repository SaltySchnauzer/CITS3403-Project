import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import threading
import time
from app.config import TestConfig
from app import create_app, db
from app.models import User

def add_test_data():
        # Create a test user
        user = User(username='testuser')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()

class SeleniumTestCase(unittest.TestCase):
    def setUp(self):
        # Configure app in testing mode
        self.testApp = create_app(TestConfig)
        self.app_context = self.testApp.app_context()
        self.app_context.push()
        db.create_all()
        add_test_data()

        # Start server thread
        def run():
            self.testApp.run(port=5001, use_reloader=False)

        self.server_thread = threading.Thread(target=run)
        self.server_thread.start()
        time.sleep(1)  # Wait for server to start

        # Set up headless Chrome browser
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=chrome_options)

    def tearDown(self):
        self.server_thread.terminate()
        self.driver.close()
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_login_success(self):
        self.driver.get("http://localhost:5001/signin")
        self.driver.find_element(By.NAME, "username").send_keys("testuser")
        self.driver.find_element(By.NAME, "password").send_keys("password123")
        self.driver.find_element(By.CSS_SELECTOR, "form button").click()

        # Check that we're redirected to the session page or homepage
        self.assertIn("session", self.browser.current_url)

if __name__ == '__main__':
    unittest.main()
