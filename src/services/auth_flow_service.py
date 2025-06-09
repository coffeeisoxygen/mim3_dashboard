"""Authentication flow service - handle complete auth business logic."""

from __future__ import annotations

import streamlit as st
from loguru import logger

from core.messages import AuthMessages
from core.user_session import clear_user_session, set_user_session
from models.md_user import UserLogin


class AuthFlowService:
    """Handle authentication flow - pure business logic."""

    def __init__(self):
        """Initialize tanpa dependency injection."""
        self._auth_service = None

    @property
    def auth_service(self):
        """Lazy load auth service."""
        if self._auth_service is None:
            from .auth_service import AuthService

            self._auth_service = AuthService()
        return self._auth_service

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
                # ✅ Simple one-liner
                set_user_session(result.user_session)
                logger.info(f"User login: {result.user_session.username}")
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
            # ✅ Simple one-liner
            clear_user_session()
            logger.info(f"User logout: {username}")
            return True, f"{username} {AuthMessages.LOGOUT_SUCCESS}"  # ✅ Consistent
        except Exception as e:
            logger.error(f"Logout error: {e}")
            return False, AuthMessages.SYSTEM_ERROR  # ✅ Consistent
