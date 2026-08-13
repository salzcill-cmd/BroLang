"""
Modul Dasar BroLang
===================

Encoding & utilitas dasar: konversi encoding (base64, hex, bin, url, html)
dan konversi tipe data.

Contoh:
    impor dasar
    teks = dasar.ke_base64("halo")
    angka = dasar.ke_angka("42")
"""

import base64
import binascii
from types import SimpleNamespace
from typing import Any, Optional


# ============= Encoding =============


def ke_base64(data) -> str:
    """Encode ke base64."""
    return base64.b64encode(str(data).encode("utf-8")).decode("utf-8")


def dari_base64(encoded: str) -> str:
    """Decode dari base64."""
    return base64.b64decode(encoded.encode("utf-8")).decode("utf-8")


def ke_base32(data) -> str:
    """Encode ke base32."""
    return base64.b32encode(str(data).encode("utf-8")).decode("utf-8")


def dari_base32(encoded: str) -> str:
    """Decode dari base32."""
    return base64.b32decode(encoded.encode("utf-8")).decode("utf-8")


def ke_hex(data) -> str:
    """Encode ke heksadesimal."""
    return binascii.hexlify(str(data).encode("utf-8")).decode("utf-8")


def dari_hex(encoded: str) -> str:
    """Decode dari heksadesimal."""
    return binascii.unhexlify(encoded.encode("utf-8")).decode("utf-8")


def ke_bin(data) -> str:
    """Encode ke biner."""
    return "".join(f"{b:08b}" for b in str(data).encode("utf-8"))


def dari_bin(encoded: str) -> str:
    """Decode dari biner."""
    bits = encoded.replace(" ", "")
    return "".join(
        chr(int(bits[i:i + 8], 2)) for i in range(0, len(bits), 8)
    )


def ke_url(data) -> str:
    """Encode URL."""
    from urllib.parse import quote
    return quote(str(data), safe="")


def dari_url(encoded: str) -> str:
    """Decode URL."""
    from urllib.parse import unquote
    return unquote(encoded)


def ke_html(data) -> str:
    """Encode HTML entities."""
    import html as _html
    return _html.escape(str(data))


def dari_html(encoded: str) -> str:
    """Decode HTML entities."""
    import html as _html
    return _html.unescape(str(encoded))


# ============= v7.1: konversi tipe & inspeksi =============


def ke_angka(teks) -> float:
    """Konversi teks ke angka (int bila bulat, float bila desimal)."""
    if isinstance(teks, (int, float)):
        return teks
    s = str(teks).strip().replace(",", ".")
    try:
        return int(s)
    except ValueError:
        return float(s)


def ke_teks(nilai) -> str:
    """Konversi nilai apa pun ke teks (str)."""
    if nilai is None:
        return "kosong"
    if isinstance(nilai, bool):
        return "benar" if nilai else "salah"
    return str(nilai)


def ke_boolean(teks) -> bool:
    """Konversi teks ke boolean: \"benar\"/\"true\"/\"1\" -> benar, dst."""
    if isinstance(teks, bool):
        return teks
    if isinstance(teks, (int, float)):
        return teks != 0
    s = str(teks).strip().lower()
    return s in ("benar", "true", "ya", "1", "yes", "on")


def jenis(nilai) -> str:
    """Nama tipe BroLang: angka/desimal/teks/boolean/list/objek/kosong."""
    if nilai is None:
        return "kosong"
    if isinstance(nilai, bool):
        return "boolean"
    if isinstance(nilai, int):
        return "angka"
    if isinstance(nilai, float):
        return "desimal"
    if isinstance(nilai, str):
        return "teks"
    if isinstance(nilai, (list, tuple)):
        return "list"
    if isinstance(nilai, dict):
        return "objek"
    return type(nilai).__name__


def panjang(nilai) -> int:
    """Panjang list/teks/objek (len)."""
    return len(nilai)


def adalah_kosong(nilai) -> bool:
    """Cek apakah nilai kosong (None, \"\", [], {}, 0)."""
    return nilai is None or nilai == "" or nilai == [] or nilai == {} or nilai == 0


def unik(nilai) -> list:
    """Hapus duplikat dari list dengan mempertahankan urutan (v7.2)."""
    seen = set()
    out = []
    for item in nilai:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def terbalik(nilai):
    """Balik urutan list atau string (v7.2)."""
    if isinstance(nilai, str):
        return nilai[::-1]
    return list(reversed(list(nilai)))


def urutkan(nilai, turun=False) -> list:
    """Urutkan list (naik default; turun bila argumen kedua benar) (v7.2)."""
    return sorted(list(nilai), reverse=bool(turun))


def kunci(objek) -> list:
    """Kunci-kunci objek/dict (v7.2)."""
    return list(objek.keys())


def nilai(objek) -> list:
    """Nilai-nilai objek/dict (v7.2)."""
    return list(objek.values())


def item(objek) -> list:
    """Pasangan (kunci, nilai) objek/dict (v7.2)."""
    return list(objek.items())


module = SimpleNamespace(
    ke_base64=ke_base64,
    dari_base64=dari_base64,
    ke_base32=ke_base32,
    dari_base32=dari_base32,
    ke_hex=ke_hex,
    dari_hex=dari_hex,
    ke_bin=ke_bin,
    dari_bin=dari_bin,
    ke_url=ke_url,
    dari_url=dari_url,
    ke_html=ke_html,
    dari_html=dari_html,
    # v7.1
    ke_angka=ke_angka,
    ke_teks=ke_teks,
    ke_boolean=ke_boolean,
    jenis=jenis,
    panjang=panjang,
    adalah_kosong=adalah_kosong,
    # v7.2
    unik=unik,
    terbalik=terbalik,
    urutkan=urutkan,
    kunci=kunci,
    nilai=nilai,
    item=item,
)
