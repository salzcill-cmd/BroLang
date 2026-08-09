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
            "putih": (255, 255, 255),
            "hitam": (0, 0, 0),
            "merah": (220, 60, 60),
            "hijau": (60, 200, 90),
            "biru": (70, 130, 255),
            "kuning": (255, 220, 60),
            "jingga": (255, 150, 40),
            "ungu": (170, 90, 255),
            "cyan": (60, 220, 255),
            "pink": (255, 90, 180),
            "magenta": (255, 60, 255),
            "coklat": (160, 100, 60),
            "abu-abu": (150, 150, 150),
            "emas": (255, 215, 0),
            "hijau_gelap": (40, 120, 60),
            "biru_gelap": (30, 40, 100),
            "merah_gelap": (160, 30, 30),
            "abu-abu_gelap": (50, 50, 50),
            "abu-abu_terang": (200, 200, 200),
            "langit": (135, 206, 235),
        }
        return palette.get(warna, (255, 255, 255))
    return tuple(warna)


class Label:
    """Teks statis di layar."""

    def __init__(self, teks, x=0, y=0, warna="putih", ukuran=24, tengah=False):
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

    def __init__(self, x, y, lebar, tinggi, warna="abu-abu_gelap", radius=0, alpha=None):
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
            surf = pygame.Surface((int(self.lebar), int(self.tinggi)), pygame.SRCALPHA)
            pygame.draw.rect(
                surf,
                (*warna, int(self.alpha)),
                (0, 0, int(self.lebar), int(self.tinggi)),
                border_radius=self.radius,
            )
            screen.blit(surf, (int(self.x), int(self.y)))
        else:
            pygame.draw.rect(
                screen,
                warna,
                (int(self.x), int(self.y), int(self.lebar), int(self.tinggi)),
                border_radius=self.radius,
            )

    def berisi(self, px, py):
        """Cek apakah titik berada di dalam panel."""
        return self.x <= px <= self.x + self.lebar and self.y <= py <= self.y + self.tinggi


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

    def __init__(
        self,
        teks,
        x,
        y,
        lebar,
        tinggi,
        warna="biru",
        warna_hover="biru_gelap",
        warna_teks="putih",
        ukuran_teks=None,
        gambar=None,  # v6.6: gambar latar tombol (path / Surface)
    ):
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
        self.on_klik = None  # callback tanpa argumen
        self.on_hover = None  # callback saat mouse masuk
        self.on_keluar = None  # callback saat mouse keluar
        self.on_klik_kanan = None
        self.ketuk_berat = None  # SimpleNamespace(on_klik=...) custom
        # v6.6: gambar latar (path string / Surface). Jika diset, tombol
        # digambar dari gambar (dengan overlay hover) bukan kotak warna.
        self.gambar = gambar
        self._gambar_dimuat = False

    def _muat_gambar(self):
        """Muat gambar latar (path / Surface) sekali saja."""
        if self._gambar_dimuat:
            return
        self._gambar_dimuat = True
        if self.gambar is None or pygame is None:
            return
        if isinstance(self.gambar, str):
            try:
                self.gambar = pygame.image.load(self.gambar).convert_alpha()
            except (pygame.error, FileNotFoundError, OSError):
                self.gambar = None

    def berisi(self, px, py):
        """Cek apakah titik berada di dalam tombol."""
        return self.x <= px <= self.x + self.lebar and self.y <= py <= self.y + self.tinggi

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
        if self.gambar is not None:
            # Tombol bergambar (v6.6): gambar discale ke ukuran tombol
            self._muat_gambar()
            if self.gambar is not None:
                try:
                    img = pygame.transform.smoothscale(
                        self.gambar, (int(self.lebar), int(self.tinggi)))
                    if self.hover:
                        overlay = pygame.Surface((int(self.lebar), int(self.tinggi)),
                                                 pygame.SRCALPHA)
                        overlay.fill((*self.warna_hover, 70))
                        img = img.copy()
                        img.blit(overlay, (0, 0))
                    screen.blit(img, (int(self.x), int(self.y)))
                except (pygame.error, ValueError, TypeError):
                    pygame.draw.rect(
                        screen, warna,
                        (int(self.x), int(self.y), int(self.lebar), int(self.tinggi)),
                        border_radius=self.radius,
                    )
        else:
            pygame.draw.rect(
                screen,
                warna,
                (int(self.x), int(self.y), int(self.lebar), int(self.tinggi)),
                border_radius=self.radius,
            )
        if self.ditekan:
            pygame.draw.rect(
                screen,
                (255, 255, 255),
                (int(self.x), int(self.y), int(self.lebar), int(self.tinggi)),
                2,
                border_radius=self.radius,
            )
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

    def __init__(
        self,
        nilai,
        maks,
        x,
        y,
        lebar,
        tinggi,
        warna_isi="hijau",
        warna_latar="abu-abu_gelap",
        warna_teks=None,
        tampil_teks=True,
        arah="kiri",
    ):
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
        pygame.draw.rect(
            screen,
            self.warna_latar,
            (int(self.x), int(self.y), int(self.lebar), int(self.tinggi)),
            border_radius=self.radius,
        )
        p = self.persen()
        if p > 0:
            isi_lebar = int(self.lebar * p)
            if isi_lebar >= self.radius * 2:
                pygame.draw.rect(
                    screen,
                    self.warna_isi,
                    (int(self.x), int(self.y), isi_lebar, int(self.tinggi)),
                    border_radius=self.radius,
                )
            else:
                # Terlalu tipis untuk rounded -> persegi
                pygame.draw.rect(
                    screen, self.warna_isi, (int(self.x), int(self.y), isi_lebar, int(self.tinggi))
                )
        if self.tampil_teks:
            font = _get_font(max(10, int(self.tinggi * 0.6)))
            if font is not None:
                warna = self.warna_teks or (255, 255, 255)
                surf = font.render(f"{int(self.nilai)}/{int(self.maks)}", True, warna)
                gx = int(self.x + (self.lebar - surf.get_width()) / 2)
                gy = int(self.y + (self.tinggi - surf.get_height()) / 2)
                screen.blit(surf, (gx, gy))


class KotakTeks:
    """Input teks satu baris dengan fokus, kursor berkedip, dan placeholder.

    Logika (fokus, teks) berjalan tanpa pygame — hanya render yang butuh
    pygame. Input keyboard dilakukan manual dari kode game:

    Contoh:
        impor ui
        impor input

        buat nama = ui.KotakTeks(200, 150, 250, 40, placeholder="Nama pemain")

        # Tiap frame:
        nama.update(input.tikus_posisi()[0], input.tikus_posisi()[1],
                    input.tikus_baru_ditekan(0))
        jika nama.fokus maka
            # Terima karakter dari event keyboard
            untuk ev dalam input.events_tombol() lakukan
                nama.tambah_karakter(ev)
            selesai
            jika input.tombol_baru_ditekan("BACKSPACE") maka
                nama.hapus_karakter()
            selesai
        selesai
        nama.gambar(screen)
    """

    def __init__(
        self,
        x,
        y,
        lebar,
        tinggi=40,
        teks="",
        placeholder="",
        warna="putih",
        warna_teks="hitam",
        warna_batas="abu-abu_terang",
        warna_fokus="biru",
        ukuran_teks=None,
        maks_karakter=None,
    ):
        self.x = float(x)
        self.y = float(y)
        self.lebar = lebar
        self.tinggi = tinggi
        self.teks = str(teks)
        self.placeholder = str(placeholder)
        self.warna = _resolve_warna(warna)
        self.warna_teks = _resolve_warna(warna_teks)
        self.warna_batas = _resolve_warna(warna_batas)
        self.warna_fokus = _resolve_warna(warna_fokus)
        self.ukuran_teks = ukuran_teks or max(14, int(tinggi * 0.55))
        self.fokus = False
        self.terlihat = True
        self.aktif = True
        self._kursor_waktu = 0.0
        self._kursor_nyala = True
        self.maks_karakter = int(maks_karakter) if maks_karakter else None
        self.on_ubah = None  # callback saat teks berubah
        self.on_enter = None  # callback saat Enter ditekan
        self.on_fokus = None  # callback saat fokus masuk
        self.on_keluar_fokus = None  # callback saat fokus hilang

    def berisi(self, px, py):
        """Cek apakah titik berada di dalam kotak teks."""
        return self.x <= px <= self.x + self.lebar and self.y <= py <= self.y + self.tinggi

    def update(self, tikus_x, tikus_y, diklik=False):
        """Update fokus berdasarkan klik mouse.

        Returns:
            True jika kotak ini menerima fokus pada klik ini.
        """
        if not self.aktif or not self.terlihat:
            return False
        if diklik:
            masuk = self.berisi(tikus_x, tikus_y)
            if masuk and not self.fokus and self.on_fokus:
                self.on_fokus()
            if not masuk and self.fokus and self.on_keluar_fokus:
                self.on_keluar_fokus()
            self.fokus = masuk
            return masuk
        return False

    def tambah_karakter(self, karakter):
        """Tambah satu karakter ke teks (hanya jika fokus)."""
        if not self.fokus or not self.aktif:
            return self
        ch = str(karakter)
        # Hanya terima karakter yang bisa diketik (1 huruf/angka/tanda baca)
        if len(ch) != 1:
            return self
        if self.maks_karakter and len(self.teks) >= self.maks_karakter:
            return self
        self.teks += ch
        self._kursor_waktu = 0.0
        if self.on_ubah:
            self.on_ubah()
        return self

    def enter(self):
        """Pemicu manual tombol Enter — memanggil callback on_enter.

        Dipanggil dari kode game saat tombol Enter ditekan dan kotak sedang
        fokus (mis. submit form).
        """
        if self.fokus and self.on_enter:
            self.on_enter()
        return self

    def hapus_karakter(self):
        """Hapus karakter terakhir (backspace)."""
        if not self.fokus or not self.teks:
            return self
        self.teks = self.teks[:-1]
        self._kursor_waktu = 0.0
        if self.on_ubah:
            self.on_ubah()
        return self

    def kosongkan(self):
        """Kosongkan seluruh teks."""
        self.teks = ""
        if self.on_ubah:
            self.on_ubah()
        return self

    def set_teks(self, teks):
        """Set teks langsung."""
        self.teks = str(teks)
        if self.on_ubah:
            self.on_ubah()
        return self

    def teks_sekarang(self):
        """Isi teks saat ini."""
        return self.teks

    def habis(self) -> bool:
        """Cek apakah kotak teks kosong (belum ada isi)."""
        return len(self.teks) == 0

    def apakah_kosong(self) -> bool:
        """Alias jelas untuk habis(): cek apakah kotak teks kosong."""
        return len(self.teks) == 0

    def fokus_set(self, nilai: bool = True):
        """Set fokus manual."""
        self.fokus = bool(nilai)
        return self

    def gambar(self, screen):
        """Gambar kotak teks ke layar."""
        if not self.terlihat or pygame is None:
            return
        # Latar
        pygame.draw.rect(
            screen,
            self.warna,
            (int(self.x), int(self.y), int(self.lebar), int(self.tinggi)),
            border_radius=6,
        )
        # Batas
        warna_batas = self.warna_fokus if self.fokus else self.warna_batas
        pygame.draw.rect(
            screen,
            warna_batas,
            (int(self.x), int(self.y), int(self.lebar), int(self.tinggi)),
            2,
            border_radius=6,
        )
        font = _get_font(int(self.ukuran_teks))
        if font is None:
            return
        margin = 10
        if self.teks:
            surf = font.render(self.teks, True, self.warna_teks)
        elif self.placeholder:
            surf = font.render(self.placeholder, True, (150, 150, 150))
        else:
            surf = None
        teks_x = int(self.x) + margin
        teks_y = int(
            self.y
            + (self.tinggi - (font.get_linesize() if surf is None else surf.get_height())) / 2
        )
        if surf is not None:
            screen.blit(surf, (teks_x, teks_y))
            teks_x += surf.get_width()
        # Kursor berkedip saat fokus
        if self.fokus:
            self._kursor_waktu += 1 / 30
            if self._kursor_waktu > 0.6:
                self._kursor_waktu = 0.0
            self._kursor_nyala = self._kursor_waktu < 0.3
            if self._kursor_nyala:
                tinggi_k = font.get_linesize()
                pygame.draw.line(
                    screen,
                    self.warna_fokus,
                    (teks_x, teks_y + 2),
                    (teks_x, teks_y + tinggi_k - 4),
                    2,
                )


class Slider:
    """Slider horizontal: geser nilai dengan drag mouse.

    Contoh:
        buat volume = ui.Slider(200, 300, 250, nilai=50, min=0, maks=100)

        # Tiap frame:
        volume.update(input.tikus_posisi()[0], input.tikus_posisi()[1],
                      input.tikus_tekanan()[0])
        tulis volume.nilai_sekarang()
        volume.gambar(screen)
    """

    def __init__(
        self,
        x,
        y,
        lebar,
        nilai=50,
        min=0,
        maks=100,
        warna="biru",
        warna_track="abu-abu_gelap",
        warna_handle="putih",
        tinggi=10,
        radius_handle=10,
        langkah=None,
    ):
        self.x = float(x)
        self.y = float(y)
        self.lebar = float(lebar)
        self.min = float(min)
        self.maks = float(maks)
        self.tinggi = tinggi
        self.radius_handle = radius_handle
        self.warna = _resolve_warna(warna)
        self.warna_track = _resolve_warna(warna_track)
        self.warna_handle = _resolve_warna(warna_handle)
        self.langkah = langkah  # None = halus, mis. 5 = kelipatan 5
        self.nilai = self._clamp(nilai)
        self._drag = False
        self.terlihat = True
        self.aktif = True
        self.on_ubah = None  # callback saat nilai berubah
        self.on_selesai = None  # callback saat drag selesai

    def _clamp(self, v):
        v = max(self.min, min(float(v), self.maks))
        if self.langkah:
            v = round((v - self.min) / self.langkah) * self.langkah + self.min
            v = max(self.min, min(v, self.maks))
        return v

    def berisi(self, px, py):
        """Cek apakah titik berada di sekitar handle slider."""
        hx = self._handle_x()
        return (
            abs(px - hx) <= self.radius_handle + 5 and abs(py - self.y) <= self.radius_handle + 10
        )

    def berisi_track(self, px, py):
        """Cek apakah titik berada di dalam area track (termasuk handle)."""
        return (
            self.x - 5 <= px <= self.x + self.lebar + 5
            and abs(py - self.y) <= self.radius_handle + 10
        )

    def _handle_x(self):
        if self.maks == self.min:
            return self.x
        p = (self.nilai - self.min) / (self.maks - self.min)
        return self.x + p * self.lebar

    def atur_dari_posisi(self, px):
        """Set nilai dari koordinat x mouse (di-clamp ke track)."""
        p = max(0.0, min((px - self.x) / self.lebar, 1.0))
        baru = self.min + p * (self.maks - self.min)
        baru = self._clamp(baru)
        if baru != self.nilai:
            self.nilai = baru
            if self.on_ubah:
                self.on_ubah()
        return self.nilai

    def update(self, tikus_x, tikus_y, ditekan=False):
        """Update slider: mulai/hentikan drag & geser handle.

        Args:
            tikus_x, tikus_y: Posisi mouse.
            ditekan: True jika tombol kiri mouse sedang ditekan.

        Returns:
            Nilai slider saat ini.
        """
        if not self.aktif or not self.terlihat:
            return self.nilai
        if ditekan and self.berisi_track(tikus_x, tikus_y):
            if not self._drag:
                self._drag = True
            self.atur_dari_posisi(tikus_x)
        elif not ditekan:
            if self._drag and self.on_selesai:
                self.on_selesai()
            self._drag = False
        return self.nilai

    def nilai_sekarang(self):
        """Nilai slider saat ini."""
        return self.nilai

    def atur_nilai(self, nilai):
        """Set nilai langsung (di-clamp)."""
        baru = self._clamp(nilai)
        if baru != self.nilai:
            self.nilai = baru
            if self.on_ubah:
                self.on_ubah()
        return self

    def persen(self) -> float:
        """Persentase 0.0 .. 1.0."""
        if self.maks == self.min:
            return 0.0
        return (self.nilai - self.min) / (self.maks - self.min)

    def gambar(self, screen):
        """Gambar slider ke layar."""
        if not self.terlihat or pygame is None:
            return
        # Track
        pygame.draw.rect(
            screen,
            self.warna_track,
            (int(self.x), int(self.y - self.tinggi / 2), int(self.lebar), int(self.tinggi)),
            border_radius=int(self.tinggi / 2),
        )
        # Track terisi
        p = self.persen()
        if p > 0:
            isi = max(4, int(self.lebar * p))
            pygame.draw.rect(
                screen,
                self.warna,
                (int(self.x), int(self.y - self.tinggi / 2), isi, int(self.tinggi)),
                border_radius=int(self.tinggi / 2),
            )
        # Handle
        hx = int(self._handle_x())
        pygame.draw.circle(screen, self.warna_handle, (hx, int(self.y)), self.radius_handle)
        pygame.draw.circle(screen, self.warna, (hx, int(self.y)), self.radius_handle, 2)


class KotakCentang:
    """Checkbox dengan label dan callback.

    Contoh:
        buat musik = ui.KotakCentang(200, 400, label="Aktifkan musik",
                                     dicentang=True)

        # Tiap frame:
        musik.update(input.tikus_posisi()[0], input.tikus_posisi()[1],
                     input.tikus_baru_ditekan(0))
        jika musik.dicentang_sekarang() maka
            tulis "musik nyala"
        selesai
        musik.gambar(screen)
    """

    def __init__(
        self,
        x,
        y,
        label="",
        dicentang=False,
        ukuran=22,
        warna="biru",
        warna_cek="putih",
        warna_label="putih",
        ukuran_label=20,
    ):
        self.x = float(x)
        self.y = float(y)
        self.label = str(label)
        self.dicentang = bool(dicentang)
        self.ukuran = ukuran
        self.warna = _resolve_warna(warna)
        self.warna_cek = _resolve_warna(warna_cek)
        self.warna_label = _resolve_warna(warna_label)
        self.ukuran_label = ukuran_label
        self.terlihat = True
        self.aktif = True
        self.on_ubah = None  # callback saat dicentang berubah
        self.on_centang = None  # callback saat baru dicentang
        self.on_hapus = None  # callback saat centang dihapus

    def berisi(self, px, py):
        """Cek apakah titik berada di area checkbox (kotak + label)."""
        # Estimasi lebar label tanpa butuh pygame (aman untuk logika murni)
        lebar_label = len(self.label) * max(8, int(self.ukuran_label * 0.6))
        return (
            self.x <= px <= self.x + self.ukuran + 8 + lebar_label
            and self.y <= py <= self.y + self.ukuran
        )

    def update(self, tikus_x, tikus_y, diklik=False):
        """Update checkbox: toggle saat diklik di dalam area.

        Returns:
            Nilai baru (True/False) jika status berubah, None jika tidak.
        """
        if not self.aktif or not self.terlihat:
            return None
        if diklik and self.berisi(tikus_x, tikus_y):
            self.dicentang = not self.dicentang
            if self.dicentang and self.on_centang:
                self.on_centang()
            if not self.dicentang and self.on_hapus:
                self.on_hapus()
            if self.on_ubah:
                self.on_ubah()
            return self.dicentang
        return None

    def centang(self):
        """Centang checkbox."""
        if not self.dicentang:
            self.dicentang = True
            if self.on_centang:
                self.on_centang()
            if self.on_ubah:
                self.on_ubah()
        return self

    def hapus_centang(self):
        """Hapus centang."""
        if self.dicentang:
            self.dicentang = False
            if self.on_hapus:
                self.on_hapus()
            if self.on_ubah:
                self.on_ubah()
        return self

    def toggle(self):
        """Balik status centang."""
        if self.dicentang:
            self.hapus_centang()
        else:
            self.centang()
        return self

    def dicentang_sekarang(self) -> bool:
        """Cek apakah checkbox sedang dicentang."""
        return self.dicentang

    def gambar(self, screen):
        """Gambar checkbox ke layar."""
        if not self.terlihat or pygame is None:
            return
        u = int(self.ukuran)
        x, y = int(self.x), int(self.y)
        pygame.draw.rect(screen, self.warna, (x, y, u, u), border_radius=4)
        if self.dicentang:
            # Tanda centang
            pygame.draw.lines(
                screen,
                self.warna_cek,
                False,
                [(x + 4, y + u // 2), (x + u // 3, y + u - 5), (x + u - 3, y + 4)],
                3,
            )
        pygame.draw.rect(screen, (255, 255, 255), (x, y, u, u), 2, border_radius=4)
        if self.label:
            font = _get_font(int(self.ukuran_label))
            if font is not None:
                surf = font.render(self.label, True, self.warna_label)
                screen.blit(surf, (x + u + 8, y + (u - surf.get_height()) // 2))


class DaftarPilih:
    """Dropdown/select: pilih satu opsi dari daftar.

    Contoh:
        buat level = ui.DaftarPilih(200, 500, 200,
                                    opsi=["Mudah", "Sedang", "Sulit"],
                                    terpilih=1)

        # Tiap frame:
        level.update(input.tikus_posisi()[0], input.tikus_posisi()[1],
                     input.tikus_baru_ditekan(0))
        tulis level.opsi_terpilih()
        level.gambar(screen)
    """

    def __init__(
        self,
        x,
        y,
        lebar,
        opsi=None,
        terpilih=0,
        tinggi_item=32,
        warna="biru_gelap",
        warna_teks="putih",
        warna_buka="abu-abu_gelap",
        warna_teks_buka="putih",
        warna_hover="biru",
        ukuran_teks=18,
    ):
        self.x = float(x)
        self.y = float(y)
        self.lebar = lebar
        self.opsi = list(opsi or [])
        self.terpilih = max(0, min(int(terpilih), max(0, len(self.opsi) - 1)))
        self.tinggi_item = tinggi_item
        self.warna = _resolve_warna(warna)
        self.warna_teks = _resolve_warna(warna_teks)
        self.warna_buka = _resolve_warna(warna_buka)
        self.warna_teks_buka = _resolve_warna(warna_teks_buka)
        self.warna_hover = _resolve_warna(warna_hover)
        self.ukuran_teks = ukuran_teks
        self.terbuka = False
        self.terlihat = True
        self.aktif = True
        self.hover_indeks = None
        self.on_ubah = None  # callback saat pilihan berubah
        self.on_buka = None  # callback saat dropdown dibuka
        self.on_tutup = None  # callback saat dropdown ditutup

    def berisi(self, px, py):
        """Cek apakah titik berada di dalam kotak dropdown."""
        return self.x <= px <= self.x + self.lebar and self.y <= py <= self.y + self.tinggi_item

    def _berisi_item(self, px, py):
        """Indeks item dropdown yang berisi titik, atau None."""
        if not self.terbuka:
            return None
        for i in range(len(self.opsi)):
            iy = self.y + self.tinggi_item * (i + 1)
            # Batas bawah eksklusif supaya baris tidak saling tumpang tindih
            if self.x <= px <= self.x + self.lebar and iy <= py < iy + self.tinggi_item:
                return i
        return None

    def update(self, tikus_x, tikus_y, diklik=False):
        """Update dropdown: buka/tutup & pilih opsi.

        Returns:
            Index opsi yang baru dipilih, atau None.
        """
        if not self.aktif or not self.terlihat:
            return None
        if self.terbuka:
            self.hover_indeks = self._berisi_item(tikus_x, tikus_y)
        else:
            self.hover_indeks = None

        if diklik:
            if self.terbuka:
                # Klik item → pilih
                idx = self._berisi_item(tikus_x, tikus_y)
                if idx is not None and idx != self.terpilih:
                    self.terpilih = idx
                    if self.on_ubah:
                        self.on_ubah()
                # Klik di luar (termasuk kotak) → tutup
                if idx is not None:
                    if self.on_tutup:
                        self.on_tutup()
                    self.terbuka = False
                    return idx
                if self.berisi(tikus_x, tikus_y):
                    if self.on_tutup:
                        self.on_tutup()
                    self.terbuka = False
                    return None
                if self.on_tutup:
                    self.on_tutup()
                self.terbuka = False
                return None
            else:
                # Klik kotak → buka
                if self.berisi(tikus_x, tikus_y):
                    self.terbuka = True
                    if self.on_buka:
                        self.on_buka()
                    return None
        return None

    def buka(self):
        """Buka dropdown."""
        self.terbuka = True
        if self.on_buka:
            self.on_buka()
        return self

    def tutup(self):
        """Tutup dropdown."""
        if self.terbuka:
            self.terbuka = False
            if self.on_tutup:
                self.on_tutup()
        return self

    def pilih(self, indeks):
        """Pilih opsi berdasarkan index."""
        if 0 <= int(indeks) < len(self.opsi):
            baru = int(indeks)
            if baru != self.terpilih:
                self.terpilih = baru
                if self.on_ubah:
                    self.on_ubah()
        return self

    def indeks_terpilih(self) -> int:
        """Index opsi yang terpilih."""
        return self.terpilih

    def opsi_terpilih(self):
        """Nilai opsi yang terpilih (atau None jika kosong)."""
        if not self.opsi:
            return None
        return self.opsi[self.terpilih]

    def jumlah_opsi(self) -> int:
        """Jumlah opsi."""
        return len(self.opsi)

    def gambar(self, screen):
        """Gambar dropdown ke layar."""
        if not self.terlihat or pygame is None:
            return
        font = _get_font(int(self.ukuran_teks))
        x, y, w = int(self.x), int(self.y), int(self.lebar)
        # Kotak utama
        pygame.draw.rect(screen, self.warna, (x, y, w, int(self.tinggi_item)), border_radius=6)
        pygame.draw.rect(
            screen, (255, 255, 255), (x, y, w, int(self.tinggi_item)), 2, border_radius=6
        )
        if font is not None and self.opsi:
            teks = str(self.opsi[self.terpilih])
            surf = font.render(teks, True, self.warna_teks)
            screen.blit(surf, (x + 10, y + (int(self.tinggi_item) - surf.get_height()) // 2))
            # Panah bawah
            ax = x + w - 18
            ay = y + int(self.tinggi_item) // 2
            pygame.draw.polygon(
                screen, self.warna_teks, [(ax - 5, ay - 2), (ax + 5, ay - 2), (ax, ay + 4)]
            )
        # Daftar item saat terbuka
        if self.terbuka:
            for i, opsi in enumerate(self.opsi):
                iy = y + int(self.tinggi_item) * (i + 1)
                hover = i == self.hover_indeks
                warna_item = self.warna_hover if hover else self.warna_buka
                pygame.draw.rect(screen, warna_item, (x, iy, w, int(self.tinggi_item)))
                pygame.draw.rect(screen, (255, 255, 255), (x, iy, w, int(self.tinggi_item)), 1)
                if font is not None:
                    warna_teks = self.warna_teks_buka if not hover else (255, 255, 255)
                    surf = font.render(str(opsi), True, warna_teks)
                    screen.blit(
                        surf, (x + 10, iy + (int(self.tinggi_item) - surf.get_height()) // 2)
                    )


class Tooltip:
    """Tooltip yang muncul mengikuti mouse saat kursor hover target — v6.6.

    Contoh:
        buat tip = ui.Tooltip("Klik untuk mulai", warna="putih")

        # Tiap frame:
        tip.update(input.tikus_posisi()[0], input.tikus_posisi()[1],
                   tombol.hover, dt)
        tip.gambar(screen)
    """

    def __init__(self, teks, x=0, y=0, warna="putih", warna_bg="abu-abu_gelap",
                 ukuran=18, delay=0.4, padding=8, offset=(16, 22),
                 warna_batas="abu-abu_terang"):
        self.teks = str(teks)
        self.x = float(x)
        self.y = float(y)
        self.warna = _resolve_warna(warna)
        self.warna_bg = _resolve_warna(warna_bg)
        self.warna_batas = _resolve_warna(warna_batas)
        self.ukuran = ukuran
        self.delay = max(0.0, float(delay))
        self.padding = max(2, int(padding))
        self.offset_x, self.offset_y = float(offset[0]), float(offset[1])
        self._waktu = 0.0
        self._aktif = False
        self.terlihat = True

    def update(self, tikus_x, tikus_y, hover=False, dt=1 / 60):
        """Update tooltip: muncul setelah `delay` detik hover, ikuti mouse.

        Returns:
            True jika tooltip sedang tampil.
        """
        if hover:
            self._waktu += max(0.0, float(dt))
        else:
            self._waktu = 0.0
        self.x = float(tikus_x) + self.offset_x
        self.y = float(tikus_y) + self.offset_y
        self._aktif = self._waktu >= self.delay
        return self._aktif

    def aktif(self):
        """Cek apakah tooltip sedang tampil."""
        return self._aktif

    def set_teks(self, teks):
        """Ubah isi tooltip."""
        self.teks = str(teks)
        return self

    def gambar(self, screen):
        """Gambar tooltip (panel membulat + teks)."""
        if not self.terlihat or not self._aktif or pygame is None:
            return
        font = _get_font(int(self.ukuran))
        if font is None:
            return
        surf = font.render(self.teks, True, self.warna)
        w = surf.get_width() + self.padding * 2
        h = surf.get_height() + self.padding * 2
        gx, gy = int(self.x), int(self.y)
        # Jaga tooltip tetap di dalam layar
        try:
            lw, lh = screen.get_size()
            if gx + w > lw:
                gx = lw - w - 4
            if gy + h > lh:
                gy = lh - h - 4
        except Exception:
            pass
        pygame.draw.rect(screen, self.warna_bg, (gx, gy, w, h), border_radius=6)
        pygame.draw.rect(screen, self.warna_batas, (gx, gy, w, h), 1, border_radius=6)
        screen.blit(surf, (gx + self.padding, gy + self.padding))


class DaftarSkor:
    """Daftar skor tertinggi dengan penyimpanan file (JSON) — v6.6.

    Contoh:
        buat skor = ui.DaftarSkor("skor.json", maks_entri=10)
        skor.tambah("Budi", 1200)
        skor.tambah("Siti", 900)
        tulis skor.skor_tertinggi()      # 1200
        tulis skor.peringkat("Budi")     # 0
        # Iterasi tabel (nama, skor) terurut turun:
        untuk entri dalam skor.tabel() lakukan
            tulis entri[0] + " - " + entri[1]
        selesai
    """

    def __init__(self, path="skor.json", maks_entri=10):
        self.path = str(path)
        self.maks_entri = max(1, int(maks_entri))
        self.entri = []  # list [nama, skor]
        self._muat()

    def _muat(self):
        """Baca entri dari file (jika ada)."""
        import json
        import os
        try:
            if os.path.exists(self.path):
                with open(self.path, encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, list):
                    self.entri = [
                        [str(n), int(s)] for n, s in data if isinstance(s, (int, float))
                    ][:self.maks_entri]
        except (OSError, ValueError, TypeError):
            self.entri = []

    def simpan(self):
        """Simpan entri ke file (dipanggil otomatis saat tambah)."""
        import json
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.entri[:self.maks_entri], f, ensure_ascii=False)
        except OSError:
            pass
        return self

    def tambah(self, nama, skor):
        """Tambah entri skor baru; pangkas ke maks_entri; simpan otomatis.

        Returns:
            True jika masuk daftar (skor cukup bagus), False jika tidak.
        """
        self.entri.append([str(nama), int(skor)])
        self.entri.sort(key=lambda e: e[1], reverse=True)
        if len(self.entri) > self.maks_entri:
            self.entri = self.entri[:self.maks_entri]
            return self.peringkat(str(nama)) is not None
        self.simpan()
        return True

    def tabel(self):
        """List (nama, skor) terurut dari skor tertinggi."""
        return [tuple(e) for e in sorted(self.entri, key=lambda e: e[1], reverse=True)]

    def skor_tertinggi(self):
        """Skor tertinggi saat ini, atau 0."""
        if not self.entri:
            return 0
        return max(s for _, s in self.entri)

    def peringkat(self, nama):
        """Posisi (0-based) nama di daftar, atau None jika tidak ada."""
        for i, (n, _s) in enumerate(self.tabel()):
            if n == str(nama):
                return i
        return None

    def jumlah(self):
        """Jumlah entri tersimpan."""
        return len(self.entri)

    def bersihkan(self):
        """Kosongkan semua entri & simpan."""
        self.entri = []
        self.simpan()
        return self


def navigasi_fokus(komponen, arah, daftar):
    """Pindahkan fokus antar komponen (keyboard) — v6.6.

    Args:
        komponen: Komponen yang sedang fokus (atau None).
        arah: "atas", "bawah", "kiri", atau "kanan".
        daftar: List komponen yang bisa menerima fokus (KotakTeks, Tombol...).

    Returns:
        Komponen yang sekarang menerima fokus.

    Contoh:
        # Dari kode game, saat tombol panah/Enter ditekan:
        buat baru = ui.navigasi_fokus(nama, "bawah", [nama, email, umur])
    """
    if not daftar:
        return komponen
    if komponen is None or komponen not in daftar:
        baru = daftar[0]
    else:
        idx = daftar.index(komponen)
        if arah in ("bawah", "kanan"):
            idx = (idx + 1) % len(daftar)
        elif arah in ("atas", "kiri"):
            idx = (idx - 1) % len(daftar)
        else:
            return komponen
        baru = daftar[idx]
    if baru is not komponen:
        if hasattr(komponen, "fokus_set"):
            komponen.fokus_set(False)
        if hasattr(baru, "fokus_set"):
            baru.fokus_set(True)
    return baru


module = SimpleNamespace(
    Label=Label,
    Panel=Panel,
    Tombol=Tombol,
    Bar=Bar,
    KotakTeks=KotakTeks,
    Slider=Slider,
    KotakCentang=KotakCentang,
    DaftarPilih=DaftarPilih,
    Tooltip=Tooltip,
    DaftarSkor=DaftarSkor,
    navigasi_fokus=navigasi_fokus,
)
