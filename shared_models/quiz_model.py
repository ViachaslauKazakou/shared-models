from sqlalchemy.sql import func
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Text,
    Boolean,
    JSON,
    DateTime,
)
from sqlalchemy.orm import (
    relationship,
    validates,
    Mapped,
    mapped_column,
    DeclarativeBase,
)
from pydantic import BaseModel, field_validator
from typing import List, Dict, Optional
from src.models import Base, User

# from sqlalchemy import MetaData

# metadata = MetaData()

# class Base(DeclarativeBase):
#     metadata = metadata


# Pydantic models for JSON validation
class AnswerSchema(BaseModel):
    answer_text: str
    is_correct: bool


class QuestionSchema(BaseModel):
    question_id: str
    question_description: Optional[str] | None  # Optional field question in text format
    question_text: str
    question_image: Optional[str] | None  # Optional field for image with question
    description_answer: str | None  #
    answers: List[AnswerSchema]


class Quiz(Base):
    __tablename__ = "quizzes"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), nullable=True, server_default=func.now()
    )
    title: Mapped[str] = mapped_column(nullable=False, unique=True)
    language: Mapped[str] = mapped_column(nullable=True, unique=True, default="en")
    questions: Mapped[Dict] = mapped_column(
        JSON
    )  # Stores list of questions with nested answers

    # user = relationship("User", back_populates="users")

    # @validates('questions')
    # def validate_questions(self, key, questions_data):
    #     # Validate JSON structure using pydantic
    #     questions = [QuestionSchema(**q) for q in questions_data]
    #     return questions_data


class UserQuizResult(Base):
    __tablename__ = "user_quiz_results"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), nullable=True, server_default=func.now()
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    quiz_id: Mapped[int] = mapped_column(ForeignKey("quizzes.id"))
    results: Mapped[Dict] = mapped_column(JSON)
    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), nullable=True, server_default=func.now()
    )

    # user = relationship("User", back_populates="user_quiz_results")
    # quiz = relationship("Quiz", back_populates="user_quiz_results")
