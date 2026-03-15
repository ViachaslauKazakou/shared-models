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
from .quiz_model import *
from .documents_models import *
from .mentor_models import (
    MentorMentee,
    MentorMenteeStatus,
)
from .tutor_models import (
    TutorTopic,
    TutorSession,
    TutorMessage,
    TutorQuestionResult,
    TutorStudentProgress,
    TopicLevel,
    TopicStatus,
    SessionStatus,
    MessageRole,
    MessageType,
    LessonPhase,
)
from .rag_models import (
    UserTopicKnowledgeChunk,
    TutorRAGUsage,
    RAGSourceType,
    RAGUsagePurpose,
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
    # Mentor-Mentee models
    "MentorMentee",
    "MentorMenteeStatus",
    # Tutor models
    "TutorTopic",
    "TutorSession",
    "TutorMessage",
    "TutorQuestionResult",
    "TutorStudentProgress",
    "TopicLevel",
    "TopicStatus",
    "SessionStatus",
    "MessageRole",
    "MessageType",
    "LessonPhase",
    # RAG models
    "UserTopicKnowledgeChunk",
    "TutorRAGUsage",
    "RAGSourceType",
    "RAGUsagePurpose",
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
