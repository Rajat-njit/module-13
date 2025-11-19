# tests/conftest.py

import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

# Use a local SQLite DB just for tests
TEST_DATABASE_URL = "sqlite:///./test.db"

engine_test = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)


# ---------- DB OVERRIDE ----------

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


# ---------- GLOBAL FIXTURES ----------

@pytest.fixture(scope="session", autouse=True)
def create_test_database():
    """
    Create all tables in the SQLite test DB once per test session.
    Drops and recreates tables so tests are deterministic.
    """
    # Start fresh each time
    Base.metadata.drop_all(bind=engine_test)
    Base.metadata.create_all(bind=engine_test)
    yield
    # Optional: clean up afterwards
    Base.metadata.drop_all(bind=engine_test)


@pytest.fixture()
def client():
    """
    Provides a TestClient that uses the overridden DB.
    """
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def registered_user(client):
    """
    Registers a default user and returns its data.
    """
    payload = {
        "first_name": "Test",
        "last_name": "User",
        "email": "testuser@example.com",
        "username": "testuser",
        "password": "StrongPass123!",
        "confirm_password": "StrongPass123!",
    }
    resp = client.post("/auth/register", json=payload)
    assert resp.status_code in (201, 400)  # if tests re-use, 400 = already exists
    return payload


@pytest.fixture()
def auth_headers(client, registered_user):
    """
    Logs in and returns Authorization headers for protected routes.
    """
    login_payload = {
        "username": registered_user["username"],
        "password": registered_user["password"],
    }
    resp = client.post("/auth/login", json=login_payload)
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
