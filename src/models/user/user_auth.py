"""Authentication models - login, session, logout flow."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from .user_commons import OperationResult


class AccountLogin(BaseModel):
    """Model untuk user login - simplified untuk login form."""

    username: str = Field(min_length=3, max_length=50, description="Username")
    password: str = Field(min_length=6, description="Password")
    model_config = ConfigDict(str_strip_whitespace=True)


class ActiveSession(BaseModel):
    """Model untuk active user session."""

    user_id: int = Field(gt=0, description="User ID")
    username: str = Field(description="Username")
    name: str = Field(description="Name")
    role_id: int = Field(description="Role ID")
    role_name: str | None = Field(None, description="Role name")
    login_time: datetime = Field(default_factory=datetime.now)
    session_token: str | None = Field(None, description="Database session token")
    model_config = ConfigDict(from_attributes=True)


class LoginResult(OperationResult):
    """Model untuk login operation result."""

    user_session: ActiveSession | None = Field(
        default=None, description="Session data jika berhasil"
    )
    error_message: str | None = Field(
        default=None, description="Error message jika gagal"
    )
