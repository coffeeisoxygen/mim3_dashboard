"""Commands untuk session management."""

from __future__ import annotations

from datetime import datetime

import streamlit as st
from loguru import logger
from sqlalchemy import insert, select, update

from config.constants import DBConstants
from database.definitions import (
    get_role_table_definition,
    get_session_table_definition,
    get_user_table_definition,
)
from models.session.session_db import SessionCreate, SessionRead, SessionToken


def create_session(session_data: SessionCreate) -> tuple[bool, str | None, int | None]:
    """Create new session in database."""
    try:
        conn = st.connection(DBConstants.CON_NAME, type=DBConstants.CON_TYPE)

        # Generate secure token
        token = SessionToken.generate()
        session_table = get_session_table_definition()

        with conn.session as s:
            stmt = insert(session_table).values(
                user_id=session_data.user_id,
                session_token=token.session_token,
                ip_address=session_data.ip_address,
                user_agent=session_data.user_agent,
                expires_at=session_data.expires_at,
            )

            result = s.execute(stmt)
            s.commit()
            session_id = result.lastrowid

        logger.info(f"Session created: {session_id}")
        return True, token.session_token, session_id

    except Exception as e:
        logger.error(f"Failed to create session: {e}")
        return False, None, None


def get_active_session(session_token: str) -> SessionRead | None:
    """Get active session by token with proper type safety."""
    # Validate token format first
    if not session_token or len(session_token) < 32:
        logger.warning("Invalid session token format")
        return None

    try:
        conn = st.connection(DBConstants.CON_NAME, type=DBConstants.CON_TYPE)

        # Use SQLAlchemy ORM instead of raw SQL
        session_table = get_session_table_definition()
        user_table = get_user_table_definition()
        role_table = get_role_table_definition()

        with conn.session as s:
            stmt = (
                select(
                    session_table.c.id,
                    session_table.c.user_id,
                    session_table.c.session_token,
                    session_table.c.ip_address,
                    session_table.c.user_agent,
                    session_table.c.expires_at,
                    session_table.c.last_activity,
                    session_table.c.is_active,
                    user_table.c.username,
                    user_table.c.name,
                    role_table.c.name.label("role_name"),
                )
                .select_from(
                    session_table.join(
                        user_table, session_table.c.user_id == user_table.c.id
                    ).join(role_table, user_table.c.role_id == role_table.c.id)
                )
                .where(
                    (session_table.c.session_token == session_token)
                    & (session_table.c.is_active == 1)
                    & (session_table.c.expires_at > datetime.now())
                )
            )

            result = s.execute(stmt).first()

            if result:
                # Convert to Pydantic model for type safety
                return SessionRead(
                    id=result.id,
                    user_id=result.user_id,
                    session_token=result.session_token,
                    ip_address=result.ip_address,
                    user_agent=result.user_agent,
                    expires_at=result.expires_at,
                    last_activity=result.last_activity,
                    is_active=bool(result.is_active),
                    username=result.username,
                    name=result.name,
                    role_name=result.role_name,
                )

            return None

    except Exception as e:
        logger.error(f"Failed to get session: {e}")
        return None


def deactivate_session(session_token: str) -> bool:
    """Deactivate session (logout)."""
    try:
        conn = st.connection(DBConstants.CON_NAME, type=DBConstants.CON_TYPE)

        session_table = get_session_table_definition()

        with conn.session as s:
            stmt = (
                update(session_table)
                .where(session_table.c.session_token == session_token)
                .values(is_active=0)
            )
            s.execute(stmt)
            s.commit()

        logger.info(f"Session deactivated: {session_token[:8]}...")
        return True

    except Exception as e:
        logger.error(f"Failed to deactivate session: {e}")
        return False


def update_session_activity(session_token: str) -> bool:
    """Update last activity timestamp."""
    try:
        conn = st.connection(DBConstants.CON_NAME, type=DBConstants.CON_TYPE)
        session_table = get_session_table_definition()

        with conn.session as s:
            stmt = (
                update(session_table)
                .where(session_table.c.session_token == session_token)
                .values(last_activity=datetime.now())
            )
            s.execute(stmt)
            s.commit()

        return True

    except Exception as e:
        logger.error(f"Failed to update session activity: {e}")
        return False
