"""Authentication schemas untuk MIM3 Dashboard."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator

type UserRole = Literal["admin", "operator", "team_indosat"]


# ✅ Authentication Flow (existing)
class UserLogin(BaseModel):
    """Model untuk login request."""

    username: str = Field(min_length=3, max_length=50, description="Username")
    password: str = Field(min_length=6, description="Password")
    model_config = ConfigDict(str_strip_whitespace=True)


class UserSession(BaseModel):
    """Model untuk user session data."""

    user_id: int = Field(gt=0, description="User ID")
    username: str = Field(description="Username")
    role: UserRole = Field(description="User role")
    login_time: datetime = Field(default_factory=datetime.now)
    model_config = ConfigDict(from_attributes=True)


class AuthResult(BaseModel):
    """Model untuk authentication result."""

    success: bool = Field(description="Authentication berhasil atau tidak")
    user_session: UserSession | None = Field(
        default=None, description="Session data jika berhasil"
    )
    error_message: str | None = Field(
        default=None, description="Error message jika gagal"
    )


# ✅ User CRUD Operations
class UserCreate(BaseModel):
    """Model untuk registrasi user baru."""

    username: str = Field(min_length=3, max_length=50, description="Username unik")
    name: str = Field(min_length=2, max_length=50, description="Nama lengkap")
    password: str = Field(min_length=6, description="Password")
    role_id: int = Field(gt=0, description="Role ID")
    model_config = ConfigDict(str_strip_whitespace=True)


class UserUpdate(BaseModel):
    """Model untuk update user profile."""

    name: str | None = Field(
        None, min_length=2, max_length=50, description="Nama lengkap"
    )
    role_id: int | None = Field(None, gt=0, description="Role ID")
    is_verified: bool | None = Field(None, description="Status verifikasi")
    model_config = ConfigDict(str_strip_whitespace=True)


class UserResponse(BaseModel):
    """Model untuk display user data."""

    id: int = Field(description="User ID")
    username: str = Field(description="Username")
    name: str = Field(description="Nama lengkap")
    is_verified: bool = Field(description="Status verifikasi")
    role_name: str = Field(description="Nama role")
    created_at: datetime = Field(description="Tanggal dibuat")
    model_config = ConfigDict(from_attributes=True)


# ✅ Role Management
class RoleCreate(BaseModel):
    """Model untuk buat role baru."""

    name: str = Field(min_length=3, max_length=30, description="Nama role")
    description: str | None = Field(None, max_length=100, description="Deskripsi role")
    model_config = ConfigDict(str_strip_whitespace=True)


class RoleResponse(BaseModel):
    """Model untuk display role data."""

    id: int = Field(description="Role ID")
    name: str = Field(description="Nama role")
    description: str | None = Field(description="Deskripsi role")
    user_count: int = Field(0, description="Jumlah user dengan role ini")
    created_at: datetime = Field(description="Tanggal dibuat")
    model_config = ConfigDict(from_attributes=True)


class UserChangePassword(BaseModel):
    """Model untuk ganti password user."""

    current_password: str = Field(min_length=6, description="Password saat ini")
    new_password: str = Field(min_length=6, description="Password baru")
    confirm_password: str = Field(min_length=6, description="Konfirmasi password baru")

    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v: str, info: ValidationInfo) -> str:
        """Validasi password konfirmasi harus sama dengan password baru."""
        if "new_password" in info.data and v != info.data["new_password"]:
            raise ValueError("Konfirmasi password tidak cocok")
        return v


class AdminResetPassword(BaseModel):
    """Model untuk admin reset password user (tanpa current password)."""

    user_id: int = Field(gt=0, description="ID user yang akan direset")
    new_password: str = Field(min_length=6, description="Password baru")
    confirm_password: str = Field(min_length=6, description="Konfirmasi password baru")

    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v: str, info: ValidationInfo) -> str:
        """Validasi password konfirmasi harus sama dengan password baru."""
        if "new_password" in info.data and v != info.data["new_password"]:
            raise ValueError("Konfirmasi password tidak cocok")
        return v
