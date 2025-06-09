"""Database service menggunakan Streamlit SQLConnection."""

from __future__ import annotations

import bcrypt
import streamlit as st
from loguru import logger
from sqlalchemy import text

from models.md_user import UserCreate


@st.cache_resource(show_spinner="Connecting to database...")
def get_connection():
    """Get MIM3 database connection."""
    logger.info("Establishing database connection")
    from config.paths import AppPaths

    conn = st.connection("mim3_db", type="sql", url=AppPaths.DATABASE_URL)

    logger.success("Database connection established successfully")
    return conn


def initialize_database() -> None:
    """Initialize database tables dan default data."""
    logger.info("Starting database initialization")
    conn = get_connection()

    try:
        with conn.session as s:
            logger.debug("Creating database tables")

            # Create role table
            s.execute(
                text("""
                CREATE TABLE IF NOT EXISTS role (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(30) UNIQUE NOT NULL,
                    description VARCHAR(100),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
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
                    role_id INTEGER NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (role_id) REFERENCES role (id)
                )
            """)
            )
            logger.debug("User account table created/verified")

            # Insert default roles
            logger.debug("Inserting default roles")
            s.execute(
                text("""
                INSERT OR IGNORE INTO role (name, description) VALUES
                ('admin', 'Administrator'),
                ('operator', 'Sales Operator'),
                ('team_indosat', 'Indosat Internal Team')
            """)
            )
            logger.debug("Default roles inserted/verified")

            # ✅ Create default admin dengan Pydantic validation
            logger.debug("Creating default admin user")
            admin_data = UserCreate(
                username="admin",
                name="Default Administrator",
                password="admin123",  # noqa: S106
                role_id=1,  # Admin role
            )
            logger.debug(f"Admin user data validated: {admin_data.username}")

            # Hash password setelah validation
            salt = bcrypt.gensalt()
            password_hash = bcrypt.hashpw(admin_data.password.encode("utf-8"), salt)
            logger.debug("Admin password hashed successfully")

            # Insert admin user
            s.execute(
                text("""
                INSERT OR IGNORE INTO user_account
                (username, name, password_hash, is_verified, role_id)
                VALUES (:username, :name, :password_hash, TRUE, :role_id)
            """),
                {
                    "username": admin_data.username,
                    "name": admin_data.name,
                    "password_hash": password_hash.decode("utf-8"),
                    "role_id": admin_data.role_id,
                },
            )
            logger.debug("Default admin user inserted/verified")

            s.commit()
            logger.success("Database initialization completed successfully")

    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise
