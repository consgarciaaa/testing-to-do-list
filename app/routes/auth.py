from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, login_required, logout_user
from werkzeug.security import generate_password_hash
from app import db, oauth  # Ajustamos las rutas de importación
from app.models.user import User  # Importación desde el archivo correcto
import secrets
import requests

bp = Blueprint('auth', __name__)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        email = request.form.get('email').strip()
        password = request.form.get('password')
        
        # Validación de entrada
        if not username or not email or not password:
            flash('All fields are required.')
            return redirect(url_for('auth.register'))

        # Verificar si el usuario o el email ya existen
        user = User.query.filter((User.username == username) | (User.email == email)).first()
        if user:
            flash('Username or email already exists.')
            return redirect(url_for('auth.register'))
        
        # Crear un nuevo usuario
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful. Please log in.')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')

@bp.route('/')
def home():
    return redirect(url_for('auth.login'))


@bp.route('/login', methods=['GET', 'POST'])
def login():
    weather = None  # Variable para guardar la información del clima
    error = None

    # Obtener clima desde la API
    try:
        response = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": 20.6597,  # Coordenadas de Guadalajara
                "longitude": -103.3496,
                "current_weather": "true"
            }
        )
        if response.status_code == 200:
            data = response.json()
            weather = {
                "temperature": data["current_weather"]["temperature"],
                "windspeed": data["current_weather"]["windspeed"]
            }
        else:
            print(f"Error obteniendo clima: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Excepción obteniendo clima: {e}")

    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        # Validar credenciales
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('tasks.index'))
        else:
            error = "Invalid username or password."
            return render_template('login.html', error=error, weather=weather), 400

    return render_template('login.html', weather=weather)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@bp.route('/login/<provider>')
def oauth_login(provider):
    client = oauth.create_client(provider)
    if not client:
        flash(f"Provider '{provider}' is not supported.")
        return redirect(url_for('auth.login'))

    redirect_uri = url_for('auth.oauth_callback', provider=provider, _external=True)
    session['nonce'] = secrets.token_urlsafe(32) if provider == 'google' else None
    return client.authorize_redirect(redirect_uri)

@bp.route('/login/<provider>/callback')
def oauth_callback(provider):
    client = oauth.create_client(provider)
    try:
        token = client.authorize_access_token()
    except Exception as e:
        flash(f"Error during OAuth: {str(e)}")
        return redirect(url_for('auth.login'))

    # Obtener información del usuario
    if provider == 'google':
        user_info = client.get('userinfo').json()
    else:
        user_info = client.get('user').json()

    # Verificar si el usuario existe o crearlo
    user = User.query.filter_by(email=user_info.get('email')).first()
    if not user:
        user = User(
            username=user_info.get('email').split('@')[0],
            email=user_info.get('email')
        )
        user.set_password(secrets.token_urlsafe(16))
        db.session.add(user)
        db.session.commit()
    
    login_user(user)
    return redirect(url_for('tasks.index'))
