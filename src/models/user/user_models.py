"""User domain models - flat structure, clear purpose."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class User(BaseModel):
    """Complete user model untuk database representation."""

    id: int = Field(gt=0, description="User ID")
    username: str = Field(min_length=3, max_length=50, description="Username")
    name: str = Field(min_length=2, max_length=100, description="Nama lengkap")
    password_hash: str = Field(description="Password hash untuk authentication")
    role_id: int = Field(gt=0, description="Role ID dari database")
    role_name: str = Field(description="Display role name")
    is_verified: bool = Field(default=False, description="Status verifikasi")
    is_active: bool = Field(default=True, description="Status aktif")
    created_at: datetime = Field(description="Waktu pembuatan")
    updated_at: datetime | None = Field(
        default=None, description="Waktu update terakhir"
    )

    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)


class UserCreate(BaseModel):
    """Model untuk admin create new user."""

    username: str = Field(min_length=3, max_length=50, description="Username")
    name: str = Field(min_length=2, max_length=100, description="Nama lengkap")
    password: str = Field(min_length=6, description="Password")
    role_id: int = Field(gt=0, description="Role ID yang akan diberikan")
    is_verified: bool = Field(
        default=True, description="Auto-verify untuk admin creation"
    )
    is_active: bool = Field(
        default=True, description="Auto-active untuk admin creation"
    )  # ✅ Tambah ini
    created_at: datetime = Field(
        default_factory=datetime.now, description="Waktu pembuatan"
    )

    model_config = ConfigDict(str_strip_whitespace=True)


class UserUpdate(BaseModel):
    """Model untuk update user data."""

    name: str | None = Field(
        default=None, min_length=2, max_length=100, description="Nama lengkap"
    )
    role_id: int | None = Field(default=None, gt=0, description="Role ID")
    is_active: bool | None = Field(default=None, description="Status aktif")
    is_verified: bool | None = Field(
        default=None, description="Status verifikasi"
    )  # ✅ Tambah ini

    model_config = ConfigDict(str_strip_whitespace=True)


class UserListItem(BaseModel):
    """Model untuk UI listing/dropdown."""

    id: int = Field(gt=0, description="User ID")
    username: str = Field(description="Username")
    name: str = Field(description="Nama lengkap")
    role_name: str = Field(description="Nama role")
    is_verified: bool = Field(description="Status verifikasi")
    is_active: bool = Field(description="Status aktif")

    model_config = ConfigDict(from_attributes=True)
