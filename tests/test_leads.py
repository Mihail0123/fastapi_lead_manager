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


def test_get_lead_by_id(client: TestClient):
    payload = {
        "name": "Charlie Brown",
        "email": "charlie@example.com",
        "company": "Peanuts Inc",
        "source": "referral",
    }

    create_response = client.post("/leads", json=payload)

    assert create_response.status_code == 201

    created_lead = create_response.json()
    lead_id = created_lead["id"]

    detail_response = client.get(f"/leads/{lead_id}")

    assert detail_response.status_code == 200

    data = detail_response.json()

    assert data["id"] == lead_id
    assert data["name"] == "Charlie Brown"
    assert data["email"] == "charlie@example.com"
    assert data["company"] == "Peanuts Inc"
    assert data["source"] == "referral"
    assert data["status"] == "new"


def test_get_lead_by_unknown_id_returns_404(client: TestClient):
    response = client.get("/leads/999")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Lead with id 999 doesn't exist"
    }


def test_update_lead_status(client: TestClient):
    payload = {
        "name": "Diana Prince",
        "email": "diana@example.com",
        "company": "Amazon Corp",
        "source": "website",
    }

    create_response = client.post("/leads", json=payload)

    assert create_response.status_code == 201

    lead_id = create_response.json()["id"]

    update_response = client.patch(
        f"/leads/{lead_id}",
        json={"status": "qualified"},
    )

    assert update_response.status_code == 200

    data = update_response.json()

    assert data["id"] == lead_id
    assert data["status"] == "qualified"
    assert data["name"] == "Diana Prince"
    assert data["email"] == "diana@example.com"


def test_update_lead_with_invalid_status_returns_422(client: TestClient):
    payload = {
        "name": "Edward Nygma",
        "email": "edward@example.com",
        "company": "Puzzle Ltd",
        "source": "manual",
    }

    create_response = client.post("/leads", json=payload)

    assert create_response.status_code == 201

    lead_id = create_response.json()["id"]

    update_response = client.patch(
        f"/leads/{lead_id}",
        json={"status": "banana"},
    )

    assert update_response.status_code == 422


def test_delete_lead(client: TestClient):
    payload = {
        "name": "Frank Castle",
        "email": "frank@example.com",
        "company": "Punisher Ltd",
        "source": "manual",
    }

    create_response = client.post("/leads", json=payload)

    assert create_response.status_code == 201

    lead_id = create_response.json()["id"]

    delete_response = client.delete(f"/leads/{lead_id}")

    assert delete_response.status_code == 200
    assert delete_response.json() == {
        "message": f"Lead with id {lead_id} deleted successfully"
    }

    get_response = client.get(f"/leads/{lead_id}")

    assert get_response.status_code == 404


def test_count_leads(client: TestClient):
    first_payload = {
        "name": "Grace Hopper",
        "email": "grace@example.com",
        "company": "Navy",
        "source": "website",
    }

    second_payload = {
        "name": "Alan Turing",
        "email": "alan@example.com",
        "company": "Bletchley Park",
        "source": "referral",
    }

    empty_count_response = client.get("/leads/count")

    assert empty_count_response.status_code == 200
    assert empty_count_response.json() == {"count": 0}

    first_create_response = client.post("/leads", json=first_payload)
    second_create_response = client.post("/leads", json=second_payload)

    assert first_create_response.status_code == 201
    assert second_create_response.status_code == 201

    count_response = client.get("/leads/count")

    assert count_response.status_code == 200
    assert count_response.json() == {"count": 2}


def test_get_leads_filters_by_status(client: TestClient):
    first_payload = {
        "name": "New Lead",
        "email": "new@example.com",
        "company": "New Corp",
        "source": "website",
    }

    second_payload = {
        "name": "Qualified Lead",
        "email": "qualified@example.com",
        "company": "Qualified Corp",
        "source": "manual",
    }

    first_response = client.post("/leads", json=first_payload)
    second_response = client.post("/leads", json=second_payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 201

    second_lead_id = second_response.json()["id"]

    update_response = client.patch(
        f"/leads/{second_lead_id}",
        json={"status": "qualified"},
    )

    assert update_response.status_code == 200

    filtered_response = client.get("/leads?status=qualified")

    assert filtered_response.status_code == 200

    data = filtered_response.json()

    assert len(data) == 1
    assert data[0]["email"] == "qualified@example.com"
    assert data[0]["status"] == "qualified"


def test_get_leads_filters_by_source(client: TestClient):
    website_payload = {
        "name": "Website Lead",
        "email": "website@example.com",
        "company": "Web Corp",
        "source": "website",
    }

    manual_payload = {
        "name": "Manual Lead",
        "email": "manual@example.com",
        "company": "Manual Corp",
        "source": "manual",
    }

    website_response = client.post("/leads", json=website_payload)
    manual_response = client.post("/leads", json=manual_payload)

    assert website_response.status_code == 201
    assert manual_response.status_code == 201

    filtered_response = client.get("/leads?source=manual")

    assert filtered_response.status_code == 200

    data = filtered_response.json()

    assert len(data) == 1
    assert data[0]["email"] == "manual@example.com"
    assert data[0]["source"] == "manual"


def test_get_leads_searches_by_name_email_and_company(client: TestClient):
    first_payload = {
        "name": "Searchable Person",
        "email": "searchable@example.com",
        "company": "Acme Search Corp",
        "source": "website",
    }

    second_payload = {
        "name": "Another Person",
        "email": "another@example.com",
        "company": "Different Corp",
        "source": "manual",
    }

    first_response = client.post("/leads", json=first_payload)
    second_response = client.post("/leads", json=second_payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 201

    name_search_response = client.get("/leads?search=searchable")
    email_search_response = client.get("/leads?search=searchable@example.com")
    company_search_response = client.get("/leads?search=acme")
    empty_search_response = client.get("/leads?search=notfound")

    assert name_search_response.status_code == 200
    assert email_search_response.status_code == 200
    assert company_search_response.status_code == 200
    assert empty_search_response.status_code == 200

    assert len(name_search_response.json()) == 1
    assert len(email_search_response.json()) == 1
    assert len(company_search_response.json()) == 1
    assert empty_search_response.json() == []

    assert name_search_response.json()[0]["email"] == "searchable@example.com"
    assert email_search_response.json()[0]["email"] == "searchable@example.com"
    assert company_search_response.json()[0]["email"] == "searchable@example.com"


def test_get_leads_pagination(client: TestClient):
    first_payload = {
        "name": "First Lead",
        "email": "first@example.com",
        "company": "First Corp",
        "source": "website",
    }

    second_payload = {
        "name": "Second Lead",
        "email": "second@example.com",
        "company": "Second Corp",
        "source": "manual",
    }

    third_payload = {
        "name": "Third Lead",
        "email": "third@example.com",
        "company": "Third Corp",
        "source": "referral",
    }

    first_response = client.post("/leads", json=first_payload)
    second_response = client.post("/leads", json=second_payload)
    third_response = client.post("/leads", json=third_payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 201
    assert third_response.status_code == 201

    response = client.get("/leads?skip=1&limit=1")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["email"] == "second@example.com"


def test_get_leads_invalid_pagination_returns_422(client: TestClient):
    negative_skip_response = client.get("/leads?skip=-1")
    zero_limit_response = client.get("/leads?limit=0")
    too_large_limit_response = client.get("/leads?limit=101")

    assert negative_skip_response.status_code == 422
    assert zero_limit_response.status_code == 422
    assert too_large_limit_response.status_code == 422


def test_get_lead_with_invalid_id_returns_422(client: TestClient):
    response = client.get("/leads/0")

    assert response.status_code == 422


def test_update_unknown_lead_returns_404(client: TestClient):
    response = client.patch(
        "/leads/999",
        json={"status": "qualified"},
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Lead with id 999 doesn't exist"
    }
