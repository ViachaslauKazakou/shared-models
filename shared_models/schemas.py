from enum import Enum as PyEnum


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
