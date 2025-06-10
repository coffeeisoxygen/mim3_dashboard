"""User self-management journey schemas - profile & account control."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator


class ProfileView(BaseModel):
    """Model untuk user view profile sendiri."""

    username: str = Field(description="Username")
    name: str = Field(description="Nama lengkap")
    role_name: str = Field(description="Role saat ini")
    is_verified: bool = Field(description="Status verifikasi")
    created_at: datetime = Field(description="Member sejak")
    model_config = ConfigDict(from_attributes=True)


class ProfileUpdate(BaseModel):
    """Model untuk user update profile sendiri."""

    name: str = Field(min_length=2, max_length=50, description="Nama lengkap baru")
    model_config = ConfigDict(str_strip_whitespace=True)


class PasswordChange(BaseModel):
    """Model untuk user ganti password sendiri."""

    current_password: str = Field(min_length=6, description="Password lama")
    new_password: str = Field(min_length=6, description="Password baru")
    confirm_password: str = Field(min_length=6, description="Konfirmasi password baru")

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str, info: ValidationInfo) -> str:
        """Validate new password.

        Password must be different from current password.

        Args:
            v (str): _description_
            info (ValidationInfo): _description_

        Raises:
            ValueError: _description_

        Returns:
            str: _description_
        """
        if "current_password" in info.data and v == info.data["current_password"]:
            raise ValueError("Password baru harus berbeda dari password lama")
        return v

    @field_validator("confirm_password")
    @classmethod
    def validate_confirm_password(cls, v: str, info: ValidationInfo) -> str:
        """Validate confirm password.

        Confirm password must match new password.

        Args:
            v (str): _description_
            info (ValidationInfo): _description_

        Raises:
            ValueError: _description_

        Returns:
            str: _description_
        """
        if "new_password" in info.data and v != info.data["new_password"]:
            raise ValueError("Konfirmasi password tidak sesuai")
        return v

    model_config = ConfigDict(str_strip_whitespace=True)


class AccountStatus(BaseModel):
    """Model untuk show account status ke user."""

    is_verified: bool = Field(description="Status approval")
    role_name: str = Field(description="Role saat ini")
    last_login: datetime | None = Field(default=None, description="Login terakhir")
    member_since: datetime = Field(description="Member sejak")


class ProfileUpdateResult(BaseModel):
    """moduel untuk result update profile."""

    success: bool = Field(description="Update berhasil atau tidak")
    message: str = Field(description="Pesan tambahan")
