from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routers import cases, users
from app.utils.logger import logger
from app.utils.auth import hash_password
from app.database import users_collection, get_next_id
from fastapi.middleware.cors import CORSMiddleware


def seed_db():
    """Create default admin user if it doesn't exist."""
    try:
        user = users_collection.find_one({"username": "admin"})
        if not user:
            user_doc = {
                "id": get_next_id("users"),
                "username": "admin",
                "email": "admin@example.com",
                "full_name": "Admin User",
                "password": hash_password("password"),
                "is_active": True,
            }
            users_collection.insert_one(user_doc)
            logger.info("Created default admin user")
        else:
            logger.info("Admin user already exists")
    except Exception as e:
        logger.error(f"Error seeding DB: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Seed default data
    logger.info("Starting up...")
    seed_db()
    logger.info("MongoDB connected and seeded successfully.")
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
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
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
