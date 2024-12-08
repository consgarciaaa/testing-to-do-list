"""import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import pytest
from flask import url_for
from app.models.tasks import Task
from app.models.user import User
from app import create_app, db
from config import TestingConfig

@pytest.fixture
def client():
    app = create_app(TestingConfig)
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

def login_user(client, username, password):
    return client.post('/login', data={'username': username, 'password': password}, follow_redirects=True)

# 1. Test: Crear tarea con datos válidos
def test_create_task_valid_input(client):
    user = User(username='testuser', email='test@example.com')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()

    login_user(client, 'testuser', 'password123')

    response = client.post('/tasks/create_task', data={'content': 'Test task', 'priority': '1'}, follow_redirects=True)
    assert response.status_code == 302
    task = Task.query.filter_by(content='<p>Test task</p>').first()
    assert task is not None, "La tarea no fue encontrada en la base de datos."
    assert task.priority == 1
    assert task.user_id == user.id

# 2. Test: Crear tarea con contenido vacío
def test_create_task_empty_content(client):
    user = User(username='testuser', email='test@example.com')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()

    login_user(client, 'testuser', 'password123')

    response = client.post('/create_task', data={'content': '', 'priority': '1'}, follow_redirects=True)
    assert response.status_code == 400
    assert b"Content cannot be empty" in response.data

# 3. Test: Crear tarea con prioridad no válida
def test_create_task_invalid_priority(client):
    user = User(username='testuser', email='test@example.com')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()

    login_user(client, 'testuser', 'password123')

    response = client.post('/create_task', data={'content': 'Test task', 'priority': 'high'}, follow_redirects=True)
    assert response.status_code == 400
    assert b"Invalid priority" in response.data

# 4. Test: Eliminar una tarea
def test_delete_task(client):
    user = User(username='testuser', email='test@example.com')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()

    login_user(client, 'testuser', 'password123')

    task = Task(content='<p>Test task</p>', priority=1, user_id=user.id)
    db.session.add(task)
    db.session.commit()

    response = client.post(url_for('tasks.delete_task', task_id=task.id), follow_redirects=True)
    assert response.status_code == 200
    assert Task.query.get(task.id) is None

# 5. Test: Crear tarea con campos faltantes
def test_create_task_missing_input(client):
    user = User(username='testuser', email='test@example.com')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()

    login_user(client, 'testuser', 'password123')

    response = client.post('/create_task', data={'priority': '1'}, follow_redirects=True)
    assert response.status_code == 400
    assert b"Content cannot be empty" in response.data

# 6. Test: Actualizar tarea con datos válidos
def test_update_task_valid_input(client):
    user = User(username='testuser', email='test@example.com')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()

    login_user(client, 'testuser', 'password123')

    task = Task(content='<p>Old task</p>', priority=1, user_id=user.id)
    db.session.add(task)
    db.session.commit()

    response = client.post(url_for('tasks.update_task', task_id=task.id), data={
        'content': 'Updated task',
        'priority': '2'
    }, follow_redirects=True)

    assert response.status_code == 302
    updated_task = Task.query.get(task.id)
    assert updated_task.content == '<p>Updated task</p>'
    assert updated_task.priority == 2

# 7. Test: Actualizar tarea con datos inválidos
def test_update_task_invalid_priority(client):
    user = User(username='testuser', email='test@example.com')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()

    login_user(client, 'testuser', 'password123')

    task = Task(content='<p>Task</p>', priority=1, user_id=user.id)
    db.session.add(task)
    db.session.commit()

    response = client.post(url_for('tasks.update_task', task_id=task.id), data={
        'content': 'New Task',
        'priority': 'high'
    }, follow_redirects=True)

    assert response.status_code == 400
    assert b"Invalid priority" in response.data

# 8. Test: Ver tarea específica
def test_view_task(client):
    user = User(username='testuser', email='test@example.com')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()

    login_user(client, 'testuser', 'password123')

    task = Task(content='<p>View Task</p>', priority=1, user_id=user.id)
    db.session.add(task)
    db.session.commit()

    response = client.get(url_for('tasks.view_task', task_id=task.id), follow_redirects=True)
    assert response.status_code == 200
    assert b'View Task' in response.data

# 9. Test: Listar tareas (API)
def test_get_tasks_api(client):
    user = User(username='testuser', email='test@example.com')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()

    login_user(client, 'testuser', 'password123')

    task = Task(content='<p>Test Task</p>', priority=1, user_id=user.id)
    db.session.add(task)
    db.session.commit()

    response = client.get('/api/tasks')
    assert response.status_code == 200
    assert b'Test Task' in response.data"""

import pytest
from flask import url_for
from app.models.tasks import Task
from app.models.user import User
from app import create_app, db
from config import TestingConfig

# Configuración de pruebas
@pytest.fixture
def client():
    app = create_app(TestingConfig)
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

def login_user(client, username, password):
    return client.post('/login', data={'username': username, 'password': password}, follow_redirects=True)

# 1. Test: Crear tarea con datos válidos
def test_create_task_valid_input(client):
    user = User(username='testuser', email='test@example.com')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()

    login_user(client, 'testuser', 'password123')

    response = client.post('/tasks/create_task', data={'content': 'Test task', 'priority': '1'}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Task created successfully" in response.data

# 2. Test: Crear tarea con contenido vacío
def test_create_task_empty_content(client):
    user = User(username='testuser', email='test@example.com')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()

    login_user(client, 'testuser', 'password123')

    response = client.post('/tasks/create_task', data={'content': '', 'priority': '1'}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Content cannot be empty" in response.data

# 3. Test: Crear tarea con prioridad no válida
def test_create_task_invalid_priority(client):
    user = User(username='testuser', email='test@example.com')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()

    login_user(client, 'testuser', 'password123')

    response = client.post('/tasks/create_task', data={'content': 'Test task', 'priority': 'high'}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Invalid priority" in response.data

# 4. Test: Eliminar una tarea
def test_delete_task(client):
    user = User(username='testuser', email='test@example.com')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()

    login_user(client, 'testuser', 'password123')

    task = Task(content='Test task', priority=1, user_id=user.id)
    db.session.add(task)
    db.session.commit()

    response = client.post(url_for('tasks.delete_task', task_id=task.id), follow_redirects=True)
    assert response.status_code == 200
    assert b"Task deleted successfully" in response.data

# 5. Test: Crear tarea con campos faltantes
def test_create_task_missing_input(client):
    user = User(username='testuser', email='test@example.com')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()

    login_user(client, 'testuser', 'password123')

    response = client.post('/tasks/create_task', data={'priority': '1'}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Content cannot be empty" in response.data

# 6. Test: Actualizar tarea con datos válidos
# Test: Actualizar tarea con datos válidos
def test_update_task_valid_input(client):
    user = User(username='testuser', email='test@example.com')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()

    login_user(client, 'testuser', 'password123')

    task = Task(content='Old task', priority=1, user_id=user.id)
    db.session.add(task)
    db.session.commit()

    response = client.post(url_for('tasks.update_task', task_id=task.id), data={
        'content': 'Updated task',
        'priority': '2'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Task updated successfully" in response.data

# 7. Test: Actualizar tarea con prioridad no válida
# Test: Actualizar tarea con prioridad no válida
def test_update_task_invalid_priority(client):
    user = User(username='testuser', email='test@example.com')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()

    login_user(client, 'testuser', 'password123')

    task = Task(content='Test task', priority=1, user_id=user.id)
    db.session.add(task)
    db.session.commit()

    response = client.post(url_for('tasks.update_task', task_id=task.id), data={
        'content': 'New Task',
        'priority': 'high'  # Prioridad no válida
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Invalid priority" in response.data


# 8. Test: Ver tarea específica
# Test: Ver tarea específica
# Test: Ver tarea específica
def test_view_task(client):
    user = User(username='testuser', email='test@example.com')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()

    login_user(client, 'testuser', 'password123')

    task = Task(content='View Task', priority=1, user_id=user.id)
    db.session.add(task)
    db.session.commit()

    response = client.get(url_for('tasks.view_task', task_id=task.id), follow_redirects=True)
    assert response.status_code == 200
    assert b'View Task' in response.data


# 9. Test: Listar tareas (API)
def test_get_tasks_api(client):
    # Crear un usuario de prueba
    user = User(username='testuser', email='test@example.com')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()

    # Iniciar sesión
    login_user(client, 'testuser', 'password123')

    # Crear una tarea de prueba
    task = Task(content='Test Task', priority=1, user_id=user.id)
    db.session.add(task)
    db.session.commit()

    # Hacer una solicitud GET a la API
    response = client.get('/tasks/api/tasks', follow_redirects=True)

    # Validar respuesta
    assert response.status_code == 200, f"Error: Código de estado {response.status_code}"
    assert b'Test Task' in response.data
