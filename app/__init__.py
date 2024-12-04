from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from authlib.integrations.flask_client import OAuth

db = SQLAlchemy()
login_manager = LoginManager()
oauth = OAuth()

def create_app(config_class):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    oauth.init_app(app)
    
    # Configuración de OAuth
    oauth.register(
        name='google',
        client_id=app.config.get('GOOGLE_CLIENT_ID'),
        client_secret=app.config.get('GOOGLE_CLIENT_SECRET'),
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'},
    )

    oauth.register(
        name='github',
        client_id=app.config.get('GITHUB_CLIENT_ID'),
        client_secret=app.config.get('GITHUB_CLIENT_SECRET'),
        access_token_url='https://github.com/login/oauth/access_token',
        authorize_url='https://github.com/login/oauth/authorize',
        api_base_url='https://api.github.com/',
        client_kwargs={'scope': 'user:email'},
    )

    # Importar y registrar Blueprints
    from .routes.weather import bp as weather_bp
    app.register_blueprint(weather_bp)


    from .routes import auth, tasks
    app.register_blueprint(auth.bp)
    app.register_blueprint(tasks.bp, url_prefix='/tasks')

    # Cargar el modelo de usuario
    from app.models.user import User  # Ajustado para reflejar la nueva ubicación del modelo

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app
