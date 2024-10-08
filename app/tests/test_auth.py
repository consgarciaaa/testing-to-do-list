import pytest
from flask import url_for
from werkzeug.security import check_password_hash
from app import create_app, db
from app.models import User
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

def test_password_hashing(client):
    # Setup: Create a new user and hash their password
    user = User(username='testuser', email='test@example.com')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()
    
    # Verifica que la contraseña está hasheada
    assert user.password_hash is not None
    assert check_password_hash(user.password_hash, 'password123')

def test_login_valid_credentials(client):
    # Setup: Create a user
    user = User(username='testuser', email='test@example.com')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()

    # Test: Log in with valid credentials
    response = client.post(url_for('auth.login'), data={'username': 'testuser', 'password': 'password123'})
    assert response.status_code == 302  # Redirige a la página de tareas después del login

def test_login_invalid_credentials(client):
    # Setup: Create a user
    user = User(username='testuser', email='test@example.com')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()

    # Test: Log in with an incorrect password
    response = client.post(url_for('auth.login'), data={'username': 'testuser', 'password': 'wrongpassword'})
    assert b'Invalid username or password' in response.data  # Verifica el mensaje flash para credenciales incorrectas

def test_session_management(client):
    # Setup: Create a user and log in
    user = User(username='testuser', email='test@example.com')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()

    # Log in
    client.post(url_for('auth.login'), data={'username': 'testuser', 'password': 'password123'})
    
    # Verifica que el usuario está logueado
    response = client.get(url_for('tasks.index'))
    assert response.status_code == 200  # Debe tener éxito porque el usuario está logueado
    
    # Logout
    client.get(url_for('auth.logout'))
    
    # Intenta acceder a una página que requiere login después del logout
    response = client.get(url_for('tasks.index'))
    assert response.status_code == 302  # Debe redirigir a la página de login ya que la sesión terminó
