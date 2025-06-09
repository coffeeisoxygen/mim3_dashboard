"""User CRUD schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


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
