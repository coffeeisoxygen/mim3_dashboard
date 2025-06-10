"""Database initialization service."""

from __future__ import annotations

import os

import streamlit as st
from loguru import logger
from sqlalchemy import text

from config.constants import DBConstants


def create_tables() -> None:
    """Create database tables if not exist."""
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
            logger.debug("Role table created/verified")

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
            logger.debug("User account table created/verified")

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
            logger.debug("User session table created/verified")

            s.commit()
            logger.success("All tables created/verified successfully")

    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        raise


@st.cache_resource(show_spinner="Initializing database...")
def initialize_database() -> None:
    """Initialize database dengan default data."""
    logger.info("Starting database initialization")

    try:
        # 1. Create tables first
        create_tables()

        # 2. Then seed data
        from services.register_service import RegistrationService
        from services.role_service import RoleService

        # Seed system roles
        role_service = RoleService()
        roles_success = role_service.seed_system_roles()
        logger.debug(f"Roles seeded successfully: {roles_success}")

        # Create system admin
        registration_service = RegistrationService()
        admin_success = registration_service.create_system_admin()

        # Demo accounts (optional)
        demo_success = True
        if os.getenv("MIM3_SEED_DEMO_ACCOUNTS", "false").lower() == "true":
            demo_success = registration_service.create_demo_accounts()

        if roles_success and admin_success and demo_success:
            logger.success("Database initialization completed successfully")
        else:
            logger.warning("Database initialization completed with warnings")

    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise
