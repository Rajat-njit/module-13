# tests/unit/test_user_model.py

from app.models.user import User


def test_password_hash_and_verify():
    raw = "StrongPass123!"
    hashed = User.hash_password(raw)
    assert hashed != raw

    u = User(
        username="unituser",
        email="unit@example.com",
        first_name="Unit",
        last_name="Test",
        password=hashed,
    )
    assert u.verify_password(raw)
    assert not u.verify_password("WrongPass!")

