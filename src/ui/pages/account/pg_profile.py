"""Simple user profile management - essential features only."""

# import streamlit as st


# def show_profile_page():
#     """Minimal profile page untuk MIM3 internal use."""
#     st.title("👤 User Profile")

#     # Basic info section
#     with st.container():
#         st.subheader("Basic Information")

#         with st.form("profile_form"):
#             display_name = st.text_input(
#                 "Display Name", value=st.session_state.get("username", "")
#             )

#             # Change password section
#             with st.expander("🔑 Change Password"):
#                 current_password = st.text_input("Current Password", type="password")
#                 new_password = st.text_input("New Password", type="password")
#                 confirm_password = st.text_input("Confirm Password", type="password")

#             if st.form_submit_button("Save Changes", type="primary"):
#                 # TODO: Implement save logic
#                 st.success("✅ Profile updated!")

#     # Session info (read-only)
#     with st.container():
#         st.subheader("Session Information")

#         col1, col2 = st.columns(2)
#         with col1:
#             st.metric("Role", st.session_state.get("user_role", "").title())
#         with col2:
#             if login_time := st.session_state.get("login_time"):
#                 st.metric("Login Time", login_time.strftime("%H:%M"))
