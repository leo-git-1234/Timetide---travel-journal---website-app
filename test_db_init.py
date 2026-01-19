from app.models import init_db
try:
    init_db()
    print("Database initialized successfully")
except Exception as e:
    print(f"Error initializing database: {e}")
    import traceback
    traceback.print_exc()
