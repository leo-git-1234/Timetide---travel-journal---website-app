from app.models import SessionLocal
from app.models.database import User, Trip, Entry
from datetime import datetime, timedelta, date

db = SessionLocal()
user = db.query(User).first()

if user:
    # Create test trips with different dates for testing
    trips_data = [
        {
            "title": "Paris Spring Trip",
            "description": "A beautiful spring break in Paris",
            "start_date": date(2025, 4, 15),
            "end_date": date(2025, 4, 22),
            "location": "Paris, France",
            "cover_image": "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='400' height='300'%3E%3Crect fill='%236E8C78' width='400' height='300'/%3E%3C/svg%3E"
        },
        {
            "title": "Tokyo Adventure",
            "description": "Amazing food and culture in Tokyo",
            "start_date": date(2024, 11, 1),
            "end_date": date(2024, 11, 14),
            "location": "Tokyo, Japan",
            "cover_image": "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='400' height='300'%3E%3Crect fill='%238B6B47' width='400' height='300'/%3E%3C/svg%3E"
        },
        {
            "title": "New York City",
            "description": "Classic NYC experience",
            "start_date": date(2024, 9, 10),
            "end_date": date(2024, 9, 17),
            "location": "New York, USA",
            "cover_image": "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='400' height='300'%3E%3Crect fill='%234A5B70' width='400' height='300'/%3E%3C/svg%3E"
        },
        {
            "title": "Barcelona Beach",
            "description": "Summer on the Mediterranean",
            "start_date": date(2023, 7, 20),
            "end_date": date(2023, 7, 27),
            "location": "Barcelona, Spain",
            "cover_image": "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='400' height='300'%3E%3Crect fill='%23C49A6C' width='400' height='300'/%3E%3C/svg%3E"
        },
        {
            "title": "London Winter",
            "description": "Holiday season in London",
            "start_date": date(2023, 12, 15),
            "end_date": date(2023, 12, 22),
            "location": "London, UK",
            "cover_image": "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='400' height='300'%3E%3Crect fill='%235C5C5C' width='400' height='300'/%3E%3C/svg%3E"
        },
        {
            "title": "Sydney Opera",
            "description": "Visiting the iconic Sydney Opera House",
            "start_date": date(2022, 6, 10),
            "end_date": date(2022, 6, 18),
            "location": "Sydney, Australia",
            "cover_image": "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='400' height='300'%3E%3Crect fill='%238FA39B' width='400' height='300'/%3E%3C/svg%3E"
        }
    ]
    
    for trip_data in trips_data:
        trip = Trip(
            title=trip_data["title"],
            description=trip_data["description"],
            start_date=trip_data["start_date"],
            end_date=trip_data["end_date"],
            location=trip_data["location"],
            cover_image=trip_data["cover_image"],
            owner_id=user.id
        )
        db.add(trip)
        db.commit()
        print(f"Created trip: {trip.title} (ID: {trip.id})")
        
        # Add a sample entry to each trip
        entry = Entry(
            content="This was a wonderful experience.",
            trip_id=trip.id,
            author_id=user.id,
            entry_date=trip.start_date
        )
        db.add(entry)
    
    db.commit()
    print(f"\nAdded {len(trips_data)} trips with entries!")
else:
    print("No user found")
