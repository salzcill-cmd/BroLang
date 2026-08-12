"""
Modul Tilemap untuk BroLang Game Development
=============================================

Sistem tilemap 2D: membuat peta dari array/string/file, deteksi tabrakan,
dan rendering dengan tileset gambar atau warna fallback.

Contoh:
    impor tilemap

    buat peta = tilemap.Tilemap(20, 15, 32)
    peta.dari_array([
        [1, 1, 1, 1],
        [1, 0, 0, 1],
        [1, 0, 0, 1],
        [1, 1, 1, 1],
    ])
    peta.atur_solid(1, True)   # tile id 1 = solid
    jika peta.is_solid(1, 1) maka
        tulis "Tile solid"
    selesai
"""

from types import SimpleNamespace


_TILE_PALETTE = {
    "putih": (255, 255, 255), "hitam": (0, 0, 0),
    "merah": (220, 60, 60), "hijau": (60, 200, 90),
    "biru": (70, 130, 255), "kuning": (255, 220, 60),
    "jingga": (255, 150, 40), "ungu": (170, 90, 255),
    "cyan": (60, 220, 255), "pink": (255, 90, 180),
    "magenta": (255, 60, 255), "coklat": (150, 90, 50),
    "abu-abu": (150, 150, 150), "emas": (255, 215, 0),
    "hijau_gelap": (40, 120, 60), "biru_gelap": (30, 40, 100),
    "merah_gelap": (160, 30, 30), "abu-abu_gelap": (50, 50, 50),
    "langit": (135, 206, 235),
}


def _resolve_warna(warna):
    """Konversi nama warna ke tuple RGB."""
    if isinstance(warna, str):
        return _TILE_PALETTE.get(warna, (200, 200, 200))
    return tuple(warna)


class Tile:
    """Tile individual."""

    def __init__(self, id=0, solid=False, animasi=None):
        self.id = id
        self.solid = solid
        self.animasi = animasi
        self.data = {}


class Tileset:
    """Tileset untuk tilemap."""

    def __init__(self, nama, ukuran_tile=32, baris=1, kolom=1):
        self.nama = nama
        self.ukuran_tile = ukuran_tile
        self.baris = baris
        self.kolom = kolom
        self.tiles = {}
        self.gambar = None
        self.warna = {}  # id -> warna fallback (jika tanpa gambar)
        self.animasi = {}  # v6.6: tile_id -> {"urutan": [ids], "kecepatan": s}

    def atur_animasi(self, tile_id, urutan, kecepatan=0.2):
        """Buat tile animasi — tile_id berganti-ganti mengikuti `urutan` (v6.6).

        Args:
            tile_id: Tile id yang akan dianimasikan di peta.
            urutan: List tile id yang ditampilkan bergantian, mis. [5, 6, 7].
            kecepatan: Detik per frame animasi (default 0.2).

        Contoh:
            tileset.atur_animasi(9, [9, 10, 11], kecepatan=0.15)  # air mengalir
        """
        self.animasi[tile_id] = {
            "urutan": list(urutan) or [tile_id],
            "kecepatan": max(0.01, float(kecepatan)),
        }
        return self

    def tambah_tile(self, id, solid=False, warna=None):
        """Menambahkan tile type.

        Args:
            id: ID tile.
            solid: True jika tile tidak bisa ditembus.
            warna: Warna fallback untuk rendering tanpa gambar.
        """
        self.tiles[id] = Tile(id=id, solid=solid)
        if warna is not None:
            self.warna[id] = warna

    def atur_solid(self, id, solid=True):
        """Set properti solid untuk sebuah tile id (buat otomatis jika belum ada)."""
        if id not in self.tiles:
            self.tiles[id] = Tile(id=id, solid=solid)
        else:
            self.tiles[id].solid = solid

    def atur_warna(self, id, warna):
        """Set warna fallback untuk tile id."""
        self.warna[id] = warna

    def set_gambar(self, gambar):
        """Set gambar tileset."""
        self.gambar = gambar

    def dapatkan_tile(self, id):
        """Mendapatkan tile by id."""
        return self.tiles.get(id)


class Tilemap:
    """Tilemap 2D."""

    def __init__(self, lebar=20, tinggi=15, ukuran_tile=32):
        # Guard dimensi <= 0: hindari ZeroDivisionError di pixel_ke_tile /
        # check_collision serta peta berukuran nol yang tidak berguna.
        self.lebar = max(int(lebar), 1)
        self.tinggi = max(int(tinggi), 1)
        self.ukuran_tile = max(int(ukuran_tile), 1)
        self.data = [[0] * self.lebar for _ in range(self.tinggi)]
        self.tileset = None

        # Collision layer
        self.solid_map = [[False] * lebar for _ in range(tinggi)]

        # v6.6: animasi & objek
        self._waktu_animasi = 0.0
        self.objek = []  # layer objek: SimpleNamespace(nama, x, y, ...)

    def set_tileset(self, tileset):
        """Set tileset untuk tilemap."""
        self.tileset = tileset
        self._refresh_solid_map()

    def _refresh_solid_map(self):
        """Sinkronkan solid_map dari data + tileset. Dipanggil setelah load."""
        if not self.tileset:
            return
        for y in range(self.tinggi):
            for x in range(self.lebar):
                tile_id = self.data[y][x]
                tile = self.tileset.dapatkan_tile(tile_id)
                self.solid_map[y][x] = bool(tile and tile.solid)

    def atur(self, x, y, tile_id):
        """Mengatur tile di posisi (x, y)."""
        if 0 <= x < self.lebar and 0 <= y < self.tinggi:
            self.data[y][x] = tile_id
            # Update solid map
            if self.tileset:
                tile = self.tileset.dapatkan_tile(tile_id)
                self.solid_map[y][x] = bool(tile and tile.solid)

    def dapatkan(self, x, y):
        """Mendapatkan tile id di posisi (x, y)."""
        if 0 <= x < self.lebar and 0 <= y < self.tinggi:
            return self.data[y][x]
        return -1

    def is_solid(self, x, y):
        """Mengecek apakah tile solid. Di luar peta dianggap solid."""
        if 0 <= x < self.lebar and 0 <= y < self.tinggi:
            return self.solid_map[y][x]
        return True

    def atur_solid(self, tile_id, solid=True):
        """Set properti solid untuk sebuah tile id di tileset.

        Contoh:
            peta.atur_solid(1, True)
        """
        if not self.tileset:
            raise RuntimeError(
                "Set tileset dulu: peta.set_tileset(tileset). "
                "Atau gunakan tilemap.buat_tileset().")
        self.tileset.atur_solid(tile_id, solid)
        self._refresh_solid_map()

    def dari_array(self, array_data):
        """Mengisi tilemap dari array 2D (baris terluar = y=0 di atas)."""
        for y in range(min(len(array_data), self.tinggi)):
            for x in range(min(len(array_data[y]), self.lebar)):
                self.data[y][x] = int(array_data[y][x])
        self._refresh_solid_map()

    def dari_string(self, string_data, pemisah=','):
        """Mengisi tilemap dari string multi-baris."""
        baris = string_data.strip().split('\n')
        for y, baris_data in enumerate(baris):
            if y >= self.tinggi:
                break
            kolom = baris_data.split(pemisah)
            for x, val in enumerate(kolom):
                if x >= self.lebar:
                    break
                try:
                    self.data[y][x] = int(val.strip())
                except ValueError:
                    self.data[y][x] = 0
        self._refresh_solid_map()

    def dari_file(self, path, pemisah=','):
        """Mengisi tilemap dari file teks.

        Contoh:
            peta.dari_file("level1.txt")
        """
        with open(path, encoding='utf-8') as f:
            konten = f.read()
        self.dari_string(konten, pemisah)

    def simpan_file(self, path, pemisah=','):
        """Menyimpan tilemap ke file teks."""
        with open(path, 'w', encoding='utf-8') as f:
            f.write(self.ke_string(pemisah))

    def ke_string(self, pemisah=','):
        """Mengkonversi tilemap ke string."""
        baris = []
        for y in range(self.tinggi):
            kolom = [str(self.data[y][x]) for x in range(self.lebar)]
            baris.append(pemisah.join(kolom))
        return '\n'.join(baris)

    def ke_array(self):
        """Mengkonversi ke array 2D."""
        return [row[:] for row in self.data]

    def pixel_ke_tile(self, px, py):
        """Mengkonversi koordinat pixel ke tile (tx, ty)."""
        return int(px // self.ukuran_tile), int(py // self.ukuran_tile)

    def tile_ke_pixel(self, tx, ty):
        """Mengkonversi koordinat tile ke pixel."""
        return tx * self.ukuran_tile, ty * self.ukuran_tile

    def check_collision(self, x, y, lebar=1, tinggi=1):
        """Mengecek tabrakan area (pixel) dengan tile solid.

        Args:
            x, y: Posisi pixel kiri-atas.
            lebar, tinggi: Ukuran area dalam pixel.
        """
        start_tx = int(x // self.ukuran_tile)
        start_ty = int(y // self.ukuran_tile)
        end_tx = int((x + lebar - 1) // self.ukuran_tile)
        end_ty = int((y + tinggi - 1) // self.ukuran_tile)

        for ty in range(start_ty, end_ty + 1):
            for tx in range(start_tx, end_tx + 1):
                if self.is_solid(tx, ty):
                    return True
        return False

    def tabrakan(self, x, y, lebar=1, tinggi=1):
        """Alias check_collision — cek tabrakan dengan tile solid."""
        return self.check_collision(x, y, lebar, tinggi)

    def is_solid_at(self, px, py):
        """Cek apakah titik pixel berada di tile solid."""
        tx, ty = self.pixel_ke_tile(px, py)
        return self.is_solid(tx, ty)

    def cek_lantai(self, px, py):
        """Cek apakah ada tile solid tepat di bawah titik (px, py) — v6.6.

        Berguna untuk deteksi pijakan karakter (posisi kaki, 1 tile ke bawah).
        """
        tx, ty = self.pixel_ke_tile(px, py)
        return self.is_solid(tx, ty + 1)

    def update(self, dt):
        """Majukan timer animasi tile — panggil tiap frame — v6.6."""
        self._waktu_animasi += dt

    def _frame_tile(self, tile_id):
        """Tile id yang sedang tampil (memperhitungkan animasi)."""
        if self.tileset and tile_id in getattr(self.tileset, "animasi", {}):
            anim = self.tileset.animasi[tile_id]
            urutan = anim["urutan"]
            idx = int(self._waktu_animasi / anim["kecepatan"]) % len(urutan)
            return urutan[idx]
        return tile_id

    # ================= Layer Objek (v6.6) =================

    def tambah_objek(self, nama, x, y, **atribut):
        """Tambah objek ke layer objek peta (spawn point, item, musuh...).

        Args:
            nama: Nama/jenis objek.
            x, y: Posisi pixel objek.
            atribut: Properti tambahan (mis. tipe="musuh", nyawa=3).

        Returns:
            Objek (SimpleNamespace) yang ditambahkan.

        Contoh:
            peta.tambah_objek("pemain", 64, 64, tipe="spawn")
            peta.tambah_objek("musuh", 300, 64, kecepatan=50)
        """
        obj = SimpleNamespace(nama=nama, x=float(x), y=float(y))
        for k, v in atribut.items():
            setattr(obj, k, v)
        self.objek.append(obj)
        return obj

    def cari_objek(self, nama):
        """Cari objek pertama dengan nama tertentu, atau None."""
        for o in self.objek:
            if o.nama == nama:
                return o
        return None

    def cari_semua_objek(self, nama):
        """Cari semua objek dengan nama tertentu."""
        return [o for o in self.objek if o.nama == nama]

    def hapus_objek(self, nama):
        """Hapus semua objek dengan nama tertentu. Kembalikan jumlah terhapus."""
        before = len(self.objek)
        self.objek = [o for o in self.objek if o.nama != nama]
        return before - len(self.objek)

    def bersihkan_objek(self):
        """Hapus semua objek dari layer objek."""
        self.objek.clear()

    def gambar(self, screen, kamera_x=0, kamera_y=0):
        """Menggambar tilemap (gambar tileset atau warna fallback)."""
        import math
        start_x = max(0, int(kamera_x // self.ukuran_tile))
        start_y = max(0, int(kamera_y // self.ukuran_tile))
        end_x = min(self.lebar, start_x + screen.get_width() // self.ukuran_tile + 2)
        end_y = min(self.tinggi, start_y + screen.get_height() // self.ukuran_tile + 2)

        try:
            import pygame
        except ImportError:
            return

        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                tile_id = self.data[y][x]
                if tile_id == 0:
                    continue

                # Tile animasi: tampilkan frame sesuai waktu (v6.6)
                tile_id = self._frame_tile(tile_id)

                screen_x = x * self.ukuran_tile - kamera_x
                screen_y = y * self.ukuran_tile - kamera_y

                if self.tileset and self.tileset.gambar is not None:
                    tileset_x = (tile_id % self.tileset.kolom) * self.ukuran_tile
                    tileset_y = (tile_id // self.tileset.kolom) * self.ukuran_tile
                    screen.blit(
                        self.tileset.gambar,
                        (screen_x, screen_y),
                        (tileset_x, tileset_y, self.ukuran_tile, self.ukuran_tile)
                    )
                else:
                    # Fallback: gambar persegi warna
                    warna = None
                    if self.tileset:
                        warna = self.tileset.warna.get(tile_id)
                    if warna is None:
                        # Warna default per id
                        palette = [
                            (200, 60, 60), (60, 200, 60), (60, 60, 200),
                            (200, 200, 60), (200, 60, 200), (60, 200, 200),
                            (200, 140, 60), (140, 60, 200),
                        ]
                        warna = palette[tile_id % len(palette)]
                    pygame.draw.rect(
                        screen, _resolve_warna(warna),
                        (int(screen_x), int(screen_y),
                         self.ukuran_tile, self.ukuran_tile)
                    )

    def fill(self, tile_id):
        """Mengisi seluruh tilemap dengan tile tertentu."""
        for y in range(self.tinggi):
            for x in range(self.lebar):
                self.data[y][x] = tile_id
        self._refresh_solid_map()

    def clear(self):
        """Mengosongkan tilemap."""
        self.fill(0)

    def resize(self, lebar, tinggi):
        """Mengubah ukuran tilemap (data lama dipertahankan)."""
        lebar = max(lebar, 1)
        tinggi = max(tinggi, 1)
        data_baru = [[0] * lebar for _ in range(tinggi)]
        for y in range(min(tinggi, self.tinggi)):
            for x in range(min(lebar, self.lebar)):
                data_baru[y][x] = self.data[y][x]
        self.data = data_baru
        self.lebar = lebar
        self.tinggi = tinggi
        self.solid_map = [[False] * lebar for _ in range(tinggi)]
        self._refresh_solid_map()

    def banyak_tile(self, tile_id) -> int:
        """Jumlah kemunculan sebuah tile id di peta."""
        return sum(row.count(tile_id) for row in self.data)


def buat_peta(lebar=20, tinggi=15, ukuran_tile=32):
    """Membuat tilemap baru."""
    return Tilemap(lebar, tinggi, ukuran_tile)


# Alias Python internal (nama 'buat' tabrakan dengan keyword BroLang,
# jadi dipakai lewat buat_peta dari kode BroLang).
def buat(lebar=20, tinggi=15, ukuran_tile=32):
    return Tilemap(lebar, tinggi, ukuran_tile)


def buat_tileset(nama, ukuran_tile=32, baris=1, kolom=1):
    """Membuat tileset baru."""
    return Tileset(nama, ukuran_tile, baris, kolom)


def dari_file(path, pemisah=',', ukuran_tile=32):
    """Membuat tilemap langsung dari file teks.

    Contoh:
        buat peta = tilemap.dari_file("level1.txt")
    """
    with open(path, encoding='utf-8') as f:
        baris = [b.strip() for b in f.readlines() if b.strip()]
    if not baris:
        # File kosong / hanya baris kosong -> peta kosong 1x1 (tidak crash)
        return Tilemap(1, 1, ukuran_tile)
    peta = Tilemap(
        lebar=max(len(b.split(pemisah)) for b in baris),
        tinggi=len(baris),
        ukuran_tile=ukuran_tile,
    )
    peta.dari_string('\n'.join(baris), pemisah)
    return peta


module = SimpleNamespace(
    Tilemap=Tilemap,
    Tile=Tile,
    Tileset=Tileset,
    buat_peta=buat_peta,
    buat_tileset=buat_tileset,
    dari_file=dari_file,
)
