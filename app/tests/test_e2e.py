from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pytest
import sys
import os

# Ajuste del path para importar correctamente la aplicación
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from app import create_app, db
from app.models.user import User
from config import TestingConfig

BASE_URL = "http://127.0.0.1:5005"

# Configura la base de datos
@pytest.fixture(scope="module", autouse=True)
def setup_database():
    app = create_app(TestingConfig)
    with app.app_context():
        db.create_all()
        # Usuario base para las pruebas
        user = User(username="Constanza", email="constanza@example.com")
        user.set_password("1234")
        db.session.add(user)
        db.session.commit()
        yield
        db.drop_all()
        db.session.remove()

# Configura Selenium
@pytest.fixture(scope="module")
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    yield driver
    driver.quit()

# Función auxiliar de login
def login(driver, username="Constanza", password="1234"):
    driver.get(f"{BASE_URL}/login")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "username"))
    ).send_keys(username)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.XPATH, "//button[@type='submit']").click()

# Test de inicio de sesión
def test_login(driver):
    login(driver)
    assert "Your Tasks" in driver.page_source, "El texto 'Your Tasks' no está presente tras iniciar sesión."

# Test de creación de tarea
def test_create_task(driver):
    login(driver)
    driver.get(f"{BASE_URL}/tasks")
    content_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "content"))
    )
    content_field.send_keys("Nueva tarea")
    driver.find_element(By.NAME, "priority").send_keys("1")
    driver.find_element(By.XPATH, "//button[@type='submit']").click()

    tasks = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "task-content"))
    )
    assert any("Nueva tarea" in task.text for task in tasks), "La tarea no se creó correctamente."

# Test de mensaje de error en login
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
    assert "Invalid username or password." in error_message.text, "El mensaje de error no fue mostrado."

# Test de diseño responsivo
def test_responsive_design(driver):
    driver.set_window_size(375, 812)  # Modo móvil
    driver.get(f"{BASE_URL}/login")
    assert "Login" in driver.page_source, "La página de login no aparece correctamente en móvil."

    driver.set_window_size(1920, 1080)  # Modo escritorio
    assert "Login" in driver.page_source, "La página de login no aparece correctamente en escritorio."

# Test de edición de tarea
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
    assert any("Tarea editada" in task.text for task in tasks), "La tarea no se editó correctamente."

# Test de cierre de sesión
def test_logout(driver):
    login(driver)
    driver.get(f"{BASE_URL}/logout")
    assert "Login" in driver.page_source, "El usuario no fue redirigido correctamente al cerrar sesión."

# Función auxiliar para iniciar sesión
# Función auxiliar para iniciar sesión
def test_login(driver):
    driver.get(f"{BASE_URL}/login")
    try:
        username_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        username_field.send_keys("Constanza")

        password_field = driver.find_element(By.NAME, "password")
        password_field.send_keys("1234")

        login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        login_button.click()

        assert "Your Tasks" in driver.page_source, "El inicio de sesión falló"
    except TimeoutException as e:
        print(f"Error de tiempo de espera: {e}")
        raise

# Prueba de eliminación de tarea
def test_delete_task(driver):
    login(driver)  # Inicia sesión antes de eliminar

    # Navega a la página de tareas
    driver.get(f"{BASE_URL}/tasks")

    # Crea una tarea de prueba
    task_content = "Tarea para eliminar"
    content_field = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, "content"))
    )
    priority_field = driver.find_element(By.ID, "priority")
    submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")

    content_field.send_keys(task_content)
    priority_field.send_keys("1")
    submit_button.click()

    # Asegura que la tarea fue creada
    task_element = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, f"//li[contains(@class, 'task-card') and .//div[text()='{task_content}']]"))
    )

    # Encuentra y hace clic en el botón "Delete"
    delete_button = task_element.find_element(By.XPATH, ".//form[contains(@class, 'inline')]/button")
    delete_button.click()

    # Verifica que la tarea desaparezca
    WebDriverWait(driver, 20).until_not(
        EC.presence_of_element_located((By.XPATH, f"//li[contains(@class, 'task-card') and .//div[text()='{task_content}']]"))
    )
