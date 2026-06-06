"""
Sistem Error BroLang
=====================

BroLang memiliki sistem error yang jauh lebih baik daripada Python.
Setiap error menyertakan:
- Lokasi error (baris, kolom)
- Penjelasan sederhana dalam Bahasa Indonesia
- Solusi yang dapat ditindaklanjuti
- Contoh perbaikan

Penggunaan:
    raise BroLangError(
        message="Kamu lupa menutup tanda kutip.",
        line=10,
        column=15,
        solution="Tambahkan \" pada akhir teks.",
        example='tulis "Halo"'
    )
"""

from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class ErrorDetail:
    """Detail dari sebuah error untuk ditampilkan ke pengguna."""

    message: str
    line: int
    column: int
    solution: str = ""
    example: str = ""
    file_path: str = ""
    source_line: str = ""
    hint: str = ""


class BroLangError(Exception):
    """Base exception untuk semua error BroLang.

    Error ini dirancang untuk memberikan feedback yang jelas dan
    actionable kepada programmer, terutama pemula.
    """

    def __init__(
        self,
        message: str = "",
        line: int = 0,
        column: int = 0,
        solution: str = "",
        example: str = "",
        file_path: str = "",
        source_line: str = "",
        hint: str = "",
    ):
        self.detail = ErrorDetail(
            message=message,
            line=line,
            column=column,
            solution=solution,
            example=example,
            file_path=file_path,
            source_line=source_line,
            hint=hint,
        )
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        """Format error message with detailed information."""
        parts: List[str] = []
        parts.append("=" * 50)
        parts.append("[Error BroLang]")
        parts.append("=" * 50)

        if self.detail.file_path:
            parts.append(f"File    : {self.detail.file_path}")

        if self.detail.line > 0:
            parts.append(f"Baris   : {self.detail.line}")
            if self.detail.column > 0:
                parts.append(f"Kolom   : {self.detail.column}")

        if self.detail.source_line:
            parts.append("")
            parts.append(f"  {self.detail.source_line}")
            if self.detail.column > 0:
                parts.append(f"  {' ' * (self.detail.column - 1)}^")

        parts.append("")
        parts.append(f"Pesan   : {self.detail.message}")

        if self.detail.solution:
            parts.append(f"Solusi  : {self.detail.solution}")

        if self.detail.example:
            parts.append(f"Contoh  : {self.detail.example}")

        if self.detail.hint:
            parts.append(f"Tips    : {self.detail.hint}")

        parts.append("=" * 50)
        return "\n".join(parts)

    def to_dict(self) -> dict:
        """Convert error to dictionary for LSP and other tools."""
        return {
            "type": self.__class__.__name__,
            "message": self.detail.message,
            "line": self.detail.line,
            "column": self.detail.column,
            "solution": self.detail.solution,
            "example": self.detail.example,
            "file_path": self.detail.file_path,
        }


class LexerError(BroLangError):
    """Error yang terjadi saat proses lexing/tokenizing."""
    pass


class ParserError(BroLangError):
    """Error yang terjadi saat proses parsing."""
    pass


class SemanticError(BroLangError):
    """Error yang terjadi saat analisis semantik."""
    pass


class RuntimeError_(BroLangError):
    """Error yang terjadi saat runtime/eksekusi.

    Nama RuntimeError_ digunakan untuk menghindari konflik
    dengan built-in RuntimeError Python.
    """
    pass


class TypeError_(BroLangError):
    """Error yang terjadi karena ketidakcocokan tipe data."""
    pass


class NameError_(BroLangError):
    """Error yang terjadi karena variabel tidak ditemukan."""
    pass


class SyntaxError_(BroLangError):
    """Error yang terjadi karena kesalahan sintaks."""
    pass


class ImportError_(BroLangError):
    """Error yang terjadi karena gagal mengimpor modul."""
    pass


class ZeroDivisionError_(BroLangError):
    """Error yang terjadi karena pembagian dengan nol."""
    pass


class IndexError_(BroLangError):
    """Error yang terjadi karena indeks di luar batas."""
    pass


class FileError_(BroLangError):
    """Error yang terjadi karena operasi file gagal."""
    pass
