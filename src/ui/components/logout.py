"""Logout component - pure UI logic."""

from __future__ import annotations

import time

import streamlit as st

from services.auth_flow_service import AuthFlowService


class LogoutHandler:
    """Handle logout UI only."""

    def __init__(self):
        """Initialize dengan auth flow service."""
        self.auth_flow = AuthFlowService()

    @st.dialog("Konfirmasi Logout")
    def show_logout_dialog(self) -> None:
        """Dialog konfirmasi logout dengan user info."""
        username = st.session_state.get("username", "User")
        role = st.session_state.get("user_role", "user")

        st.markdown(f"### 👤 {username}")
        st.caption(f"Role: {role.title()}")
        st.markdown("---")
        st.write("**Yakin ingin logout dari MIM3 Dashboard?**")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("✅ Ya, Logout", type="primary", use_container_width=True):
                # ✅ Delegate to service
                success, message = self.auth_flow.perform_logout()

                if success:
                    st.success(f"✅ {message}")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(f"❌ {message}")

        with col2:
            if st.button("❌ Batal", use_container_width=True):
                st.rerun()
