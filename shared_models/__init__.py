"""Shared models package."""

from .models import (
    Base,
    User,
    Topic,
    Message,
    Category,
    Subcategory,
    Task,
    Embedding,
    MessageEmbedding,
    UserKnowledgeRecord,
    UserMessageExample,
)
from .schemas import (
    # Category schemas
    CategoryBase,
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    # Subcategory schemas
    SubcategoryBase,
    SubcategoryCreate,
    SubcategoryUpdate,
    SubcategoryResponse,
    # User schemas
    UserBaseModel,
    UserBaseContext,
    Status,
    UserRole,
    # Topic schemas
    TopicBase,
    TopicCreate,
    TopicUpdate,
    TopicResponse,
    TopicWithMessages,
    TopicWithCategories,
    TopicList,
    # Message schemas
    MessageBase,
    MessageCreate,
    MessageUpdate,
    MessageResponse,
)
from .database import engine, SessionLocal, get_db

__all__ = [
    # Models
    "Base",
    "User",
    "Topic",
    "Message",
    "Category",
    "Subcategory",
    "Task",
    "Embedding",
    "MessageEmbedding",
    "UserKnowledgeRecord",
    "UserMessageExample",
    # Category schemas
    "CategoryBase",
    "CategoryCreate",
    "CategoryUpdate",
    "CategoryResponse",
    # Subcategory schemas
    "SubcategoryBase",
    "SubcategoryCreate",
    "SubcategoryUpdate",
    "SubcategoryResponse",
    # User schemas
    "UserBaseModel",
    "UserBaseContext",
    "UserRole",
    "Status",
    # Topic schemas
    "TopicBase",
    "TopicCreate",
    "TopicUpdate",
    "TopicResponse",
    "TopicWithMessages",
    "TopicWithCategories",
    "TopicList",
    # Message schemas
    "MessageBase",
    "MessageCreate",
    "MessageUpdate",
    "MessageResponse",
    # Database
    "engine",
    "SessionLocal",
    "get_db",
]
