# app/routers/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.schemas.token import TokenResponse

router = APIRouter()



# ---------------- REGISTER ----------------
@router.post("/register", response_model=UserResponse, status_code=201)
def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register new user:
    - Validates unique username/email
    - Hashes password
    - Returns UserResponse
    """
    try:
        cleaned = user_data.model_dump(exclude={"confirm_password"})
        user = User.register(db, cleaned)
        db.commit()
        db.refresh(user)
        return user
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


# ---------------- LOGIN (JSON) ----------------
@router.post("/login", response_model=TokenResponse)
def login_user(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Validate username/email + password and return JWT.
    """
    auth = User.authenticate(db, login_data.username, login_data.password)
    if not auth:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    user = auth["user"]
    access = auth["access_token"]

    db.commit()   # commit last_login update

    return TokenResponse(
        access_token=access,
        token_type="bearer",
        user_id=user.id,
        username=user.username,
        email=user.email
    )
