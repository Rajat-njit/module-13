# tests/e2e/test_full_flow.py

def test_full_user_and_calculation_flow(client):
    # Register
    reg_payload = {
        "first_name": "E2E",
        "last_name": "User",
        "email": "e2e@example.com",
        "username": "e2euser",
        "password": "StrongPass123!",
        "confirm_password": "StrongPass123!",
    }
    r1 = client.post("/auth/register", json=reg_payload)
    assert r1.status_code in (201, 400)

    # Login
    login_payload = {
        "username": "e2euser",
        "password": "StrongPass123!",
    }
    r2 = client.post("/auth/login", json=login_payload)
    assert r2.status_code == 200
    token = r2.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create calculation
    calc_payload = {"type": "addition", "inputs": [5, 7]}
    r3 = client.post("/calculations", json=calc_payload, headers=headers)
    assert r3.status_code == 201
    assert r3.json()["result"] == 12.0
