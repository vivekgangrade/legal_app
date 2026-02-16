from fastapi import FastAPI
from app.routers import cases, users
from app.utils.logger import logger

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
