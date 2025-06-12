"""Sessions Context dengan robust fallback system - using REAL Streamlit APIs only."""

from typing import Any

import streamlit as st
from loguru import logger
from pydantic import BaseModel, Field


class SessionContext(BaseModel):
    """Rich session context menggunakan REAL st.context APIs."""

    # ✅ Real st.context properties
    client_ip: str | None = None  # st.context.ip_address
    access_url: str | None = None  # st.context.url
    timezone: str | None = None  # st.context.timezone
    timezone_offset: int | None = None  # st.context.timezone_offset
    locale: str | None = None  # st.context.locale
    is_embedded: bool = False  # st.context.is_embedded

    # From headers
    user_agent: str | None = None  # st.context.headers['user-agent']
    headers: dict[str, str] = Field(default_factory=dict)  # st.context.headers

    # From cookies
    cookies: dict[str, str] = Field(default_factory=dict)  # st.context.cookies

    @classmethod
    def from_streamlit_context(cls) -> "SessionContext":
        """Factory: Extract context using REAL Streamlit APIs with fallbacks."""
        # ✅ HARDCODED DEFAULTS untuk LAN deployment
        FALLBACK_VALUES = {
            "client_ip": "192.168.1.100",
            "user_agent": "MIM3Dashboard/1.0 (Windows NT 10.0; Win64; x64)",
            "access_url": "http://192.168.1.100:8501",
            "timezone": "Asia/Jakarta",
            "timezone_offset": -420,  # UTC+7
            "locale": "id-ID",
            "is_embedded": False,
        }

        def safe_get_context_attr(attr_name: str, fallback_key: str) -> Any:
            """Safely get REAL st.context attribute."""
            try:
                value = getattr(st.context, attr_name, None)
                if value is not None:
                    return value
                logger.debug(f"st.context.{attr_name} is None, using fallback")
                return FALLBACK_VALUES.get(fallback_key)
            except (AttributeError, RuntimeError) as e:
                logger.debug(
                    f"st.context.{attr_name} not available: {e}, using fallback"
                )
                return FALLBACK_VALUES.get(fallback_key)

        def safe_get_headers() -> tuple[dict[str, str], str | None]:
            """Get headers dan extract user-agent."""
            try:
                headers = getattr(st.context, "headers", None)
                if headers:
                    headers_dict = dict(headers)
                    user_agent = headers_dict.get(
                        "user-agent", FALLBACK_VALUES["user_agent"]
                    )
                    return headers_dict, user_agent
                logger.debug("st.context.headers is None, using fallback")
                # ✅ Fix: Ensure user_agent is always string
                fallback_user_agent = str(FALLBACK_VALUES["user_agent"])
                return {"user-agent": fallback_user_agent}, fallback_user_agent
            except (AttributeError, RuntimeError) as e:
                logger.debug(f"Failed to get headers: {e}, using fallback")
                # ✅ Fix: Ensure user_agent is always string
                fallback_user_agent = str(FALLBACK_VALUES["user_agent"])
                return {"user-agent": fallback_user_agent}, fallback_user_agent

        def safe_get_cookies() -> dict[str, str]:
            """Get cookies safely."""
            try:
                cookies = getattr(st.context, "cookies", None)
                return dict(cookies) if cookies else {}
            except (AttributeError, RuntimeError):
                return {}

        # ✅ Extract real context data
        headers_dict, extracted_user_agent = safe_get_headers()

        context = cls(
            # ✅ Using REAL st.context properties only
            client_ip=safe_get_context_attr("ip_address", "client_ip"),
            access_url=safe_get_context_attr("url", "access_url"),
            timezone=safe_get_context_attr("timezone", "timezone"),
            timezone_offset=safe_get_context_attr("timezone_offset", "timezone_offset"),
            locale=safe_get_context_attr("locale", "locale"),
            is_embedded=safe_get_context_attr("is_embedded", "is_embedded"),
            user_agent=extracted_user_agent,
            headers=headers_dict,
            cookies=safe_get_cookies(),
        )

        logger.debug(
            "Session context created using REAL APIs",
            client_ip=context.client_ip,
            timezone=context.timezone,
            is_local=context.is_local_access(),
        )

        return context

    @classmethod
    def create_default_local(cls) -> "SessionContext":
        """Create default context untuk local development."""
        return cls(
            client_ip="127.0.0.1",
            user_agent="MIM3Dashboard/1.0 Local Development",
            access_url="http://localhost:8501",
            timezone="Asia/Jakarta",
            timezone_offset=-420,
            locale="id-ID",
            headers={"user-agent": "MIM3Dashboard/1.0 Local Development"},
            cookies={},
            is_embedded=False,
        )

    @classmethod
    def create_default_lan(cls) -> "SessionContext":
        """Create default context untuk LAN access."""
        return cls(
            client_ip="192.168.1.100",
            user_agent="MIM3Dashboard/1.0 (Windows LAN)",
            access_url="http://192.168.1.100:8501",
            timezone="Asia/Jakarta",
            timezone_offset=-420,
            locale="id-ID",
            headers={"user-agent": "MIM3Dashboard/1.0 (Windows LAN)"},
            cookies={},
            is_embedded=False,
        )

    def get_display_timezone(self) -> str:
        """Get user-friendly timezone display."""
        if self.timezone:
            return self.timezone
        elif self.timezone_offset is not None:
            # Convert minutes to hours for display
            hours = abs(self.timezone_offset) // 60
            minutes = abs(self.timezone_offset) % 60
            sign = (
                "+" if self.timezone_offset <= 0 else "-"
            )  # Note: offset is negative for ahead of UTC
            return f"UTC{sign}{hours:02d}:{minutes:02d}"
        else:
            return "Unknown"

    def get_client_info(self) -> str:
        """Get formatted client information for logging."""
        parts = []
        if self.client_ip:
            parts.append(f"IP: {self.client_ip}")
        if self.user_agent:
            # Truncate long user agents
            ua = (
                self.user_agent[:50] + "..."
                if len(self.user_agent) > 50
                else self.user_agent
            )
            parts.append(f"UA: {ua}")
        if self.locale:
            parts.append(f"Locale: {self.locale}")

        return " | ".join(parts) if parts else "Unknown client"

    def is_local_access(self) -> bool:
        """Check if access is from localhost/local network."""
        if not self.client_ip:
            return True  # None means localhost in Streamlit

        # Check for localhost patterns
        localhost_patterns = ["127.", "::1", "localhost"]
        if any(pattern in self.client_ip for pattern in localhost_patterns):
            return True

        # Check for private network ranges
        private_ranges = ["192.168.", "10.", "172.16.", "172.17.", "172.18."]
        return any(self.client_ip.startswith(range_) for range_ in private_ranges)

    def get_deployment_type(self) -> str:
        """Detect deployment type berdasarkan context."""
        if not self.client_ip:
            return "localhost"

        if self.client_ip in {"127.0.0.1", "::1"}:
            return "localhost"

        if self.client_ip.startswith("192.168.1."):
            return "lan"

        if self.is_local_access():
            return "local_network"

        return "external"
