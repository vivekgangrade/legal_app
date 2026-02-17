from fastapi import FastAPI
from app.routers import cases, users
from app.utils.logger import logger
from app.database import engine, Base

# Create Tables with Retry
import time
from sqlalchemy.exc import OperationalError

MAX_RETRIES = 10
RETRY_DELAY = 3 # seconds

for i in range(MAX_RETRIES):
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully.")
        break
    except OperationalError as e:
        if i == MAX_RETRIES - 1:
            logger.error(f"Could not connect to database after {MAX_RETRIES} attempts: {e}")
            raise e
        logger.warning(f"Database not ready, retrying in {RETRY_DELAY}s... ({i+1}/{MAX_RETRIES})")
        time.sleep(RETRY_DELAY)

from sqlalchemy.orm import Session
from app.models import User
from app.database import SessionLocal

def seed_db():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == "admin").first()
        if not user:
            admin_user = User(
                username="admin",
                email="admin@example.com",
                full_name="Admin User",
                password="password" # In production, hash this!
            )
            db.add(admin_user)
            db.commit()
            logger.info("Created default admin user")
    except Exception as e:
        logger.error(f"Error seeding DB: {e}")
    finally:
        db.close()

seed_db()

app = FastAPI(
    title="Legal Case Management API",
    description="API for managing legal cases and users.",
    version="1.0.0",
)

# Add CORS Middleware
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cases.router)
app.include_router(users.router)

@app.get("/health", tags=["Health"])
async def health_check():
    logger.info("Health check endpoint called")
    return {"status": "healthy"}

@app.get("/", tags=["Root"])
async def root():
    return {"message": "Welcome to the Legal Case Management API"}
