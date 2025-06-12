"""User role models dan role management - complete role domain."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

# ✅ Move from user_commons.py untuk cohesion
UserRole = Literal["admin", "staff", "support"]

# ================================
# Role Business Rules & Configuration
# ================================


@dataclass(frozen=True)
class RoleDefinition:
    """Core role definition dengan business rules."""

    name: UserRole
    description: str
    can_deactivate: bool = True  # Business rule
    min_required: int = 1  # Minimum users required
    permissions: list[str] = field(default_factory=list)  # Permission list


# ✅ Business rules definition - moved from commons
SYSTEM_ROLES: tuple[RoleDefinition, ...] = (
    RoleDefinition(
        name="admin",
        description="Owner MIM3 - Full System Access",
        can_deactivate=False,  # ✅ Protected role
        min_required=1,
        permissions=["*"],  # Full access
    ),
    RoleDefinition(
        name="staff",
        description="Karyawan MIM3 - Daily Operations",
        can_deactivate=True,
        min_required=0,
        permissions=["read", "write", "update", "dashboard"],
    ),
    RoleDefinition(
        name="support",
        description="Tim Indosat - Monitoring & Reports",
        can_deactivate=True,
        min_required=0,
        permissions=["read", "dashboard", "export"],
    ),
)

# ================================
# Role Pydantic Models
# ================================


class RoleModel(BaseModel):
    """Pydantic model untuk role database operations."""

    id: int = Field(gt=0, description="Role ID")
    name: UserRole = Field(description="Role name")
    description: str = Field(
        min_length=5, max_length=200, description="Role description"
    )
    permissions: list[str] = Field(default_factory=list, description="Permission list")
    is_system_role: bool = Field(
        default=False, description="System role (cannot be deleted)"
    )
    is_active: bool = Field(default=True, description="Role active status")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime | None = Field(None, description="Last update timestamp")
    model_config = ConfigDict(from_attributes=True)


class RoleAssignment(BaseModel):
    """User role assignment tracking."""

    user_id: int = Field(gt=0, description="User ID")
    role_id: int = Field(gt=0, description="Role ID")
    assigned_by: int = Field(gt=0, description="Admin user ID who assigned")
    assigned_at: datetime = Field(description="Assignment timestamp")
    reason: str | None = Field(None, max_length=500, description="Assignment reason")
    model_config = ConfigDict(from_attributes=True)


class RoleOperationResult(BaseModel):
    """Result untuk role operations dengan user impact awareness."""

    success: bool = Field(description="Operation berhasil atau tidak")
    message: str = Field(description="Pesan hasil operation")
    affected_users_count: int = Field(
        default=0, description="Jumlah user yang terpengaruh"
    )
    can_proceed: bool = Field(description="Apakah operation bisa dilanjutkan")
    warning_message: str | None = Field(None, description="Warning untuk admin")
    role: RoleModel | None = Field(None, description="Role data if successful")


# ================================
# Role Business Logic Functions
# ================================


def get_role_names() -> list[UserRole]:
    """Get list of valid role names."""
    return [role.name for role in SYSTEM_ROLES]


def get_role_definition(role_name: UserRole) -> RoleDefinition | None:
    """Get role definition by name."""
    for role in SYSTEM_ROLES:
        if role.name == role_name:
            return role
    return None


def can_deactivate_role(role_name: UserRole) -> bool:
    """Check if role can be deactivated based on business rules."""
    role_def = get_role_definition(role_name)
    return role_def.can_deactivate if role_def else False


def get_role_permissions(role_name: UserRole) -> list[str]:
    """Get permissions for specific role."""
    role_def = get_role_definition(role_name)
    return role_def.permissions if role_def else []


def is_role_change_allowed(
    from_role: UserRole,  # noqa: ARG001
    to_role: UserRole,
    admin_role: UserRole,
) -> bool:
    """Check if role change is allowed berdasarkan business rules."""
    # Admin bisa change any role
    if admin_role == "admin":
        return True

    # Non-admin tidak bisa promote ke admin
    if to_role == "admin":
        return False

    return True


def _get_role_model_by_name(role_name: UserRole) -> RoleModel | None:
    """Helper function to get RoleModel by role name."""
    return RoleFactory.get_role_by_name(role_name)


def check_role_deactivation_impact(
    role_name: UserRole, active_users_count: int = 0
) -> RoleOperationResult:
    """Check impact sebelum deactivate role - force admin awareness."""
    role_model = _get_role_model_by_name(role_name)

    if not can_deactivate_role(role_name):
        return RoleOperationResult(
            success=False,
            message=f"Role '{role_name}' tidak bisa di-deactivate (protected role)",
            affected_users_count=0,
            can_proceed=False,
            warning_message="Admin dan minimum required roles tidak bisa di-deactivate",
            role=role_model,
        )

    if active_users_count > 0:
        return RoleOperationResult(
            success=False,
            message=f"Role '{role_name}' masih digunakan oleh {active_users_count} user aktif",
            affected_users_count=active_users_count,
            can_proceed=False,
            warning_message=f"Deactivate {active_users_count} users terlebih dahulu sebelum deactivate role",
            role=role_model,
        )

    return RoleOperationResult(
        success=True,
        message=f"Role '{role_name}' dapat di-deactivate",
        affected_users_count=0,
        can_proceed=True,
        warning_message=None,
        role=role_model,
    )


def get_default_registration_role() -> UserRole:
    """Get default role untuk new user registration."""
    return "support"  # Business rule: new users default to support


def validate_role_permissions(role_name: UserRole, required_permission: str) -> bool:
    """Validate if role has required permission."""
    permissions = get_role_permissions(role_name)

    # Admin has all permissions
    if "*" in permissions:
        return True

    return required_permission in permissions


# ================================
# Role Factory & Utilities
# ================================


class RoleFactory:
    """Factory untuk create role objects."""

    @staticmethod
    def create_system_roles() -> list[RoleModel]:
        """Create system roles untuk database seeding."""
        roles = []
        for i, role_def in enumerate(SYSTEM_ROLES, 1):
            roles.append(
                RoleModel(
                    id=i,
                    name=role_def.name,
                    description=role_def.description,
                    permissions=role_def.permissions,
                    is_system_role=True,
                    is_active=True,
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                )
            )
        return roles

    @staticmethod
    def get_role_by_name(role_name: UserRole) -> RoleModel | None:
        """Get role model by name."""
        role_def = get_role_definition(role_name)
        if not role_def:
            return None

        # Default IDs untuk system roles
        role_ids = {"admin": 1, "staff": 2, "support": 3}

        return RoleModel(
            id=role_ids.get(role_name, 0),
            name=role_def.name,
            description=role_def.description,
            permissions=role_def.permissions,
            is_system_role=True,
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )


# REMINDER: Complete role domain logic dalam 1 module untuk better cohesion
# TODO: Add permission checking middleware untuk service layer
# PINNED: System roles (admin, staff, support) cannot be deleted
# PINNED: All role business logic centralized untuk maintainability
