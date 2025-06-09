"""Admin-specific user management schemas."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class UserVerification(BaseModel):
    """Model untuk admin verifikasi user."""

    user_id: int = Field(gt=0, description="User ID yang akan diverifikasi")
    is_verified: bool = Field(description="Status verifikasi (approve/reject)")
    notes: str | None = Field(
        None, max_length=200, description="Catatan admin (opsional)"
    )
    verified_by: int = Field(gt=0, description="Admin ID yang melakukan verifikasi")
    model_config = ConfigDict(str_strip_whitespace=True)


class BulkUserVerification(BaseModel):
    """Model untuk bulk verification users."""

    user_ids: list[int] = Field(min_length=1, description="List User IDs")
    is_verified: bool = Field(description="Status verifikasi untuk semua user")
    notes: str | None = Field(
        None, max_length=200, description="Catatan untuk semua user"
    )
    verified_by: int = Field(gt=0, description="Admin ID")


class VerificationResult(BaseModel):
    """Model untuk result verification operation."""

    success: bool = Field(description="Operasi berhasil atau tidak")
    processed_count: int = Field(ge=0, description="Jumlah user yang diproses")
    failed_count: int = Field(ge=0, description="Jumlah user yang gagal")
    message: str = Field(description="Pesan result")
