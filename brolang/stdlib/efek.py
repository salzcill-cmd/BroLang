"""
Modul Efek untuk BroLang Game Development (v6.6)
================================================

Efek visual instan: flash layar, vignette, teks melayang (damage number),
dan gelombang pulsa.

Contoh:
    impor efek

    # Flash putih singkat saat pemain kena damage
    buat kilat = efek.buat_flash("putih", durasi=0.15)
    kilat.update(dt)
    kilat.gambar(screen)

    # Damage number yang naik & memudar
    buat teks = efek.TeksMelayang("-25", musuh.x, musuh.y, warna="merah")
    teks.update(dt)
    teks.gambar(screen)
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
            "hijau_gelap": (40, 120, 60), "biru_gelap": (30, 40, 100),
            "merah_gelap": (160, 30, 30), "abu-abu_gelap": (50, 50, 50),
            "langit": (135, 206, 235),
        }
        return palette.get(warna, (255, 255, 255))
    return tuple(warna)


class Flash:
    """Kilatan layar penuh yang memudar seiring waktu.

    Contoh:
        buat kilat = efek.Flash("putih", durasi=0.2, kekuatan=160)
        kilat.picu()          # nyalakan (ulang dari awal)
        kilat.update(dt)      # tiap frame
        kilat.gambar(screen)  # gambar overlay
    """

    def __init__(self, warna="putih", durasi=0.2, kekuatan=180):
        self.warna = _resolve_warna(warna)
        self.durasi = max(0.01, float(durasi))
        self.kekuatan = max(0, min(int(kekuatan), 255))
        self.waktu = self.durasi  # langsung menyala saat dibuat
        self.terlihat = True

    def picu(self):
        """Nyalakan flash (restart)."""
        self.waktu = self.durasi
        return self

    def update(self, dt):
        """Kurangi sisa waktu. Kembalikan False jika sudah habis."""
        if self.waktu > 0:
            self.waktu -= dt
            if self.waktu <= 0:
                self.waktu = 0.0
                return False
        return self.waktu > 0

    def aktif(self):
        """Cek apakah flash masih menyala."""
        return self.waktu > 0

    def alpha(self):
        """Alpha overlay saat ini 0..255."""
        if self.waktu <= 0:
            return 0
        sisa = max(0.0, min(self.waktu / self.durasi, 1.0))
        return int(self.kekuatan * sisa)

    def gambar(self, screen):
        """Gambar overlay flash di atas layar."""
        if not self.terlihat or pygame is None or self.waktu <= 0:
            return
        alpha = self.alpha()
        if alpha <= 0:
            return
        try:
            lebar, tinggi = screen.get_size()
            overlay = pygame.Surface((lebar, tinggi), pygame.SRCALPHA)
            overlay.fill((*self.warna, alpha))
            screen.blit(overlay, (0, 0))
        except (pygame.error, ValueError, TypeError):
            pass


class Vignette:
    """Vignette statis di tepi layar (gelap di sudut).

    Contoh:
        buat vin = efek.Vignette(kekuatan=0.5)
        vin.gambar(screen)   # tiap frame setelah scene digambar
    """

    def __init__(self, kekuatan=0.5, radius=None, warna="hitam"):
        self.kekuatan = max(0.0, min(float(kekuatan), 1.0))
        self.radius = radius  # None = auto dari ukuran layar
        self.warna = _resolve_warna(warna)
        self.terlihat = True
        self._cache = None   # (ukuran, surface) cache vignette

    def atur_kekuatan(self, kekuatan):
        """Ubah kekuatan vignette 0.0..1.0."""
        self.kekuatan = max(0.0, min(float(kekuatan), 1.0))
        self._cache = None

    def gambar(self, screen):
        """Gambar vignette. Cache surface per ukuran layar."""
        if not self.terlihat or pygame is None or self.kekuatan <= 0:
            return
        try:
            lebar, tinggi = screen.get_size()
            if self._cache is None or self._cache[0] != (lebar, tinggi):
                self._cache = ((lebar, tinggi), self._buat_surface(lebar, tinggi))
            _, surf = self._cache
            screen.blit(surf, (0, 0))
        except (pygame.error, ValueError, TypeError):
            pass

    def _buat_surface(self, lebar, tinggi):
        """Buat surface vignette radial-gradient."""
        radius = self.radius or max(lebar, tinggi) * 0.75
        kekuatan = self.kekuatan
        surf = pygame.Surface((lebar, tinggi), pygame.SRCALPHA)
        langkah = 24
        for i in range(langkah):
            r = radius * (1.0 - i / langkah)
            a = int(255 * kekuatan * (1.0 - i / langkah))
            if a <= 0:
                break
            pygame.draw.circle(surf, (*self.warna, a), (lebar // 2, tinggi // 2), int(r))
        return surf


class TeksMelayang:
    """Teks yang naik & memudar — damage number, skor, dll.

    Contoh:
        buat dmg = efek.TeksMelayang("-25", 100, 100, warna="merah",
                                     ukuran=28, kecepatan_naik=50)
        dmg.update(dt)
        dmg.gambar(screen)
    """

    def __init__(self, teks, x, y, warna="kuning", ukuran=24,
                 kecepatan_naik=45, durasi=1.0, acak_x=0):
        self.teks = str(teks)
        self.x = float(x) + random.uniform(-acak_x, acak_x)
        self.y = float(y)
        self.warna = _resolve_warna(warna)
        self.ukuran = ukuran
        self.kecepatan_naik = float(kecepatan_naik)
        self.durasi = max(0.05, float(durasi))
        self.waktu = 0.0
        self.terlihat = True

    def update(self, dt):
        """Naikkan posisi & tambah umur. Kembalikan False jika selesai."""
        self.waktu += dt
        self.y -= self.kecepatan_naik * dt
        if self.waktu >= self.durasi:
            self.waktu = self.durasi
            return False
        return True

    def selesai(self):
        """Cek apakah teks sudah selesai melayang."""
        return self.waktu >= self.durasi

    def alpha(self):
        """Alpha 0..255 berdasarkan sisa umur."""
        sisa = 1.0 - self.waktu / self.durasi
        return int(max(0.0, min(1.0, sisa)) * 255)

    def gambar(self, screen):
        """Gambar teks melayang."""
        if not self.terlihat or pygame is None or self.selesai():
            return
        try:
            font = pygame.font.SysFont(None, int(self.ukuran))
            surf = font.render(self.teks, True, self.warna)
            surf.set_alpha(self.alpha())
            rect = surf.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(surf, rect)
        except (pygame.error, ValueError, TypeError):
            pass


class Pulsa:
    """Gelombang cincin yang membesar & memudar.

    Contoh:
        buat gel = efek.Pulsa(400, 300, radius_akhir=100, durasi=0.5,
                              warna="cyan")
        gel.update(dt)
        gel.gambar(screen)
    """

    def __init__(self, x, y, radius_akhir=80, durasi=0.6, warna="cyan",
                 ketebalan=3):
        self.x = float(x)
        self.y = float(y)
        self.radius_akhir = max(1.0, float(radius_akhir))
        self.durasi = max(0.01, float(durasi))
        self.warna = _resolve_warna(warna)
        self.ketebalan = max(1, int(ketebalan))
        self.waktu = 0.0
        self.terlihat = True

    def update(self, dt):
        """Perbesar cincin. Kembalikan False jika selesai."""
        self.waktu += dt
        if self.waktu >= self.durasi:
            self.waktu = self.durasi
            return False
        return True

    def selesai(self):
        return self.waktu >= self.durasi

    def radius_sekarang(self):
        """Radius cincin saat ini (dengan easing keluar)."""
        p = min(self.waktu / self.durasi, 1.0)
        return self.radius_akhir * (1.0 - (1.0 - p) ** 2)

    def gambar(self, screen):
        """Gambar cincin pulsa."""
        if not self.terlihat or pygame is None or self.selesai():
            return
        try:
            r = int(self.radius_sekarang())
            if r <= 0:
                return
            sisa = 1.0 - self.waktu / self.durasi
            alpha = int(max(0.0, min(1.0, sisa)) * 255)
            surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*self.warna, alpha),
                               (r + 2, r + 2), r, self.ketebalan)
            screen.blit(surf, (int(self.x) - r - 2, int(self.y) - r - 2))
        except (pygame.error, ValueError, TypeError):
            pass


class Guncangan:
    """Screen shake berbasis trauma (v6.7).

    Menggunakan model trauma klasik ala game: tiap guncangan menambah
    trauma, lalu trauma memudar eksponensial seiring waktu. Offset kamera
    dihitung dari trauma * acak(searah waktu). Makin sering diguncang,
    makin keras getarannya — lalu reda sendiri.

    Contoh:
        buat getar = efek.Guncangan(kekuatan_maks=20)

        # tiap frame:
        getar.update(dt)
        ox, oy = getar.offset()
        kamera.gerak(ox, oy)          # geser kamera
        # atau gambar semua di offset manual

        # saat pemain kena damage:
        getar.guncang(0.8)            # kuat
        getar.guncang(0.3)            # getar tambahan (menumpuk)

        # cek apakah sudah reda:
        jika getar.selesai() maka ...
    """

    def __init__(self, kekuatan_maks=16, peluruhan=1.8, durasi=1.0):
        """
        Args:
            kekuatan_maks: Offset pixel maksimum (dipengaruhi trauma).
            peluruhan: Kecepatan trauma memudar (semakin besar makin cepat reda).
            durasi: Lama getaran maksimum dalam detik (keamanan anti-takberujung).
        """
        self.kekuatan_maks = max(0.0, float(kekuatan_maks))
        self.peluruhan = max(0.1, float(peluruhan))
        self.durasi = max(0.05, float(durasi))
        self.trauma = 0.0
        self.waktu = 0.0
        self.terlihat = True
        self._seed = random.random() * 1000

    def guncang(self, kekuatan=1.0):
        """Tambahkan guncangan. kekuatan 0.0..1.0 (boleh > 1 untuk keras)."""
        self.trauma = min(1.0, self.trauma + max(0.0, float(kekuatan)))
        self.waktu = 0.0
        return self

    def update(self, dt):
        """Kurangi trauma seiring waktu.

        Returns:
            False jika sudah reda total, True jika masih bergetar.
        """
        if self.trauma <= 0:
            return False
        self.waktu += dt
        # Peluruhan eksponensial: trauma *= e^(-peluruhan*dt)
        self.trauma = max(0.0, self.trauma * math.exp(-self.peluruhan * dt))
        if self.waktu >= self.durasi or self.trauma <= 0.001:
            self.trauma = 0.0
            return False
        return True

    def offset(self):
        """Offset (x, y) yang harus digeserkan — konsisten dalam satu frame."""
        if self.trauma <= 0:
            return (0.0, 0.0)
        # Trauma dikuadratkan agar getaran terasa "keras lalu cepat reda"
        # (rasa getaran tidak linear).
        kekuatan = self.trauma * self.trauma * self.kekuatan_maks
        # Noise 1D deterministik per frame — hindari jitter acak murni yang
        # membuat gambar "melompat-lompat" tanpa arah.
        t = self.waktu * 40.0 + self._seed
        x = math.sin(t) * kekuatan
        y = math.cos(t * 1.3) * kekuatan
        return (x, y)

    def selesai(self):
        """Cek apakah getaran sudah reda total."""
        return self.trauma <= 0.001

    def kekuatan_sekarang(self):
        """Trauma saat ini 0.0..1.0."""
        return self.trauma

    def gambar(self, screen):
        """Placeholder agar konsisten dengan efek lain (tidak menggambar apa-apa)."""
        pass


def buat_flash(warna="putih", durasi=0.2, kekuatan=180):
    """Buat flash instan yang langsung menyala."""
    return Flash(warna, durasi, kekuatan)


def buat_teks_melayang(teks, x, y, warna="kuning", ukuran=24, durasi=1.0):
    """Buat teks melayang (damage number) sekali pakai."""
    return TeksMelayang(teks, x, y, warna=warna, ukuran=ukuran, durasi=durasi)


def buat_pulsa(x, y, radius_akhir=80, durasi=0.6, warna="cyan"):
    """Buat gelombang pulsa sekali pakai."""
    return Pulsa(x, y, radius_akhir, durasi, warna)


def buat_guncangan(kekuatan_maks=16, peluruhan=1.8, durasi=1.0):
    """Buat screen shake (getaran kamera) — Guncangan (v6.7)."""
    return Guncangan(kekuatan_maks, peluruhan, durasi)


module = SimpleNamespace(
    Flash=Flash,
    Vignette=Vignette,
    TeksMelayang=TeksMelayang,
    Pulsa=Pulsa,
    Guncangan=Guncangan,
    buat_flash=buat_flash,
    buat_teks_melayang=buat_teks_melayang,
    buat_pulsa=buat_pulsa,
    buat_guncangan=buat_guncangan,
)
