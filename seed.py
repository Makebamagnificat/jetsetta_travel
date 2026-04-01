# seed.py - Final Fixed Version
from app import create_app
from models import db, User, Itinerary, Booking
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    db.create_all()
    print("🌍 Database in use:", app.config['SQLALCHEMY_DATABASE_URI'])

    # Create Admin
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
    
    


    # ==================== GHANA LUXURY ITINERARY (10 Activities) ====================
    if Itinerary.query.count() == 0:
        ghana_itineraries = [
            {"day": "Day 1", "date_str": "15 Jun 2026", "title": "VIP Arrival in Accra", 
             "description": "Private airport pickup from Kotoka International Airport. Transfer to luxury villa in Airport Residential Area with welcome Ghanaian cocktail.", 
             "location_lat": 5.6037, "location_lng": -0.1870},

            {"day": "Day 2", "date_str": "16 Jun 2026", "title": "Accra Heritage & Food Tour", 
             "description": "Private tour of Kwame Nkrumah Mausoleum and Independence Square. Lunch featuring Jollof Rice, Waakye and fresh palm wine tasting.", 
             "location_lat": 5.5557, "location_lng": -0.1963},

            {"day": "Day 3", "date_str": "17 Jun 2026", "title": "Cape Coast & Elmina Castle", 
             "description": "Luxury drive to Cape Coast Castle and Elmina Castle (UNESCO). Private historian guide with afternoon high tea at a oceanside resort.", 
             "location_lat": 5.1030, "location_lng": -1.2460},

            {"day": "Day 4", "date_str": "18 Jun 2026", "title": "Kakum National Park Canopy Walk", 
             "description": "Early morning canopy walkway experience with expert naturalist. Breakfast picnic with Ghanaian pastries and fresh fruits.", 
             "location_lat": 5.3500, "location_lng": -1.3830},

            {"day": "Day 5", "date_str": "19 Jun 2026", "title": "Lake Volta Luxury Cruise", 
             "description": "Private yacht cruise on Lake Volta with Dodi Island stop. Ghanaian seafood lunch featuring grilled tilapia and banku.", 
             "location_lat": 6.3000, "location_lng": 0.0500},

            {"day": "Day 6", "date_str": "20 Jun 2026", "title": "Kumasi Ashanti Kingdom Experience", 
             "description": "Private visit to Manhyia Palace. Traditional Kente weaving demonstration and Adowa cultural dance performance.", 
             "location_lat": 6.6885, "location_lng": -1.6244},

            {"day": "Day 7", "date_str": "21 Jun 2026", "title": "Aburi Botanical Gardens & Mountains", 
             "description": "Relaxing day at Aburi Botanical Gardens with private picnic. Enjoy fresh coconut and local delicacies.", 
             "location_lat": 5.8500, "location_lng": -0.1833},

            {"day": "Day 8", "date_str": "22 Jun 2026", "title": "Ghanaian Cuisine Masterclass", 
             "description": "Private cooking class with a top Accra chef. Learn to prepare Jollof Rice, Fufu with light soup, and Kelewele.", 
             "location_lat": 5.6037, "location_lng": -0.1870},

            {"day": "Day 9", "date_str": "23 Jun 2026", "title": "Shopping & Souvenirs", 
             "description": "Private shopping tour at Art Centre and local craft villages. Curated selection of Kente cloth, beads and handicrafts.", 
             "location_lat": 5.5557, "location_lng": -0.1963},

            {"day": "Day 10", "date_str": "24 Jun 2026", "title": "Departure Day", 
             "description": "Morning spa session at villa followed by VIP airport transfer with farewell gifts.", 
             "location_lat": 5.6037, "location_lng": -0.1870},
        ]
        for data in ghana_itineraries:
            activity = Itinerary(**data)
            db.session.add(activity)

        print("✅ 10 Ghana luxury itinerary activities added (including cuisine masterclass)")

    db.session.commit()
    print("🎉 Enhanced Ghana seed data loaded successfully!")
    print("\nLogin Details:")
    print("Admin → admin@jetsetta.com / admin123")
    print("User  → mary@jetsetta.com / password123")