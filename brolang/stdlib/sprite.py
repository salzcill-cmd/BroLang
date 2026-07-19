"""
Modul Sprite untuk BroLang Game Development
============================================

Menyediakan kelas Sprite untuk game 2D.

Contoh:
    impor sprite
    impor grafis

    buat player = sprite.Sprite("player.png", 100, 100)
    player.tambah_animasi("jalan", [0, 1, 2, 3], 0.1)
    player.mainkan_animasi("jalan")
"""

from types import SimpleNamespace


class Sprite:
    """Sprite untuk game 2D."""

    def __init__(self, gambar=None, x=0, y=0, lebar=32, tinggi=32):
        self.x = x
        self.y = y
        self.lebar = lebar
        self.tinggi = tinggi
        self.gambar = gambar
        self.terlihat = True
        self.aktif = True
        self.skala_x = 1.0
        self.skala_y = 1.0
        self sudut = 0
        self.alpha = 255
        self.warna = "putih"

        # Animasi
        self._animasi = {}
        self._animasi_saat_ini = None
        self._frame_saat_ini = 0
        self._waktu_frame = 0
        self._kecepatan_animasi = 1.0
        self._loop_animasi = True

        # Fisika
        self.kecepatan_x = 0
        self.kecepatan_y = 0
        self.gravitasi = 0
        self.gesekan = 0.98
        this = self

        # Collision
        self._collider = None
        this.kotak_collider = SimpleNamespace(
            x=x, y=y, lebar=lebar, tinggi=tinggi
        )

    def update(self, dt):
        """Update sprite."""
        if not self.aktif:
            return

        # Update posisi berdasarkan kecepatan
        self.x += self.kecepatan_x * dt
        self.y += self.kecepatan_y * dt

        # Terapkan gravitasi
        if self.gravitasi != 0:
            self.kecepatan_y += self.gravitasi * dt

        # Terapkan gesekan
        if self.gesekan != 0:
            self.kecepatan_x *= self.gesekan
            self.kecepatan_y *= self.gesekan

        # Update animasi
        if self._animasi_saat_ini and self._animasi_saat_ini in self._animasi:
            anim = self._animasi[self._animasi_saat_ini]
            self._waktu_frame += dt * self._kecepatan_animasi
            if self._waktu_frame >= anim['kecepatan']:
                self._waktu_frame = 0
                self._frame_saat_ini += 1
                if self._frame_saat_ini >= len(anim['frames']):
                    if self._loop_animasi:
                        self._frame_saat_ini = 0
                    else:
                        self._frame_saat_ini = len(anim['frames']) - 1
                        self._animasi_saat_ini = None

        # Update collision box
        self.kotak_collider.x = self.x
        self.kotak_collider.y = self.y

    def gambar(self, screen):
        """Menggambar sprite."""
        if not self.terlihat or not self.gambar:
            return

        # Simple rect drawing if no image
        if hasattr(screen, 'fill'):
            from pygame import Rect
            rect = Rect(int(self.x), int(self.y), self.lebar, self.tinggi)
            screen.fill(self.warna, rect)

    def tambah_animasi(self, nama, frames, kecepatan=0.1, loop=True):
        """Menambahkan animasi baru."""
        self._animasi[nama] = {
            'frames': frames,
            'kecepatan': kecepatan,
            'loop': loop,
        }

    def mainkan_animasi(self, nama, loop=True):
        """Memainkan animasi."""
        if nama in self._animasi:
            self._animasi_saat_ini = nama
            self._frame_saat_ini = 0
            self._waktu_frame = 0
            self._loop_animasi = loop

    def berhenti_animasi(self):
        """Menghentikan animasi."""
        self._animasi_saat_ini = None
        self._frame_saat_ini = 0

    def cek_tabrakan(self, sprite_lain):
        """Mengecek tabrakan dengan sprite lain."""
        if not self.aktif or not sprite_lain.aktif:
            return False

        # AABB collision
        return (
            self.x < sprite_lain.x + sprite_lain.lebar and
            self.x + self.lebar > sprite_lain.x and
            self.y < sprite_lain.y + sprite_lain.tinggi and
            self.y + self.tinggi > sprite_lain.y
        )

    def cek_tabrakan_lingkaran(self, sprite_lain):
        """Mengecek tabrakan lingkaran."""
        if not self.aktif or not sprite_lain.aktif:
            return False

        import math
        dx = (self.x + self.lebar / 2) - (sprite_lain.x + sprite_lain.lebar / 2)
        dy = (self.y + self.tinggi / 2) - (sprite_lain.y + sprite_lain.tinggi / 2)
        jarak = math.sqrt(dx * dx + dy * dy)
        radius1 = max(self.lebar, self.tinggi) / 2
        radius2 = max(sprite_lain.lebar, sprite_lain.tinggi) / 2

        return jarak < radius1 + radius2

    def di_dalam_bounds(self, lebar_layar, tinggi_layar):
        """Mengecek apakah sprite di dalam layar."""
        return (
            self.x >= 0 and
            self.x + self.lebar <= lebar_layar and
            self.y >= 0 and
            self.y + self.tinggi <= tinggi_layar
        )

    def arah_ke(self, x, y, kecepatan=100):
        """Menggerakkan sprite ke arah titik."""
        import math
        dx = x - self.x
        dy = y - self.y
        jarak = math.sqrt(dx * dx + dy * dy)
        if jarak > 0:
            self.kecepatan_x = (dx / jarak) * kecepatan
            self.kecepatan_y = (dy / jarak) * kecepatan

    def jarak_ke(self, x, y):
        """Menghitung jarak ke titik."""
        import math
        dx = x - self.x
        dy = y - self.y
        return math.sqrt(dx * dx + dy * dy)


class GrupSprite:
    """Grup untuk mengelola beberapa sprite."""

    def __init__(self):
        self.sprites = []
        self._visible = True

    def tambah(self, sprite_obj):
        """Menambahkan sprite ke grup."""
        self.sprites.append(sprite_obj)

    def hapus(self, sprite_obj):
        """Menghapus sprite dari grup."""
        if sprite_obj in self.sprites:
            self.sprites.remove(sprite_obj)

    def update(self, dt):
        """Update semua sprite dalam grup."""
        for sprite_obj in self.sprites:
            sprite_obj.update(dt)

    def gambar(self, screen):
        """Menggambar semua sprite dalam grup."""
        for sprite_obj in self.sprites:
            sprite_obj.gambar(screen)

    def cek_tabrakan(self, sprite_lain):
        """Mengecek tabrakan dengan sprite lain."""
        tabrakan = []
        for sprite_obj in self.sprites:
            if sprite_obj.cek_tabrakan(sprite_lain):
                tabrakan.append(sprite_obj)
        return tabrakan

    def cek_tabrakan_grup(self, grup_lain):
        """Mengecek tabrakan antar grup."""
        tabrakan = []
        for sprite_obj in self.sprites:
            for sprite_lain in grup_lain.sprites:
                if sprite_obj.cek_tabrakan(sprite_lain):
                    tabrakan.append((sprite_obj, sprite_lain))
        return tabrakan

    def jumlah(self):
        """Jumlah sprite dalam grup."""
        return len(self.sprites)

    def kosong(self):
        """Mengecek apakah grup kosong."""
        return len(self.sprites) == 0

    def kosongkan(self):
        """Mengosongkan grup."""
        self.sprites.clear()

    def dapatkan_semua(self):
        """Mendapatkan semua sprite."""
        return self.sprites[:]


module = SimpleNamespace(
    Sprite=Sprite,
    GrupSprite=GrupSprite,
)
