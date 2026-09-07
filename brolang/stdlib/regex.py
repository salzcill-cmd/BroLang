"""
Modul Regex - Pencocok Pola Lanjutan untuk BroLang
===================================================

Modul untuk pencocokan pola menggunakan regular expressions.

Contoh:
    impor regex

    # Cek apakah pola cocok
    regex.cocok("abc123", r"[a-z]+\\d+")

    # Cari semua kecocokan
    regex.cari_semua("abc 123 def 456", r"\\d+")

    # Ganti teks
    regex.ganti("Hello World", r"World", "BroLang")

    # Ambil group
    regex.ambil_group("abc123def", r"(\\d+)([a-z]+)")
"""

from types import SimpleNamespace
import re as _re


def _cocok(teks, pola, flags=None):
    """Cek apakah pola cocok dengan teks."""
    f = 0
    if flags:
        if "i" in flags:
            f |= _re.IGNORECASE
        if "m" in flags:
            f |= _re.MULTILINE
        if "s" in flags:
            f |= _re.DOTALL
    return bool(_re.search(pola, teks, f))


def _cari_satu(teks, pola, flags=None):
    """Cari satu kecocokan pertama. Kembalikan teks cocok atau None."""
    f = 0
    if flags:
        if "i" in flags:
            f |= _re.IGNORECASE
        if "m" in flags:
            f |= _re.MULTILINE
    m = _re.search(pola, teks, f)
    return m.group(0) if m else None


def _cari_semua(teks, pola, flags=None):
    """Cari semua kecocokan. Kembalikan list teks."""
    f = 0
    if flags:
        if "i" in flags:
            f |= _re.IGNORECASE
        if "m" in flags:
            f |= _re.MULTILINE
    return _re.findall(pola, teks, f)


def _ganti(teks, pola, pengganti, flags=None):
    """Ganti semua kecocokan dengan teks pengganti."""
    f = 0
    if flags:
        if "i" in flags:
            f |= _re.IGNORECASE
    return _re.sub(pola, pengganti, teks, flags=f)


def _ambil_group(teks, pola, group=1, flags=None):
    """Ambil group tertentu dari kecocokan pertama."""
    f = 0
    if flags:
        if "i" in flags:
            f |= _re.IGNORECASE
    m = _re.search(pola, teks, f)
    if m:
        try:
            return m.group(group)
        except IndexError:
            return None
    return None


def _ambil_semua_group(teks, pola, flags=None):
    """Ambil semua group dari semua kecocokan. Kembalikan list of tuples."""
    f = 0
    if flags:
        if "i" in flags:
            f |= _re.IGNORECASE
    return _re.findall(pola, teks, f)


def _pecah(teks, pola, flags=None):
    """Pecah teks berdasarkan pola."""
    f = 0
    if flags:
        if "i" in flags:
            f |= _re.IGNORECASE
    return _re.split(pola, teks, flags=f)


def _valid(pola):
    """Cek apakah pola regex valid."""
    try:
        _re.compile(pola)
        return True
    except _re.error:
        return False


module = SimpleNamespace(
    cocok=_cocok,
    cari_satu=_cari_satu,
    cari_semua=_cari_semua,
    ganti=_ganti,
    ambil_group=_ambil_group,
    ambil_semua_group=_ambil_semua_group,
    pecah=_pecah,
    valid=_valid,
)
