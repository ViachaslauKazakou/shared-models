from enum import Enum as PyEnum
from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime
from typing import List, Optional


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


class PrivateMessageStatus(str, PyEnum):
    unread = "unread"
    read = "read"
    deleted = "deleted"


class SubjectBookStatus(str, PyEnum):
    pending = "pending"
    confirmed = "confirmed"
    cancelled = "cancelled"


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
    ai_bot = "ai_bot"  # AI user with both admin and user capabilities
    mixed = "mixed"  # User with both admin and user capabilities
    mentor = "mentor"  # User with mentor capabilities
    mentee = "mentee"  # User with mentee capabilities
    

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
    

class LanguageEnum(str, PyEnum):
    en = "en"
    ru = "ru"
    by = "by"
    pl = "pl"
    ua = "ua"


# Обновляем forward reference
MessageResponse.model_rebuild()
