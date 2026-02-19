from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routers import cases, users
from app.utils.logger import logger
from app.database import engine, Base, SessionLocal
from app.models import User
import time
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

MAX_RETRIES = 10
RETRY_DELAY = 3 # seconds

def create_tables():
    for i in range(MAX_RETRIES):
        try:
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables created successfully.")
            return
        except OperationalError as e:
            if i == MAX_RETRIES - 1:
                logger.error(f"Could not connect to database after {MAX_RETRIES} attempts: {e}")
                raise e
            logger.warning(f"Database not ready, retrying in {RETRY_DELAY}s... ({i+1}/{MAX_RETRIES})")
            time.sleep(RETRY_DELAY)

def seed_db():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == "admin").first()
        if not user:
            # TODO: In production, use a proper password hashing library like passlib
            # context.verify(password, hashed_password)
            admin_user = User(
                username="admin",
                email="admin@example.com",
                full_name="Admin User",
                password="password" 
            )
            db.add(admin_user)
            db.commit()
            logger.info("Created default admin user")
        else:
            logger.info("Admin user already exists")
    except Exception as e:
        logger.error(f"Error seeding DB: {e}")
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables and seed DB
    logger.info("Starting up...")
    create_tables()
    seed_db()
    yield
    # Shutdown
    logger.info("Shutting down...")

app = FastAPI(
    title="Legal Case Management API",
    description="API for managing legal cases and users.",
    version="1.0.0",
    lifespan=lifespan
)

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
