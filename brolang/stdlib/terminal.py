"""
Modul Terminal BroLang
======================

Pengalaman terminal (UX) untuk program CLI: warna ANSI, gaya teks,
progress bar, prompt interaktif, dan pesan status — murni stdlib Python.

Fitur:
- Warna teks: merah, hijau, kuning, biru, magenta, cyan, putih, abu
- Gaya teks: tebal, miring, garis_bawah, terbalik
- Pesan status: sukses, peringatan, gagal, info
- Progress bar: bilah_progress & cetak_progress
- Prompt interaktif: tanya & tanya_ya

Contoh:
    impor terminal

    tulis terminal.hijau("Sukses!")          # teks hijau
    tulis terminal.tebal("Judul")
    terminal.sukses("Deploy berhasil")

    untuk i dari 0 sampai 100 langkah 10
        terminal.cetak_progress(i, 100)
    selesai

    buat nama = terminal.tanya("Nama kamu? ")
"""

import os as _os
import sys as _sys
from types import SimpleNamespace

# Kode ANSI
_RESET = "\033[0m"
_KODE = {
    "merah": "\033[31m",
    "hijau": "\033[32m",
    "kuning": "\033[33m",
    "biru": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "putih": "\033[37m",
    "abu": "\033[90m",
}


def warna(teks: str, nama_warna: str) -> str:
    """Mewarnai teks dengan warna bernama (merah, hijau, kuning, ...).

    Contoh:
        tulis terminal.warna("Penting", "kuning")
    """
    kode = _KODE.get(str(nama_warna), _KODE["putih"])
    return f"{kode}{teks}{_RESET}"


def merah(teks: str) -> str:
    """Teks berwarna merah (error/peringatan keras)."""
    return f"{_KODE['merah']}{teks}{_RESET}"


def hijau(teks: str) -> str:
    """Teks berwarna hijau (sukses)."""
    return f"{_KODE['hijau']}{teks}{_RESET}"


def kuning(teks: str) -> str:
    """Teks berwarna kuning (peringatan)."""
    return f"{_KODE['kuning']}{teks}{_RESET}"


def biru(teks: str) -> str:
    """Teks berwarna biru (info)."""
    return f"{_KODE['biru']}{teks}{_RESET}"


def magenta(teks: str) -> str:
    """Teks berwarna magenta."""
    return f"{_KODE['magenta']}{teks}{_RESET}"


def cyan(teks: str) -> str:
    """Teks berwarna cyan."""
    return f"{_KODE['cyan']}{teks}{_RESET}"


def putih(teks: str) -> str:
    """Teks berwarna putih."""
    return f"{_KODE['putih']}{teks}{_RESET}"


def abu(teks: str) -> str:
    """Teks berwarna abu-abu (keterangan)."""
    return f"{_KODE['abu']}{teks}{_RESET}"


def tebal(teks: str) -> str:
    """Teks tebal (bold)."""
    return f"\033[1m{teks}{_RESET}"


def miring(teks: str) -> str:
    """Teks miring (italic)."""
    return f"\033[3m{teks}{_RESET}"


def garis_bawah(teks: str) -> str:
    """Teks bergaris bawah (underline)."""
    return f"\033[4m{teks}{_RESET}"


def terbalik(teks: str) -> str:
    """Teks dengan warna latar terbalik (reverse video)."""
    return f"\033[7m{teks}{_RESET}"


def bersihkan() -> str:
    """Escape sequence untuk membersihkan layar terminal.

    Gunakan dengan `tulis terminal.bersihkan()`.

    Contoh:
        tulis terminal.bersihkan()   # layar bersih
    """
    if _os.name == "nt":
        return "\033[2J\033[H"
    return "\033[2J\033[H"


def bilah_progress(sekarang: int, total: int, lebar: int = 30) -> str:
    """Bilah progress teks, mis. "[██████████░░░░░] 67%".

    Args:
        sekarang: Posisi saat ini (0..total)
        total: Nilai total
        lebar: Panjang bilah dalam karakter

    Contoh:
        tulis terminal.bilah_progress(7, 10)   # [█████████████░░] 70%
    """
    total = max(1, int(total))
    sekarang = max(0, min(int(sekarang), total))
    lebar = max(1, int(lebar))
    persen = int((sekarang / total) * 100)
    terisi = int(round((sekarang / total) * lebar))
    kosong = lebar - terisi
    bilah = "█" * terisi + "░" * kosong
    return f"[{bilah}] {persen}%"


def cetak_progress(sekarang: int, total: int, lebar: int = 30) -> str:
    """Cetak bilah progress di baris yang sama (dengan carriage return).

    Cocok untuk loop panjang: panggil di tiap iterasi dan bilah
    akan ter-update di tempat.

    Contoh:
        untuk i dari 1 sampai 100
            terminal.cetak_progress(i, 100)
        selesai
    """
    baris = bilah_progress(sekarang, total, lebar)
    _sys.stdout.write("\r" + baris)
    _sys.stdout.flush()
    if int(sekarang) >= int(total):
        _sys.stdout.write("\n")
        _sys.stdout.flush()
    return ""


def tanya(pesan: str, default: str = "") -> str:
    """Prompt input interaktif (seperti input() Python).

    Args:
        pesan: Teks yang ditampilkan
        default: Nilai default bila user hanya menekan Enter

    Contoh:
        buat nama = terminal.tanya("Nama kamu? ", "anonim")
    """
    try:
        jawaban = input(str(pesan))
    except EOFError:
        return str(default)
    if jawaban.strip() == "" and default != "":
        return str(default)
    return jawaban


def tanya_ya(pesan: str) -> bool:
    """Prompt ya/tidak (y/t) — mengembalikan True bila "ya".

    Contoh:
        jika terminal.tanya_ya("Lanjutkan? ") maka
            tulis "Oke lanjut!"
        selesai
    """
    while True:
        try:
            jawaban = input(f"{pesan} (y/t): ").strip().lower()
        except EOFError:
            return False
        if jawaban in ("y", "ya", "yes", "benar", "betul", "true"):
            return True
        if jawaban in ("t", "tidak", "no", "n", "salah", "false"):
            return False


# --- Pesan status ---


def sukses(pesan: str) -> str:
    """Cetak pesan sukses hijau dengan ikon ✓."""
    teks_pesan = f"{_KODE['hijau']}✓ {pesan}{_RESET}"
    print(teks_pesan)
    return ""


def info(pesan: str) -> str:
    """Cetak pesan info biru dengan ikon ℹ."""
    teks_pesan = f"{_KODE['biru']}ℹ {pesan}{_RESET}"
    print(teks_pesan)
    return ""


def peringatan(pesan: str) -> str:
    """Cetak pesan peringatan kuning dengan ikon ⚠."""
    teks_pesan = f"{_KODE['kuning']}⚠ {pesan}{_RESET}"
    print(teks_pesan)
    return ""


def gagal(pesan: str) -> str:
    """Cetak pesan error merah dengan ikon ✗."""
    teks_pesan = f"{_KODE['merah']}✗ {pesan}{_RESET}"
    print(teks_pesan)
    return ""


def banner(teks: str, lebar: int = 50) -> str:
    """Banner dekoratif untuk header program.

    Contoh:
        tulis terminal.banner("Aplikasi Saya")
    """
    lebar = max(20, int(lebar))
    if len(str(teks)) > lebar - 4:
        teks = str(teks)[: lebar - 7] + "..."
    garis = "═" * lebar
    return f"{garis}\n  {tebal(str(teks))}\n{garis}"


module = SimpleNamespace(
    warna=warna,
    merah=merah,
    hijau=hijau,
    kuning=kuning,
    biru=biru,
    magenta=magenta,
    cyan=cyan,
    putih=putih,
    abu=abu,
    tebal=tebal,
    miring=miring,
    garis_bawah=garis_bawah,
    terbalik=terbalik,
    bersihkan=bersihkan,
    bilah_progress=bilah_progress,
    cetak_progress=cetak_progress,
    tanya=tanya,
    tanya_ya=tanya_ya,
    sukses=sukses,
    info=info,
    peringatan=peringatan,
    gagal=gagal,
    banner=banner,
)
