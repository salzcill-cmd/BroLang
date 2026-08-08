"""
Modul Sistem Operasi BroLang
============================

Operasi sistem operasi: daftar file, buat/hapus/pindah file & folder,
manipulasi jalur, dan info lingkungan.

Contoh:
    impor sistem_operasi

    buat daftar = sistem_operasi.list_dir(".")
    untuk file dalam daftar lakukan
        tulis file
    selesai

    sistem_operasi.buat_folder("assets")
    sistem_operasi.pindah("a.txt", "assets/a.txt")
"""

import os
import shutil
from types import SimpleNamespace


def list_dir(path: str = ".") -> list:
    """Daftar nama semua file & folder di direktori (urut abjad).

    Contoh:
        buat daftar = sistem_operasi.list_dir(".")
    """
    try:
        return sorted(os.listdir(path))
    except FileNotFoundError:
        return []


def daftar_file(path: str = ".") -> list:
    """Daftar nama file saja (bukan folder) di direktori."""
    return sorted(f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)))


def daftar_folder(path: str = ".") -> list:
    """Daftar nama folder saja di direktori."""
    return sorted(f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f)))


def ada(path: str) -> bool:
    """Cek apakah file/folder ada."""
    return os.path.exists(path)


def adalah_file(path: str) -> bool:
    """Cek apakah path adalah file."""
    return os.path.isfile(path)


def adalah_folder(path: str) -> bool:
    """Cek apakah path adalah folder."""
    return os.path.isdir(path)


def buat_folder(path: str) -> bool:
    """Buat folder (beserta folder induk bila perlu). Tidak error jika sudah ada."""
    os.makedirs(path, exist_ok=True)
    return True


def hapus_file(path: str) -> bool:
    """Hapus file. Kembalikan True jika berhasil, False jika tidak ada."""
    try:
        os.remove(path)
        return True
    except FileNotFoundError:
        return False


def hapus_folder(path: str) -> bool:
    """Hapus folder beserta isinya. Kembalikan True jika berhasil."""
    try:
        shutil.rmtree(path)
        return True
    except FileNotFoundError:
        return False


def pindah(sumber: str, tujuan: str) -> str:
    """Pindahkan/rename file atau folder."""
    return shutil.move(sumber, tujuan)


def salin(sumber: str, tujuan: str) -> str:
    """Salin file ke tujuan."""
    return shutil.copy2(sumber, tujuan)


def ukuran(path: str) -> int:
    """Ukuran file dalam byte (0 bila tidak ada)."""
    try:
        return os.path.getsize(path)
    except FileNotFoundError:
        return 0


def cwd() -> str:
    """Direktori kerja saat ini."""
    return os.getcwd()


def ganti_cwd(path: str) -> None:
    """Ganti direktori kerja."""
    os.chdir(path)


def nama_dasar(path: str) -> str:
    """Nama file/folder terakhir dari sebuah jalur (basename)."""
    return os.path.basename(path)


def folder_induk(path: str) -> str:
    """Folder yang memuat path tersebut (dirname)."""
    return os.path.dirname(path)


def ekstensi(path: str) -> str:
    """Ekstensi file (termasuk titik, mis. ".txt"). Kosong bila tidak ada."""
    return os.path.splitext(path)[1]


def nama_tanpa_ekstensi(path: str) -> str:
    """Nama file tanpa ekstensi."""
    return os.path.splitext(os.path.basename(path))[0]


def gabung_jalur(*bagian) -> str:
    """Gabungkan beberapa bagian jalur menjadi satu (sesuai OS)."""
    return os.path.join(*[str(b) for b in bagian])


def jalur_absolut(path: str) -> str:
    """Jalur absolut (lengkap) dari sebuah path."""
    return os.path.abspath(path)


def jalur_nyata(path: str) -> str:
    """Jalur kanonik (resolve symlink)."""
    return os.path.realpath(path)


def ubah_ekstensi(path: str, ekstensi_baru: str) -> str:
    """Ganti ekstensi file (tulis dengan titik, mis. \".md\")."""
    if not ekstensi_baru.startswith("."):
        ekstensi_baru = "." + ekstensi_baru
    return os.path.splitext(path)[0] + ekstensi_baru


module = SimpleNamespace(
    list_dir=list_dir,
    daftar_file=daftar_file,
    daftar_folder=daftar_folder,
    ada=ada,
    adalah_file=adalah_file,
    adalah_folder=adalah_folder,
    buat_folder=buat_folder,
    hapus_file=hapus_file,
    hapus_folder=hapus_folder,
    pindah=pindah,
    salin=salin,
    ukuran=ukuran,
    cwd=cwd,
    ganti_cwd=ganti_cwd,
    nama_dasar=nama_dasar,
    folder_induk=folder_induk,
    ekstensi=ekstensi,
    nama_tanpa_ekstensi=nama_tanpa_ekstensi,
    gabung_jalur=gabung_jalur,
    jalur_absolut=jalur_absolut,
    jalur_nyata=jalur_nyata,
    ubah_ekstensi=ubah_ekstensi,
)
