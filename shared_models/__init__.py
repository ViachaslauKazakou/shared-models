"""Shared models package.

CHANGED FILE: shared_models/__init__.py
Changes vs original: added payment_models imports and exports.
"""

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
# ── NEW: payment models ──────────────────────────────────────────────────────
from .payment_models import (
    UserBalance,
    BalanceTransaction,
    TopupRequest,
    WithdrawRequest,
    TopicVote,
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
    # ── NEW: payment enums & schemas ────────────────────────────────────────
    TransactionType,
    TransactionStatus,
    WithdrawRequestStatus,
    BalanceResponse,
    TransactionResponse,
    AdminBalanceAdjustRequest,
    TopupRequestCreate,
    TopupRequestResponse,
    WithdrawRequestCreate,
    WithdrawRequestResponse,
    InternalTransferRequest,
    TopicVoteResponse,
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
    # Payment models (NEW)
    "UserBalance",
    "BalanceTransaction",
    "TopupRequest",
    "WithdrawRequest",
    "TopicVote",
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
    # Payment enums & schemas (NEW)
    "TransactionType",
    "TransactionStatus",
    "WithdrawRequestStatus",
    "BalanceResponse",
    "TransactionResponse",
    "AdminBalanceAdjustRequest",
    "TopupRequestCreate",
    "TopupRequestResponse",
    "WithdrawRequestCreate",
    "WithdrawRequestResponse",
    "InternalTransferRequest",
    "TopicVoteResponse",
    # Database
    "engine",
    "SessionLocal",
    "get_db",
]
