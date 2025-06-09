"""Services package dengan caching untuk performance."""

import streamlit as st
from .auth_service import AuthService
from .auth_flow_service import AuthFlowService


@st.cache_resource(show_spinner="Initializing auth service...")
def get_auth_service() -> AuthService:
    """Get cached auth service instance."""
    return AuthService()


@st.cache_resource(show_spinner="Initializing auth flow...")
def get_auth_flow_service() -> AuthFlowService:
    """Get cached auth flow service instance."""
    return AuthFlowService()


__all__ = ["AuthService", "AuthFlowService", "get_auth_service", "get_auth_flow_service"]
