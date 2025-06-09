"""Authentication service untuk MIM3 Dashboard."""

from __future__ import annotations

import bcrypt
import streamlit as st
from loguru import logger

from core.messages import AuthMessages
from core.us_session import clear_user_session, set_user_session
from database.auth_commands import get_user_by_username
from models.user import AuthResult, UserLogin, UserSession


class AuthService:
    """Service untuk menangani complete authentication flow."""

    def __init__(self):
        """Initialize auth service."""
        pass

    def perform_login(self, username: str, password: str) -> tuple[bool, str]:
        """Handle complete login flow.

        Args:
            username: User's username
            password: User's password

        Returns:
            Tuple of (success: bool, message: str)
        """
        # Input validation
        if not username or not password:
            return False, AuthMessages.REQUIRED_FIELDS

        try:
            # Create login data
            login_data = UserLogin(username=username, password=password)

            # Authenticate
            result = self._authenticate(login_data)

            if result.success and result.user_session:
                set_user_session(result.user_session)
                logger.info(f"User login: {result.user_session.username}")
                return True, AuthMessages.LOGIN_SUCCESS
            else:
                return False, result.error_message or AuthMessages.LOGIN_FAILED

        except ValueError as e:
            logger.error(f"Login validation error: {e}")
            return False, AuthMessages.REQUIRED_FIELDS
        except Exception as e:
            logger.error(f"Login error: {e}")
            return False, AuthMessages.SYSTEM_ERROR

    def perform_logout(self) -> tuple[bool, str]:
        """Handle complete logout flow."""
        try:
            username = st.session_state.get("username", "User")
            clear_user_session()
            logger.info(f"User logout: {username}")
            return True, f"{username} {AuthMessages.LOGOUT_SUCCESS}"
        except Exception as e:
            logger.error(f"Logout error: {e}")
            return False, AuthMessages.SYSTEM_ERROR

    def _authenticate(self, login_data: UserLogin) -> AuthResult:
        """Internal authentication logic."""
        try:
            logger.info(f"Login attempt: {login_data.username}")

            # Database operation
            user_data = get_user_by_username(login_data.username)

            if not user_data:
                logger.warning(f"User not found: {login_data.username}")
                return AuthResult(
                    success=False, error_message=AuthMessages.LOGIN_FAILED
                )

            # Password verification
            logger.debug("Verifying password...")
            password_valid = bcrypt.checkpw(
                login_data.password.encode("utf-8"),
                user_data["password_hash"].encode("utf-8"),
            )

            if not password_valid:
                logger.warning(f"Invalid password for: {login_data.username}")
                return AuthResult(
                    success=False, error_message=AuthMessages.LOGIN_FAILED
                )

            # Create session
            user_session = UserSession.from_db_data(user_data)
            logger.info(f"Authentication successful for: {login_data.username}")
            return AuthResult(success=True, user_session=user_session)

        except ValueError as e:
            # Pydantic validation errors
            logger.error(f"Data validation error: {e}")
            return AuthResult(success=False, error_message="Invalid user data format")

        except KeyError as e:
            # Missing database fields
            logger.error(f"Database schema error: {e}")
            return AuthResult(success=False, error_message=AuthMessages.SYSTEM_ERROR)

        except Exception as e:
            # Unexpected system errors
            logger.error(f"Unexpected authentication error: {e}")
            return AuthResult(success=False, error_message=AuthMessages.SYSTEM_ERROR)
