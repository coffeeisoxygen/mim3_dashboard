"""Password management schemas."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator


class UserChangePassword(BaseModel):
    """Model untuk user mengubah password sendiri."""

    current_password: str = Field(min_length=6, description="Password saat ini")
    new_password: str = Field(min_length=6, description="Password baru")
    confirm_password: str = Field(min_length=6, description="Konfirmasi password baru")
    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v: str, info) -> str:
        """Validate password confirmation matches."""
        if "new_password" in info.data and v != info.data["new_password"]:
            raise ValueError("Password konfirmasi tidak sama")
        return v


class AdminResetPassword(BaseModel):
    """Model untuk admin reset password user."""

    user_id: int = Field(gt=0, description="User ID yang akan di-reset")
    new_password: str = Field(min_length=6, description="Password baru")
    confirm_password: str = Field(min_length=6, description="Konfirmasi password baru")
    force_change: bool = Field(
        default=True, description="User harus ganti password saat login pertama"
    )
    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v: str, info) -> str:
        """Validate password confirmation matches."""
        if "new_password" in info.data and v != info.data["new_password"]:
            raise ValueError("Password konfirmasi tidak sama")
        return v


class PasswordResetResult(BaseModel):
    """Model untuk result password reset operation."""

    success: bool = Field(description="Reset berhasil atau tidak")
    message: str = Field(description="Pesan result")
    temporary_password: str | None = Field(
        default=None, description="Password sementara jika auto-generated"
    )
