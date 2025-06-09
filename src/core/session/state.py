"""Session state management - core functionality."""

from __future__ import annotations

from datetime import datetime

import streamlit as st


class SessionState:
    """Minimal session state management."""

    @staticmethod
    def initialize_defaults() -> None:
        """Initialize session state dengan default values."""
        defaults = {
            "logged_in": False,
            "user_role": "user",
            "username": "",
            "user_id": None,
            "login_time": None,
        }

        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value

    @staticmethod
    def set_user(user_id: int, username: str, role: str) -> None:
        """Set user session data."""
        st.session_state.logged_in = True
        st.session_state.user_id = user_id
        st.session_state.username = username
        st.session_state.user_role = role
        st.session_state.login_time = datetime.now()

    @staticmethod
    def clear_user() -> None:
        """Clear user session data."""
        st.session_state.logged_in = False
        st.session_state.user_role = "user"
        st.session_state.username = ""
        st.session_state.user_id = None
        st.session_state.login_time = None
