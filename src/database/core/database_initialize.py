"""Database service menggunakan Streamlit SQLConnection."""

from __future__ import annotations

import os

import streamlit as st
from loguru import logger
from sqlalchemy import text

from config.constants import DBConstants
from database.core.database_service import DatabaseService


@st.cache_resource(show_spinner="Connecting to database...")
def get_connection():
    """Get MIM3 database connection."""
    logger.info("Establishing database connection")
    from config.paths import AppPaths

    conn = st.connection(
        DBConstants.CON_NAME, type=DBConstants.CON_TYPE, url=AppPaths.DATABASE_URL
    )

    logger.success("Database connection established successfully")
    return conn


@st.cache_resource(show_spinner="Initializing database...")
def initialize_database() -> None:
    """Initialize database tables dan default data."""
    logger.info("Starting database initialization")

    conn = get_connection()

    try:
        with conn.session as s:
            # DDL operations
            create_tables(s)
            s.commit()

        # Seeding operations (separate transactions for safety)
        db_service = DatabaseService()
        roles_success = db_service.seed_required_roles()
        admin_success = db_service.create_default_admin()

        # ✅ Fix: conditional demo seeding
        demo_success = True
        if os.getenv("MIM3_SEED_DEMO_ACCOUNTS", "false").lower() == "true":
            demo_success = db_service.create_demo_accounts()

        if roles_success and admin_success and demo_success:
            logger.success("Database initialization completed successfully")
        else:
            logger.warning("Database initialization completed with warnings")

    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


def create_tables(session) -> None:
    """Create database tables if not exist."""
    logger.info("Creating database tables")
    try:
        # Create role table
        session.execute(
            text("""
            CREATE TABLE IF NOT EXISTS role (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(30) UNIQUE NOT NULL,
                description VARCHAR(100),
                is_active BOOLEAN DEFAULT TRUE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """)
        )
        logger.debug("Role table created/verified")

        # Create user table
        session.execute(
            text("""
            CREATE TABLE IF NOT EXISTS user_account (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(50) UNIQUE NOT NULL,
                name VARCHAR(50) NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                is_verified BOOLEAN DEFAULT FALSE,
                role_id INTEGER NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (role_id) REFERENCES role (id)
            )
            """)
        )
        logger.debug("User account table created/verified")

        # ✅ Create session table
        session.execute(
            text("""
            CREATE TABLE IF NOT EXISTS user_session (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_token VARCHAR(255) UNIQUE NOT NULL,
                ip_address VARCHAR(45),
                user_agent TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                expires_at DATETIME NOT NULL,
                last_activity DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE,
                FOREIGN KEY (user_id) REFERENCES user_account (id)
            )
            """)
        )
        logger.debug("User session table created/verified")

    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        raise
