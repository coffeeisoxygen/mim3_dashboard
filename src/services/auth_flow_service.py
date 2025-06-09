"""Authentication flow service - handle complete auth business logic."""

from __future__ import annotations

import streamlit as st
from loguru import logger

from core.messages import AuthMessages
from core.session.manager import SessionManager
from models.md_user import UserLogin


class AuthFlowService:
    """Handle authentication flow - pure business logic."""

    def __init__(self):
        """Initialize dengan auth service."""
        from .auth_service import AuthService

        self.auth_service = AuthService()

    def perform_login(self, username: str, password: str) -> tuple[bool, str]:
        """Handle complete login flow - no UI dependencies.

        Args:
            username: User's username
            password: User's password

        Returns:
            Tuple of (success: bool, message: str)
        """
        # ✅ Consistent validation message
        if not username or not password:
            return False, AuthMessages.REQUIRED_FIELDS

        try:
            # ✅ Authentication logic
            login_data = UserLogin(username=username, password=password)
            result = self.auth_service.authenticate(login_data)

            if result.success and result.user_session:
                # ✅ Session management logic
                SessionManager.login(
                    user_id=result.user_session.user_id,
                    username=result.user_session.username,
                    role=result.user_session.role,
                )
                return True, AuthMessages.LOGIN_SUCCESS  # ✅ Consistent
            else:
                return False, result.error_message or AuthMessages.LOGIN_FAILED

        except Exception as e:
            logger.error(f"Login error: {e}")
            return False, AuthMessages.SYSTEM_ERROR  # ✅ Consistent

    def perform_logout(self) -> tuple[bool, str]:
        """Handle complete logout flow - no UI dependencies.

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            username = st.session_state.get("username", "User")
            SessionManager.logout()
            return True, f"{username} {AuthMessages.LOGOUT_SUCCESS}"  # ✅ Consistent
        except Exception as e:
            logger.error(f"Logout error: {e}")
            return False, AuthMessages.SYSTEM_ERROR  # ✅ Consistent
