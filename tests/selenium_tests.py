import time
import tempfile
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
#from selenium.webdriver.chrome.service import Service as ChromeService
#from selenium.webdriver.chrome.options import Options
from selenium.webdriver import Edge
from selenium.webdriver.edge.options import Options as EdgeOptions




import pytest
from selenium.webdriver import Edge
from selenium.webdriver.edge.options import Options as EdgeOptions

BASE_URL = "http://127.0.0.1:5000"

@pytest.fixture(scope="function")
def browser():
    options = EdgeOptions()
    options.add_argument("--headless=new")  # Run without GUI (optional)
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")  # Helpful in WSL/Linux
    driver = Edge(options=options)
    yield driver
    driver.quit()


def signup_user(browser, username, password):
    browser.get(f"{BASE_URL}/signup")
    browser.find_element(By.NAME, "username").send_keys(username)
    browser.find_element(By.NAME, "password").send_keys(password)
    browser.find_element(By.NAME, "password2").send_keys(password)
    browser.find_element(By.NAME, "submit").click()

def login_user(browser, username, password):
    browser.get(f"{BASE_URL}/signin")
    browser.find_element(By.NAME, "username").send_keys(username)
    browser.find_element(By.NAME, "password").send_keys(password)
    browser.find_element(By.NAME, "submit").click()

def test_signup(browser):
    signup_user(browser, "testuser1", "testpass123")
    assert "/signin" in browser.current_url

def test_login(browser):
    login_user(browser, "testuser1", "testpass123")
    assert "index" in browser.current_url

def test_record_study_session(browser):
    login_user(browser, "testuser1", "testpass123")
    browser.get(f"{BASE_URL}/session")

    # Start session via JS or custom start button (simulate if needed)
    browser.execute_script("""
        fetch('/api/sessions', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ type: 'start' })
        }).then(res => console.log('Session started'));
    """)
    time.sleep(2)

    # Fill out session summary form
    browser.find_element(By.NAME, "subject").send_keys("Math Revision")
    Select(browser.find_element(By.NAME, "task_type")).select_by_value("Assignment")
    browser.find_element(By.NAME, "productivity").send_keys("80")
    browser.find_element(By.CSS_SELECTOR, "input[type='radio'][value='happy']").click()
    browser.find_element(By.NAME, "description").send_keys("Did some practice exams.")
    browser.find_element(By.CSS_SELECTOR, "form[action='/submit-session-summary'] button[type='submit']").click() 

    # Verify redirect back to /session
    assert "/session" in browser.current_url

def test_navigate_to_history(browser):
    login_user(browser, "testuser1", "testpass123")
    browser.get(f"{BASE_URL}/history")
    assert "History" in browser.page_source

def test_session_in_history(browser):
    login_user(browser, "testuser1", "testpass123")
    browser.get(f"{BASE_URL}/history")
    assert "Math Revision" in browser.page_source  # depends on how session is rendered
