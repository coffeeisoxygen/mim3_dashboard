"""User domain models - CRUD operations MIM3 business."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from models.user.user_password import PasswordChangeModel

from .user_commons import OperationResult
from .user_role import UserRole


class UserBase(BaseModel):
    """Base user model dengan common fields."""

    username: str = Field(min_length=3, max_length=50, description="Username")
    name: str = Field(min_length=2, max_length=100, description="Nama lengkap")
    role_name: UserRole = Field(description="User role: admin/staff/support")
    model_config = ConfigDict(str_strip_whitespace=True)


class UserUpdate(BaseModel):
    """Model untuk update user - partial updates (no password)."""

    name: str | None = Field(
        None, min_length=2, max_length=100, description="Nama lengkap"
    )
    role_name: UserRole | None = Field(None, description="User role")
    is_active: bool | None = Field(None, description="Status aktif")
    model_config = ConfigDict(str_strip_whitespace=True)


class UserListItem(UserBase):
    """Model untuk display di table/list."""

    id: int = Field(gt=0, description="User ID")
    is_active: bool = Field(description="Status aktif")
    created_at: datetime = Field(description="Tanggal dibuat")
    updated_at: datetime | None = Field(None, description="Terakhir diupdate")
    model_config = ConfigDict(from_attributes=True)


class UserDetail(UserListItem):
    """Extended user detail dengan session analytics."""

    last_login: datetime | None = Field(None, description="Login terakhir")
    active_session_count: int = Field(default=0, description="Jumlah session aktif")
    total_logins: int = Field(default=0, description="Total login")


class UserFilter(BaseModel):
    """Filter parameters untuk user search."""

    name_search: str | None = Field(None, min_length=2, description="Search by name")
    role_filter: UserRole | None = Field(None, description="Filter by role")
    is_active: bool | None = Field(None, description="Filter by active status")
    model_config = ConfigDict(str_strip_whitespace=True)


class UserOperationResult(OperationResult):
    """Model untuk user operation result."""

    user: UserListItem | None = Field(None, description="User data jika berhasil")


# Alias untuk backward compatibility dan domain consistency
UserPasswordChange = PasswordChangeModel

# TODO: Add user permission model untuk fine-grained access control
# [ ] PINNED: Consider role hierarchy untuk permission checks
