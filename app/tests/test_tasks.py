import pytest
from flask import url_for
from ..models import Task, User
from datetime import datetime
from .. import create_app, db
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

@pytest.fixture
def client():
    app = create_app('testing')
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

def login_user(client, username, password):
    return client.post(url_for('auth.login'), data={'username': username, 'password': password})

def test_create_task_valid_input(client):
    # Setup: Create a user and log in
    user = User(username='testuser', email='test@example.com')
    user.set_password('password')
    db.session.add(user)
    db.session.commit()

    login_user(client, 'testuser', 'password')
    
    # Test: Valid task creation
    response = client.post(url_for('tasks.create_task'), data={'content': 'Test task', 'priority': '1'})
    assert response.status_code == 302  # Redirect after successful creation
    task = Task.query.first()
    assert task is not None
    assert task.content == '<p>Test task</p>'
    assert task.priority == '1'
    assert task.user_id == user.id

def test_create_task_empty_content(client):
    # Similar setup as above
    user = User(username='testuser', email='test@example.com')
    user.set_password('password')
    db.session.add(user)
    db.session.commit()

    login_user(client, 'testuser', 'password')

    # Test: Task creation with empty content
    response = client.post(url_for('tasks.create_task'), data={'content': '', 'priority': '1'})
    assert response.status_code == 400  # Assuming your app returns 400 for bad request

def test_create_task_invalid_priority(client):
    # Similar setup as above
    user = User(username='testuser', email='test@example.com')
    user.set_password('password')
    db.session.add(user)
    db.session.commit()

    login_user(client, 'testuser', 'password')

    # Test: Task creation with invalid priority (non-integer)
    response = client.post(url_for('tasks.create_task'), data={'content': 'Test', 'priority': 'high'})
    assert response.status_code == 400  # Assuming your app returns 400 for bad request

def test_create_task_markdown_processing(client):
    # Similar setup as above
    user = User(username='testuser', email='test@example.com')
    user.set_password('password')
    db.session.add(user)
    db.session.commit()

    login_user(client, 'testuser', 'password')

    # Test: Markdown processing
    response = client.post(url_for('tasks.create_task'), data={'content': '**Bold text**', 'priority': '1'})
    task = Task.query.first()
    assert task.content == '<p><strong>Bold text</strong></p>'

def test_delete_task(client):
    # Setup user and task
    user = User(username='testuser', email='test@example.com')
    user.set_password('password')
    db.session.add(user)
    db.session.commit()

    login_user(client, 'testuser', 'password')

    task = Task(content='Test task', priority=1, user_id=user.id)
    db.session.add(task)
    db.session.commit()

    # Test: Valid task deletion
    response = client.post(url_for('tasks.delete_task', task_id=task.id))
    assert response.status_code == 302  # Redirect after successful deletion
    assert Task.query.get(task.id) is None
