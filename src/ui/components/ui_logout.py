"""Logout component - pure UI logic."""

from __future__ import annotations

import time

import streamlit as st

from services.auth_service import AuthService


class LogoutHandler:
    """Handle logout UI only."""

    def __init__(self):
        """Initialize dengan auth service instance."""
        self.auth_service = AuthService()

    def add_logout_to_sidebar(self) -> None:
        """Add user info dan logout button ke sidebar."""
        st.sidebar.markdown("---")

        username = st.session_state.get("username", "User")
        role = st.session_state.get("user_role", "user")

        # User info display
        with st.sidebar.container():
            st.markdown(f"**👤 {username}**")
            st.caption(f"🏷️ {role.title()}")

        # ✅ Direct logout trigger
        if st.sidebar.button(
            "🚪 Logout",
            type="secondary",
            use_container_width=True,
            help="Logout dari MIM3 Dashboard",
        ):
            st.session_state.show_logout_confirm = True
            st.rerun()

        # ✅ Show confirmation if needed
        if st.session_state.get("show_logout_confirm", False):
            self._render_logout_confirmation()

    @st.fragment
    def _render_logout_confirmation(self) -> None:
        """Render logout confirmation dengan form pattern."""
        username = st.session_state.get("username", "User")
        role = st.session_state.get("user_role", "user")

        # ✅ Use warning container
        with st.container():
            st.warning("🚪 **Konfirmasi Logout**")

            _, col2, _ = st.columns([1, 2, 1])
            with col2:
                st.markdown(f"**👤 {username}** ({role.title()})")
                st.write("Yakin ingin logout dari MIM3 Dashboard?")

                # ✅ Use form untuk persistent state
                with st.form("logout_form", clear_on_submit=False):
                    col_yes, col_no = st.columns(2)

                    with col_yes:
                        logout_clicked = st.form_submit_button(
                            "✅ Ya, Logout", type="primary", use_container_width=True
                        )

                    with col_no:
                        cancel_clicked = st.form_submit_button(
                            "❌ Batal", use_container_width=True
                        )

                # ✅ Process form submission
                if logout_clicked:
                    success, message = self.auth_service.perform_logout()

                    if success:
                        st.success(f"✅ {message}")
                        st.session_state.show_logout_confirm = False
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
                        st.session_state.show_logout_confirm = False

                elif cancel_clicked:
                    st.session_state.show_logout_confirm = False
                    st.rerun()
