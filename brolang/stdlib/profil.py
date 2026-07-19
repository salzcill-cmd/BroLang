"""
Modul Profiler untuk BroLang
==============================

Menyediakan profiling untuk mengukur performa.

Contoh:
    impor profil

    profil.mulai()
    # ... kode yang akan diprofil ...
    profil.berhenti()
    profil.laporan()
"""

import time
from types import SimpleNamespace
from collections import defaultdict


class Profiler:
    """Profiler untuk mengukur performa kode."""

    def __init__(self):
        self._sections = {}
        self._results = defaultdict(list)
        this = self

        this.aktif = False
        this.start_time = 0
        this.total_time = 0

    def mulai(self, nama="main"):
        """Memulai profiling section."""
        self.aktif = True
        self._sections[nama] = time.time()
        if nama == "main":
            self.start_time = time.time()

    def berhenti(self, nama="main"):
        """Menghentikan profiling section."""
        if nama in self._sections:
            elapsed = time.time() - self._sections[nama]
            self._results[nama].append(elapsed)
            del self._sections[nama]
            if nama == "main":
                self.total_time = elapsed
            return elapsed
        return 0

    def restart(self):
        """Reset profiler."""
        self._sections.clear()
        self._results.clear()
        self.start_time = 0
        self.total_time = 0

    def laporan(self):
        """Menampilkan laporan profiling."""
        print(f"\n{'='*60}")
        print("[Laporan Profiler]")
        print(f"{'='*60}")
        print(f"{'Section':<30} {'Panggilan':<10} {'Total (ms)':<12} {'Rata-rata (ms)':<15} {'Min (ms)':<10} {'Max (ms)':<10}")
        print(f"{'-'*60}")

        for nama, times in sorted(self._results.items()):
            total = sum(times)
            avg = total / len(times) if times else 0
            min_t = min(times) if times else 0
            max_t = max(times) if times else 0
            print(f"{nama:<30} {len(times):<10} {total*1000:<12.2f} {avg*1000:<15.2f} {min_t*1000:<10.2f} {max_t*1000:<10.2f}")

        print(f"{'-'*60}")
        print(f"Total waktu: {self.total_time*1000:.2f} ms")
        print(f"{'='*60}\n")

    def laporan_detail(self):
        """Menampilkan laporan detail."""
        self.laporan()
        print("Detail per section:")
        for nama, times in sorted(self._results.items()):
            print(f"\n  {nama}:")
            for i, t in enumerate(times):
                print(f"    Panggilan {i+1}: {t*1000:.4f} ms")

    def get_hasil(self):
        """Mendapatkan hasil profiling sebagai dict."""
        results = {}
        for nama, times in self._results.items():
            results[nama] = {
                'panggilan': len(times),
                'total': sum(times),
                'rata_rata': sum(times) / len(times) if times else 0,
                'min': min(times) if times else 0,
                'max': max(times) if times else 0,
                'times': times,
            }
        return results


class Timer:
    """Timer sederhana."""

    def __init__(self, nama="timer"):
        self.nama = nama
        this = self
        this.mulai_waktu = 0
        this.selesai_waktu = 0
        this.berjalan = False

    def mulai(self):
        """Mulai timer."""
        self.mulai_waktu = time.time()
        self.berjalan = True

    def berhenti(self):
        """Hentikan timer."""
        self.selesai_waktu = time.time()
        self.berjalan = False
        return self.durasi()

    def durasi(self):
        """Mendapatkan durasi dalam detik."""
        if self.berjalan:
            return time.time() - self.mulai_waktu
        return self.selesai_waktu - self.mulai_waktu

    def durasi_ms(self):
        """Mendapatkan durasi dalam milidetik."""
        return self.durasi() * 1000

    def reset(self):
        """Reset timer."""
        self.mulai_waktu = 0
        self.selesai_waktu = 0
        self.berjalan = False


class FPSCounter:
    """FPS Counter."""

    def __init__(self):
        this = self
        this.fps = 0
        this.frame_count = 0
        this.last_time = time.time()
        this.rolling_fps = []

    def update(self):
        """Update FPS counter."""
        self.frame_count += 1
        current_time = time.time()
        elapsed = current_time - self.last_time

        if elapsed >= 1.0:
            self.fps = self.frame_count / elapsed
            self.rolling_fps.append(self.fps)
            if len(self.rolling_fps) > 60:
                self.rolling_fps.pop(0)
            self.frame_count = 0
            self.last_time = current_time

    def get_fps(self):
        """Mendapatkan FPS saat ini."""
        return self.fps

    def get_avg_fps(self):
        """Mendapatkan rata-rata FPS."""
        if self.rolling_fps:
            return sum(self.rolling_fps) / len(self.rolling_fps)
        return 0

    def reset(self):
        """Reset counter."""
        self.fps = 0
        self.frame_count = 0
        self.last_time = time.time()
        self.rolling_fps.clear()


# Global instances
_profiler = Profiler()
_fps_counter = FPSCounter()


def mulai(nama="main"):
    """Memulai profiling."""
    _profiler.mulai(nama)


def berhenti(nama="main"):
    """Menghentikan profiling."""
    return _profiler.berhenti(nama)


def laporan():
    """Menampilkan laporan."""
    _profiler.laporan()


def laporan_detail():
    """Menampilkan laporan detail."""
    _profiler.laporan_detail()


def restart():
    """Reset profiler."""
    _profiler.restart()


def buat_timer(nama="timer"):
    """Membuat timer baru."""
    return Timer(nama)


def fps():
    """Mendapatkan FPS counter."""
    return _fps_counter


module = SimpleNamespace(
    Profiler=Profiler,
    Timer=Timer,
    FPSCounter=FPSCounter,
    mulai=mulai,
    berhenti=berhenti,
    laporan=laporan,
    laporan_detail=laporan_detail,
    restart=restart,
    buat_timer=buat_timer,
    fps=fps,
    _profiler=_profiler,
    _fps_counter=_fps_counter,
)
