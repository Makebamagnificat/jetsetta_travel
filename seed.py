# seed.py - Fixed & Enhanced Ghana Luxury Tour

from app import create_app
from models import db, User, Itinerary, Booking
from werkzeug.security import generate_password_hash
from datetime import datetime

app = create_app()

with app.app_context():
    db.create_all()
    print("🌍 Seeding Ghana Luxury Travel Experience...")

    # ==================== CREATE USERS ====================
    
    # Admin User
    admin = User.query.filter_by(email="admin@jetsetta.com").first()
    if not admin:
        admin = User(
            name="Jetsetta Admin",
            email="admin@jetsetta.com",
            password=generate_password_hash("admin123"),
            role="admin"
        )
        db.session.add(admin)
        print("✅ Admin created: admin@jetsetta.com / admin123")

    # Mary Johnson (Main Test User)
    mary = User.query.filter_by(email="mary@jetsetta.com").first()
    if not mary:
        mary = User(
            name="Mary Johnson",
            email="mary@jetsetta.com",
            password=generate_password_hash("password123"),
            role="user"
        )
        db.session.add(mary)
        print("✅ User created: mary@jetsetta.com / password123")

    # Kwame Mensah (Second User)
    kwame = User.query.filter_by(email="kwame@jetsetta.com").first()
    if not kwame:
        kwame = User(
            name="Kwame Mensah",
            email="kwame@jetsetta.com",
            password=generate_password_hash("password123"),
            role="user"
        )
        db.session.add(kwame)

    # Commit users first
    db.session.commit()

    # Refresh objects to get IDs
    mary = User.query.filter_by(email="mary@jetsetta.com").first()

    # ==================== ITINERARIES (Ghana Luxury) ====================
    if Itinerary.query.count() == 0:
        ghana_itineraries = [
            {"day": "Day 1", "date_str": "15 Jun 2026", "title": "VIP Arrival in Accra", 
             "description": "Private pickup from Kotoka International Airport to your luxury villa/airbnb with welcome Ghanaian cocktail.", 
             "location_lat": 5.6037, "location_lng": -0.1870},

            {"day": "Day 2", "date_str": "16 Jun 2026", "title": "Accra City Heritage Tour", 
             "description": "Private guided tour of Kwame Nkrumah Mausoleum, Independence Square and Makola Market. Lunch with Jollof Rice.", 
             "location_lat": 5.5557, "location_lng": -0.1963},

            {"day": "Day 3", "date_str": "17 Jun 2026", "title": "Cape Coast & Elmina Castle", 
             "description": "Luxury drive to the historic castles (UNESCO). Private historian guide with oceanside lunch.", 
             "location_lat": 5.1030, "location_lng": -1.2460},

            {"day": "Day 4", "date_str": "18 Jun 2026", "title": "Kakum National Park Canopy Walk", 
             "description": "Exclusive canopy walkway experience with naturalist guide and Ghanaian breakfast picnic.", 
             "location_lat": 5.3500, "location_lng": -1.3830},

            {"day": "Day 5", "date_str": "19 Jun 2026", "title": "Lake Volta Luxury Cruise", 
             "description": "Private boat cruise on Lake Volta with stop at Dodi Island. Grilled tilapia and banku lunch.", 
             "location_lat": 6.3000, "location_lng": 0.0500},

            {"day": "Day 6", "date_str": "20 Jun 2026", "title": "Ashanti Kingdom Cultural Experience", 
             "description": "Visit to Manhyia Palace and Kente weaving village with traditional Adowa dance.", 
             "location_lat": 6.6885, "location_lng": -1.6244},

            {"day": "Day 7", "date_str": "21 Jun 2026", "title": "Ghanaian Cuisine Masterclass", 
             "description": "Private cooking class with a top chef. Learn to prepare Jollof, Fufu with light soup, and Kelewele.", 
             "location_lat": 5.6037, "location_lng": -0.1870},
        ]

        for data in ghana_itineraries:
            activity = Itinerary(**data)
            db.session.add(activity)
        
        print("✅ 7 Ghana luxury itinerary activities added")

    # ==================== SAMPLE BOOKING ====================
    if mary and Booking.query.count() == 0:
        booking = Booking(
            user_id=mary.id,
            title="7-Day Ghana Luxury Heritage & Culinary Journey",
            amount=8950.00,
            status="pending"
        )
        db.session.add(booking)
        print("✅ Sample booking created for Mary")

    db.session.commit()
    print("\n🎉 Seed data completed successfully!")
    print("You can now login with:")
    print("   Admin : admin@jetsetta.com / admin123")
    print("   User  : mary@jetsetta.com / password123")