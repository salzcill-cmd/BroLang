"""
Modul Sejajar (Parallel / Threading) untuk BroLang
===================================================

Menjalankan fungsi secara paralel di background thread — berguna untuk
operasi yang lambat (I/O, jaringan, menunggu) supaya game loop / program
utama tetap responsif.

Contoh:
    impor sejajar

    fungsi hitung(x)
        kembali x * 2
    selesai

    buat t = sejajar.jalankan(hitung, 21)
    tulis t.selesai()      # False/True
    tulis t.hasil()        # 42 (blokir sampai selesai)

    # Jalankan banyak sekaligus
    buat hasil = sejajar.peta_sejajar(hitung, [1, 2, 3, 4])   # [2, 4, 6, 8]

Catatan penting:
- Fungsi BroLang berbagi interpreter yang tidak thread-safe, jadi saat
  dijalankan lewat modul ini mereka di-serialisasi otomatis (aman).
- Callable Python murni (mis. dari modul stdlib lain) jalan benar-benar
  paralel.
- Gunakan `sejajar.atur_thread(n)` untuk mengatur jumlah thread (default 4).
- **Hindari deadlock**: fungsi BroLang yang dipanggil dari thread TIDAK
  boleh memanggil `sejajar.jalankan(fungsi_brolang_lain)` lalu langsung
  `.hasil()` di dalam dirinya — thread yang memegang lock akan menunggu
  tugas yang membutuhkan lock yang sama.
"""

from types import SimpleNamespace
from concurrent.futures import ThreadPoolExecutor
import threading

_executor = None
_default_threads = 4
# Interpreter BroLang tidak thread-safe -> serialisasi eksekusi fungsi BroLang.
_LOCK = threading.RLock()


def _get_executor() -> ThreadPoolExecutor:
    global _executor
    if _executor is None:
        _executor = ThreadPoolExecutor(
            max_workers=_default_threads, thread_name_prefix="brolang-sejajar")
    return _executor


def _run_safe(fn, args, kwargs):
    """Jalankan fungsi — serialisasi fungsi BroLang, paralelkan callable murni."""
    if getattr(fn, "_brolang_fn", False):
        with _LOCK:
            return fn(*args, **kwargs)
    return fn(*args, **kwargs)


class Tugas:
    """Task asinkron yang berjalan di background thread."""

    def __init__(self, future):
        self._future = future

    def selesai(self) -> bool:
        """Cek apakah task sudah selesai (tanpa memblokir)."""
        return self._future.done()

    def hasil(self, timeout=None):
        """Ambil hasil task — blokir sampai selesai (atau timeout detik)."""
        return self._future.result(timeout)

    def tunggu(self, timeout=None):
        """Alias hasil(): blokir sampai selesai."""
        return self._future.result(timeout)

    def batal(self) -> bool:
        """Coba batalkan task (hanya berhasil kalau belum mulai jalan)."""
        return self._future.cancel()


def jalankan(fn, *args, **kwargs) -> Tugas:
    """Jalankan fungsi di background thread. Kembalikan objek Tugas.

    Contoh:
        buat tugas = sejajar.jalankan(fungsi_saya, 10, 20)
        # ... kerja lain ...
        tulis tugas.hasil()
    """
    return Tugas(_get_executor().submit(_run_safe, fn, args, kwargs))


def tunggu(tugas, timeout=None):
    """Blokir sampai satu tugas selesai, kembalikan hasilnya."""
    return tugas._future.result(timeout)


def tunggu_semua(tugas_list) -> list:
    """Tunggu semua tugas selesai. Kembalikan list hasil (urutan input)."""
    return [t._future.result() for t in tugas_list]


def peta_sejajar(fn, iterable) -> list:
    """Map fungsi ke semua elemen iterable secara paralel.

    Nama `peta_sejajar` (bukan `peta`) karena `peta` adalah keyword bahasa
    untuk map/filter. Contoh:
        buat hasil = sejajar.peta_sejajar(kali2, [1, 2, 3, 4])   # [2, 4, 6, 8]
    """
    futures = [_get_executor().submit(_run_safe, fn, (item,), {})
               for item in iterable]
    return [f.result() for f in futures]


def atur_thread(jumlah: int):
    """Atur jumlah thread pool (berlaku untuk pool berikutnya)."""
    global _default_threads
    _default_threads = max(1, int(jumlah))


def jumlah_thread() -> int:
    """Jumlah thread yang dikonfigurasi."""
    return _default_threads


def tutup():
    """Tutup thread pool (program selesai)."""
    global _executor
    if _executor is not None:
        _executor.shutdown(wait=True)
        _executor = None


module = SimpleNamespace(
    jalankan=jalankan,
    tunggu=tunggu,
    tunggu_semua=tunggu_semua,
    peta_sejajar=peta_sejajar,
    atur_thread=atur_thread,
    jumlah_thread=jumlah_thread,
    tutup=tutup,
    Tugas=Tugas,
)
