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

@pytest.fixture(scope="module")
def driver():
    # Configura el driver para las pruebas
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    yield driver
    driver.quit()

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    # Configura la base de datos para pruebas
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})
    with app.app_context():
        db.create_all()
        # Crea un usuario de prueba para login
        user = User(username="Constanza", email="constanza@example.com")
        user.set_password("1234")
        db.session.add(user)
        db.session.commit()
        yield
        db.drop_all()
        db.session.remove()

def test_login(driver):
    driver.get("http://127.0.0.1:5000")
    assert "Login" in driver.page_source

    # Completa el formulario de login
    username_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "username"))
    )
    password_field = driver.find_element(By.NAME, "password")
    submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")

    username_field.send_keys("Constanza")
    password_field.send_keys("1234")
    submit_button.click()

    # Verifica redirección al dashboard
    assert "Your Tasks" in driver.page_source

def test_create_task(driver):
    driver.get("http://127.0.0.1:5000")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "username"))
    ).send_keys("Constanza")
    driver.find_element(By.NAME, "password").send_keys("1234")
    driver.find_element(By.XPATH, "//button[@type='submit']").click()

    # Crear nueva tarea
    content_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "content"))
    )
    priority_field = driver.find_element(By.NAME, "priority")
    submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")

    content_field.send_keys("Nueva tarea E2E")
    priority_field.send_keys("1")
    submit_button.click()

    # Verifica que la tarea fue creada
    tasks = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "task-content"))
    )
    assert any("Nueva tarea E2E" in task.text for task in tasks)

def test_delete_task(driver):
    driver.get("http://127.0.0.1:5000")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "username"))
    ).send_keys("Constanza")
    driver.find_element(By.NAME, "password").send_keys("1234")
    driver.find_element(By.XPATH, "//button[@type='submit']").click()

    # Eliminar tarea
    delete_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Delete')]"))
    )
    delete_button.click()

    # Verifica que la tarea fue eliminada
    tasks = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "task-content"))
    )
    assert not any("Nueva tarea E2E" in task.text for task in tasks)

def test_responsive_design(driver):
    driver.set_window_size(375, 812)  # Modo móvil
    driver.get("http://127.0.0.1:5000")
    assert "Login" in driver.page_source

    driver.set_window_size(1920, 1080)  # Modo escritorio
    assert "Login" in driver.page_source

"""def test_mocked_oauth_login(driver):
    driver.get("http://127.0.0.1:5000/login/google/callback")

    # Verifica redirección al dashboard
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//h1[contains(text(), 'Your Tasks')]"))
    )
    assert "Your Tasks" in driver.page_source"""
