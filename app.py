# app.py - FIXED VERSION
from flask import Flask
from config import Config
from models import db
from flask_login import LoginManager

login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    # Register Blueprints
    from routes.auth import auth_bp
    from routes.user import user_bp
    from routes.admin import admin_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(user_bp)           # Main routes at root /
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # Create database tables
    with app.app_context():
        db.create_all()
        print("✅ Database tables are ready")

    return app

# IMPORTANT: user_loader must be defined OUTSIDE create_app()
@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

if __name__ == '__main__':
    app = create_app()
    print("🚀 Jetsetta Travel & Tours server starting...")
    print("🌐 Visit: http://127.0.0.1:5001")
    app.run(debug=True, port=5001)   # Using port 5001 to avoid conflicts