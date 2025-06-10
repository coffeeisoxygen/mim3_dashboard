"""Role service untuk business logic role management."""

from __future__ import annotations

from loguru import logger

from database.commands.role_commands import (
    get_role_by_id,
    get_roles_excluding_names,
)
from models.role.role_schemas import RoleOption


class RoleService:
    """Service untuk role management operations."""

    def get_registration_role_options(self) -> list[RoleOption]:
        """Get role options untuk registration form (exclude admin)."""
        try:
            roles = get_roles_excluding_names(["admin"])
            return [
                RoleOption(id=role.id, name=role.name, description=role.description)
                for role in roles
            ]
        except Exception as e:
            logger.error(f"Failed to get registration role options: {e}")
            return []

    def get_default_role_id(self) -> int:
        """Get default role ID untuk fallback (operator)."""
        try:
            roles = get_roles_excluding_names(["admin"])
            # Cari operator role, kalau ga ada ambil yang pertama
            for role in roles:
                if role.name == "operator":
                    return role.id

            # Fallback ke role pertama kalau operator ga ada
            return roles[0].id if roles else 2  # Hard fallback

        except Exception as e:
            logger.error(f"Failed to get default role: {e}")
            return 2  # Hard fallback ke ID 2

    def validate_role_for_registration(self, role_id: int) -> bool:
        """Validate role bisa dipakai untuk registration (not admin)."""
        try:
            role = get_role_by_id(role_id)
            if not role:
                return False

            # Admin role ga boleh dipilih user
            return role.name != "admin"

        except Exception as e:
            logger.error(f"Failed to validate role {role_id}: {e}")
            return False

    def seed_system_roles(self) -> bool:
        """Seed system roles dari SystemSeeder."""
        try:
            logger.debug("Importing dependencies...")
            from database.commands.role_commands import create_role
            from models.role.role_schemas import RoleCreate
            from models.system.sys_seeder import SystemSeeder

            logger.debug(f"SystemSeeder.REQUIRED_ROLES: {SystemSeeder.REQUIRED_ROLES}")

            logger.info("Starting system roles seeding")

            for required_role in SystemSeeder.REQUIRED_ROLES:
                logger.debug(f"Processing role: {required_role.name}")  # ✅ Add this

                role_data = RoleCreate.model_construct(  # ✅ Skip validation
                    name=required_role.name, description=required_role.description
                )
                logger.debug(f"RoleCreate object created: {role_data}")  # ✅ Add this

                # Use existing role commands (reuse pattern)
                success, message = create_role(role_data)

                if success:
                    logger.debug(f"System role created: {required_role.name}")
                else:
                    logger.warning(
                        f"Role creation failed: {required_role.name} - {message}"
                    )  # ✅ Log failure

            logger.success("System roles seeding completed")
            return True

        except Exception as e:
            logger.error(f"Failed to seed system roles: {e}")
            return False
