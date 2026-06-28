from fastapi.testclient import TestClient


def test_create_lead(client: TestClient):
    payload = {
        "name": "John Smith",
        "email": "john@example.com",
        "company": "Acme Inc",
        "source": "website",
    }

    response = client.post("/leads", json=payload)

    assert response.status_code == 201

    data = response.json()

    assert data["id"] == 1
    assert data["name"] == "John Smith"
    assert data["email"] == "john@example.com"
    assert data["company"] == "Acme Inc"
    assert data["source"] == "website"
    assert data["status"] == "new"
    assert "created_at" in data
    assert "updated_at" in data


def test_create_lead_duplicate_email_returns_400(client: TestClient):
    payload = {
        "name": "John Smith",
        "email": "john@example.com",
        "company": "Acme Inc",
        "source": "website",
    }

    first_response = client.post("/leads", json=payload)
    second_response = client.post("/leads", json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 400
    assert second_response.json() == {
        "detail": "Lead with email john@example.com already exists"
    }


def test_create_lead_with_empty_fields_returns_422(client: TestClient):
    payload = {
        "name": "",
        "email": "test@example.com",
        "company": "",
        "source": "",
    }

    response = client.post("/leads", json=payload)

    assert response.status_code == 422
