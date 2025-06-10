"""Application bootstrap - handle app lifecycle and initialization."""

from __future__ import annotations

import streamlit as st
from loguru import logger

from config.logging import setup_logging
from database.core import initialize_database
from models.session.session_st import get_current_user
from models.system.bootstrap import ensure_system_ready
from ui.components.ui_auth import AuthHandler
from ui.components.ui_logout import LogoutHandler
from ui.page_manager import PageManager


class App:
    """Main application class - handle complete app lifecycle."""

    def run(self) -> None:
        """Run the application main loop."""
        if not self._initialize():
            self._render_bootstrap_error()
            return

        self._setup_session_state()

        # Main app flow
        if st.session_state.logged_in:
            self._render_authenticated_app()
        else:
            self._render_login_page()

    def _initialize(self) -> bool:
        """Initialize app components dengan proper error handling."""
        try:
            # Step 1: Basic infrastructure
            setup_logging()
            logger.info("Starting MIM3 Dashboard...")

            # Step 2: Database infrastructure (tables only)
            initialize_database()

            # Step 3: Business logic bootstrap (roles + admin)
            if not ensure_system_ready():
                logger.error("System bootstrap failed")
                return False

            logger.success("MIM3 Dashboard initialized successfully")
            return True

        except Exception as e:
            logger.error(f"App initialization failed: {e}")
            return False

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

    def _render_bootstrap_error(self) -> None:
        """Render error page kalau bootstrap gagal."""
        st.error("🚨 **System Initialization Failed**")
        st.write("""
        MIM3 Dashboard gagal melakukan inisialisasi system.

        **Possible solutions:**
        1. Check database permissions
        2. Check log files di `logs/` folder
        3. Contact system administrator
        """)

        # TODO: Add restart button or troubleshooting info
        if st.button("🔄 Retry Initialization"):
            st.rerun()


# REMINDER: Bootstrap sequence = Infrastructure → Business Logic → UI
