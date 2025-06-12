"""Authentication models - login, session, password operations."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from models.user.user_password import validate_password_strength

from .user_commons import OperationResult
from .user_role import UserRole


class UserLogin(BaseModel):
    """Model untuk user login."""

    username: str = Field(min_length=3, max_length=50, description="Username")
    password: str = Field(
        min_length=6,
        max_length=20,
        description=(
            "Password (6-20 karakter, harus mengandung huruf besar, kecil, angka, "
            "dan karakter khusus)"
        ),
    )
    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength for login."""
        return validate_password_strength(v)


class UserActiveSession(BaseModel):
    """Model untuk active user session - simplified."""

    user_id: int = Field(gt=0, description="User ID")
    username: str = Field(description="Username")
    name: str = Field(description="Nama lengkap")
    role_id: int = Field(gt=0, description="Role ID dari database")
    role_name: UserRole = Field(description="User role")
    login_time: datetime = Field(default_factory=datetime.now)
    session_token: str | None = Field(None, description="Database session token")
    model_config = ConfigDict(from_attributes=True)


class LoginResult(OperationResult):
    """Model untuk login operation result."""

    user_session: UserActiveSession | None = Field(
        default=None, description="Session data jika berhasil"
    )
