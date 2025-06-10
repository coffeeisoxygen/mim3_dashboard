"""Simple session state utilities - clean and predictable."""

import streamlit as st
from loguru import logger

from models.user.user_auth import ActiveSession


def set_user_session(user_session: ActiveSession) -> None:
    """Set user session data dengan clean mapping."""
    try:
        # Basic user data - always present
        st.session_state.logged_in = True
        st.session_state.user_id = user_session.user_id
        st.session_state.username = user_session.username
        st.session_state.name = user_session.name
        st.session_state.login_time = user_session.login_time

        # Role data dengan clear fallback
        st.session_state.user_role = _get_user_role(user_session)
        st.session_state.role_id = _get_role_id(user_session)

        # Session token - direct assignment
        st.session_state.session_token = user_session.session_token

        logger.debug(
            f"Session set for user: {user_session.username} with role: {st.session_state.user_role}"
        )

    except Exception as e:
        logger.error(f"Failed to set user session: {e}")
        clear_user_session()  # Failsafe


def _get_user_role(user_session: ActiveSession) -> str:
    """Extract user role dengan fallback logic."""
    if not user_session.role_name or user_session.role_name.strip() == "":
        return "pending"
    return user_session.role_name


def _get_role_id(user_session: ActiveSession) -> int:
    """Extract role ID dengan fallback logic."""
    if not user_session.role_name or user_session.role_name.strip() == "":
        return 0
    return user_session.role_id or 0


def clear_user_session() -> None:
    """Clear user session data completely dengan safety."""
    session_keys = [
        "logged_in",
        "user_id",
        "username",
        "name",
        "user_role",
        "role_id",
        "login_time",
        "session_token",
    ]

    cleared_count = 0
    for key in session_keys:
        if key in st.session_state:
            del st.session_state[key]
            cleared_count += 1

    logger.debug(f"Cleared {cleared_count} session keys")


def get_current_user() -> dict:
    """Get current user info dengan safe access."""
    return {
        "user_id": st.session_state.get("user_id"),
        "username": st.session_state.get("username", ""),
        "name": st.session_state.get("name", ""),
        "role": st.session_state.get("user_role", "pending"),
        "role_id": st.session_state.get("role_id", 0),
        "is_pending": st.session_state.get("user_role", "pending") == "pending",
        "is_logged_in": st.session_state.get("logged_in", False),
    }


def is_session_valid() -> bool:
    """Quick session validity check."""
    required_keys = ["logged_in", "user_id", "username"]
    return all(
        key in st.session_state for key in required_keys
    ) and st.session_state.get("logged_in", False)
