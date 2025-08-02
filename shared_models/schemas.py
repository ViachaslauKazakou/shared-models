from enum import Enum as PyEnum
from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime
from typing import List, Optional


class Status(str, PyEnum):
    pending = "pending"
    active = "active"
    disabled = "disabled"
    blocked = "Забанен"
    deleted = "deleted"


# Enum for user roles
class UserRole(str, PyEnum):
    admin = "admin"
    user = "user"
    ai_bot = "ai_bot"  # AI user with both admin and user capabilities
    mixed = "mixed"  # User with both admin and user capabilities
    mentor = "mentor"  # User with mentor capabilities
    mentee = "mentee"  # User with mentee capabilities


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


class TopicBase(BaseModel):
    title: str
    description: Optional[str] = None


class TopicCreate(TopicBase):
    user_id: Optional[int] = None


class TopicUpdate(TopicBase):
    is_active: bool = True


class TopicResponse(TopicBase):
    id: int
    user_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


class TopicWithMessages(TopicResponse):
    messages: List[MessageResponse] = []


class TopicList(TopicBase):
    id: int
    user_id: Optional[int]
    created_at: datetime
    message_count: int = 0
    is_active: bool

    class Config:
        from_attributes = True


class UserBaseContext(BaseModel):
    # id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # user_id: int
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
    user_type: Optional[UserRole] = None  # = UserRole.admin  # Default role is admin
    status: Optional[Status] = None  # = UserStatus.pending  # Default status is pending

    model_config = ConfigDict(from_attributes=True)


# Обновляем forward reference
MessageResponse.model_rebuild()
