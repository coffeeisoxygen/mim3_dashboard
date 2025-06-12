"""Advanced rotators yang bisa dikonfigurasi via admin."""

import datetime
from typing import Protocol, runtime_checkable


@runtime_checkable
class RotatorProtocol(Protocol):
    """Protocol untuk custom rotators."""

    def should_rotate(self, message, file) -> bool:
        """Menentukan apakah file log perlu dirotasi berdasarkan kondisi tertentu.

        Method ini dipanggil setiap kali ada log message baru untuk mengecek
        apakah file log saat ini sudah perlu dirotasi (dipindah/diganti dengan
        file baru). Implementasi bisa berdasarkan ukuran file, waktu, atau
        kondisi custom lainnya.

        Args:
            message: Log message record dari Loguru yang berisi informasi
                    lengkap tentang log entry (level, time, content, dll)
            file: File object dari log file yang sedang aktif untuk
                  pengecekan ukuran atau properti file lainnya

        Returns:
            bool: True jika file perlu dirotasi, False jika masih bisa
                 digunakan untuk log berikutnya

        Examples:
            >>> rotator = AdminConfigurableRotator(size_mb=10)
            >>> should_rotate = rotator.should_rotate(message, file)
            >>> if should_rotate:
            ...     # Loguru akan membuat file log baru
            ...     print("Creating new log file...")

        Note:
            - Method ini harus efisien karena dipanggil untuk setiap log entry
            - Jangan melakukan operasi yang berat/lambat di sini
            - File seek position mungkin berubah setelah method ini dipanggil
        """
        ...


class AdminConfigurableRotator:
    """Rotator yang configurable via admin settings."""

    def __init__(self, *, size_mb: int = 50, rotate_at_hour: int = 2):
        self.size_limit = size_mb * 1024 * 1024
        self.rotate_hour = rotate_at_hour
        self._next_rotation = self._calculate_next_rotation()

    def _calculate_next_rotation(self) -> datetime.datetime:
        now = datetime.datetime.now()
        target = now.replace(hour=self.rotate_hour, minute=0, second=0, microsecond=0)
        if now >= target:
            target += datetime.timedelta(days=1)
        return target

    def should_rotate(self, message, file) -> bool:
        """Check apakah rotasi diperlukan berdasarkan kondisi tertentu."""
        file.seek(0, 2)
        if file.tell() + len(message) > self.size_limit:
            return True

        # Check time-based rotation
        now = message.record["time"]
        if now >= self._next_rotation:
            self._next_rotation = self._calculate_next_rotation()
            return True

        return False


# Default configurations untuk different log types
DEFAULT_ROTATORS = {
    "info": AdminConfigurableRotator(size_mb=10, rotate_at_hour=2),
    "error": AdminConfigurableRotator(size_mb=50, rotate_at_hour=2),
    "debug": AdminConfigurableRotator(size_mb=100, rotate_at_hour=6),
}
