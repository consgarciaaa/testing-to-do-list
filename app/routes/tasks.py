from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app import db  # Ajustamos la ruta para que use el módulo principal
from app.models.tasks import Task  # Aseguramos que se importe el modelo desde el archivo correcto
import markdown
import bleach
from datetime import datetime

bp = Blueprint('tasks', __name__)

@bp.route('/')
@login_required
def index():
    tasks = Task.query.filter_by(user_id=current_user.id).order_by(
        Task.priority.desc(), Task.created_at.desc()
    ).all()
    return render_template('index.html', tasks=tasks)

@bp.route('/create_task', methods=['POST'])
@login_required
def create_task():
    content = request.form.get('content')
    priority = request.form.get('priority', 0)

    # Validación para contenido vacío
    if not content:
        print("Error: Content cannot be empty.")
        return jsonify({"error": "Content cannot be empty"}), 400

    # Validación para prioridad no numérica
    try:
        priority = int(priority)
    except ValueError:
        print("Error: Invalid priority.")
        return jsonify({"error": "Invalid priority"}), 400

    # Procesamiento de Markdown y sanitización
    html_content = markdown.markdown(content, extensions=['extra'])
    sanitized_content = bleach.clean(
        html_content,
        tags=[
            'p', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'ul', 'ol', 'li', 'img', 'a', 'code', 'pre'
        ],
        attributes={'img': ['src', 'alt'], 'a': ['href', 'title']}
    )

    # Creación de la tarea
    task = Task(content=sanitized_content, priority=priority, user_id=current_user.id)
    db.session.add(task)
    db.session.commit()

    print(f"Tarea creada exitosamente: {task}")

    # Redireccionar tras la creación
    print("Redireccionando al índice de tareas.")
    return redirect(url_for('tasks.index'))


@bp.route('/update_task/<int:task_id>', methods=['POST'])
@login_required
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    content = request.form.get('content')
    priority = request.form.get('priority', task.priority)

    # Procesamiento de Markdown y sanitización
    html_content = markdown.markdown(content, extensions=['extra'])
    sanitized_content = bleach.clean(
        html_content,
        tags=[
            'p', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'ul', 'ol', 'li', 'img', 'a', 'code', 'pre'
        ],
        attributes={'img': ['src', 'alt'], 'a': ['href', 'title']}
    )

    task.content = sanitized_content
    task.priority = int(priority)
    task.updated_at = datetime.utcnow()
    db.session.commit()

    return redirect(url_for('tasks.index'))

@bp.route('/delete_task/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('tasks.index'))


@bp.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Devuelve todas las tareas del usuario autenticado."""
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    tasks_list = [
        {
            'id': task.id,
            'content': task.content,
            'priority': task.priority,
            'created_at': task.created_at.isoformat(),
        }
        for task in tasks
    ]
    return jsonify(tasks_list), 200

@bp.route('/api/tasks', methods=['POST'])
def create_task_api():
    """Crea una nueva tarea a través de la API."""
    data = request.get_json()

    if not data or 'content' not in data:
        return jsonify({"error": "Content is required"}), 400

    priority = data.get('priority', 0)
    try:
        priority = int(priority)
    except ValueError:
        return jsonify({"error": "Invalid priority"}), 400

    new_task = Task(content=data['content'], priority=priority, user_id=current_user.id)
    db.session.add(new_task)
    db.session.commit()

    return jsonify({
        'id': new_task.id,
        'content': new_task.content,
        'priority': new_task.priority,
        'created_at': new_task.created_at.isoformat()
    }), 201

@bp.route('/view_task/<int:task_id>', methods=['GET'])
@login_required
def view_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    return jsonify({
        'id': task.id,
        'content': task.content,
        'priority': task.priority,
        'created_at': task.created_at.isoformat(),
    }), 200
