import time


def test_create_link_with_auto_generated_code(client):
    response = client.post(
        "/links",
        json={"original_url": "https://example.com/some/very/long/path"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["original_url"] == "https://example.com/some/very/long/path"
    assert len(data["code"]) == 6
    assert data["short_url"].endswith(f"/{data['code']}")
    assert data["is_active"] is True


def test_create_link_with_custom_code(client):
    response = client.post(
        "/links",
        json={
            "original_url": "https://example.com",
            "custom_code": "my-code_123",
        },
    )

    assert response.status_code == 201
    assert response.json()["code"] == "my-code_123"


def test_create_link_with_duplicate_custom_code_returns_conflict(client):
    payload = {
        "original_url": "https://example.com/1",
        "custom_code": "taken-code",
    }
    client.post("/links", json=payload)

    response = client.post(
        "/links",
        json={
            "original_url": "https://example.com/2",
            "custom_code": "taken-code",
        },
    )

    assert response.status_code == 409
    data = response.json()
    assert data["error"]["code"] == "custom_code_already_exists"


def test_invalid_url_returns_validation_error(client):
    response = client.post(
        "/links",
        json={"original_url": "not-a-valid-url"},
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_redirect_increments_click_counter(client):
    create_response = client.post(
        "/links",
        json={"original_url": "https://example.com/docs"},
    )
    code = create_response.json()["code"]

    response = client.get(f"/{code}", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "https://example.com/docs"

    stats_response = client.get(f"/links/{code}")
    assert stats_response.status_code == 200
    assert stats_response.json()["clicks"] == 1


def test_redirect_for_missing_code_returns_404(client):
    response = client.get("/unknown-code", follow_redirects=False)

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "link_not_found"


def test_redirect_for_expired_code_returns_410(client):
    create_response = client.post(
        "/links",
        json={
            "original_url": "https://example.com/ttl",
            "expires_in_seconds": 1,
        },
    )
    code = create_response.json()["code"]

    time.sleep(1.1)
    response = client.get(f"/{code}", follow_redirects=False)

    assert response.status_code == 410
    assert response.json()["error"]["code"] == "link_expired"


def test_delete_deactivates_link(client):
    create_response = client.post(
        "/links",
        json={"original_url": "https://example.com/delete-me"},
    )
    code = create_response.json()["code"]

    delete_response = client.delete(f"/links/{code}")
    assert delete_response.status_code == 200
    assert delete_response.json()["is_active"] is False

    redirect_response = client.get(f"/{code}", follow_redirects=False)
    assert redirect_response.status_code == 410
    assert redirect_response.json()["error"]["code"] == "link_inactive"


def test_list_links_returns_created_links(client):
    client.post("/links", json={"original_url": "https://example.com/1"})
    client.post("/links", json={"original_url": "https://example.com/2"})

    response = client.get("/links")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert {item["original_url"] for item in data} == {
        "https://example.com/1",
        "https://example.com/2",
    }
