"""
Modul Sprite untuk BroLang Game Development
============================================

Menyediakan kelas Sprite untuk game 2D dengan dukungan gambar,
sprite sheet, animasi frame, rotasi, skala, alpha, dan collider.

Contoh:
    impor sprite
    impor grafis

    buat player = sprite.Sprite("player.png", 100, 100)
    player.tambah_animasi("jalan", [0, 1, 2, 3], kecepatan=0.1)
    player.mainkan_animasi("jalan")

    # Tanpa gambar (kotak berwarna saja)
    buat musuh = sprite.Sprite(None, 50, 50, lebar=32, tinggi=32)
    musuh.warna = "merah"
"""

import math
import os
from types import SimpleNamespace

try:
    import pygame
except ImportError:
    pygame = None


def _load_image(gambar):
    """Muat gambar dari path / pygame Surface / objek bergambar."""
    if gambar is None:
        return None
    if isinstance(gambar, str):
        if pygame is None:
            return None
        try:
            return pygame.image.load(gambar).convert_alpha()
        except (pygame.error, FileNotFoundError, OSError):
            return None
    # Sudah berupa Surface atau objek dengan atribut get_width/get_height
    return gambar


class Sprite:
    """Sprite untuk game 2D."""

    def __init__(self, gambar=None, x=0, y=0, lebar=32, tinggi=32,
                 ukuran_frame_x=32, ukuran_frame_y=32):
        self.x = float(x)
        self.y = float(y)
        self.lebar = lebar
        self.tinggi = tinggi
        # Atribut gambar diberi nama 'surface' agar TIDAK menimpa method gambar()
        self.surface = _load_image(gambar)
        self.ukuran_frame_x = ukuran_frame_x
        self.ukuran_frame_y = ukuran_frame_y

        # Render properties
        self.terlihat = True
        self.aktif = True
        self.skala_x = 1.0
        self.skala_y = 1.0
        self.sudut = 0.0          # derajat
        self.alpha = 255
        self.flip_x = False
        self.flip_y = False
        self.warna = "putih"      # dipakai jika tidak ada gambar
        self.z = 0                # urutan gambar (makin besar makin depan)
        self.tint = None          # (r, g, b) untuk overlay warna

        # Animasi
        self._animasi = {}
        self._animasi_saat_ini = None
        self._frame_saat_ini = 0
        self._waktu_frame = 0.0
        self._kecepatan_animasi = 1.0
        self._loop_animasi = True
        self._satu_putaran_selesai = False
        self.on_selesai = None    # callback saat animasi non-loop selesai

        # Gerak sederhana
        self.kecepatan_x = 0.0
        self.kecepatan_y = 0.0
        self.gravitasi = 0.0
        self.gesekan = 0.0        # 0 = tanpa gesekan, 0.98 = gesekan kuat
        self.batasan = None       # SimpleNamespace(lebar, tinggi) untuk clamp

        # Collider: "rect" (default) atau "lingkaran"
        self.mode_collider = "rect"
        self.radius = max(lebar, tinggi) / 2.0
        self.offset_x = 0.0
        self.offset_y = 0.0

        # v6.6: patroli waypoint (dipakai ikuti_patroli)
        self._patroli = None

    # ---------------- Frame / Animasi ----------------

    def _region_frame(self, frame):
        """Konversi frame ke region (x, y, w, h) pada sprite sheet."""
        if isinstance(frame, (list, tuple)):
            if len(frame) == 4:
                return (int(frame[0]), int(frame[1]),
                        int(frame[2]), int(frame[3]))
            return (int(frame[0]), int(frame[1]),
                    self.ukuran_frame_x, self.ukuran_frame_y)
        # frame berupa angka -> indeks grid pada sprite sheet
        kolom = max(1, int(self.surface.get_width() / self.ukuran_frame_x)
                    if self.surface else 1)
        idx = int(frame)
        return (idx % kolom * self.ukuran_frame_x,
                idx // kolom * self.ukuran_frame_y,
                self.ukuran_frame_x, self.ukuran_frame_y)

    def tambah_animasi(self, nama, frames, kecepatan=0.1, loop=True):
        """Menambahkan animasi baru.

        frames: list angka indeks grid, atau list region (x, y, w, h).
        """
        self._animasi[nama] = {
            "frames": frames,
            "kecepatan": max(0.001, float(kecepatan)),
            "loop": loop,
        }
        return self

    def mainkan_animasi(self, nama, loop=None):
        """Memainkan animasi. Kembalikan False jika nama tidak ada."""
        if nama not in self._animasi:
            return False
        self._animasi_saat_ini = nama
        self._frame_saat_ini = 0
        self._waktu_frame = 0.0
        self._satu_putaran_selesai = False
        if loop is not None:
            self._animasi[nama]["loop"] = loop
        self._loop_animasi = self._animasi[nama]["loop"]
        return True

    def berhenti_animasi(self):
        """Menghentikan animasi dan kembali ke frame 0."""
        self._animasi_saat_ini = None
        self._frame_saat_ini = 0
        self._satu_putaran_selesai = False

    def frame_sekarang(self):
        """Region frame yang sedang aktif, atau None."""
        if not self._animasi_saat_ini:
            return None
        anim = self._animasi.get(self._animasi_saat_ini)
        if not anim:
            return None
        frames = anim["frames"]
        if not frames:
            return None
        idx = min(self._frame_saat_ini, len(frames) - 1)
        return frames[idx]

    def animasi_selesai(self):
        """True jika animasi non-loop sudah selesai satu putaran."""
        return self._satu_putaran_selesai

    def set_fps_animasi(self, fps):
        """Set kecepatan animasi dalam frame per detik."""
        if fps > 0:
            self._kecepatan_animasi = fps
        return self

    def daftar_animasi(self):
        return list(self._animasi.keys())

    # ---------------- Update ----------------

    def update(self, dt):
        """Update posisi, gravitasi, dan animasi."""
        if not self.aktif:
            return

        if self.gravitasi != 0:
            self.kecepatan_y += self.gravitasi * dt

        self.x += self.kecepatan_x * dt
        self.y += self.kecepatan_y * dt

        if self.gesekan > 0:
            self.kecepatan_x *= max(0.0, 1.0 - self.gesekan * dt)
            self.kecepatan_y *= max(0.0, 1.0 - self.gesekan * dt)

        # Batasi dalam area (mis. layar)
        if self.batasan is not None:
            self.x = max(0.0, min(float(self.batasan.lebar) - self.lebar, self.x))
            self.y = max(0.0, min(float(self.batasan.tinggi) - self.tinggi, self.y))

        # Patroli waypoint (v6.6): posisi sprite ikut bergerak
        if self._patroli is not None:
            self._patroli.update(dt)
            self.x, self.y = self._patroli.posisi()

        # Animasi
        if self._animasi_saat_ini and self._animasi_saat_ini in self._animasi:
            anim = self._animasi[self._animasi_saat_ini]
            self._waktu_frame += dt * self._kecepatan_animasi
            langkah = 0
            while self._waktu_frame >= anim["kecepatan"] - 1e-9 and langkah < 60:
                self._waktu_frame -= anim["kecepatan"]
                self._frame_saat_ini += 1
                langkah += 1
                if self._frame_saat_ini >= len(anim["frames"]):
                    if anim["loop"]:
                        self._frame_saat_ini = 0
                    else:
                        self._frame_saat_ini = len(anim["frames"]) - 1
                        self._satu_putaran_selesai = True
                        if self.on_selesai is not None:
                            cb = self.on_selesai
                            self.on_selesai = None
                            cb(self)
                        break

    # ---------------- Gambar ----------------

    def _surface_frame(self):
        """Surface untuk frame saat ini (atau gambar penuh)."""
        if self.surface is None:
            return None
        frame = self.frame_sekarang()
        if frame is None:
            return self.surface
        rx, ry, rw, rh = self._region_frame(frame)
        try:
            return self.surface.subsurface(pygame.Rect(rx, ry, rw, rh))
        except (ValueError, pygame.error):
            return self.surface

    def gambar(self, screen, kamera=None, posisi_x=None, posisi_y=None):
        """Menggambar sprite. kamera opsional (objek dengan world_to_screen)."""
        if not self.terlihat or not self.aktif:
            return
        if pygame is None:
            return

        gx = self.x if posisi_x is None else posisi_x
        gy = self.y if posisi_y is None else posisi_y
        if kamera is not None:
            gx, gy = kamera.world_to_screen(gx, gy)

        surf = self._surface_frame()
        if surf is not None:
            w = int(surf.get_width() * self.skala_x)
            h = int(surf.get_height() * self.skala_y)
            if w <= 0 or h <= 0:
                return
            if self.skala_x != 1.0 or self.skala_y != 1.0:
                surf = pygame.transform.smoothscale(surf, (w, h))
            if self.flip_x or self.flip_y:
                surf = pygame.transform.flip(surf, self.flip_x, self.flip_y)
            if self.alpha < 255:
                surf.set_alpha(max(0, min(255, int(self.alpha))))
            if self.tint is not None:
                overlay = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
                overlay.fill((*self.tint, 90))
                surf = surf.copy()
                surf.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            if self.sudut != 0.0:
                # Rotasi berputar di tengah sprite (bukan pojok kiri-atas)
                surf = pygame.transform.rotate(surf, self.sudut)
                rect = surf.get_rect(center=(int(gx) + int(w) // 2,
                                              int(gy) + int(h) // 2))
                screen.blit(surf, rect)
            else:
                screen.blit(surf, (int(gx), int(gy)))
        else:
            # Tidak ada gambar -> kotak berwarna
            import brolang.stdlib.grafis as grafis
            grafis.segi_panjang(gx, gy, self.lebar * self.skala_x,
                                self.tinggi * self.skala_y, self.warna)

    # ---------------- Collider ----------------

    def _rect_collider(self):
        """Rectangle collider (dengan offset)."""
        return (
            self.x + self.offset_x,
            self.y + self.offset_y,
            self.lebar,
            self.tinggi,
        )

    def cek_tabrakan(self, sprite_lain):
        """AABB collision dengan sprite lain."""
        if not self.aktif or not sprite_lain.aktif:
            return False
        if self.mode_collider == "lingkaran" or sprite_lain.mode_collider == "lingkaran":
            return self.cek_tabrakan_lingkaran(sprite_lain)
        ax, ay, aw, ah = self._rect_collider()
        bx, by, bw, bh = sprite_lain._rect_collider()
        return (ax < bx + bw and ax + aw > bx and
                ay < by + bh and ay + ah > by)

    def cek_tabrakan_lingkaran(self, sprite_lain):
        """Collision lingkaran (pakai radius tiap sprite)."""
        if not self.aktif or not sprite_lain.aktif:
            return False
        cx1 = self.x + self.lebar / 2 + self.offset_x
        cy1 = self.y + self.tinggi / 2 + self.offset_y
        cx2 = sprite_lain.x + sprite_lain.lebar / 2 + sprite_lain.offset_x
        cy2 = sprite_lain.y + sprite_lain.tinggi / 2 + sprite_lain.offset_y
        dx = cx1 - cx2
        dy = cy1 - cy2
        r = self.radius + sprite_lain.radius
        return dx * dx + dy * dy < r * r

    def cek_titik(self, px, py):
        """Cek apakah titik berada di dalam sprite."""
        ax, ay, aw, ah = self._rect_collider()
        return ax <= px <= ax + aw and ay <= py <= ay + ah

    def di_dalam_bounds(self, lebar_layar, tinggi_layar):
        return (0 <= self.x and self.x + self.lebar <= lebar_layar and
                0 <= self.y and self.y + self.tinggi <= tinggi_layar)

    def arah_ke(self, x, y, kecepatan=100):
        """Set kecepatan menuju titik (x, y)."""
        dx = x - self.x
        dy = y - self.y
        j = math.hypot(dx, dy)
        if j > 0:
            self.kecepatan_x = (dx / j) * kecepatan
            self.kecepatan_y = (dy / j) * kecepatan

    def jarak_ke(self, x, y):
        return math.hypot(x - self.x, y - self.y)

    def ke_awal(self, x, y):
        """Kembalikan ke posisi awal (reset gerak)."""
        self.x = float(x)
        self.y = float(y)
        self.kecepatan_x = 0.0
        self.kecepatan_y = 0.0
        return self

    # ---------------- Patroli Waypoint (v6.6) ----------------

    def ikuti_patroli(self, titik_titik, kecepatan=100.0, mode="loop"):
        """Mulai patroli antar waypoint — posisi sprite mengikuti jalur.

        Args:
            titik_titik: List koordinat (x, y) yang dilewati berurutan.
            kecepatan: Kecepatan gerak (pixel/detik).
            mode: "loop" (ulang), "bolak-balik" (ping-pong), atau "sekali".

        Contoh:
            penjaga.ikuti_patroli([(100, 100), (500, 100), (500, 400)],
                                  kecepatan=120, mode="bolak-balik")
        """
        from brolang.stdlib.jalur import Patroli

        self._patroli = Patroli(titik_titik, kecepatan=kecepatan, mode=mode)
        self.x, self.y = self._patroli.posisi()
        return self

    def berhenti_patroli(self):
        """Hentikan patroli (posisi tetap di tempat)."""
        self._patroli = None
        return self

    def patroli_aktif(self):
        """Cek apakah sprite sedang patroli."""
        return self._patroli is not None

    def rotasi_ke_titik(self, x, y):
        """Putar sprite menghadap titik (x, y) — set sudut derajat (v6.6)."""
        self.sudut = math.degrees(math.atan2(y - self.y, x - self.x))
        return self

    def tampilkan(self):
        """Tampilkan sprite (terlihat=True)."""
        self.terlihat = True
        return self

    def sembunyikan(self):
        """Sembunyikan sprite (terlihat=False)."""
        self.terlihat = False
        return self


class GrupSprite:
    """Grup untuk mengelola banyak sprite."""

    def __init__(self):
        self.sprites = []

    def tambah(self, *sprites):
        for s in sprites:
            if s not in self.sprites:
                self.sprites.append(s)
        return self

    def hapus_sprite(self, sprite_obj):
        if sprite_obj in self.sprites:
            self.sprites.remove(sprite_obj)

    def hapus(self, sprite_obj):
        """Alias Python untuk hapus_sprite() (nama 'hapus' tabrakan keyword)."""
        self.hapus_sprite(sprite_obj)

    def hapus_tidak_aktif(self):
        self.sprites = [s for s in self.sprites if s.aktif]

    def update(self, dt):
        for s in self.sprites:
            s.update(dt)

    def gambar(self, screen, kamera=None):
        for s in sorted(self.sprites, key=lambda sp: sp.z):
            s.gambar(screen, kamera=kamera)

    def cek_tabrakan(self, sprite_lain):
        return [s for s in self.sprites if s.cek_tabrakan(sprite_lain)]

    def cek_tabrakan_grup(self, grup_lain):
        return [(a, b) for a in self.sprites
                for b in grup_lain.sprites if a.cek_tabrakan(b)]

    def jumlah(self):
        return len(self.sprites)

    def apakah_kosong(self):
        return len(self.sprites) == 0

    def kosong(self):
        """Alias Python untuk apakah_kosong() (nama 'kosong' tabrakan keyword)."""
        return self.apakah_kosong()

    def kosongkan(self):
        self.sprites.clear()

    def dapatkan_semua(self):
        return self.sprites[:]

    def pertama(self):
        return self.sprites[0] if self.sprites else None


module = SimpleNamespace(
    Sprite=Sprite,
    GrupSprite=GrupSprite,
)
