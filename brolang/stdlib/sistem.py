"""
Modul Sistem BroLang
====================

Informasi sistem & lingkungan (OS, Python, hardware).

Contoh:
    impor sistem

    tulis sistem.versi()        # 6.6.0  (versi BroLang)
    tulis sistem.platform()     # linux / windows / darwin
    tulis sistem.nama()         # Linux
"""

import os
import platform as _platform
import socket
from types import SimpleNamespace

from brolang import __version__


def versi() -> str:
    """Versi BroLang yang sedang berjalan.

    Contoh:
        tulis sistem.versi()    # 6.6.0
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
)
