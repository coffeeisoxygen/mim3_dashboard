"""Admin user service - administrative operations dengan verification."""

from __future__ import annotations

from loguru import logger

from models.user.user_admin import (
    AdminDefaultRoleChange,
    AdminRoleDeactivate,
    AdminUserCreate,
    AdminUserDelete,
)
from models.user.user_commons import OperationResult
from models.user.user_models import UserListItem, UserOperationResult
from repositories.protocols.user_repository import UserRepository


class AdminUserService:
    """Service untuk administrative user operations dengan security verification."""

    def __init__(self, repository: UserRepository):
        self.repository = repository

    # ================================
    # Admin User CRUD Operations
    # ================================

    @logger.catch(reraise=True)
    def create_user(
        self, data: AdminUserCreate, admin_user_id: int
    ) -> UserOperationResult:
        """Admin create new user dengan verification."""
        logger.info(
            "Admin user creation request",
            admin_user_id=admin_user_id,
            target_username=data.username,
            target_role=data.role_name,
        )

        try:
            # Repository handles admin password verification + user creation
            result = self.repository.admin_create_user(data, admin_user_id)

            if result.success and result.user_id:
                # Get created user data for enriched response
                user_data = self.repository.get_user_by_id(result.user_id)
                if user_data:
                    try:
                        created_user = UserListItem.model_validate(user_data)
                        logger.info(
                            "User created successfully by admin",
                            admin_user_id=admin_user_id,
                            created_user_id=result.user_id,
                            username=data.username,
                        )
                        return UserOperationResult(
                            success=True,
                            message=result.message,
                            user=created_user,
                        )
                    except Exception as e:
                        logger.warning(
                            "Failed to validate created user data",
                            created_user_id=result.user_id,
                            error=str(e),
                        )
                        # Return success tapi tanpa user object
                        return UserOperationResult(
                            success=True,
                            message=f"{result.message} (validation warning)",
                        )

            logger.warning(
                "Admin user creation failed",
                admin_user_id=admin_user_id,
                target_username=data.username,
                reason=result.message,
            )
            return UserOperationResult(success=False, message=result.message)

        except Exception:
            logger.opt(exception=True).error(
                "Exception during admin user creation",
                admin_user_id=admin_user_id,
                target_username=data.username,
            )
            return UserOperationResult(
                success=False, message="Error sistem saat membuat user"
            )

    @logger.catch(reraise=True)
    def delete_user(self, data: AdminUserDelete, admin_user_id: int) -> OperationResult:
        """Admin delete user dengan verification."""
        logger.info(
            "Admin user deletion request",
            admin_user_id=admin_user_id,
            target_user_id=data.user_id,
        )

        try:
            # Repository handles admin password verification + user deletion
            result = self.repository.admin_delete_user(data, admin_user_id)

            if result.success:
                logger.info(
                    "User deleted successfully by admin",
                    admin_user_id=admin_user_id,
                    deleted_user_id=data.user_id,
                )
            else:
                logger.warning(
                    "Admin user deletion failed",
                    admin_user_id=admin_user_id,
                    target_user_id=data.user_id,
                    reason=result.message,
                )

            return result

        except Exception:
            logger.opt(exception=True).error(
                "Exception during admin user deletion",
                admin_user_id=admin_user_id,
                target_user_id=data.user_id,
            )
            return OperationResult(
                success=False, message="Error sistem saat menghapus user"
            )

    # ================================
    # Admin Role Management
    # ================================

    @logger.catch(reraise=True)
    def deactivate_role(
        self, data: AdminRoleDeactivate, admin_user_id: int
    ) -> OperationResult:
        """Admin deactivate role dengan verification."""
        logger.info(
            "Admin role deactivation request",
            admin_user_id=admin_user_id,
            target_role=data.role_name,
        )

        try:
            # Repository handles admin password verification + role deactivation
            result = self.repository.admin_deactivate_role(data, admin_user_id)

            if result.success:
                logger.info(
                    "Role deactivated successfully by admin",
                    admin_user_id=admin_user_id,
                    deactivated_role=data.role_name,
                )
            else:
                logger.warning(
                    "Admin role deactivation failed",
                    admin_user_id=admin_user_id,
                    target_role=data.role_name,
                    reason=result.message,
                )

            return result

        except Exception:
            logger.opt(exception=True).error(
                "Exception during admin role deactivation",
                admin_user_id=admin_user_id,
                target_role=data.role_name,
            )
            return OperationResult(
                success=False, message="Error sistem saat menonaktifkan role"
            )

    @logger.catch(reraise=True)
    def change_default_role(
        self, data: AdminDefaultRoleChange, admin_user_id: int
    ) -> OperationResult:
        """Admin change default registration role."""
        logger.info(
            "Admin default role change request",
            admin_user_id=admin_user_id,
            new_default_role=data.new_default_role,
            reason=data.reason,
        )

        try:
            # Repository handles admin password verification + default role change
            result = self.repository.admin_change_default_role(data, admin_user_id)

            if result.success:
                logger.info(
                    "Default role changed successfully by admin",
                    admin_user_id=admin_user_id,
                    new_default_role=data.new_default_role,
                    reason=data.reason,
                )
            else:
                logger.warning(
                    "Admin default role change failed",
                    admin_user_id=admin_user_id,
                    target_role=data.new_default_role,
                    reason=result.message,
                )

            return result

        except Exception:
            logger.opt(exception=True).error(
                "Exception during admin default role change",
                admin_user_id=admin_user_id,
                target_role=data.new_default_role,
            )
            return OperationResult(
                success=False, message="Error sistem saat mengubah default role"
            )

    # ================================
    # Admin User Status Management
    # ================================

    @logger.catch(reraise=True)
    def activate_user(self, user_id: int, admin_user_id: int) -> OperationResult:
        """Admin activate user (simple activation tanpa heavy verification)."""
        logger.info(
            "Admin user activation request",
            admin_user_id=admin_user_id,
            target_user_id=user_id,
        )

        try:
            # Repository handles user activation
            success = self.repository.update_user_status(user_id, is_active=True)

            if success:
                logger.info(
                    "User activated successfully by admin",
                    admin_user_id=admin_user_id,
                    activated_user_id=user_id,
                )
                return OperationResult(success=True, message="User berhasil diaktifkan")

            logger.warning(
                "Admin user activation failed",
                admin_user_id=admin_user_id,
                target_user_id=user_id,
            )
            return OperationResult(success=False, message="Gagal mengaktifkan user")

        except Exception:
            logger.opt(exception=True).error(
                "Exception during admin user activation",
                admin_user_id=admin_user_id,
                target_user_id=user_id,
            )
            return OperationResult(
                success=False, message="Error sistem saat mengaktifkan user"
            )

    @logger.catch(reraise=True)
    def deactivate_user(self, user_id: int, admin_user_id: int) -> OperationResult:
        """Admin deactivate user (simple deactivation tanpa heavy verification)."""
        logger.info(
            "Admin user deactivation request",
            admin_user_id=admin_user_id,
            target_user_id=user_id,
        )

        try:
            # Repository handles user deactivation
            success = self.repository.update_user_status(user_id, is_active=False)

            if success:
                logger.info(
                    "User deactivated successfully by admin",
                    admin_user_id=admin_user_id,
                    deactivated_user_id=user_id,
                )
                return OperationResult(
                    success=True, message="User berhasil dinonaktifkan"
                )

            logger.warning(
                "Admin user deactivation failed",
                admin_user_id=admin_user_id,
                target_user_id=user_id,
            )
            return OperationResult(success=False, message="Gagal menonaktifkan user")

        except Exception:
            logger.opt(exception=True).error(
                "Exception during admin user deactivation",
                admin_user_id=admin_user_id,
                target_user_id=user_id,
            )
            return OperationResult(
                success=False, message="Error sistem saat menonaktifkan user"
            )

    # ================================
    # Admin Utility Methods
    # ================================

    @logger.catch(reraise=True)
    def verify_admin_password(self, admin_user_id: int, password: str) -> bool:
        """Verify admin password untuk sensitive operations."""
        logger.debug(
            "Admin password verification requested", admin_user_id=admin_user_id
        )

        if not password:
            logger.debug("Empty admin password provided", admin_user_id=admin_user_id)
            return False

        # Repository handles password verification
        is_valid = self.repository.verify_password(admin_user_id, password)

        logger.debug(
            "Admin password verification completed",
            admin_user_id=admin_user_id,
            is_valid=is_valid,
        )
        return is_valid

    @logger.catch(reraise=True)
    def get_admin_operation_log(
        self, admin_user_id: int, operation_type: str | None = None
    ) -> list[dict]:
        """Get admin operation log untuk audit (if supported by repository)."""
        logger.debug(
            "Getting admin operation log",
            admin_user_id=admin_user_id,
            operation_type=operation_type,
        )

        try:
            # Repository might have audit log functionality
            if hasattr(self.repository, "get_admin_operation_log"):
                log_entries = self.repository.get_admin_operation_log(
                    admin_user_id, operation_type
                )
                logger.debug(
                    "Admin operation log retrieved",
                    admin_user_id=admin_user_id,
                    entries_count=len(log_entries),
                )
                return log_entries
            else:
                logger.debug("Admin operation log not supported by repository")
                return []

        except Exception as e:
            logger.error(
                "Failed to retrieve admin operation log",
                admin_user_id=admin_user_id,
                error=str(e),
            )
            return []


# REMINDER: Service focused on admin operations dengan comprehensive security
# PINNED: All admin operations require proper verification via repository layer
# PINNED: Comprehensive logging untuk audit trail dan security monitoring
# TODO: Add batch operations untuk multiple user management
# TODO: Consider adding admin operation rate limiting untuk security
# PINNED: Error handling dengan graceful degradation dan clear error messages
# TODO: Add admin notification system untuk critical operations
