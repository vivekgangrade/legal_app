from datetime import datetime
from typing import List, Optional

# Mock Database
cases_db = []
users_db = [
    {
        "id": 1,
        "username": "admin",
        "password": "password",
        "email": "admin@example.com",
        "full_name": "Admin User"
    }
]

# Helper to find case by ID
def get_case_by_id(case_id: int):
    for case in cases_db:
        if case["id"] == case_id:
            return case
    return None

# Helper to find user by username
def get_user_by_username(username: str):
    for user in users_db:
        if user["username"] == username:
            return user
    return None
