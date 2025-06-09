"""Logout component - pure UI logic."""

from __future__ import annotations

import time

import streamlit as st

from services import get_auth_service


class LogoutHandler:
    """Handle logout UI only."""

    def __init__(self):
        """Initialize dengan cached auth service."""
        self.auth_service = get_auth_service()  # ✅ Same cached instance

    def add_logout_to_sidebar(self) -> None:
        """Add user info dan logout button ke sidebar."""
        st.sidebar.markdown("---")

        username = st.session_state.get("username", "User")
        role = st.session_state.get("user_role", "user")

        # User info display
        with st.sidebar.container():
            st.markdown(f"**👤 {username}**")
            st.caption(f"🏷️ {role.title()}")

        # Logout button
        if st.sidebar.button(
            "🚪 Logout",
            type="secondary",
            use_container_width=True,
            help="Logout dari MIM3 Dashboard",
        ):
            self.show_logout_dialog()  # ✅ Call instance method

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
                success, message = self.auth_service.perform_logout()

                if success:
                    st.success(f"✅ {message}")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(f"❌ {message}")

        with col2:
            if st.button("❌ Batal", use_container_width=True):
                st.rerun()
