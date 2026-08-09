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
                 'gesekan', 'memudar', 'mengecil', 'aktif',
                 'gambar', 'warna_awal', 'warna_akhir')

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
        # v6.6: tekstur & gradien warna seumur hidup
        self.gambar = None
        self.warna_awal = None   # tuple RGB untuk gradien
        self.warna_akhir = None  # tuple RGB untuk gradien

    def warna_sekarang(self):
        """Warna saat ini (interpolasi gradien jika warna_awal/akhir diset)."""
        if self.warna_awal is not None and self.warna_akhir is not None:
            t = min(max(self.umur / self.umur_max, 0.0), 1.0)
            a = self.warna_awal
            b = self.warna_akhir
            return (int(a[0] + (b[0] - a[0]) * t),
                    int(a[1] + (b[1] - a[1]) * t),
                    int(a[2] + (b[2] - a[2]) * t))
        return self.warna

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
        # v6.6: tekstur & gradien warna
        self.gambar_tekstur = None   # Surface / path gambar
        self.warna_awal = None       # tuple RGB (gradien mulai)
        self.warna_akhir = None      # tuple RGB (gradien selesai)

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
        if self.gambar_tekstur is not None:
            p.gambar = self.gambar_tekstur
        if self.warna_awal is not None:
            p.warna_awal = _resolve_warna(self.warna_awal)
        if self.warna_akhir is not None:
            p.warna_akhir = _resolve_warna(self.warna_akhir)
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
        """Gambar semua partikel (tekstur atau lingkaran berwarna).

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
            warna = p.warna_sekarang()
            if p.memudar:
                sisa = p.alpha_sekarang() / 255.0
                # Blend ke hitam agar memudar terlihat di surface biasa
                warna = (int(warna[0] * sisa),
                         int(warna[1] * sisa),
                         int(warna[2] * sisa))
            if p.gambar is not None:
                try:
                    surf = p.gambar
                    w = max(1, int(surf.get_width() * ukuran / max(p.ukuran_awal, 1)))
                    h = max(1, int(surf.get_height() * ukuran / max(p.ukuran_awal, 1)))
                    if w != surf.get_width() or h != surf.get_height():
                        surf = pygame.transform.smoothscale(surf, (w, h))
                    if p.memudar and sisa < 1.0:
                        surf.set_alpha(max(0, min(255, int(sisa * 255))))
                    screen.blit(surf, (int(gx - w / 2), int(gy - h / 2)))
                except (pygame.error, ValueError, TypeError):
                    pygame.draw.circle(screen, warna, (int(gx), int(gy)), int(ukuran))
            else:
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


def buat_trail(x=0, y=0, warna="cyan", umur=0.4):
    """Emiter trail: partikel kecil memudar yang mengikuti posisi emiter — v6.6.

    Gerakkan emiter lewat atribut x/y (atau set ke posisi objek tiap frame),
    lalu update + gambar seperti biasa.
    """
    e = PartikelEmiter(x, y)
    e.jumlah = 3
    e.kecepatan = 5
    e.kecepatan_bervariasi = 0.5
    e.umur = umur
    e.ukuran = 6
    e.ukuran_bervariasi = 0.4
    e.warna = warna
    e.gravitasi = 0
    e.gesekan = 0
    e.emisi_per_detik = 40
    e.memudar = True
    e.mengecil = True
    return e


def buat_asap(x=0, y=0, warna="abu-abu", umur=1.4):
    """Emiter asap: naik pelan, membesar, memudar — v6.6."""
    e = PartikelEmiter(x, y)
    e.jumlah = 2
    e.kecepatan = 25
    e.kecepatan_bervariasi = 0.6
    e.umur = umur
    e.umur_bervariasi = 0.3
    e.ukuran = 10
    e.ukuran_bervariasi = 0.5
    e.warna = warna
    e.gravitasi = -30          # naik ke atas
    e.gesekan = 0.5
    e.sudut_mulai = 270        # ke atas
    e.sudut_rentang = 40
    e.emisi_per_detik = 15
    e.warna_awal = (170, 170, 170)
    e.warna_akhir = (90, 90, 90)
    return e


def buat_bintang(x=0, y=0, warna="emas"):
    """Emiter percikan bintang (sparkle) — v6.6."""
    e = PartikelEmiter(x, y)
    e.jumlah = 12
    e.kecepatan = 160
    e.kecepatan_bervariasi = 0.7
    e.umur = 0.7
    e.umur_bervariasi = 0.4
    e.ukuran = 3
    e.ukuran_bervariasi = 0.5
    e.warna = warna
    e.gravitasi = 40
    e.gesekan = 0.3
    e.emisi_per_detik = 0
    e.ledak(x, y, 12)
    return e


module = SimpleNamespace(
    Partikel=Partikel,
    PartikelEmiter=PartikelEmiter,
    buat_emiter=buat_emiter,
    buat_ledakan=buat_ledakan,
    buat_hujan=buat_hujan,
    buat_trail=buat_trail,
    buat_asap=buat_asap,
    buat_bintang=buat_bintang,
)
