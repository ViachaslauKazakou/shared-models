"""Mentor-Mentee relationship models."""

from __future__ import annotations

import enum
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from shared_models.models import Base


class MentorMenteeStatus(str, enum.Enum):
    """Status of mentor-mentee relationship."""

    PENDING = "pending"  # Request sent, awaiting confirmation
    ACTIVE = "active"  # Active relationship
    PAUSED = "paused"  # Paused
    COMPLETED = "completed"  # Completed
    REJECTED = "rejected"  # Rejected


class MentorMentee(Base):
    """Relationship between mentor and mentee."""

    __tablename__ = "mentor_mentee"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Relationships with users
    mentor_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    mentee_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)

    # Relationship status
    status: Mapped[MentorMenteeStatus] = mapped_column(
        Enum(MentorMenteeStatus, name="mentor_mentee_status", native_enum=False),
        default=MentorMenteeStatus.PENDING,
        nullable=False,
    )

    # Subscription settings
    subscribe_to_quizzes: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    subscribe_to_courses: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    subscribe_to_subjects: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Notes and description
    mentor_notes: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="Mentor's notes about the mentee"
    )
    mentee_notes: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="Mentee's notes about the mentor"
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    accepted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="When the relationship was accepted"
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="When the relationship was completed"
    )

    # Who initiated the relationship
    initiated_by: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        comment="'mentor' or 'mentee' - who created the request",
    )

    # Relationships
    mentor: Mapped["User"] = relationship(
        "User", foreign_keys=[mentor_id], back_populates="mentees"
    )
    mentee: Mapped["User"] = relationship(
        "User", foreign_keys=[mentee_id], back_populates="mentors"
    )

    # Constraints and indexes
    __table_args__ = (
        UniqueConstraint("mentor_id", "mentee_id", name="unique_mentor_mentee_pair"),
        Index("idx_mentor_id_status", "mentor_id", "status"),
        Index("idx_mentee_id_status", "mentee_id", "status"),
    )
