# seed.py
from app import create_app, db
from models import User, Itinerary, Booking, ActivityRSVP, Review
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    print("🌍 Seeding Ghana Luxury Travel Experience with Real Coordinates...")

    # Delete dependent records first (important order)
    db.session.query(ActivityRSVP).delete()
    db.session.query(Booking).delete()
    db.session.query(Review).delete()
    db.session.query(Itinerary).delete()
    db.session.query(User).delete()
    db.session.commit()

    # Create Admin
    admin = User(
        name="Admin",
        email="admin@jetsetta.com",
        password=generate_password_hash("admin123"),
        role="admin"
    )
    db.session.add(admin)

    # Create Test User
    user = User(
        name="Mary Johnson",
        email="mary@jetsetta.com",
        password=generate_password_hash("password123"),
        role="user"
    )
    db.session.add(user)
    db.session.commit()

    # Ghana Luxury Itineraries with Real Coordinates (7th - 14th July 2026)
    itineraries_data = [
        {
        "day": "Day 1", 
        "title": "VIP Arrival in Accra",
        "description": "Private airport pickup and transfer to your luxury villa with welcome Ghanaian dinner.",
        "date_str": "2026-07-07",
        "latitude": 5.6052, 
        "longitude": -0.1668,
        "location_name": "Accra International Airport, Accra"
        },
        {
            "day": "Day 2", "title": "Accra Heritage Tour",
            "description": "Explore Jamestown, Kwame Nkrumah Mausoleum and vibrant local markets.",
            "date_str": "2026-07-08",
            "latitude":5.5400, "longitude": -0.2100,
            "location_name": "Jamestown, Accra"
        },
        {
            "day": "Day 3", "title": "Kakum National Park Canopy Walk",
            "description": "Experience the famous canopy walkway through the rainforest.",
            "date_str": "2026-07-09",
            "latitude": 5.3536, "longitude": -1.3833,
            "location_name": "Kakum National Park"
        },
        {
            "day": "Day 4", "title": "Cape Coast & Elmina Castle Tour",
            "description": "Visit UNESCO World Heritage castles with a private historian guide.",
            "date_str": "2026-07-10",
            "latitude": 5.1036, "longitude": -1.2410,
            "location_name": "Cape Coast Castle"
        },
        {
            "day": "Day 5", "title": "Lake Volta Cruise & Akosombo",
            "description": "Luxury boat cruise on the world's largest man-made lake with sunset dinner.",
            "date_str": "2026-07-11",
            "latitude": 6.3000, "longitude": 0.0500,
            "location_name": "Lake Volta, Akosombo"
        },
        {
            "day": "Day 6", "title": "Kumasi Ashanti Cultural Experience",
            "description": "Visit Manhyia Palace and enjoy traditional Ashanti drumming and dance.",
            "date_str": "2026-07-12",
            "latitude": 6.6885, "longitude": -1.6244,
            "location_name": "Manhyia Palace, Kumasi"
        },
        {
            "day": "Day 7", "title": "Aburi Botanical Gardens & Mountain Retreat",
            "description": "Relax at the beautiful Aburi Botanical Gardens with stunning mountain views.",
            "date_str": "2026-07-13",
            "latitude": 5.8500, "longitude": -0.1800,
            "location_name": "Aburi Botanical Gardens"
        },
        {
            "day": "Day 8", "title": "Spa Day and Departure",
            "description": "Relax at the spa and luxury escort to the airport for departure.",
            "date_str": "2026-07-14",
            "latitude": 5.6052, "longitude": -0.1668,
            "location_name": "Kotoka International Airport, Accra"
        }
    ]    

    for data in itineraries_data:
        itinerary = Itinerary(**data)
        db.session.add(itinerary)

    db.session.commit()

    # Sample pending booking for testing Pay Now
    sample_booking = Booking(
        user_id=user.id,
        title="Kakum National Park Canopy Walk",
        amount=154.140,
        status="pending"
    )
    db.session.add(sample_booking)
    db.session.commit()

    print("✅ Admin: admin@jetsetta.com / admin123")
    print("✅ User: mary@jetsetta.com / password123")
    print(f"✅ {len(itineraries_data)} Itineraries added with real GPS coordinates")
    print("✅ Sample pending booking created")

    print("🌟 Seeding completed successfully!")