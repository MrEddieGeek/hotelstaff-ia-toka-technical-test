from __future__ import annotations


def test_register_login_refresh_me_flow(client) -> None:
    # Register
    r = client.post(
        "/auth/register",
        json={"email": "ada@example.com", "password": "contrasena-super-segura"},
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["email"] == "ada@example.com"
    assert body["is_active"] is True

    # Login
    r = client.post(
        "/auth/login",
        json={"email": "ada@example.com", "password": "contrasena-super-segura"},
    )
    assert r.status_code == 200
    tokens = r.json()
    assert tokens["token_type"] == "bearer"
    assert tokens["expires_in"] > 0
    access = tokens["access_token"]
    refresh = tokens["refresh_token"]

    # /me with access token
    r = client.get("/auth/me", headers={"Authorization": f"Bearer {access}"})
    assert r.status_code == 200
    me = r.json()
    assert me["roles"] == []
    assert me["sub"]

    # /me with refresh token should be rejected
    r = client.get("/auth/me", headers={"Authorization": f"Bearer {refresh}"})
    assert r.status_code == 401

    # Refresh
    r = client.post("/auth/refresh", json={"refresh_token": refresh})
    assert r.status_code == 200
    assert r.json()["access_token"]


def test_register_duplicate_email_returns_409(client) -> None:
    payload = {"email": "dup@example.com", "password": "contrasena-super-segura"}
    assert client.post("/auth/register", json=payload).status_code == 201
    r = client.post("/auth/register", json=payload)
    assert r.status_code == 409


def test_login_invalid_credentials_returns_401(client) -> None:
    client.post(
        "/auth/register",
        json={"email": "x@example.com", "password": "contrasena-super-segura"},
    )
    r = client.post(
        "/auth/login",
        json={"email": "x@example.com", "password": "contrasena-mala"},
    )
    assert r.status_code == 401


def test_oauth2_password_grant(client) -> None:
    client.post(
        "/auth/register",
        json={"email": "oauth@example.com", "password": "contrasena-super-segura"},
    )
    r = client.post(
        "/auth/token",
        data={"username": "oauth@example.com", "password": "contrasena-super-segura"},
    )
    assert r.status_code == 200
    assert r.json()["access_token"]


def test_jwks_exposes_public_key(client) -> None:
    r = client.get("/.well-known/jwks.json")
    assert r.status_code == 200
    jwks = r.json()
    assert "keys" in jwks and len(jwks["keys"]) == 1
    k = jwks["keys"][0]
    assert k["kty"] == "RSA"
    assert k["alg"] == "RS256"
    assert k["use"] == "sig"
    assert k["n"] and k["e"]


def test_refresh_with_invalid_token_returns_401(client) -> None:
    r = client.post("/auth/refresh", json={"refresh_token": "no-es-un-jwt"})
    assert r.status_code == 401
