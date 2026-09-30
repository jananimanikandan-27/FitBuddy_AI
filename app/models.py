from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class User(Base):
    """
    Stores FitBuddy user information.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=False
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    age: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    weight: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    goal: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    intensity: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )


class WorkoutPlan(Base):
    """
    Stores original and updated AI workout plans.
    """

    __tablename__ = "workout_plans"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id: Mapped[str] = mapped_column(
        String(100),
        index=True,
        nullable=False
    )

    original_plan: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    updated_plan: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    nutrition_tip: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    feedback: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )