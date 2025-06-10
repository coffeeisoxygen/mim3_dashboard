"""Simple session state utilities."""

import streamlit as st

from models.user.us_onauth import ActiveSession


def set_user_session(user_session: ActiveSession) -> None:
    """Set user session data dengan role handling."""
    st.session_state.logged_in = True
    st.session_state.user_id = user_session.user_id
    st.session_state.username = user_session.username
    st.session_state.name = user_session.name
    st.session_state.login_time = user_session.login_time

    # Role handling untuk user baru
    if user_session.role_name is None or user_session.role_name == "":
        st.session_state.user_role = "pending"
        st.session_state.role_id = 0
    else:
        st.session_state.user_role = user_session.role_name
        st.session_state.role_id = user_session.role_id

    # ✅ Always store session token (even if None)
    st.session_state.session_token = getattr(user_session, "session_token", None)


def clear_user_session() -> None:
    """Clear user session data completely."""
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

    for key in session_keys:
        if key in st.session_state:
            del st.session_state[key]


def get_current_user() -> dict:
    """Get current user info with role status."""
    return {
        "user_id": st.session_state.get("user_id"),
        "username": st.session_state.get("username", ""),
        "name": st.session_state.get("name", ""),
        "role": st.session_state.get("user_role"),
        "role_id": st.session_state.get("role_id"),
        "is_pending": st.session_state.get("user_role") == "pending",
    }
