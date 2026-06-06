"""
Modul File BroLang
==================

Operasi baca/tulis file.

Contoh:
    impor file
    isi = file.baca("data.txt")
    file.tulis("output.txt", "Halo Dunia")
"""

from types import SimpleNamespace
from typing import Optional, List
import os


def baca(path: str, encoding: str = "utf-8") -> str:
    """Membaca file teks."""
    with open(path, "r", encoding=encoding) as f:
        return f.read()


def tulis(path: str, konten: str, encoding: str = "utf-8") -> int:
    """Menulis file teks."""
    with open(path, "w", encoding=encoding) as f:
        return f.write(konten)


def tambah(path: str, konten: str, encoding: str = "utf-8") -> int:
    """Menambahkan ke akhir file."""
    with open(path, "a", encoding=encoding) as f:
        return f.write(konten)


def baca_baris(path: str, encoding: str = "utf-8") -> List[str]:
    """Membaca file per baris."""
    with open(path, "r", encoding=encoding) as f:
        return f.readlines()


def ada(path: str) -> bool:
    """Cek apakah file/direktori ada."""
    return os.path.exists(path)


def hapus(path: str) -> None:
    """Menghapus file."""
    os.remove(path)


def ukuran(path: str) -> int:
    """Ukuran file dalam bytes."""
    return os.path.getsize(path)


def daftar(path: str = ".") -> List[str]:
    """Mendaftar isi direktori."""
    return os.listdir(path)


def buat_folder(path: str) -> None:
    """Membuat direktori."""
    os.makedirs(path, exist_ok=True)


module = SimpleNamespace(
    baca=baca,
    tulis=tulis,
    tambah=tambah,
    baca_baris=baca_baris,
    ada=ada,
    hapus=hapus,
    ukuran=ukuran,
    daftar=daftar,
    buat_folder=buat_folder,
)
