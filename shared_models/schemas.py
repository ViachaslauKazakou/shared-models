"""Shared Pydantic schemas and enums.

CHANGED FILE: shared_models/schemas.py
Changes vs original:
  1. Added `import enum` (was missing)
  2. Added `from decimal import Decimal`
  3. Added `import uuid`
  4. Added payment enums: TransactionType, TransactionStatus, WithdrawRequestStatus
  5. Added payment Pydantic schemas at the bottom (before MessageResponse.model_rebuild())
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime
from decimal import Decimal
from enum import Enum as PyEnum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class Status(str, PyEnum):
    pending = "pending"
    active = "active"
    disabled = "disabled"
    blocked = "blocked"
    deleted = "deleted"


class MessageStatus(str, PyEnum):
    pending = "pending"
    active = "active"
    blocked = "blocked"
    replied = "replied"


class PrivateMessageStatus(str, PyEnum):
    unread = "unread"
    read = "read"
    deleted = "deleted"
    replied = "replied"


class SubjectBookStatus(str, PyEnum):
    pending = "pending"
    confirmed = "confirmed"
    cancelled = "cancelled"
    released = "released"
    finished = "finished"


class TaskType(str, PyEnum):
    general = "general"
    question = "question"
    tutorial = "tutorial"
    code = "code"
    moderate = "moderate"
    create = "create"
    help = "help"


# Enum for user roles
class UserRole(str, PyEnum):
    admin = "admin"
    user = "user"
    ai_bot = "ai_bot"
    mixed = "mixed"
    mentor = "mentor"
    mentee = "mentee"


# Enum for learn type
class LearnMode(str, PyEnum):
    offline = "offline"
    online = "online"
    both = "both"


class CurrentMonth(str, PyEnum):
    january = "january"
    february = "february"
    march = "march"
    april = "april"
    may = "may"
    june = "june"
    july = "july"
    august = "august"
    september = "september"
    october = "october"
    november = "november"
    december = "december"


class DayOfWeek(str, PyEnum):
    monday = "monday"
    tuesday = "tuesday"
    wednesday = "wednesday"
    thursday = "thursday"
    friday = "friday"
    saturday = "saturday"
    sunday = "sunday"


class LanguageEnum(str, PyEnum):
    en = "en"
    ru = "ru"
    by = "by"
    pl = "pl"
    ua = "ua"


class QuestionType(str, PyEnum):
    """Question type: single choice or multiple choice"""
    single_choice = "single_choice"
    multiple_choice = "multiple_choice"


# =============================================================================
# Payment enums
# Defined here (not in payment_models.py) to avoid circular imports:
#   schemas.py  ←  models.py  ←  payment_models.py
# =============================================================================

class TransactionType(str, PyEnum):
    """All possible types of balance movement."""

    # Credits IN
    topup_stub = "topup_stub"
    """Bank / payment-system topup (stub — confirmed manually by admin)."""
    reward_forum_topic = "reward_forum_topic"
    """Reward for a forum topic that reached rating >= 10 unique votes."""
    reward_public_quiz = "reward_public_quiz"
    """Reward for publishing a public quiz (after first paid access event)."""
    reward_ai_course = "reward_ai_course"
    """Reward for publishing an AI Tutor topic (after first paid access)."""
    admin_adjustment = "admin_adjustment"
    """Manual admin correction — amount may be negative."""
    refund_to_student = "refund_to_student"
    """Mentor returns credits to a student."""

    # Credits OUT
    spend_quiz = "spend_quiz"
    """Student pays to access a paid quiz."""
    spend_ai_tokens = "spend_ai_tokens"
    """AI generation / AI Tutor session cost, proportional to tokens used."""
    spend_course_access = "spend_course_access"
    """Student pays to access a paid AI Tutor topic / course."""
    spend_booking = "spend_booking"
    """Student pays for a subject/lesson booking."""
    transfer_to_mentor = "transfer_to_mentor"
    """Internal transfer: student → mentor payout after finished booking."""
    withdraw_stub = "withdraw_stub"
    """Withdrawal to bank/card — stub, processed manually by admin."""

    # System / internal
    reserve = "reserve"
    """Reserve credits for a pending booking (reduces available_credits)."""
    release = "release"
    """Release reserved credits on cancellation or refund."""


class TransactionStatus(str, PyEnum):
    """Lifecycle status of a single ledger entry."""

    pending = "pending"
    """Created but not yet finalised (e.g. booking not confirmed yet)."""
    completed = "completed"
    """Successfully applied to the user's balance."""
    failed = "failed"
    """Processing failed; balance was NOT changed."""
    canceled = "canceled"
    """Explicitly canceled before completion."""
    reversed = "reversed"
    """Reversed by a subsequent refund / release transaction."""


class WithdrawRequestStatus(str, PyEnum):
    """Status of a topup or withdrawal stub request."""

    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"
    canceled = "canceled"


# =============================================================================
# Existing Pydantic schemas (unchanged from original)
# =============================================================================

class MessageBase(BaseModel):
    content: str
    author_name: str


class MessageCreate(MessageBase):
    topic_id: int
    parent_id: Optional[int] = None
    user_id: Optional[int] = None


class MessageUpdate(BaseModel):
    content: str
    author_name: str


class MessageResponse(MessageBase):
    id: int
    topic_id: int
    parent_id: Optional[int]
    user_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    replies: List["MessageResponse"] = []

    class Config:
        from_attributes = True


class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    slug: str
    color: Optional[str] = None
    icon: Optional[str] = None
    is_active: bool = True
    sort_order: int = 0


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    slug: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None


class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SubcategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    slug: str
    color: Optional[str] = None
    icon: Optional[str] = None
    is_active: bool = True
    sort_order: int = 0
    category_id: int


class SubcategoryCreate(SubcategoryBase):
    pass


class SubcategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    slug: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None
    category_id: Optional[int] = None


class SubcategoryResponse(SubcategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TopicBase(BaseModel):
    title: str
    description: Optional[str] = None
    task_type: Optional[TaskType] = TaskType.general


class TopicCreate(TopicBase):
    user_id: Optional[int] = None
    category_id: Optional[int] = None
    subcategory_id: Optional[int] = None


class TopicUpdate(TopicBase):
    is_active: bool = True
    category_id: Optional[int] = None
    subcategory_id: Optional[int] = None


class TopicResponse(TopicBase):
    id: int
    user_id: Optional[int]
    category_id: Optional[int]
    subcategory_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


class TopicWithMessages(TopicResponse):
    messages: List[MessageResponse] = []


class TopicWithCategories(TopicResponse):
    category: Optional[CategoryResponse] = None
    subcategory: Optional[SubcategoryResponse] = None


class TopicList(TopicBase):
    id: int
    user_id: Optional[int]
    category_id: Optional[int]
    subcategory_id: Optional[int]
    created_at: datetime
    message_count: int = 0
    is_active: bool

    class Config:
        from_attributes = True


class UserBaseContext(BaseModel):
    character: str
    character_type: str
    mood: str
    context: Optional[str]
    content: str
    timestamp: datetime
    reply_to: Optional[str]
    topic_id: Optional[str]

    class Config:
        from_attributes = True


class UserBaseModel(BaseModel):
    username: str
    firstname: str
    lastname: str
    password: str
    email: EmailStr
    user_type: Optional[UserRole] = None
    status: Optional[Status] = None

    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# Payment Pydantic schemas (NEW)
# =============================================================================

class BalanceResponse(BaseModel):
    """Current balance summary for a user — safe to expose in API responses."""

    user_id: int
    available_credits: Decimal
    reserved_credits: Decimal
    total_earned: Decimal
    total_spent: Decimal
    last_transaction_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class TransactionResponse(BaseModel):
    """Public view of a single ledger entry."""

    id: int
    user_id: int
    amount: Decimal
    transaction_type: TransactionType
    status: TransactionStatus
    reference_type: Optional[str] = None
    reference_id: Optional[int] = None
    counterpart_user_id: Optional[int] = None
    description: Optional[str] = None
    ai_tokens_used: Optional[int] = None
    extra_metadata: Optional[dict] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class AdminBalanceAdjustRequest(BaseModel):
    """Admin manual credit adjustment (positive = add, negative = deduct)."""

    user_id: int
    amount: Decimal = Field(..., description="Positive to add credits, negative to deduct")
    description: str = Field(..., min_length=5, max_length=500)
    idempotency_key: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique key to prevent duplicate adjustments",
    )


class TopupRequestCreate(BaseModel):
    """User creates a bank topup stub request."""

    amount_requested: Decimal = Field(..., gt=0)
    payment_method: Optional[str] = None
    external_reference: Optional[str] = None


class TopupRequestResponse(BaseModel):
    id: int
    user_id: int
    amount_requested: Decimal
    payment_method: Optional[str] = None
    status: WithdrawRequestStatus
    created_at: datetime
    processed_at: Optional[datetime] = None
    notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class WithdrawRequestCreate(BaseModel):
    """User requests withdrawal to bank/card (stub MVP)."""

    amount_requested: Decimal = Field(..., gt=0)
    payout_method: Optional[str] = None
    payout_details_masked: Optional[str] = Field(
        None,
        max_length=200,
        description="Masked bank/card details, e.g. '**** 1234'. NEVER submit raw numbers.",
    )

    @field_validator("payout_details_masked")
    @classmethod
    def must_be_masked(cls, v: Optional[str]) -> Optional[str]:
        """Reject obviously unmasked card numbers (16-digit strings)."""
        if v:
            digits_only = v.replace(" ", "").replace("-", "")
            if digits_only.isdigit() and len(digits_only) >= 15:
                raise ValueError(
                    "Do not submit raw card numbers — provide a masked value only (e.g. '**** 1234')."
                )
        return v


class WithdrawRequestResponse(BaseModel):
    id: int
    user_id: int
    amount_requested: Decimal
    payout_method: Optional[str] = None
    payout_details_masked: Optional[str] = None
    status: WithdrawRequestStatus
    created_at: datetime
    processed_at: Optional[datetime] = None
    notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class InternalTransferRequest(BaseModel):
    """Internal credit transfer between users (student → mentor or mentor → student)."""

    to_user_id: int
    amount: Decimal = Field(..., gt=0)
    description: Optional[str] = None
    idempotency_key: str = Field(default_factory=lambda: str(uuid.uuid4()))


class TopicVoteResponse(BaseModel):
    id: int
    topic_id: int
    user_id: int
    created_at: datetime
    vote_count: int = Field(0, description="Total votes for the topic at response time")

    model_config = ConfigDict(from_attributes=True)


# Update forward references
MessageResponse.model_rebuild()
