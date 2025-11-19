# app/schemas/token.py

from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID


class TokenResponse(BaseModel):
    """Response schema returned on successful login."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Token type")

    # Optional: small user info if you want, or leave minimal for now.
    user_id: UUID | None = None
    username: str | None = None
    email: str | None = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "username": "johndoe",
                "email": "john.doe@example.com",
            }
        }
    )
