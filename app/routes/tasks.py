from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models.tasks import Task
import markdown
import bleach
from datetime import datetime

bp = Blueprint('tasks', __name__)

# Página principal
@bp.route('/')
@login_required
def index():
    tasks = Task.query.filter_by(user_id=current_user.id).order_by(
        Task.priority.desc(), Task.created_at.desc()
    ).all()
    return render_template('index.html', tasks=tasks)

# Crear tarea
@bp.route('/create_task', methods=['POST'])
@login_required
def create_task():
    content = request.form.get('content', "").strip()  # Maneja el valor faltante
    priority = request.form.get('priority', "0").strip()  # Maneja la prioridad por defecto

    if not content:
        flash("Content cannot be empty", "error")
        return redirect(url_for('tasks.index'))

    try:
        priority = int(priority)
    except ValueError:
        flash("Invalid priority", "error")
        return redirect(url_for('tasks.index'))

    if priority not in [0, 1, 2]:
        flash("Invalid priority", "error")
        return redirect(url_for('tasks.index'))

    # Crear la tarea
    html_content = markdown.markdown(content, extensions=['extra'])
    sanitized_content = bleach.clean(
        html_content, tags=['p', 'strong', 'em', 'ul', 'ol', 'li', 'a', 'code', 'pre'],
        attributes={'a': ['href', 'title']}
    )

    task = Task(content=sanitized_content, priority=priority, user_id=current_user.id)
    db.session.add(task)
    db.session.commit()

    flash("Task created successfully", "success")
    return redirect(url_for('tasks.index'))

# Actualizar tarea
@bp.route('/update_task/<int:task_id>', methods=['POST'])
@login_required
def update_task(task_id):
    task = Task.query.get_or_404(task_id)

    if task.user_id != current_user.id:
        flash("Unauthorized access", "error")
        return redirect(url_for('tasks.index'))

    content = request.form.get('content')
    priority = request.form.get('priority', task.priority)

    if not content.strip():
        flash("Content cannot be empty", "error")
        return redirect(url_for('tasks.index'))

    try:
        priority = int(priority)
    except ValueError:
        flash("Invalid priority", "error")
        return redirect(url_for('tasks.index'))

    html_content = markdown.markdown(content.strip(), extensions=['extra'])
    sanitized_content = bleach.clean(
        html_content, tags=['p', 'strong', 'em', 'ul', 'ol', 'li', 'a', 'code', 'pre'],
        attributes={'a': ['href', 'title']}
    )

    task.content = sanitized_content
    task.priority = priority
    task.updated_at = datetime.utcnow()
    db.session.commit()

    flash("Task updated successfully", "success")
    return redirect(url_for('tasks.index'))

# Eliminar tarea
# Eliminar tarea
@bp.route('/delete_task/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)

    if task.user_id != current_user.id:
        flash("Unauthorized access", "error")
        return redirect(url_for('tasks.index'))

    db.session.delete(task)
    db.session.commit()

    flash("Task deleted successfully", "success")
    return redirect(url_for('tasks.index'))

# Ver tarea específica
@bp.route('/view_task/<int:task_id>', methods=['GET'])
@login_required
def view_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        flash("Unauthorized access", "error")
        return redirect(url_for('tasks.index'))

    # Mostrar detalles de la tarea usando flash
    flash(f'Task: {task.content} - Priority: {["Low", "Medium", "High"][task.priority]}', "success")
    return render_template('index.html', tasks=[task])

# API para listar tareas
@bp.route('/api/tasks', methods=['GET'])
@login_required
def get_tasks():
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
