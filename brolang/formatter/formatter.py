"""
Formatter Implementation untuk BroLang
=======================================

Mengubah kode BroLang menjadi format yang rapi dan konsisten.
"""

from typing import List, Optional, Tuple
from brolang.token_types import Token, TokenType, KEYWORDS


def format_code(source: str) -> str:
    """Memformat kode BroLang.

    Args:
        source: Kode sumber BroLang

    Returns:
        str: Kode yang sudah diformat
    """
    lines = source.split("\n")
    formatted_lines: List[str] = []
    indent_level = 0
    in_block = False

    for i, line in enumerate(lines):
        stripped = line.strip()

        if not stripped:
            formatted_lines.append("")
            continue

        if stripped.startswith("#"):
            formatted_lines.append(line)
            continue

        # Hitung indentasi berdasarkan struktur blok
        if in_block:
            indent_level += 1
            in_block = False

        # Keywords yang memulai blok
        block_starters = [
            "jika", "selama", "untuk", "fungsi", "kelas",
            "coba", "lainnya",
        ]

        # Check if this line starts a block
        first_word = stripped.split()[0] if stripped.split() else ""
        if first_word in block_starters or stripped.endswith("maka") or stripped.endswith("lakukan"):
            in_block = True

        # DEDENT untuk selesai
        if first_word == "selesai" or first_word == "lainnya" or first_word == "tangkap":
            indent_level = max(0, indent_level - 1)

        indent = "    " * indent_level
        formatted_lines.append(f"{indent}{stripped}")

    return "\n".join(formatted_lines)


def format_file(file_path: str) -> None:
    """Memformat file BroLang dan menulis kembali.

    Args:
        file_path: Path ke file .bro
    """
    with open(file_path, "r", encoding="utf-8") as f:
        source = f.read()

    formatted = format_code(source)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(formatted)


def check_format(file_path: str) -> bool:
    """Memeriksa apakah file sudah diformat.

    Args:
        file_path: Path ke file .bro

    Returns:
        bool: True jika sudah rapi
    """
    with open(file_path, "r", encoding="utf-8") as f:
        source = f.read()

    formatted = format_code(source)
    return source == formatted
