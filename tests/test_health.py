def test_live_health_endpoint_returns_ok(client):
    response = client.get("/health/live")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_legacy_health_endpoint_still_returns_ok(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_ready_health_endpoint_checks_database(client):
    response = client.get("/health/ready")

    assert response.status_code == 200
    assert response.get_json()["checks"]["database"] == {"ok": True}
