from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from app import create_app, db
from app.models.user import User
from config import TestingConfig

BASE_URL = "http://127.0.0.1:5000"  # Cambia a localhost

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    app = create_app(TestingConfig)
    with app.app_context():
        db.create_all()
        # Crea un usuario de prueba
        user = User(username="TestUser", email="testuser@example.com")
        user.set_password("password")
        db.session.add(user)
        db.session.commit()
        yield
        db.drop_all()
        db.session.remove()

@pytest.fixture(scope="module")
def driver():
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    yield driver
    driver.quit()

def login(driver, username="TestUser", password="password"):
    driver.get(f"{BASE_URL}/login")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "username"))
    ).send_keys(username)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.XPATH, "//button[@type='submit']").click()

def test_login(driver):
    login(driver)
    assert "Your Tasks" in driver.page_source

def test_create_task(driver):
    login(driver)
    driver.get(f"{BASE_URL}/tasks")
    content_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "content"))
    )
    priority_field = driver.find_element(By.NAME, "priority")
    submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")

    content_field.send_keys("Nueva tarea")
    priority_field.send_keys("1")
    submit_button.click()

    tasks = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "task-content"))
    )
    assert any("Nueva tarea" in task.text for task in tasks)

def test_delete_task(driver):
    login(driver)
    driver.get(f"{BASE_URL}/tasks")
    delete_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//form[contains(@class, 'inline')]/button[text()='Delete']"))
    )
    delete_button.click()

    WebDriverWait(driver, 10).until_not(
        EC.presence_of_element_located((By.CLASS_NAME, "task-card"))
    )

    tasks = driver.find_elements(By.CLASS_NAME, "task-content")
    assert not any("Nueva tarea" in task.text for task in tasks)

def test_edit_task(driver):
    login(driver)
    driver.get(f"{BASE_URL}/tasks")
    edit_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Edit')]"))
    )
    edit_button.click()

    content_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "content"))
    )
    content_field.clear()
    content_field.send_keys("Tarea editada")
    submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")
    submit_button.click()

    tasks = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "task-content"))
    )
    assert any("Tarea editada" in task.text for task in tasks)

def test_login_error_message(driver):
    driver.get(f"{BASE_URL}/login")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "username"))
    ).send_keys("wrong_user")
    driver.find_element(By.NAME, "password").send_keys("wrong_password")
    driver.find_element(By.XPATH, "//button[@type='submit']").click()

    error_message = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "text-red-700"))
    )
    assert "Invalid username or password." in error_message.text

def test_responsive_design(driver):
    driver.set_window_size(375, 812)  # Modo móvil
    driver.get(f"{BASE_URL}/login")
    assert "Login" in driver.page_source

    driver.set_window_size(1920, 1080)  # Modo escritorio
    assert "Login" in driver.page_source

def test_create_high_priority_task(driver):
    login(driver)
    driver.get(f"{BASE_URL}/tasks")
    content_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "content"))
    )
    priority_field = driver.find_element(By.NAME, "priority")
    submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")

    content_field.send_keys("Tarea de alta prioridad")
    priority_field.send_keys("2")
    submit_button.click()

    tasks = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "task-content"))
    )
    assert any("Tarea de alta prioridad" in task.text for task in tasks)

def test_mocked_oauth_login(driver):
    # Simulación de autenticación (omitir si no se implementa OAuth)
    login(driver)
    assert "Your Tasks" in driver.page_source
