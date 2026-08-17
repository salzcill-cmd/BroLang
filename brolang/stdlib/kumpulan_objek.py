"""
Modul Kumpulan Objek (Object Pooling) untuk BroLang Game Development
====================================================================

Object pooling — pola industri game untuk MENGGUNAKAN ULANG objek
(bullet, partikel, musuh, damage number) alih-alih membuat & membuang
objek baru setiap frame. Menghindari lag akibat garbage collection.

Contoh:
    impor kumpulan_objek

    # Pool peluru: buat fungsi pabrik + reset saat ambil/kembali
    buat peluru_baru = fungsi()
        kembali {"x": 0, "y": 0, "aktif": salah, "kecepatan": 300}
    selesai

    buat pool = kumpulan_objek.KumpulanObjek(peluru_baru, ukuran_awal=20)

    # Saat menembak:
    buat peluru = pool.ambil()
    peluru.x = pemain.x
    peluru.y = pemain.y
    peluru.aktif = benar

    # Saat peluru keluar layar:
    pool.kembalikan(peluru)

    # Reset semua ke pool (mis. saat ganti scene):
    pool.kosongkan()
"""

from types import SimpleNamespace


class KumpulanObjek:
    """Kumpulan (pool) objek yang bisa dipinjam & dikembalikan.

    Args:
        buat: Fungsi pabrik `buat() -> objek` yang membuat objek baru.
        ukuran_awal: Jumlah objek yang dibuat di awal (pre-warm).
        aktifkan: Fungsi `aktifkan(objek, *args, **kwargs)` yang dipanggil
            setiap objek diambil (reset state / pasang parameter).
        nonaktifkan: Fungsi `nonaktifkan(objek)` yang dipanggil setiap
            objek dikembalikan (reset state).
    """

    def __init__(self, buat, ukuran_awal=0, aktifkan=None, nonaktifkan=None):
        self._buat = buat
        self._aktifkan = aktifkan
        self._nonaktifkan = nonaktifkan
        self._aktif = []     # objek sedang dipakai
        self._tersedia = []  # objek siap pakai
        if ukuran_awal and ukuran_awal > 0:
            for _ in range(int(ukuran_awal)):
                self._tersedia.append(buat())

    def ambil(self, *args, **kwargs):
        """Ambil objek dari pool (buat baru bila kosong), lalu aktifkan."""
        if self._tersedia:
            obj = self._tersedia.pop()
        else:
            obj = self._buat()
        if self._aktifkan:
            self._aktifkan(obj, *args, **kwargs)
        self._aktif.append(obj)
        return obj

    def kembalikan(self, obj):
        """Kembalikan objek ke pool (reset via nonaktifkan bila ada)."""
        if obj in self._aktif:
            self._aktif.remove(obj)
        if self._nonaktifkan:
            self._nonaktifkan(obj)
        self._tersedia.append(obj)
        return self

    def aktif(self):
        """Daftar objek yang sedang dipakai (salinan)."""
        return list(self._aktif)

    def jumlah_aktif(self):
        """Berapa objek sedang dipakai."""
        return len(self._aktif)

    def jumlah_tersedia(self):
        """Berapa objek siap pakai di pool."""
        return len(self._tersedia)

    def total(self):
        """Total objek yang pernah dibuat (aktif + tersedia)."""
        return len(self._aktif) + len(self._tersedia)

    def kosongkan(self):
        """Kembalikan SEMUA objek aktif ke pool (tanpa membuangnya)."""
        for obj in self._aktif:
            if self._nonaktifkan:
                self._nonaktifkan(obj)
            self._tersedia.append(obj)
        self._aktif.clear()
        return self

    def hapus_semua(self):
        """Buang semua objek (pool kosong total)."""
        self._aktif.clear()
        self._tersedia.clear()
        return self


def buat_kumpulan(buat, ukuran_awal=0, aktifkan=None, nonaktifkan=None):
    """Buat KumpulanObjek baru (alias ringkas)."""
    return KumpulanObjek(buat, ukuran_awal, aktifkan, nonaktifkan)


# Helper siap pakai: pool objek sederhana berisi dict ber-flag `aktif`.
def buat_pool_flag(ukuran_awal=10):
    """Pool objek dict {'aktif': False} — ringan untuk bullet/partikel."""
    def _baru():
        return {"aktif": False}

    def _nonaktifkan(o):
        o["aktif"] = False

    return KumpulanObjek(_baru, ukuran_awal=ukuran_awal, nonaktifkan=_nonaktifkan)


module = SimpleNamespace(
    KumpulanObjek=KumpulanObjek,
    buat_kumpulan=buat_kumpulan,
    buat_pool_flag=buat_pool_flag,
)
