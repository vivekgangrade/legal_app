"""Tests for the /cases endpoints."""


def test_create_case(client):
    response = client.post(
        "/cases/",
        json={"title": "Test Case", "client_name": "John Doe", "status": "open"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Case"
    assert data["client_name"] == "John Doe"
    assert data["status"] == "open"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_create_case_validation_error(client):
    """Title must be at least 3 characters."""
    response = client.post(
        "/cases/",
        json={"title": "Ab", "client_name": "Jane"},
    )
    assert response.status_code == 422


def test_read_cases(client):
    response = client.get("/cases/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_read_case_by_id(client):
    create_resp = client.post(
        "/cases/",
        json={"title": "Lookup Case", "client_name": "Jane Doe"},
    )
    case_id = create_resp.json()["id"]

    response = client.get(f"/cases/{case_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Lookup Case"


def test_read_case_not_found(client):
    response = client.get("/cases/999999")
    assert response.status_code == 404


def test_update_case(client):
    create_resp = client.post(
        "/cases/",
        json={"title": "Old Title", "client_name": "Update User"},
    )
    case_id = create_resp.json()["id"]

    response = client.put(f"/cases/{case_id}", json={"title": "New Title"})
    assert response.status_code == 200
    assert response.json()["title"] == "New Title"


def test_delete_case(client):
    create_resp = client.post(
        "/cases/",
        json={"title": "To Delete", "client_name": "Delete User"},
    )
    case_id = create_resp.json()["id"]

    response = client.delete(f"/cases/{case_id}")
    assert response.status_code == 204

    # Verify it's gone
    get_response = client.get(f"/cases/{case_id}")
    assert get_response.status_code == 404


def test_delete_case_not_found(client):
    response = client.delete("/cases/999999")
    assert response.status_code == 404
