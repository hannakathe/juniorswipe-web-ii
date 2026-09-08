import time

import jwt as pyjwt


def test_register_success(client, register):
    r = register(client, "new@local.test")
    assert r.status_code == 201
    body = r.get_json()
    assert body["token"]
    assert body["user"]["email"] == "new@local.test"
    assert body["user"]["role"] == "developer"


def test_register_duplicate(client, register):
    register(client, "dup@local.test")
    r = register(client, "dup@local.test")
    assert r.status_code == 409
    assert r.get_json()["error"]["code"] == "email_taken"


def test_register_rejects_short_password(client):
    r = client.post("/api/auth/register", json={
        "email": "x@local.test", "password": "short", "full_name": "X"})
    assert r.status_code == 422


def test_login_success_returns_jwt(client):
    r = client.post("/api/auth/login",
                    json={"email": "dev@local.test", "password": "Password123!"})
    assert r.status_code == 200
    token = r.get_json()["token"]
    decoded = pyjwt.decode(token, "test-secret", algorithms=["HS256"])
    assert decoded["email"] == "dev@local.test"
    assert decoded["role"] == "developer"
    assert "exp" in decoded
    assert "password" not in decoded and "password_hash" not in decoded


def test_login_wrong_password(client):
    r = client.post("/api/auth/login",
                    json={"email": "dev@local.test", "password": "nope"})
    assert r.status_code == 401
    assert r.get_json()["error"]["code"] == "invalid_credentials"


def test_me_with_valid_token(client, dev_token):
    r = client.get("/api/auth/me", headers={"Authorization": f"Bearer {dev_token}"})
    assert r.status_code == 200
    assert r.get_json()["email"] == "dev@local.test"


def test_protected_without_token(client):
    r = client.get("/api/auth/me")
    assert r.status_code == 401
    assert r.get_json()["error"]["code"] == "token_missing"


def test_protected_with_invalid_token(client):
    r = client.get("/api/auth/me", headers={"Authorization": "Bearer not.a.jwt"})
    assert r.status_code == 401
    assert r.get_json()["error"]["code"] == "token_invalid"


def test_expired_token_rejected(client, app):
    with app.app_context():
        expired = pyjwt.encode(
            {"sub": "1", "exp": int(time.time()) - 10}, "test-secret", algorithm="HS256")
    r = client.get("/api/auth/me", headers={"Authorization": f"Bearer {expired}"})
    assert r.status_code == 401
    assert r.get_json()["error"]["code"] == "token_expired"


def test_token_for_deleted_user_rejected(client, app):
    with app.app_context():
        ghost = pyjwt.encode(
            {"sub": "999999", "exp": int(time.time()) + 60}, "test-secret",
            algorithm="HS256")
    r = client.get("/api/auth/me", headers={"Authorization": f"Bearer {ghost}"})
    assert r.status_code == 401
    assert r.get_json()["error"]["code"] == "user_not_found"
