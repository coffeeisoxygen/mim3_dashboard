"""System seeder dengan business rules protection."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from models.user.user_role import SYSTEM_ROLES, RoleDefinition, UserRole


@dataclass(frozen=True)
class SystemUser:
    """Model untuk system users yang wajib ada."""

    username: str
    name: str
    password: str  # Will be hashed by service
    role_name: UserRole
    is_protected: bool = False  # Can't be deleted


@dataclass(frozen=True)
class SystemSeeder:
    """Centralized seeder dengan business protection."""

    # Default admin account - PROTECTED
    DEFAULT_ADMIN: ClassVar[SystemUser] = SystemUser(
        username="admin",
        name="Default Administrator",
        password="admin123",  # noqa: S106
        role_name="admin",
        is_protected=True,  # ✅ Can't delete this user
    )

    # Demo accounts untuk testing
    DEMO_ACCOUNTS: ClassVar[tuple[SystemUser, ...]] = (
        SystemUser(
            username="staff1",
            name="Demo Staff",
            password="demo123",  # noqa: S106
            role_name="staff",
        ),
        SystemUser(
            username="support1",
            name="Demo Support",
            password="demo123",  # noqa: S106
            role_name="support",
        ),
    )

    @classmethod
    def get_system_roles(cls) -> tuple[RoleDefinition, ...]:
        """Get system roles dari constants."""
        return SYSTEM_ROLES

    @classmethod
    def get_all_users(cls) -> list[SystemUser]:
        """Get semua default users."""
        return [cls.DEFAULT_ADMIN, *list(cls.DEMO_ACCOUNTS)]


# REMINDER: Static roles with business rules protection
# TODO: Service layer handle role deactivation cascade effects
# [ ] PINNED: Consider role hierarchy untuk future extensions
