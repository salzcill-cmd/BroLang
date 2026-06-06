"""
Modul Waktu BroLang
===================

Fungsi waktu dan tanggal.

Contoh:
    impor waktu
    waktu.tidur(1)
"""

import time
from datetime import datetime
from types import SimpleNamespace


def sekarang() -> str:
    """Waktu saat ini dalam format ISO."""
    return datetime.now().isoformat()


def tidur(detik: float) -> None:
    """Tidur/jeda dalam detik."""
    time.sleep(detik)


def waktu() -> float:
    """Timestamp UNIX saat ini."""
    return time.time()


def tanggal() -> str:
    """Tanggal hari ini."""
    return datetime.now().strftime("%Y-%m-%d")


def jam() -> str:
    """Jam saat ini."""
    return datetime.now().strftime("%H:%M:%S")


def format_waktu(fmt: str) -> str:
    """Format waktu kustom."""
    return datetime.now().strftime(fmt)


module = SimpleNamespace(
    sekarang=sekarang,
    tidur=tidur,
    waktu=waktu,
    tanggal=tanggal,
    jam=jam,
    format_waktu=format_waktu,
)
