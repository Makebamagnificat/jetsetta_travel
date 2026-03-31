from flask_mail import Message
from app import mail  
from flask import current_app

def send_confirmation_email(user_email, booking_title):
    msg = Message(
        subject="Booking Confirmation ✈️",
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=[user_email]
    )
    msg.body = f"Your booking for '{booking_title}' is confirmed. Thank you for choosing Jetsetta!"

    if qr_path:
        with open(qr_path, 'rb') as f:
            msg.attach(
                filename=f"{booking_title}_QR.png",
                content_type='image/png',
                data=f.read()
            )

    mail.send(msg)