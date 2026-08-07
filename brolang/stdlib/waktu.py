"""
Modul Waktu BroLang
===================

Fungsi waktu, tanggal, dan alat bantu timing untuk game:
Timer hitung-mundur, Stopwatch, penghitung FPS, dan delta time.

Contoh:
    impor waktu

    # Timer hitung mundur 3 detik
    buat timer = waktu.Timer(3.0)
    timer.update(dt)
    jika timer.selesai() maka
        tulis "Waktu habis!"
    selesai

    # Stopwatch
    buat stopwatch = waktu.Stopwatch()
    stopwatch.mulai()

    # FPS counter
    buat fps = waktu.FpsCounter()
    fps.update(dt)
    tulis "FPS:", fps.fps()
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
    """Tanggal hari ini (YYYY-MM-DD)."""
    return datetime.now().strftime("%Y-%m-%d")


def jam() -> str:
    """Jam saat ini (HH:MM:SS)."""
    return datetime.now().strftime("%H:%M:%S")


def format_waktu(fmt: str) -> str:
    """Format waktu kustom."""
    return datetime.now().strftime(fmt)


def delta() -> float:
    """Delta time frame terakhir (diukur otomatis antar panggilan).

    Contoh:
        buat dt = waktu.delta()
    """
    global _last_time
    now = time.perf_counter()
    dt = now - _last_time
    _last_time = now
    return dt


_last_time = time.perf_counter()


class Timer:
    """Timer hitung mundur.

    Contoh:
        buat timer = waktu.Timer(3.0)
        timer.update(dt)
        jika timer.selesai() maka
            tulis "Waktu habis!"
        selesai
        timer.reset()   # mulai ulang
    """

    def __init__(self, durasi: float = 1.0):
        self.durasi = max(durasi, 0.0)
        self._sisa = self.durasi
        self.on_selesai = None

    def update(self, dt):
        """Kurangi sisa waktu. Kembalikan True tepat saat habis."""
        if self._sisa <= 0:
            return True
        self._sisa -= dt
        if self._sisa <= 0:
            self._sisa = 0
            if callable(self.on_selesai):
                self.on_selesai()
            return True
        return False

    def habis(self) -> bool:
        """Cek apakah timer sudah habis."""
        return self._sisa <= 0

    def selesai(self) -> bool:
        """Alias Python untuk habis() (nama 'selesai' tabrakan keyword BroLang)."""
        return self._sisa <= 0

    def sisa(self) -> float:
        """Sisa waktu dalam detik."""
        return max(self._sisa, 0.0)

    def kemajuan(self) -> float:
        """Kemajuan timer 0.0 (baru mulai) .. 1.0 (habis)."""
        if self.durasi <= 0:
            return 1.0
        return min(max(1.0 - self._sisa / self.durasi, 0.0), 1.0)

    def reset(self, durasi=None):
        """Reset timer. Bisa dengan durasi baru."""
        if durasi is not None:
            self.durasi = max(durasi, 0.0)
        self._sisa = self.durasi


class Stopwatch:
    """Penghitung waktu berlalu (stopwatch).

    Contoh:
        buat sw = waktu.Stopwatch()
        sw.mulai()
        # ... lama kemudian ...
        tulis "Waktu:", sw.elapsed()
    """

    def __init__(self):
        self._mulai = None
        self._total = 0.0

    def mulai(self):
        """Mulai / lanjutkan stopwatch."""
        if self._mulai is None:
            self._mulai = time.perf_counter()

    def stop(self):
        """Stop stopwatch (total tersimpan)."""
        if self._mulai is not None:
            self._total += time.perf_counter() - self._mulai
            self._mulai = None

    def reset(self):
        """Reset stopwatch ke nol."""
        self._mulai = None
        self._total = 0.0

    def elapsed(self) -> float:
        """Total waktu berlalu dalam detik."""
        if self._mulai is not None:
            return self._total + (time.perf_counter() - self._mulai)
        return self._total

    def sedang_jalan(self) -> bool:
        """Cek apakah stopwatch sedang berjalan."""
        return self._mulai is not None


class FpsCounter:
    """Penghitung FPS (frames per second).

    Contoh:
        buat fps = waktu.FpsCounter()
        fps.update(dt)
        tulis "FPS:", fps.fps()
    """

    def __init__(self, sampel: int = 30):
        self.sampel = max(sampel, 1)
        self._frames = []

    def update(self, dt):
        """Catat frame. Panggil setiap frame dengan dt."""
        self._frames.append(dt)
        if len(self._frames) > self.sampel:
            self._frames.pop(0)

    def fps(self) -> float:
        """FPS rata-rata dari frame terakhir."""
        if not self._frames:
            return 0.0
        total = sum(self._frames)
        if total <= 0:
            return 0.0
        return len(self._frames) / total

    def reset(self):
        """Reset counter."""
        self._frames.clear()


def buat_timer(durasi: float = 1.0) -> Timer:
    """Membuat timer hitung mundur."""
    return Timer(durasi)


def buat_stopwatch() -> Stopwatch:
    """Membuat stopwatch baru."""
    return Stopwatch()


def buat_fps() -> FpsCounter:
    """Membuat penghitung FPS baru."""
    return FpsCounter()


module = SimpleNamespace(
    sekarang=sekarang,
    tidur=tidur,
    waktu=waktu,
    tanggal=tanggal,
    jam=jam,
    format_waktu=format_waktu,
    delta=delta,
    Timer=Timer,
    Stopwatch=Stopwatch,
    FpsCounter=FpsCounter,
    buat_timer=buat_timer,
    buat_stopwatch=buat_stopwatch,
    buat_fps=buat_fps,
)
