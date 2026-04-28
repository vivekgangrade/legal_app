# MongoDB is schemaless - we don't need SQLAlchemy models.
# All schema validation is handled by Pydantic models in schemas.py.
# This file is kept for reference of the document structure.

"""
MongoDB Document Structures:

users collection:
{
    "id": int (auto-increment),
    "username": str,
    "email": str,
    "full_name": str | None,
    "password": str,
    "is_active": bool (default True)
}

cases collection:
{
    "id": int (auto-increment),
    "title": str,
    "description": str | None,
    "client_name": str,
    "status": "open" | "closed" | "pending",
    "created_at": datetime,
    "updated_at": datetime
}

counters collection (for auto-increment IDs):
{
    "_id": str (collection name),
    "seq": int
}
"""
