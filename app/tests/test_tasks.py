import pytest
from flask import url_for
from app.models import Task, User
from app import create_app, db
from config import TestingConfig  # Importamos TestingConfig desde config.py

@pytest.fixture
def client():
    app = create_app(TestingConfig)  # Usamos TestingConfig en lugar de 'testing'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

def login_user(client, username, password):
    with client.application.test_request_context():
        return client.post(url_for('auth.login'), data={'username': username, 'password': password})

def test_create_task_valid_input(client):
    user = User(username='testuser', email='test@example.com')
    user.set_password('password')
    db.session.add(user)
    db.session.commit()

    login_user(client, 'testuser', 'password')

    # Test de creación de tarea válida
    response = client.post(url_for('tasks.create_task'), data={'content': 'Test task', 'priority': '1'})
    assert response.status_code == 302
    task = Task.query.first()
    assert task is not None
    assert task.content == '<p>Test task</p>'
    assert task.priority == 1  # Comparando prioridad como número
    assert task.user_id == user.id

def test_create_task_empty_content(client):
    user = User(username='testuser', email='test@example.com')
    user.set_password('password')
    db.session.add(user)
    db.session.commit()

    login_user(client, 'testuser', 'password')

    # Test de creación de tarea con contenido vacío
    response = client.post(url_for('tasks.create_task'), data={'content': '', 'priority': '1'})
    assert response.status_code == 400  # Verifica que el código sea 400 para error

def test_create_task_invalid_priority(client):
    user = User(username='testuser', email='test@example.com')
    user.set_password('password')
    db.session.add(user)
    db.session.commit()

    login_user(client, 'testuser', 'password')

    # Test de creación de tarea con prioridad no válida (texto en vez de número)
    response = client.post(url_for('tasks.create_task'), data={'content': 'Test', 'priority': 'high'})
    assert response.status_code == 400  # Verifica que el código sea 400 para error de prioridad

def test_delete_task(client):
    user = User(username='testuser', email='test@example.com')
    user.set_password('password')
    db.session.add(user)
    db.session.commit()

    login_user(client, 'testuser', 'password')

    task = Task(content='Test task', priority=1, user_id=user.id)
    db.session.add(task)
    db.session.commit()

    # Test de eliminación de tarea
    response = client.post(url_for('tasks.delete_task', task_id=task.id))
    assert response.status_code == 302
    assert Task.query.get(task.id) is None
