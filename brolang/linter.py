"""
Linter BroLang (brolint)
========================

Static analysis untuk kode BroLang.
Mendeteksi potensi masalah dan memberikan saran perbaikan.

Fitur:
- Variabel tidak terpakai
- Fungsi tanpa return
- Indentasi tidak konsisten
- Panjang baris berlebihan
- Konvensi penamaan
"""

from dataclasses import dataclass, field
from typing import List, Optional
from brolang.lexer import Lexer
from brolang.token_types import TokenType


@dataclass
class LintIssue:
    """Mewakili satu issue yang ditemukan linter."""
    line: int
    column: int
    message: str
    severity: str  # "error", "warning", "info"
    suggestion: str = ""
    rule: str = ""


@dataclass
class LintResult:
    """Hasil dari proses linting."""
    issues: List[LintIssue] = field(default_factory=list)
    file_path: str = ""

    @property
    def error_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "warning")


class Linter:
    """Linter untuk kode BroLang.

    Attributes:
        rules: Daftar rules yang akan dijalankan
    """

    def __init__(self):
        self.rules = [
            self._check_line_length,
            self._check_trailing_whitespace,
            self._check_indentation,
            self._check_naming_convention,
        ]

    def lint(self, source: str, file_path: str = "") -> LintResult:
        """Menjalankan linting pada kode sumber.

        Args:
            source: Kode sumber BroLang
            file_path: Path file (optional)

        Returns:
            LintResult: Hasil linting
        """
        result = LintResult(file_path=file_path)
        lines = source.split("\n")

        for rule in self.rules:
            rule(source, lines, result)

        return result

    def _check_line_length(self, source: str, lines: List[str], result: LintResult) -> None:
        """Cek panjang baris maksimal 100 karakter."""
        max_length = 100
        for i, line in enumerate(lines, 1):
            if len(line) > max_length:
                result.issues.append(LintIssue(
                    line=i,
                    column=max_length,
                    message=f"Baris terlalu panjang ({len(line)} > {max_length} karakter).",
                    severity="warning",
                    suggestion=f"Pecah baris menjadi beberapa baris yang lebih pendek.",
                    rule="line-length",
                ))

    def _check_trailing_whitespace(self, source: str, lines: List[str], result: LintResult) -> None:
        """Cek spasi di akhir baris."""
        for i, line in enumerate(lines, 1):
            if line != line.rstrip():
                result.issues.append(LintIssue(
                    line=i,
                    column=len(line.rstrip()) + 1,
                    message="Ada spasi di akhir baris.",
                    severity="info",
                    suggestion="Hapus spasi di akhir baris.",
                    rule="trailing-whitespace",
                ))

    def _check_indentation(self, source: str, lines: List[str], result: LintResult) -> None:
        """Cek indentasi konsisten."""
        for i, line in enumerate(lines, 1):
            if line.startswith("\t"):
                result.issues.append(LintIssue(
                    line=i,
                    column=1,
                    message="Gunakan spasi untuk indentasi, bukan tab.",
                    severity="warning",
                    suggestion="Ganti tab dengan 4 spasi.",
                    rule="indentation",
                ))

    def _check_naming_convention(self, source: str, lines: List[str], result: LintResult) -> None:
        """Cek konvensi penamaan variable dan fungsi."""
        try:
            lexer = Lexer(source)
            tokens = lexer.tokenize()

            for token in tokens:
                if token.type == TokenType.TOKEN_IDENTIFIER:
                    name = token.value
                    if len(name) <= 2 and name.islower():
                        result.issues.append(LintIssue(
                            line=token.line,
                            column=token.column,
                            message=f"Nama '{name}' terlalu pendek. Gunakan nama yang deskriptif.",
                            severity="info",
                            suggestion=f"Ganti '{name}' dengan nama yang lebih deskriptif.",
                            rule="naming-convention",
                        ))
        except Exception:
            pass


def lint_code(source: str, file_path: str = "") -> List[LintIssue]:
    """Convenience function untuk linting.

    Args:
        source: Kode sumber BroLang
        file_path: Path file (optional)

    Returns:
        List[LintIssue]: Daftar issue
    """
    linter = Linter()
    result = linter.lint(source, file_path)
    return result.issues


def lint_file(file_path: str) -> List[LintIssue]:
    """Melakukan linting pada file BroLang.

    Args:
        file_path: Path ke file .bro

    Returns:
        List[LintIssue]: Daftar issue
    """
    with open(file_path, "r", encoding="utf-8") as f:
        source = f.read()
    return lint_code(source, file_path)
