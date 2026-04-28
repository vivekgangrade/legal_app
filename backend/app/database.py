from pymongo import MongoClient
import os

# Get MongoDB URL from environment or fallback to localhost
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "legal_db")

client = MongoClient(MONGO_URL)
db = client[DB_NAME]

# Collections
cases_collection = db["cases"]
users_collection = db["users"]

# Counter collection for auto-incrementing IDs
counters_collection = db["counters"]


def get_next_id(collection_name: str) -> int:
    """Get next auto-incrementing integer ID for a collection."""
    counter = counters_collection.find_one_and_update(
        {"_id": collection_name},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=True
    )
    return counter["seq"]


def get_db():
    """Dependency that returns the database instance."""
    return db
