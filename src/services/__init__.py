"""Services package dengan caching untuk performance."""

import streamlit as st
from .auth_service import AuthService



@st.cache_resource(show_spinner="Initializing auth service...")
def get_auth_service() -> AuthService:
    """Get cached auth service instance."""
    return AuthService()


__all__ = ["AuthService", "get_auth_service"]
