from __future__ import annotations


def _payload(email="ana@example.com", full_name="Ana López", position="Recepcionista"):
    return {
        "email": email,
        "full_name": full_name,
        "position": position,
        "department": "Front Desk",
    }


def test_create_and_get_user_emits_event(client) -> None:
    app = client.app
    publisher = app.state.publisher

    r = client.post("/users", json=_payload())
    assert r.status_code == 201
    user = r.json()
    assert user["email"] == "ana@example.com"

    r = client.get(f"/users/{user['id']}")
    assert r.status_code == 200
    assert r.json()["full_name"] == "Ana López"

    events = publisher.published
    assert any(e.event_type == "user.created" for e in events)


def test_duplicate_email_returns_409(client) -> None:
    client.post("/users", json=_payload())
    r = client.post("/users", json=_payload())
    assert r.status_code == 409


def test_list_users_pagination(client) -> None:
    for i in range(3):
        client.post("/users", json=_payload(email=f"u{i}@example.com", full_name=f"Usuario {i}"))
    r = client.get("/users?limit=2&offset=0")
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 3
    assert len(body["items"]) == 2


def test_update_user_emits_event(client) -> None:
    app = client.app
    r = client.post("/users", json=_payload())
    uid = r.json()["id"]

    r = client.patch(f"/users/{uid}", json={"position": "Supervisor", "is_active": False})
    assert r.status_code == 200
    updated = r.json()
    assert updated["position"] == "Supervisor"
    assert updated["is_active"] is False

    events = app.state.publisher.published
    assert any(e.event_type == "user.updated" for e in events)


def test_delete_user_emits_event(client) -> None:
    app = client.app
    r = client.post("/users", json=_payload())
    uid = r.json()["id"]

    r = client.delete(f"/users/{uid}")
    assert r.status_code == 204

    assert client.get(f"/users/{uid}").status_code == 404
    assert any(e.event_type == "user.deleted" for e in app.state.publisher.published)


def test_get_unknown_user_returns_404(client) -> None:
    r = client.get("/users/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404
