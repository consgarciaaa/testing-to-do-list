import sys
import os

# Agregar el directorio raíz del proyecto al PATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app import create_app, db
from app.models.user import User
import pytest


@pytest.fixture(scope="module")
def client():
    app = create_app("config.TestingConfig")
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Crear un usuario para las pruebas
            user = User(username="Constanza", email="constanza@example.com")
            user.set_password("1234")
            db.session.add(user)
            db.session.commit()
            yield client
            db.session.remove()
            db.drop_all()


@pytest.mark.benchmark
def test_login_benchmark(client, benchmark):
    """Prueba de rendimiento para el inicio de sesión"""
    result = benchmark(lambda: client.post("/login", data={"username": "Constanza", "password": "1234"}))
    assert result.status_code == 200, "Error en la prueba de inicio de sesión."


@pytest.mark.benchmark
def test_create_task_benchmark(client, benchmark):
    """Prueba de rendimiento para la creación de una tarea"""
    result = benchmark(lambda: client.post("/tasks/create_task", data={
        "content": "Tarea de prueba de rendimiento",
        "priority": "1"
    }))
    assert result.status_code == 302, "Error al crear una tarea."
