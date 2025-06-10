"""Database service untuk seeding dan management initial data."""

from __future__ import annotations

import bcrypt
import streamlit as st
from loguru import logger
from sqlalchemy import insert

from config.constants import DBConstants
from database.core.database_seeding import DatabaseSeeder
from database.definitions import get_role_table_definition, get_user_table_definition


class DatabaseService:
    """Service untuk handle database seeding operations."""

    def __init__(self) -> None:
        """Initialize database service."""
        self.conn = st.connection(DBConstants.CON_NAME, type=DBConstants.CON_TYPE)

    def _hash_password(self, password: str) -> str:
        """Hash password menggunakan bcrypt."""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    def seed_required_roles(self) -> bool:
        """Seed required system roles."""
        try:
            role_table = get_role_table_definition()
            with self.conn.session as s:
                for role in DatabaseSeeder.REQUIRED_ROLES:
                    stmt = (
                        insert(role_table)
                        .prefix_with("OR IGNORE")
                        .values(
                            id=role.role_id,
                            name=role.name,
                            description=role.description,
                            is_active=True,
                        )
                    )
                    s.execute(stmt)
                s.commit()
                logger.info("Required roles seeded successfully")
                return True
        except Exception as e:
            logger.error(f"Failed to seed roles: {e}")
            return False

    def create_default_admin(self) -> bool:
        """Create default admin user dengan hashed password."""
        try:
            user_table = get_user_table_definition()
            with self.conn.session as s:
                admin = DatabaseSeeder.DEFAULT_ADMIN
                hashed_password = self._hash_password(admin.password)

                stmt = (
                    insert(user_table)
                    .prefix_with("OR IGNORE")
                    .values(
                        username=admin.username,
                        name=admin.name,
                        password_hash=hashed_password,
                        role_id=admin.role_id,
                        is_verified=True,
                    )
                )
                s.execute(stmt)
                s.commit()
                logger.info("Default admin created successfully")
                return True
        except Exception as e:
            logger.error(f"Failed to create admin: {e}")
            return False

    def create_demo_accounts(self) -> bool:
        """Seed demo users for testing purposes."""
        try:
            user_table = get_user_table_definition()
            with self.conn.session as s:
                for user in DatabaseSeeder.DEMO_USERS:
                    hashed_password = self._hash_password(user.password)
                    stmt = (
                        insert(user_table)
                        .prefix_with("OR IGNORE")
                        .values(
                            username=user.username,
                            name=user.name,
                            password_hash=hashed_password,
                            role_id=user.role_id,
                            is_verified=True,
                        )
                    )
                    s.execute(stmt)
                s.commit()
                logger.info("Demo users seeded successfully")
                return True
        except Exception as e:
            logger.error(f"Failed to seed demo users: {e}")
            return False
