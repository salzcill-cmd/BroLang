"""
Modul Dialog untuk BroLang Game Development
============================================

Sistem dialog RPG: kotak dialog dengan efek mesin ketik (typewriter),
nama pembicara, dan pilihan bercabang (branching choices).

Contoh:
    impor dialog

    # Dialog NPC sederhana
    buat d = dialog.Dialog(
        ["Halo, pengembara!", "Selamat datang di desa kami.", "Hati-hati di hutan."],
        nama_pembicara="Kepala Desa",
        kecepatan=40,   # karakter per detik
    )

    # Tiap frame:
    d.update(dt)
    d.gambar(screen)

    # Saat pemain tekan tombol lanjut:
    buat selesai = d.lanjut()   # True bila dialog habis

    # Dialog bercabang: baris terakhir punya pilihan
    buat d2 = dialog.Dialog(["Apa yang kamu cari?"], nama_pembicara="Penjaga")
    d2.atur_pilihan(["Tempa pedang", "Belanja", "Keluar"])
    # Setelah pemain memilih:
    buat hasil = d2.pilih(1)    # ("Belanja", selesai?)
"""

import math

from types import SimpleNamespace

try:
    import pygame
except ImportError:
    pygame = None


def _resolve_warna(warna):
    """Konversi nama warna / tuple ke tuple RGBA."""
    if isinstance(warna, str):
        palette = {
            "putih": (255, 255, 255), "hitam": (0, 0, 0),
            "merah": (255, 60, 60), "hijau": (60, 255, 90),
            "biru": (80, 140, 255), "kuning": (255, 220, 60),
            "jingga": (255, 150, 40), "ungu": (170, 90, 255),
            "cyan": (60, 220, 255), "pink": (255, 90, 180),
            "magenta": (255, 60, 255), "coklat": (160, 100, 60),
            "abu-abu": (150, 150, 150), "emas": (255, 215, 0),
        }
        return palette.get(warna, (255, 255, 255))
    return tuple(warna)


class Dialog:
    """Kotak dialog dengan efek mesin ketik & pilihan bercabang.

    Args:
        kalimat: List teks baris dialog.
        nama_pembicara: Nama pembicara (opsional).
        kecepatan: Karakter per detik untuk efek mesin ketik.
        ukuran: Ukuran font teks.
        warna: Warna teks (nama atau tuple RGB).
        lebar: Lebar kotak dialog (pixel).
        x, y: Posisi kiri-atas kotak (default: bawah tengah layar 800x600).
        kotak_warna: Warna latar kotak dialog.
    """

    def __init__(self, kalimat=None, nama_pembicara="", kecepatan=30.0,
                 ukuran=24, warna="putih", lebar=600, x=0, y=0,
                 kotak_warna="hitam"):
        self.kalimat = [str(k) for k in (kalimat or [])]
        self.nama_pembicara = str(nama_pembicara)
        self.kecepatan = max(1.0, float(kecepatan))
        self.ukuran = int(ukuran)
        self.warna = _resolve_warna(warna)
        self.lebar = int(lebar)
        self.x = float(x)
        self.y = float(y)
        self.kotak_warna = _resolve_warna(kotak_warna)
        self.tinggi = 120

        # State mesin ketik
        self._indeks = 0
        self._karakter = 0.0
        self._selesai = False
        self._pilihan = []          # pilihan bercabang baris saat ini
        self._pilihan_terpilih = None
        self._pilihan_indeks = 0
        self._callback_selesai = None
        self.terlihat = True

    # ---------------- Setup ----------------

    def tambah_baris(self, teks):
        """Tambahkan baris dialog ke akhir."""
        self.kalimat.append(str(teks))
        return self

    def atur_pilihan(self, pilihan):
        """Pasang pilihan bercabang untuk baris SAAT INI.

        Selama ada pilihan, `lanjut()` tidak maju — pemain harus `pilih()`.
        """
        self._pilihan = [str(p) for p in (pilihan or [])]
        self._pilihan_indeks = 0
        return self

    def on_selesai(self, fungsi):
        """Registrasi callback yang dipanggil saat dialog habis."""
        self._callback_selesai = fungsi
        return self

    # ---------------- Update ----------------

    def update(self, dt):
        """Majukan efek mesin ketik (panggil tiap frame)."""
        if self._selesai or self._pilihan:
            return
        self._karakter += float(dt) * self.kecepatan

    def selesai_mengetik(self):
        """Apakah baris saat ini sudah selesai diketik penuh?"""
        return self._karakter >= len(self.baris_sekarang())

    def tampilkan_semua(self):
        """Lewati efek mesin ketik — tampilkan baris penuh sekarang."""
        self._karakter = len(self.baris_sekarang())
        return self

    def lanjut(self):
        """Lanjut ke tahap berikutnya.

        - Masih mengetik  -> selesaikan baris penuh.
        - Ada pilihan     -> tidak maju (pakai `pilih`).
        - Baris habis     -> baris berikutnya; True bila dialog selesai.
        """
        if self._selesai:
            return True
        if self._pilihan:
            return False
        if not self.selesai_mengetik():
            self.tampilkan_semua()
            return False
        self._indeks += 1
        self._karakter = 0.0
        if self._indeks >= len(self.kalimat):
            self._selesai = True
            if self._callback_selesai:
                self._callback_selesai()
            return True
        return False

    def pilih(self, indeks):
        """Pilih salah satu pilihan bercabang.

        Returns:
            (teks_pilihan, selesai) — selesai True bila dialog habis.
        """
        if not self._pilihan:
            return (None, self._selesai)
        indeks = max(0, min(int(indeks), len(self._pilihan) - 1))
        teks = self._pilihan[indeks]
        self._pilihan_terpilih = teks
        self._pilihan_indeks = indeks
        self._pilihan = []
        self._karakter = 0.0
        self._indeks += 1
        if self._indeks >= len(self.kalimat):
            self._selesai = True
            if self._callback_selesai:
                self._callback_selesai()
        return (teks, self._selesai)

    # ---------------- Query ----------------

    def baris_sekarang(self):
        """Teks penuh baris dialog saat ini."""
        if not self.kalimat:
            return ""
        return self.kalimat[min(self._indeks, len(self.kalimat) - 1)]

    def teks_terlihat(self):
        """Teks yang sudah muncul (efek mesin ketik)."""
        teks = self.baris_sekarang()
        n = min(len(teks), int(self._karakter))
        return teks[:n]

    def indeks_baris(self):
        """Index baris dialog saat ini (0-based)."""
        return self._indeks

    def jumlah_baris(self):
        """Total baris dialog."""
        return len(self.kalimat)

    def selesai(self):
        """Apakah seluruh dialog sudah selesai?"""
        return self._selesai

    def pilihan_sekarang(self):
        """Daftar pilihan bercabang baris saat ini (kosong bila tak ada)."""
        return list(self._pilihan)

    def pilihan_terpilih(self):
        """Teks pilihan terakhir yang dipilih (atau None)."""
        return self._pilihan_terpilih

    def indeks_pilihan(self):
        """Index pilihan yang sedang disorot (untuk navigasi)."""
        return self._pilihan_indeks

    def geser_pilihan(self, arah):
        """Geser sorotan pilihan (-1 / +1), membungkus."""
        if not self._pilihan:
            return 0
        n = len(self._pilihan)
        self._pilihan_indeks = (self._pilihan_indeks + arah) % n
        return self._pilihan_indeks

    def reset(self):
        """Kembalikan dialog ke awal."""
        self._indeks = 0
        self._karakter = 0.0
        self._selesai = False
        self._pilihan = []
        self._pilihan_terpilih = None
        self._pilihan_indeks = 0
        return self

    # ---------------- Render ----------------

    def gambar(self, screen, kamera_x=0, kamera_y=0):
        """Gambar kotak dialog ke layar (pygame). Tanpa pygame: no-op."""
        if pygame is None or screen is None or not self.terlihat or self._selesai:
            return
        x = int(self.x - kamera_x)
        y = int(self.y - kamera_y)
        if self.x == 0 and self.y == 0:
            # Default: bawah tengah layar
            try:
                w = screen.get_width()
                x = max(0, (w - self.lebar) // 2)
                y = screen.get_height() - self.tinggi - 20
            except AttributeError:
                x, y = 0, 0

        pygame.draw.rect(screen, self.kotak_warna, (x, y, self.lebar, self.tinggi),
                         border_radius=12)
        pygame.draw.rect(screen, (255, 255, 255), (x, y, self.lebar, self.tinggi), 2,
                         border_radius=12)

        try:
            font = pygame.font.Font(None, self.ukuran)
        except Exception:
            font = None
        if font is None:
            return

        if self.nama_pembicara:
            nama_surf = font.render(self.nama_pembicara, True, (255, 215, 0))
            screen.blit(nama_surf, (x + 16, y + 10))

        teks = self.teks_terlihat()
        # Bungkus teks agar muat di kotak
        kata = teks.split(" ")
        baris = []
        baris_saat_ini = ""
        for k in kata:
            if font.size(baris_saat_ini + " " + k)[0] <= self.lebar - 32:
                baris_saat_ini = (baris_saat_ini + " " + k).strip()
            else:
                if baris_saat_ini:
                    baris.append(baris_saat_ini)
                baris_saat_ini = k
        if baris_saat_ini:
            baris.append(baris_saat_ini)

        dy = y + 40
        for b in baris[:3]:
            surf = font.render(b, True, self.warna)
            screen.blit(surf, (x + 16, dy))
            dy += self.ukuran + 4

        if self._pilihan:
            py_ = y + self.tinggi - 40
            for i, p in enumerate(self._pilihan):
                panah = ">" if i == self._pilihan_indeks else " "
                surf = font.render(f"{panah} {p}", True,
                                   (255, 255, 120) if i == self._pilihan_indeks else self.warna)
                screen.blit(surf, (x + 24, py_))
                py_ += self.ukuran


def buat_dialog(kalimat=None, nama_pembicara="", kecepatan=30.0, ukuran=24,
                warna="putih", lebar=600, x=0, y=0, kotak_warna="hitam"):
    """Buat Dialog baru (alias ringkas)."""
    return Dialog(kalimat, nama_pembicara, kecepatan, ukuran, warna,
                  lebar, x, y, kotak_warna)


module = SimpleNamespace(
    Dialog=Dialog,
    buat_dialog=buat_dialog,
)
