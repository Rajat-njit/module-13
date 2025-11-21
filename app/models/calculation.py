# app/models/calculation.py

"""
Polymorphic Calculation model.

We support multiple calculation types via inheritance:
- Base `Calculation` (polymorphic parent)
- `Addition`, `Subtraction`, `Multiplication`, `Division` subclasses

Factory method:
    Calculation.create(type, user_id, inputs)
"""

import uuid
from datetime import datetime
from typing import List

from sqlalchemy import (
    Column,
    String,
    DateTime,
    ForeignKey,
    JSON,
    Float,
)
from sqlalchemy.orm import relationship, declared_attr
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy import types

from app.database import Base


# -------------------------------------------------------------
# UUID compatibility for BOTH PostgreSQL & SQLite
# -------------------------------------------------------------
class GUID(types.TypeDecorator):
    """Platform-independent GUID type.

    - On PostgreSQL -> use native UUID
    - On SQLite -> store as CHAR(36)
    """

    impl = types.CHAR(36)
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            # Use native UUID column
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        else:
            # Store UUID as a string for SQLite
            return dialect.type_descriptor(types.CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return None

        if isinstance(value, uuid.UUID):
            # Always store as string
            return str(value)

        # Convert from string → UUID → string (normalized)
        return str(uuid.UUID(str(value)))

    def process_result_value(self, value, dialect):
        if value is None:
            return None

        # Convert database string → UUID object
        return uuid.UUID(str(value))


# -------------------------------------------------------------
# Abstract mixin class
# -------------------------------------------------------------
class AbstractCalculation:
    """Shared fields for all calculation models via declared_attr."""

    @declared_attr
    def __tablename__(cls):
        return "calculations"

    @declared_attr
    def id(cls):
        return Column(GUID(), primary_key=True, default=uuid.uuid4)

    @declared_attr
    def user_id(cls):
        return Column(
            GUID(),
            ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        )

    @declared_attr
    def type(cls):
        return Column(String(50), nullable=False, index=True)

    @declared_attr
    def inputs(cls):
        return Column(JSON, nullable=False)

    @declared_attr
    def result(cls):
        return Column(Float, nullable=True)

    @declared_attr
    def created_at(cls):
        return Column(DateTime, default=datetime.utcnow, nullable=False)

    @declared_attr
    def updated_at(cls):
        return Column(
            DateTime,
            default=datetime.utcnow,
            onupdate=datetime.utcnow,
            nullable=False,
        )

    @declared_attr
    def user(cls):
        return relationship("User", back_populates="calculations")

    # ------------ Factory method ------------
    @classmethod
    def create(cls, calculation_type: str, user_id: uuid.UUID, inputs: List[float]):
        mapping = {
            "addition": Addition,
            "subtraction": Subtraction,
            "multiplication": Multiplication,
            "division": Division,
        }

        calculation_cls = mapping.get(calculation_type.lower())
        if not calculation_cls:
            raise ValueError(f"Unsupported calculation type: {calculation_type}")   # pragma: no cover

        return calculation_cls(user_id=user_id, inputs=inputs)

    # ------------ Abstract compute method ------------
    def get_result(self) -> float:
        raise NotImplementedError       # pragma: no cover


# -------------------------------------------------------------
# Parent Polymorphic Model
# -------------------------------------------------------------
class Calculation(Base, AbstractCalculation):
    __mapper_args__ = {
        "polymorphic_on": "type",
        "polymorphic_identity": "calculation",
    }


# -------------------------------------------------------------
# CHILD MODELS WITH PROPER polymorphic_identity + constructors
# -------------------------------------------------------------
class Addition(Calculation):
    __mapper_args__ = {"polymorphic_identity": "addition"}

    def __init__(self, **kwargs):
        kwargs["type"] = "addition"
        super().__init__(**kwargs)

    def get_result(self) -> float:
        if len(self.inputs) < 2:
            raise ValueError("Addition requires at least two numbers.") # pragma: no cover
        return float(sum(self.inputs))


class Subtraction(Calculation):
    __mapper_args__ = {"polymorphic_identity": "subtraction"}

    def __init__(self, **kwargs):
        kwargs["type"] = "subtraction"
        super().__init__(**kwargs)

    def get_result(self) -> float:  # pragma: no cover
        if len(self.inputs) < 2:
            raise ValueError("Subtraction requires at least two numbers.")  # pragma: no cover
        result = self.inputs[0]
        for v in self.inputs[1:]:
            result -= v
        return float(result)    # pragma: no cover


class Multiplication(Calculation):
    __mapper_args__ = {"polymorphic_identity": "multiplication"}

    def __init__(self, **kwargs):
        kwargs["type"] = "multiplication"
        super().__init__(**kwargs)

    def get_result(self) -> float:
        if len(self.inputs) < 2:
            raise ValueError("Multiplication requires at least two numbers.")
        result = 1.0
        for v in self.inputs:
            result *= v
        return float(result)


class Division(Calculation):
    __mapper_args__ = {"polymorphic_identity": "division"}

    def __init__(self, **kwargs):
        kwargs["type"] = "division"
        super().__init__(**kwargs)

    def get_result(self) -> float:
        if len(self.inputs) < 2:
            raise ValueError("Division requires at least two numbers.")
        result = self.inputs[0]
        for v in self.inputs[1:]:
            if v == 0:
                raise ValueError("Cannot divide by zero.")
            result /= v
        return float(result)
