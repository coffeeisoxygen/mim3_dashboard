"""Database session models untuk audit dan security."""

# ruff: noqa
from __future__ import annotations

import secrets
from datetime import datetime, timedelta

from pydantic import BaseModel, ConfigDict, Field


class SessionCreate(BaseModel):
    """Model untuk create session di database."""

    user_id: int = Field(gt=0, description="User ID")
    session_token: str = Field(description="Unique session token")
    ip_address: str | None = Field(None, max_length=45, description="Client IP")
    user_agent: str | None = Field(None, max_length=500, description="Browser info")
    expires_at: datetime = Field(description="Session expiry time")

    @classmethod
    def create_new(
        cls, user_id: int, hours: int = 8, request_info: dict | None = None
    ) -> SessionCreate:
        """Create new session dengan auto-generated token dan expiry."""
        return cls(
            user_id=user_id,
            session_token=secrets.token_urlsafe(32),  # Generate token di sini
            ip_address=request_info.get("ip_address") if request_info else None,
            user_agent=request_info.get("user_agent") if request_info else None,
            expires_at=datetime.now() + timedelta(hours=hours),
        )

    model_config = ConfigDict(str_strip_whitespace=True)


class SessionUpdate(BaseModel):
    """Model untuk update session activity."""

    last_activity: datetime = Field(
        default_factory=datetime.now, description="Last activity time"
    )
    is_active: bool | None = Field(None, description="Session status")

    model_config = ConfigDict(str_strip_whitespace=True)


class SessionRead(BaseModel):
    """Model untuk read session dengan user data - complete info."""

    id: int = Field(description="Session ID")
    user_id: int = Field(description="User ID")
    session_token: str = Field(description="Session token")
    ip_address: str | None = Field(description="Client IP")
    user_agent: str | None = Field(description="Browser info")
    created_at: datetime = Field(description="Created time")
    expires_at: datetime = Field(description="Expiry time")
    last_activity: datetime = Field(description="Last activity")
    is_active: bool = Field(description="Session status")

    # JOIN fields dari user & role
    username: str = Field(description="Username")
    name: str = Field(description="Full name")
    role_name: str = Field(description="Role name")

    model_config = ConfigDict(from_attributes=True)


class SessionListItem(BaseModel):
    """Model untuk listing sessions - minimal info."""

    id: int = Field(description="Session ID")
    username: str = Field(description="Username")
    ip_address: str | None = Field(description="Client IP")
    last_activity: datetime = Field(description="Last activity")
    is_active: bool = Field(description="Session status")

    model_config = ConfigDict(from_attributes=True)


class SessionResult(BaseModel):
    """Model untuk session operation results."""

    success: bool = Field(description="Operasi berhasil")
    session_id: int | None = Field(None, description="Session ID if success")
    message: str = Field(description="Result message")
    token: str | None = Field(None, description="Session token if success")

    @classmethod
    def success_result(
        cls, session_id: int, token: str, message: str = "Session berhasil dibuat"
    ) -> SessionResult:
        """Helper untuk create success result."""
        return cls(success=True, session_id=session_id, token=token, message=message)

    @classmethod
    def error_result(cls, message: str) -> SessionResult:
        """Helper untuk create error result."""
        return cls(
            success=False,
            session_id=None,  # ✅ Provide default None
            token=None,  # ✅ Provide default None
            message=message,
        )


class SessionValidation(BaseModel):
    """Model untuk session validation result."""

    is_valid: bool = Field(description="Session valid")
    is_expired: bool = Field(description="Session expired")
    user_id: int | None = Field(None, description="User ID if valid")
    username: str | None = Field(None, description="Username if valid")
    role_name: str | None = Field(None, description="Role name if valid")

    @classmethod
    def invalid_session(cls, reason: str = "Session tidak valid") -> SessionValidation:
        """Helper untuk invalid session."""
        return cls(
            is_valid=False,
            is_expired=False,
            user_id=None,
            username=None,
            role_name=None,
        )

    @classmethod
    def expired_session(cls) -> SessionValidation:
        """Helper untuk expired session."""
        return cls(
            is_valid=False, is_expired=True, user_id=None, username=None, role_name=None
        )

    @classmethod
    def valid_session(
        cls, user_id: int, username: str, role_name: str
    ) -> SessionValidation:
        """Helper untuk valid session."""
        return cls(
            is_valid=True,
            is_expired=False,
            user_id=user_id,
            username=username,
            role_name=role_name,
        )
