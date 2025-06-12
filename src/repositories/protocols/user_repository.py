"""User repository protocol - interface untuk user data access."""

from __future__ import annotations

from typing import Protocol

from models.user.user_admin import (
    AdminUserCreate,
    AdminUserDeactivate,
    AdminUserDelete,
    AdminUserRoleChange,
)
from models.user.user_auth import UserActiveSession
from models.user.user_commons import OperationResult
from models.user.user_models import UserFilter
from models.user.user_role import UserRole


class UserRepository(Protocol):
    """Protocol untuk user data access - comprehensive business operations."""

    # ================================
    # Read Operations
    # ================================

    def get_user_by_id(self, user_id: int) -> dict | None:
        """Get user by ID - raw data for internal operations."""
        ...

    def get_user_by_username(self, username: str) -> dict | None:
        """Get user by username untuk authentication check."""
        ...

    def get_all_users(self, filter_params: UserFilter | None = None) -> list[dict]:
        """Get users dengan optional filtering."""
        ...

    def get_user_for_session(self, username: str) -> UserActiveSession | None:
        """Get user data untuk create session after successful auth."""
        ...

    # ================================
    # Authentication Operations
    # ================================

    def verify_password(self, user_id: int, password: str) -> bool:
        """Verify user password (BCrypt check)."""
        ...

    def update_last_login(self, user_id: int) -> bool:
        """Update last login timestamp."""
        ...

    # ================================
    # Basic CRUD Operations
    # ================================

    def create_user(self, data: AdminUserCreate, password_hash: str) -> dict | None:
        """Create new user dengan hashed password."""
        ...

    def update_user_basic_info(self, user_id: int, name: str | None = None) -> bool:
        """Update basic user info (name, etc)."""
        ...

    def update_user_password(self, user_id: int, new_password_hash: str) -> bool:
        """Update user password dengan new hash."""
        ...

    def delete_user(self, user_id: int) -> bool:
        """Hard delete user - permanent removal."""
        ...

    def set_user_active_status(self, user_id: int, is_active: bool) -> bool:
        """Activate/deactivate user."""
        ...

    def update_user_role(self, user_id: int, new_role_id: int) -> bool:
        """Update user role by role_id."""
        ...

    # ================================
    # ✅ ADMIN OPERATIONS (WITH VERIFICATION)
    # ================================

    def admin_delete_user(
        self, data: AdminUserDelete, admin_user_id: int
    ) -> OperationResult:
        """Hard delete user dengan admin password verification.

        Args:
            data: AdminUserDelete dengan user_id, admin_password, confirmation
            admin_user_id: ID admin yang melakukan operasi (for audit)

        Returns:
            OperationResult dengan success status dan message
        """
        ...

    def admin_deactivate_user(
        self, data: AdminUserDeactivate, admin_user_id: int
    ) -> OperationResult:
        """Deactivate user dengan admin verification.

        Args:
            data: AdminUserDeactivate dengan user_id, reason, admin_password
            admin_user_id: ID admin yang melakukan operasi

        Returns:
            OperationResult dengan success status dan message
        """
        ...

    def admin_change_user_role(
        self, data: AdminUserRoleChange, admin_user_id: int
    ) -> OperationResult:
        """Change user role dengan admin verification.

        Args:
            data: AdminUserRoleChange dengan user_id, new_role, admin_password, reason
            admin_user_id: ID admin yang melakukan operasi

        Returns:
            OperationResult dengan success status dan message
        """
        ...

    # ================================
    # Business Rules Support
    # ================================

    def count_active_users_by_role(self, role_name: UserRole) -> int:
        """Count active users in specific role - untuk role deactivation check."""
        ...

    def is_username_available(
        self, username: str, exclude_user_id: int | None = None
    ) -> bool:
        """Check if username is available for registration/update."""
        ...

    def is_user_protected(self, user_id: int) -> bool:
        """Check if user is protected (admin yang gak boleh dihapus)."""
        ...

    def get_admin_users(self) -> list[dict]:
        """Get all admin users untuk system validation."""
        ...

    # ✅ ADD: Admin verification support
    def verify_admin_password(self, admin_user_id: int, password: str) -> bool:
        """Verify admin password untuk admin operations."""
        ...

    def log_admin_operation(
        self,
        admin_user_id: int,
        operation: str,
        target_user_id: int | None = None,
        details: str | None = None,
    ) -> bool:
        """Log admin operation untuk audit trail."""
        ...

    # ================================
    # Role Management Support
    # ================================

    def get_role_by_name(self, role_name: UserRole) -> dict | None:
        """Get role data by name."""
        ...

    def get_role_by_id(self, role_id: int) -> dict | None:
        """Get role data by ID."""
        ...

    def create_role_if_not_exists(self, role_name: UserRole, description: str) -> bool:
        """Create role if doesn't exist (seeding)."""
        ...

    def is_role_in_use(self, role_name: UserRole) -> bool:
        """Check if role is currently assigned to any active user."""
        ...


# REMINDER: Repository returns raw dict data, Service layer handles model conversion
# TODO: Add audit logging methods untuk admin operations tracking
# PINNED: Password hashing handled in Service layer, not Repository
# PINNED: Business validation in Service layer, Repository just data access
# PINNED: Admin operations include verification + audit logging
# PINNED : REMINDER: Bisa refactor ke split pattern nanti kalau repository jadi terlalu complex atau ada team collaboration needs.
# Keep audit di Repository untuk simplicity
# Document sebagai "Repository + Audit hybrid pattern"
# Add comment: # TODO: Consider separating audit concerns
