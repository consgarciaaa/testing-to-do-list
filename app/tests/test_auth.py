import pytest
from flask import url_for
from werkzeug.security import check_password_hash
from app.models import User
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

def test_password_hashing(client):
    user = User(username='testuser', email='test@example.com')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()
    
    assert user.password_hash is not None
    assert check_password_hash(user.password_hash, 'password123')

def test_login_valid_credentials(client):
    user = User(username='testuser', email='test@example.com')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()

    response = client.post('/login', data={'username': 'testuser', 'password': 'password123'}, follow_redirects=True)
    assert response.status_code == 200

def test_login_invalid_credentials(client):
    user = User(username='testuser', email='test@example.com')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()

    response = client.post('/login', data={'username': 'testuser', 'password': 'wrongpassword'}, follow_redirects=True)
    assert response.status_code == 400
    assert b'Invalid username or password' in response.data

def test_session_management(client):
    user = User(username='testuser', email='test@example.com')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()

    client.post('/login', data={'username': 'testuser', 'password': 'password123'}, follow_redirects=True)
    
    response = client.get(url_for('tasks.index'))
    assert response.status_code == 200
    
    client.get('/logout', follow_redirects=True)
    
    response = client.get(url_for('tasks.index'))
    assert response.status_code == 302

