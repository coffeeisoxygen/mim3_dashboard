"""Application bootstrap - handle app lifecycle and initialization."""

from __future__ import annotations

import streamlit as st
from loguru import logger

from config.logging import setup_logging
from core.bootstrap import ensure_system_ready
from database.base import initialize_database
from ui.components.ui_auth import AuthHandler
from ui.page_manager import PageManager


@st.cache_resource(show_spinner="🚀 Initializing MIM3 Dashboard...")
def _initialize_app_once() -> bool:
    """Initialize app components sekali saja per Streamlit session."""
    try:
        # Step 1: Basic infrastructure
        setup_logging()
        logger.info("Starting MIM3 Dashboard...")

        # Step 2: Database infrastructure
        initialize_database()

        # Step 3: System bootstrap
        if not ensure_system_ready():
            logger.error("System bootstrap failed")
            return False

        logger.success("MIM3 Dashboard initialized successfully")
        return True

    except Exception as e:
        logger.error(f"App initialization failed: {e}")
        return False


class App:
    """Main application class - handle complete app lifecycle."""

    def run(self) -> None:
        """Run the application main loop."""
        # ✅ Cache resource ensures this runs only once
        if not _initialize_app_once():
            self._render_bootstrap_error()
            return

        self._setup_session_state()

        # Main app flow
        if st.session_state.logged_in:
            self._render_authenticated_app()
        else:
            self._render_login_page()

    def _setup_session_state(self) -> None:
        """Setup session state dengan session restoration."""
        # Initialize default values
        defaults = {
            "logged_in": False,
            "user_role": None,
            "username": "",
        }

        for key, default_value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = default_value

        # ✅ Attempt session restoration jika belum logged in
        if not st.session_state.get("logged_in", False):
            self._attempt_session_restoration()

    @logger.catch
    def _attempt_session_restoration(self) -> None:
        """Restore session dari query params using new service layer."""
        try:
            # Check query params for session token
            session_token = st.query_params.get("session")

            if session_token:
                logger.debug(f"Found session token in URL: {session_token[:10]}...")

                # ✅ Use SessionRestorationManager
                from services.session_restore_manager import (
                    get_session_restoration_manager,
                )

                restore_manager = get_session_restoration_manager()
                success = restore_manager.restore_session_from_token(session_token)

                if success:
                    logger.info("Session restored from URL successfully")
                    # ✅ Set logged_in state explicitly for clarity
                    st.session_state.logged_in = True
                    # Keep URL clean after restoration
                    st.query_params.clear()
                else:
                    logger.warning("Failed to restore session from URL")
                    st.query_params.clear()

        except Exception as e:
            logger.warning(f"Session restoration from URL failed: {e}")
            st.query_params.clear()

    def _render_authenticated_app(self) -> None:
        """Render app untuk user yang sudah login."""
        # ✅ Remove old LogoutHandler - use simple footer instead
        # LogoutHandler().add_logout_to_sidebar()

        # ✅ Add simple sidebar footer
        self._render_sidebar_footer()

        # ✅ Cache page manager
        if "page_manager" not in st.session_state:
            st.session_state.page_manager = PageManager()

        page_manager = st.session_state.page_manager
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

    def _render_sidebar_footer(self) -> None:
        """Simple logout footer di sidebar."""
        with st.sidebar:
            st.divider()

            # User info
            username = st.session_state.get("username", "User")
            role = st.session_state.get("user_role", "user")

            st.caption(f"👤 {username} ({role.title()})")

            # Simple logout button - no confirmation
            if st.button("🚪 Logout", type="secondary", use_container_width=True):
                from services.auth_service import AuthService

                auth_service = AuthService()
                success, message = auth_service.perform_logout()

                if success:
                    st.rerun()
                else:
                    st.error(f"❌ {message}")


# REMINDER: Bootstrap sequence = Infrastructure → Business Logic → UI
