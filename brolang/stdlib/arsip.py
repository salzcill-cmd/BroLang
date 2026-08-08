"""
Modul Arsip BroLang
===================

Arsip & kompresi: membuat/membaca arsip ZIP dan kompresi teks —
berbasis stdlib Python (zipfile, zlib, base64) tanpa dependency eksternal.

Fitur:
- Arsip ZIP: buat_zip, tambah_ke_zip, ekstrak_zip, daftar_zip
- Kompresi teks: kompres (zlib + Base64) & dekompres

Contoh:
    impor arsip

    # Arsip ZIP
    arsip.buat_zip("backup.zip", ["data.txt", "catatan.md"])
    tulis arsip.daftar_zip("backup.zip")        # [data.txt, catatan.md]
    arsip.ekstrak_zip("backup.zip", "hasil/")
    arsip.tambah_ke_zip("backup.zip", "baru.txt")

    # Kompresi teks
    buat padat = arsip.kompres("teks panjang ...")
    tulis arsip.dekompres(padat)
"""

import base64 as _base64
import os as _os
import zipfile as _zipfile
import zlib as _zlib
from types import SimpleNamespace


def _daftar_file(isi) -> list:
    """Normalisasi input file: str tunggal atau list jadi list."""
    if isinstance(isi, (list, tuple)):
        return [str(f) for f in isi]
    return [str(isi)]


def buat_zip(nama_zip: str, daftar_file) -> bool:
    """Membuat arsip ZIP baru berisi file-file yang diberikan.

    Args:
        nama_zip: Nama file arsip (mis. "backup.zip")
        daftar_file: Satu file atau list file yang ingin diarsipkan

    Returns:
        benar bila setidaknya satu file berhasil diarsipkan, salah bila tidak

    Contoh:
        arsip.buat_zip("backup.zip", ["a.txt", "b.txt"])
        arsip.buat_zip("satu.zip", "catatan.md")
    """
    ditulis = 0
    try:
        with _zipfile.ZipFile(str(nama_zip), "w", _zipfile.ZIP_DEFLATED) as z:
            for f in _daftar_file(daftar_file):
                if _os.path.exists(f):
                    z.write(f, _os.path.basename(f))
                    ditulis += 1
        return ditulis > 0
    except (OSError, ValueError):
        return False


def tambah_ke_zip(nama_zip: str, daftar_file) -> bool:
    """Menambahkan file ke arsip ZIP yang sudah ada (append).

    Returns:
        benar bila setidaknya satu file berhasil ditambahkan, salah bila tidak

    Contoh:
        arsip.tambah_ke_zip("backup.zip", "file_baru.txt")
    """
    ditulis = 0
    try:
        with _zipfile.ZipFile(str(nama_zip), "a", _zipfile.ZIP_DEFLATED) as z:
            for f in _daftar_file(daftar_file):
                if _os.path.exists(f):
                    z.write(f, _os.path.basename(f))
                    ditulis += 1
        return ditulis > 0
    except (OSError, ValueError):
        return False


def _nama_aman(nama: str) -> bool:
    """Cek nama member ZIP aman dari zip-slip (path traversal)."""
    normal = str(nama).replace("\\", "/")
    if normal.startswith("/"):
        return False
    return ".." not in normal.split("/")


def ekstrak_zip(nama_zip: str, tujuan: str = ".") -> list:
    """Mengekstrak isi arsip ZIP ke folder tujuan (dengan proteksi zip-slip).

    Member berbahaya seperti `../keluar/arsip` dilewati demi keamanan.
    Mengembalikan daftar nama file yang diekstrak.

    Contoh:
        buat isi = arsip.ekstrak_zip("backup.zip", "restore/")
    """
    try:
        with _zipfile.ZipFile(str(nama_zip), "r") as z:
            diekstrak = []
            for member in z.namelist():
                if _nama_aman(member):
                    z.extract(member, str(tujuan))
                    diekstrak.append(member)
            return diekstrak
    except (OSError, ValueError, _zipfile.BadZipFile):
        return []


def daftar_zip(nama_zip: str) -> list:
    """Mendaftar isi arsip ZIP (nama file di dalam arsip).

    Contoh:
        tulis arsip.daftar_zip("backup.zip")
    """
    try:
        with _zipfile.ZipFile(str(nama_zip), "r") as z:
            return z.namelist()
    except (OSError, ValueError, _zipfile.BadZipFile):
        return []


# --- Kompresi teks (zlib + Base64) ---


def kompres(teks: str) -> str:
    """Mengompres teks jadi string Base64 yang lebih pendek.

    Berguna untuk menyimpan data berulang / log / respons API
    dalam bentuk teks yang aman disimpan.

    Contoh:
        buat padat = arsip.kompres("halo" * 100)
        tulis arsip.dekompres(padat)   # halo halo halo ...
    """
    data = _zlib.compress(str(teks).encode("utf-8"), level=9)
    return _base64.b64encode(data).decode("ascii")


def dekompres(data: str) -> str:
    """Mengembalikan teks asli dari hasil arsip.kompres().

    Contoh:
        tulis arsip.dekompres(padat)
    """
    try:
        raw = _base64.b64decode(str(data))
        return _zlib.decompress(raw).decode("utf-8")
    except (ValueError, _zlib.error):
        return ""


module = SimpleNamespace(
    buat_zip=buat_zip,
    tambah_ke_zip=tambah_ke_zip,
    ekstrak_zip=ekstrak_zip,
    daftar_zip=daftar_zip,
    kompres=kompres,
    dekompres=dekompres,
)
