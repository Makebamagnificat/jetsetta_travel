from flask import Flask
from config import Config
from models import db, User
from flask_login import LoginManager
from flask_mail import Mail
import os

# 1️⃣ Initialize extensions (NO app yet)
db = db
mail = Mail()
login_manager = LoginManager()

login_manager.login_view = 'auth.login'

# 2️⃣ Define user loader AFTER login_manager is created
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # 3️⃣ Mail config
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')

    # 4️⃣ Database config (IMPORTANT FIX)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL',
        'sqlite:///site.db'  # fallback for local dev
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 5️⃣ Initialize extensions
    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)

    # 6️⃣ Register blueprints
    from routes.auth import auth_bp
    from routes.user import user_bp
    from routes.admin import admin_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # 7️⃣ Create DB tables
    with app.app_context():
        db.create_all()
        print("✅ Database tables created")

    return app


# 8️⃣ Run app locally
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5001)