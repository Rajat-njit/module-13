# app/routers/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse,
    TokenResponse,
    TokenResponseWithMessage
)
from app.core.security import create_access_token

router = APIRouter()


# -------------------------------------------------------
# REGISTER
# -------------------------------------------------------
@router.post("/register", status_code=201)
def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    try:
        payload = user_data.model_dump(exclude={"confirm_password"})
        user = User.register(db, payload)
        db.commit()
        db.refresh(user)
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

    # Token for frontend
    token = create_access_token({"sub": str(user.id)})

    # Pytest expects the full user object
    user_response = UserResponse.model_validate(user)

    # Return both (pytest ignores extra fields)
    return {
        **user_response.model_dump(),
        "message": "User registered successfully!",
        "access_token": token,
        "token_type": "bearer"
    }


# -------------------------------------------------------
# LOGIN
# -------------------------------------------------------
@router.post("/login", response_model=TokenResponseWithMessage)
def login_user(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Login using username OR email.
    Returns token + success message (Module 13).
    """
    identifier = login_data.get_identifier()

    auth = User.authenticate(
        db,
        identifier,
        login_data.password
)

    if not auth:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    user = auth["user"]
    token = auth["access_token"]

    db.commit()

    return TokenResponseWithMessage(
        message="Login successful!",
        access_token=token,
        token_type="bearer"
    )
