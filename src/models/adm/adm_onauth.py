"""Admin journey schemas - user management & system oversight."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UserOverview(BaseModel):
    """Model untuk admin view semua users."""

    id: int = Field(description="User ID")
    username: str = Field(description="Username")
    name: str = Field(description="Nama lengkap")
    role_name: str = Field(description="Role user")
    is_verified: bool = Field(description="Status approval")
    created_at: datetime = Field(description="Tanggal registrasi")
    model_config = ConfigDict(from_attributes=True)


class UserApproval(BaseModel):
    """Model untuk approve/reject individual user."""

    user_id: int = Field(gt=0, description="User ID yang akan di-manage")
    is_approved: bool = Field(description="Approve atau reject")
    notes: str | None = Field(None, max_length=200, description="Catatan admin")
    approved_by: int = Field(gt=0, description="Admin ID yang melakukan action")
    model_config = ConfigDict(str_strip_whitespace=True)


class BulkUserAction(BaseModel):
    """Model untuk bulk operations pada multiple users."""

    user_ids: list[int] = Field(min_length=1, description="List User IDs")
    action: str = Field(description="Action: approve, reject, deactivate")
    notes: str | None = Field(
        None, max_length=200, description="Catatan untuk semua user"
    )
    performed_by: int = Field(gt=0, description="Admin ID")
    model_config = ConfigDict(str_strip_whitespace=True)


class AdminActionResult(BaseModel):
    """Model untuk result dari admin operations."""

    success: bool = Field(description="Operasi berhasil atau tidak")
    processed_count: int = Field(ge=0, description="Jumlah user yang berhasil diproses")
    failed_count: int = Field(ge=0, description="Jumlah user yang gagal")
    message: str = Field(description="Pesan hasil operasi")
