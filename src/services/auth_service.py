"""Authentication service untuk MIM3 Dashboard."""

from __future__ import annotations

import bcrypt
import streamlit as st
from loguru import logger

from core.messages import AuthMessages
from database.commands.auth_commands import get_user_by_username
from database.commands.user_commands import get_user_by_id
from models.user.user_auth import ActiveSession
from services.session_service import SessionService


class AuthService:
    """Service untuk menangani complete authentication flow."""

    @staticmethod
    def verify_password(raw_password: str, stored_hash: str) -> bool:
        """Verify raw password against stored bcrypt hash."""
        return bcrypt.checkpw(
            raw_password.encode("utf-8"),
            stored_hash.encode("utf-8"),
        )

    @staticmethod
    def verify_user_password(user_id: int, raw_password: str) -> bool:
        """Verify password for specific user - untuk admin operations."""
        user_data = get_user_by_id(user_id)
        if not user_data:
            return False
        return AuthService.verify_password(raw_password, user_data.password_hash)

    def perform_login(self, username: str, password: str) -> tuple[bool, str]:
        """Handle complete login flow."""
        # Basic validation
        if not username or not password:
            return False, AuthMessages.REQUIRED_FIELDS

        try:
            # Get user data
            user_data = get_user_by_username(username)
            if not user_data:
                return False, AuthMessages.LOGIN_FAILED

            # Verify password
            if not self.verify_password(password, user_data.password_hash):
                logger.warning(f"Invalid password: {username}")
                return False, AuthMessages.LOGIN_FAILED

            # Create session
            user_session = ActiveSession(
                user_id=user_data.id,
                username=user_data.username,
                name=user_data.name,
                role_id=user_data.role_id,
                role_name=user_data.role_name,
                session_token=None,
            )

            # Save session
            session_service = SessionService()
            session_result = session_service.create_user_session(
                user_session,
                {"ip_address": "127.0.0.1", "user_agent": "Streamlit Dashboard"},
            )

            if not session_result.success:
                return False, session_result.message

            logger.info(f"Login successful: {username}")
            return True, AuthMessages.LOGIN_SUCCESS

        except Exception as e:
            logger.error(f"Login error: {e}")
            return False, AuthMessages.SYSTEM_ERROR

    def perform_logout(self) -> tuple[bool, str]:
        """Handle complete logout flow."""
        try:
            session_token = st.session_state.get("session_token")
            session_service = SessionService()
            success = session_service.clear_user_session(session_token)

            if success:
                logger.info("Logout successful")
                return True, AuthMessages.LOGOUT_SUCCESS
            return False, "Logout gagal"

        except Exception as e:
            logger.error(f"Logout error: {e}")
            return False, AuthMessages.SYSTEM_ERROR
