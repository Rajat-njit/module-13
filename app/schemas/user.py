# app/schemas/user.py

from datetime import datetime
from uuid import UUID
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict, model_validator


class UserBase(BaseModel):
    """Common fields shared by user read/create/update schemas."""
    first_name: str = Field(..., min_length=1, max_length=50, example="John")
    last_name: str = Field(..., min_length=1, max_length=50, example="Doe")
    email: EmailStr = Field(..., example="john.doe@example.com")
    username: str = Field(..., min_length=3, max_length=50, example="johndoe")

    model_config = ConfigDict(from_attributes=True)


class UserCreate(UserBase):
    """Schema used for user registration."""
    password: str = Field(..., min_length=8, max_length=128, example="StrongPass123!")
    confirm_password: str = Field(..., min_length=8, max_length=128, example="StrongPass123!")

    @model_validator(mode="after")
    def check_password_match(self):
        if self.password != self.confirm_password:
            raise ValueError("Password and confirm_password do not match")
        return self


class UserLogin(BaseModel):
    """Schema used for login."""
    username: str = Field(..., min_length=3, max_length=50, example="johndoe")
    password: str = Field(..., min_length=8, max_length=128, example="StrongPass123!")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "johndoe",
                "password": "StrongPass123!",
            }
        }
    )


class UserResponse(BaseModel):
    """Schema returned when reading user data from the API."""
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
