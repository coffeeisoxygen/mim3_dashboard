"""Seeder nilai default untuk sistem - centralized configuration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True)
class SystemRole:
    """Model untuk system roles yang wajib ada."""

    name: str
    description: str


@dataclass(frozen=True)
class SystemUser:
    """Model untuk system users yang wajib ada."""

    username: str
    name: str
    password: str
    role_name: str


@dataclass(frozen=True)
class SystemSeeder:
    """Centralized seeder untuk semua default system values."""

    # Required system roles
    REQUIRED_ROLES: ClassVar[list[SystemRole]] = [
        SystemRole(name="admin", description="Owner MIM3 - Full System Access"),
        SystemRole(name="operator", description="Operator Harian - CRUD Operations"),
        SystemRole(name="support", description="Tim Support - Read & Report Access"),
    ]

    # Default admin account
    DEFAULT_ACCOUNT: ClassVar[SystemUser] = SystemUser(
        username="admin",
        name="Default Administrator",
        password="admin123",  # noqa: S106
        role_name="admin",
    )

    DEMO_ACCOUNT: ClassVar[list[SystemUser]] = [
        SystemUser(
            username="operator1",
            name="Demo Operator",
            password="demo123",  # noqa: S106
            role_name="operator",
        ),
        SystemUser(
            username="operator2",
            name="Demo Operator 2",
            password="demo123",  # noqa: S106
            role_name="operator",
        ),
        SystemUser(
            username="support1",
            name="Demo Support",
            password="demo123",  # noqa: S106
            role_name="support",
        ),
    ]
