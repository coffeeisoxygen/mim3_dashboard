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

    def perform_login_headless(
        self, username: str, password: str
    ) -> tuple[bool, ActiveSession | None, str]:
        """Perform login tanpa Streamlit dependencies - untuk API usage.

        Returns:
            tuple[bool, ActiveSession | None, str]: (success, session_data, message)
        """
        try:
            logger.debug(f"Headless auth: performing login for {username}")

            # Step 1: Get user from database
            user = get_user_by_username(username)
            logger.debug(f"User found: {user is not None}")

            if not user:
                logger.debug("User not found in database")
                return False, None, "Username atau password salah"

            # Step 2: Verify password
            logger.debug("Verifying password...")
            if not self.verify_password(password, user.password_hash):
                logger.debug("Password verification failed")
                return False, None, "Username atau password salah"

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

            # Step 4: Save session to database
            session_service = SessionService()
            session_result = session_service.create_user_session(
                user_session,
                {"ip_address": "127.0.0.1", "user_agent": "API Client"},
            )

            if not session_result.success:
                logger.error(f"Session creation failed: {session_result.message}")
                return False, None, "Error saat membuat session"

            # Step 5: Update session dengan token
            user_session.session_token = session_result.token

            logger.info(f"Headless login successful: {username}")
            return True, user_session, AuthMessages.LOGIN_SUCCESS

        except Exception as e:
            logger.error(f"Headless auth service error: {e}")
            return False, None, "Terjadi kesalahan sistem"

    def perform_login(self, username: str, password: str) -> tuple[bool, str]:
        """Perform login dengan Streamlit UI integration."""
        try:
            # Use headless login as base
            success, user_session, message = self.perform_login_headless(
                username, password
            )

            if not success or not user_session:
                return success, message

            # UI-specific steps
            logger.debug("Setting up Streamlit session state...")

            # ✅ Step 5: Set UI session state dengan token
            from models.session.session_st import set_user_session

            set_user_session(user_session)

            # ✅ Step 6: Set query params untuk browser refresh protection
            if user_session.session_token:
                st.query_params["session"] = user_session.session_token
            else:
                logger.warning("Session token is None, skipping query params")

            logger.info(f"UI login successful with session restoration: {username}")
            return True, AuthMessages.LOGIN_SUCCESS

        except Exception as e:
            logger.error(f"UI auth service error: {e}")
            return False, "Terjadi kesalahan sistem"

    def perform_logout(self) -> tuple[bool, str]:
        """Handle complete logout flow dengan enhanced logging."""
        try:
            # ✅ Use SessionRestorationManager untuk complete cleanup
            from services.session_restore_manager import get_session_restoration_manager

            session_token = st.session_state.get("session_token")
            restore_manager = get_session_restoration_manager()

            # Clear both UI state dan database session
            success = restore_manager.clear_session_state(session_token)

            # ✅ Clear query params
            st.query_params.clear()

            if success:
                # Enhanced logging dengan session token info
                token_info = session_token[:10] + "..." if session_token else "no-token"
                logger.info(f"Logout success: {token_info}")
                return True, AuthMessages.LOGOUT_SUCCESS

            logger.warning(
                f"Logout failed for session: {session_token[:10] + '...' if session_token else 'no-token'}"
            )
            return False, "Logout gagal"

        except Exception as e:
            logger.error(f"Logout error: {e}")
            return False, AuthMessages.SYSTEM_ERROR
