"""System bootstrap models dan logic untuk initial setup."""

from __future__ import annotations

from datetime import datetime

from loguru import logger
from pydantic import BaseModel, Field

from models.role.role_schemas import SystemRoleCreate
from models.user.user_models import UserCreate


class BootstrapConfig(BaseModel):
    """Configuration untuk system bootstrap."""

    admin_username: str = Field(default="admin", description="Default admin username")
    admin_password: str = Field(
        default="admin123", description="Default admin password"
    )
    admin_name: str = Field(
        default="Default Administrator", description="Default admin full name"
    )

    # System roles yang harus ada
    system_roles: list[SystemRoleCreate] = Field(
        default_factory=lambda: [
            SystemRoleCreate(name="admin", description="Full system access"),
            SystemRoleCreate(name="manager", description="Management access"),
            SystemRoleCreate(name="operator", description="Operational access"),
        ]
    )


class BootstrapResult(BaseModel):
    """Result dari bootstrap operation."""

    success: bool = Field(description="Bootstrap berhasil")
    message: str = Field(description="Status message")
    roles_created: int = Field(default=0, description="Jumlah role yang dibuat")
    admin_created: bool = Field(default=False, description="Admin user dibuat")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Waktu bootstrap"
    )


class SystemBootstrap:
    """Strategy untuk system bootstrap operations."""

    def __init__(self, config: BootstrapConfig | None = None):
        self.config = config or BootstrapConfig()

    def needs_bootstrap(self) -> bool:
        """Check apakah system butuh bootstrap."""
        from database.commands.user_commands import has_any_admin_user

        try:
            return not has_any_admin_user()
        except Exception as e:
            logger.warning(f"Bootstrap check failed: {e}")
            return True  # Assume needs bootstrap on error

    def execute_bootstrap(self) -> BootstrapResult:
        """Execute complete bootstrap sequence dengan detailed logging."""
        logger.info("Starting system bootstrap...")

        try:
            # Step 1: Bootstrap system roles
            logger.debug("Step 1: Starting role bootstrap...")
            roles_result = self._bootstrap_roles()
            logger.debug(f"Step 1 result: {roles_result}")

            if not roles_result:
                return BootstrapResult(
                    success=False, message="Failed to bootstrap system roles"
                )

            # Step 2: Create default admin
            logger.debug("Step 2: Starting admin bootstrap...")
            admin_result = self._bootstrap_admin()
            logger.debug(f"Step 2 result: {admin_result}")

            if not admin_result:
                return BootstrapResult(
                    success=False,
                    message="Failed to create default admin",
                    roles_created=len(self.config.system_roles),
                )

            logger.info("System bootstrap completed successfully")
            return BootstrapResult(
                success=True,
                message="System bootstrap berhasil",
                roles_created=len(self.config.system_roles),
                admin_created=True,
            )

        except Exception as e:
            logger.error(f"Bootstrap failed: {e}")
            return BootstrapResult(success=False, message=f"Bootstrap error: {e!s}")

    def _bootstrap_roles(self) -> bool:
        """Bootstrap system roles tanpa validation."""
        from database.commands.role_commands import seed_system_roles

        try:
            logger.debug(f"About to seed {len(self.config.system_roles)} roles")
            logger.debug(
                f"Role names: {[role.name for role in self.config.system_roles]}"
            )

            # ✅ Langsung pass SystemRoleCreate (no validation)
            success = seed_system_roles(self.config.system_roles)
            logger.debug(f"seed_system_roles returned: {success}")

            if success:
                logger.info(
                    f"System roles bootstrapped: {len(self.config.system_roles)}"
                )
            else:
                logger.error(
                    "seed_system_roles returned False - check role_commands.py"
                )

            return success
        except Exception as e:
            logger.error(f"Role bootstrap failed: {e}")
            return False

    def _bootstrap_admin(self) -> bool:
        """Create default admin user."""
        from database.commands.user_commands import create_user, has_any_admin_user

        try:
            # Check if admin already exists
            if has_any_admin_user():
                logger.info("Admin user already exists - skipping creation")
                return True

            logger.debug(f"Creating admin user: {self.config.admin_username}")

            # Create admin user - pastikan field sesuai UserCreate
            admin_data = UserCreate(
                username=self.config.admin_username,
                name=self.config.admin_name,
                password=self.config.admin_password,  # ✅ Raw password
                role_id=1,
                is_verified=True,  # ✅ Field ada di UserCreate
                is_active=True,  # ✅ Field ada di UserCreate
            )

            logger.debug(f"Admin data prepared: {admin_data.username}")

            result = create_user(admin_data)
            logger.debug(
                f"Create user result: success={result.success}, message={result.message}"
            )

            if result.success:
                logger.info(f"Default admin created: {self.config.admin_username}")
                return True
            else:
                logger.error(f"Admin creation failed: {result.message}")
                return False
        except Exception as e:
            logger.error(f"Admin bootstrap failed: {e}")
            return False


def ensure_system_ready() -> bool:
    """Ensure system is ready by checking and running bootstrap if needed."""
    try:
        bootstrap = SystemBootstrap()

        if not bootstrap.needs_bootstrap():
            logger.debug("System already bootstrapped")
            return True

        logger.info("System needs bootstrap - starting...")
        result = bootstrap.execute_bootstrap()

        if result.success:
            logger.info(f"Bootstrap completed: {result.message}")
            return True
        else:
            logger.error(f"Bootstrap failed: {result.message}")
            return False

    except Exception as e:
        logger.error(f"System ready check failed: {e}")
        return False
