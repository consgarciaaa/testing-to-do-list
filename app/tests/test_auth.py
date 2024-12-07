import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import pytest
from flask import url_for
from werkzeug.security import check_password_hash
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

# 1. Test: Validar el hashing de contraseñas
def test_password_hashing(client):
    user = User(username='testuser', email='test@example.com', password='password123')
    db.session.add(user)
    db.session.commit()
    
    assert user.password_hash is not None, "El hash de la contraseña no se generó."
    assert check_password_hash(user.password_hash, 'password123'), "El hash no coincide con la contraseña original."

# 2. Test: Inicio de sesión con credenciales válidas
def test_login_valid_credentials(client):
    user = User(username='testuser', email='test@example.com', password='password123')
    db.session.add(user)
    db.session.commit()

    response = client.post('/login', data={'username': 'testuser', 'password': 'password123'}, follow_redirects=True)
    assert response.status_code == 200, "El inicio de sesión válido no retornó el código 200."
    assert b'Welcome' in response.data, "El usuario no fue bienvenido tras iniciar sesión correctamente."

# 3. Test: Inicio de sesión con credenciales inválidas
def test_login_invalid_credentials(client):
    user = User(username='testuser', email='test@example.com', password='password123')
    db.session.add(user)
    db.session.commit()

    response = client.post('/login', data={'username': 'testuser', 'password': 'wrongpassword'}, follow_redirects=True)
    assert response.status_code == 400, "El inicio de sesión con credenciales inválidas no retornó el código 400."
    assert b'Invalid username or password' in response.data, "El mensaje de error no fue encontrado en la respuesta."

# 4. Test: Manejo de sesiones (inicio y cierre de sesión)
def test_session_management(client):
    user = User(username='testuser', email='test@example.com', password='password123')
    db.session.add(user)
    db.session.commit()

    client.post('/login', data={'username': 'testuser', 'password': 'password123'}, follow_redirects=True)
    response = client.get(url_for('tasks.index'))
    assert response.status_code == 200, "El usuario autenticado no pudo acceder a la página de tareas."

    client.get('/logout', follow_redirects=True)
    response = client.get(url_for('tasks.index'))
    assert response.status_code == 302, "El usuario no autenticado pudo acceder a la página de tareas."

# 5. Test: Registro de un nuevo usuario
def test_register_new_user(client):
    response = client.post('/register', data={
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'password123'
    }, follow_redirects=True)
    assert response.status_code == 200, "El registro no retornó el código 200."
    user = User.query.filter_by(username='newuser').first()
    assert user is not None, "El usuario no fue registrado en la base de datos."
    assert user.check_password('password123'), "La contraseña del usuario no fue correctamente almacenada."

# 6. Test: Registro con datos incompletos
def test_register_incomplete_data(client):
    response = client.post('/register', data={'username': '', 'email': '', 'password': ''}, follow_redirects=True)
    assert response.status_code == 400, "El registro con datos incompletos no retornó el código 400."
    assert b'All fields are required.' in response.data, "El mensaje de error no fue encontrado en la respuesta."

# 7. Test: Registro con un correo ya existente
def test_register_duplicate_email(client):
    user = User(username='existinguser', email='existing@example.com', password='password123')
    db.session.add(user)
    db.session.commit()

    response = client.post('/register', data={
        'username': 'newuser',
        'email': 'existing@example.com',
        'password': 'password123'
    }, follow_redirects=True)
    assert response.status_code == 400, "El registro con un correo duplicado no retornó el código 400."
    assert b'Username or email already exists.' in response.data, "El mensaje de error no fue encontrado en la respuesta."

# 8. Test: Registro con un nombre de usuario ya existente
def test_register_duplicate_username(client):
    user = User(username='existinguser', email='existing@example.com', password='password123')
    db.session.add(user)
    db.session.commit()

    response = client.post('/register', data={
        'username': 'existinguser',
        'email': 'new@example.com',
        'password': 'password123'
    }, follow_redirects=True)
    assert response.status_code == 400, "El registro con un nombre de usuario duplicado no retornó el código 400."
    assert b'Username or email already exists.' in response.data, "El mensaje de error no fue encontrado en la respuesta."

# 9. Test: Logout
def test_logout(client):
    user = User(username='testuser', email='test@example.com', password='password123')
    db.session.add(user)
    db.session.commit()

    client.post('/login', data={'username': 'testuser', 'password': 'password123'}, follow_redirects=True)
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200, "El logout no redirigió correctamente."
    assert b'Login' in response.data, "El usuario no fue redirigido a la página de inicio de sesión."

