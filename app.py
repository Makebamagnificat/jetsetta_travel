from flask import Flask
from config import Config
from extensions import db, login_manager   # ✅ use extensions

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['SQLALCHEMY_ECHO'] = True

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    # Import models (no circular import now)
    import models

    # Register blueprints
    from routes.auth import auth_bp
    from routes.user import user_bp
    from routes.admin import admin_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # User loader
    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return db.session.get(User, int(user_id))

    # Create tables
    with app.app_context():
        db.create_all()
        print("✅ Database tables created successfully")

    return app


app = create_app()

if __name__ == '__main__':
    print("🚀 Starting Jetsetta on http://127.0.0.1:5001")
    app.run(debug=True, port=5001)