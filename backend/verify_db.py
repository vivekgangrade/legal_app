from app.database import SessionLocal
from app.models import User
from app.utils.logger import logger

def verify_users():
    db = SessionLocal()
    try:
        print("Checking users in database...")
        users = db.query(User).all()
        print(f"Found {len(users)} users.")
        for user in users:
            print(f"User: {user.username}, Email: {user.email}")
        
        if not any(u.username == "admin" for u in users):
            print("Admin user NOT found. Attempting to create...")
            admin_user = User(
                username="admin",
                email="admin@example.com",
                full_name="Admin User",
                password="password"
            )
            db.add(admin_user)
            db.commit()
            print("Admin user created successfully.")
        else:
            print("Admin user exists.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    verify_users()
