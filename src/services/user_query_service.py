"""User query service - read operations, search, business rules."""

from __future__ import annotations

from loguru import logger

from models.user.user_models import UserDetail, UserFilter, UserListItem
from models.user.user_role import UserRole
from repositories.protocols.user_repository import UserRepository


class UserQueryService:
    """Service untuk user query operations dan business rules."""

    def __init__(self, repository: UserRepository):
        self.repository = repository

    # ================================
    # User Query Operations
    # ================================

    @logger.catch(reraise=True)
    def get_all_users(
        self, filter_params: UserFilter | None = None
    ) -> list[UserListItem]:
        """Get all users dengan optional filtering."""
        logger.debug("Getting all users", has_filter=filter_params is not None)

        # Use empty filter if none provided
        if filter_params is None:
            filter_params = UserFilter()

        # Get raw user data
        users_data = self.repository.get_all_users(filter_params)

        # Convert to UserListItem models
        users = []
        for user_data in users_data:
            try:
                user_item = UserListItem.model_validate(user_data)
                users.append(user_item)
            except Exception as e:
                logger.warning(
                    "Failed to validate user data", user_data=user_data, error=str(e)
                )
                continue

        logger.debug("Retrieved users", total_count=len(users))
        return users

    @logger.catch(reraise=True)
    def get_users_by_role(self, role_name: UserRole) -> list[UserListItem]:
        """Get users filtered by specific role."""
        logger.debug("Getting users by role", role=role_name)

        # Create filter for specific role
        filter_params = UserFilter(role_filter=role_name)
        users = self.get_all_users(filter_params)

        logger.debug("Users retrieved by role", role=role_name, count=len(users))
        return users

    @logger.catch(reraise=True)
    def search_users(
        self,
        name_search: str | None = None,
        role_filter: UserRole | None = None,
        is_active: bool | None = None,
    ) -> list[UserListItem]:
        """Search users dengan multiple criteria."""
        logger.debug(
            "Searching users",
            name_search=name_search,
            role_filter=role_filter,
            is_active=is_active,
        )

        # Build filter parameters
        filter_params = UserFilter(
            name_search=name_search, role_filter=role_filter, is_active=is_active
        )

        # Get filtered users
        users = self.get_all_users(filter_params)

        # Count non-None criteria for logging
        criteria_count = sum(
            1 for x in [name_search, role_filter, is_active] if x is not None
        )

        logger.debug(
            "User search completed",
            criteria_count=criteria_count,
            results_count=len(users),
        )
        return users

    @logger.catch(reraise=True)
    def get_user_detail(self, user_id: int) -> UserDetail | None:
        """Get detailed user information by ID."""
        logger.debug("Getting user detail", user_id=user_id)

        user_data = self.repository.get_user_by_id(user_id)
        if not user_data:
            logger.debug("User detail not found", user_id=user_id)
            return None

        try:
            user_detail = UserDetail.model_validate(user_data)
            logger.debug("User detail retrieved successfully", user_id=user_id)
            return user_detail
        except Exception as e:
            logger.error(
                "Failed to validate user detail data", user_id=user_id, error=str(e)
            )
            return None

    # ================================
    # Business Rules & Validation
    # ================================

    @logger.catch(reraise=True)
    def is_username_available(
        self, username: str, exclude_user_id: int | None = None
    ) -> bool:
        """Check if username is available for registration or update."""
        logger.debug(
            "Checking username availability",
            username=username,
            exclude_user_id=exclude_user_id,
        )

        if not username or len(username.strip()) < 3:
            logger.debug("Invalid username provided", username=username)
            return False

        is_available = self.repository.is_username_available(
            username.strip(), exclude_user_id
        )

        logger.debug(
            "Username availability check completed",
            username=username,
            is_available=is_available,
        )
        return is_available

    @logger.catch(reraise=True)
    def can_deactivate_role(self, role_name: UserRole) -> bool:
        """Check if role can be safely deactivated."""
        from models.user.user_role import can_deactivate_role

        logger.debug("Checking role deactivation eligibility", role=role_name)

        # Check role definition first (business rule)
        if not can_deactivate_role(role_name):
            logger.debug("Role cannot be deactivated by definition", role=role_name)
            return False

        # Check if role is currently in use
        active_users_count = self.repository.count_active_users_by_role(role_name)
        if active_users_count > 0:
            logger.debug(
                "Role cannot be deactivated - has active users",
                role=role_name,
                active_users_count=active_users_count,
            )
            return False

        logger.debug("Role can be safely deactivated", role=role_name)
        return True

    # ================================
    # Statistics & Analytics
    # ================================

    @logger.catch(reraise=True)
    def get_role_usage_stats(self) -> dict[UserRole, int]:
        """Get user count by role untuk admin monitoring."""
        logger.debug("Getting role usage statistics")

        stats = {}
        # Use UserRole enum values instead of string literals
        roles = [UserRole.ADMIN, UserRole.STAFF, UserRole.SUPPORT]

        for role in roles:
            try:
                count = self.repository.count_active_users_by_role(role)
                stats[role] = count
            except Exception as e:
                logger.warning(
                    "Failed to get role usage count", role=role, error=str(e)
                )
                stats[role] = 0

        logger.debug("Role usage statistics retrieved", stats=stats)
        return stats

    @logger.catch(reraise=True)
    def get_user_count_summary(self) -> dict[str, int]:
        """Get user count summary untuk dashboard."""
        logger.debug("Getting user count summary")

        try:
            # Get all users to calculate summary
            all_users = self.get_all_users()

            # Calculate statistics
            total_users = len(all_users)
            active_users = len([u for u in all_users if u.is_active])
            inactive_users = total_users - active_users

            # Role breakdown
            role_stats = self.get_role_usage_stats()

            summary = {
                "total_users": total_users,
                "active_users": active_users,
                "inactive_users": inactive_users,
                "admin_users": role_stats.get("admin", 0),
                "staff_users": role_stats.get("staff", 0),
                "support_users": role_stats.get("support", 0),
            }

            logger.debug("User count summary calculated", summary=summary)
            return summary

        except Exception as e:
            logger.error("Failed to calculate user count summary", error=str(e))
            return {
                "total_users": 0,
                "active_users": 0,
                "inactive_users": 0,
                "admin_users": 0,
                "staff_users": 0,
                "support_users": 0,
            }

    # ================================
    # Utility Methods
    # ================================

    @logger.catch(reraise=True)
    def validate_user_exists(self, user_id: int) -> bool:
        """Validate that user exists in system."""
        logger.debug("Validating user existence", user_id=user_id)

        user_data = self.repository.get_user_by_id(user_id)
        exists = user_data is not None

        logger.debug(
            "User existence validation completed", user_id=user_id, exists=exists
        )
        return exists

    @logger.catch(reraise=True)
    def get_users_by_ids(self, user_ids: list[int]) -> list[UserListItem]:
        """Get multiple users by their IDs."""
        logger.debug("Getting users by IDs", user_ids=user_ids, count=len(user_ids))

        if not user_ids:
            logger.debug("Empty user IDs list provided")
            return []

        users = []
        for user_id in user_ids:
            user_data = self.repository.get_user_by_id(user_id)
            if user_data:
                try:
                    user_item = UserListItem.model_validate(user_data)
                    users.append(user_item)
                except Exception as e:
                    logger.warning(
                        "Failed to validate user data", user_id=user_id, error=str(e)
                    )
                    continue

        logger.debug(
            "Users retrieved by IDs",
            requested_count=len(user_ids),
            found_count=len(users),
        )
        return users


# REMINDER: Service focused on read operations dan business rules only
# TODO: Add caching with @st.cache_data untuk expensive queries
# PINNED: All data conversion handled in service layer (dict → Pydantic models)
# PINNED: Business rules centralized dalam service layer
# TODO: Consider adding advanced search capabilities (fuzzy search, etc.)
# TODO: Add user activity analytics (last login, frequency, etc.)
# PINNED: Error handling dengan graceful degradation untuk partial failures
