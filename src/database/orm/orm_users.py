"""SQLAlchemy Entities untuk User Management System."""

# Ruff: noqa D105
from __future__ import annotations

import secrets
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base


class RoleORM(Base):
    """Role entity untuk permission management."""

    __tablename__ = "role"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    description: Mapped[str | None] = mapped_column(String(255))

    # Relationship ke users
    users: Mapped[list[UserAccountORM]] = relationship(
        "UserAccountORM", back_populates="role"
    )

    def __repr__(self) -> str:  # noqa: D105
        return f"<RoleORM(id={self.id}, name='{self.name}')>"

    def __str__(self) -> str:  # noqa: D105
        return self.name


class UserAccountORM(Base):
    """User account entity dengan auto datetime conversion."""

    __tablename__ = "user_account"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    name: Mapped[str] = mapped_column(String(50))
    password_hash: Mapped[str] = mapped_column(String(255))
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("role.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime)
    updated_at: Mapped[datetime] = mapped_column(DateTime)

    # Bidirectional relationships
    role: Mapped[RoleORM] = relationship("RoleORM", back_populates="users")
    sessions: Mapped[list[UserSessionORM]] = relationship(
        "UserSessionORM", back_populates="user"
    )

    def __repr__(self) -> str:  # noqa: D105
        return f"<UserAccountORM(id={self.id}, username='{self.username}')>"

    def __str__(self) -> str:  # noqa: D105
        return self.username


class UserSessionORM(Base):
    """User session entity dengan auto datetime conversion."""

    __tablename__ = "user_session"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
    session_token: Mapped[str] = mapped_column(String(255), unique=True)
    ip_address: Mapped[str | None] = mapped_column(String(45))
    user_agent: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime)
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    last_activity: Mapped[datetime] = mapped_column(DateTime)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationship ke user
    user: Mapped[UserAccountORM] = relationship(
        "UserAccountORM", back_populates="sessions"
    )

    @classmethod
    def create_new_session(
        cls, user_id: int, hours: int = 8, request_info: dict | None = None
    ) -> UserSessionORM:
        """Factory method untuk create session dengan proper datetime."""
        from database.commons import DateTimeUtils

        now = DateTimeUtils.now_local()

        return cls(
            user_id=user_id,
            session_token=secrets.token_urlsafe(32),
            ip_address=request_info.get("ip_address") if request_info else None,
            user_agent=request_info.get("user_agent") if request_info else None,
            created_at=now,
            expires_at=DateTimeUtils.expires_in_hours(hours),
            last_activity=now,
            is_active=True,
        )

    def is_expired(self) -> bool:
        """Check if session sudah expired."""
        from database.commons import DateTimeUtils

        return DateTimeUtils.is_expired(self.expires_at)

    def refresh_activity(self) -> None:
        """Update last activity timestamp."""
        from database.commons import DateTimeUtils

        self.last_activity = DateTimeUtils.now_local()

    def __repr__(self) -> str:  # noqa: D105
        return f"<UserSessionORM(id={self.id}, token='{self.session_token[:10]}...')>"


# TODO: Hapus file ent_roles.py dan ent_usersession.py setelah refactor selesai
# REMINDER: Update import di file lain yang menggunakan RoleORM atau UserSessionORM
