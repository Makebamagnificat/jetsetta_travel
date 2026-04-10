# routes/user.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from models import db, Itinerary, Booking, Review, ActivityRSVP
import requests
import os
import uuid

user_bp = Blueprint('user', __name__)

# -------------------- PAYSTACK CONFIG --------------------
PAYSTACK_SECRET_KEY = os.getenv('PAYSTACK_SECRET_KEY')
PAYSTACK_PUBLIC_KEY = os.getenv('PAYSTACK_PUBLIC_KEY')

if not PAYSTACK_SECRET_KEY:
    print("⚠️  WARNING: PAYSTACK_SECRET_KEY is missing from .env")

# -------------------- PAGES -------------------- #
@user_bp.route('/')
def index():
    return render_template('index.html')


@user_bp.route('/dashboard')
@login_required
def dashboard():
    itineraries = Itinerary.query.all()
    
    if current_user.role == 'admin':
        bookings = Booking.query.all()
    else:
        bookings = Booking.query.filter_by(user_id=current_user.id).all()

    return render_template(
        'dashboard.html',
        itineraries=itineraries,
        bookings=bookings,
        user=current_user
    )


@user_bp.route('/itineraries')
@login_required
def itineraries():
    itineraries = Itinerary.query.all()
    bookings = Booking.query.filter_by(user_id=current_user.id).all()   # for AI chat
    
    return render_template('itineraries.html', 
                           itineraries=itineraries,
                           bookings=bookings)


@user_bp.route('/bookings')
@login_required
def bookings():
    bookings = Booking.query.filter_by(user_id=current_user.id).all()
    itineraries = Itinerary.query.all()   # for AI chat
    
    return render_template('bookings.html', 
                           bookings=bookings,
                           itineraries=itineraries,
                           user=current_user)


@user_bp.route('/reviews')
@login_required
def reviews():
    reviews = Review.query.filter_by(user_id=current_user.id).all()
    return render_template('reviews.html', reviews=reviews)


@user_bp.route('/accept-activity/<int:itinerary_id>', methods=['POST'])
@login_required
def accept_activity(itinerary_id):
    itinerary = Itinerary.query.get_or_404(itinerary_id)
    
    # Daily rate after $300 deposit
    DAILY_USD = 242.86
    
    booking = Booking(
        user_id=current_user.id,
        title=itinerary.title,
        amount=DAILY_USD,           # ← Daily amount only
        status='pending'
    )
    db.session.add(booking)
    db.session.commit()
    
    flash(f'You joined {itinerary.title} – Daily payment: ${DAILY_USD}', 'success')
    return redirect(url_for('user.bookings'))


# -------------------- PAYSTACK PAYMENT -------------------- #
@user_bp.route('/create-paystack-session', methods=['POST'])
@login_required
def create_paystack_session():
    try:
        data = request.get_json()
        booking_id = data.get('booking_id')
        
        if not booking_id:
            return jsonify({'error': 'No booking ID received'}), 400

        booking = Booking.query.get_or_404(booking_id)
        
        if booking.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized booking'}), 403

        amount_kobo = int(booking.amount * 100)

        payload = {
            "email": current_user.email,
            "amount": amount_kobo,
            "currency": "GHS",
            "metadata": {
                "booking_id": booking.id,
                "user_id": current_user.id
            },
            "callback_url": url_for('user.payment_success', _external=True)
        }

        headers = {
            "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json"
        }

        response = requests.post(
            "https://api.paystack.co/transaction/initialize",
            json=payload,
            headers=headers,
            timeout=15
        )

        result = response.json()

        if result.get('status') is True:
            return jsonify({'url': result['data']['authorization_url']})
        else:
            error_msg = result.get('message', 'Unknown Paystack error')
            return jsonify({'error': error_msg}), 400

    except Exception as e:
        print(f"💥 Paystack error: {str(e)}")
        return jsonify({'error': str(e)}), 500


# -------------------- PAYMENT SUCCESS -------------------- #
@user_bp.route('/payment-success')
@login_required
def payment_success():
    reference = request.args.get('reference')
    if not reference:
        flash('Payment failed - no reference received', 'danger')
        return redirect(url_for('user.bookings'))

    try:
        headers = {
            "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json"
        }
        resp = requests.get(
            f"https://api.paystack.co/transaction/verify/{reference}",
            headers=headers
        )
        data = resp.json()

        if data.get('status') is True and data['data']['status'] == 'success':
            booking_id = data['data']['metadata'].get('booking_id')
            if booking_id:
                booking = Booking.query.get(booking_id)
                if booking:
                    booking.status = 'confirmed'
                    db.session.commit()
                    flash('✅ Payment successful! Your booking is now confirmed.', 'success')
                else:
                    flash('Booking not found', 'danger')
            return redirect(url_for('user.bookings'))
        else:
            flash('Payment verification failed', 'danger')
    except Exception as e:
        print("Paystack verify error:", str(e))
        flash('Error verifying payment', 'danger')

    return redirect(url_for('user.bookings'))


# -------------------- REVIEW SUBMISSION -------------------- #
@user_bp.route('/submit-review', methods=['POST'])
@login_required
def submit_review():
    text = request.form.get('text')
    if text and len(text.strip()) > 10:
        review = Review(user_id=current_user.id, text=text.strip(), stars=5)
        db.session.add(review)
        db.session.commit()
        flash('Thank you! Your review has been posted.', 'success')
    else:
        flash('Please write a meaningful review.', 'danger')
    return redirect(url_for('user.reviews'))


# -------------------- PAYSTACK CHECKOUT PAGE -------------------- #
@user_bp.route('/checkout/<int:booking_id>')
@login_required
def checkout(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    
    if booking.user_id != current_user.id:
        flash('Unauthorized', 'danger')
        return redirect(url_for('user.bookings'))

    if booking.status != 'pending':
        flash('This booking is already paid or confirmed', 'warning')
        return redirect(url_for('user.bookings'))

    reference = f"jetsetta-{booking.id}-{uuid.uuid4().hex[:8]}"

    return render_template('checkout.html', 
                           booking=booking,
                           reference=reference,
                           paystack_public_key=os.getenv('PAYSTACK_PUBLIC_KEY'))


# ====================== WEATHER ======================
@user_bp.route('/api/weather')
def weather():
    city = request.args.get('city', 'Accra')
    return jsonify({
        "city": city,
        "temp": 28,
        "description": "Sunny",
        "icon": "☀️"
    })


# -------------------- VIEW ON MAP -------------------- #
@user_bp.route('/view_map/<int:itinerary_id>')
@login_required
def view_map(itinerary_id):
    itinerary = Itinerary.query.get_or_404(itinerary_id)
    return render_template('map.html', itinerary=itinerary)