"""
Modul Tumpukan (Stack) untuk BroLang
=====================================

Menyediakan struktur data tumpukan.

Contoh:
    impor tumpukan
    buat s = tumpukan.Buat()
    s.tumpuk("a")
    s.tumpuk("b")
    tulis(s.pop())  # "b"
"""

from types import SimpleNamespace


class Tumpukan:
    """Tumpukan LIFO (Last In First Out)."""

    def __init__(self, maxsize=0):
        self._data = []
        self._maxsize = maxsize

    def tumpuk(self, item):
        """Menambahkan item ke tumpukan."""
        if self._maxsize > 0 and len(self._data) >= self._maxsize:
            raise RuntimeError("Tumpukan penuh.")
        self._data.append(item)

    def ambil(self):
        """Mengambil item dari atas tumpukan."""
        if not self._data:
            raise RuntimeError("Tumpukan kosong.")
        return self._data.pop()

    def lihat(self):
        """Melihat item di atas tanpa mengambil."""
        if not self._data:
            raise RuntimeError("Tumpukan kosong.")
        return self._data[-1]

    def jumlah(self):
        """Mengembalikan jumlah item dalam tumpukan."""
        return len(self._data)

    def kosong(self):
        """Mengecek apakah tumpukan kosong."""
        return len(self._data) == 0

    def penuh(self):
        """Mengecek apakah tumpukan penuh."""
        if self._maxsize <= 0:
            return False
        return len(self._data) >= self._maxsize

    def kosongkan(self):
        """Mengosongkan tumpukan."""
        self._data.clear()

    def ke_list(self):
        """Mengkonversi ke list."""
        return self._data[:]

    def balik(self):
        """Membalik urutan tumpukan."""
        self._data.reverse()


class TumpukanTerbatas:
    """Tumpukan dengan ukuran maksimum."""

    def __init__(self, maxsize):
        self._data = []
        self._maxsize = maxsize

    def tumpuk(self, item):
        if len(self._data) >= self._maxsize:
            raise RuntimeError(f"Tumpukan penuh (maks: {self._maxsize}).")
        self._data.append(item)

    def ambil(self):
        if not self._data:
            raise RuntimeError("Tumpukan kosong.")
        return self._data.pop()

    def lihat(self):
        if not self._data:
            raise RuntimeError("Tumpukan kosong.")
        return self._data[-1]

    def jumlah(self):
        return len(self._data)

    def sisa(self):
        """Mengembalikan sisa kapasitas."""
        return self._maxsize - len(self._data)

    def kosong(self):
        return len(self._data) == 0

    def penuh(self):
        return len(self._data) >= self._maxsize

    def kosongkan(self):
        self._data.clear()


def buat(maxsize=0):
    """Membuat tumpukan baru."""
    return Tumpukan(maxsize=maxsize)


def buat_terbatas(maxsize):
    """Membuat tumpukan dengan batas ukuran."""
    return TumpukanTerbatas(maxsize=maxsize)


module = SimpleNamespace(
    Buat=buat,
    buat=buat,
    buat_terbatas=buat_terbatas,
    Tumpukan=Tumpukan,
    TumpukanTerbatas=TumpukanTerbatas,
)
