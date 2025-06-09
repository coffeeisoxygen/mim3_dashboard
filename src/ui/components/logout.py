"""Logout component dengan dialog confirmation untuk MIM3 Dashboard."""

from __future__ import annotations

import streamlit as st
from loguru import logger

from core.session import SessionManager


class LogoutHandler:
    """Handle logout functionality dengan dialog confirmation."""

    @staticmethod
    @st.dialog("Konfirmasi Logout")
    def show_logout_dialog() -> None:
        """Dialog konfirmasi logout dengan user info."""
        username = st.session_state.get("username", "User")
        role = st.session_state.get("user_role", "user")

        # User info display
        st.markdown(f"### 👤 {username}")
        st.caption(f"Role: {role.title()}")
        st.markdown("---")

        st.write("**Yakin ingin logout dari MIM3 Dashboard?**")

        # Action buttons
        col1, col2 = st.columns(2)

        with col1:
            if st.button("✅ Ya, Logout", type="primary", use_container_width=True):
                LogoutHandler._perform_logout(username)

        with col2:
            if st.button("❌ Batal", use_container_width=True):
                st.rerun()  # Close dialog

    @staticmethod
    def _perform_logout(username: str) -> None:
        """Perform actual logout dengan clear state."""
        try:
            # Clear session state
            SessionManager.clear_session()

            # Success feedback
            st.success(f"✅ {username} berhasil logout!")
            logger.info(f"User logout completed: {username}")

            # Force app restart to login page
            st.rerun()

        except Exception as e:
            logger.error(f"Logout error: {e}")
            st.error("❌ Terjadi kesalahan saat logout")

    @staticmethod
    def add_logout_to_sidebar() -> None:
        """Add user info dan logout button ke sidebar dengan compact design."""
        # Custom CSS untuk compact user info
        st.sidebar.markdown(
            """
        <style>
        .user-info-compact {
            background: linear-gradient(90deg, #f0f2f6, #ffffff);
            border-radius: 8px;
            padding: 8px 12px;
            margin: 8px 0;
            border-left: 3px solid #1f77b4;
        }
        .user-name {
            font-weight: 600;
            font-size: 14px;
            color: #262730;
            margin-bottom: 2px;
        }
        .user-details {
            font-size: 11px;
            color: #6c757d;
            display: flex;
            justify-content: space-between;
        }
        .divider-thin {
            height: 1px;
            background: #e0e0e0;
            margin: 12px 0 8px 0;
        }
        </style>
        """,
            unsafe_allow_html=True,
        )

        # Thin divider
        st.sidebar.markdown('<div class="divider-thin"></div>', unsafe_allow_html=True)

        username = st.session_state.get("username", "User")
        role = st.session_state.get("user_role", "user")
        login_time = st.session_state.get("login_time")

        # Compact user info card
        time_str = login_time.strftime("%H:%M") if login_time else ""

        user_info_html = f"""
        <div class="user-info-compact">
            <div class="user-name">👤 {username}</div>
            <div class="user-details">
                <span>🏷️ {role.title()}</span>
                {f"<span>⏰ {time_str}</span>" if time_str else ""}
            </div>
        </div>
        """

        st.sidebar.markdown(user_info_html, unsafe_allow_html=True)

        # Compact logout button
        if st.sidebar.button(
            "🚪 Logout",
            type="secondary",
            use_container_width=True,
            help="Logout dari MIM3 Dashboard",
        ):
            LogoutHandler.show_logout_dialog()
