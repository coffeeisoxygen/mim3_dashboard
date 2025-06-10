"""Session service untuk hybrid session management."""

from __future__ import annotations

from loguru import logger

from database.commands.session_commands import create_session, deactivate_session
from models.session.session_db import SessionCreate, SessionResult
from models.session.session_st import clear_user_session, set_user_session
from models.user.us_onauth import ActiveSession


class SessionService:
    """Service untuk hybrid session management."""

    def create_user_session(
        self, user_session: ActiveSession, request_info: dict | None = None
    ) -> SessionResult:
        """Create hybrid session (database + streamlit)."""
        try:
            # Create database session untuk audit trail
            session_data = SessionCreate.create_new(
                user_id=user_session.user_id,
                hours=8,  # 8 jam kerja
            )

            # Add request info if available
            if request_info:
                session_data.ip_address = request_info.get("ip_address")
                session_data.user_agent = request_info.get("user_agent")

            success, token, session_id = create_session(session_data)

            if not success:
                return SessionResult(
                    success=False,
                    session_id=None,
                    message="Gagal membuat session database",
                )

            # ✅ Update user_session dengan token dari database
            user_session.session_token = token

            # Set streamlit session dengan token
            set_user_session(user_session)

            logger.info(f"Hybrid session created for user: {user_session.username}")
            return SessionResult(
                success=True, session_id=session_id, message="Session berhasil dibuat"
            )

        except Exception as e:
            logger.error(f"Failed to create user session: {e}")
            return SessionResult(
                success=False,
                message="Error sistem saat membuat session",
                session_id=None,
            )

    def clear_user_session(self, session_token: str | None = None) -> bool:
        """Clear hybrid session (database + streamlit)."""
        logger.debug(
            f"Starting session clear - Token provided: {session_token is not None}"
        )

        try:
            # Clear streamlit session
            logger.debug("Clearing Streamlit session state")
            clear_user_session()
            logger.info("Streamlit session cleared successfully")

            # Deactivate database session if token provided
            if session_token:
                logger.debug(
                    f"Deactivating database session with token: {session_token[:10]}..."
                )
                deactivate_session(session_token)
                logger.info(
                    f"Database session deactivated for token: {session_token[:10]}..."
                )
            else:
                logger.debug(
                    "No session token provided, skipping database session deactivation"
                )

            logger.info("User session cleared successfully")
            return True

        except Exception as e:
            logger.error(f"Exception during session clear: {type(e).__name__}: {e}")
            logger.debug(
                f"Session clear failed with token: {session_token[:10] if session_token else 'None'}, Error: {e}",
                exc_info=True,
            )
            return False

    # TODO: Phase 2 - Admin session monitoring (owner request)
    # def get_active_sessions(self) -> list[SessionView]:
    #     """Get all active sessions untuk admin monitoring."""
    #     pass

    # def force_logout_user(self, user_id: int) -> bool:
    #     """Force logout user untuk admin control."""
    #     pass
