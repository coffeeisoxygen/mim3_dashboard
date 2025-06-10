"""Authentication journey schemas - login, session, logout flow."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AccountLogin(BaseModel):
    """Model untuk user login."""

    username: str = Field(min_length=3, max_length=50, description="Username")
    password: str = Field(min_length=6, description="Password")
    model_config = ConfigDict(str_strip_whitespace=True)


class ActiveSession(BaseModel):
    """Model untuk active user session."""

    user_id: int = Field(gt=0, description="User ID")
    username: str = Field(description="Username")
    name: str = Field(description="Nama lengkap user")
    role_id: int = Field(gt=0, description="Role ID dari database")
    role_name: str = Field(description="Display role name dari database")
    login_time: datetime = Field(default_factory=datetime.now)
    session_token: str | None = Field(
        None, description="Database session token"
    )  # ✅ Tambah ini
    model_config = ConfigDict(from_attributes=True)


class LoginResult(BaseModel):
    """Model untuk login operation result."""

    success: bool = Field(description="Login berhasil atau tidak")
    user_session: ActiveSession | None = Field(
        default=None, description="Session data jika berhasil"
    )
    error_message: str | None = Field(
        default=None, description="Error message jika gagal"
    )
