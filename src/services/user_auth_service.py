"""User authentication service - login, profile, password management."""

from __future__ import annotations

from loguru import logger

from models.user.user_auth import UserActiveSession
from models.user.user_commons import OperationResult
from models.user.user_models import UserDetail
from models.user.user_password import PasswordChangeModel
from repositories.protocols.user_repository import UserRepository


class UserAuthService:
    """Service untuk user authentication dan self-service operations."""

    def __init__(self, repository: UserRepository):
        self.repository = repository

    # ================================
    # Authentication Operations
    # ================================

    @logger.catch(reraise=True)
    def authenticate_user(
        self, username: str, password: str
    ) -> UserActiveSession | None:
        """Authenticate user dan return session data."""
        logger.info("Authentication attempt", username=username)

        # Validate input
        if not username or not password:
            logger.warning("Empty credentials provided", username=username)
            return None

        # Get user for authentication
        user = self.repository.get_user_for_session(username)
        if not user:
            logger.warning("User not found during authentication", username=username)
            return None

        # Verify password
        if not self.repository.verify_password(user.user_id, password):
            logger.warning(
                "Invalid password attempt", username=username, user_id=user.user_id
            )
            return None

        # Update last login timestamp
        self.repository.update_last_login(user.user_id)

        logger.info(
            "Authentication successful",
            username=username,
            user_id=user.user_id,
            role=user.role_name,
        )
        return user

    @logger.catch(reraise=True)
    def verify_user_password(self, user_id: int, password: str) -> bool:
        """Verify user password - for sensitive operations."""
        logger.debug("Password verification requested", user_id=user_id)

        if not password:
            logger.debug("Empty password provided for verification", user_id=user_id)
            return False

        is_valid = self.repository.verify_password(user_id, password)

        logger.debug(
            "Password verification completed", user_id=user_id, is_valid=is_valid
        )
        return is_valid

    # ================================
    # Password Management
    # ================================

    @logger.catch(reraise=True)
    def change_password(
        self, user_id: int, data: PasswordChangeModel
    ) -> OperationResult:
        """Change user password dengan current password verification."""
        logger.info("Password change request", user_id=user_id)

        # Verify current password first
        if not self.repository.verify_password(user_id, data.current_password):
            logger.warning("Invalid current password during change", user_id=user_id)
            return OperationResult(
                success=False, message="Password saat ini tidak benar"
            )

        # Update password (repository should handle hashing)
        success = self.repository.update_user_password(user_id, data.new_password)

        if success:
            logger.info("Password changed successfully", user_id=user_id)
            return OperationResult(success=True, message="Password berhasil diubah")

        logger.error("Failed to update password in database", user_id=user_id)
        return OperationResult(success=False, message="Gagal mengubah password")

    # ================================
    # Profile Management (Self-Service)
    # ================================

    @logger.catch(reraise=True)
    def get_user_profile(self, user_id: int) -> UserDetail | None:
        """Get user profile untuk self-service display."""
        logger.debug("Getting user profile", user_id=user_id)

        user_data = self.repository.get_user_by_id(user_id)
        if not user_data:
            logger.debug("User profile not found", user_id=user_id)
            return None

        # Convert raw dict to UserDetail model
        try:
            profile = UserDetail.model_validate(user_data)
            logger.debug("User profile retrieved successfully", user_id=user_id)
            return profile
        except Exception as e:
            logger.error(
                "Failed to validate user profile data", user_id=user_id, error=str(e)
            )
            return None

    @logger.catch(reraise=True)
    def update_user_profile(self, user_id: int, name: str) -> OperationResult:
        """Update user basic profile information (self-service)."""
        logger.info("Profile update request", user_id=user_id, new_name=name)

        # Validate name
        if not name or len(name.strip()) < 2:
            logger.warning("Invalid name provided for profile update", user_id=user_id)
            return OperationResult(
                success=False, message="Nama harus minimal 2 karakter"
            )

        # Update profile
        success = self.repository.update_user_basic_info(user_id, name=name.strip())

        if success:
            logger.info("Profile updated successfully", user_id=user_id, new_name=name)
            return OperationResult(success=True, message="Profile berhasil diperbarui")

        logger.error("Failed to update profile in database", user_id=user_id)
        return OperationResult(success=False, message="Gagal memperbarui profile")

    # ================================
    # Session Support
    # ================================

    @logger.catch(reraise=True)
    def refresh_user_activity(self, user_id: int) -> bool:
        """Refresh user last activity untuk session management."""
        logger.debug("Refreshing user activity", user_id=user_id)

        success = self.repository.update_last_login(user_id)

        logger.debug(
            "User activity refresh completed", user_id=user_id, success=success
        )
        return success

    @logger.catch(reraise=True)
    def get_user_for_session(self, username: str) -> UserActiveSession | None:
        """Get user data untuk session creation (tanpa password verification)."""
        logger.debug("Getting user for session", username=username)

        if not username:
            logger.debug("Empty username provided for session")
            return None

        user = self.repository.get_user_for_session(username)

        if user:
            logger.debug(
                "User found for session", username=username, user_id=user.user_id
            )
        else:
            logger.debug("User not found for session", username=username)

        return user


# REMINDER: Service focused on authentication dan self-service operations only
# TODO: Add session integration with SessionService for coordinated session management
# PINNED: Password hashing delegated to repository layer
# PINNED: All operations logged dengan structured data untuk audit trail
# TODO: Consider adding password policy enforcement at service level
# TODO: Add user activity tracking for security monitoring
