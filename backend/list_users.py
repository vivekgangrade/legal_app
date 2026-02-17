from app.database import SessionLocal
from app.models import User

db = SessionLocal()
try:
    users = db.query(User).all()
    print(f"Total Users: {len(users)}")
    for user in users:
        print(f"User: {user.username}, Password: {user.password}")
except Exception as e:
    print(f"Error: {e}")
finally:
    db.close()
