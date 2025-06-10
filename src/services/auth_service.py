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
        """Perform login dengan enhanced error logging."""
        try:
            logger.debug(f"Auth service: performing login for {username}")

            # Step 1: Get user from database
            user = get_user_by_username(username)  # ← Check ini dulu
            logger.debug(f"User found: {user is not None}")

            if not user:
                logger.debug("User not found in database")
                return False, "Username atau password salah"

            # Step 2: Verify password
            logger.debug("Verifying password...")
            if not self.verify_password(password, user.password_hash):
                logger.debug("Password verification failed")
                return False, "Username atau password salah"

            # Step 3: Create session
            logger.debug("Creating user session...")
            user_session = ActiveSession(
                user_id=user.id,
                username=user.username,
                name=user.name,
                role_id=user.role_id,
                role_name=user.role_name,
                session_token=None,
            )

            # Save session
            session_service = SessionService()
            session_result = session_service.create_user_session(
                user_session,
                {"ip_address": "127.0.0.1", "user_agent": "Streamlit Dashboard"},
            )
            logger.debug(f"Session creation result: {session_result.success}")

            # ✅ Enhanced logging untuk debug session creation
            if not session_result.success:
                logger.error(f"Session creation failed: {session_result.message}")
                logger.error(
                    f"Session error details: {session_result}"
                )  # ← Debug detail
                return False, "Error saat membuat session"

            logger.info(f"Login successful: {username}")
            return True, AuthMessages.LOGIN_SUCCESS

        except Exception as e:
            logger.error(f"Auth service error: {e}")
            return False, "Terjadi kesalahan sistem"  # ← Generic error

    def perform_logout(self) -> tuple[bool, str]:
        """Handle complete logout flow."""
        try:
            session_token = st.session_state.get("session_token")
            session_service = SessionService()
            success = session_service.clear_session(session_token)

            if success:
                logger.info("Logout successful")
                return True, AuthMessages.LOGOUT_SUCCESS
            return False, "Logout gagal"

        except Exception as e:
            logger.error(f"Logout error: {e}")
            return False, AuthMessages.SYSTEM_ERROR
