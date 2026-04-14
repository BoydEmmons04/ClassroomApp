def test_index_returns_counts_and_recent_problems(client):
    response = client.get("/")
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["status"] == "running"
    assert payload["counts"] == {
        "users": 0,
        "courses": 0,
        "problems": 0,
        "launches": 0,
        "submissions": 0,
    }
    assert payload["recent_problems"] == []


def test_request_id_header_is_preserved(client):
    response = client.get("/health/live", headers={"X-Request-ID": "test-request-id"})

    assert response.headers["X-Request-ID"] == "test-request-id"
