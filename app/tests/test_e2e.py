from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pytest
import time


@pytest.fixture
def driver():
    # Configura el WebDriver para Chrome
    driver = webdriver.Chrome(executable_path="PATH_TO_CHROMEDRIVER")  # Reemplaza con la ruta de tu ChromeDriver
    yield driver
    driver.quit()  # Cierra el navegador después de cada prueba


def test_login(driver):
    # Accede a la página principal (login)
    driver.get("http://127.0.0.1:5000")
    
    # Verifica el título de la página
    assert "Login" in driver.title

    # Completa el formulario de login
    username_field = driver.find_element(By.NAME, "username")
    password_field = driver.find_element(By.NAME, "password")

    username_field.send_keys("testuser")
    password_field.send_keys("password123")
    password_field.send_keys(Keys.RETURN)

    # Espera para que cargue la página
    time.sleep(2)

    # Verifica que redirigió a la página de tareas
    assert "Tasks" in driver.title


def test_create_task(driver):
    # Iniciar sesión
    driver.get("http://127.0.0.1:5000")
    driver.find_element(By.NAME, "username").send_keys("testuser")
    driver.find_element(By.NAME, "password").send_keys("password123", Keys.RETURN)
    time.sleep(2)

    # Completa el formulario de creación de tarea
    content_field = driver.find_element(By.NAME, "content")
    priority_field = driver.find_element(By.NAME, "priority")
    submit_button = driver.find_element(By.NAME, "create_task")

    content_field.send_keys("Nueva tarea E2E")
    priority_field.send_keys("5")
    submit_button.click()

    # Verifica que la tarea fue creada
    tasks = driver.find_elements(By.CLASS_NAME, "task-content")
    assert any("Nueva tarea E2E" in task.text for task in tasks), "La tarea no fue creada."


def test_delete_task(driver):
    # Iniciar sesión
    driver.get("http://127.0.0.1:5000")
    driver.find_element(By.NAME, "username").send_keys("testuser")
    driver.find_element(By.NAME, "password").send_keys("password123", Keys.RETURN)
    time.sleep(2)

    # Elimina la primera tarea
    delete_button = driver.find_elements(By.CLASS_NAME, "delete-task")[0]
    delete_button.click()

    # Verifica que la tarea fue eliminada
    time.sleep(2)
    tasks = driver.find_elements(By.CLASS_NAME, "task-content")
    assert not any("Nueva tarea E2E" in task.text for task in tasks), "La tarea no fue eliminada."
