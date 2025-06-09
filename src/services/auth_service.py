"""Authentication service untuk MIM3 Dashboard."""

from __future__ import annotations

import bcrypt
from loguru import logger

from core.messages import AuthMessages
from database.auth_commands import get_user_by_username
from models.user import AuthResult, UserLogin, UserSession


class AuthService:
    """Service untuk menangani authentication logic dengan database."""

    def __init__(self):
        """Initialize auth service - no database dependencies."""
        pass

    def authenticate(self, login_data: UserLogin) -> AuthResult:
        """Authenticate user dengan database lookup."""
        try:
            logger.info(f"Login attempt: {login_data.username}")

            # ✅ Use command function
            user_data = get_user_by_username(login_data.username)

            if not user_data:
                logger.warning(f"User not found: {login_data.username}")
                return AuthResult(
                    success=False,
                    error_message=AuthMessages.LOGIN_FAILED,
                )

            # Verify password
            logger.debug("Verifying password...")
            password_valid = bcrypt.checkpw(
                login_data.password.encode("utf-8"),
                user_data["password_hash"].encode("utf-8"),
            )

            if not password_valid:
                logger.warning(f"Invalid password for: {login_data.username}")
                return AuthResult(
                    success=False,
                    error_message=AuthMessages.LOGIN_FAILED,
                )

            # Create session data
            user_session = UserSession.from_db_data(user_data)

            logger.info(f"Authentication successful for: {login_data.username}")
            return AuthResult(success=True, user_session=user_session)

        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return AuthResult(
                success=False,
                error_message=AuthMessages.SYSTEM_ERROR,
            )
