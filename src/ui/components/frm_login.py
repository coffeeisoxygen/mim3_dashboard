import streamlit as st

login = st.form("frm_login")
login.header("Login")

username = login.text_input("Username", placeholder="Enter your username")
password = login.text_input(
    "Password", type="password", placeholder="Enter your password"
)
confirm_password = login.text_input(
    "Confirm Password", type="password", placeholder="Confirm your password"
)

col1, col2 = login.columns(2)
login_clicked = col1.form_submit_button("Login")
clear_clicked = col2.form_submit_button("Clear")

if login_clicked:
    if username and password and confirm_password:
        if password == confirm_password:
            st.success(f"Welcome, {username}!")
        else:
            st.error("Passwords do not match.")
    else:
        st.error("Please fill in all fields.")

if clear_clicked:
    st.rerun()
