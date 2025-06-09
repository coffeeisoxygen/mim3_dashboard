"""Authentication service untuk MIM3 Dashboard."""

from __future__ import annotations

import bcrypt
import streamlit as st
from loguru import logger
from sqlalchemy import text

from core.messages import AuthMessages
from models.md_user import AuthResult, UserLogin, UserRole, UserSession


@st.cache_data(ttl=300)
def get_user_by_username(username: str) -> dict | None:
    """Get user data dari database - function level untuk proper caching."""
    conn = st.connection("mim3_db", type="sql")

    stmt = text("""
        SELECT u.id, u.username, u.name, u.password_hash,
               u.is_verified, r.name as role_name
        FROM user_account u
        JOIN role r ON u.role_id = r.id
        WHERE u.username = :username AND u.is_verified = 1
    """)

    result = conn.query(str(stmt), params={"username": username}, ttl=300)
    return result.iloc[0].to_dict() if len(result) > 0 else None


class AuthService:
    """Service untuk menangani authentication logic dengan database."""

    def __init__(self):
        """Initialize auth service dengan database connection."""
        try:
            self.conn = st.connection("mim3_db", type="sql")
            # Test connection
            test_query = self.conn.query("SELECT 1 as test", ttl=0)
            logger.success(f"Database connection test: {test_query}")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise

    def authenticate(self, login_data: UserLogin) -> AuthResult:
        """Authenticate user dengan database lookup."""
        session_id = getattr(st.session_state, "session_id", "unknown")

        try:
            logger.info(f"Login attempt: {login_data.username} [session: {session_id}]")

            user_data = get_user_by_username(login_data.username)

            if not user_data:
                logger.warning(
                    f"User not found: {login_data.username} [session: {session_id}]"
                )
                return AuthResult(
                    success=False,
                    error_message=AuthMessages.LOGIN_FAILED,
                )

            logger.debug("Verifying password...")
            if not self._verify_password(
                login_data.password, user_data["password_hash"]
            ):
                logger.warning(f"Invalid password for user: {login_data.username}")
                return AuthResult(
                    success=False,
                    error_message=AuthMessages.LOGIN_FAILED,
                )

            logger.info(f"Authentication successful for: {login_data.username}")
            # Create session dengan role mapping
            session = UserSession(
                user_id=user_data["id"],
                username=user_data["username"],
                role=self._map_role(user_data["role_name"]),
            )

            logger.info(
                f"Login successful: {login_data.username} [session: {session_id}]"
            )
            return AuthResult(success=True, user_session=session)

        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return AuthResult(success=False, error_message=AuthMessages.SYSTEM_ERROR)

    def _map_role(self, role_name: str) -> UserRole:
        """Map database role ke UserRole type."""
        role_mapping: dict[str, UserRole] = {
            "admin": "admin",
            "operator": "operator",
            "team_indosat": "team_indosat",
        }
        return role_mapping.get(role_name, "operator")  # Default fallback

    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password dengan bcrypt hash dari database."""
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
