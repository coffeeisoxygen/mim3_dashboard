"""Session manager - main interface."""

from __future__ import annotations

import streamlit as st
from loguru import logger

from config.paths import AppPaths
from core.session.persistance import SessionPersistence
from core.session.state import SessionState


class SessionManager:
    """Main session management interface."""

    @staticmethod
    def initialize() -> None:
        """Initialize session - call once per app run."""
        AppPaths.ensure_directories()

        # Get session ID (efficient - check memory first)
        if "session_id" not in st.session_state:
            st.session_state.session_id = SessionPersistence.get_or_create_session_id()

        # Try restore from file (only if not already logged in)
        if not st.session_state.get("logged_in", False):
            restored = SessionPersistence.restore_session()
            if restored:
                logger.info(f"Session restored: {st.session_state.username}")

        # Initialize defaults
        SessionState.initialize_defaults()

    @staticmethod
    def login(user_id: int, username: str, role: str) -> None:
        """Handle user login."""
        SessionState.set_user(user_id, username, role)
        SessionPersistence.save_session()
        logger.info(f"User login: {username} ({role})")

    @staticmethod
    def logout() -> None:
        """Handle user logout."""
        username = st.session_state.get("username", "Unknown")
        SessionState.clear_user()

        # Delete session file
        session_id = st.session_state.get("session_id")
        if session_id:
            session_file = AppPaths.SESSIONS_DIR / f"session_{session_id}.json"
            session_file.unlink(missing_ok=True)

        logger.info(f"User logout: {username}")

    @staticmethod
    def get_session_info() -> dict:
        """Get current session info - for debugging."""
        return {
            "session_id": st.session_state.get("session_id"),
            "logged_in": st.session_state.get("logged_in", False),
            "user_id": st.session_state.get("user_id"),
            "username": st.session_state.get("username"),
            "user_role": st.session_state.get("user_role"),
            "login_time": st.session_state.get("login_time"),
        }
