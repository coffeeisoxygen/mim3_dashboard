"""Authentication UI components - pure UI logic."""

# ruff noqa: F841
from __future__ import annotations

import time

import streamlit as st
from core.messages import UIMessages
from loguru import logger

from services.auth_service import AuthService


class AuthHandler:
    """Handle authentication UI only - no business logic."""

    def __init__(self):
        """Initialize dengan cached auth service."""
        self.auth_service = AuthService()

    def render_login_form(self) -> None:
        """Render login form dengan optimized fragment."""
        # ✅ Static content outside fragment
        username = st.text_input("Username", placeholder="Masukkan username")
        password = st.text_input(
            "Password", type="password", placeholder="Masukkan password"
        )

        # ✅ Only interactive logic inside fragment
        self._render_login_buttons(username, password)

    @st.fragment
    def _render_login_buttons(self, username: str, password: str) -> None:
        """Fragment hanya untuk button interactions."""
        col1, col2 = st.columns(2)

        with col1:
            if st.button("🔐 Log in", type="primary", use_container_width=True):
                # ✅ Reduced logging - only for actual clicks
                logger.info(f"Login attempt: {username}")

                if not username or not password:
                    st.error("❌ Username dan password harus diisi")
                    return

                success, message = self.auth_service.perform_login(username, password)

                if success:
                    st.success(f"{UIMessages.SUCCESS_PREFIX} {message}")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(f"{UIMessages.ERROR_PREFIX} {message}")

        with col2:
            if st.button("📝 Register", use_container_width=True):
                self.show_register_dialog()

    @st.dialog("Daftar Akun Baru")
    def show_register_dialog(self) -> None:
        """Dialog register dengan form."""
        st.write("**Buat akun baru MIM3 Dashboard**")
        st.caption("Akun akan menunggu persetujuan admin")

        # Registration form here
        username = st.text_input("Username", placeholder="Username unik")  # noqa: F841
        name = st.text_input("Nama Lengkap", placeholder="Nama lengkap")  # noqa: F841
        password = st.text_input("Password", type="password")  # noqa: F841

        col1, col2 = st.columns(2)

        with col1:
            if st.button("📝 Daftar", type="primary", use_container_width=True):
                # TODO: delegate to registration service
                pass

        with col2:
            if st.button("❌ Batal", use_container_width=True):
                st.rerun()

    def render_demo_credentials(self) -> None:
        """Show demo credentials - pure UI component."""
        with st.expander("🔧 Demo Credentials"):
            st.info("**Testing purposes only:**")
            st.write("• **Admin:** admin / admin123")
            st.write("• **User:** operator / demo123")
            st.write("• **Manager:** support / demo123")
