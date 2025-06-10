"""Commands untuk session management - pure database operations."""

from __future__ import annotations

from datetime import datetime

import streamlit as st
from loguru import logger
from sqlalchemy import select, update

from config.constants import DBConstants
from database.definitions import (
    get_role_table_definition,
    get_session_table_definition,
    get_user_table_definition,
)
from models.session.session_db import SessionCreate, SessionResult, SessionValidation


@st.cache_data(ttl=DBConstants.CACHE_TTL_SHORT, show_spinner="Creating session...")
def create_session(session_data: SessionCreate) -> SessionResult:
    """Create database session - return SessionResult."""
    try:
        conn = st.connection(DBConstants.CON_NAME, type=DBConstants.CON_TYPE)
        session_table = get_session_table_definition()

        with conn.session as s:
            # Insert session ke database
            insert_stmt = session_table.insert().values(
                user_id=session_data.user_id,
                session_token=session_data.session_token,
                ip_address=session_data.ip_address,
                user_agent=session_data.user_agent,
                expires_at=session_data.expires_at,
                created_at=datetime.now(),
                last_activity=datetime.now(),
                is_active=True,
            )

            result = s.execute(insert_stmt)
            session_id = result.lastrowid
            s.commit()

            logger.info(f"Database session created: ID {session_id}")
            return SessionResult.success_result(
                session_id=session_id,
                token=session_data.session_token,
                message="Database session berhasil dibuat",
            )

    except Exception as e:
        logger.error(f"Failed to create database session: {e}")
        return SessionResult.error_result("Gagal membuat database session")


def deactivate_session(session_token: str) -> bool:
    """Deactivate session by token - simple boolean return."""
    try:
        conn = st.connection(DBConstants.CON_NAME, type=DBConstants.CON_TYPE)
        session_table = get_session_table_definition()

        with conn.session as s:
            update_stmt = (
                update(session_table)
                .where(session_table.c.session_token == session_token)
                .values(is_active=False, last_activity=datetime.now())
            )

            result = s.execute(update_stmt)
            s.commit()

            if result.rowcount > 0:
                logger.info(f"Session deactivated: {session_token[:10]}...")
                return True
            else:
                logger.warning(f"Session not found: {session_token[:10]}...")
                return False

    except Exception as e:
        logger.error(f"Failed to deactivate session {session_token[:10]}...: {e}")
        return False


@st.cache_data(ttl=DBConstants.CACHE_TTL_SHORT, show_spinner="Validating session...")
def get_session_by_token(session_token: str) -> SessionValidation:
    """Get session with user info untuk validation."""
    try:
        conn = st.connection(DBConstants.CON_NAME, type=DBConstants.CON_TYPE)
        session_table = get_session_table_definition()
        user_table = get_user_table_definition()
        role_table = get_role_table_definition()

        with conn.session as s:
            # Join session, user, dan role untuk complete info
            stmt = (
                select(
                    session_table.c.user_id,
                    session_table.c.expires_at,
                    session_table.c.is_active,
                    user_table.c.username,
                    role_table.c.name.label("role_name"),
                )
                .select_from(
                    session_table.join(
                        user_table, session_table.c.user_id == user_table.c.id
                    ).join(role_table, user_table.c.role_id == role_table.c.id)
                )
                .where(session_table.c.session_token == session_token)
            )

            result = s.execute(stmt).first()

            if not result:
                return SessionValidation.invalid_session("Session tidak ditemukan")

            # Check if session active
            if not result.is_active:
                return SessionValidation.invalid_session("Session tidak aktif")

            # Check if expired
            if datetime.now() > result.expires_at:
                return SessionValidation.expired_session()

            # Valid session
            return SessionValidation.valid_session(
                user_id=result.user_id,
                username=result.username,
                role_name=result.role_name,
            )

    except Exception as e:
        logger.error(f"Failed to validate session {session_token[:10]}...: {e}")
        return SessionValidation.invalid_session("Error validasi session")


def update_session_activity(session_token: str) -> bool:
    """Update last activity untuk keep session alive."""
    try:
        conn = st.connection(DBConstants.CON_NAME, type=DBConstants.CON_TYPE)
        session_table = get_session_table_definition()

        with conn.session as s:
            update_stmt = (
                update(session_table)
                .where(
                    (session_table.c.session_token == session_token)
                    & (session_table.c.is_active)
                )
                .values(last_activity=datetime.now())
            )

            result = s.execute(update_stmt)
            s.commit()

            success = result.rowcount > 0
            if success:
                logger.debug(f"Session activity updated: {session_token[:10]}...")
            else:
                logger.warning(
                    f"Failed to update session activity: {session_token[:10]}..."
                )

            return success

    except Exception as e:
        logger.error(f"Failed to update session activity {session_token[:10]}...: {e}")
        return False


@st.cache_data(ttl=DBConstants.CACHE_TTL_SHORT)
def is_session_expired(session_token: str) -> bool:
    """Quick check if session is expired."""
    try:
        conn = st.connection(DBConstants.CON_NAME, type=DBConstants.CON_TYPE)
        session_table = get_session_table_definition()

        with conn.session as s:
            stmt = select(session_table.c.expires_at).where(
                session_table.c.session_token == session_token
            )

            result = s.execute(stmt).first()

            if not result:
                return True  # Session tidak ada = expired

            return datetime.now() > result.expires_at

    except Exception as e:
        logger.error(f"Failed to check session expiry {session_token[:10]}...: {e}")
        return True  # Failsafe - consider expired on error


# PINNED: Phase 1 - Hybrid session management
# ? [ ] pinned get_active_sessions() - admin monitoring dashboard
# ? [ ] pinned force_deactivate_user_sessions() - admin user control
