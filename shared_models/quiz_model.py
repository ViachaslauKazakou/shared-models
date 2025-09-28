"""Quiz domain models and Pydantic schemas."""

from __future__ import annotations

import enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field
from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models import Base


class QuestionType(str, enum.Enum):
    """Supported question formats."""

    SINGLE_CHOICE = "single_choice"
    MULTIPLE_CHOICE = "multiple_choice"
    TEXT_INPUT = "text_input"
    IMAGE = "image"
    FORMULA = "formula"


class QuizStatus(str, enum.Enum):
    """Publication status for a quiz."""

    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class ResultMode(str, enum.Enum):
    """Controls how quiz results are revealed."""

    PER_QUESTION = "per_question"
    FINAL_SUMMARY = "final_summary"
    BOTH = "both"


class CourseStatus(str, enum.Enum):
    """Publication status for a quiz course."""

    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class AttemptStatus(str, enum.Enum):
    """Lifecycle of a user's quiz attempt."""

    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class AnswerSchema(BaseModel):
    """Schema representing a single answer option."""

    id: Optional[str] = Field(default=None, description="Optional answer identifier")
    text: str = Field(..., description="Answer text")
    is_correct: bool = Field(False, description="Marks whether the answer is correct")
    explanation: Optional[str] = Field(
        default=None, description="Explanation shown after the question is answered"
    )
    points: int = Field(1, ge=0, description="Points awarded for this answer")


class QuestionSchema(BaseModel):
    """Schema representing a quiz question."""

    id: str = Field(..., description="Question identifier")
    title: Optional[str] = Field(default=None, description="Short title for navigation")
    text: str = Field(..., description="Question text")
    type: QuestionType = Field(default=QuestionType.SINGLE_CHOICE)
    description: Optional[str] = Field(default=None, description="Additional details")
    image_url: Optional[str] = Field(default=None, description="Optional image for the question")
    formula_template: Optional[str] = Field(
        default=None, description="Math/physics/chemistry formula stored as KaTeX"
    )
    points: int = Field(1, ge=0, description="Points awarded for the question")
    time_limit_seconds: Optional[int] = Field(
        default=None, ge=1, description="Optional time limit for the question"
    )
    shuffle_answers: bool = Field(default=True, description="Shuffle answers when rendering")
    answers: List[AnswerSchema] = Field(default_factory=list)


class QuizPayload(BaseModel):
    """Container for storing questions inside a quiz."""

    questions: List[QuestionSchema] = Field(default_factory=list)


class QuizResultPayload(BaseModel):
    """Serialized quiz result stored for auditing or reporting."""

    quiz_id: int
    total_questions: int
    correct_answers: int
    total_points: int
    earned_points: int
    percentage: float
    answers: Dict[str, Any]


class Quiz(Base):
    """Quiz entity describing a standalone assessment."""

    __tablename__ = "quizzes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    slug: Mapped[Optional[str]] = mapped_column(String(255), unique=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    language: Mapped[str] = mapped_column(String(16), default="en")
    status: Mapped[QuizStatus] = mapped_column(Enum(QuizStatus), default=QuizStatus.DRAFT)
    result_mode: Mapped[ResultMode] = mapped_column(Enum(ResultMode), default=ResultMode.FINAL_SUMMARY)
    time_limit_minutes: Mapped[Optional[int]] = mapped_column(Integer)
    passing_score: Mapped[float] = mapped_column(Float, default=70.0)
    max_attempts: Mapped[int] = mapped_column(Integer, default=3)
    show_correct_answers: Mapped[bool] = mapped_column(Boolean, default=True)
    send_email_on_completion: Mapped[bool] = mapped_column(Boolean, default=False)
    randomize_questions: Mapped[bool] = mapped_column(Boolean, default=False)
    payload: Mapped[Dict[str, Any]] = mapped_column(
        "questions", JSON, default=lambda: {"questions": []}
    )
    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    creator = relationship("User")
    course_items = relationship(
        "QuizCourseItem", back_populates="quiz", cascade="all, delete-orphan"
    )
    attempts = relationship(
        "QuizProgress", back_populates="quiz", cascade="all, delete-orphan"
    )
    results = relationship(
        "UserQuizResult", back_populates="quiz", cascade="all, delete-orphan"
    )


class UserQuizResult(Base):
    """Finalized quiz attempt result."""

    __tablename__ = "user_quiz_results"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    quiz_id: Mapped[int] = mapped_column(ForeignKey("quizzes.id"))
    attempt_id: Mapped[Optional[int]] = mapped_column(ForeignKey("quiz_progress.id"))
    total_questions: Mapped[int] = mapped_column(Integer)
    correct_answers: Mapped[int] = mapped_column(Integer)
    total_points: Mapped[int] = mapped_column(Integer)
    earned_points: Mapped[int] = mapped_column(Integer)
    percentage: Mapped[float] = mapped_column(Float)
    passed: Mapped[bool] = mapped_column(Boolean, default=False)
    time_spent_seconds: Mapped[Optional[int]] = mapped_column(Integer)
    result_payload: Mapped[Dict[str, Any]] = mapped_column(JSON)

    quiz = relationship("Quiz", back_populates="results")
    user = relationship("User")


class QuizProgress(Base):
    """Represents an in-progress or completed attempt."""

    __tablename__ = "quiz_progress"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    quiz_id: Mapped[int] = mapped_column(ForeignKey("quizzes.id"))
    status: Mapped[AttemptStatus] = mapped_column(
        Enum(AttemptStatus), default=AttemptStatus.IN_PROGRESS
    )
    started_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    completed_at: Mapped[Optional[str]] = mapped_column(DateTime(timezone=True))
    current_index: Mapped[int] = mapped_column(Integer, default=0)
    answers: Mapped[Dict[str, Any]] = mapped_column(JSON, default=lambda: {"answers": {}})
    score: Mapped[Optional[float]] = mapped_column(Float)
    show_explanations: Mapped[bool] = mapped_column(Boolean, default=False)

    quiz = relationship("Quiz", back_populates="attempts")
    user = relationship("User")
    result = relationship("UserQuizResult", backref="attempt", uselist=False)


class QuizCourse(Base):
    """Course grouping quizzes into a sequence."""

    __tablename__ = "quiz_courses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    language: Mapped[str] = mapped_column(String(16), default="en")
    status: Mapped[CourseStatus] = mapped_column(Enum(CourseStatus), default=CourseStatus.DRAFT)
    is_sequential: Mapped[bool] = mapped_column(Boolean, default=True)
    certificate_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    creator = relationship("User")
    items = relationship("QuizCourseItem", back_populates="course", cascade="all, delete-orphan")
    progress_entries = relationship(
        "CourseProgress", back_populates="course", cascade="all, delete-orphan"
    )


class QuizCourseItem(Base):
    """Ordering metadata for quizzes inside a course."""

    __tablename__ = "quiz_course_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("quiz_courses.id"))
    quiz_id: Mapped[int] = mapped_column(ForeignKey("quizzes.id"))
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    is_required: Mapped[bool] = mapped_column(Boolean, default=True)

    course = relationship("QuizCourse", back_populates="items")
    quiz = relationship("Quiz", back_populates="course_items")


class CourseProgress(Base):
    """Tracks user progress throughout a quiz course."""

    __tablename__ = "quiz_course_progress"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    course_id: Mapped[int] = mapped_column(ForeignKey("quiz_courses.id"))
    started_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    last_activity_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    completed_item_ids: Mapped[List[int]] = mapped_column(JSON, default=list)
    current_item_id: Mapped[Optional[int]] = mapped_column(ForeignKey("quiz_course_items.id"))
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    completion_percentage: Mapped[float] = mapped_column(Float, default=0.0)

    user = relationship("User")
    course = relationship("QuizCourse", back_populates="progress_entries")
    current_item = relationship("QuizCourseItem")
