"""Admin-specific operations - create, delete, deactivate users dengan security verification."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from models.user.user_password import (
    PasswordGenerationOptions,
    validate_password_strength,
)

from .user_commons import OperationResult
from .user_role import UserRole, can_deactivate_role


class AdminUserCreate(BaseModel):
    """Model untuk admin create user dengan password options."""

    username: str = Field(min_length=3, max_length=50)
    name: str = Field(min_length=2, max_length=100)
    role: UserRole = Field(default="support", description="Default role untuk new user")

    # ✅ Password options - using centralized validation
    password: str | None = Field(
        None, min_length=6, max_length=20, description="Manual password"
    )
    generate_password: bool = False
    password_options: PasswordGenerationOptions | None = None

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str | None) -> str | None:
        """Validate password using centralized policy."""
        if v is not None:
            return validate_password_strength(v)
        return v

    @model_validator(mode="after")
    def validate_password_options(self):
        """Validate password creation options."""
        if not self.password and not self.generate_password:
            raise ValueError("Harus pilih manual password atau generate password")

        if self.password and self.generate_password:
            raise ValueError("Tidak bisa manual password dan generate bersamaan")

        if self.generate_password and not self.password_options:
            # Set default generation options
            self.password_options = PasswordGenerationOptions()

        return self


class AdminUserDelete(BaseModel):
    """Model untuk admin hard delete user - require verification."""

    user_id: int = Field(gt=0, description="User ID yang akan dihapus")
    admin_password: str = Field(
        min_length=6, description="Password admin untuk verifikasi"
    )
    confirmation_text: str = Field(description="Ketik 'DELETE' untuk konfirmasi")
    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator("admin_password")
    @classmethod
    def validate_admin_password(cls, v: str) -> str:
        """Validate admin password using centralized policy."""
        return validate_password_strength(v)

    @field_validator("confirmation_text")
    @classmethod
    def validate_confirmation(cls, v: str) -> str:
        """Validate user typed 'DELETE' exactly."""
        if v.upper() != "DELETE":
            raise ValueError("Harus ketik 'DELETE' untuk konfirmasi")
        return v.upper()


class AdminUserDeactivate(BaseModel):
    """Model untuk admin deactivate/activate user."""

    user_id: int = Field(gt=0, description="User ID")
    is_active: bool = Field(description="Status aktif baru")
    admin_password: str = Field(
        min_length=6, description="Password admin untuk verifikasi"
    )
    reason: str | None = Field(
        None, max_length=200, description="Alasan perubahan status"
    )
    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator("admin_password")
    @classmethod
    def validate_admin_password(cls, v: str) -> str:
        """Validate admin password using centralized policy."""
        return validate_password_strength(v)


class AdminUserRoleChange(BaseModel):
    """Model untuk admin change user role."""

    user_id: int = Field(gt=0, description="User ID")
    new_role: UserRole = Field(description="Role baru")
    admin_password: str = Field(
        min_length=6, description="Password admin untuk verifikasi"
    )
    reason: str | None = Field(
        None, max_length=200, description="Alasan perubahan role"
    )
    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator("admin_password")
    @classmethod
    def validate_admin_password(cls, v: str) -> str:
        """Validate admin password using centralized policy."""
        return validate_password_strength(v)


class AdminRoleDeactivate(BaseModel):
    """Model untuk admin deactivate role - dengan user impact check."""

    role_name: UserRole = Field(description="Role yang akan di-deactivate")
    admin_password: str = Field(
        min_length=6, description="Admin password untuk verifikasi"
    )
    force_deactivate: bool = Field(
        default=False, description="Force deactivate meski ada user"
    )
    reason: str = Field(
        min_length=10, max_length=200, description="Alasan deactivate role"
    )

    # ✅ Additional validation
    confirmation_text: str = Field(description="Ketik nama role untuk konfirmasi")
    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator("admin_password")
    @classmethod
    def validate_admin_password(cls, v: str) -> str:
        """Validate admin password using centralized policy."""
        return validate_password_strength(v)

    @field_validator("confirmation_text")
    @classmethod
    def validate_confirmation(cls, v: str, info) -> str:
        """Validate admin typed role name exactly."""
        # Access role_name from other field during validation
        if hasattr(info.data, "role_name") and v != info.data["role_name"]:
            raise ValueError(f"Harus ketik '{info.data['role_name']}' untuk konfirmasi")
        return v

    @model_validator(mode="after")
    def validate_deactivation_rules(self):
        """Validate role deactivation business rules."""
        if not can_deactivate_role(self.role_name):
            raise ValueError(f"Role '{self.role_name}' tidak dapat di-deactivate")

        return self


class AdminDefaultRoleChange(BaseModel):
    """Model untuk admin change default registration role."""

    new_default_role: UserRole = Field(
        description="Role default baru untuk registration"
    )
    admin_password: str = Field(
        min_length=6, description="Admin password untuk verifikasi"
    )
    reason: str = Field(
        min_length=10, max_length=200, description="Alasan perubahan default role"
    )
    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator("admin_password")
    @classmethod
    def validate_admin_password(cls, v: str) -> str:
        """Validate admin password using centralized policy."""
        return validate_password_strength(v)


class AdminOperationResult(OperationResult):
    """Model untuk admin operation result."""

    affected_user_id: int | None = Field(None, description="User ID yang terpengaruh")
    operation_type: str | None = Field(None, description="Jenis operasi")
    admin_user_id: int | None = Field(None, description="Admin yang melakukan operasi")


# REMINDER: Semua admin operations require password verification - now using centralized validation
# TODO: Add audit log model untuk admin operations
# [ ] PINNED: Consider adding admin operation history tracking
# REMINDER: Role deactivation requires user count check via repository
# TODO: Add audit logging untuk role operations
# PINNED: Force admin awareness - show impact before confirm
