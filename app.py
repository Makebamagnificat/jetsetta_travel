from flask import Flask
from config import Config
from models import db
from flask_login import LoginManager
from flask_mail import Mail
import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# 1️⃣ Initialize extensions WITHOUT app
mail = Mail()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app():
    # 2️⃣ Create Flask app
    app = Flask(__name__)
    app.config.from_object(Config)

    # Step 3: Configure app for mail
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'animpongmary123@gmail.com')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'ayou rfra ooof pnay')

    # 4️⃣ Initialize extensions with app
    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)

    # 5️⃣ Register Blueprints
    from routes.auth import auth_bp
    from routes.user import user_bp
    from routes.admin import admin_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(user_bp)           # Main routes at root /
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # 6️⃣ Create database tables
    with app.app_context():
        db.create_all()
        print("✅ Database tables are created successfully")
    
    
    return app



# 8️⃣ Run the app
if __name__ == '__main__':
    app = create_app()
    print("🚀 Jetsetta Travel & Tours server starting...")
    print("🌐 Visit: http://127.0.0.1:5001")
    app.run(debug=True, port=5001)   # Using port 5001 to avoid conflicts