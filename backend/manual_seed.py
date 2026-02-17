from app.database import SessionLocal, engine
from app.models import User
import traceback

try:
    print(f"Connecting to: {engine.url}")
    db = SessionLocal()
    print("Querying for admin user...")
    user = db.query(User).filter(User.username == "admin").first()
    if not user:
        print("Creating admin user...")
        admin_user = User(
            username="admin",
            email="admin@example.com",
            full_name="Admin User",
            password="password"
        )
        db.add(admin_user)
        db.commit()
        print("Admin user created.")
    else:
        print("Admin user already exists.")
    db.close()
except Exception:
    with open("error.log", "w") as f:
        traceback.print_exc(file=f)
    print("Error occurred. Check error.log")
