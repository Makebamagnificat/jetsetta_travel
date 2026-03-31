# routes/admin.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, User, Booking, Itinerary, ActivityRSVP

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Decorator to enforce admin access
def admin_required(f):
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.role != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('user.index'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function


# -------------------- DASHBOARD --------------------
@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    total_users = User.query.count()
    total_bookings = Booking.query.count()
    pending_bookings = Booking.query.filter_by(status='pending').count()
    return render_template('admin/dashboard.html',
                           total_users=total_users,
                           total_bookings=total_bookings,
                           pending_bookings=pending_bookings)


# -------------------- USERS --------------------
@admin_bp.route('/users')
@admin_required
def users():
    """List all users"""
    all_users = User.query.all()
    return render_template('admin/users.html', users=all_users)


@admin_bp.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        user.name = request.form['name']
        user.email = request.form['email']
        db.session.commit()
        flash(f'User {user.name} has been updated.', 'success')
        return redirect(url_for('admin.users'))
    return render_template('admin/edit_user.html', user=user)


@admin_bp.route('/users/delete/<int:user_id>')
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    user_name = user.name
    db.session.delete(user)
    db.session.commit()
    flash(f'User {user_name} has been deleted.', 'success')
    return redirect(url_for('admin.users'))


# -------------------- BOOKINGS --------------------
@admin_bp.route('/bookings')
@admin_required
def bookings():
    """All bookings"""
    all_bookings = Booking.query.all()
    return render_template('admin/bookings.html', bookings=all_bookings)


@admin_bp.route('/bookings/pending')
@admin_required
def pending_bookings():
    bookings = Booking.query.filter_by(status='pending').all()
    return render_template('admin/pending_bookings.html', bookings=bookings)


@admin_bp.route('/bookings/confirmed')
@admin_required
def confirmed_bookings():
    bookings = Booking.query.filter_by(status='confirmed').all()
    return render_template('admin/confirmed_bookings.html', bookings=bookings)


@admin_bp.route('/bookings/confirm/<int:booking_id>', methods=['POST'])
@admin_required
def confirm_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    booking.status = 'confirmed'
    db.session.commit()
    flash('Booking confirmed successfully!', 'success')
    return redirect(url_for('admin.bookings'))


# -------------------- RSVPS / ACTIVITIES --------------------
@admin_bp.route('/rsvps/pending')
@admin_required
def pending_rsvps():
    rsvps = ActivityRSVP.query.filter_by(status='pending').order_by(ActivityRSVP.created_at.desc()).all()
    return render_template('admin/pending_rsvps.html', rsvps=rsvps)


@admin_bp.route('/rsvps/approve/<int:rsvp_id>')
@admin_required
def approve_rsvp(rsvp_id):
    rsvp = ActivityRSVP.query.get_or_404(rsvp_id)
    rsvp.status = 'approved'
    db.session.commit()
    flash(f"{rsvp.user.name}'s RSVP for '{rsvp.itinerary.title}' has been approved.", "success")
    return redirect(url_for('admin.pending_rsvps'))


@admin_bp.route('/activities')
@admin_required
def activities():
    """View all activity RSVPs"""
    activities = ActivityRSVP.query.all()
    return render_template('admin/activities.html', activities=activities)


# -------------------- ITINERARIES --------------------
@admin_bp.route('/itineraries')
@admin_required
def itineraries():
    all_itineraries = Itinerary.query.all()
    return render_template('admin/itineraries.html', itineraries=all_itineraries)


@admin_bp.route('/itineraries/add', methods=['POST'])
@admin_required
def add_itinerary():
    day = request.form.get('day')
    title = request.form.get('title')
    description = request.form.get('description')
    date_str = request.form.get('date')
    
    new_itinerary = Itinerary(
        day=day,
        title=title,
        description=description,
        date_str=date_str
    )
    db.session.add(new_itinerary)
    db.session.commit()
    
    flash('New itinerary/activity added!', 'success')
    return redirect(url_for('admin.itineraries'))