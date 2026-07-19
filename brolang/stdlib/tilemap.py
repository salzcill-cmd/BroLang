"""
Modul Tilemap untuk BroLang Game Development
=============================================

Menyediakan sistem tilemap untuk game.

Contoh:
    impor tilemap

    buat peta = tilemap.Tilemap(20, 15, 32)
    peta.atur(5, 3, 1)
    peta.atur(5, 4, 1)
"""

from types import SimpleNamespace


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

    def tambah_tile(self, id, solid=False):
        """Menambahkan tile type."""
        self.tiles[id] = Tile(id=id, solid=solid)

    def set_gambar(self, gambar):
        """Set gambar tileset."""
        self.gambar = gambar

    def dapatkan_tile(self, id):
        """Mendapatkan tile by id."""
        return self.tiles.get(id)


class Tilemap:
    """Tilemap 2D."""

    def __init__(self, lebar=20, tinggi=15, ukuran_tile=32):
        self.lebar = lebar
        self.tinggi = tinggi
        self.ukuran_tile = ukuran_tile
        self.data = [[0] * lebar for _ in range(tinggi)]
        self.tileset = None
        this = self

        # Collision layers
        self._layers = {}
        this.solid_map = [[False] * lebar for _ in range(tinggi)]

    def set_tileset(self, tileset):
        """Set tileset untuk tilemap."""
        self.tileset = tileset

    def atur(self, x, y, tile_id):
        """Mengatur tile di posisi (x, y)."""
        if 0 <= x < self.lebar and 0 <= y < self.tinggi:
            self.data[y][x] = tile_id
            # Update solid map
            if self.tileset:
                tile = self.tileset.dapatkan_tile(tile_id)
                if tile:
                    self.solid_map[y][x] = tile.solid

    def dapatkan(self, x, y):
        """Mendapatkan tile id di posisi (x, y)."""
        if 0 <= x < self.lebar and 0 <= y < self.tinggi:
            return self.data[y][x]
        return -1

    def is_solid(self, x, y):
        """Mengecek apakah tile solid."""
        if 0 <= x < self.lebar and 0 <= y < self.tinggi:
            return self.solid_map[y][x]
        return True

    def dari_array(self, array_data):
        """Mengisi tilemap dari array 2D."""
        for y in range(min(len(array_data), self.tinggi)):
            for x in range(min(len(array_data[y]), self.lebar)):
                self.data[y][x] = array_data[y][x]

    def dari_string(self, string_data, pemisah=','):
        """Mengisi tilemap dari string."""
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
        """Mengkonversi koordinat pixel ke tile."""
        return int(px // self.ukuran_tile), int(py // self.ukuran_tile)

    def tile_ke_pixel(self, tx, ty):
        """Mengkonversi koordinat tile ke pixel."""
        return tx * self.ukuran_tile, ty * self.ukuran_tile

    def gambar(self, screen, kamera_x=0, kamera_y=0):
        """Menggambar tilemap."""
        if not self.tileset or not self.tileset.gambar:
            return

        try:
            import pygame
            # Calculate visible tiles
            start_x = max(0, int(kamera_x // self.ukuran_tile))
            start_y = max(0, int(kamera_y // self.ukuran_tile))
            end_x = min(self.lebar, start_x + screen.get_width() // self.ukuran_tile + 2)
            end_y = min(self.tinggi, start_y + screen.get_height() // self.ukuran_tile + 2)

            for y in range(start_y, end_y):
                for x in range(start_x, end_x):
                    tile_id = self.data[y][x]
                    if tile_id == 0:
                        continue

                    # Get tile position in tileset
                    tileset_x = (tile_id % self.tileset.kolom) * self.ukuran_tile
                    tileset_y = (tile_id // self.tileset.kolom) * self.ukuran_tile

                    screen_x = x * self.ukuran_tile - kamera_x
                    screen_y = y * self.ukuran_tile - kamera_y

                    screen.blit(
                        self.tileset.gambar,
                        (screen_x, screen_y),
                        (tileset_x, tileset_y, self.ukuran_tile, self.ukuran_tile)
                    )
        except ImportError:
            pass

    def check_collision(self, x, y, lebar=1, tinggi=1):
        """Mengecek kolisi dengan tile solid."""
        # Check all tiles the entity overlaps
        start_tx = int(x // self.ukuran_tile)
        start_ty = int(y // self.ukuran_tile)
        end_tx = int((x + lebar - 1) // self.ukuran_tile)
        end_ty = int((y + tinggi - 1) // self.ukuran_tile)

        for ty in range(start_ty, end_ty + 1):
            for tx in range(start_tx, end_tx + 1):
                if self.is_solid(tx, ty):
                    return True
        return False

    def fill(self, tile_id):
        """Mengisi seluruh tilemap dengan tile tertentu."""
        for y in range(self.tinggi):
            for x in range(self.lebar):
                self.data[y][x] = tile_id

    def clear(self):
        """Mengosongkan tilemap."""
        self.fill(0)


def buat(lebar=20, tinggi=15, ukuran_tile=32):
    """Membuat tilemap baru."""
    return Tilemap(lebar, tinggi, ukuran_tile)


def buat_tileset(nama, ukuran_tile=32, baris=1, kolom=1):
    """Membuat tileset baru."""
    return Tileset(nama, ukuran_tile, baris, kolom)


module = SimpleNamespace(
    Tilemap=Tilemap,
    Tile=Tile,
    Tileset=Tileset,
    buat=buat,
    buat_tileset=buat_tileset,
)
