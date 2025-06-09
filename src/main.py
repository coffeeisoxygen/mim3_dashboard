"""main.py - Entry point for the MIM3 Dashboard application."""

import streamlit as st
from loguru import logger

from config.logging import setup_logging
from core.session.manager import SessionManager
from database import initialize_database
from ui.components.auth import AuthHandler
from ui.components.logout import LogoutHandler
from ui.page_manager import PageManager

# ✅ Streamlit config - must be first
st.set_page_config(
    page_title="MIM3 Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

setup_logging()


@logger.catch
def login():
    """Login page dengan auth service integration."""
    st.title("🔐 MIM3 Dashboard Login")

    auth_handler = AuthHandler()
    auth_handler.render_login_form()
    auth_handler.render_demo_credentials()


@logger.catch
def main():
    """Main application logic - clean and focused."""
    # ✅ Setup logging hanya sekali per session
    if "logging_initialized" not in st.session_state:
        setup_logging()
        st.session_state.logging_initialized = True

    # ✅ Initialize database hanya sekali per session
    if "db_initialized" not in st.session_state:
        initialize_database()
        st.session_state.db_initialized = True
        logger.info(f"Database initialized for session: {st.session_state.session_id}")

    SessionManager.initialize()

    if st.session_state.logged_in:
        _add_session_debug_info()

        # ✅ Create instance
        logout_handler = LogoutHandler()
        logout_handler.add_logout_to_sidebar()

        page_manager = PageManager()
        user_role = st.session_state.user_role
        navigation = page_manager.get_navigation_structure(user_role)

        if navigation:
            pg = st.navigation(navigation)
            pg.run()
        else:
            st.error("❌ No pages available for your role.")
    else:
        login_page = st.Page(login, title="Log in", icon=":material/login:")
        pg = st.navigation([login_page])
        pg.run()


def _add_session_debug_info():
    """Add session debug info to sidebar (development only)."""
    import os

    # ✅ Only show in development
    if os.getenv("LOG_LEVEL", "INFO") == "DEBUG":
        with st.sidebar.expander("🔍 Session Info"):
            session_info = SessionManager.get_session_info()
            st.json(session_info)


if __name__ == "__main__":
    main()
