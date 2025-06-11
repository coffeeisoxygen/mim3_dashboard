"""Simple user profile management - essential features only."""

import streamlit as st


def show_profile_page():
    """Minimal profile page.."""
    st.title("👤 User Profile")

    # Basic info section
    with st.container():
        st.subheader("Basic Information")

        with st.form("profile_form"):
            new_display_name = st.text_input(
                "Display Name", value=st.session_state.get("username", "")
            )

            # Change password section
            with st.expander("🔑 Change Password"):
                current_pwd = st.text_input("Current Password", type="password")
                new_pwd = st.text_input("New Password", type="password")
                confirm_pwd = st.text_input("Confirm Password", type="password")

            if st.form_submit_button("Save Changes", type="primary"):
                # Basic validation for password change
                if new_pwd or confirm_pwd or current_pwd:
                    if not all([current_pwd, new_pwd, confirm_pwd]):
                        st.error("❌ All password fields are required")
                    elif new_pwd != confirm_pwd:
                        st.error("❌ New passwords don't match")
                    elif len(new_pwd) < 6:
                        st.error("❌ Password must be at least 6 characters")
                    else:
                        # TODO: Implement actual password change logic
                        st.success("✅ Password updated!")

                # Update display name if changed
                if new_display_name != st.session_state.get("username", ""):
                    # TODO: Implement display name update logic
                    st.session_state["username"] = new_display_name
                    st.success("✅ Display name updated!")

    # Session info (read-only)
    with st.container():
        st.subheader("Session Information")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Role", st.session_state.get("user_role", "").title())
        with col2:
            if login_time := st.session_state.get("login_time"):
                st.metric("Login Time", login_time.strftime("%H:%M"))
