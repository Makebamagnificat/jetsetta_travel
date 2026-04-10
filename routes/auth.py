# routes/auth.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import User 
from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    print("=== LOGIN ROUTE CALLED ===")
    
    if current_user.is_authenticated:
        print("User already authenticated, redirecting to dashboard")
        return redirect(url_for('user.dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        print(f"Login attempt with email: {email}")
        
        if not email or not password:
            flash('Please enter both email and password', 'danger')
            return render_template('login.html')
        
        # Clean email
        email = email.strip().lower()
        
        user = User.query.filter_by(email=email).first()
        
        if user:
            print(f"User found: {user.email}, checking password...")
            if check_password_hash(user.password, password):
                print("Password correct - logging in user")
                login_user(user)
                flash(f'Welcome back, {user.name}!', 'success')
                
                if user.role == "admin":
                    print("Redirecting to admin dashboard")
                    return redirect(url_for('admin.dashboard'))
                print("Redirecting to user dashboard")
                return redirect(url_for('user.dashboard'))
            else:
                print("Password incorrect")
                flash('Invalid email or password', 'danger')
        else:
            print("No user found with that email")
            flash('Invalid email or password', 'danger')
    
    return render_template('login.html')


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('user.dashboard'))
        
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not name or not email or not password:
            flash('All fields are required', 'danger')
            return render_template('signup.html')
        
        email = email.strip().lower()
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered. Please login.', 'danger')
            return redirect(url_for('auth.login'))
        
        new_user = User(
            name=name.strip(),
            email=email,
            password=generate_password_hash(password),
            role='user'
        )
        
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        flash(f'Welcome, {new_user.name}! Your account has been created.', 'success')
        
        
        return redirect(url_for('auth.login'))
    
    return render_template('signup.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('user.index'))