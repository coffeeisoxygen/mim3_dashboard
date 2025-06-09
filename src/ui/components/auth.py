"""Authentication UI components - pure UI logic."""

from __future__ import annotations

import time

import streamlit as st

from core.messages import UIMessages
from services import get_auth_flow_service


class AuthHandler:
    """Handle authentication UI only - no business logic."""

    def __init__(self):
        """Initialize dengan cached auth flow service."""
        self.auth_flow = get_auth_flow_service()  # ✅ Cached instance

    @st.fragment
    def render_login_form(self) -> None:
        """Render login form - pure UI rendering."""
        username = st.text_input("Username", placeholder="Masukkan username")
        password = st.text_input(
            "Password", type="password", placeholder="Masukkan password"
        )

        if st.button("🔐 Log in", type="primary", use_container_width=True):
            # ✅ Delegate to service, handle UI feedback only
            success, message = self.auth_flow.perform_login(username, password)

            if success:
                st.success(f"{UIMessages.SUCCESS_PREFIX} {message}")  # ✅ Consistent
                time.sleep(1)  # UI feedback pause
                st.rerun()
            else:
                st.error(f"{UIMessages.ERROR_PREFIX} {message}")  # ✅ Consistent

    def render_demo_credentials(self) -> None:
        """Show demo credentials - pure UI component."""
        with st.expander("🔧 Demo Credentials"):
            st.info("**Testing purposes only:**")
            st.write("• **Admin:** admin / admin123")
            st.write("• **User:** user / user123")
            st.write("• **Manager:** manager / manager123")
