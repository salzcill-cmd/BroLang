"""
Modul Proses BroLang (v6.0)
===========================

Menjalankan perintah sistem (subprocess) dengan output & exit code.

Contoh:
    impor proses

    buat hasil = proses.jalankan("echo halo")
    tulis hasil.keluaran          # "halo"
    tulis hasil.kode              # 0
    tulis proses.kode_keluar("ls /tidak/ada")   # 2
"""

import os
import subprocess
from types import SimpleNamespace
from typing import List


def jalankan(perintah: str, timeout: float = 30.0) -> SimpleNamespace:
    """Jalankan perintah shell. Kembalikan {keluaran, error, kode}.

    Contoh:
        buat hasil = proses.jalankan("dir" if proses.sistem()=="Windows" else "ls")
        tulis hasil.keluaran
    """
    try:
        res = subprocess.run(
            perintah, shell=True, capture_output=True, text=True,
            timeout=timeout,
        )
        return SimpleNamespace(
            keluaran=res.stdout.strip(),
            error=res.stderr.strip(),
            kode=res.returncode,
            sukses=res.returncode == 0,
        )
    except subprocess.TimeoutExpired:
        return SimpleNamespace(keluaran="", error="Timeout", kode=-1, sukses=False)


def kode_keluar(perintah: str, timeout: float = 30.0) -> int:
    """Jalankan perintah dan kembalikan exit code-nya saja."""
    try:
        res = subprocess.run(perintah, shell=True, capture_output=True,
                             text=True, timeout=timeout)
        return res.returncode
    except subprocess.TimeoutExpired:
        return -1


def keluaran(perintah: str, timeout: float = 30.0) -> str:
    """Jalankan perintah dan kembalikan stdout-nya (strip)."""
    return jalankan(perintah, timeout).keluaran


def error(perintah: str, timeout: float = 30.0) -> str:
    """Jalankan perintah dan kembalikan stderr-nya (strip)."""
    return jalankan(perintah, timeout).error


def jalankan_di(perintah: str, direktori: str, timeout: float = 30.0) -> SimpleNamespace:
    """Jalankan perintah di direktori tertentu."""
    try:
        res = subprocess.run(
            perintah, shell=True, capture_output=True, text=True,
            cwd=direktori, timeout=timeout,
        )
        return SimpleNamespace(
            keluaran=res.stdout.strip(),
            error=res.stderr.strip(),
            kode=res.returncode,
            sukses=res.returncode == 0,
        )
    except subprocess.TimeoutExpired:
        return SimpleNamespace(keluaran="", error="Timeout", kode=-1, sukses=False)
    except FileNotFoundError:
        return SimpleNamespace(keluaran="", error=f"Direktori tidak ada: {direktori}",
                               kode=-1, sukses=False)


# ============= v7.1 =============


def proses_id() -> int:
    """PID (process ID) dari proses BroLang saat ini."""
    return os.getpid()


def jalankan_list(perintah: List[str], timeout: float = 30.0) -> SimpleNamespace:
    """Jalankan perintah tanpa shell (list argumen) — lebih aman.

    Contoh:
        buat hasil = proses.jalankan_list(["echo", "halo"])
    """
    try:
        res = subprocess.run(
            perintah, capture_output=True, text=True, timeout=timeout,
        )
        return SimpleNamespace(
            keluaran=res.stdout.strip(),
            error=res.stderr.strip(),
            kode=res.returncode,
            sukses=res.returncode == 0,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        return SimpleNamespace(keluaran="", error=str(e), kode=-1, sukses=False)


module = SimpleNamespace(
    jalankan=jalankan,
    kode_keluar=kode_keluar,
    keluaran=keluaran,
    error=error,
    jalankan_di=jalankan_di,
    # v7.1
    proses_id=proses_id,
    jalankan_list=jalankan_list,
)
