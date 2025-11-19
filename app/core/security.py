# app/core/security.py

from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

from jose import jwt, JWTError
from passlib.context import CryptContext

from app.core.config import settings

# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ---------------------- PASSWORD HASHING ----------------------

def get_password_hash(password: str) -> str:
    """Hash a plaintext password."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against the stored hash."""
    return pwd_context.verify(plain_password, hashed_password)


# ---------------------- JWT CREATION ----------------------

def create_access_token(data: Dict[str, Any], expires_minutes: int = 30) -> str:
    """
    Create a JWT access token.
    - data should contain {"sub": user_id}
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


# ---------------------- JWT DECODING ----------------------

def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode a JWT and return the payload.
    Raises JWTError if token is invalid or expired.
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        return payload
    except JWTError:
        raise
