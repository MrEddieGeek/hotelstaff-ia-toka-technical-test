from __future__ import annotations


def test_health_live(client) -> None:
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_ready(client) -> None:
    response = client.get("/health/ready")
    assert response.status_code == 200


def test_correlation_id_propagated(client) -> None:
    response = client.get("/health/live", headers={"X-Request-ID": "abc-123"})
    assert response.headers["X-Request-ID"] == "abc-123"
