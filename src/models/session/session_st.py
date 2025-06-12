"""Streamlit session state management - decoupled from user domain."""

from __future__ import annotations

from typing import Any, Protocol

import streamlit as st
from loguru import logger


class StreamlitSessionData(Protocol):
    """Protocol untuk streamlit session - minimal dependencies."""

    user_id: int
    username: str
    display_name: str
    role: str
    session_token: str | None


class StreamlitSessionManager:
    """Manage Streamlit session state - framework specific."""

    @property
    def streamlit_session_id(self) -> str:
        """Generate consistent session ID dari available context."""
        try:
            # ✅ Method 1: Use IP + User-Agent untuk generate consistent ID
            context_data = []

            # Get IP address (None for localhost)
            try:
                ip = st.context.ip_address
                if ip:
                    context_data.append(ip)
                else:
                    context_data.append("localhost")  # Default for local access
            except (AttributeError, RuntimeError):
                context_data.append("localhost")

            # Get User-Agent from headers
            try:
                headers = st.context.headers
                if headers and "user-agent" in headers:
                    ua = headers.get("user-agent", "")[:50]  # First 50 chars
                    if ua:
                        context_data.append(ua)
                else:
                    context_data.append("unknown_browser")
            except (AttributeError, RuntimeError):
                context_data.append("unknown_browser")

            # Get URL untuk additional uniqueness
            try:
                url = st.context.url
                if url:
                    # Extract port atau path untuk uniqueness
                    import urllib.parse

                    parsed = urllib.parse.urlparse(url)
                    context_data.append(f"{parsed.netloc}{parsed.path}")
                else:
                    context_data.append("default_url")
            except (AttributeError, RuntimeError):
                context_data.append("default_url")

            # ✅ Generate consistent hash dari context
            if context_data:
                import hashlib

                context_str = "|".join(context_data)

                session_id = hashlib.sha256(context_str.encode()).hexdigest()[:16]
                logger.debug(
                    "Generated session ID from context",
                    session_id=session_id,
                    context_parts=len(context_data),
                )
                return session_id

            # ✅ Fallback: timestamp-based ID
            import time

            fallback_id = f"session_{int(time.time())}"
            logger.debug("Using timestamp-based session ID", session_id=fallback_id)
            return fallback_id

        except Exception as e:
            logger.debug("Failed to generate session ID: {error}", error=e)
            # ✅ Ultimate fallback
            return "local_session_default"

    @logger.catch
    def set_session(self, data: StreamlitSessionData) -> bool:
        """Set session dengan minimal user coupling."""
        if data is None:
            logger.error("Cannot set session: data is None")
            return False

        try:
            st.session_state.authenticated = True
            st.session_state.user_id = data.user_id
            st.session_state.username = data.username
            st.session_state.display_name = data.display_name
            st.session_state.user_role = data.role
            st.session_state.session_token = data.session_token
            st.session_state.session_id = self.streamlit_session_id

            logger.opt(lazy=True).debug(
                "Streamlit session set for user: {user} with role: {role}",
                user=lambda: data.username,
                role=lambda: data.role,
            )
            return True

        except Exception as e:
            logger.error("Failed to set streamlit session: {error}", error=e)
            self.clear_session()
            return False

    @logger.catch
    def clear_session(self) -> bool:
        """Clear semua session data."""
        session_keys = [
            "authenticated",
            "user_id",
            "username",
            "display_name",
            "user_role",
            "session_token",
            "session_id",
        ]

        cleared = 0
        for key in session_keys:
            if key in st.session_state:
                st.session_state.pop(key, None)
                cleared += 1

        logger.debug("Cleared {count} streamlit session keys", count=cleared)
        return True

    def get_session_info(self) -> dict[str, Any]:
        """Get current session info dengan context enrichment."""
        # ✅ Basic session info
        session_info = {
            "streamlit_id": self.streamlit_session_id,
            "user_id": st.session_state.get("user_id"),
            "username": st.session_state.get("username"),
            "display_name": st.session_state.get("display_name"),
            "role": st.session_state.get("user_role"),
            "authenticated": st.session_state.get("authenticated", False),
            "session_token": st.session_state.get("session_token"),
        }

        # ✅ Enrich dengan context info (optional)
        try:
            session_info.update(
                {
                    "client_ip": getattr(st.context, "ip_address", None),
                    "access_url": getattr(st.context, "url", None),
                    "timezone": getattr(st.context, "timezone", None),
                    "locale": getattr(st.context, "locale", None),
                    "is_embedded": getattr(st.context, "is_embedded", False),
                }
            )
        except (AttributeError, RuntimeError):
            # Context tidak tersedia, skip enrichment
            pass

        return session_info

    def is_authenticated(self) -> bool:
        """Check authentication status."""
        return st.session_state.get("authenticated", False)

    def get_context_summary(self) -> dict[str, Any]:
        """Get Streamlit context summary untuk debugging."""
        # ✅ Explicit type annotation untuk features
        features_dict: dict[str, dict[str, Any]] = {}

        summary: dict[str, Any] = {
            "context_available": False,
            "features": features_dict,  # Use the typed dict
            "session_id": self.streamlit_session_id,
        }

        # Test each context feature
        context_features = [
            "ip_address",
            "headers",
            "url",
            "timezone",
            "timezone_offset",
            "locale",
            "cookies",
            "is_embedded",
        ]

        try:
            # Test basic context access
            _ = st.context
            summary["context_available"] = True

            for feature in context_features:
                try:
                    value = getattr(st.context, feature, None)
                    # ✅ Assign to the properly typed features_dict
                    features_dict[feature] = {
                        "available": True,
                        "has_value": value is not None,
                        "type": type(value).__name__ if value is not None else "None",
                    }
                except Exception as e:
                    features_dict[feature] = {"available": False, "error": str(e)}

        except Exception as e:
            summary["context_error"] = str(e)

        return summary


# Singleton instance
_streamlit_session = StreamlitSessionManager()


# ✅ Backward compatibility API
def set_user_session(data: StreamlitSessionData) -> bool:
    """Set streamlit session - backward compatible."""
    return _streamlit_session.set_session(data)


def clear_user_session() -> bool:
    """Clear streamlit session - backward compatible."""
    return _streamlit_session.clear_session()


def get_current_user() -> dict[str, Any]:
    """Get current session info - backward compatible."""
    return _streamlit_session.get_session_info()


def is_session_valid() -> bool:
    """Check if session valid - backward compatible."""
    return _streamlit_session.is_authenticated()


def get_streamlit_context_debug() -> dict[str, Any]:
    """Get context debug info untuk troubleshooting."""
    return _streamlit_session.get_context_summary()


# REMINDER: Using only REAL Streamlit APIs dari official docs
# TODO: Remove imaginary API calls from other session files
# PINNED: Session ID generated dari IP + User-Agent + URL untuk consistency
# PINNED: Context enrichment optional - fallback gracefully jika tidak tersedia
