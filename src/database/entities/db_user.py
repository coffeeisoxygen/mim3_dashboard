"""User dan Role models - simple and clean."""

from __future__ import annotations

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class untuk semua models."""

    pass


class User(Base):
    """User model - essential fields only."""

    __tablename__ = "user_account"

    # Core fields
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(50), index=True)
    password_hash: Mapped[str] = mapped_column(String(255))  # Safe untuk bcrypt
    is_verified: Mapped[bool] = mapped_column(default=False, index=True)

    # Foreign key
    role_id: Mapped[int] = mapped_column(ForeignKey("role.id", ondelete="RESTRICT"))

    # Audit fields
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), default=func.now()
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now()
    )

    # Relationship
    role: Mapped[Role] = relationship("Role", back_populates="users")

    @hybrid_property
    def display_name(self) -> str:
        """Display name untuk UI."""
        return f"{self.name} ({self.username})"


class Role(Base):
    """Role model - essential fields only."""

    __tablename__ = "role"

    # Core fields
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Audit fields
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), default=func.now()
    )

    # Relationship
    users: Mapped[list[User]] = relationship("User", back_populates="role")
