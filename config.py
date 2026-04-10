# config.py - For Render.com
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'jetsetta-super-secret-key-2026-change-in-production')
    
    # PostgreSQL Database from Render
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:password123@localhost:5432/jetsetta_db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Paystack Keys (Test keys recommended)
    PAYSTACK_PUBLIC_KEY = os.getenv('PAYSTACK_PUBLIC_KEY')
    PAYSTACK_SECRET_KEY = os.getenv('PAYSTACK_SECRET_KEY')
    
    # OpenWeatherMap API Key
    OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')

    # Email Configuration (Optional for now)
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')