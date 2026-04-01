# routes/user.py - Cleaned & Fixed Version
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models import db, Itinerary, Booking, Review, ActivityRSVP
import stripe
import os

user_bp = Blueprint('user', __name__)

# Initialize Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

# ====================== MAIN PAGES ======================
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
    all_reviews = Review.query.order_by(Review.created_at.desc()).all()
    return render_template('reviews.html', reviews=all_reviews)

# ====================== ACTIVITY ACCEPT & BOOKING ======================
@user_bp.route('/accept-activity/<int:itinerary_id>', methods=['POST'])
@login_required
def accept_activity(itinerary_id):
    # Check if already accepted
    existing = ActivityRSVP.query.filter_by(
        user_id=current_user.id, 
        itinerary_id=itinerary_id
    ).first()
    
    if existing:
        flash('You have already joined this activity.', 'info')
        return redirect(url_for('user.bookings'))

    # Create RSVP
    rsvp = ActivityRSVP(
        user_id=current_user.id,
        itinerary_id=itinerary_id,
        status='pending'
    )
    db.session.add(rsvp)
    
    # Auto-create booking
    itinerary = Itinerary.query.get(itinerary_id)
    if itinerary:
        booking = Booking(
            user_id=current_user.id,
            title=itinerary.title,
            amount=1250.00,
            status='pending'
        )
        db.session.add(booking)
    
    db.session.commit()
    flash('✅ You have successfully joined this activity! Please complete payment on the Bookings page.', 'success')
    return redirect(url_for('user.bookings'))

# ====================== STRIPE PAYMENT ======================
@user_bp.route('/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session():
    try:
        data = request.get_json()
        booking_id = data.get('booking_id')

        booking = Booking.query.filter_by(id=booking_id, user_id=current_user.id).first()
        if not booking or booking.status != 'pending':
            return jsonify({'error': 'Invalid or already paid booking'}), 400

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': booking.title,
                    },
                    'unit_amount': int(booking.amount * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=url_for('user.payment_success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('user.bookings', _external=True),
            metadata={'booking_id': str(booking.id)}
        )

        return jsonify({'url': session.url})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/payment-success')
@login_required
def payment_success():
    flash('🎉 Payment successful! Your booking is now confirmed.', 'success')
    return redirect(url_for('user.bookings'))

# ====================== REVIEW ======================
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
        flash('Please write a meaningful review (minimum 10 characters).', 'danger')
    
    return redirect(url_for('user.reviews'))

# ====================== WEATHER API (Simple fallback) ======================
@user_bp.route('/api/weather')
def weather():
    city = request.args.get('city', 'Accra')
    return jsonify({
        "city": city,
        "temp": 28,
        "description": "Sunny",
        "icon": "☀️"
    })