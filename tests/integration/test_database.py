# tests/integration/test_database.py

from sqlalchemy.orm import Session
from app.models.user import User
from app.database import Base
from tests.conftest import engine_test, TestingSessionLocal  # type: ignore
from sqlalchemy import inspect
from app.database import engine

def test_tables_exist():
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    assert "users" in tables
    assert "calculations" in tables


def test_can_insert_user():
    session: Session = TestingSessionLocal()
    try:
        user = User(
            username="dbtest",
            email="dbtest@example.com",
            first_name="DB",
            last_name="Test",
            password=User.hash_password("StrongPass123!"),
            is_active=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        fetched = session.query(User).filter_by(username="dbtest").first()
        assert fetched is not None
        assert fetched.email == "dbtest@example.com"
    finally:
        session.close()
