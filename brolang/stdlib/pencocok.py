"""
Modul Pencocokan Pola (Regex) untuk BroLang
============================================

Menyediakan fungsi pencocokan pola reguler.

Contoh:
    impor pencocok
    hasil = pencocok.cari(r'\d+', "ada 123 angka")
    tulis(hasil)
"""

import re
from types import SimpleNamespace


def cari(pattern, string, flags=0):
    """Mencari pola dalam string."""
    match = re.search(pattern, string, flags)
    if match:
        return SimpleNamespace(
            grup=match.group,
            grups=match.groups(),
            mulai=match.start(),
            akhir=match.end(),
            teks=match.group(),
        )
    return None


def cari_semua(pattern, string, flags=0):
    """Mencari semua kemunculan pola."""
    return re.findall(pattern, string, flags)


def cari_semua_detail(pattern, string, flags=0):
    """Mencari semua kemunculan dengan detail."""
    results = []
    for match in re.finditer(pattern, string, flags):
        results.append(SimpleNamespace(
            grup=match.group,
            grups=match.groups(),
            mulai=match.start(),
            akhir=match.end(),
            teks=match.group(),
        ))
    return results


def cocok(pattern, string, flags=0):
    """Mengecek apakah string cocok dengan pola (full match)."""
    return bool(re.fullmatch(pattern, string, flags))


def mengandung(pattern, string, flags=0):
    """Mengecek apakah string mengandung pola."""
    return bool(re.search(pattern, string, flags))


def ganti(pattern, replacement, string, flags=0):
    """Mengganti pola dengan string baru."""
    return re.sub(pattern, replacement, string, flags)


def ganti_dengan_func(pattern, func, string, flags=0):
    """Mengganti pola dengan hasil fungsi."""
    return re.sub(pattern, func, string, flags)


def bagi(pattern, string, flags=0):
    """Membagi string berdasarkan pola."""
    return re.split(pattern, string, flags)


def escape(string):
    """Escape karakter khusus regex."""
    return re.escape(string)


def compile(pattern, flags=0):
    """Mengkompilasi pola regex."""
    compiled = re.compile(pattern, flags)
    return SimpleNamespace(
        cari=lambda s: cari(pattern, s, flags),
        cari_semua=lambda s: cari_semua(pattern, s, flags),
        cocok=lambda s: cocok(pattern, s, flags),
        mengandung=lambda s: mengandung(pattern, s, flags),
        ganti=lambda r, s: ganti(pattern, r, s, flags),
        bagi=lambda s: bagi(pattern, s, flags),
        pola=pattern,
    )


# Module interface
module = SimpleNamespace(
    cari=cari,
    cari_semua=cari_semua,
    cari_semua_detail=cari_semua_detail,
    cocok=cocok,
    mengandung=mengandung,
    ganti=ganti,
    ganti_dengan_func=ganti_dengan_func,
    bagi=bagi,
    escape=escape,
    compile=compile,
    # Flags
    IGNORECASE=re.IGNORECASE,
    MULTILINE=re.MULTILINE,
    DOTALL=re.DOTALL,
    VERBOSE=re.VERBOSE,
)
