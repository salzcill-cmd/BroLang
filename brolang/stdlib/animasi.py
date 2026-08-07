"""
Modul Animasi untuk BroLang Game Development
=============================================

Sistem animasi untuk game: animasi frame sprite, tween (perubahan nilai
gradual), dan sequence animasi.

Contoh:
    impor animasi

    buat anim = animasi.Animasi()
    anim.tambah("jalan", [0, 1, 2, 3], fps=10)
    anim.mainkan("jalan")

    # Tween dengan easing
    buat tween = animasi.buat_tween(0, 100, durasi=1.0, easing="ease_out_back")
    tween.on_selesai = fungsi_saya
"""

import math
from types import SimpleNamespace


class Animasi:
    """Sistem animasi sprite (frame-based)."""

    def __init__(self):
        self._animasi = {}
        self._saat_ini = None
        self._frame = 0
        self._waktu = 0
        self._selesai = False
        self.on_selesai = None  # callback saat animasi non-loop selesai

    def tambah(self, nama, frames, fps=10, loop=True):
        """Menambahkan animasi baru.

        Args:
            nama: Nama animasi.
            frames: Daftar frame (id gambar / nilai).
            fps: Frame per detik.
            loop: True = berputar terus, False = berhenti di frame terakhir.
        """
        self._animasi[nama] = {
            'frames': list(frames),
            'fps': fps,
            'loop': loop,
            'frame_sekarang': 0,
        }

    def mainkan(self, nama, loop=None, mulai_dari=0):
        """Memainkan animasi.

        Args:
            nama: Nama animasi yang dimainkan.
            loop: Override setting loop (opsional).
            mulai_dari: Index frame awal (default 0).
        """
        if nama in self._animasi:
            self._saat_ini = nama
            self._frame = max(0, min(int(mulai_dari), len(self._animasi[nama]['frames']) - 1))
            self._waktu = 0
            self._selesai = False
            if loop is not None:
                self._animasi[nama]['loop'] = loop

    def berhenti(self):
        """Menghentikan animasi."""
        self._saat_ini = None
        self._frame = 0
        self._selesai = False

    def pause(self):
        """Pause animasi."""
        if self._saat_ini and self._saat_ini in self._animasi:
            self._animasi[self._saat_ini]['paused'] = True

    def teruskan(self):
        """Lanjutkan animasi."""
        if self._saat_ini and self._saat_ini in self._animasi:
            self._animasi[self._saat_ini]['paused'] = False

    def lanjutkan(self):
        """Alias Python untuk teruskan() (nama 'lanjutkan' tabrakan keyword)."""
        self.teruskan()

    def set_pause(self, paused: bool):
        """Set status pause animasi."""
        if self._saat_ini and self._saat_ini in self._animasi:
            self._animasi[self._saat_ini]['paused'] = bool(paused)

    def update(self, dt):
        """Update animasi. Panggil setiap frame."""
        if not self._saat_ini or self._saat_ini not in self._animasi:
            return

        anim = self._animasi[self._saat_ini]
        if anim.get('paused', False):
            return

        self._waktu += dt
        fps = anim['fps']
        frame_durasi = 1.0 / fps if fps > 0 else 0.1

        # Majukan beberapa frame sekaligus (dt besar = tetap akurat)
        langkah = 0
        while self._waktu >= frame_durasi - 1e-9 and langkah < 60:
            self._waktu -= frame_durasi
            self._frame += 1
            langkah += 1
            if self._frame >= len(anim['frames']):
                if anim['loop']:
                    self._frame = 0
                else:
                    self._frame = len(anim['frames']) - 1
                    if not self._selesai:
                        self._selesai = True
                        if callable(self.on_selesai):
                            self.on_selesai()
                    break

    def frame_sekarang(self):
        """Mendapatkan frame saat ini."""
        if self._saat_ini and self._saat_ini in self._animasi:
            anim = self._animasi[self._saat_ini]
            return anim['frames'][self._frame]
        return None

    def index_frame(self) -> int:
        """Index frame saat ini."""
        return self._frame

    def sudah_selesai(self):
        """Mengecek apakah animasi sudah selesai."""
        return self._selesai

    def sedang_mainkan(self, nama=None):
        """Mengecek apakah sedang memainkan animasi."""
        if nama:
            return self._saat_ini == nama
        return self._saat_ini is not None

    def set_fps(self, nama, fps):
        """Mengatur FPS animasi."""
        if nama in self._animasi:
            self._animasi[nama]['fps'] = fps

    def daftar_animasi(self):
        """Mendapatkan daftar semua animasi."""
        return list(self._animasi.keys())

    def total_frame(self, nama=None) -> int:
        """Jumlah frame animasi (aktif atau bernama)."""
        if nama is None:
            nama = self._saat_ini
        if nama and nama in self._animasi:
            return len(self._animasi[nama]['frames'])
        return 0


# --- Easing Functions ---
# Semua fungsi menerima t (0..1) dan mengembalikan nilai easing (0..1).

def _ease_linear(t):
    return t


def _ease_in_quad(t):
    return t * t


def _ease_out_quad(t):
    return 1 - (1 - t) * (1 - t)


def _ease_in_out_quad(t):
    if t < 0.5:
        return 2 * t * t
    return 1 - 2 * (t - 1) * (t - 1)


def _ease_in_cubic(t):
    return t * t * t


def _ease_out_cubic(t):
    t -= 1
    return 1 + t * t * t


def _ease_in_out_cubic(t):
    if t < 0.5:
        return 4 * t * t * t
    t = 2 * t - 2
    return 1 + t * t * t / 2


def _ease_in_quart(t):
    return t * t * t * t


def _ease_out_quart(t):
    t -= 1
    return 1 - t * t * t * t


def _ease_in_expo(t):
    return 0 if t == 0 else math.pow(2, 10 * (t - 1))


def _ease_out_expo(t):
    return 1 if t == 1 else 1 - math.pow(2, -10 * t)


def _ease_in_out_expo(t):
    if t == 0 or t == 1:
        return t
    if t < 0.5:
        return 0.5 * math.pow(2, 20 * t - 10)
    return 1 - 0.5 * math.pow(2, -20 * t + 10)


def _ease_in_back(t):
    c1 = 1.70158
    c3 = c1 + 1
    return c3 * t * t * t - c1 * t * t


def _ease_out_back(t):
    c1 = 1.70158
    c3 = c1 + 1
    t -= 1
    return 1 + c3 * t * t * t + c1 * t * t


def _ease_in_out_back(t):
    c1 = 1.70158
    c2 = c1 * 1.525
    if t < 0.5:
        return (2 * t) * (2 * t) * ((c2 + 1) * 2 * t - c2) / 2
    t = 2 * t - 2
    return ((t * t * ((c2 + 1) * t + c2)) + 2) / 2


def _ease_in_elastic(t):
    if t == 0 or t == 1:
        return t
    c4 = 2 * math.pi / 3
    return -math.pow(2, 10 * (t - 1)) * math.sin((t - 1) * c4)


def _ease_out_elastic(t):
    if t == 0 or t == 1:
        return t
    c4 = 2 * math.pi / 3
    return math.pow(2, -10 * t) * math.sin((t - 1) * c4) + 1


def _ease_in_out_elastic(t):
    if t == 0 or t == 1:
        return t
    c5 = 2 * math.pi / 4.5
    if t < 0.5:
        return -(math.pow(2, 20 * t - 10) * math.sin((20 * t - 11.125) * c5)) / 2
    return (math.pow(2, -20 * t + 10) * math.sin((20 * t - 11.125) * c5)) / 2 + 1


def _ease_in_bounce(t):
    return 1 - _ease_out_bounce(1 - t)


def _ease_out_bounce(t):
    n1 = 7.5625
    d1 = 2.75
    if t < 1 / d1:
        return n1 * t * t
    elif t < 2 / d1:
        t -= 1.5 / d1
        return n1 * t * t + 0.75
    elif t < 2.5 / d1:
        t -= 2.25 / d1
        return n1 * t * t + 0.9375
    t -= 2.625 / d1
    return n1 * t * t + 0.984375


def _ease_in_out_bounce(t):
    if t < 0.5:
        return (1 - _ease_out_bounce(1 - 2 * t)) / 2
    return (1 + _ease_out_bounce(2 * t - 1)) / 2


def _ease_in_sine(t):
    return 1 - math.cos(t * math.pi / 2)


def _ease_out_sine(t):
    return math.sin(t * math.pi / 2)


def _ease_in_out_sine(t):
    return -(math.cos(math.pi * t) - 1) / 2


_EASINGS = {
    "linear": _ease_linear,
    "ease_in": _ease_in_quad,
    "ease_out": _ease_out_quad,
    "ease_in_out": _ease_in_out_quad,
    "ease_in_quad": _ease_in_quad,
    "ease_out_quad": _ease_out_quad,
    "ease_in_out_quad": _ease_in_out_quad,
    "ease_in_cubic": _ease_in_cubic,
    "ease_out_cubic": _ease_out_cubic,
    "ease_in_out_cubic": _ease_in_out_cubic,
    "ease_in_quart": _ease_in_quart,
    "ease_out_quart": _ease_out_quart,
    "ease_in_expo": _ease_in_expo,
    "ease_out_expo": _ease_out_expo,
    "ease_in_out_expo": _ease_in_out_expo,
    "ease_in_back": _ease_in_back,
    "ease_out_back": _ease_out_back,
    "ease_in_out_back": _ease_in_out_back,
    "ease_in_elastic": _ease_in_elastic,
    "ease_out_elastic": _ease_out_elastic,
    "ease_in_out_elastic": _ease_in_out_elastic,
    "ease_in_bounce": _ease_in_bounce,
    "ease_out_bounce": _ease_out_bounce,
    "ease_in_out_bounce": _ease_in_out_bounce,
    "ease_in_sine": _ease_in_sine,
    "ease_out_sine": _ease_out_sine,
    "ease_in_out_sine": _ease_in_out_sine,
    "bounce": _ease_out_bounce,   # alias backward-compatible
    "elastic": _ease_out_elastic,  # alias backward-compatible (sekarang benar)
}


def daftar_easing():
    """Mendapatkan daftar nama easing yang tersedia."""
    return list(_EASINGS.keys())


class AnimasiTween:
    """Animasi tween: perubahan nilai secara gradual dengan easing.

    Contoh:
        buat tween = animasi.buat_tween(0, 100, durasi=1.0, easing="ease_out_back")
        selama game berjalan:
            nilai = tween.update(dt)
    """

    def __init__(self, nilai_awal=0, nilai_akhir=1, durasi=1.0, easing='linear'):
        self.nilai_awal = nilai_awal
        self.nilai_akhir = nilai_akhir
        self.durasi = max(durasi, 0.0001)
        self.easing = easing
        self.waktu_sekarang = 0
        self.selesai = False
        self.berulang = False
        self.on_selesai = None      # callback saat tween selesai
        self.on_siklus = None       # callback saat satu siklus loop selesai

    def update(self, dt):
        """Update tween dan mengembalikan nilai saat ini."""
        if self.selesai:
            return self.nilai_akhir

        self.waktu_sekarang += dt
        # epsilon agar akumulasi float (10 x 0.1) tetap dianggap selesai
        if self.waktu_sekarang >= self.durasi - 1e-9:
            if self.berulang:
                self.waktu_sekarang = 0
                if callable(self.on_siklus):
                    self.on_siklus()
            else:
                self.waktu_sekarang = self.durasi
                self.selesai = True
                if callable(self.on_selesai):
                    self.on_selesai()

        t = min(self.waktu_sekarang / self.durasi, 1.0)
        t = self._apply_easing(t)
        return self.nilai_awal + (self.nilai_akhir - self.nilai_awal) * t

    def _apply_easing(self, t):
        """Menerapkan easing function."""
        fn = _EASINGS.get(self.easing, _ease_linear)
        return fn(t)

    def reset(self):
        """Reset tween ke awal."""
        self.waktu_sekarang = 0
        self.selesai = False

    def nilai_sekarang(self):
        """Mendapatkan nilai saat ini tanpa majukan waktu."""
        return self.update(0)

    def set_easing(self, easing):
        """Mengubah easing tween."""
        self.easing = easing

    def kemajuan(self) -> float:
        """Kemajuan tween 0.0 .. 1.0 (tanpa easing)."""
        return min(self.waktu_sekarang / self.durasi, 1.0)


class AnimasiSequence:
    """Urutan animasi yang dijalankan berurutan."""

    def __init__(self):
        self._steps = []
        self._index = 0
        self.selesai = False
        self.on_selesai = None

    def tambah_step(self, tween):
        """Menambahkan step animasi."""
        self._steps.append(tween)
        return self

    def tambah_tween(self, nilai_awal=0, nilai_akhir=1, durasi=1.0, easing='linear'):
        """Membuat dan menambahkan tween baru ke sequence."""
        return self.tambah_step(AnimasiTween(nilai_awal, nilai_akhir, durasi, easing))

    def update(self, dt):
        """Update sequence."""
        if self.selesai or not self._steps:
            return

        step = self._steps[self._index]
        step.update(dt)
        if step.selesai:
            self._index += 1
            if self._index >= len(self._steps):
                self.selesai = True
                if callable(self.on_selesai):
                    self.on_selesai()

    def nilai_sekarang(self):
        """Mendapatkan nilai saat ini."""
        if self._steps and not self.selesai:
            return self._steps[self._index].nilai_sekarang()
        if self._steps:
            return self._steps[-1].nilai_akhir
        return None

    def reset(self):
        """Reset sequence."""
        self._index = 0
        self.selesai = False
        for step in self._steps:
            step.reset()


def buat_tween(nilai_awal=0, nilai_akhir=1, durasi=1.0, easing='linear'):
    """Membuat tween baru."""
    return AnimasiTween(nilai_awal, nilai_akhir, durasi, easing)


def buat_sequence():
    """Membuat sequence baru."""
    return AnimasiSequence()


module = SimpleNamespace(
    Animasi=Animasi,
    AnimasiTween=AnimasiTween,
    AnimasiSequence=AnimasiSequence,
    buat_tween=buat_tween,
    buat_sequence=buat_sequence,
    daftar_easing=daftar_easing,
)
