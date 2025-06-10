"""Authentication service untuk MIM3 Dashboard."""

from __future__ import annotations

import bcrypt
from loguru import logger

from core.messages import AuthMessages
from database.commands.auth_commands import get_user_by_username
from models.user.us_onauth import AccountLogin, ActiveSession, LoginResult
from services.session_service import SessionService


class AuthService:
    """Service untuk menangani complete authentication flow."""

    def perform_login(self, username: str, password: str) -> tuple[bool, str]:
        """Handle complete login flow with early return pattern."""
        # Early validation
        if not username or not password:
            return False, AuthMessages.REQUIRED_FIELDS

        try:
            login_data = AccountLogin(username=username, password=password)
            result = self._authenticate(login_data)

            # Early failure return
            if not result.success:
                return False, result.error_message or AuthMessages.LOGIN_FAILED

            # Early missing session return
            if not result.user_session:
                return False, AuthMessages.SYSTEM_ERROR

            # ✅ Capture request info untuk audit trail
            request_info = {
                "ip_address": "127.0.0.1",  # Local Streamlit app
                "user_agent": "Streamlit Dashboard",
            }

            # Delegate session management to session service
            session_service = SessionService()
            session_result = session_service.create_user_session(
                result.user_session,
                request_info,  # ✅ Pass request info
            )

            if not session_result.success:
                return False, session_result.message

            logger.info(f"User login successful: {result.user_session.username}")
            return True, AuthMessages.LOGIN_SUCCESS

        except ValueError as e:
            logger.error(f"Login validation error: {e}")
            return False, AuthMessages.REQUIRED_FIELDS
        except Exception as e:
            logger.error(f"Login error: {e}")
            return False, AuthMessages.SYSTEM_ERROR

    def perform_logout(self) -> tuple[bool, str]:
        """Handle complete logout flow."""
        try:
            # ✅ Get session token dari streamlit session
            import streamlit as st

            session_token = st.session_state.get("session_token")

            # Delegate session clearing to session service
            session_service = SessionService()
            success = session_service.clear_user_session(session_token)  # ✅ Pass token

            if success:
                logger.info("User logout successful")
                return True, AuthMessages.LOGOUT_SUCCESS
            else:
                return False, "Logout gagal"

        except Exception as e:
            logger.error(f"Logout error: {e}")
            return False, AuthMessages.SYSTEM_ERROR

    def _authenticate(self, login_data: AccountLogin) -> LoginResult:
        """Internal authentication with early returns."""
        try:
            logger.debug("=== AUTHENTICATION START ===")
            logger.debug(f"Login attempt for username: '{login_data.username}'")
            logger.debug(f"Password length: {len(login_data.password)} chars")

            # Get user data with early return
            logger.debug("Attempting to fetch user from database...")
            user_data = get_user_by_username(login_data.username)

            if not user_data:
                logger.warning(f"User not found in database: {login_data.username}")
                logger.debug("=== AUTHENTICATION END (USER NOT FOUND) ===")
                return LoginResult(
                    success=False, error_message=AuthMessages.LOGIN_FAILED
                )

            # Debug user data structure
            logger.debug("User data retrieved successfully")
            logger.debug(f"User data keys: {list(user_data.keys())}")
            logger.debug(f"User ID: {user_data.get('id')}")
            logger.debug(f"Username: {user_data.get('username')}")
            logger.debug(f"Name: {user_data.get('name')}")
            logger.debug(f"Role ID: {user_data.get('role_id')}")
            logger.debug(f"Role Name: {user_data.get('role_name')}")
            logger.debug(f"Has password_hash: {'password_hash' in user_data}")

            # Verify password
            logger.debug("Starting password verification...")
            try:
                stored_hash = user_data["password_hash"]
                logger.debug(f"Stored hash type: {type(stored_hash)}")
                logger.debug(
                    f"Stored hash length: {len(stored_hash) if stored_hash else 0}"
                )

                password_valid = bcrypt.checkpw(
                    login_data.password.encode("utf-8"),
                    stored_hash.encode("utf-8"),
                )
                logger.debug(f"Password verification result: {password_valid}")

            except Exception as pwd_error:
                logger.error(f"Password verification failed: {pwd_error}")
                logger.debug("=== AUTHENTICATION END (PASSWORD ERROR) ===")
                return LoginResult(
                    success=False, error_message=AuthMessages.SYSTEM_ERROR
                )

            if not password_valid:
                logger.warning(f"Invalid password for user: {login_data.username}")
                logger.debug("=== AUTHENTICATION END (INVALID PASSWORD) ===")
                return LoginResult(
                    success=False, error_message=AuthMessages.LOGIN_FAILED
                )

            # Success path - create session object
            logger.debug("Creating ActiveSession object...")
            try:
                user_session = ActiveSession(
                    user_id=user_data["id"],
                    username=user_data["username"],
                    name=user_data["name"],
                    role_id=user_data["role_id"],
                    role_name=user_data["role_name"],
                    session_token=None,
                )
                logger.debug("ActiveSession created successfully")
                logger.debug(f"Session user_id: {user_session.user_id}")
                logger.debug(f"Session username: {user_session.username}")

            except Exception as session_error:
                logger.error(f"Failed to create ActiveSession: {session_error}")
                logger.debug("=== AUTHENTICATION END (SESSION CREATION ERROR) ===")
                return LoginResult(
                    success=False, error_message=AuthMessages.SYSTEM_ERROR
                )

            logger.info(f"Authentication successful: {login_data.username}")
            logger.debug("=== AUTHENTICATION END (SUCCESS) ===")
            return LoginResult(success=True, user_session=user_session)

        except KeyError as e:
            logger.error(f"Missing required database field: {e}")
            logger.debug(
                f"Available user_data keys: {list(user_data.keys()) if 'user_data' in locals() else 'user_data not available'}"  # type: ignore
            )
            logger.debug("=== AUTHENTICATION END (MISSING FIELD) ===")
            return LoginResult(success=False, error_message=AuthMessages.DATABASE_ERROR)
        except Exception as e:
            logger.error(f"Unexpected authentication error: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            logger.debug("=== AUTHENTICATION END (UNEXPECTED ERROR) ===")
            return LoginResult(success=False, error_message=AuthMessages.SYSTEM_ERROR)
