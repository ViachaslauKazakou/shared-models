"""Example models for shared_models integration (RAG).

This file contains reference SQLAlchemy models that should live in shared_models,
not in the service runtime models. They are kept here as a blueprint for the
shared_models repository.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

try:
    from pgvector.sqlalchemy import Vector
except Exception:  # pragma: no cover
    Vector = None  # type: ignore[assignment]

try:
    from shared_models.models import Base
except Exception:  # pragma: no cover
    # Fallback for local typing/demo usage.
    from sqlalchemy.orm import DeclarativeBase

    class Base(DeclarativeBase):
        pass


class RAGSourceType(str, Enum):
    manual = "manual"
    session = "session"
    file = "file"


class RAGUsagePurpose(str, Enum):
    lesson_draft = "lesson_draft"
    quiz_check = "quiz_check"


class UserTopicKnowledgeChunk(Base):
    """Per-user, per-topic chunk used for retrieval."""

    __tablename__ = "user_topic_knowledge_chunks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)

    topic: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    source_type: Mapped[RAGSourceType] = mapped_column(
        SAEnum(RAGSourceType, name="rag_source_type"),
        nullable=False,
        default=RAGSourceType.manual,
    )

    content: Mapped[str] = mapped_column(Text, nullable=False)

    if Vector is not None:
        embedding: Mapped[list[float] | None] = mapped_column(Vector(1536), nullable=True)
    else:
        embedding: Mapped[Any | None] = mapped_column(JSONB, nullable=True)

    embedding_model: Mapped[str] = mapped_column(String(128), nullable=False, default="text-embedding-3-small")
    metadata_json: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class TutorRAGUsage(Base):
    """Audit and token accounting for RAG usage in AI Tutor."""

    __tablename__ = "tutor_rag_usage"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)

    topic: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    session_id: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True)
    purpose: Mapped[RAGUsagePurpose] = mapped_column(SAEnum(RAGUsagePurpose, name="rag_usage_purpose"), nullable=False)

    query_text: Mapped[str] = mapped_column(Text, nullable=False)
    retrieved_chunk_ids: Mapped[list[int] | None] = mapped_column(JSONB, nullable=True)

    prompt_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    completion_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
