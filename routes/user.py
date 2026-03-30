# routes/user.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from models import db, Itinerary, Booking, Review
import stripe
import os

user_bp = Blueprint('user', __name__)

# Initialize Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

@user_bp.route('/')
def index():
    return render_template('index.html')

@user_bp.route('/dashboard')
@login_required
def dashboard():
    itineraries = Itinerary.query.all()
    bookings = Booking.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', itineraries=itineraries, bookings=bookings)

@user_bp.route('/itineraries')
@login_required
def itineraries():
    itineraries = Itinerary.query.all()
    return render_template('itineraries.html', itineraries=itineraries)

@user_bp.route('/bookings')
@login_required
def bookings():
    user_bookings = Booking.query.filter_by(user_id=current_user.id).all()
    return render_template('bookings.html', bookings=user_bookings)

@user_bp.route('/reviews')
@login_required
def reviews():
    all_reviews = Review.query.all()
    return render_template('reviews.html', reviews=all_reviews)

# Accept Activity (RSVP)
@user_bp.route('/accept-activity/<int:itinerary_id>', methods=['POST'])
@login_required
def accept_activity(itinerary_id):
    # In a real app, you would have an RSVP model. For simplicity, we just flash success.
    flash(f'You have successfully joined the activity!', 'success')
    return redirect(url_for('user.itineraries'))

# Stripe Checkout Session
@user_bp.route('/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session():
    try:
        data = request.get_json()
        booking_id = data.get('booking_id')
        
        booking = Booking.query.filter_by(id=booking_id, user_id=current_user.id).first()
        if not booking or booking.status != 'pending':
            return jsonify({'error': 'Invalid booking'}), 400

        # Create Stripe Checkout Session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': booking.title,
                        'description': 'Jetsetta Luxury Travel Booking',
                    },
                    'unit_amount': int(booking.amount * 100),  # Convert to cents
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=url_for('user.payment_success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('user.bookings', _external=True),
            metadata={
                'booking_id': booking.id,
                'user_id': current_user.id
            }
        )
        
        return jsonify({'url': checkout_session.url})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/payment-success')
@login_required
def payment_success():
    session_id = request.args.get('session_id')
    # In production, verify the session with Stripe
    flash('Payment successful! Your booking is now confirmed.', 'success')
    # Update booking status
    # booking = Booking.query... (add logic here)
    return redirect(url_for('user.bookings'))

# Add this at the end of routes/user.py

@user_bp.route('/submit-review', methods=['POST'])
@login_required
def submit_review():
    text = request.form.get('text')
    if text and len(text.strip()) > 10:
        review = Review(
            user_id=current_user.id,
            text=text.strip(),
            stars=5
        )
        db.session.add(review)
        db.session.commit()
        flash('Thank you! Your review has been posted.', 'success')
    else:
        flash('Please write a meaningful review.', 'danger')
    
    return redirect(url_for('user.reviews'))