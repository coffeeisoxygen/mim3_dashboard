"""Session restoration manager - UI orchestration layer."""

from __future__ import annotations

import streamlit as st
from loguru import logger

from models.session.session_st import clear_user_session, set_user_session
from models.user.user_auth import ActiveSession
from services.session_service import SessionService


class SessionRestorationManager:
    """Handle UI state restoration - coordinates service + UI state."""

    def __init__(self):
        self.session_service = SessionService()

    @logger.catch
    def restore_session_from_token(self, session_token: str) -> bool:
        """Restore Streamlit state dari database session."""
        try:
            logger.debug(f"Attempting session restoration: {session_token[:10]}...")

            # Step 1: Get validation data dari service
            validation = self.session_service.get_session_restoration_data(
                session_token
            )

            if not validation.is_valid:
                logger.warning("Cannot restore invalid session")
                return False

            # Step 2: Validate required fields are not None
            if not validation.user_id or not validation.username:
                logger.warning("Session validation missing required user data")
                return False

            # Step 3: Create ActiveSession untuk UI dengan safe values
            active_session = ActiveSession(
                user_id=validation.user_id,
                username=validation.username,
                name=validation.username,  # TODO: Get actual display name
                role_id=getattr(validation, "role_id", 0),  # Safe access
                role_name=validation.role_name or "unknown",  # Safe default
                session_token=session_token,
            )

            # Step 4: Set UI state
            set_user_session(active_session)

            logger.info(f"Session restored in UI: {validation.username}")
            return True

        except Exception as e:
            logger.error(f"Session restoration failed: {e}")
            return False

    @logger.catch
    def ensure_session_active(self) -> bool:
        """Check dan refresh current session."""
        try:
            session_token = st.session_state.get("session_token")

            if not session_token:
                logger.debug("No session token found in state")
                return False

            # Validate via service
            validation = self.session_service.validate_session(session_token)

            if not validation.is_valid:
                logger.info("Session invalid, clearing UI state")
                self.clear_session_state(session_token)
                return False

            # Refresh activity
            return self.session_service.refresh_session(session_token)

        except Exception as e:
            logger.error(f"Session health check failed: {e}")
            return False

    def clear_session_state(self, session_token: str | None = None) -> bool:
        """Clear UI state dan database session."""
        try:
            # Step 1: Clear UI state
            clear_user_session()
            logger.debug("UI session cleared")

            # Step 2: Deactivate database session
            if session_token:
                self.session_service.deactivate_session(session_token)

            logger.info("Complete session clear successful")
            return True

        except Exception as e:
            logger.error(f"Session clear error: {e}")
            return True  # Partial success - UI cleared


# PINNED: Factory pattern untuk easier instantiation
def get_session_restoration_manager() -> SessionRestorationManager:
    """Factory untuk SessionRestorationManager instance."""
    return SessionRestorationManager()
