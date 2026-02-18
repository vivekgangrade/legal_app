from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db

# Setup in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def setup_module(module):
    # Create tables
    Base.metadata.create_all(bind=engine)

def teardown_module(module):
    # Drop tables
    Base.metadata.drop_all(bind=engine)

def test_create_case():
    response = client.post(
        "/cases/",
        json={"title": "Test Case", "client_name": "John Doe", "status": "open"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Case"
    assert "id" in data
    assert data["status"] == "open"

def test_read_cases():
    response = client.get("/cases/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_read_case_by_id():
    # Create a case first
    create_response = client.post(
        "/cases/",
        json={"title": "Lookup Case", "client_name": "Jane Doe"}
    )
    case_id = create_response.json()["id"]

    response = client.get(f"/cases/{case_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Lookup Case"

def test_update_case():
    # Create a case first
    create_response = client.post(
        "/cases/",
        json={"title": "Old Title", "client_name": "Update User"}
    )
    case_id = create_response.json()["id"]

    response = client.put(
        f"/cases/{case_id}",
        json={"title": "New Title"}
    )
    assert response.status_code == 200
    assert response.json()["title"] == "New Title"

def test_delete_case():
    # Create a case first
    create_response = client.post(
        "/cases/",
        json={"title": "To Delete", "client_name": "Delete User"}
    )
    case_id = create_response.json()["id"]

    response = client.delete(f"/cases/{case_id}")
    assert response.status_code == 204

    # Verify it's gone
    get_response = client.get(f"/cases/{case_id}")
    assert get_response.status_code == 404
