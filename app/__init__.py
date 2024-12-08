from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from authlib.integrations.flask_client import OAuth
import os

# Inicializar Extensiones
db = SQLAlchemy()
login_manager = LoginManager()
oauth = OAuth()

def create_app(config_class):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Inicializar Extensiones
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # Registrar Blueprints
    from app.routes.tasks import bp as tasks_bp
    app.register_blueprint(tasks_bp, url_prefix='/tasks')

    from app.routes.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/')

    from app.routes.movies import bp as movies_bp
    app.register_blueprint(movies_bp, url_prefix='/api/movies')

    # Configuración de OAuth
    oauth.init_app(app)
    oauth.register(
        name='google',
        client_id=os.environ.get('GOOGLE_CLIENT_ID'),
        client_secret=os.environ.get('GOOGLE_CLIENT_SECRET'),
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'},
    )

    # Cargar Usuario
    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Mostrar Rutas Registradas
    print(app.url_map)

    return app
