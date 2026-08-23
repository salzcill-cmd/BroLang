"""
Modul Zaman untuk BroLang
==========================

Timer, stopwatch, dan utilitas waktu.

Contoh:
    impor zaman
    
    # Stopwatch — ukur waktu eksekusi
    buat sw = zaman.Stopwatch()
    sw.mulai()
    # ... kode yang mau diukur ...
    sw.berhenti()
    tulis sw.detik            # 1.234 (detik)
    tulis sw.mili_detik       # 1234.0 (mili detik)
    
    # Timer — countdown
    buat timer = zaman.Timer(5.0)   # 5 detik
    timer.mulai()
    sisa = timer.sisa()
    tulis sisa                      # ~5.0 (menurun)
    
    # Waktu berlalu
    buat t0 = zaman.sekarang()
    # ... kode ...
    tulis zaman.berlalu(t0)         # 0.050 (detik sejak t0)
    
    # Waktu dalam format teks
    tulis zaman.uman(detik=3725)    # "1j 2m 5d"
    tulis zaman.detik_milidetik(1.234)  # "1d 234md"
"""

import time
import threading


class Stopwatch:
    """Stopwatch untuk mengukur waktu eksekusi.
    
    Contoh:
        buat sw = zaman.Stopwatch()
        sw.mulai()
        # ... kode ...
        sw.berhenti()
        tulis sw.detik
    """
    
    def __init__(self):
        self._start = 0
        self._stop = 0
        self._running = False
        self._laps = []
    
    def mulai(self):
        """Mulai stopwatch."""
        self._start = time.perf_counter()
        self._running = True
        self._stop = self._start
        return self
    
    def berhenti(self):
        """Berhenti stopwatch."""
        if self._running:
            self._stop = time.perf_counter()
            self._running = False
        return self
    
    def lap(self):
        """Catat lap time (waktu sejak mulai/lap terakhir)."""
        now = time.perf_counter()
        if self._laps:
            lap_time = now - self._laps[-1][1]
        else:
            lap_time = now - self._start
        self._laps.append((lap_time, now))
        return lap_time
    
    def reset(self):
        """Reset stopwatch."""
        self._start = 0
        self._stop = 0
        self._running = False
        self._laps = []
        return self
    
    @property
    def detik(self):
        """Waktu dalam detik."""
        if self._running:
            return time.perf_counter() - self._start
        return self._stop - self._start
    
    @property
    def mili_detik(self):
        """Waktu dalam mili detik."""
        return self.detik * 1000
    
    @property
    def micro_detik(self):
        """Waktu dalam micro detik."""
        return self.detik * 1_000_000
    
    @property
    def berjalan(self):
        """Apakah stopwatch sedang berjalan?"""
        return self._running
    
    @property
    def lap_times(self):
        """Daftar waktu lap."""
        return [lap[0] for lap in self._laps]
    
    def __enter__(self):
        self.mulai()
        return self
    
    def __exit__(self, *args):
        self.berhenti()
    
    def __repr__(self):
        return f"Stopwatch({self.detik:.4f}s)"
    
    # For BroLang property access
    def get(self, name):
        if name == "detik":
            return self.detik
        if name == "mili_detik":
            return self.mili_detik
        if name == "berjalan":
            return self.berjalan
        return None


class Timer:
    """Countdown timer — hitung mundur dari detik tertentu.
    
    Contoh:
        buat timer = zaman.Timer(5.0)
        timer.mulai()
        tulis timer.sisa()   # ~5.0 (menurun)
        tulis timer.habis    # False
    """
    
    def __init__(self, durasi):
        self._durasi = durasi
        self._start = 0
        self._running = False
    
    def mulai(self):
        """Mulai timer countdown."""
        self._start = time.perf_counter()
        self._running = True
        return self
    
    def berhenti(self):
        """Berhenti timer."""
        self._running = False
        return self
    
    def reset(self):
        """Reset timer ke durasi awal."""
        self._running = False
        self._start = 0
        return self
    
    def sisa(self):
        """Sisa waktu countdown (detik)."""
        if not self._running:
            return self._durasi
        elapsed = time.perf_counter() - self._start
        remaining = self._durasi - elapsed
        return max(0.0, remaining)
    
    def berlalu(self):
        """Waktu yang sudah berlalu (detik)."""
        if not self._running:
            return 0.0
        return time.perf_counter() - self._start
    
    @property
    def habis(self):
        """Apakah timer sudah habis?"""
        return self.sisa() <= 0
    
    @property
    def persentase(self):
        """Persentase waktu yang sudah berlalu (0-100)."""
        sisa = self.sisa()
        return (1 - sisa / self._durasi) * 100 if self._durasi > 0 else 100
    
    def __enter__(self):
        self.mulai()
        return self
    
    def __exit__(self, *args):
        self.berhenti()
    
    def __repr__(self):
        return f"Timer({self._durasi}s, sisa={self.sisa():.2f}s)"
    
    def get(self, name):
        if name == "sisa":
            return self.sisa()
        if name == "habis":
            return self.habis
        if name == "persentase":
            return self.persentase
        return None


def sekarang():
    """Mengembalikan waktu saat ini (detik sejak epoch, presisi tinggi)."""
    return time.perf_counter()


def sekarang_unix():
    """Mengembalikan waktu Unix saat ini (detik sejak 1 Jan 1970)."""
    return time.time()


def berlalu(waktu_mulai):
    """Menghitung waktu yang berlalu sejak waktu_mulai (detik)."""
    return time.perf_counter() - waktu_mulai


def tidur(detik):
    """Tidur selama detik tertentu."""
    time.sleep(detik)


def uman(detik):
    """Konversi detik ke format yang mudah dibaca manusia.
    
    Contoh:
        zaman.uman(3725)    # "1j 2m 5d"
        zaman.uman(65)       # "1m 5d"
        zaman.uman(0.5)      # "500md"
    """
    detik = float(detik)
    
    if detik < 0.001:
        return f"{detik * 1_000_000:.0f}μd"
    if detik < 1:
        return f"{detik * 1000:.0f}md"
    
    jam = int(detik // 3600)
    menit = int((detik % 3600) // 60)
    detik_sisa = detik % 60
    
    parts = []
    if jam > 0:
        parts.append(f"{jam}j")
    if menit > 0:
        parts.append(f"{menit}m")
    if detik_sisa > 0.001 or not parts:
        if detik_sisa == int(detik_sisa):
            parts.append(f"{int(detik_sisa)}d")
        else:
            parts.append(f"{detik_sisa:.2f}d")
    
    return " ".join(parts)


def detik_milidetik(detik):
    """Konversi detik ke format 'Xd Ymd'.
    
    Contoh:
        zaman.detik_milidetik(1.234)  # "1d 234md"
    """
    d = int(detik)
    md = int((detik - d) * 1000)
    return f"{d}d {md}md"
