"""Session persistence - file operations only."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timedelta

import streamlit as st
from loguru import logger

from config.paths import AppPaths


class SessionPersistence:
    """Handle session file persistence."""

    DURATION = timedelta(hours=1)

    @staticmethod
    def _is_session_valid(session_file) -> bool:
        """Check if session file is valid and not expired."""
        try:
            with session_file.open(encoding="utf-8") as f:
                data = json.load(f)

            expires_at = datetime.fromisoformat(data["expires_at"])
            if datetime.now() > expires_at:
                session_file.unlink()  # Clean up expired session
                return False

            return True
        except Exception as e:
            logger.error(f"Session validation failed: {e}")
            # Clean up corrupted session file
            try:
                session_file.unlink()
            except Exception as cleanup_error:
                logger.warning(
                    f"Failed to cleanup corrupted session file {session_file}: {cleanup_error}"
                )
            return False

    @staticmethod
    def get_or_create_session_id() -> str:
        """Get existing session ID atau create new."""
        # ✅ Check memory first (avoid file I/O)
        if hasattr(st.session_state, "_session_checked"):
            return st.session_state.session_id

        # Only check files once per session
        st.session_state._session_checked = True

        if AppPaths.SESSIONS_DIR.exists():
            for session_file in AppPaths.SESSIONS_DIR.glob("session_*.json"):
                if SessionPersistence._is_session_valid(session_file):
                    session_id = session_file.stem.replace("session_", "")
                    logger.debug(f"Reusing session: {session_id}")
                    return session_id

        # Create new session
        new_id = str(uuid.uuid4())[:8]
        logger.info(f"New session: {new_id}")
        return new_id

    @staticmethod
    def save_session() -> None:
        """Save current session to file."""
        if not st.session_state.get("logged_in"):
            return

        session_id = st.session_state.get("session_id")
        if not session_id:
            return

        session_file = AppPaths.SESSIONS_DIR / f"session_{session_id}.json"
        session_data = {
            "logged_in": True,
            "user_id": st.session_state.user_id,
            "username": st.session_state.username,
            "user_role": st.session_state.user_role,
            "login_time": st.session_state.login_time.isoformat(),
            "expires_at": (datetime.now() + SessionPersistence.DURATION).isoformat(),
        }

        try:
            with session_file.open("w", encoding="utf-8") as f:
                json.dump(session_data, f)
            logger.debug(f"Session saved: {session_id}")
        except Exception as e:
            logger.error(f"Save failed: {e}")

    @staticmethod
    def restore_session() -> bool:
        """Restore session from file if valid."""
        session_id = st.session_state.get("session_id")
        if not session_id:
            return False

        session_file = AppPaths.SESSIONS_DIR / f"session_{session_id}.json"
        if not session_file.exists():
            return False

        try:
            with session_file.open(encoding="utf-8") as f:
                data = json.load(f)

            # Check expiry
            expires_at = datetime.fromisoformat(data["expires_at"])
            if datetime.now() > expires_at:
                session_file.unlink()
                return False

            # Restore to session state
            st.session_state.logged_in = data["logged_in"]
            st.session_state.user_id = data["user_id"]
            st.session_state.username = data["username"]
            st.session_state.user_role = data["user_role"]
            st.session_state.login_time = datetime.fromisoformat(data["login_time"])

            return True

        except Exception as e:
            logger.error(f"Restore failed: {e}")
            session_file.unlink()
            return False
