from __future__ import annotations

from uuid import uuid4


def _create_role(client, name="recepcion", permissions=None):
    return client.post(
        "/roles",
        json={
            "name": name,
            "description": f"Rol {name}",
            "permissions": permissions or ["users.read"],
        },
    )


def test_create_and_list_roles(client) -> None:
    r = _create_role(client)
    assert r.status_code == 201
    assert r.json()["name"] == "recepcion"

    r = client.get("/roles")
    assert r.status_code == 200
    assert len(r.json()) == 1


def test_duplicate_role_returns_409(client) -> None:
    _create_role(client)
    assert _create_role(client).status_code == 409


def test_assign_and_revoke_emits_events(client) -> None:
    app = client.app
    role = _create_role(client).json()
    user_id = str(uuid4())

    r = client.post("/assignments", json={"user_id": user_id, "role_id": role["id"]})
    assert r.status_code == 201
    assert r.json()["role_name"] == "recepcion"

    assert any(e.event_type == "role.assigned" for e in app.state.publisher.published)

    assignments = client.get(f"/users/{user_id}/roles").json()
    assert len(assignments) == 1

    r = client.delete(f"/assignments?user_id={user_id}&role_id={role['id']}")
    assert r.status_code == 204
    assert any(e.event_type == "role.revoked" for e in app.state.publisher.published)


def test_assign_unknown_role_returns_404(client) -> None:
    r = client.post(
        "/assignments",
        json={"user_id": str(uuid4()), "role_id": str(uuid4())},
    )
    assert r.status_code == 404


def test_duplicate_assignment_returns_409(client) -> None:
    role = _create_role(client).json()
    user_id = str(uuid4())
    payload = {"user_id": user_id, "role_id": role["id"]}
    assert client.post("/assignments", json=payload).status_code == 201
    assert client.post("/assignments", json=payload).status_code == 409
