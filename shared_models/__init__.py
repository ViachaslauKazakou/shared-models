"""Shared models package."""

from .models import (
    Base,
    User,
    Topic,
    Message,
    Embedding,
    MessageEmbedding,
    UserKnowledgeRecord,
    UserMessageExample,
)
from .schemas import UserRole, Status
from .database import engine, SessionLocal, get_db

__all__ = [
    "Base",
    "User",
    "Topic", 
    "Message",
    "Embedding",
    "MessageEmbedding",
    "UserKnowledgeRecord",
    "UserMessageExample",
    "UserRole",
    "Status",
    "engine",
    "SessionLocal",
    "get_db",
]
