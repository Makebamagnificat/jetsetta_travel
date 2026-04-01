# routes/admin.py - Safe & Clean Version
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, User, Booking, Itinerary, ActivityRSVP

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.role != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('user.index'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function


@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    total_users = User.query.count()
    total_bookings = Booking.query.count()
    pending_bookings = Booking.query.filter_by(status='pending').count()
    total_itineraries = Itinerary.query.count()
    recent_rsvps = ActivityRSVP.query.order_by(ActivityRSVP.created_at.desc()).limit(10).all()

    return render_template('admin/dashboard.html',
                           total_users=total_users,
                           total_bookings=total_bookings,
                           pending_bookings=pending_bookings,
                           total_itineraries=total_itineraries,
                           recent_rsvps=recent_rsvps)


@admin_bp.route('/users')
@admin_required
def users():
    all_users = User.query.all()
    return render_template('admin/users.html', users=all_users)


@admin_bp.route('/bookings')
@admin_required
def bookings():
    all_bookings = Booking.query.all()
    return render_template('admin/bookings.html', bookings=all_bookings)


@admin_bp.route('/bookings/confirm/<int:booking_id>')
@admin_required
def confirm_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    booking.status = 'confirmed'
    db.session.commit()
    flash('Booking confirmed successfully!', 'success')
    return redirect(url_for('admin.bookings'))


@admin_bp.route('/itineraries')
@admin_required
def itineraries():
    all_itineraries = Itinerary.query.all()
    return render_template('admin/itineraries.html', itineraries=all_itineraries)


@admin_bp.route('/itineraries/add', methods=['POST'])
@admin_required
def add_itinerary():
    new_itinerary = Itinerary(
        day=request.form.get('day'),
        title=request.form.get('title'),
        description=request.form.get('description'),
        date_str=request.form.get('date_str')
    )
    db.session.add(new_itinerary)
    db.session.commit()
    flash('New activity added!', 'success')
    return redirect(url_for('admin.itineraries'))

@admin_bp.route('/rsvps')
@admin_required
def rsvps():
    all_rsvps = ActivityRSVP.query.order_by(ActivityRSVP.created_at.desc()).all()
    return render_template('admin/rsvps.html', rsvps=all_rsvps)

@admin_bp.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        user.name = request.form.get('name')
        user.email = request.form.get('email')
        user.role = request.form.get('role')

        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('admin.users'))

    return render_template('admin/edit_user.html', user=user)

@admin_bp.route('/users/delete/<int:user_id>')
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)

    # Prevent admin from deleting themselves (important safety)
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('admin.users'))

    db.session.delete(user)
    db.session.commit()

    flash('User deleted successfully!', 'success')
    return redirect(url_for('admin.users'))

# Edit itinerary
@admin_bp.route('/itinerary/edit/<int:itinerary_id>', methods=['GET', 'POST'])
def edit_itinerary(itinerary_id):
    itinerary = Itinerary.query.get_or_404(itinerary_id)

    if request.method == 'POST':
        itinerary.day = request.form['day']
        itinerary.date_str = request.form['date_str']
        itinerary.title = request.form['title']
        itinerary.description = request.form['description']

        db.session.commit()
        flash("✅ Itinerary updated successfully!")
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/edit_itinerary.html', itinerary=itinerary)


# Delete itinerary
@admin_bp.route('/itinerary/delete/<int:itinerary_id>', methods=['POST'])
def delete_itinerary(itinerary_id):
    itinerary = Itinerary.query.get_or_404(itinerary_id)
    db.session.delete(itinerary)
    db.session.commit()
    flash("❌ Itinerary deleted successfully!")
    return redirect(url_for('admin.dashboard'))