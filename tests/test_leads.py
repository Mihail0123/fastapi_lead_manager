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


def test_create_lead_strips_whitespace(client: TestClient):
    payload = {
        "name": "   Bob Stone   ",
        "email": "bob@example.com",
        "company": "   Stone Ltd   ",
        "source": "   manual   ",
    }

    response = client.post("/leads", json=payload)

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Bob Stone"
    assert data["company"] == "Stone Ltd"
    assert data["source"] == "manual"

def test_get_leads_returns_created_leads(client: TestClient):
    payload = {
        "name": "Alice Cooper",
        "email": "alice@example.com",
        "company": "Music Ltd",
        "source": "website",
    }

    create_response = client.post("/leads", json=payload)
    list_response = client.get("/leads")

    assert create_response.status_code == 201
    assert list_response.status_code == 200

    data = list_response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Alice Cooper"
    assert data[0]["email"] == "alice@example.com"
    assert data[0]["company"] == "Music Ltd"
    assert data[0]["source"] == "website"
    assert data[0]["status"] == "new"

