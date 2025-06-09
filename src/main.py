"""main.py - Entry point for the MIM3 Dashboard application."""

import streamlit as st

from core.app import App

st.set_page_config(
    page_title="MIM3 Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ✅ Single import


def main():
    """Main application entry point."""
    app = App()
    app.run()


if __name__ == "__main__":
    main()
