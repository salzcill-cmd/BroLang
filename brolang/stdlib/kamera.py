"""
Modul Kamera untuk BroLang Game Development
============================================

Menyediakan sistem kamera untuk game.

Contoh:
    impor kamera

    buat cam = kamera.Kamera(800, 600)
    cam.set_target(player)
    cam.update(dt)
"""

import math
from types import SimpleNamespace


class Kamera:
    """Kamera 2D dengan smoothing."""

    def __init__(self, lebar_layar=800, tinggi_layar=600):
        self.x = 0.0
        self.y = 0.0
        self.lebar_layar = lebar_layar
        self.tinggi_layar = tinggi_layar
        self.zoom = 1.0
        self.sudut = 0.0
        self.target = None
        this = self

        # Smoothing
        this.kecepatan_smooth = 5.0
        this.offset_x = 0.0
        this.offset_y = 0.0

        # Bounds
        this.batas_kiri = None
        this.batas_kanan = None
        this.batas_atas = None
        this.batas_bawah = None

        # Screen shake
        this.shake_intensity = 0
        this.shake_duration = 0
        this.shake_waktu = 0
        this.shake_offset_x = 0
        this.shake_offset_y = 0

    def set_target(self, target):
        """Set target kamera (objek yang diikuti)."""
        self.target = target

    def set_offset(self, x, y):
        """Set offset kamera."""
        self.offset_x = x
        self.offset_y = y

    def set_posisi(self, x, y):
        """Set posisi kamera langsung (tanpa smoothing)."""
        self.x = float(x)
        self.y = float(y)

    def posisi(self):
        """Posisi kamera saat ini (x, y)."""
        return self.x, self.y

    def gerak(self, dx, dy):
        """Geser kamera (pan) sebesar dx, dy."""
        self.x += dx
        self.y += dy

    def reset(self):
        """Reset kamera ke posisi awal & zoom 1."""
        self.x = 0.0
        self.y = 0.0
        self.zoom = 1.0
        self.sudut = 0.0
        self.target = None
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.shake_waktu = 0
        self.shake_offset_x = 0
        self.shake_offset_y = 0

    def set_batas_world(self, lebar_world, tinggi_world):
        """Set batas kamera otomatis dari ukuran world.

        Kamera tidak akan keluar dari world.
        """
        self.batas_kiri = 0
        self.batas_atas = 0
        self.batas_kanan = lebar_world
        self.batas_bawah = tinggi_world

    def set_sudut(self, derajat):
        """Set rotasi kamera (derajat)."""
        self.sudut = derajat

    def set_bounds(self, kiri, atas, kanan, bawah):
        """Set batas pergerakan kamera."""
        self.batas_kiri = kiri
        self.batas_atas = atas
        self.batas_kanan = kanan
        self.batas_bawah = bawah

    def set_zoom(self, zoom):
        """Set zoom level."""
        self.zoom = max(0.1, min(zoom, 5.0))

    def update(self, dt):
        """Update kamera."""
        # Follow target
        if self.target:
            target_x = self.target.x + self.offset_x
            target_y = self.target.y + self.offset_y

            # Smooth follow
            self.x += (target_x - self.x) * self.kecepatan_smooth * dt
            self.y += (target_y - self.y) * self.kecepatan_smooth * dt

        # Apply bounds
        if self.batas_kiri is not None:
            self.x = max(self.batas_kiri, self.x)
        if self.batas_kanan is not None:
            self.x = min(self.batas_kanan - self.lebar_layar / self.zoom, self.x)
        if self.batas_atas is not None:
            self.y = max(self.batas_atas, self.y)
        if self.batas_bawah is not None:
            self.y = min(self.batas_bawah - self.tinggi_layar / self.zoom, self.y)

        # Screen shake
        if self.shake_waktu > 0:
            self.shake_waktu -= dt
            import random
            self.shake_offset_x = random.uniform(-1, 1) * self.shake_intensity
            self.shake_offset_y = random.uniform(-1, 1) * self.shake_intensity
        else:
            self.shake_offset_x = 0
            self.shake_offset_y = 0

    def shake(self, intensity=5, duration=0.2):
        """Memulai screen shake."""
        self.shake_intensity = intensity
        self.shake_duration = duration
        self.shake_waktu = duration

    def world_to_screen(self, world_x, world_y):
        """Mengkonversi koordinat world ke screen."""
        screen_x = (world_x - self.x) * self.zoom + self.shake_offset_x
        screen_y = (world_y - self.y) * self.zoom + self.shake_offset_y
        return screen_x, screen_y

    def screen_to_world(self, screen_x, screen_y):
        """Mengkonversi koordinat screen ke world."""
        world_x = (screen_x - self.shake_offset_x) / self.zoom + self.x
        world_y = (screen_y - self.shake_offset_y) / self.zoom + self.y
        return world_x, world_y

    def is_visible(self, x, y, lebar=0, tinggi=0):
        """Mengecek apakah objek terlihat di layar."""
        screen_x, screen_y = self.world_to_screen(x, y)
        return (
            -lebar < screen_x < self.lebar_layar and
            -tinggi < screen_y < self.tinggi_layar
        )

    def get_view_rect(self):
        """Mendapatkan rectangle area yang terlihat."""
        lebar = self.lebar_layar / self.zoom
        tinggi = self.tinggi_layar / self.zoom
        return SimpleNamespace(
            x=self.x,
            y=self.y,
            lebar=lebar,
            tinggi=tinggi,
        )

    def apply(self, x, y):
        """Menerapkan transformasi kamera ke koordinat (dengan rotasi)."""
        sx, sy = self.world_to_screen(x, y)
        if self.sudut:
            import math
            rad = math.radians(self.sudut)
            cx = self.lebar_layar / 2
            cy = self.tinggi_layar / 2
            dx = sx - cx
            dy = sy - cy
            cos_a = math.cos(rad)
            sin_a = math.sin(rad)
            sx = cx + dx * cos_a - dy * sin_a
            sy = cy + dx * sin_a + dy * cos_a
        return sx, sy


class KameraTopDown(Kamera):
    """Kamera untuk game top-down."""

    def __init__(self, lebar_layar=800, tinggi_layar=600):
        super().__init__(lebar_layar, tinggi_layar)
        this = self
        this.kecepatan_smooth = 8.0
        this.debounce = 0.1
        this._debounce_timer = 0

    def follow_with_debounce(self, target, dt):
        """Follow target dengan debounce."""
        self._debounce_timer -= dt
        if self._debounce_timer <= 0:
            self.set_target(target)
            self._debounce_timer = self.debounce


class KameraSideScroll(Kamera):
    """Kamera untuk game side-scrolling."""

    def __init__(self, lebar_layar=800, tinggi_layar=600):
        super().__init__(lebar_layar, tinggi_layar)
        this = self
        this.kecepatan_smooth = 10.0
        this.follow_x = True
        this.follow_y = False

    def update(self, dt):
        if self.target:
            target_x = self.target.x + self.offset_x
            target_y = self.y

            if self.follow_x:
                self.x += (target_x - self.x) * self.kecepatan_smooth * dt
            if self.follow_y:
                target_y = self.target.y + self.offset_y
                self.y += (target_y - self.y) * self.kecepatan_smooth * dt

        # Bounds check
        if self.batas_kiri is not None:
            self.x = max(self.batas_kiri, self.x)
        if self.batas_kanan is not None:
            self.x = min(self.batas_kanan - self.lebar_layar / self.zoom, self.x)

        # Screen shake
        if self.shake_waktu > 0:
            self.shake_waktu -= dt
            import random
            self.shake_offset_x = random.uniform(-1, 1) * self.shake_intensity
            self.shake_offset_y = random.uniform(-1, 1) * self.shake_intensity
        else:
            self.shake_offset_x = 0
            self.shake_offset_y = 0


def buat_kamera(lebar_layar=800, tinggi_layar=600):
    """Membuat kamera baru."""
    return Kamera(lebar_layar, tinggi_layar)


def buat(lebar_layar=800, tinggi_layar=600):
    return Kamera(lebar_layar, tinggi_layar)


def buat_layar_penuh():
    """Membuat kamera yang mengikuti ukuran layar aktif.

    Butuh pygame display aktif (game.buat_jendela sudah dipanggil).
    """
    try:
        import pygame
        surf = pygame.display.get_surface()
        if surf is not None:
            w, h = surf.get_size()
            return Kamera(w, h)
    except Exception:
        pass
    return Kamera(800, 600)


def buat_top_down(lebar_layar=800, tinggi_layar=600):
    """Membuat kamera top-down."""
    return KameraTopDown(lebar_layar, tinggi_layar)


def buat_side_scroll(lebar_layar=800, tinggi_layar=600):
    """Membuat kamera side-scrolling."""
    return KameraSideScroll(lebar_layar, tinggi_layar)


module = SimpleNamespace(
    Kamera=Kamera,
    KameraTopDown=KameraTopDown,
    KameraSideScroll=KameraSideScroll,
    buat_kamera=buat_kamera,
    buat_layar_penuh=buat_layar_penuh,
    buat_top_down=buat_top_down,
    buat_side_scroll=buat_side_scroll,
)
