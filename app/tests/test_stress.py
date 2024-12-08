import pytest
from app import create_app, db
from app.models.user import User
from app.models.tasks import Task
from config import TestingConfig

# Configuración de pruebas
@pytest.fixture(scope="module")
def client():
    app = create_app(TestingConfig)
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Crear un usuario base
            user = User(username="Constanza", email="constanza@example.com")
            user.set_password("1234")
            db.session.add(user)
            db.session.commit()
            yield client
            db.session.remove()
            db.drop_all()

# Función auxiliar para iniciar sesión
def login_user(client, username="Constanza", password="1234"):
    return client.post("/login", data={"username": username, "password": password}, follow_redirects=False)

# Prueba de rendimiento para inicio de sesión
@pytest.mark.benchmark
def test_login_benchmark(client, benchmark):
    """Prueba de rendimiento para inicio de sesión"""
    # Ejecuta el benchmark para el login
    result = benchmark(lambda: login_user(client))
    
    # Verifica que el login redirija correctamente
    assert result.status_code == 302, f"El inicio de sesión falló. Código recibido: {result.status_code}"
    
    location = result.headers.get("Location", "No Location header found")
    assert "/tasks" in location, f"Redirección inesperada: {location}"

# Prueba de rendimiento para crear una tarea
@pytest.mark.benchmark
def test_create_task_benchmark(client, benchmark):
    """Prueba de rendimiento para la creación de una tarea"""
    # Inicia sesión antes de crear la tarea
    login_user(client)

    # Ejecuta el benchmark para crear una tarea
    result = benchmark(lambda: client.post("/tasks/create_task", data={
        "content": "Tarea de prueba de rendimiento",
        "priority": "1"
    }, follow_redirects=True))
    
    # Verifica el resultado
    assert result.status_code == 200, "Error al crear la tarea."
    
    # Asegura que la tarea se haya creado en la base de datos
    with client.application.app_context():
        task = Task.query.filter_by(content="Tarea de prueba de rendimiento").first()
        assert task is not None, "La tarea no fue encontrada en la base de datos."

@pytest.mark.benchmark
def test_massive_task_creation(client, benchmark):
    """Prueba de rendimiento para la creación masiva de tareas."""
    login_user(client)
    
    def create_tasks():
        for i in range(1000):
            client.post("/tasks/create_task", data={
                "content": f"Tarea masiva {i}",
                "priority": "1"
            }, follow_redirects=True)
    
    benchmark(create_tasks)
    with client.application.app_context():
        count = Task.query.count()
    assert count >= 1000, "No se crearon suficientes tareas."
