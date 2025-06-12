"""Database session models - pure session concerns, decoupled from user domain."""

from __future__ import annotations

import secrets
from datetime import datetime, timedelta

from pydantic import BaseModel, ConfigDict, Field


class DatabaseSession(BaseModel):
    """Core database session model - minimal dependencies."""

    user_id: int = Field(gt=0, description="User ID reference")
    session_token: str = Field(description="Unique session token")
    ip_address: str | None = Field(None, max_length=45, description="Client IP")
    user_agent: str | None = Field(None, max_length=500, description="Browser info")
    expires_at: datetime = Field(description="Session expiry time")
    created_at: datetime = Field(default_factory=datetime.now)
    last_activity: datetime = Field(default_factory=datetime.now)
    is_active: bool = Field(default=True, description="Session status")

    @classmethod
    def create_new(
        cls, user_id: int, hours: int = 8, request_info: dict | None = None
    ) -> DatabaseSession:
        """Factory untuk create session dengan auto-generated token."""
        current_time = datetime.now()

        return cls(
            user_id=user_id,
            session_token=secrets.token_urlsafe(32),
            ip_address=request_info.get("ip_address") if request_info else None,
            user_agent=request_info.get("user_agent") if request_info else None,
            expires_at=current_time + timedelta(hours=hours),
            created_at=current_time,
            last_activity=current_time,
        )

    def is_idle(self, idle_hours: int = 8) -> bool:
        """Check if session is idle beyond threshold."""
        if not self.last_activity:
            return True

        idle_duration = datetime.now() - self.last_activity
        return idle_duration > timedelta(hours=idle_hours)

    def update_activity(self) -> None:
        """Update last activity timestamp."""
        self.last_activity = datetime.now()

    model_config = ConfigDict(str_strip_whitespace=True)


class SessionCreate(BaseModel):
    """Model untuk create session operation - simplified."""

    user_id: int = Field(gt=0, description="User ID")
    session_token: str = Field(description="Unique session token")
    ip_address: str | None = Field(None, max_length=45)
    user_agent: str | None = Field(None, max_length=500)
    expires_at: datetime = Field(description="Session expiry time")

    @classmethod
    def create_new(
        cls, user_id: int, hours: int = 8, request_info: dict | None = None
    ) -> SessionCreate:
        """Create new session dengan auto-generated token."""
        current_time = datetime.now()

        return cls(
            user_id=user_id,
            session_token=secrets.token_urlsafe(32),
            ip_address=request_info.get("ip_address") if request_info else None,
            user_agent=request_info.get("user_agent") if request_info else None,
            expires_at=current_time + timedelta(hours=hours),
        )

    model_config = ConfigDict(str_strip_whitespace=True)


class SessionValidation(BaseModel):
    """Session validation result - minimal user data."""

    is_valid: bool = Field(description="Session valid")
    is_expired: bool = Field(description="Session expired")
    user_id: int | None = Field(None, description="User ID if valid")
    username: str | None = Field(None, description="Username if valid")
    role_name: str | None = Field(None, description="Role name if valid")
    message: str = Field(default="", description="Validation message")

    @classmethod
    def invalid_session(cls, reason: str = "Session tidak valid") -> SessionValidation:
        """Helper untuk invalid session."""
        return cls(
            is_valid=False,
            is_expired=False,
            user_id=None,
            username=None,
            role_name=None,
            message=reason,
        )

    @classmethod
    def expired_session(cls) -> SessionValidation:
        """Helper untuk expired session."""
        return cls(
            is_valid=False,
            is_expired=True,
            user_id=None,
            username=None,
            role_name=None,
            message="Session expired",
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
            message="Session valid",
        )


class SessionResult(BaseModel):
    """Session operation result - focused on session data."""

    success: bool = Field(description="Operasi berhasil")
    session_id: int | None = Field(None, description="Session ID if success")
    token: str | None = Field(None, description="Session token if success")
    message: str = Field(description="Result message")

    @classmethod
    def success_result(
        cls, session_id: int, token: str, message: str = "Session berhasil dibuat"
    ) -> SessionResult:
        """Helper untuk success result."""
        return cls(success=True, session_id=session_id, token=token, message=message)

    @classmethod
    def error_result(cls, message: str) -> SessionResult:
        """Helper untuk error result."""
        return cls(
            success=False,
            session_id=None,
            token=None,
            message=message,
        )


# TODO: User-session relationship models should be in user domain
# [ ] PINNED: SessionValidation still has minimal user data for compatibility
