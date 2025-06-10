"""Model untuk seeding initial data ke database."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True)
class RequiredRole:
    """Model untuk role yang wajib ada di system."""

    name: str
    description: str
    role_id: int


@dataclass(frozen=True)
class DefaultUser:
    """Model untuk default admin user."""

    username: str
    name: str
    password: str
    role_id: int


@dataclass(frozen=True)
class DatabaseSeeder:
    """Seeder untuk initial database setup."""

    # Required roles - immutable system roles
    REQUIRED_ROLES: ClassVar[list[RequiredRole]] = [
        RequiredRole(
            name="admin", description="Owner MIM3 - Full System Access", role_id=1
        ),
        RequiredRole(
            name="operator", description="Operator Harian - CRUD Operations", role_id=2
        ),
        RequiredRole(
            name="support", description="Tim Support - Read & Report Access", role_id=3
        ),
    ]

    # Default admin user
    DEFAULT_ADMIN: ClassVar[DefaultUser] = DefaultUser(
        username="admin",
        name="Default Administrator",
        password="admin123",  # noqa: S106
        role_id=1,
    )

    # Demo accounts (optional - bisa dicontrol via environment)
    DEMO_USERS: ClassVar[list[DefaultUser]] = [
        DefaultUser(
            username="operator1",
            name="Demo Operator",
            password="demo123",  # noqa: S106
            role_id=2,
        ),
        DefaultUser(
            username="support1",
            name="Demo Support",
            password="demo123",  # noqa: S106
            role_id=3,
        ),
    ]
