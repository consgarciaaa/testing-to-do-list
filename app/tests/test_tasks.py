import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import pytest
from flask import url_for
from app.models.tasks import Task  # Cambiamos la importación para reflejar el nuevo archivo
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

def test_create_task_valid_input(client):
    user = User(username='testuser', email='test@example.com')
    user.set_password('password')
    db.session.add(user)
    db.session.commit()

    login_user(client, 'testuser', 'password')

    # Test creación de tarea válida
    response = client.post('/tasks/create_task', data={'content': 'Test task', 'priority': '1'}, follow_redirects=True)
    assert response.status_code == 302  # Redirige tras la creación
    task = db.session.get(Task, 1)
    assert task is not None
    assert task.content == '<p>Test task</p>'
    assert task.priority == 1
    assert task.user_id == user.id

def test_create_task_empty_content(client):
    user = User(username='testuser', email='test@example.com')
    user.set_password('password')
    db.session.add(user)
    db.session.commit()

    login_user(client, 'testuser', 'password')

    # Test creación de tarea con contenido vacío
    response = client.post('/tasks/create_task', data={'content': '', 'priority': '1'}, follow_redirects=True)
    assert response.status_code == 400

def test_create_task_invalid_priority(client):
    user = User(username='testuser', email='test@example.com')
    user.set_password('password')
    db.session.add(user)
    db.session.commit()

    login_user(client, 'testuser', 'password')

    # Test creación de tarea con prioridad no válida
    response = client.post('/tasks/create_task', data={'content': 'Test', 'priority': 'high'}, follow_redirects=True)
    assert response.status_code == 400

def test_delete_task(client):
    user = User(username='testuser', email='test@example.com')
    user.set_password('password')
    db.session.add(user)
    db.session.commit()

    login_user(client, 'testuser', 'password')

    task = Task(content='Test task', priority=1, user_id=user.id)
    db.session.add(task)
    db.session.commit()

    # Test eliminación de tarea
    response = client.post(url_for('tasks.delete_task', task_id=task.id), follow_redirects=True)
    assert response.status_code == 200
    assert db.session.get(Task, task.id) is None

def test_create_task_missing_input(client):
    # Simula la creación de una tarea con campos faltantes
    response = client.post('/tasks/create_task', data={'priority': '1'}, follow_redirects=True)
    
    # Validar el código de estado
    assert response.status_code == 400, "El código de estado debería ser 400 para datos incompletos."
    
    # Validar que la respuesta sea JSON
    assert response.is_json, "La respuesta debería estar en formato JSON."
    
    # Validar el contenido del mensaje de error
    error_message = response.get_json()
    assert error_message == {"error": "Content cannot be empty"}, f"Mensaje de error inesperado: {error_message}"



def test_create_task_markdown_sanitization(client):
    user = User(username='testuser', email='test@example.com')
    user.set_password('password')
    db.session.add(user)
    db.session.commit()

    login_user(client, 'testuser', 'password')

    response = client.post('/tasks/create_task', data={'content': '**Bold Task**', 'priority': '1'})
    task = db.session.get(Task, 1)
    assert task.content == '<p><strong>Bold Task</strong></p>'  # Verificar que el markdown fue procesado correctamente
    assert response.status_code == 302  # Redirige tras la creación

def test_update_task_content_and_priority(client):
    user = User(username='testuser', email='test@example.com')
    user.set_password('password')
    db.session.add(user)
    db.session.commit()

    login_user(client, 'testuser', 'password')

    task = Task(content='Old task', priority=1, user_id=user.id)
    db.session.add(task)
    db.session.commit()

    response = client.post(f'/tasks/update_task/{task.id}', data={'content': 'Updated task', 'priority': '2'})
    updated_task = db.session.get(Task, task.id)
    
    assert updated_task.content == '<p>Updated task</p>'
    assert updated_task.priority == 2
    assert response.status_code == 302  # Redirige tras la actualización

def test_update_task_not_authorized(client):
    owner = User(username='owner', email='owner@example.com')
    owner.set_password('password')
    user02 = User(username='user02', email='user02@example.com')
    user02.set_password('testpassword')
    db.session.add_all([owner, user02])
    db.session.commit()

    task = Task(content='Original task', priority=1, user_id=owner.id)
    db.session.add(task)
    db.session.commit()

    login_user(client, 'user02', 'testpassword')

    response = client.post(f'/tasks/update_task/{task.id}', data={'content': 'New content', 'priority': '2'})
    
    assert response.status_code == 403  # El usuario no autorizado debería recibir un error 403

def test_task_priority_order(client):
    user = User(username='testuser', email='test@example.com')
    user.set_password('password')
    db.session.add(user)
    db.session.commit()

    login_user(client, 'testuser', 'password')

    task1 = Task(content='Low priority task', priority=1, user_id=user.id)
    task2 = Task(content='High priority task', priority=10, user_id=user.id)
    db.session.add_all([task1, task2])
    db.session.commit()

    response = client.get('/tasks/')
    assert response.status_code == 200
    tasks = response.get_data(as_text=True)
    assert tasks.index('High priority task') < tasks.index('Low priority task')  # Verifica que la tarea de alta prioridad aparezca primero
