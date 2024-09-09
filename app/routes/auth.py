from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, login_required, logout_user
from werkzeug.security import generate_password_hash
from .. import db, oauth
from ..models import User
import secrets

bp = Blueprint('auth', __name__)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter((User.username == username) | (User.email == email)).first()
        if user:
            flash('Username or email already exists.')
            return redirect(url_for('auth.register'))
        
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful. Please log in.')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('tasks.index'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@bp.route('/login/<provider>')
def oauth_login(provider):
    client = oauth.create_client(provider)
    redirect_uri = url_for('auth.oauth_callback', provider=provider, _external=True)
    print(f"Debug: Redirect URI is {redirect_uri}")  
    if provider == 'google':
        session['nonce'] = secrets.token_urlsafe(32)
        return client.authorize_redirect(redirect_uri, nonce=session['nonce'])
    return client.authorize_redirect(redirect_uri)

@bp.route('/login/<provider>/callback')
def oauth_callback(provider):
    client = oauth.create_client(provider)
    try:
        token = client.authorize_access_token()
    except Exception as e:
        flash(f"Error during OAuth: {str(e)}")
        return redirect(url_for('auth.login'))
    
    if provider == 'google':
        userinfo_endpoint = 'https://openidconnect.googleapis.com/v1/userinfo'
        resp = client.get(userinfo_endpoint)
        user_info = resp.json()
        if resp.status_code != 200:
            flash(f"Error fetching user info: {user_info.get('error_description', 'Unknown error')}")
            return redirect(url_for('auth.login'))
    elif provider == 'microsoft':
        user_info = client.userinfo()
    elif provider == 'github':
        resp = client.get('user')
        user_info = resp.json()
        emails = client.get('user/emails').json()
        user_info['email'] = next(email['email'] for email in emails if email['primary'])
    else:
        flash('Unsupported OAuth provider')
        return redirect(url_for('auth.login'))
    
    user = User.query.filter_by(email=user_info['email']).first()
    if not user:
        user = User(username=user_info['email'].split('@')[0], 
                    email=user_info['email'])
        user.set_password(secrets.token_urlsafe(16))  # Set a random password for OAuth users
        db.session.add(user)
        db.session.commit()
    
    login_user(user)
    return redirect(url_for('tasks.index'))