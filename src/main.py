"""main.py - Entry point for the MIM3 Dashboard application."""

import streamlit as st
from dotenv import load_dotenv

from core.app import App

st.set_page_config(
    page_title="MIM3 Dashboard",
    page_icon=":streamlit:",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_dotenv(override=True)  # Load environment variables from .env file


def main():
    """Main application entry point."""
    app = App()
    app.run()


if __name__ == "__main__":
    main()
