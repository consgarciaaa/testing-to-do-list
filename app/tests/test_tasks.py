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
            print("Tablas creadas:", db.engine.table_names()) 
            yield client
            db.session.remove()
            db.drop_all()

def login_user(client, username, password):
    return client.post('/login', data={'username': username, 'password': password}, follow_redirects=True)

# 1. Test: Crear tarea con datos válidos
def test_create_task_valid_input(client):
    # Crear un usuario
    user = User(username='testuser', email='test@example.com')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()

    # Iniciar sesión con el usuario
    login_user(client, 'testuser', 'password123')

    # Crear tarea válida
    response = client.post('/tasks/create_task', data={'content': 'Test task', 'priority': '1'}, follow_redirects=False)

    # Validar que redirige correctamente
    # Validar que redirige correctamente
    assert response.status_code == 302, "El código de estado no es 302 tras crear la tarea."
    assert response.headers['Location'].endswith('/tasks/'), "La redirección no apunta a la URL relativa de 'tasks.index'."


    # Confirmar que la tarea fue creada en la base de datos
    task = Task.query.filter_by(content='<p>Test task</p>').first()
    assert task is not None, "La tarea no fue encontrada en la base de datos."
    assert task.priority == 1, "La prioridad de la tarea no es correcta."
    assert task.user_id == user.id, "El usuario de la tarea no coincide con el usuario logueado."


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
    assert b"Invalid priority" in response.data  # Mensaje esperado del servidor

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

# 6. Test: Sanitización de Markdown en contenido de tarea
def test_create_task_markdown_sanitization(client):
    user = User(username='testuser', email='test@example.com', password='password123')
    user.set_password('password')
    db.session.add(user)
    db.session.commit()

    # Iniciar sesión para el usuario de prueba
    login_user(client, 'testuser', 'password')

    # Crear tarea con contenido en Markdown
    response = client.post('/tasks/create_task', data={'content': '**Bold Task**', 'priority': '1'}, follow_redirects=False)


    # Validar redirección
    assert response.status_code == 302, "No hubo redirección tras crear la tarea"
    assert response.headers['Location'] == url_for('tasks.index', _external=True), "La redirección no apunta al índice de tareas."


    # Validar que la tarea se creó correctamente en la base de datos
    task = db.session.query(Task).filter_by(user_id=user.id).first()
    assert task is not None, "La tarea no se creó en la base de datos"
    assert task.content == '<p><strong>Bold Task</strong></p>', "El contenido procesado no es el esperado"


# 7. Test: Actualizar contenido y prioridad de una tarea
def test_update_task_content_and_priority(client):
    user = User(username='testuser', email='test@example.com', password='password123')
    user.set_password('password')
    db.session.add(user)
    db.session.commit()

    login_user(client, 'testuser', 'password')

    task = Task(content='Old task', priority=1, user_id=user.id)
    db.session.add(task)
    db.session.commit()

    response = client.post(f'/tasks/update_task/{task.id}', data={'content': 'Updated task', 'priority': '2'}, follow_redirects=True)
    updated_task = db.session.get(Task, task.id)
    assert updated_task.content == '<p>Updated task</p>'
    assert updated_task.priority == 2
    assert response.status_code == 302

# 8. Test: Actualizar tarea no autorizada
def test_update_task_not_authorized(client):
    owner = User(username='owner', email='owner@example.com', password='password123')
    owner.set_password('password')
    user02 = User(username='user02', email='user02@example.com', password='password123')
    user02.set_password('testpassword')
    db.session.add_all([owner, user02])
    db.session.commit()

    task = Task(content='Original task', priority=1, user_id=owner.id)
    db.session.add(task)
    db.session.commit()

    login_user(client, 'user02', 'testpassword')

    response = client.post(f'/tasks/update_task/{task.id}', data={'content': 'New content', 'priority': '2'}, follow_redirects=True)
    assert response.status_code == 403

# 9. Test: Orden de tareas por prioridad
def test_task_priority_order(client):
    user = User(username='testuser', email='test@example.com', password='password123')
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
    assert tasks.index('High priority task') < tasks.index('Low priority task')

# 10. Test: Validar que una tarea solo puede ser vista por su creador
def test_task_visibility_restricted_to_owner(client):
    owner = User(username='owner', email='owner@example.com', password='password123')
    owner.set_password('password')
    other_user = User(username='otheruser', email='otheruser@example.com',password='password123')
    other_user.set_password('password')
    db.session.add_all([owner, other_user])
    db.session.commit()

    task = Task(content='Owner task', priority=1, user_id=owner.id)
    db.session.add(task)
    db.session.commit()

    login_user(client, 'otheruser', 'password')

    response = client.get(url_for('tasks.view_task', task_id=task.id))
    assert response.status_code == 403
