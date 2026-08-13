"""
Modul Sistem BroLang
====================

Informasi sistem & lingkungan (OS, Python, hardware).

Contoh:
    impor sistem

    tulis sistem.versi()        # 7.1.0  (versi BroLang)
    tulis sistem.platform()     # linux / windows / darwin
    tulis sistem.nama()         # Linux
"""

import os
import platform as _platform
import socket
from types import SimpleNamespace
from typing import Optional

from brolang import __version__


def versi() -> str:
    """Versi BroLang yang sedang berjalan.

    Contoh:
        tulis sistem.versi()    # 7.1.0
    """
    return __version__


def platform() -> str:
    """Nama sistem operasi huruf kecil: linux / windows / darwin.

    Contoh:
        tulis sistem.platform()   # linux
    """
    return _platform.system().lower()


def nama() -> str:
    """Nama sistem operasi (Linux / Windows / Darwin)."""
    return _platform.system()


def versi_os() -> str:
    """Versi detail sistem operasi (mis. "Linux-6.x")."""
    return _platform.version()


def prosesor() -> str:
    """Arsitektur prosesor (x86_64, arm64, ...)."""
    return _platform.machine()


def python() -> str:
    """Versi Python yang menjalankan BroLang."""
    return _platform.python_version()


def hostname() -> str:
    """Nama host mesin."""
    return socket.gethostname()


def cwd() -> str:
    """Direktori kerja saat ini."""
    return os.getcwd()


def home() -> str:
    """Jalur folder home user."""
    return os.path.expanduser("~")


def lingkungan() -> str:
    """Nama lingkungan (mis. 'production' bila var BROLANG_ENV di-set)."""
    return os.environ.get("BROLANG_ENV", "development")


# ============= v7.1: hardware =============


def jumlah_cpu() -> int:
    """Jumlah CPU/logical cores."""
    return os.cpu_count() or 1


def memori() -> dict:
    """Info memori (bytes): {total, tersedia}. None bila tidak tersedia."""
    info = {"total": None, "tersedia": None}
    try:
        if hasattr(os, "sysconf"):
            page = os.sysconf("SC_PAGE_SIZE")
            info["total"] = page * os.sysconf("SC_PHYS_PAGES")
            info["tersedia"] = page * os.sysconf("SC_AVPHYS_PAGES")
    except (ValueError, OSError, KeyError):
        pass
    return info


def memori_total() -> Optional[int]:
    """Total memori fisik (bytes)."""
    return memori()["total"]


def memori_bebas() -> Optional[int]:
    """Memori fisik tersedia (bytes)."""
    return memori()["tersedia"]


def arsitektur() -> str:
    """Arsitektur + bitness prosesor (mis. "64bit")."""
    return _platform.machine() + " " + _platform.architecture()[0]


module = SimpleNamespace(
    versi=versi,
    platform=platform,
    nama=nama,
    versi_os=versi_os,
    prosesor=prosesor,
    python=python,
    hostname=hostname,
    cwd=cwd,
    home=home,
    lingkungan=lingkungan,
    # v7.1
    jumlah_cpu=jumlah_cpu,
    memori=memori,
    memori_total=memori_total,
    memori_bebas=memori_bebas,
    arsitektur=arsitektur,
)
