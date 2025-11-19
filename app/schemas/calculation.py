# app/schemas/calculation.py

from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict, model_validator, field_validator


class CalculationType(str, Enum):
    ADDITION = "addition"
    SUBTRACTION = "subtraction"
    MULTIPLICATION = "multiplication"
    DIVISION = "division"


class CalculationBase(BaseModel):
    """Base schema for calculation operations."""
    type: CalculationType = Field(..., description="Type of calculation")
    inputs: List[float] = Field(..., min_length=2, description="List of numbers")

    @field_validator("inputs", mode="before")
    @classmethod
    def ensure_list(cls, v):
        if not isinstance(v, list):
            raise ValueError("inputs must be a list of numbers")    # pragma: no cover
        return v

    @model_validator(mode="after")
    def check_division_by_zero(self):
        """Prevent division by zero (for division type)."""
        if self.type == CalculationType.DIVISION:
            if any(x == 0 for x in self.inputs[1:]):
                raise ValueError("Division by zero is not allowed") # pragma: no cover
        return self

    model_config = ConfigDict(from_attributes=True)


class CalculationUpdate(BaseModel):
    """Schema used when updating an existing calculation."""
    inputs: Optional[List[float]] = Field(
        default=None,
        min_length=2,
        description="New list of inputs",
    )

    @model_validator(mode="after")
    def validate_inputs(self):
        if self.inputs is not None and len(self.inputs) < 2:
            raise ValueError("At least two numbers are required")
        return self

    model_config = ConfigDict(from_attributes=True)


class CalculationResponse(CalculationBase):
    """Schema for sending calculation data back to the client."""
    id: UUID
    user_id: UUID
    result: float
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
