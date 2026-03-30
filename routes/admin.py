# routes/admin.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models import (
    db, User, Booking, Itinerary, Review)
from models import ActivityRSVP

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('user.index'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    total_users = User.query.count()
    pending_bookings = Booking.query.filter_by(status='pending').count()
    total_bookings = Booking.query.count()
    return render_template('admin/dashboard.html', 
                         total_users=total_users,
                         pending_bookings=pending_bookings,
                         total_bookings=total_bookings)

@admin_bp.route('/users')
@admin_required
def users():
    all_users = User.query.all()
    return render_template('admin/users.html', users=all_users)

# VIEW USERS
@admin_bp.route('/admin/users')
def view_users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)

# Delete user
@admin_bp.route('/users/delete/<int:user_id>')
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash(f'User {user.username} has been deleted.', 'success')
    return redirect(url_for('admin.users'))

# Edit user
@admin_bp.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        user.username = request.form['username']
        user.email = request.form['email']
        # Add any other fields you want to edit
        db.session.commit()
        flash(f'User {user.username} has been updated.', 'success')
        return redirect(url_for('admin.users'))
    return render_template('admin/edit_user.html', user=user)

@admin_bp.route('/bookings')
@admin_required
def bookings():
    all_bookings = Booking.query.all()
    return render_template('admin/bookings.html', bookings=all_bookings)

# PENDING BOOKINGS
@admin_bp.route('/admin/bookings/pending')
def pending_bookings():
    bookings = Booking.query.filter_by(status='pending').all()
    return render_template('admin/pending_bookings.html', bookings=bookings)

@admin_bp.route('/confirm-booking/<int:booking_id>', methods=['POST'])
@admin_required
def confirm_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    booking.status = 'confirmed'
    db.session.commit()
    flash('Booking confirmed successfully!', 'success')
    return redirect(url_for('admin.bookings'))


# CONFIRMED BOOKINGS
@admin_bp.route('/admin/bookings/confirmed')
def confirmed_bookings():
    bookings = Booking.query.filter_by(status='confirmed').all()
    return render_template('admin/confirmed_bookings.html', bookings=bookings)

@admin_bp.route('/itineraries')
@admin_required
def itineraries():
    all_itineraries = Itinerary.query.all()
    return render_template('admin/itineraries.html', itineraries=all_itineraries)


# ACTIVITIES
@admin_bp.route('/admin/activities')
def activities():
    activities = ActivityRSVP.query.all()
    return render_template('admin/activities.html', activities=activities)

@admin_bp.route('/add-itinerary', methods=['POST'])
@admin_required
def add_itinerary():
    day = request.form.get('day')
    title = request.form.get('title')
    description = request.form.get('description')
    date = request.form.get('date')

    new_itinerary = Itinerary(
        day=day,
        title=title,
        description=description,
        date=date
    )
    db.session.add(new_itinerary)
    db.session.commit()
    
    flash('New activity added to itinerary!', 'success')
    return redirect(url_for('admin.itineraries'))