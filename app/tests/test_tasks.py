import sys
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
            print("Tablas creadas:", db.metadata.tables.keys())  # Corregido
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

    response = client.post('/tasks/create_task', data={'content': 'Test task', 'priority': '1'}, follow_redirects=False)
    assert response.status_code == 302
    assert response.headers['Location'].endswith('/tasks/')

    task = Task.query.filter_by(content='<p>Test task</p>').first()
    assert task is not None, "La tarea no fue encontrada en la base de datos."
    assert task.priority == 1
    assert task.user_id == user.id

# 2. Test: Crear tarea con contenido vacío
def test_create_task_empty_content(client):
    user = User(username='testuser', email='test@example.com', password='password123')
    user.set_password('password')
    db.session.add(user)
    db.session.commit()

    login_user(client, 'testuser', 'password')

    response = client.post('/tasks/create_task', data={'content': '', 'priority': '1'}, follow_redirects=True)
    assert response.status_code == 400
    assert b"Content cannot be empty" in response.data

# 3. Test: Crear tarea con prioridad no válida
def test_create_task_invalid_priority(client):
    user = User(username='testuser', email='test@example.com', password='password123')
    user.set_password('password')
    db.session.add(user)
    db.session.commit()

    login_user(client, 'testuser', 'password')

    response = client.post('/tasks/create_task', data={'content': 'Test', 'priority': 'high'}, follow_redirects=True)
    assert response.status_code == 400
    assert b"Invalid priority" in response.data

# 4. Test: Eliminar una tarea
def test_delete_task(client):
    user = User(username='testuser', email='test@example.com', password='password123')
    user.set_password('password')
    db.session.add(user)
    db.session.commit()

    login_user(client, 'testuser', 'password')

    task = Task(content='Test task', priority=1, user_id=user.id)
    db.session.add(task)
    db.session.commit()

    response = client.post(url_for('tasks.delete_task', task_id=task.id), follow_redirects=True)
    assert response.status_code == 200
    assert db.session.get(Task, task.id) is None

# 5. Test: Crear tarea con campos faltantes
def test_create_task_missing_input(client):
    user = User(username='testuser', email='test@example.com', password='password123')
    user.set_password('password')
    db.session.add(user)
    db.session.commit()

    login_user(client, 'testuser', 'password')

    response = client.post('/tasks/create_task', data={'priority': '1'}, follow_redirects=True)
    assert response.status_code == 400
    assert b"Content cannot be empty" in response.data
