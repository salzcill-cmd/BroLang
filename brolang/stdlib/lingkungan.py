"""
Modul Lingkungan BroLang (v6.0)
===============================

Akses variabel lingkungan (environment), informasi sistem, dan jalur.

Contoh:
    impor lingkungan

    lingkungan.set("NAMA_APP", "myapp")
    tulis lingkungan.get("NAMA_APP")
    tulis lingkungan.sistem()          # Linux
    tulis lingkungan.prosesor()        # x86_64
"""

import os
import platform
import socket
from types import SimpleNamespace


def get(nama: str, default: str = "") -> str:
    """Baca variabel lingkungan (dengan default)."""
    return os.environ.get(nama, default)


def set(nama: str, nilai: str) -> None:
    """Set variabel lingkungan untuk proses ini."""
    os.environ[nama] = str(nilai)


def hapus(nama: str) -> bool:
    """Hapus variabel lingkungan. Kembalikan True jika ada."""
    return os.environ.pop(nama, None) is not None


# v7.1: alias aman-keyword (`hapus` adalah keyword bahasa) — level modul
# agar berfungsi di interpreter DAN VM.
hapus_var = hapus


def ada(nama: str) -> bool:
    """Cek apakah variabel lingkungan ada."""
    return nama in os.environ


def semua() -> dict:
    """Semua variabel lingkungan sebagai objek."""
    return dict(os.environ)


def sistem() -> str:
    """Nama sistem operasi (Linux, Darwin, Windows)."""
    return platform.system()


def prosesor() -> str:
    """Arsitektur prosesor (x86_64, arm64, ...)."""
    return platform.machine()


def python() -> str:
    """Versi Python yang menjalankan BroLang."""
    return platform.python_version()


def hostname() -> str:
    """Nama host mesin."""
    return socket.gethostname()


def cwd() -> str:
    """Direktori kerja saat ini."""
    return os.getcwd()


def jalur_home() -> str:
    """Jalur folder home user."""
    return os.path.expanduser("~")


module = SimpleNamespace(
    get=get,
    set=set,
    hapus=hapus,
    hapus_var=hapus_var,
    ada=ada,
    semua=semua,
    sistem=sistem,
    prosesor=prosesor,
    python=python,
    hostname=hostname,
    cwd=cwd,
    jalur_home=jalur_home,
)
