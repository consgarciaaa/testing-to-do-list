from flask import Blueprint, render_template, redirect, url_for, flash, request, session, current_app
from flask_login import login_user, login_required, logout_user
from app import db, oauth
from app.models.user import User
import secrets
import requests

bp = Blueprint('auth', __name__)

# Ruta de inicio
@bp.route('/')
def home():
    return redirect(url_for('auth.login'))

# Ruta de registro de usuario
@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = request.form['password'].strip()

        if not username or not email or not password:
            return render_template('register.html', error='All fields are required.'), 400

        user = User.query.filter((User.username == username) | (User.email == email)).first()
        if user:
            return render_template('register.html', error='Username or email already exists.'), 400

        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')

# Ruta de login
@bp.route('/login', methods=['GET', 'POST'])
def login():
    weather = None
    error = None

    try:
        response = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": 20.6597,
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
    except Exception as e:
        print(f"Error fetching weather: {e}")

    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash("Logged in successfully!", "success")
            return redirect(url_for('tasks.index'))
        else:
            error = "Invalid username or password."
            return render_template('login.html', error=error, weather=weather), 400

    return render_template('login.html', weather=weather)

# Ruta de logout
@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for('auth.login'))

# Ruta de OAuth
@bp.route('/login/<provider>')
def oauth_login(provider):
    client = oauth.create_client(provider)
    if not client:
        flash(f"Provider '{provider}' is not supported.")
        return redirect(url_for('auth.login'))

    redirect_uri = url_for('auth.oauth_callback', provider=provider, _external=True)
    session['nonce'] = secrets.token_urlsafe(32) if provider == 'google' else None
    return client.authorize_redirect(redirect_uri)

# Callback de OAuth
@bp.route('/login/<provider>/callback')
def oauth_callback(provider):
    if current_app.config['TESTING']:
        user = User.query.filter_by(email='test_oauth@example.com').first()
        if not user:
            user = User(username='test_oauth', email='test_oauth@example.com')
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
        login_user(user)
        return redirect(url_for('tasks.index'))

    client = oauth.create_client(provider)
    token = client.authorize_access_token()
    user_info = client.get('userinfo').json() if provider == 'google' else client.get('user').json()

    user = User.query.filter_by(email=user_info['email']).first()
    if not user:
        user = User(username=user_info['email'].split('@')[0], email=user_info['email'])
        user.set_password(secrets.token_urlsafe(16))
        db.session.add(user)
        db.session.commit()

    login_user(user)
    return redirect(url_for('tasks.index'))
