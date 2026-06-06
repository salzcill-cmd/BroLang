"""
Modul Teks BroLang
==================

Fungsi manipulasi string/teks.

Contoh:
    impor teks
    teks.upper("halo")
"""

from types import SimpleNamespace
from typing import List, Optional


def upper(s: str) -> str:
    """Ubah ke huruf kapital."""
    return s.upper()


def lower(s: str) -> str:
    """Ubah ke huruf kecil."""
    return s.lower()


def kapital(s: str) -> str:
    """Kapitalisasi huruf pertama."""
    return s.capitalize()


def judul(s: str) -> str:
    """Kapitalisasi setiap kata."""
    return s.title()


def potong(s: str, delimiter: Optional[str] = None) -> List[str]:
    """Memotong string menjadi list."""
    return s.split(delimiter) if delimiter else s.split()


def gabung(parts: List[str], separator: str = "") -> str:
    """Menggabungkan list menjadi string."""
    return separator.join(parts)


def ganti(s: str, old: str, new: str) -> str:
    """Mengganti substring."""
    return s.replace(old, new)


def panjang(s: str) -> int:
    """Panjang string."""
    return len(s)


def strip(s: str) -> str:
    """Menghapus spasi di awal dan akhir."""
    return s.strip()


def cari(s: str, sub: str) -> int:
    """Mencari posisi substring."""
    return s.find(sub)


def mulai(s: str, prefix: str) -> bool:
    """Cek apakah dimulai dengan prefix."""
    return s.startswith(prefix)


def berakhir(s: str, suffix: str) -> bool:
    """Cek apakah diakhiri dengan suffix."""
    return s.endswith(suffix)


def potong_kiri(s: str, chars: Optional[str] = None) -> str:
    """Menghapus karakter dari kiri."""
    return s.lstrip(chars)


def potong_kanan(s: str, chars: Optional[str] = None) -> str:
    """Menghapus karakter dari kanan."""
    return s.rstrip(chars)


module = SimpleNamespace(
    upper=upper,
    lower=lower,
    kapital=kapital,
    judul=judul,
    potong=potong,
    gabung=gabung,
    ganti=ganti,
    panjang=panjang,
    strip=strip,
    cari=cari,
    mulai=mulai,
    berakhir=berakhir,
    potong_kiri=potong_kiri,
    potong_kanan=potong_kanan,
)
