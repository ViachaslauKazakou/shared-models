"""Shared-model-ready SQLAlchemy models for Tutor RAG.

This module is a blueprint for moving RAG models to shared_models.
It defines:
1. Per-user, per-topic chunk storage with many records per user.
2. Retrieval/usage audit records for observability and token accounting.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Any

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

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
    ocr = "ocr"
    import_api = "import_api"


class RAGUsagePurpose(str, Enum):
    lesson_draft = "lesson_draft"
    quiz_check = "quiz_check"
    ingest = "ingest"


class UserTopicKnowledgeChunk(Base):
    """Per-user, per-topic chunk used for semantic retrieval."""

    __tablename__ = "user_topic_knowledge_chunks"
    __table_args__ = (
        Index("ix_utkc_user_topic_updated", "user_id", "topic", "updated_at"),
        Index("ix_utkc_user_source_filename", "user_id", "source_filename"),
        Index("ix_utkc_user_source_ref", "user_id", "source_ref"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    topic: Mapped[str] = mapped_column(String(255), index=True, nullable=False)

    source_type: Mapped[RAGSourceType] = mapped_column(
        SAEnum(RAGSourceType, name="rag_source_type", native_enum=False),
        nullable=False,
        default=RAGSourceType.manual,
    )
    source_label: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_filename: Mapped[str | None] = mapped_column(String(512), nullable=True)
    source_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    chunk_index: Mapped[int | None] = mapped_column(Integer, nullable=True)

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

    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])


class TutorRAGUsage(Base):
    """Audit and token accounting for RAG usage in AI Tutor."""

    __tablename__ = "tutor_rag_usage"
    __table_args__ = (
        Index("ix_tru_user_topic_created", "user_id", "topic", "created_at"),
        Index("ix_tru_session_created", "session_id", "created_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)

    topic: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    session_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tutor_sessions.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    purpose: Mapped[RAGUsagePurpose] = mapped_column(
        SAEnum(RAGUsagePurpose, name="rag_usage_purpose", native_enum=False),
        nullable=False,
    )

    query_text: Mapped[str] = mapped_column(Text, nullable=False)
    retrieved_chunk_ids: Mapped[list[str] | None] = mapped_column(JSONB, nullable=True)
    retrieved_count: Mapped[int | None] = mapped_column(Integer, nullable=True)

    provider: Mapped[str | None] = mapped_column(String(64), nullable=True)
    llm_model: Mapped[str | None] = mapped_column(String(128), nullable=True)

    prompt_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    completion_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    metadata_json: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])
    session: Mapped["TutorSession"] = relationship("TutorSession", foreign_keys=[session_id])


__all__ = [
    "RAGSourceType",
    "RAGUsagePurpose",
    "UserTopicKnowledgeChunk",
    "TutorRAGUsage",
]
