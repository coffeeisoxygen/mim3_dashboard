"""Simple session state utilities."""

import streamlit as st

from models.md_user import UserSession


def set_user_session(user_session: UserSession) -> None:
    """Set user session data."""
    st.session_state.logged_in = True
    st.session_state.user_id = user_session.user_id
    st.session_state.username = user_session.username
    st.session_state.user_role = user_session.role


def clear_user_session() -> None:
    """Clear user session data."""
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.username = ""
    st.session_state.user_role = None


def get_current_user() -> dict:
    """Get current user info."""
    return {
        "user_id": st.session_state.get("user_id"),
        "username": st.session_state.get("username", ""),
        "role": st.session_state.get("user_role"),
    }
