# tests/integration/test_calculation_routes.py
#
# Integration tests for the /calculations endpoints.
# These are written to match the current implementation:
# - POST   /calculations        -> create calculation (factory-based)
# - GET    /calculations        -> list calculations for current user
# - GET    /calculations/{id}   -> get single calculation
# - PUT    /calculations/{id}   -> update inputs & recompute result
# - DELETE /calculations/{id}   -> delete calculation
#
# Fixtures `client` and `auth_headers` are provided by tests/conftest.py.

def test_create_calculation_success(client, auth_headers):
    payload = {"type": "addition", "inputs": [10, 5, 3]}

    resp = client.post("/calculations", json=payload, headers=auth_headers)
    assert resp.status_code == 201

    data = resp.json()
    # Basic shape checks
    assert "id" in data
    assert "user_id" in data
    assert data["type"] == "addition"
    assert data["inputs"] == [10, 5, 3]
    # 10 + 5 + 3 = 18
    assert data["result"] == 18.0


def test_list_calculations(client, auth_headers):
    # Seed at least two calculations for the current user
    client.post(
        "/calculations",
        json={"type": "addition", "inputs": [1, 2]},
        headers=auth_headers,
    )
    client.post(
        "/calculations",
        json={"type": "multiplication", "inputs": [2, 3]},
        headers=auth_headers,
    )

    resp = client.get("/calculations", headers=auth_headers)
    assert resp.status_code == 200

    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 2

    # All rows should belong to the *same* authenticated user
    user_ids = {item["user_id"] for item in data}
    assert len(user_ids) == 1


def test_get_update_delete_calculation_full_flow(client, auth_headers):
    # ---------- CREATE ----------
    create_payload = {"type": "multiplication", "inputs": [2, 3, 4]}
    resp_create = client.post(
        "/calculations",
        json=create_payload,
        headers=auth_headers,
    )
    assert resp_create.status_code == 201
    created = resp_create.json()

    calc_id = created["id"]
    # 2 * 3 * 4 = 24
    assert created["result"] == 24.0

    # ---------- READ (GET by ID) ----------
    resp_get = client.get(f"/calculations/{calc_id}", headers=auth_headers)
    assert resp_get.status_code == 200
    fetched = resp_get.json()
    assert fetched["id"] == calc_id
    assert fetched["type"] == "multiplication"
    assert fetched["result"] == 24.0

    # ---------- UPDATE ----------
    update_payload = {"inputs": [3, 5]}  # still multiplication (3 * 5 = 15)
    resp_update = client.put(
        f"/calculations/{calc_id}",
        json=update_payload,
        headers=auth_headers,
    )
    assert resp_update.status_code == 200
    updated = resp_update.json()

    assert updated["id"] == calc_id
    assert updated["inputs"] == [3, 5]
    assert updated["result"] == 15.0

    # ---------- DELETE ----------
    resp_delete = client.delete(f"/calculations/{calc_id}", headers=auth_headers)
    assert resp_delete.status_code == 204

    # After deletion, GET by id must return 404
    resp_get_again = client.get(f"/calculations/{calc_id}", headers=auth_headers)
    assert resp_get_again.status_code == 404
