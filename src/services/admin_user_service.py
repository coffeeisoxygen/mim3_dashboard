"""Service admin untuk CRUD user operations - thin business logic layer."""

# ruff: noqa
from __future__ import annotations

from functools import wraps

import streamlit as st
from loguru import logger

from database.commands.user_commands import (
    activate_user as cmd_activate_user,
)
from database.commands.user_commands import (
    create_user as cmd_create_user,
)
from database.commands.user_commands import (
    deactivate_user as cmd_deactivate_user,
)
from database.commands.user_commands import (
    delete_user as cmd_delete_user,
)
from database.commands.user_commands import (
    get_all_users as cmd_get_all_users,
)
from database.commands.user_commands import (
    get_user_by_id as cmd_get_user_by_id,
)
from database.commands.user_commands import (
    update_user as cmd_update_user,
)
from models.user.user_commons import OperationResult
from models.user.user_models import User, UserCreate, UserListItem, UserUpdate
from services.auth_service import AuthService


def require_admin_auth(require_password: bool = True):
    """Decorator untuk admin authentication dengan configurable security level."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Layer 1: Session check - always required
            if not _verify_admin_session():
                return OperationResult(
                    success=False, message="Session tidak valid atau bukan admin"
                )

            # Layer 2: Password check - configurable
            if require_password:
                admin_password = kwargs.get("admin_password")
                if not admin_password:
                    return OperationResult(
                        success=False, message="Admin password diperlukan"
                    )

                if not _verify_admin_password(admin_password):
                    return OperationResult(
                        success=False, message="Admin password tidak valid"
                    )

                # Remove password dari kwargs sebelum call function
                kwargs.pop("admin_password", None)

            return func(*args, **kwargs)

        return wrapper

    return decorator


class AdminUserService:
    """Service untuk admin manage users - business logic only."""

    @staticmethod
    def get_all_users() -> list[UserListItem]:
        """Get semua users untuk admin listing - no auth required for read."""
        logger.debug("AdminUserService: Getting all users")
        return cmd_get_all_users()

    @staticmethod
    def get_user_by_id(user_id: int) -> User | None:
        """Get user by ID untuk detail/edit - no auth required for read."""
        logger.debug(f"AdminUserService: Getting user {user_id}")
        return cmd_get_user_by_id(user_id)

    @staticmethod
    @require_admin_auth(require_password=True)
    def create_user(user_data: UserCreate, admin_password: str) -> OperationResult:  # noqa: ARG004
        """Admin create user - requires password confirmation."""
        logger.info(f"AdminUserService: Creating user {user_data.username}")
        return cmd_create_user(user_data)

    @staticmethod
    @require_admin_auth(require_password=False)
    def update_user(user_id: int, user_data: UserUpdate) -> OperationResult:
        """Update user - session only, no password required."""
        logger.info(f"AdminUserService: Updating user {user_id}")
        return cmd_update_user(user_id, user_data)

    @staticmethod
    @require_admin_auth(require_password=False)
    def soft_delete_user(user_id: int) -> OperationResult:
        """Soft delete user - session only."""
        logger.info(f"AdminUserService: Soft deleting user {user_id}")
        return cmd_deactivate_user(user_id)

    @staticmethod
    @require_admin_auth(require_password=True)
    def hard_delete_user(user_id: int, admin_password: str) -> OperationResult:
        """Hard delete user - requires password confirmation."""
        logger.warning(f"AdminUserService: Hard deleting user {user_id}")
        return cmd_delete_user(user_id)

    @staticmethod
    @require_admin_auth(require_password=True)
    def activate_user(user_id: int, admin_password: str) -> OperationResult:
        """Activate user - requires password confirmation."""
        logger.info(f"AdminUserService: Activating user {user_id}")
        return cmd_activate_user(user_id)


def _verify_admin_session() -> bool:
    """Layer 1: Quick session validation."""
    user_role = st.session_state.get("user_role")
    return user_role == "admin"


def _verify_admin_password(password: str) -> bool:
    """Layer 2: Password verification - delegate ke AuthService."""
    user_id = st.session_state.get("user_id")
    if not user_id:
        return False
    return AuthService.verify_user_password(user_id, password)
