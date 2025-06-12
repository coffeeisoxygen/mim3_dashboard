"""Session restoration manager dengan SessionContext integration."""

from __future__ import annotations

import streamlit as st
from loguru import logger

from models.session.session_context import SessionContext
from models.session.session_st import clear_user_session, set_user_session
from models.user.user_auth import UserActiveSession
from services.session_service import SessionService


class SessionRestorationManager:
    """Handle UI state restoration dengan rich context tracking."""

    def __init__(self, session_service: SessionService):
        self.session_service = session_service

    @logger.catch
    def restore_session_from_token(self, session_token: str) -> bool:
        """Restore Streamlit state dengan context validation."""
        try:
            # Step 1: Capture current context
            current_context = SessionContext.from_streamlit_context()

            logger.debug(
                f"Attempting session restoration: {session_token[:10]}...",
                client_info=current_context.get_client_info(),
            )

            # Step 2: Get validation data
            validation = self.session_service.get_session_restoration_data(
                session_token
            )

            if not validation.is_valid:
                logger.warning("Cannot restore invalid session")
                return False

            # Step 3: Security check - context validation jika perlu
            if not current_context.is_local_access():
                logger.info("Remote session restoration", ip=current_context.client_ip)

            # Step 4: Create ActiveSession untuk UI state
            active_session = UserActiveSession(
                user_id=validation.user_id,
                username=validation.username,
                name=validation.username,
                role_id=getattr(validation, "role_id", 0),
                role_name=validation.role_name or "unknown",
                session_token=session_token,
            )

            # Step 5: Set UI state
            set_user_session(active_session)

            logger.info(
                f"Session restored in UI: {validation.username}",
                context=current_context.get_client_info(),
                timezone=current_context.get_display_timezone(),
            )
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

            # Delegate validation ke service layer
            validation = self.session_service.validate_session(session_token)

            if not validation.is_valid:
                logger.info("Session invalid, clearing UI state")
                self.clear_session_state(session_token)
                return False

            # Delegate refresh ke service layer
            return self.session_service.refresh_session(session_token)

        except Exception as e:
            logger.error(f"Session health check failed: {e}")
            return False

    def clear_session_state(self, session_token: str | None = None) -> bool:
        """Clear UI state dan database session."""
        try:
            # Step 1: Clear UI state (UI layer responsibility)
            clear_user_session()
            logger.debug("UI session cleared")

            # Step 2: Deactivate database session (delegate to service)
            if session_token:
                self.session_service.deactivate_session(session_token)

            logger.info("Complete session clear successful")
            return True

        except Exception as e:
            logger.error(f"Session clear error: {e}")
            return True  # Partial success - UI cleared


# PINNED: Factory pattern untuk dependency injection
def get_session_restoration_manager() -> SessionRestorationManager:
    """Factory untuk SessionRestorationManager dengan injected dependencies.

    Clean Architecture: Factory handles dependency wiring, tidak ada
    hard coupling di constructor.
    """
    from services.session_service import get_session_service

    session_service = get_session_service()
    return SessionRestorationManager(session_service)


# TODO: Add UserService dependency untuk get display name
# [ ] PINNED: Create MockSessionService untuk unit testing
# REMINDER: Manager layer fokus ke UI orchestration, business logic di service
