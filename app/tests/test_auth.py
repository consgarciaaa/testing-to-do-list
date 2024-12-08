import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import pytest
from app import create_app, db
from app.models.user import User
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

# Test 1: Registro de un nuevo usuario con datos válidos
def test_register_new_user(client):
    response = client.post('/register', data={
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'password123'
    }, follow_redirects=True)
    assert response.status_code == 200, "Error al registrar un nuevo usuario."
    user = User.query.filter_by(username='newuser').first()
    assert user is not None, "El usuario no se registró correctamente."
    assert user.check_password('password123'), "La contraseña no fue almacenada correctamente."

# Test 2: Registro con campos vacíos
def test_register_incomplete_data(client):
    response = client.post('/register', data={
        'username': '',
        'email': '',
        'password': ''
    }, follow_redirects=True)
    assert response.status_code == 400, "Se permitió el registro con campos vacíos."
    assert b'All fields are required.' in response.data, "Mensaje de error no encontrado."

# Test 3: Registro con un correo existente
def test_register_duplicate_email(client):
    user = User(username='existinguser', email='existing@example.com')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()

    response = client.post('/register', data={
        'username': 'newuser',
        'email': 'existing@example.com',
        'password': 'password123'
    }, follow_redirects=True)
    assert response.status_code == 400, "Se permitió el registro con un correo duplicado."
    assert b'Username or email already exists.' in response.data, "Mensaje de error no encontrado."

# Test 4: Registro con un nombre de usuario existente
def test_register_duplicate_username(client):
    user = User(username='existinguser', email='unique@example.com')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()

    response = client.post('/register', data={
        'username': 'existinguser',
        'email': 'new@example.com',
        'password': 'password123'
    }, follow_redirects=True)
    assert response.status_code == 400, "Se permitió el registro con un nombre de usuario duplicado."
    assert b'Username or email already exists.' in response.data, "Mensaje de error no encontrado."

# Test 5: Inicio de sesión con credenciales válidas
def test_login_valid_credentials(client):
    user = User(username='testuser', email='test@example.com')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()

    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'password123'
    }, follow_redirects=True)
    assert response.status_code == 200, "Error al iniciar sesión con credenciales válidas."
    assert b'Welcome' in response.data, "Mensaje de bienvenida no encontrado."

# Test 6: Inicio de sesión con credenciales inválidas
def test_login_invalid_credentials(client):
    user = User(username='testuser', email='test@example.com')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()

    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'wrongpassword'
    }, follow_redirects=True)
    assert response.status_code == 400, "Se permitió el inicio de sesión con credenciales inválidas."
    assert b'Invalid username or password.' in response.data, "Mensaje de error no encontrado."

# Test 7: Manejo de sesiones (inicio y cierre de sesión)
def test_session_management(client):
    user = User(username='testuser', email='test@example.com')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()

    client.post('/login', data={
        'username': 'testuser',
        'password': 'password123'
    }, follow_redirects=True)

    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200, "Error al cerrar sesión."
    assert b'Login' in response.data, "Mensaje de cierre de sesión no encontrado."

# Test 8: Callback de OAuth (simulado)
def test_mocked_oauth_login(client):
    with client.application.app_context():
        user = User.query.filter_by(email='test_oauth@example.com').first()
        if not user:
            user = User(username='test_oauth', email='test_oauth@example.com')
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()

    response = client.get('/login/google/callback', follow_redirects=True)
    assert response.status_code == 200, "Error en el flujo de inicio de sesión con OAuth."

# Test 9: Cierre de sesión después de un inicio de sesión exitoso
def test_logout_after_login(client):
    # Crear y registrar un usuario
    user = User(username='logoutuser', email='logoutuser@example.com')
    user.set_password('logoutpass')
    db.session.add(user)
    db.session.commit()

    # Iniciar sesión con el usuario creado
    login_response = client.post('/login', data={
        'username': 'logoutuser',
        'password': 'logoutpass'
    }, follow_redirects=True)
    assert login_response.status_code == 200, "Error al iniciar sesión antes del cierre de sesión."
    assert b'Welcome' in login_response.data, "Mensaje de bienvenida no encontrado tras el inicio de sesión."

    # Cerrar sesión
    logout_response = client.get('/logout', follow_redirects=True)
    assert logout_response.status_code == 200, "Error al cerrar sesión."
    assert b'Login' in logout_response.data, "Mensaje de inicio de sesión no encontrado tras cerrar sesión."

    def test_mocked_oauth_login(client):
        with requests_mock.Mocker() as mocker:
            mock_response_token = {
            "access_token": "mock_access_token",
            "token_type": "Bearer",
            "expires_in": 3600,
            "refresh_token": "mock_refresh_token",
        }
        mocker.post(
            "https://oauth2.googleapis.com/token",
            json=mock_response_token,
            status_code=200,
        )

        mock_response_user = {
            "id": "123456789",
            "email": "mockuser@example.com",
            "verified_email": True,
            "name": "Mock User",
        }
        mocker.get(
            "https://www.googleapis.com/oauth2/v1/userinfo",
            json=mock_response_user,
            status_code=200,
        )

        response = client.get(url_for('oauth_callback', provider='google'))
        assert response.status_code == 302
        assert response.location.endswith("/dashboard")

