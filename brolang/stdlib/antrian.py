"""
Modul Antrian (Queue) untuk BroLang
====================================

Menyediakan struktur data antrian.

Contoh:
    impor antrian
    buat q = antrian.Buat()
    q.sisipkan("a")
    q.sisipkan("b")
    tulis(q.ambil())  # "a"
"""

from collections import deque
from types import SimpleNamespace


class Antrian:
    """Antrian FIFO (First In First Out)."""

    def __init__(self, maxsize=0):
        self._data = deque()
        self._maxsize = maxsize

    def sisipkan(self, item):
        """Menambahkan item ke antrian."""
        if self._maxsize > 0 and len(self._data) >= self._maxsize:
            raise RuntimeError("Antrian penuh.")
        self._data.append(item)

    def ambil(self):
        """Mengambil item dari depan antrian."""
        if not self._data:
            raise RuntimeError("Antrian kosong.")
        return self._data.popleft()

    def lihat(self):
        """Melihat item depan tanpa mengambil."""
        if not self._data:
            raise RuntimeError("Antrian kosong.")
        return self._data[0]

    def jumlah(self):
        """Mengembalikan jumlah item dalam antrian."""
        return len(self._data)

    def kosong(self):
        """Mengecek apakah antrian kosong."""
        return len(self._data) == 0

    def penuh(self):
        """Mengecek apakah antrian penuh."""
        if self._maxsize <= 0:
            return False
        return len(self._data) >= self._maxsize

    def kosongkan(self):
        """Mengosongkan antrian."""
        self._data.clear()

    def ke_list(self):
        """Mengkonversi ke list."""
        return list(self._data)


class AntrianPrioritas:
    """Antrian dengan prioritas."""

    def __init__(self):
        self._data = []

    def sisipkan(self, item, prioritas=0):
        """Menambahkan item dengan prioritas (semakin kecil semakin tinggi)."""
        self._data.append((prioritas, item))
        self._data.sort(key=lambda x: x[0])

    def ambil(self):
        """Mengambil item dengan prioritas tertinggi."""
        if not self._data:
            raise RuntimeError("Antrian kosong.")
        return self._data.pop(0)[1]

    def lihat(self):
        """Melihat item prioritas tertinggi."""
        if not self._data:
            raise RuntimeError("Antrian kosong.")
        return self._data[0][1]

    def jumlah(self):
        return len(self._data)

    def kosong(self):
        return len(self._data) == 0

    def kosongkan(self):
        self._data.clear()


class AntrianDuaArah:
    """Antrian dua arah (Deque)."""

    def __init__(self):
        self._data = deque()

    def sisipkan_depan(self, item):
        """Menambahkan item di depan."""
        self._data.appendleft(item)

    def sisipkan_belakang(self, item):
        """Menambahkan item di belakang."""
        self._data.append(item)

    def ambil_depan(self):
        """Mengambil item dari depan."""
        if not self._data:
            raise RuntimeError("Antrian kosong.")
        return self._data.popleft()

    def ambil_belakang(self):
        """Mengambil item dari belakang."""
        if not self._data:
            raise RuntimeError("Antrian kosong.")
        return self._data.pop()

    def lihat_depan(self):
        if not self._data:
            raise RuntimeError("Antrian kosong.")
        return self._data[0]

    def lihat_belakang(self):
        if not self._data:
            raise RuntimeError("Antrian kosong.")
        return self._data[-1]

    def jumlah(self):
        return len(self._data)

    def kosong(self):
        return len(self._data) == 0

    def kosongkan(self):
        self._data.clear()

    def ke_list(self):
        return list(self._data)


def buat(maxsize=0):
    """Membuat antrian baru."""
    return Antrian(maxsize=maxsize)


def buat_prioritas():
    """Membuat antrian prioritas baru."""
    return AntrianPrioritas()


def buat_dua_arah():
    """Membuat antrian dua arah baru."""
    return AntrianDuaArah()


# v7.1: alias aman-keyword (`buat` adalah keyword bahasa) — level modul
# agar berfungsi di interpreter DAN VM.
buat_antrian = buat


module = SimpleNamespace(
    Buat=buat,
    buat=buat,
    buat_antrian=buat_antrian,
    buat_prioritas=buat_prioritas,
    buat_dua_arah=buat_dua_arah,
    Antrian=Antrian,
    AntrianPrioritas=AntrianPrioritas,
    AntrianDuaArah=AntrianDuaArah,
)
