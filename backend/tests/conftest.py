"""Test configuration for the Legal Case Management API.

Uses mongomock to mock MongoDB collections so tests run
without a real database connection.
"""

import pytest
from unittest import mock
from fastapi.testclient import TestClient

# Patch pymongo with mongomock BEFORE importing app modules
import mongomock

mock_client = mongomock.MongoClient()
mock_db = mock_client["test_legal_db"]


def _mock_get_next_id(collection_name: str) -> int:
    """Auto-increment helper for the mocked database."""
    counter = mock_db["counters"].find_one_and_update(
        {"_id": collection_name},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=True,
    )
    return counter["seq"]


# Patch the database module's collections and helpers
_patches = [
    mock.patch("app.database.client", mock_client),
    mock.patch("app.database.db", mock_db),
    mock.patch("app.database.cases_collection", mock_db["cases"]),
    mock.patch("app.database.users_collection", mock_db["users"]),
    mock.patch("app.database.counters_collection", mock_db["counters"]),
    mock.patch("app.database.get_next_id", _mock_get_next_id),
]

for p in _patches:
    p.start()

from app.main import app  # noqa: E402 — must import after patches


@pytest.fixture(autouse=True)
def clean_db():
    """Drop all test collections before each test for isolation."""
    mock_db["cases"].delete_many({})
    mock_db["users"].delete_many({})
    mock_db["counters"].delete_many({})
    yield


@pytest.fixture()
def client():
    """Provide a FastAPI TestClient."""
    with TestClient(app) as c:
        yield c
