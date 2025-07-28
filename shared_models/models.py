import uuid
from sqlalchemy import String, Text, DateTime, ForeignKey, Boolean, Enum, JSON, UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import Optional, List, Dict
from datetime import datetime
from shared_models.schemas import UserRole, Status
from pgvector.sqlalchemy import Vector


# Базовый класс для моделей
class Base(DeclarativeBase):
    pass


class Topic(Base):
    __tablename__ = "topics"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Внешний ключ на пользователя
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)

    # Связи
    user: Mapped["User"] = relationship("User", back_populates="topics")
    messages: Mapped[List["Message"]] = relationship("Message", back_populates="topic", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    author_name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Внешние ключи
    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("messages.id"), nullable=True)

    # Связи
    topic: Mapped["Topic"] = relationship("Topic", back_populates="messages")
    user: Mapped["User"] = relationship("User", back_populates="messages")
    parent: Mapped[Optional["Message"]] = relationship("Message", remote_side=[id], back_populates="replies")
    replies: Mapped[List["Message"]] = relationship("Message", back_populates="parent", cascade="all, delete-orphan")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True, server_default=func.now())
    username: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    firstname: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    lastname: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

    user_type: Mapped[Optional[UserRole]] = mapped_column(
        Enum(UserRole, name="user_type", native_enum=False),
        default=UserRole.user,
        nullable=True,
    )
    status: Mapped[Optional[Status]] = mapped_column(
        Enum(Status, name="user_status", native_enum=False),
        default=Status.pending,
        nullable=True,
    )

    # Relationships
    topics: Mapped[List["Topic"]] = relationship("Topic", back_populates="user")
    messages: Mapped[List["Message"]] = relationship("Message", back_populates="user")

    # RAG models


class Embedding(Base):
    """Таблица эмбеддингов"""

    __tablename__ = "embeddings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    content: Mapped[str] = mapped_column(Text)
    embedding: Mapped[Vector] = mapped_column(Vector(1536))
    extra_metadata: Mapped[Optional[Dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class MessageEmbedding(Base):
    """Таблица эмбеддингов сообщений форума"""

    __tablename__ = "message_embeddings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    message_id: Mapped[int] = mapped_column(index=True)
    topic_id: Mapped[int] = mapped_column(index=True)
    content: Mapped[str] = mapped_column(Text)
    embedding: Mapped[Vector] = mapped_column(Vector(1536))
    extra_metadata: Mapped[Optional[Dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class UserKnowledgeRecord(Base):
    """Таблица знаний пользователей"""

    __tablename__ = "user_knowledge"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Связь с реальным пользователем
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, index=True)

    # Дополнительное поле для хранения строкового идентификатора (например, alice_researcher)
    character_id: Mapped[Optional[str]] = mapped_column(String(50), unique=True, index=True, nullable=True)

    name: Mapped[str] = mapped_column(String(100))
    personality: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    background: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    expertise: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    communication_style: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    preferences: Mapped[Optional[Dict]] = mapped_column(JSON, nullable=True)
    file_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())


class UserMessageExample(Base):
    """Таблица примеров сообщений пользователей"""

    __tablename__ = "user_message_examples"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Связь с реальным пользователем
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    # Дополнительное поле для хранения строкового идентификатора (например, alaev)
    character_id: Mapped[Optional[str]] = mapped_column(String(50), index=True, nullable=True)

    # Основные поля сообщения
    context: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    content: Mapped[str] = mapped_column(Text)
    thread_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    reply_to: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)

    # Эмбеддинги для similarity search
    content_embedding: Mapped[Optional[Vector]] = mapped_column(Vector(1536), nullable=True)
    context_embedding: Mapped[Optional[Vector]] = mapped_column(Vector(1536), nullable=True)

    # Метаданные и служебные поля
    extra_metadata: Mapped[Optional[Dict]] = mapped_column(JSON, nullable=True)
    source_file: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
