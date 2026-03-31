# routes/user.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from models import db, Itinerary, Booking, Review, ActivityRSVP
import stripe
import os
from utils.email import send_confirmation_email
from utils.qr import generate_qr

user_bp = Blueprint('user', __name__)

# Initialize Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

# -------------------- DASHBOARD & PAGES -------------------- #
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

# -------------------- ACTIVITY RSVP -------------------- #
# In routes/user.py - Replace the accept_activity function with this:

@user_bp.route('/accept-activity/<int:itinerary_id>', methods=['POST'])
@login_required
def accept_activity(itinerary_id):
    # Check if user already accepted this activity
    existing = ActivityRSVP.query.filter_by(
        user_id=current_user.id, 
        itinerary_id=itinerary_id
    ).first()
    
    if existing:
        flash('You have already joined this activity.', 'info')
        return redirect(url_for('user.bookings'))

    # Create the RSVP record
    rsvp = ActivityRSVP(
        user_id=current_user.id,
        itinerary_id=itinerary_id,
        status='pending'
    )
    db.session.add(rsvp)
    
    # Automatically create a booking when user accepts the activity
    itinerary = Itinerary.query.get(itinerary_id)
    if itinerary:
        booking = Booking(
            user_id=current_user.id,
            title=itinerary.title,
            amount=1250.00,           # You can change this amount later
            status='pending'
        )
        db.session.add(booking)
    
    db.session.commit()
    
    flash('✅ Activity accepted! Please complete your booking on the next page.', 'success')
    return redirect(url_for('user.bookings'))

@user_bp.route('/activities/confirmed')
@login_required
def confirmed_activities():
    rsvps = ActivityRSVP.query.filter_by(
        user_id=current_user.id, status='approved'
    ).order_by(ActivityRSVP.created_at.desc()).all()
    return render_template('user/confirmed_activities.html', rsvps=rsvps)

@user_bp.route('/activities/cancel/<int:rsvp_id>')
@login_required
def cancel_rsvp(rsvp_id):
    rsvp = ActivityRSVP.query.get_or_404(rsvp_id)
    if rsvp.user_id != current_user.id:
        flash("You cannot cancel this RSVP.", "danger")
        return redirect(url_for('user.confirmed_activities'))

    rsvp.status = 'pending'  # or 'canceled' if you add a canceled state
    db.session.commit()
    flash(f"Your RSVP for '{rsvp.itinerary.title}' has been canceled.", "success")
    return redirect(url_for('user.confirmed_activities'))

# -------------------- STRIPE PAYMENT -------------------- #
@user_bp.route('/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session():
    try:
        data = request.get_json()
        booking_id = data.get('booking_id')

        booking = Booking.query.filter_by(id=booking_id, user_id=current_user.id).first()
        if not booking or booking.status != 'pending':
            return jsonify({'error': 'Invalid booking'}), 400

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': booking.title,
                        'description': 'Jetsetta Luxury Travel Booking',
                    },
                    'unit_amount': int(booking.amount * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=url_for('user.payment_success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('user.bookings', _external=True),
            metadata={'booking_id': booking.id, 'user_id': current_user.id}
        )

        return jsonify({'id': session.id})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/payment-success')
@login_required
def payment_success():
    session_id = request.args.get('session_id')

    try:
        session = stripe.checkout.Session.retrieve(session_id)
        booking_id = session.metadata.get('booking_id')
        booking = Booking.query.get(booking_id)

        if booking:
            booking.status = 'confirmed'
            db.session.commit()

            # Generate QR code
            qr_path = generate_qr(f"booking_{booking.id}")

            # Send confirmation email
            send_confirmation_email(current_user.email, booking.title)

        flash('Payment successful! Your booking is now confirmed.', 'success')

    except Exception as e:
        print("Stripe Error:", e)
        flash('Payment verification failed.', 'danger')

    if session.payment_status != 'paid':
        flash('Payment not completed.', 'danger')
    return redirect(url_for('user.bookings'))

# -------------------- REVIEW SUBMISSION -------------------- #
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

# -------------------- SIMPLE CHATBOT -------------------- #
@user_bp.route('/chatbot', methods=['POST'])
def chatbot():
    user_message = request.json.get("message", "")

    # Simple AI responses
    if "flight" in user_message.lower():
        reply = "We offer flights worldwide 🌍✈️"
    elif "price" in user_message.lower():
        reply = "Prices vary depending on destination."
    elif "hotel" in user_message.lower():
        reply = "We partner with top hotels globally 🏨"
    else:
        reply = "How can I help you plan your trip?"

    return {"reply": reply}