import uuid
from datetime import datetime
from enum import Enum as PyEnum
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    JSON,
    UUID,
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func


from shared_models.models import Base, User


class TopicLevel(str, PyEnum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"


class TopicStatus(str, PyEnum):
    draft = "draft"
    published = "published"
    archived = "archived"


class SessionStatus(str, PyEnum):
    scheduled = "scheduled"
    in_progress = "in_progress"
    completed = "completed"
    abandoned = "abandoned"


class MessageRole(str, PyEnum):
    user = "user"
    assistant = "assistant"
    system = "system"


class MessageType(str, PyEnum):
    text = "text"
    voice_transcript = "voice_transcript"
    theory = "theory"
    question = "question"
    quiz = "quiz"
    code = "code"
    diagram = "diagram"


class LessonPhase(str, PyEnum):
    intro = "intro"
    theory = "theory"
    dialog = "dialog"
    quiz = "quiz"
    summary = "summary"


# ── Models ─────────────────────────────────────────────────────────────────────

class TutorTopic(Base):
    """Учебная тема — каталог контента для ИИ-тьютора."""

    __tablename__ = "tutor_topics"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    section: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    level: Mapped[TopicLevel] = mapped_column(
        Enum(TopicLevel, name="topic_level", native_enum=False),
        default=TopicLevel.beginner,
    )
    language: Mapped[str] = mapped_column(String(16), default="en")
    lesson_plan: Mapped[Dict[str, Any]] = mapped_column(
        JSON, default=lambda: {"questions": []},
        comment="Structured lesson plan: list of questions with phases and timing",
    )
    system_prompt_template: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True,
        comment="Custom system prompt template for this topic (Jinja2-like placeholders)",
    )
    estimated_duration_minutes: Mapped[int] = mapped_column(Integer, default=45)
    prerequisites: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON, nullable=True,
        comment="List of prerequisite topic IDs",
    )
    tags: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    status: Mapped[TopicStatus] = mapped_column(
        Enum(TopicStatus, name="topic_status", native_enum=False),
        default=TopicStatus.draft,
    )
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(),
    )

    # Relationships
    creator: Mapped["User"] = relationship("User", foreign_keys=[created_by])
    sessions: Mapped[List["TutorSession"]] = relationship(
        "TutorSession", back_populates="topic", cascade="all, delete-orphan",
    )


class TutorSession(Base):
    """Сессия занятия между учеником и ИИ-тьютором."""

    __tablename__ = "tutor_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey("tutor_topics.id"), nullable=False, index=True)
    status: Mapped[SessionStatus] = mapped_column(
        Enum(SessionStatus, name="session_status", native_enum=False),
        default=SessionStatus.scheduled,
    )
    current_phase: Mapped[LessonPhase] = mapped_column(
        Enum(LessonPhase, name="lesson_phase", native_enum=False),
        default=LessonPhase.intro,
    )
    current_question_index: Mapped[int] = mapped_column(Integer, default=0)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    overall_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    summary: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True,
        comment="AI-generated summary after session completion",
    )
    metadata_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        "metadata", JSON, nullable=True,
        comment="Extra data: mode (voice/text), LLM model, etc.",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(),
    )

    # Relationships
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])
    topic: Mapped["TutorTopic"] = relationship("TutorTopic", back_populates="sessions")
    messages: Mapped[List["TutorMessage"]] = relationship(
        "TutorMessage", back_populates="session", cascade="all, delete-orphan",
        order_by="TutorMessage.created_at",
    )
    question_results: Mapped[List["TutorQuestionResult"]] = relationship(
        "TutorQuestionResult", back_populates="session", cascade="all, delete-orphan",
    )


class TutorMessage(Base):
    """Одно сообщение в сессии (от пользователя, ИИ или системы)."""

    __tablename__ = "tutor_messages"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tutor_sessions.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    role: Mapped[MessageRole] = mapped_column(
        Enum(MessageRole, name="message_role", native_enum=False),
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    message_type: Mapped[MessageType] = mapped_column(
        Enum(MessageType, name="message_type", native_enum=False),
        default=MessageType.text,
    )
    phase: Mapped[LessonPhase] = mapped_column(
        Enum(LessonPhase, name="message_phase", native_enum=False),
        default=LessonPhase.dialog,
    )
    question_id: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True,
        comment="Linked question ID from lesson_plan",
    )
    tokens_used: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(),
    )

    # Relationships
    session: Mapped["TutorSession"] = relationship("TutorSession", back_populates="messages")


class TutorQuestionResult(Base):
    """Результат ответа ученика на конкретный вопрос."""

    __tablename__ = "tutor_question_results"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tutor_sessions.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    question_id: Mapped[str] = mapped_column(String(100), nullable=False)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    student_answer: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_correct: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    score: Mapped[float] = mapped_column(Float, default=0.0)
    feedback: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True,
        comment="AI feedback on the answer",
    )
    attempts: Mapped[int] = mapped_column(Integer, default=1)
    phase: Mapped[LessonPhase] = mapped_column(
        Enum(LessonPhase, name="question_phase", native_enum=False),
        default=LessonPhase.dialog,
    )
    time_spent_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(),
    )

    # Relationships
    session: Mapped["TutorSession"] = relationship(
        "TutorSession", back_populates="question_results",
    )


class TutorStudentProgress(Base):
    """Агрегированный прогресс ученика по всем сессиям."""

    __tablename__ = "tutor_student_progress"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, unique=True, index=True,
    )
    completed_topics: Mapped[Dict[str, Any]] = mapped_column(
        JSON, default=lambda: [],
        comment='[{"topic_id": 1, "score": 85.0, "completed_at": "..."}]',
    )
    current_level: Mapped[Dict[str, Any]] = mapped_column(
        JSON, default=lambda: {},
        comment='{"section_name": "beginner|intermediate|advanced"}',
    )
    total_sessions: Mapped[int] = mapped_column(Integer, default=0)
    total_time_minutes: Mapped[int] = mapped_column(Integer, default=0)
    strengths: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    weaknesses: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(),
    )

    # Relationships
    user: Mapped[User] = relationship("User", foreign_keys=[user_id])
    anti_cheat_config: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
        comment="Anti-cheat configuration for exam mode: enabled, methods, warnings_limit, etc."
    )
