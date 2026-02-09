from app.models import SessionLocal
from app.models.database import User, Trip

db = SessionLocal()
user = db.query(User).first()
if user:
    print(f"User: {user.email}")
    trips = db.query(Trip).filter(Trip.owner_id == user.id).all()
    print(f"Total trips: {len(trips)}")
    for t in trips:
        print(f"  Trip {t.id}: {t.title} ({t.start_date})")
else:
    print("No users found")
