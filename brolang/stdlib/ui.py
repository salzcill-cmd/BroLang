"""
Modul UI untuk BroLang Game Development
=======================================

Komponen antarmuka (UI) untuk game: Label, Tombol, Panel, dan Bar
(progress/health bar).

Komponen bersifat deklaratif — panggil `.gambar(screen)` untuk render
dan `.update(...)` untuk interaksi. Bisa dipakai tanpa pygame untuk
logika (misal cek hover), hanya render yang butuh pygame.

Contoh:
    impor ui
    impor input

    buat tombol = ui.Tombol("MULAI", 300, 250, 200, 60)
    tombol.on_klik = fungsi_mulai

    # Tiap frame:
    jika tombol.update(input.tikus_posisi()[0], input.tikus_posisi()[1],
                       input.tikus_baru_ditekan(0)) maka
        tulis "Tombol diklik!"
    selesai
    tombol.gambar(screen)
"""

from types import SimpleNamespace

try:
    import pygame
except ImportError:
    pygame = None

_FONT_CACHE = {}


def _get_font(ukuran):
    global _FONT_CACHE
    if pygame is None:
        return None
    if ukuran not in _FONT_CACHE:
        _FONT_CACHE[ukuran] = pygame.font.SysFont(None, ukuran)
    return _FONT_CACHE[ukuran]


def _resolve_warna(warna):
    """Konversi nama warna / tuple ke tuple RGB."""
    if isinstance(warna, str):
        palette = {
            "putih": (255, 255, 255), "hitam": (0, 0, 0),
            "merah": (220, 60, 60), "hijau": (60, 200, 90),
            "biru": (70, 130, 255), "kuning": (255, 220, 60),
            "jingga": (255, 150, 40), "ungu": (170, 90, 255),
            "cyan": (60, 220, 255), "pink": (255, 90, 180),
            "magenta": (255, 60, 255), "coklat": (160, 100, 60),
            "abu-abu": (150, 150, 150), "emas": (255, 215, 0),
            "hijau_gelap": (40, 120, 60), "biru_gelap": (30, 40, 100),
            "merah_gelap": (160, 30, 30), "abu-abu_gelap": (50, 50, 50),
            "abu-abu_terang": (200, 200, 200), "langit": (135, 206, 235),
        }
        return palette.get(warna, (255, 255, 255))
    return tuple(warna)


class Label:
    """Teks statis di layar."""

    def __init__(self, teks, x=0, y=0, warna="putih", ukuran=24,
                 tengah=False):
        self.teks = str(teks)
        self.x = float(x)
        self.y = float(y)
        self.warna = _resolve_warna(warna)
        self.ukuran = ukuran
        self.tengah = tengah
        self.terlihat = True

    def set_teks(self, teks):
        """Ubah isi teks."""
        self.teks = str(teks)
        return self

    def gambar(self, screen):
        """Gambar label ke layar."""
        if not self.terlihat or pygame is None:
            return
        font = _get_font(int(self.ukuran))
        if font is None:
            return
        surf = font.render(self.teks, True, self.warna)
        gx = int(self.x)
        if self.tengah:
            gx = int(self.x) - surf.get_width() // 2
        screen.blit(surf, (gx, int(self.y)))

    def ukuran_teks(self):
        """Ukuran teks (lebar, tinggi)."""
        font = _get_font(int(self.ukuran))
        if font is None:
            return (0, 0)
        return font.size(self.teks)


class Panel:
    """Kotak latar belakang (dengan sudut membulat opsional)."""

    def __init__(self, x, y, lebar, tinggi, warna="abu-abu_gelap",
                 radius=0, alpha=None):
        self.x = float(x)
        self.y = float(y)
        self.lebar = lebar
        self.tinggi = tinggi
        self.warna = _resolve_warna(warna)
        self.radius = max(0, int(radius))
        self.alpha = alpha  # None = tidak transparan
        self.terlihat = True

    def gambar(self, screen):
        """Gambar panel ke layar."""
        if not self.terlihat or pygame is None:
            return
        warna = self.warna
        if self.alpha is not None:
            surf = pygame.Surface((int(self.lebar), int(self.tinggi)),
                                  pygame.SRCALPHA)
            pygame.draw.rect(surf, (*warna, int(self.alpha)),
                             (0, 0, int(self.lebar), int(self.tinggi)),
                             border_radius=self.radius)
            screen.blit(surf, (int(self.x), int(self.y)))
        else:
            pygame.draw.rect(screen, warna,
                             (int(self.x), int(self.y),
                              int(self.lebar), int(self.tinggi)),
                             border_radius=self.radius)

    def berisi(self, px, py):
        """Cek apakah titik berada di dalam panel."""
        return (self.x <= px <= self.x + self.lebar and
                self.y <= py <= self.y + self.tinggi)


class Tombol:
    """Tombol interaktif dengan hover, klik, dan callback.

    Contoh:
        buat tombol = ui.Tombol("MULAI", 300, 250, 200, 60)
        tombol.on_klik = fungsi_mulai

        # Tiap frame (biasanya di scene update):
        jika tombol.update(input.tikus_posisi()[0], input.tikus_posisi()[1],
                           input.tikus_baru_ditekan(0)) maka
            tulis "Klik terdeteksi"
        selesai
        # Gambar di scene gambar:
        tombol.gambar(screen)
    """

    def __init__(self, teks, x, y, lebar, tinggi,
                 warna="biru", warna_hover="biru_gelap",
                 warna_teks="putih", ukuran_teks=None):
        self.teks = str(teks)
        self.x = float(x)
        self.y = float(y)
        self.lebar = lebar
        self.tinggi = tinggi
        self.warna = _resolve_warna(warna)
        self.warna_hover = _resolve_warna(warna_hover)
        self.warna_teks = _resolve_warna(warna_teks)
        self.ukuran_teks = ukuran_teks or max(16, int(tinggi * 0.5))
        self.terlihat = True
        self.aktif = True
        self.hover = False
        self.ditekan = False
        self.radius = 10
        self.on_klik = None     # callback tanpa argumen
        self.on_hover = None    # callback saat mouse masuk
        self.on_keluar = None   # callback saat mouse keluar
        self.on_klik_kanan = None
        self.ketuk_berat = None  # SimpleNamespace(on_klik=...) custom

    def berisi(self, px, py):
        """Cek apakah titik berada di dalam tombol."""
        return (self.x <= px <= self.x + self.lebar and
                self.y <= py <= self.y + self.tinggi)

    def update(self, tikus_x, tikus_y, diklik=False):
        """Update state hover & deteksi klik.

        Args:
            tikus_x, tikus_y: Posisi mouse.
            diklik: True jika tombol mouse kiri baru ditekan frame ini.

        Returns:
            True jika tombol diklik frame ini.
        """
        if not self.aktif or not self.terlihat:
            self.hover = False
            return False

        sebelumnya = self.hover
        self.hover = self.berisi(tikus_x, tikus_y)
        if self.hover and not sebelumnya and self.on_hover:
            self.on_hover()
        if not self.hover and sebelumnya and self.on_keluar:
            self.on_keluar()

        if diklik and self.hover:
            self.ditekan = True
            if self.on_klik:
                self.on_klik()
            return True
        self.ditekan = False
        return False

    def klik_kanan(self, tikus_x, tikus_y, diklik_kanan=False):
        """Deteksi klik kanan. Kembalikan True jika klik kanan di dalam tombol."""
        if diklik_kanan and self.berisi(tikus_x, tikus_y):
            if self.on_klik_kanan:
                self.on_klik_kanan()
            return True
        return False

    def gambar(self, screen):
        """Gambar tombol ke layar."""
        if not self.terlihat or pygame is None:
            return
        warna = self.warna_hover if self.hover else self.warna
        pygame.draw.rect(screen, warna,
                         (int(self.x), int(self.y),
                          int(self.lebar), int(self.tinggi)),
                         border_radius=self.radius)
        if self.ditekan:
            pygame.draw.rect(screen, (255, 255, 255),
                             (int(self.x), int(self.y),
                              int(self.lebar), int(self.tinggi)), 2,
                             border_radius=self.radius)
        font = _get_font(int(self.ukuran_teks))
        if font is None:
            return
        surf = font.render(self.teks, True, self.warna_teks)
        gx = int(self.x + (self.lebar - surf.get_width()) / 2)
        gy = int(self.y + (self.tinggi - surf.get_height()) / 2)
        screen.blit(surf, (gx, gy))


class Bar:
    """Bar pengukur: health bar, progress bar, mana bar, dll.

    Contoh:
        buat hp = ui.Bar(100, 100, 20, 200, 20, warna_isi="hijau",
                         warna_latar="merah_gelap")
        hp.set_nilai(50)     # set langsung
        hp.kurang(10)        # kurangi 10
        hp.tambah(5)         # tambah 5
        hp.gambar(screen)
    """

    def __init__(self, nilai, maks, x, y, lebar, tinggi,
                 warna_isi="hijau", warna_latar="abu-abu_gelap",
                 warna_teks=None, tampil_teks=True, arah="kiri"):
        self.nilai = float(nilai)
        self.maks = max(float(maks), 0.0001)
        self.x = float(x)
        self.y = float(y)
        self.lebar = lebar
        self.tinggi = tinggi
        self.warna_isi = _resolve_warna(warna_isi)
        self.warna_latar = _resolve_warna(warna_latar)
        self.warna_teks = _resolve_warna(warna_teks) if warna_teks else None
        self.tampil_teks = tampil_teks
        self.arah = arah  # "kiri" atau "kanan"
        self.radius = max(1, int(tinggi / 2))
        self.terlihat = True

    def set_nilai(self, nilai):
        """Set nilai bar (di-clamp 0..maks)."""
        self.nilai = max(0.0, min(float(nilai), self.maks))
        return self

    def tambah(self, jumlah):
        """Tambahkan nilai."""
        return self.set_nilai(self.nilai + jumlah)

    def kurang(self, jumlah):
        """Kurangi nilai."""
        return self.set_nilai(self.nilai - jumlah)

    def set_maks(self, maks):
        """Ubah nilai maksimum."""
        self.maks = max(float(maks), 0.0001)
        self.nilai = min(self.nilai, self.maks)
        return self

    def persen(self) -> float:
        """Persentase 0.0 .. 1.0."""
        return self.nilai / self.maks

    def habis(self) -> bool:
        """Cek apakah nilai bar habis (0)."""
        return self.nilai <= 0

    def kosong(self) -> bool:
        """Alias Python untuk habis() (nama 'kosong' tabrakan keyword)."""
        return self.nilai <= 0

    def penuh(self) -> bool:
        return self.nilai >= self.maks

    def gambar(self, screen):
        """Gambar bar ke layar."""
        if not self.terlihat or pygame is None:
            return
        pygame.draw.rect(screen, self.warna_latar,
                         (int(self.x), int(self.y),
                          int(self.lebar), int(self.tinggi)),
                         border_radius=self.radius)
        p = self.persen()
        if p > 0:
            isi_lebar = int(self.lebar * p)
            if isi_lebar >= self.radius * 2:
                pygame.draw.rect(screen, self.warna_isi,
                                 (int(self.x), int(self.y),
                                  isi_lebar, int(self.tinggi)),
                                 border_radius=self.radius)
            else:
                # Terlalu tipis untuk rounded -> persegi
                pygame.draw.rect(screen, self.warna_isi,
                                 (int(self.x), int(self.y),
                                  isi_lebar, int(self.tinggi)))
        if self.tampil_teks:
            font = _get_font(max(10, int(self.tinggi * 0.6)))
            if font is not None:
                warna = self.warna_teks or (255, 255, 255)
                surf = font.render(f"{int(self.nilai)}/{int(self.maks)}",
                                   True, warna)
                gx = int(self.x + (self.lebar - surf.get_width()) / 2)
                gy = int(self.y + (self.tinggi - surf.get_height()) / 2)
                screen.blit(surf, (gx, gy))


module = SimpleNamespace(
    Label=Label,
    Panel=Panel,
    Tombol=Tombol,
    Bar=Bar,
)
