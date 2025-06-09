"""Authentication models untuk MIM3 Dashboard."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

type UserRole = Literal["admin", "user", "manager"]


class UserLogin(BaseModel):
    """Model untuk login request."""

    username: str = Field(min_length=3, max_length=50, description="Username")
    password: str = Field(min_length=6, description="Password")

    model_config = ConfigDict(str_strip_whitespace=True)


class UserSession(BaseModel):
    """Model untuk user session data."""

    user_id: int = Field(gt=0, description="User ID")
    username: str = Field(description="Username")
    role: UserRole = Field(description="User role")
    login_time: datetime = Field(default_factory=datetime.now)

    model_config = ConfigDict(from_attributes=True)


class AuthResult(BaseModel):
    """Model untuk authentication result."""

    success: bool = Field(description="Authentication berhasil atau tidak")
    user_session: UserSession | None = Field(
        default=None, description="Session data jika berhasil"
    )
    error_message: str | None = Field(
        default=None, description="Error message jika gagal"
    )
