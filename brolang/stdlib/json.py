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


module = SimpleNamespace(
    parsing=parsing,
    string=string,
    baca=baca,
    tulis=tulis,
)
