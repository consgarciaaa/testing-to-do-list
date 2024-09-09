from app import create_app, db
from config import Config

app = create_app(Config)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=app.config['DEBUG'])