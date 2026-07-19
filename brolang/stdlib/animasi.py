"""
Modul Animasi untuk BroLang Game Development
=============================================

Menyediakan sistem animasi untuk game.

Contoh:
    impor animasi

    buat anim = animasi.Animasi()
    anim.tambah_frame("jalan", [0, 1, 2, 3])
    anim.set_fps("jalan", 10)
"""

from types import SimpleNamespace


class Animasi:
    """Sistem animasi sprite."""

    def __init__(self):
        self._animasi = {}
        self._saat_ini = None
        self._frame = 0
        self._waktu = 0
        self._selesai = False
        this = self

    def tambah(self, nama, frames, fps=10, loop=True):
        """Menambahkan animasi baru."""
        self._animasi[nama] = {
            'frames': frames,
            'fps': fps,
            'loop': loop,
            'frame_sekarang': 0,
        }

    def mainkan(self, nama, loop=None):
        """Memainkan animasi."""
        if nama in self._animasi:
            self._saat_ini = nama
            self._frame = 0
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

    def lanjutkan(self):
        """Lanjutkan animasi."""
        if self._saat_ini and self._saat_ini in self._animasi:
            self._animasi[self._saat_ini]['paused'] = False

    def update(self, dt):
        """Update animasi."""
        if not self._saat_ini or self._saat_ini not in self._animasi:
            return

        anim = self._animasi[self._saat_ini]
        if anim.get('paused', False):
            return

        self._waktu += dt
        fps = anim['fps']
        if fps > 0:
            frame_durasi = 1.0 / fps
        else:
            frame_durasi = 0.1

        if self._waktu >= frame_durasi:
            self._waktu -= frame_durasi
            self._frame += 1
            if self._frame >= len(anim['frames']):
                if anim['loop']:
                    self._frame = 0
                else:
                    self._frame = len(anim['frames']) - 1
                    self._selesai = True

    def frame_sekarang(self):
        """Mendapatkan frame saat ini."""
        if self._saat_ini and self._saat_ini in self._animasi:
            anim = self._animasi[self._saat_ini]
            return anim['frames'][self._frame]
        return None

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


class AnimasiTween:
    """Animasi tween (perubahan nilai secara gradual)."""

    def __init__(self, nilai_awal=0, nilai_akhir=1, durasi=1.0, easing='linear'):
        self.nilai_awal = nilai_awal
        self.nilai_akhir = nilai_akhir
        self.durasi = durasi
        self.easing = easing
        self.waktu_sekarang = 0
        self.selesai = False
        self.berulang = False
        this = self

    def update(self, dt):
        """Update tween."""
        if self.selesai:
            return self.nilai_akhir

        self.waktu_sekarang += dt
        if self.waktu_sekarang >= self.durasi:
            if self.berulang:
                self.waktu_sekarang = 0
                self.selesai = False
            else:
                self.waktu_sekarang = self.durasi
                self.selesai = True

        t = min(self.waktu_sekarang / self.durasi, 1.0)
        t = self._apply_easing(t)

        return self.nilai_awal + (self.nilai_akhir - self.nilai_awal) * t

    def _apply_easing(self, t):
        """Menerapkan easing function."""
        if self.easing == 'linear':
            return t
        elif self.easing == 'ease_in':
            return t * t
        elif self.easing == 'ease_out':
            return t * (2 - t)
        elif self.easing == 'ease_in_out':
            if t < 0.5:
                return 2 * t * t
            return -1 + (4 - 2 * t) * t
        elif self.easing == 'bounce':
            if t < 0.5:
                return 8 * t * t * t * t
            return 1 - 8 * (t - 1) * (t - 1) * (t - 1) * (t - 1)
        elif self.easing == 'elastic':
            return 1 if t == 1 else -0.5 * (2 ** (10 * (t - 1))) * ((t - 1.1) * 5 * 3.14159).sin()
        return t

    def reset(self):
        """Reset tween."""
        self.waktu_sekarang = 0
        self.selesai = False

    def nilai_sekarang(self):
        """Mendapatkan nilai saat ini."""
        return self.update(0)


class AnimasiSequence:
    """Urutan animasi yang dijalankan berurutan."""

    def __init__(self):
        self._steps = []
        self._index = 0
        self.selesai = False

    def tambah_step(self, tween):
        """Menambahkan step animasi."""
        self._steps.append(tween)

    def update(self, dt):
        """Update sequence."""
        if self.selesai or not self._steps:
            return

        self._steps[self._index].update(dt)
        if self._steps[self._index].selesai:
            self._index += 1
            if self._index >= len(self._steps):
                self.selesai = True

    def nilai_sekarang(self):
        """Mendapatkan nilai saat ini."""
        if self._steps and not self.selesai:
            return self._steps[self._index].nilai_sekarang()
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
)
