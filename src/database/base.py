"""Database infrastructure initialization - tables only."""

from __future__ import annotations

import streamlit as st
from loguru import logger
from sqlalchemy.orm import DeclarativeBase

from config.constants import DBConstants


class Base(DeclarativeBase):
    """Base class for all database models.

    This class serves as the foundation for all database models in the application,
    providing a consistent interface and shared functionality.

    Args:
        DeclarativeBase (DeclarativeBase): The base class for SQLAlchemy declarative models.
    """

    pass


@st.cache_data(
    ttl=3600, show_spinner="Creating database tables..."
)  # ✅ Use cache_data
def create_tables() -> bool:
    """Create database tables if not exist - pure infrastructure."""
    logger.info("Creating database tables")

    try:
        conn = st.connection(DBConstants.CON_NAME, type=DBConstants.CON_TYPE)

        with conn.session as s:
            # ✅ Fix: Ensure bind is not None before calling create_all
            bind = s.bind
            if bind is None:
                # Fallback to connection engine
                bind = conn.engine

            Base.metadata.create_all(bind)
            s.commit()

        logger.success("Database tables created/verified successfully")
        return True

    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        raise


def initialize_database() -> None:
    """Initialize database infrastructure only."""
    logger.info("Initializing database infrastructure")
    success = create_tables()  # ✅ Cache akan skip re-execution  # noqa: F841
    logger.info("Database infrastructure ready")


# REMINDER: Business logic (roles/admin) now handled by bootstrap.py
# TODO: Hapus file ent_roles.py dan ent_usersession.py setelah refactor selesai
