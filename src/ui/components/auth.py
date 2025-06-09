"""Authentication UI components untuk MIM3 Dashboard."""

from __future__ import annotations

import streamlit as st
from loguru import logger

from core.session import SessionManager
from models.auth import UserLogin
from services.auth_service import AuthService


class AuthHandler:
    """Handle authentication UI and logic."""

    def __init__(self):
        """Initialize auth handler dengan service."""
        self.auth_service = AuthService()

    @st.fragment  # ✅ Keep fragment untuk better UX
    def render_login_form(self) -> None:
        """Render login form dengan validation menggunakan fragment."""
        username = st.text_input("Username", placeholder="Masukkan username")
        password = st.text_input(
            "Password", type="password", placeholder="Masukkan password"
        )

        if st.button("🔐 Log in", type="primary", use_container_width=True):
            self._handle_login(username, password)

    def render_demo_credentials(self) -> None:
        """Show demo credentials untuk testing."""
        with st.expander("🔧 Demo Credentials"):
            st.info("**Testing purposes only:**")
            st.write("• **Admin:** admin / admin123")
            st.write("• **User:** user / user123")
            st.write("• **Manager:** manager / manager123")

    def _handle_login(self, username: str, password: str) -> None:
        """Process login attempt - runs in fragment context."""
        if not username or not password:
            st.error("❌ Mohon isi username dan password")
            return

        try:
            login_data = UserLogin(username=username, password=password)
            result = self.auth_service.authenticate(login_data)

            if result.success and result.user_session:
                SessionManager.set_user_session(
                    user_id=result.user_session.user_id,
                    username=result.user_session.username,
                    role=result.user_session.role,
                )

                st.success("✅ Login berhasil!")

                # ✅ Brief pause untuk user feedback
                import time

                time.sleep(1)

                st.rerun()  # Then navigate
            else:
                st.error(f"❌ {result.error_message}")

        except Exception as e:
            logger.error(f"Login error: {e}")
            st.error(f"❌ Input tidak valid: {e}")
