"""Database infrastructure initialization - tables only."""

from __future__ import annotations

import streamlit as st
from loguru import logger
from sqlalchemy import text

from config.constants import DBConstants


@st.cache_resource(show_spinner="Creating database tables...")
def create_tables() -> None:
    """Create database tables if not exist - pure infrastructure."""
    logger.info("Creating database tables")

    try:
        conn = st.connection(DBConstants.CON_NAME, type=DBConstants.CON_TYPE)

        with conn.session as s:
            # Create role table
            s.execute(
                text("""
                CREATE TABLE IF NOT EXISTS role (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(30) UNIQUE NOT NULL,
                    description VARCHAR(100),
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at DATETIME NOT NULL
                )
            """)
            )

            # Create user table
            s.execute(
                text("""
                CREATE TABLE IF NOT EXISTS user_account (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    name VARCHAR(50) NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    is_verified BOOLEAN DEFAULT FALSE,
                    is_active BOOLEAN DEFAULT TRUE,
                    role_id INTEGER NOT NULL,
                    created_at DATETIME NOT NULL,
                    updated_at DATETIME NOT NULL,
                    FOREIGN KEY (role_id) REFERENCES role (id)
                )
            """)
            )

            # Create session table
            s.execute(
                text("""
                CREATE TABLE IF NOT EXISTS user_session (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    session_token VARCHAR(255) UNIQUE NOT NULL,
                    ip_address VARCHAR(45),
                    user_agent TEXT,
                    created_at DATETIME NOT NULL,
                    expires_at DATETIME NOT NULL,
                    last_activity DATETIME NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    FOREIGN KEY (user_id) REFERENCES user_account (id)
                )
            """)
            )

            s.commit()
            logger.success("Database tables created/verified successfully")

    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        raise


def initialize_database() -> None:
    """Initialize database infrastructure only."""
    logger.info("Initializing database infrastructure")
    create_tables()
    logger.info("Database infrastructure ready")


# REMINDER: Business logic (roles/admin) now handled by bootstrap.py
