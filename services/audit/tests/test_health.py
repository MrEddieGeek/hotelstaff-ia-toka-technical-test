from __future__ import annotations


def test_health_live(client) -> None:
    assert client.get("/health/live").status_code == 200


def test_health_ready(client) -> None:
    assert client.get("/health/ready").status_code == 200


def test_correlation_id_propagated(client) -> None:
    r = client.get("/health/live", headers={"X-Request-ID": "abc-123"})
    assert r.headers["X-Request-ID"] == "abc-123"
