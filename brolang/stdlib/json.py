"""
Modul JSON BroLang
==================

Parsing dan serialisasi JSON.

Contoh:
    impor json
    data = json.parsing('{"nama": "Budi"}')
    teks = json.string({"nama": "Budi"})
"""

import json as _json
from types import SimpleNamespace
from typing import Any


def parsing(s: str) -> Any:
    """Parse JSON string ke data BroLang."""
    return _json.loads(s)


def string(data: Any, indent: int = 2) -> str:
    """Konversi data ke JSON string."""
    return _json.dumps(data, indent=indent, ensure_ascii=False)


def baca(path: str, encoding: str = "utf-8") -> Any:
    """Baca file JSON."""
    with open(path, "r", encoding=encoding) as f:
        return _json.load(f)


def tulis(path: str, data: Any, indent: int = 2, encoding: str = "utf-8") -> None:
    """Tulis data ke file JSON."""
    with open(path, "w", encoding=encoding) as f:
        _json.dump(data, f, indent=indent, ensure_ascii=False)


def valid(teks: str) -> bool:
    """Cek apakah teks adalah JSON yang valid (v7.1)."""
    try:
        _json.loads(teks)
        return True
    except (ValueError, TypeError):
        return False


# v7.1: alias aman-keyword (`tulis` adalah keyword bahasa) — didefinisikan
# di level modul agar berfungsi di interpreter (SimpleNamespace) DAN VM
# (importlib memuat modul .py langsung).
tulis_file = tulis


module = SimpleNamespace(
    parsing=parsing,
    string=string,
    baca=baca,
    tulis=tulis,
    tulis_file=tulis,  # v7.1: alias aman-keyword
    valid=valid,
)
