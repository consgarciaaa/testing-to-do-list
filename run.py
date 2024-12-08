from app import create_app, db
from config import Config

# Crea la aplicación usando la configuración del entorno
app = create_app(Config)

if __name__ == '__main__':
    # Inicializa el contexto de la aplicación para crear las tablas
    with app.app_context():
        db.create_all()

    # Ejecuta la aplicación en modo debug, escuchando conexiones externas
    app.run(debug=True, host='0.0.0.0', port=5005)


