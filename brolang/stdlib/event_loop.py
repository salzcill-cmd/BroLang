"""
event_loop — Event loop & helper async (v7.0)
==============================================

Modul pendamping async/await sejati: `asinkron fungsi` mengembalikan
objek `Tugas` yang berjalan di background thread, dan `tunggu` memblokir
sampai selesai. Modul ini menyediakan utilitas untuk menunggu banyak
tugas dan tidur kooperatif.

Fungsi:
- tidur(detik)          : Tidur kooperatif. Di dalam body async, lock
                          interpreter dilepas sambil tidur agar task lain
                          bisa maju (concurrency nyata untuk operasi IO).
- tunggu_semua(daftar)  : Blokir sampai SEMUA tugas selesai; kembalikan
                          list hasil (urutan sama dengan input).
- tunggu_apa_saja(daftar): Kembalikan hasil tugas pertama yang selesai;
                          tugas lain tetap berjalan di background.
- jalankan(fn, *args)   : Jadwalkan fungsi biasa sebagai Tugas
                          (delegasi ke modul sejajar).

Contoh:
    impor event_loop

    asinkron fungsi muat(url)
        event_loop.tidur(0.1)          # simulasi IO — tidak memblokir task lain
        kembali "data dari " + url
    selesai

    buat a = muat("api/1")
    buat b = muat("api/2")
    tulis event_loop.tunggu_semua([a, b])   # kedua hasil
"""

import time
from types import SimpleNamespace
from typing import Any

from brolang.interpreter.interpreter import _AsyncTugas, _async_tidur


def tidur(detik: float) -> None:
    """Tidur kooperatif (v7.0).

    Di dalam body async, lock interpreter dilepas sambil tidur sehingga
    task asinkron lain bisa berjalan — berguna mensimulasikan IO tanpa
    memblokir seluruh program. Di luar body async, sama seperti
    `waktu.tidur`.
    """
    return _async_tidur(detik)


def _hasil(t):
    """Ambil hasil Tugas; nilai biasa dikembalikan apa adanya."""
    if hasattr(t, "hasil") and callable(t.hasil):
        return t.hasil()
    return t


def tunggu_semua(daftar) -> list:
    """Blokir sampai SEMUA tugas selesai; kembalikan list hasil (urut)."""
    return [_hasil(t) for t in daftar]


def tunggu_apa_saja(daftar) -> Any:
    """Kembalikan hasil tugas pertama yang selesai; sisanya tetap jalan."""
    daftar = list(daftar)
    while daftar:
        for t in daftar:
            if not hasattr(t, "selesai") or t.selesai():
                return _hasil(t)
        time.sleep(0.01)
    return None


def jalankan(fn, *args, **kwargs):
    """Jadwalkan fungsi biasa (termasuk fungsi BroLang) sebagai Tugas.

    Delegasi ke `sejajar.jalankan` — eksekusi fungsi BroLang di-serialisasi
    otomatis (interpreter tidak thread-safe), fungsi Python murni paralel.
    """
    from brolang.stdlib.sejajar import jalankan as _jalankan

    return _jalankan(fn, *args, **kwargs)


module = SimpleNamespace(
    tidur=tidur,
    tunggu_semua=tunggu_semua,
    tunggu_apa_saja=tunggu_apa_saja,
    jalankan=jalankan,
    Tugas=_AsyncTugas,
)
