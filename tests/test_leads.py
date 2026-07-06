from fastapi.testclient import TestClient


def create_lead(
        client: TestClient,
        name: str = "Test Lead",
        email: str = "test@example.com",
        phone: str | None = None,
        company: str | None = "Test Company",
        source: str = "website",
):
    payload = {
        "name": name,
        "email": email,
        "source": source,
    }

    if phone is not None:
        payload["phone"] = phone

    if company is not None:
        payload["company"] = company

    response = client.post("/leads", json=payload)

    assert response.status_code == 201

    return response.json()


def test_create_lead(client: TestClient):
    data = create_lead(
        client,
        name="John Smith",
        email="john@example.com",
        company="Acme Inc",
        source="website",
    )

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


def test_create_lead_without_company_sets_company_to_none(client: TestClient):
    data = create_lead(
        client,
        name="No Company Lead",
        email="nocompany@example.com",
        company=None,
        source="website",
    )

    assert data["name"] == "No Company Lead"
    assert data["email"] == "nocompany@example.com"
    assert data["company"] is None
    assert data["source"] == "website"
    assert data["status"] == "new"


def test_create_lead_with_whitespace_only_fields_returns_422(client: TestClient):
    payload = {
        "name": "   ",
        "email": "spaces@example.com",
        "company": "   ",
        "source": "   ",
    }

    response = client.post("/leads", json=payload)

    assert response.status_code == 422


def test_get_leads_returns_created_leads(client: TestClient):
    create_lead(
        client,
        name="Alice Cooper",
        email="alice@example.com",
        company="Music Ltd",
        source="website",
    )

    response = client.get("/leads")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Alice Cooper"
    assert data[0]["email"] == "alice@example.com"
    assert data[0]["company"] == "Music Ltd"
    assert data[0]["source"] == "website"
    assert data[0]["status"] == "new"


def test_get_lead_by_id(client: TestClient):
    created_lead = create_lead(
        client,
        name="Charlie Brown",
        email="charlie@example.com",
        company="Peanuts Inc",
        source="referral",
    )

    lead_id = created_lead["id"]

    response = client.get(f"/leads/{lead_id}")

    assert response.status_code == 200

    data = response.json()

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


def test_get_lead_with_invalid_id_returns_422(client: TestClient):
    response = client.get("/leads/0")

    assert response.status_code == 422


def test_update_lead_status(client: TestClient):
    created_lead = create_lead(
        client,
        name="Diana Prince",
        email="diana@example.com",
        company="Amazon Corp",
        source="website",
    )

    lead_id = created_lead["id"]

    response = client.patch(
        f"/leads/{lead_id}",
        json={"status": "qualified"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == lead_id
    assert data["status"] == "qualified"
    assert data["name"] == "Diana Prince"
    assert data["email"] == "diana@example.com"


def test_update_lead_with_invalid_status_returns_422(client: TestClient):
    created_lead = create_lead(
        client,
        name="Edward Nygma",
        email="edward@example.com",
        company="Puzzle Ltd",
        source="manual",
    )

    lead_id = created_lead["id"]

    response = client.patch(
        f"/leads/{lead_id}",
        json={"status": "banana"},
    )

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


def test_update_lead_with_invalid_id_returns_422(client: TestClient):
    response = client.patch(
        "/leads/0",
        json={"status": "qualified"},
    )

    assert response.status_code == 422


def test_delete_lead(client: TestClient):
    created_lead = create_lead(
        client,
        name="Frank Castle",
        email="frank@example.com",
        company="Punisher Ltd",
        source="manual",
    )

    lead_id = created_lead["id"]

    delete_response = client.delete(f"/leads/{lead_id}")

    assert delete_response.status_code == 200
    assert delete_response.json() == {
        "message": f"Lead with id {lead_id} deleted successfully"
    }

    get_response = client.get(f"/leads/{lead_id}")

    assert get_response.status_code == 404


def test_delete_unknown_lead_returns_404(client: TestClient):
    response = client.delete("/leads/999")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Lead with id 999 doesn't exist"
    }


def test_delete_lead_with_invalid_id_returns_422(client: TestClient):
    response = client.delete("/leads/0")

    assert response.status_code == 422


def test_count_leads(client: TestClient):
    empty_count_response = client.get("/leads/count")

    assert empty_count_response.status_code == 200
    assert empty_count_response.json() == {"count": 0}

    create_lead(
        client,
        name="Grace Hopper",
        email="grace@example.com",
        company="Navy",
        source="website",
    )
    create_lead(
        client,
        name="Alan Turing",
        email="alan@example.com",
        company="Bletchley Park",
        source="referral",
    )

    count_response = client.get("/leads/count")

    assert count_response.status_code == 200
    assert count_response.json() == {"count": 2}


def test_count_leads_filters_by_status(client: TestClient):
    create_lead(
        client,
        name="New Count Lead",
        email="new-count@example.com",
        company="New Count Corp",
        source="website",
    )
    qualified_lead = create_lead(
        client,
        name="Qualified Count Lead",
        email="qualified-count@example.com",
        company="Qualified Count Corp",
        source="manual",
    )

    update_response = client.patch(
        f"/leads/{qualified_lead['id']}",
        json={"status": "qualified"},
    )

    assert update_response.status_code == 200

    count_response = client.get("/leads/count?status=qualified")

    assert count_response.status_code == 200
    assert count_response.json() == {"count": 1}


def test_count_leads_filters_by_source(client: TestClient):
    create_lead(
        client,
        name="Website Count Lead",
        email="website-count@example.com",
        company="Website Count Corp",
        source="website",
    )
    create_lead(
        client,
        name="Manual Count Lead",
        email="manual-count@example.com",
        company="Manual Count Corp",
        source="manual",
    )

    count_response = client.get("/leads/count?source=manual")

    assert count_response.status_code == 200
    assert count_response.json() == {"count": 1}


def test_count_leads_filters_by_search(client: TestClient):
    create_lead(
        client,
        name="Search Count Lead",
        email="search-count@example.com",
        company="Count Search Corp",
        source="website",
    )
    create_lead(
        client,
        name="Other Count Lead",
        email="other-count@example.com",
        company="Other Corp",
        source="manual",
    )

    count_response = client.get("/leads/count?search=count search")
    empty_count_response = client.get("/leads/count?search=notfound")

    assert count_response.status_code == 200
    assert empty_count_response.status_code == 200

    assert count_response.json() == {"count": 1}
    assert empty_count_response.json() == {"count": 0}


def test_count_leads_empty_search_returns_422(client: TestClient):
    response = client.get("/leads/count?search=")

    assert response.status_code == 422


def test_get_leads_filters_by_status(client: TestClient):
    create_lead(
        client,
        name="New Lead",
        email="new@example.com",
        company="New Corp",
        source="website",
    )
    qualified_lead = create_lead(
        client,
        name="Qualified Lead",
        email="qualified@example.com",
        company="Qualified Corp",
        source="manual",
    )

    update_response = client.patch(
        f"/leads/{qualified_lead['id']}",
        json={"status": "qualified"},
    )

    assert update_response.status_code == 200

    response = client.get("/leads?status=qualified")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["email"] == "qualified@example.com"
    assert data[0]["status"] == "qualified"


def test_get_leads_filters_by_source(client: TestClient):
    create_lead(
        client,
        name="Website Lead",
        email="website@example.com",
        company="Web Corp",
        source="website",
    )
    create_lead(
        client,
        name="Manual Lead",
        email="manual@example.com",
        company="Manual Corp",
        source="manual",
    )

    response = client.get("/leads?source=manual")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["email"] == "manual@example.com"
    assert data[0]["source"] == "manual"


def test_get_leads_searches_by_name_email_and_company(client: TestClient):
    create_lead(
        client,
        name="Searchable Person",
        email="searchable@example.com",
        company="Acme Search Corp",
        source="website",
    )
    create_lead(
        client,
        name="Another Person",
        email="another@example.com",
        company="Different Corp",
        source="manual",
    )

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


def test_get_leads_invalid_status_filter_returns_422(client: TestClient):
    response = client.get("/leads?status=banana")

    assert response.status_code == 422


def test_get_leads_empty_search_returns_422(client: TestClient):
    response = client.get("/leads?search=")

    assert response.status_code == 422


def test_get_leads_pagination(client: TestClient):
    create_lead(
        client,
        name="First Lead",
        email="first@example.com",
        company="First Corp",
        source="website",
    )
    create_lead(
        client,
        name="Second Lead",
        email="second@example.com",
        company="Second Corp",
        source="manual",
    )
    create_lead(
        client,
        name="Third Lead",
        email="third@example.com",
        company="Third Corp",
        source="referral",
    )

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


def test_get_lead_status_stats(client: TestClient):
    first_lead = create_lead(
        client,
        name="First Stats Lead",
        email="first-stats@example.com",
        company="Stats Corp",
        source="website",
    )
    second_lead = create_lead(
        client,
        name="Second Stats Lead",
        email="second-stats@example.com",
        company="Stats Corp",
        source="manual",
    )
    contacted_lead = create_lead(
        client,
        name="Contacted Stats Lead",
        email="contacted-stats@example.com",
        company="Stats Corp",
        source="website",
    )
    qualified_lead = create_lead(
        client,
        name="Qualified Stats Lead",
        email="qualified-stats@example.com",
        company="Stats Corp",
        source="referral",
    )

    contacted_response = client.patch(
        f"/leads/{contacted_lead['id']}",
        json={"status": "contacted"},
    )
    qualified_response = client.patch(
        f"/leads/{qualified_lead['id']}",
        json={"status": "qualified"},
    )

    assert contacted_response.status_code == 200
    assert qualified_response.status_code == 200

    response = client.get("/leads/stats/status")

    assert response.status_code == 200
    assert response.json() == {
        "new": 2,
        "contacted": 1,
        "qualified": 1,
        "lost": 0,
    }


def test_get_lead_source_stats(client: TestClient):
    create_lead(
        client,
        name="Website Source Lead",
        email="website-source@example.com",
        company="Source Corp",
        source="website",
    )
    create_lead(
        client,
        name="Second Website Source Lead",
        email="second-website-source@example.com",
        company="Source Corp",
        source="website",
    )
    create_lead(
        client,
        name="Manual Source Lead",
        email="manual-source@example.com",
        company="Source Corp",
        source="manual",
    )
    create_lead(
        client,
        name="Referral Source Lead",
        email="referral-source@example.com",
        company="Source Corp",
        source="referral",
    )

    response = client.get("/leads/stats/source")

    assert response.status_code == 200
    assert response.json() == {
        "manual": 1,
        "referral": 1,
        "website": 2,
    }


def test_create_lead_with_phone(client: TestClient):
    data = create_lead(
        client,
        name="Phone Lead",
        email="phone@example.com",
        phone="+49123456789",
        company="Phone Corp",
        source="website",
    )

    assert data["phone"] == "+49123456789"


def test_create_lead_without_phone_sets_phone_to_none(client: TestClient):
    data = create_lead(
        client,
        name="No Phone Lead",
        email="no-phone@example.com",
        company="No Phone Corp",
        source="manual",
    )

    assert data["phone"] is None


def test_get_leads_searches_by_phone(client: TestClient):
    create_lead(
        client,
        name="Phone Search Lead",
        email="phone-search@example.com",
        phone="+34999111222",
        company="Phone Search Corp",
        source="website",
    )
    create_lead(
        client,
        name="Other Lead",
        email="other-phone-search@example.com",
        phone="+49111111111",
        company="Other Corp",
        source="manual",
    )

    response = client.get("/leads?search=999111")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["email"] == "phone-search@example.com"
    assert data[0]["phone"] == "+34999111222"


def test_get_leads_filters_by_company(client: TestClient):
    create_lead(
        client,
        name="Acme Lead",
        email="acme-company@example.com",
        company="Acme Inc",
        source="website",
    )
    create_lead(
        client,
        name="Other Company Lead",
        email="other-company@example.com",
        company="Other Inc",
        source="manual",
    )

    response = client.get("/leads?company=Acme Inc")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["email"] == "acme-company@example.com"
    assert data[0]["company"] == "Acme Inc"


def test_count_leads_filters_by_company(client: TestClient):
    create_lead(
        client,
        name="First Acme Count Lead",
        email="first-acme-count@example.com",
        company="Acme Inc",
        source="website",
    )
    create_lead(
        client,
        name="Second Acme Count Lead",
        email="second-acme-count@example.com",
        company="Acme Inc",
        source="manual",
    )
    create_lead(
        client,
        name="Other Count Lead",
        email="other-count-company@example.com",
        company="Other Inc",
        source="referral",
    )

    response = client.get("/leads/count?company=Acme Inc")

    assert response.status_code == 200
    assert response.json() == {"count": 2}


def test_get_leads_empty_company_filter_returns_422(client: TestClient):
    response = client.get("/leads?company=")

    assert response.status_code == 422


def test_count_leads_empty_company_filter_returns_422(client: TestClient):
    response = client.get("/leads/count?company=")

    assert response.status_code == 422


def test_get_leads_sorts_by_name_ascending(client: TestClient):
    create_lead(
        client,
        name="Charlie Lead",
        email="charlie-sort@example.com",
        company="Sort Corp",
        source="website",
    )
    create_lead(
        client,
        name="Alice Lead",
        email="alice-sort@example.com",
        company="Sort Corp",
        source="manual",
    )
    create_lead(
        client,
        name="Bob Lead",
        email="bob-sort@example.com",
        company="Sort Corp",
        source="referral",
    )

    response = client.get("/leads?sort_by=name&sort_order=asc")

    assert response.status_code == 200

    data = response.json()

    assert [lead["name"] for lead in data] == [
        "Alice Lead",
        "Bob Lead",
        "Charlie Lead",
    ]


def test_get_leads_sorts_by_name_descending(client: TestClient):
    create_lead(
        client,
        name="Charlie Lead",
        email="charlie-sort-desc@example.com",
        company="Sort Corp",
        source="website",
    )
    create_lead(
        client,
        name="Alice Lead",
        email="alice-sort-desc@example.com",
        company="Sort Corp",
        source="manual",
    )
    create_lead(
        client,
        name="Bob Lead",
        email="bob-sort-desc@example.com",
        company="Sort Corp",
        source="referral",
    )

    response = client.get("/leads?sort_by=name&sort_order=desc")

    assert response.status_code == 200

    data = response.json()

    assert [lead["name"] for lead in data] == [
        "Charlie Lead",
        "Bob Lead",
        "Alice Lead",
    ]


def test_get_leads_invalid_sort_by_returns_422(client: TestClient):
    response = client.get("/leads?sort_by=banana")

    assert response.status_code == 422


def test_get_leads_invalid_sort_order_returns_422(client: TestClient):
    response = client.get("/leads?sort_order=sideways")

    assert response.status_code == 422
