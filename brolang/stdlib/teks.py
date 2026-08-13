r"""
Modul Teks BroLang
==================

Fungsi manipulasi string/teks.

Contoh:
    impor teks
    teks.upper("halo")
    teks.balik("abc")              # "cba"
    teks.regex_cari("Halo 123", "\\d+")   # "123"
"""

import re
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


# ============= v7.1: Manipulasi lanjutan =============


def balik(s: str) -> str:
    """Membalik urutan karakter: balik("abc") -> "cba"."""
    return s[::-1]


def berulang(s: str, n: int) -> str:
    """Mengulang string n kali: berulang("ab", 3) -> "ababab"."""
    return s * n


def hapus_spasi(s: str) -> str:
    """Menghapus SEMUA spasi/karakter kosong: hapus_spasi("a b  c") -> "abc"."""
    return "".join(s.split())


def pad_kiri(s: str, lebar: int, karakter: str = " ") -> str:
    """Ratakan kiri ke lebar tertentu dengan karakter pengisi."""
    return s.ljust(lebar, karakter)


def pad_kanan(s: str, lebar: int, karakter: str = " ") -> str:
    """Ratakan kanan ke lebar tertentu dengan karakter pengisi."""
    return s.rjust(lebar, karakter)


def terpusat(s: str, lebar: int, karakter: str = " ") -> str:
    """Ratakan tengah ke lebar tertentu dengan karakter pengisi."""
    return s.center(lebar, karakter)


def jumlah(s: str, sub: str) -> int:
    """Menghitung berapa kali substring muncul: jumlah("abab", "ab") -> 2."""
    return s.count(sub)


def hitung_kata(s: str) -> int:
    """Menghitung jumlah kata dalam string."""
    return len(s.split())


def pecah_baris(s: str) -> List[str]:
    """Memotong string per baris (splitlines)."""
    return s.splitlines()


# ============= v7.1: Regex =============


def regex_cari(s: str, pola: str) -> Optional[str]:
    """Mencari pola regex; kembalikan teks pertama yang cocok (atau kosong)."""
    m = re.search(pola, s)
    return m.group(0) if m else None


def regex_cari_semua(s: str, pola: str) -> List[str]:
    """Mencari semua kecocokan pola regex -> list teks."""
    return re.findall(pola, s)


def regex_ganti(s: str, pola: str, pengganti: str) -> str:
    """Mengganti semua kecocokan pola regex dengan teks pengganti."""
    return re.sub(pola, pengganti, s)


def regex_cocok(s: str, pola: str) -> bool:
    """Cek apakah string cocok dengan pola regex."""
    return re.fullmatch(pola, s) is not None


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
    # v7.1
    balik=balik,
    berulang=berulang,
    hapus_spasi=hapus_spasi,
    pad_kiri=pad_kiri,
    pad_kanan=pad_kanan,
    terpusat=terpusat,
    jumlah=jumlah,
    hitung_kata=hitung_kata,
    pecah_baris=pecah_baris,
    regex_cari=regex_cari,
    regex_cari_semua=regex_cari_semua,
    regex_ganti=regex_ganti,
    regex_cocok=regex_cocok,
)
