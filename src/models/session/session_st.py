"""Streamlit session state management - clean OOP approach."""

from __future__ import annotations

from typing import Any, Protocol

import streamlit as st
from loguru import logger


# PINNED: Interface untuk loose coupling dengan user models
class SessionDataProtocol(Protocol):
    """Protocol untuk session data - no direct coupling."""

    user_id: int
    username: str
    name: str
    role_id: int
    role_name: str | None
    session_token: str | None


class SessionStateManager:
    """Manage Streamlit session state dengan clear boundaries."""

    @logger.catch
    def set_user_session(self, session_data: SessionDataProtocol) -> bool:
        """Set session state dari protocol interface."""
        # Guard against None session data
        if session_data is None:
            logger.error("Cannot set session: session_data is None")
            return False

        try:
            # Core session data
            st.session_state.logged_in = True
            st.session_state.user_id = session_data.user_id
            st.session_state.username = session_data.username or ""
            st.session_state.name = session_data.name or ""
            st.session_state.session_token = session_data.session_token

            # Role dengan safe extraction
            st.session_state.user_role = self._extract_role_name(session_data)
            st.session_state.role_id = session_data.role_id

            logger.opt(lazy=True).debug(
                "Session set for user: {username} with role: {role}",
                username=lambda: session_data.username,
                role=lambda: st.session_state.user_role,
            )
            return True

        except Exception as e:
            logger.error(f"Failed to set session: {e}")
            self.clear_session()
            return False

    def _extract_role_name(self, data: SessionDataProtocol) -> str:
        """Strategy pattern untuk role extraction."""
        if not data.role_name or data.role_name.strip() == "":
            return "pending"
        return data.role_name

    @logger.catch
    def clear_session(self) -> bool:
        """Clear session dengan safe cleanup."""
        session_keys = [
            "logged_in",
            "user_id",
            "username",
            "name",
            "user_role",
            "role_id",
            "session_token",
        ]

        cleared = sum(
            1
            for key in session_keys
            if key in st.session_state and (st.session_state.pop(key, None) is not None)
        )

        logger.debug(f"Cleared {cleared} session keys")
        return True

    def get_current_user(self) -> dict[str, Any]:
        """Safe access pattern untuk current user data."""
        return {
            "user_id": st.session_state.get("user_id"),
            "username": st.session_state.get("username", ""),
            "name": st.session_state.get("name", ""),
            "role": st.session_state.get("user_role", "pending"),
            "role_id": st.session_state.get("role_id", 0),
            "is_pending": st.session_state.get("user_role", "pending") == "pending",
            "is_logged_in": st.session_state.get("logged_in", False),
        }

    def is_valid_session(self) -> bool:
        """Validator pattern untuk session validity."""
        required = ["logged_in", "user_id", "username"]
        return all(
            key in st.session_state for key in required
        ) and st.session_state.get("logged_in", False)


# TODO: Singleton pattern untuk global state manager instance
_session_manager = SessionStateManager()


# REMINDER: Backward compatibility functions
def set_user_session(user_session) -> None:
    """Backward compatibility wrapper."""
    _session_manager.set_user_session(user_session)


def clear_user_session() -> None:
    """Backward compatibility wrapper."""
    _session_manager.clear_session()


def get_current_user() -> dict:
    """Backward compatibility wrapper."""
    return _session_manager.get_current_user()


def is_session_valid() -> bool:
    """Backward compatibility wrapper."""
    return _session_manager.is_valid_session()
