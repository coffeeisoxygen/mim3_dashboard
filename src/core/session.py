"""Session manager untuk MIM3 Dashboard."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timedelta

import streamlit as st
from loguru import logger

from config.paths import AppPaths


class SessionManager:
    """Centralized session state management dengan file persistence."""

    SESSION_DURATION = timedelta(hours=1)

    @staticmethod
    def initialize_session() -> None:
        """Initialize session dengan persistence check."""
        # ✅ Use centralized path
        AppPaths.ensure_directories()

        # ✅ Get persistent session ID FIRST
        if "session_id" not in st.session_state:
            st.session_state.session_id = SessionManager._get_or_create_session_id()
            logger.info(f"Session ID resolved: {st.session_state.session_id}")

        # ✅ Try restore from file (dengan session ID yang benar)
        restored = SessionManager._restore_from_file()

        # ✅ Track initialization count
        init_count = st.session_state.get("init_count", 0) + 1
        st.session_state.init_count = init_count

        # Default values (only if not restored)
        if not restored:
            default_values = {
                "logged_in": False,
                "user_role": "user",
                "username": "",
                "user_id": None,
                "login_time": None,
            }

            new_keys = []
            for key, default_value in default_values.items():
                if key not in st.session_state:
                    st.session_state[key] = default_value
                    new_keys.append(key)

            session_id = st.session_state.session_id
            if new_keys:
                logger.info(
                    f"Session {session_id}: New session initialized (init #{init_count})"
                )
            else:
                logger.debug(f"Session {session_id}: State check (init #{init_count})")
        else:
            session_id = st.session_state.session_id
            username = st.session_state.get("username", "")
            logger.info(
                f"Session {session_id}: Restored from file - {username} (init #{init_count})"
            )

    @staticmethod
    def set_user_session(user_id: int, username: str, role: str) -> None:
        """Set user session dan save ke file."""
        session_id = st.session_state.get("session_id", "unknown")

        st.session_state.logged_in = True
        st.session_state.user_id = user_id
        st.session_state.username = username
        st.session_state.user_role = role
        st.session_state.login_time = datetime.now()

        # ✅ Save to file
        SessionManager._save_to_file()

        logger.info(f"Session {session_id}: User login - {username} ({role})")

    @staticmethod
    def clear_session() -> None:
        """Clear user session dan delete file."""
        session_id = st.session_state.get("session_id", "unknown")
        username = st.session_state.get("username", "Unknown")

        # ✅ Delete session file
        SessionManager._delete_session_file()

        # Reset to default values
        st.session_state.logged_in = False
        st.session_state.user_role = "user"
        st.session_state.username = ""
        st.session_state.user_id = None
        st.session_state.login_time = None

        logger.info(f"Session {session_id}: User logout - {username}")

    @staticmethod
    def _save_to_file() -> None:
        """Save session data ke file."""
        session_id = st.session_state.get("session_id")
        if not session_id:
            return

        # ✅ Use centralized path
        session_file = AppPaths.SESSIONS_DIR / f"session_{session_id}.json"

        session_data = {
            "logged_in": st.session_state.logged_in,
            "user_id": st.session_state.user_id,
            "username": st.session_state.username,
            "user_role": st.session_state.user_role,
            "login_time": st.session_state.login_time.isoformat()
            if st.session_state.login_time
            else None,
            "expires_at": (
                datetime.now() + SessionManager.SESSION_DURATION
            ).isoformat(),
            "created_at": datetime.now().isoformat(),
        }

        try:
            with session_file.open("w", encoding="utf-8") as f:
                json.dump(session_data, f, indent=2)
            logger.debug(f"Session {session_id}: Saved to file")
        except Exception as e:
            logger.error(f"Session {session_id}: Save failed - {e}")

    @staticmethod
    def _restore_from_file() -> bool:
        """Restore session dari file."""
        session_id = st.session_state.get("session_id")
        if not session_id:
            return False

        session_file = AppPaths.SESSIONS_DIR / f"session_{session_id}.json"

        if not session_file.exists():
            return False

        try:
            with session_file.open(encoding="utf-8") as f:
                session_data = json.load(f)

            # ✅ Check expiry
            expires_at = datetime.fromisoformat(session_data["expires_at"])
            if datetime.now() > expires_at:
                session_file.unlink()  # Delete expired session
                logger.info(f"Session {session_id}: Expired session deleted")
                return False

            # ✅ Restore session state
            st.session_state.logged_in = session_data["logged_in"]
            st.session_state.user_id = session_data["user_id"]
            st.session_state.username = session_data["username"]
            st.session_state.user_role = session_data["user_role"]

            if session_data["login_time"]:
                st.session_state.login_time = datetime.fromisoformat(
                    session_data["login_time"]
                )

            return True

        except Exception as e:
            logger.error(f"Session {session_id}: Restore failed - {e}")
            session_file.unlink()  # Delete corrupted session
            return False

    @staticmethod
    def _delete_session_file() -> None:
        """Delete session file."""
        session_id = st.session_state.get("session_id")
        if not session_id:
            return

        session_file = AppPaths.SESSIONS_DIR / f"session_{session_id}.json"

        try:
            if session_file.exists():
                session_file.unlink()
                logger.debug(f"Session {session_id}: File deleted")
        except Exception as e:
            logger.error(f"Session {session_id}: Delete failed - {e}")

    @staticmethod
    def cleanup_expired_sessions() -> None:
        """Cleanup expired session files."""
        if not AppPaths.SESSIONS_DIR.exists():
            return

        try:
            cleaned = 0
            for session_file in AppPaths.SESSIONS_DIR.glob("session_*.json"):
                try:
                    with session_file.open(encoding="utf-8") as f:
                        session_data = json.load(f)

                    expires_at = datetime.fromisoformat(session_data["expires_at"])
                    if datetime.now() > expires_at:
                        session_file.unlink()
                        cleaned += 1

                except Exception:
                    # Delete corrupted files
                    session_file.unlink()
                    cleaned += 1

            if cleaned > 0:
                logger.info(f"Cleaned up {cleaned} expired session files")

        except Exception as e:
            logger.error(f"Session cleanup failed: {e}")

    @staticmethod
    def get_session_info() -> dict:
        """Get current session information for debugging."""
        return {
            "session_id": st.session_state.get("session_id", "unknown"),
            "init_count": st.session_state.get("init_count", 0),
            "logged_in": st.session_state.get("logged_in", False),
            "username": st.session_state.get("username", ""),
            "login_time": st.session_state.get("login_time"),
        }

    @staticmethod
    def _get_or_create_session_id() -> str:
        """Get existing valid session ID or create new one."""
        if AppPaths.SESSIONS_DIR.exists():
            # Cari session file yang masih valid
            for session_file in AppPaths.SESSIONS_DIR.glob("session_*.json"):
                try:
                    with session_file.open(encoding="utf-8") as f:
                        session_data = json.load(f)

                    # Check expiry
                    expires_at = datetime.fromisoformat(session_data["expires_at"])
                    if datetime.now() < expires_at:
                        # ✅ Use existing session ID
                        session_id = session_file.stem.replace("session_", "")
                        logger.info(f"Reusing existing session: {session_id}")
                        return session_id
                    else:
                        # Cleanup expired
                        session_file.unlink()

                except Exception:
                    # Cleanup corrupted
                    session_file.unlink()

        # No valid session found
        new_session_id = str(uuid.uuid4())[:8]
        logger.info(f"Creating new session: {new_session_id}")
        return new_session_id
