"""
Modul File BroLang
==================

Operasi baca/tulis file & direktori.

Contoh:
    impor file
    isi = file.baca("data.txt")
    file.tulis("output.txt", "Halo Dunia")
"""

from types import SimpleNamespace
from typing import Optional, List
import os
import shutil


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
    """Membuat direktori (beserta induknya bila perlu)."""
    os.makedirs(path, exist_ok=True)


# ============= v7.1: manajemen & jalur =============


def salin(dari: str, ke: str) -> None:
    """Menyalin file ke lokasi baru."""
    shutil.copy2(dari, ke)


def pindah(dari: str, ke: str) -> None:
    """Memindahkan file/direktori ke lokasi baru."""
    shutil.move(dari, ke)


def hapus_folder(path: str) -> None:
    """Menghapus direktori (kosongkan dulu bila berisi)."""
    shutil.rmtree(path)


def nama_dasar(jalur: str) -> str:
    """Nama file dari jalur (basename): nama_dasar("/a/b/c.txt") -> "c.txt"."""
    return os.path.basename(jalur)


def folder(jalur: str) -> str:
    """Folder/induk dari jalur (dirname): folder("/a/b/c.txt") -> "/a/b"."""
    return os.path.dirname(jalur)


def ekstensi(nama: str) -> str:
    """Ekstensi file (dengan titik): ekstensi("data.txt") -> ".txt"."""
    return os.path.splitext(nama)[1]


def gabung_jalur(*bagian) -> str:
    """Menggabungkan bagian jalur dengan pemisah OS yang benar."""
    return os.path.join(*bagian)


def absolute(jalur: str) -> str:
    """Jalur absolut dari sebuah jalur."""
    return os.path.abspath(jalur)


def baca_biner(path: str) -> bytes:
    """Baca file sebagai bytes (v7.2)."""
    with open(path, "rb") as f:
        return f.read()


def tulis_biner(path: str, data) -> int:
    """Tulis bytes ke file biner (v7.2)."""
    with open(path, "wb") as f:
        return f.write(bytes(data))


def salin_biner(dari: str, ke: str) -> None:
    """Salin file biner byte-per-byte (v7.2)."""
    import shutil

    shutil.copyfile(dari, ke)


def ubah_nama(dari: str, ke: str) -> None:
    """Ubah nama / pindahkan file (v7.2)."""
    os.rename(dari, ke)


def ubah_waktu(path: str) -> None:
    """Perbarui timestamp akses & modifikasi file (seperti `touch`) (v7.2)."""
    import time as _t

    now = _t.time()
    os.utime(path, (now, now))


# v7.1: alias aman-keyword (`tulis`/`hapus` adalah keyword bahasa) — di
# level modul agar berfungsi di interpreter DAN VM.
tulis_file = tulis
hapus_file = hapus


module = SimpleNamespace(
    baca=baca,
    tulis=tulis,
    tulis_file=tulis,  # v7.1: alias aman-keyword (`tulis` adalah keyword)
    tambah=tambah,
    baca_baris=baca_baris,
    ada=ada,
    hapus=hapus,
    hapus_file=hapus,  # v7.1: alias aman-keyword (`hapus` adalah keyword)
    ukuran=ukuran,
    daftar=daftar,
    buat_folder=buat_folder,
    # v7.1
    salin=salin,
    pindah=pindah,
    hapus_folder=hapus_folder,
    nama_dasar=nama_dasar,
    folder=folder,
    ekstensi=ekstensi,
    gabung_jalur=gabung_jalur,
    absolute=absolute,
    # v7.2
    baca_biner=baca_biner,
    tulis_biner=tulis_biner,
    salin_biner=salin_biner,
    ubah_nama=ubah_nama,
    ubah_waktu=ubah_waktu,
)
