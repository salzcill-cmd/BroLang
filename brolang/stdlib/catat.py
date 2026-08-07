"""
Modul Catat BroLang (v6.0)
==========================

Logging profesional dengan level, format waktu, dan output ke file.

Contoh:
    impor catat

    catat.info("Aplikasi dimulai")
    catat.peringatan("Memori menipis")
    catat.error("Koneksi gagal")
    catat.atur_file("app.log")       # log juga ke file
    catat.atur_level("debug")
"""

import os
import sys
import datetime
from types import SimpleNamespace

_LEVELS = {"debug": 10, "info": 20, "peringatan": 30, "error": 40, "kritis": 50}
_NAMA_LEVEL = {10: "DEBUG", 20: "INFO", 30: "PERINGATAN", 40: "ERROR", 50: "KRITIS"}

_tingkat_min = 20  # default INFO
_file_tujuan = None


def atur_level(level: str) -> None:
    """Atur level minimum yang ditampilkan: debug/info/peringatan/error/kritis."""
    global _tingkat_min
    if level.lower() not in _LEVELS:
        raise ValueError(f"Level '{level}' tidak dikenal. Gunakan: {', '.join(_LEVELS)}")
    _tingkat_min = _LEVELS[level.lower()]


def atur_file(path: str) -> None:
    """Arahkan log juga ke file (None untuk matikan)."""
    global _file_tujuan
    _file_tujuan = path


def _tulis(level: str, pesan: str) -> None:
    kode = _LEVELS[level]
    if kode < _tingkat_min:
        return
    waktu = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    baris = f"[{waktu}] [{_NAMA_LEVEL[kode]}] {pesan}"
    print(baris)
    if _file_tujuan:
        try:
            with open(_file_tujuan, "a", encoding="utf-8") as f:
                f.write(baris + "\n")
        except OSError as e:
            print(f"[catat] Gagal menulis ke {_file_tujuan}: {e}")


def debug(pesan: str) -> None:
    _tulis("debug", pesan)


def info(pesan: str) -> None:
    _tulis("info", pesan)


def peringatan(pesan: str) -> None:
    _tulis("peringatan", pesan)


def error(pesan: str) -> None:
    _tulis("error", pesan)


def kritis(pesan: str) -> None:
    _tulis("kritis", pesan)


def bersihkan() -> None:
    """Hapus file log saat ini (jika ada)."""
    if _file_tujuan and os.path.exists(_file_tujuan):
        os.remove(_file_tujuan)


module = SimpleNamespace(
    atur_level=atur_level,
    atur_file=atur_file,
    debug=debug,
    info=info,
    peringatan=peringatan,
    error=error,
    kritis=kritis,
    bersihkan=bersihkan,
)
