# app/schemas/user.py

from datetime import datetime
from uuid import UUID
from typing import Optional

from pydantic import (
    BaseModel, EmailStr, Field, ConfigDict, model_validator
)


# ------------------- BASE -------------------

class UserBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)

    model_config = ConfigDict(from_attributes=True)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)
    confirm_password: str = Field(..., min_length=8, max_length=128)

    @model_validator(mode="after")
    def passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError("Password and confirm_password do not match")
        return self


# ------------------- LOGIN -------------------

class UserLogin(BaseModel):
    """
    Module-13 style login:
    - Takes username OR email
    """
    username_or_email: str = Field(..., min_length=3)
    password: str = Field(..., min_length=8, max_length=128)


# ------------------- RESPONSE -------------------

class UserResponse(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    """
    Original Module-12 style response (tests still rely on this).
    """
    access_token: str
    token_type: str = "bearer"
    user_id: UUID
    username: str
    email: EmailStr


class TokenResponseWithMessage(BaseModel):
    """
    NEW frontend response for Module-13.
    """
    message: str
    access_token: str
    token_type: str = "bearer"
