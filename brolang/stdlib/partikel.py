"""
Modul Partikel untuk BroLang Game Development
=============================================

Sistem partikel untuk efek visual: ledakan, asap, hujan, bintang,
semburan air, dll.

Contoh:
    impor partikel

    # Emiter partikel di posisi (400, 300)
    buat ledakan = partikel.PartikelEmiter(400, 300)
    ledakan.jumlah = 50
    ledakan.kecepatan = 200
    ledakan.umur = 1.0
    ledakan.warna = "jingga"

    # Tiap frame:
    ledakan.update(dt)
    ledakan.gambar(screen)

    # Emisi manual saat event terjadi:
    ledakan.ledak(400, 300, 30)
"""

import math
import random
from types import SimpleNamespace

try:
    import pygame
except ImportError:
    pygame = None


def _resolve_warna(warna):
    """Konversi nama warna / tuple ke tuple RGB."""
    if isinstance(warna, str):
        palette = {
            "putih": (255, 255, 255), "hitam": (0, 0, 0),
            "merah": (255, 60, 60), "hijau": (60, 255, 90),
            "biru": (80, 140, 255), "kuning": (255, 220, 60),
            "jingga": (255, 150, 40), "ungu": (170, 90, 255),
            "cyan": (60, 220, 255), "pink": (255, 90, 180),
            "magenta": (255, 60, 255), "coklat": (160, 100, 60),
            "abu-abu": (150, 150, 150), "emas": (255, 215, 0),
            "hijau_gelap": (40, 120, 60), "merah_gelap": (160, 30, 30),
        }
        return palette.get(warna, (255, 255, 255))
    return tuple(warna)


class Partikel:
    """Satu partikel individual."""

    __slots__ = ('x', 'y', 'vx', 'vy', 'umur', 'umur_max',
                 'ukuran', 'ukuran_awal', 'warna', 'gravitasi',
                 'gesekan', 'memudar', 'mengecil', 'aktif')

    def __init__(self, x, y, vx, vy, umur, ukuran, warna,
                 gravitasi=0.0, gesekan=0.0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.umur = 0.0
        self.umur_max = umur
        self.ukuran = ukuran
        self.ukuran_awal = ukuran
        self.warna = _resolve_warna(warna)
        self.gravitasi = gravitasi
        self.gesekan = gesekan
        self.memudar = True
        self.mengecil = True
        self.aktif = True

    def update(self, dt):
        """Update posisi partikel."""
        if not self.aktif:
            return False
        self.umur += dt
        if self.umur >= self.umur_max:
            self.aktif = False
            return False

        self.vy += self.gravitasi * dt
        if self.gesekan > 0:
            faktor = max(0.0, 1.0 - self.gesekan * dt)
            self.vx *= faktor
            self.vy *= faktor
        self.x += self.vx * dt
        self.y += self.vy * dt
        return True

    def alpha_sekarang(self):
        """Alpha 0..255 berdasarkan sisa umur."""
        sisa = 1.0 - self.umur / self.umur_max
        return int(max(0.0, min(1.0, sisa)) * 255)

    def ukuran_sekarang(self):
        """Ukuran saat ini (mengecil jika mengecil=True)."""
        if not self.mengecil:
            return self.ukuran
        sisa = 1.0 - self.umur / self.umur_max
        return max(1, int(self.ukuran_awal * sisa))


class PartikelEmiter:
    """Emiter partikel yang memproduksi & mengelola partikel."""

    def __init__(self, x=0, y=0):
        self.x = float(x)
        self.y = float(y)
        self.partikel = []           # list Partikel aktif
        self.aktif = True
        self.emisi_per_detik = 20    # 0 = tidak emisi otomatis
        self._akumulator = 0.0

        # Konfigurasi partikel baru
        self.jumlah = 10             # untuk ledak()/sembur()
        self.kecepatan = 100.0
        self.kecepatan_bervariasi = 0.5   # 0..1 random spread
        self.umur = 1.0
        self.umur_bervariasi = 0.3
        self.ukuran = 4
        self.ukuran_bervariasi = 0.5
        self.warna = "putih"
        self.gravitasi = 0.0         # contoh: 300 = jatuh ke bawah
        self.gesekan = 0.0
        self.sudut_mulai = 0.0       # derajat, 0 = ke kanan
        self.sudut_rentang = 360.0   # lebar sudut emisi (360 = semua arah)
        self.memudar = True
        self.mengecil = True

    # ---------------- Emisi ----------------

    def _buat_partikel(self):
        """Membuat satu partikel dengan konfigurasi emiter."""
        spread = random.uniform(0, 1) * self.kecepatan_bervariasi
        kecepatan = self.kecepatan * (1.0 - spread + random.uniform(0, 0.2))
        sudut_rad = math.radians(
            self.sudut_mulai + random.uniform(0, self.sudut_rentang))
        vx = math.cos(sudut_rad) * kecepatan
        vy = math.sin(sudut_rad) * kecepatan

        umur = self.umur * random.uniform(1.0 - self.umur_bervariasi,
                                          1.0 + self.umur_bervariasi)
        ukuran = self.ukuran * random.uniform(1.0 - self.ukuran_bervariasi,
                                              1.0 + self.ukuran_bervariasi)

        p = Partikel(self.x, self.y, vx, vy, max(umur, 0.05),
                     max(ukuran, 1), self.warna,
                     self.gravitasi, self.gesekan)
        p.memudar = self.memudar
        p.mengecil = self.mengecil
        return p

    def emitir(self, jumlah=None):
        """Emitir partikel di posisi emiter sekarang."""
        n = int(jumlah if jumlah is not None else self.jumlah)
        for _ in range(n):
            self.partikel.append(self._buat_partikel())
        return self

    def ledak(self, x=None, y=None, jumlah=None):
        """Ledakan partikel ke segala arah di posisi (x, y).

        Contoh:
            emiter.ledak(400, 300, 40)
        """
        if x is not None:
            self.x = float(x)
        if y is not None:
            self.y = float(y)
        self.sudut_mulai = 0.0
        self.sudut_rentang = 360.0
        return self.emitir(jumlah)

    def sembur(self, x=None, y=None, jumlah=None, sudut=90, rentang=30):
        """Semburan partikel ke satu arah (default: ke bawah, sudut 90 derajat)."""
        if x is not None:
            self.x = float(x)
        if y is not None:
            self.y = float(y)
        self.sudut_mulai = sudut - rentang / 2
        self.sudut_rentang = rentang
        return self.emitir(jumlah)

    def hujan(self, lebar_layar, jumlah=None, kecepatan=300):
        """Emisi partikel jatuh dari atas layar."""
        n = int(jumlah if jumlah is not None else self.jumlah)
        for _ in range(n):
            p = Partikel(random.uniform(0, lebar_layar), random.uniform(-20, -5),
                         0.0, kecepatan, self.umur, self.ukuran, self.warna,
                         self.gravitasi, self.gesekan)
            p.memudar = self.memudar
            p.mengecil = self.mengecil
            self.partikel.append(p)
        return self

    # ---------------- Update & Gambar ----------------

    def update(self, dt):
        """Update semua partikel + emisi otomatis."""
        if self.aktif and self.emisi_per_detik > 0:
            self._akumulator += self.emisi_per_detik * dt
            while self._akumulator >= 1:
                self._akumulator -= 1
                self.partikel.append(self._buat_partikel())

        # Update & filter partikel mati
        hidup = []
        for p in self.partikel:
            if p.update(dt):
                hidup.append(p)
        self.partikel = hidup
        return len(self.partikel)

    def gambar(self, screen, kamera=None):
        """Gambar semua partikel.

        Fade diterapkan dengan blend ke warna gelap (bukan alpha) karena
        pygame.draw.circle mengabaikan alpha pada display surface biasa.
        """
        if pygame is None:
            return
        for p in self.partikel:
            gx, gy = p.x, p.y
            if kamera is not None:
                gx, gy = kamera.world_to_screen(gx, gy)
            ukuran = p.ukuran_sekarang()
            if ukuran < 1:
                continue
            warna = p.warna
            if p.memudar:
                sisa = p.alpha_sekarang() / 255.0
                # Blend ke hitam agar memudar terlihat di surface biasa
                warna = (int(warna[0] * sisa),
                         int(warna[1] * sisa),
                         int(warna[2] * sisa))
            pygame.draw.circle(screen, warna, (int(gx), int(gy)), int(ukuran))

    def jumlah_aktif(self):
        """Jumlah partikel yang masih hidup."""
        return len(self.partikel)

    def kosongkan(self):
        """Hapus semua partikel."""
        self.partikel.clear()


def buat_emiter(x=0, y=0):
    """Membuat partikel emiter baru."""
    return PartikelEmiter(x, y)


def buat(x=0, y=0):
    return PartikelEmiter(x, y)


def buat_ledakan(x, y, jumlah=30, warna="jingga", kecepatan=250):
    """Membuat emiter sekali-pakai untuk ledakan instan."""
    e = PartikelEmiter(x, y)
    e.jumlah = jumlah
    e.kecepatan = kecepatan
    e.warna = warna
    e.emisi_per_detik = 0
    e.ledak(x, y, jumlah)
    return e


def buat_hujan(lebar_layar, jumlah=50, warna="biru"):
    """Membuat emiter hujan otomatis."""
    e = PartikelEmiter(0, 0)
    e.jumlah = jumlah
    e.warna = warna
    e.gravitasi = 0
    e.emisi_per_detik = 0
    e.hujan(lebar_layar, jumlah, kecepatan=350)
    return e


module = SimpleNamespace(
    Partikel=Partikel,
    PartikelEmiter=PartikelEmiter,
    buat_emiter=buat_emiter,
    buat_ledakan=buat_ledakan,
    buat_hujan=buat_hujan,
)
