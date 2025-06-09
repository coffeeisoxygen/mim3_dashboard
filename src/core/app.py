"""Application bootstrap - handle app lifecycle and initialization."""

from __future__ import annotations

import streamlit as st

from config.logging import setup_logging
from core.us_session import get_current_user
from database import initialize_database
from ui.components.ui_auth import AuthHandler
from ui.components.ui_logout import LogoutHandler
from ui.page_manager import PageManager


class App:
    """Main application class - handle complete app lifecycle."""

    def run(self) -> None:
        """Run the application main loop."""
        self._initialize()
        self._setup_session_state()

        # Main app flow
        if st.session_state.logged_in:
            self._render_authenticated_app()
        else:
            self._render_login_page()

    def _initialize(self) -> None:
        """Initialize app components once."""
        setup_logging()  # @st.cache_resource
        initialize_database()  # @st.cache_resource

    def _setup_session_state(self) -> None:
        """Setup session state dengan current user check."""
        # Initialize default values
        defaults = {
            "logged_in": False,
            "user_role": None,
            "username": "",
        }

        for key, default_value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = default_value

        # Check current user status
        current_user = get_current_user()
        if current_user.get("user_id"):
            st.session_state.logged_in = True
            st.session_state.user_role = current_user.get("role")
            st.session_state.username = current_user.get("username")

    def _render_authenticated_app(self) -> None:
        """Render app untuk user yang sudah login."""
        LogoutHandler().add_logout_to_sidebar()

        page_manager = PageManager()
        navigation = page_manager.get_navigation_structure(st.session_state.user_role)

        if navigation:
            st.navigation(navigation).run()
        else:
            st.error("❌ No pages available for your role.")

    def _render_login_page(self) -> None:
        """Render login page untuk user yang belum login."""
        st.title("🔐 MIM3 Dashboard Login")

        auth_handler = AuthHandler()
        auth_handler.render_login_form()
        auth_handler.render_demo_credentials()
