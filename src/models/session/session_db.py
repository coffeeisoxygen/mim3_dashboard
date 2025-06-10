"""Database session models untuk audit dan security."""

from __future__ import annotations

import secrets
from datetime import datetime, timedelta

from pydantic import BaseModel, ConfigDict, Field


class SessionCreate(BaseModel):
    """Model untuk create session di database."""

    user_id: int = Field(gt=0, description="User ID")
    ip_address: str | None = Field(None, max_length=45, description="Client IP")
    user_agent: str | None = Field(None, max_length=500, description="Browser info")
    expires_at: datetime = Field(description="Session expiry time")

    @classmethod
    def create_new(cls, user_id: int, hours: int = 8) -> SessionCreate:
        """Create new session with auto-generated expiry."""
        return cls(
            user_id=user_id,
            ip_address=None,
            user_agent=None,
            expires_at=datetime.now() + timedelta(hours=hours),
        )


class SessionToken(BaseModel):
    """Model untuk session token generation."""

    session_token: str = Field(description="Unique session identifier")

    @classmethod
    def generate(cls) -> SessionToken:
        """Generate secure session token."""
        token = secrets.token_urlsafe(32)
        return cls(session_token=token)


class SessionRead(BaseModel):
    """Model untuk read session dengan user data."""

    id: int = Field(description="Session ID")
    user_id: int = Field(description="User ID")
    session_token: str = Field(description="Session token")
    ip_address: str | None = Field(description="Client IP")
    user_agent: str | None = Field(description="Browser info")
    expires_at: datetime = Field(description="Expiry time")
    last_activity: datetime = Field(description="Last activity")
    is_active: bool = Field(description="Session status")

    # JOIN fields from user & role
    username: str = Field(description="Username")
    name: str = Field(description="Full name")
    role_name: str = Field(description="Role name")

    model_config = ConfigDict(from_attributes=True)


class SessionView(BaseModel):
    """Model untuk display active sessions."""

    id: int = Field(description="Session ID")
    user_id: int = Field(description="User ID")
    session_token: str = Field(description="Session token")
    created_at: datetime = Field(description="Created time")
    expires_at: datetime = Field(description="Expiry time")
    last_activity: datetime = Field(description="Last activity")
    is_active: bool = Field(description="Session status")
    model_config = ConfigDict(from_attributes=True)


class SessionResult(BaseModel):
    """Model untuk session operation results."""

    success: bool = Field(description="Operasi berhasil")
    session_id: int | None = Field(None, description="Session ID if success")
    message: str = Field(description="Result message")
