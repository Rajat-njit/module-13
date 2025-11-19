# tests/integration/test_user_auth.py

def test_register_user_success(client):
    payload = {
        "first_name": "Rajat",
        "last_name": "Test",
        "email": "rajat.test@example.com",
        "username": "rajat_test",
        "password": "StrongPass123!",
        "confirm_password": "StrongPass123!",
    }
    resp = client.post("/auth/register", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["username"] == "rajat_test"
    assert data["email"] == "rajat.test@example.com"
    assert "id" in data


def test_register_duplicate_fails(client, registered_user):
    resp = client.post("/auth/register", json=registered_user)
    assert resp.status_code == 400
    assert "exists" in resp.json()["detail"].lower()


def test_login_success(client, registered_user):
    payload = {
        "username": registered_user["username"],
        "password": registered_user["password"],
    }
    resp = client.post("/auth/login", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, registered_user):
    payload = {
        "username": registered_user["username"],
        "password": "WrongPassword123!",
    }
    resp = client.post("/auth/login", json=payload)
    assert resp.status_code == 401
