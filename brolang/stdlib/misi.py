"""
Modul Misi (Quest & Achievement) untuk BroLang Game Development
================================================================

Sistem quest & achievement: misi dengan progres, status
(aktif/selesai/gagal), pencapaian yang terbuka, dan manajer untuk
melacak semuanya sekaligus. Status bisa disimpan & dimuat (JSON-safe).

Contoh:
    impor misi

    # Quest klasik: kumpulkan 5 kunci
    buat q = misi.Misi("cari_kunci", "Cari 5 Kunci",
                       deskripsi="Kumpulkan kunci di hutan gelap.",
                       tujuan=5)
    q.tambah_progres(2)     # 2/5
    q.tambah_progres(3)     # 5/5 -> selesai (kembali True)

    # Achievement
    buat a = misi.Pencapaian("pembunuh_pertama", "Pembunuh Pertama",
                             deskripsi="Kalahkan musuh pertamamu.")
    a.buka_kunci()          # True (baru terbuka)

    # Manajer — kelola banyak quest sekaligus
    buat manajer = misi.ManajerMisi()
    manajer.tambah_misi(misi.Misi("m1", "Misi 1", tujuan=3))
    manajer.tambah_progres("m1", 3)
    manajer.semua()          # [misi m1 (selesai)]
    manajer.aktif()          # quest yang belum selesai

    # Simpan & muat status
    buat data = manajer.ke_dict()
    manajer2 = misi.ManajerMisi()
    manajer2.muat(data)
"""

from types import SimpleNamespace


class Misi:
    """Satu quest dengan progres & status.

    Args:
        id: Identitas unik quest.
        nama: Nama tampilan quest.
        deskripsi: Penjelasan quest.
        tujuan: Jumlah progres yang dibutuhkan untuk selesai (>= 1).
        hadiah: Data hadiah opsional (dict/angka/teks — apa saja).
    """

    def __init__(self, id, nama, deskripsi="", tujuan=1, hadiah=None):
        self.id = str(id)
        self.nama = str(nama)
        self.deskripsi = str(deskripsi)
        self.tujuan = max(1, int(tujuan))
        self.hadiah = hadiah
        self._progres = 0
        self._status = "aktif"      # "aktif" | "selesai" | "gagal"
        self.on_selesai = None      # callback() saat baru selesai
        self.on_gagal = None        # callback() saat digagalkan

    def tambah_progres(self, n=1):
        """Tambah progres quest.

        Returns:
            True bila quest BARU saja selesai (transisi aktif -> selesai).
        """
        if self._status != "aktif":
            return False
        self._progres = min(self.tujuan, self._progres + int(n))
        if self._progres >= self.tujuan:
            self._status = "selesai"
            if self.on_selesai:
                self.on_selesai()
            return True
        return False

    def atur_progres(self, n):
        """Set progres langsung (tanpa trigger on_selesai)."""
        if self._status == "aktif":
            self._progres = max(0, min(self.tujuan, int(n)))
        return self

    def progres(self):
        """Progres saat ini (0..tujuan)."""
        return self._progres

    def selesai(self):
        """Apakah quest sudah selesai?"""
        return self._status == "selesai"

    def gagal(self):
        """Tandai quest gagal. Kembalikan True bila baru digagalkan."""
        if self._status != "aktif":
            return False
        self._status = "gagal"
        if self.on_gagal:
            self.on_gagal()
        return True

    def status(self):
        """Status quest: 'aktif', 'selesai', atau 'gagal'."""
        return self._status

    def sisa(self):
        """Sisa progres yang dibutuhkan (0 bila selesai/gagal)."""
        if self._status != "aktif":
            return 0
        return max(0, self.tujuan - self._progres)

    def ke_dict(self):
        """Status quest sebagai dict (untuk simpan/muat)."""
        return {
            "id": self.id,
            "nama": self.nama,
            "deskripsi": self.deskripsi,
            "tujuan": self.tujuan,
            "progres": self._progres,
            "status": self._status,
        }

    @staticmethod
    def dari_dict(data):
        """Bangun Misi dari dict `ke_dict()`."""
        m = Misi(data.get("id", ""), data.get("nama", ""),
                 data.get("deskripsi", ""), data.get("tujuan", 1))
        m._progres = int(data.get("progres", 0))
        m._status = data.get("status", "aktif")
        return m

    def __repr__(self):
        return (f"<Misi {self.id} ({self._status}) "
                f"{self._progres}/{self.tujuan}>")


class Pencapaian:
    """Satu achievement yang bisa terbuka (unlock) sekali saja.

    Args:
        id: Identitas unik achievement.
        nama: Nama tampilan.
        deskripsi: Penjelasan.
        tersembunyi: True = tidak ditampilkan sebelum terbuka.
    """

    def __init__(self, id, nama, deskripsi="", tersembunyi=False):
        self.id = str(id)
        self.nama = str(nama)
        self.deskripsi = str(deskripsi)
        self.tersembunyi = bool(tersembunyi)
        self._terbuka = False
        self._waktu_buka = 0.0
        self.on_buka = None         # callback() saat baru terbuka

    def buka_kunci(self):
        """Buka achievement.

        Returns:
            True bila BARU terbuka (transisi tertutup -> terbuka).
        """
        if self._terbuka:
            return False
        self._terbuka = True
        if self.on_buka:
            self.on_buka()
        return True

    def terbuka(self):
        """Apakah achievement sudah terbuka?"""
        return self._terbuka

    def ke_dict(self):
        """Status achievement sebagai dict."""
        return {
            "id": self.id,
            "nama": self.nama,
            "deskripsi": self.deskripsi,
            "tersembunyi": self.tersembunyi,
            "terbuka": self._terbuka,
            "waktu_buka": self._waktu_buka,
        }

    @staticmethod
    def dari_dict(data):
        """Bangun Pencapaian dari dict `ke_dict()`."""
        a = Pencapaian(data.get("id", ""), data.get("nama", ""),
                       data.get("deskripsi", ""), data.get("tersembunyi", False))
        a._terbuka = bool(data.get("terbuka", False))
        a._waktu_buka = float(data.get("waktu_buka", 0.0))
        return a

    def __repr__(self):
        return f"<Pencapaian {self.id} ({'terbuka' if self._terbuka else 'tertutup'})>"


class ManajerMisi:
    """Kelola banyak quest & achievement sekaligus."""

    def __init__(self):
        self._misi = {}
        self._pencapaian = {}
        self._riwayat = []          # id quest yang pernah selesai/gagal

    # ---------------- Quest ----------------

    def tambah_misi(self, misi):
        """Daftarkan objek Misi."""
        self._misi[misi.id] = misi
        return misi

    def buat_misi(self, id, nama, deskripsi="", tujuan=1, hadiah=None):
        """Buat & daftarkan Misi baru, kembalikan objeknya."""
        return self.tambah_misi(Misi(id, nama, deskripsi, tujuan, hadiah))

    def dapatkan(self, id):
        """Ambil Misi berdasarkan id (atau None)."""
        return self._misi.get(str(id))

    def semua(self):
        """Semua quest (dalam urutan didaftarkan)."""
        return list(self._misi.values())

    def aktif(self):
        """Quest berstatus 'aktif'."""
        return [m for m in self._misi.values() if m.status() == "aktif"]

    def selesai(self):
        """Quest berstatus 'selesai'."""
        return [m for m in self._misi.values() if m.status() == "selesai"]

    def gagal(self):
        """Quest berstatus 'gagal'."""
        return [m for m in self._misi.values() if m.status() == "gagal"]

    def tambah_progres(self, id, n=1):
        """Tambah progres quest. True bila quest baru selesai."""
        m = self.dapatkan(id)
        if m is None:
            return False
        baru_selesai = m.tambah_progres(n)
        if baru_selesai:
            self._riwayat.append(m.id)
        return baru_selesai

    def selesaikan(self, id):
        """Langsung selesaikan quest (set progres penuh)."""
        m = self.dapatkan(id)
        if m is None or m.selesai():
            return False
        m.atur_progres(m.tujuan)
        m.tambah_progres(0)
        self._riwayat.append(m.id)
        return True

    def gagalkan(self, id):
        """Gagalkan quest. True bila berhasil digagalkan."""
        m = self.dapatkan(id)
        if m is None:
            return False
        if m.gagal():
            self._riwayat.append(m.id)
            return True
        return False

    # ---------------- Achievement ----------------

    def tambah_pencapaian(self, pencapaian):
        """Daftarkan objek Pencapaian."""
        self._pencapaian[pencapaian.id] = pencapaian
        return pencapaian

    def buat_pencapaian(self, id, nama, deskripsi="", tersembunyi=False):
        """Buat & daftarkan Pencapaian baru."""
        return self.tambah_pencapaian(
            Pencapaian(id, nama, deskripsi, tersembunyi))

    def dapatkan_pencapaian(self, id):
        """Ambil Pencapaian berdasarkan id (atau None)."""
        return self._pencapaian.get(str(id))

    def buka_pencapaian(self, id):
        """Buka achievement. True bila BARU terbuka."""
        a = self.dapatkan_pencapaian(id)
        if a is None:
            return False
        return a.buka_kunci()

    def pencapaian_terbuka(self):
        """Daftar achievement yang sudah terbuka."""
        return [a for a in self._pencapaian.values() if a.terbuka()]

    def semua_pencapaian(self):
        """Semua achievement."""
        return list(self._pencapaian.values())

    # ---------------- Simpan / Muat ----------------

    def ke_dict(self):
        """Status semua quest & achievement sebagai dict (JSON-safe)."""
        return {
            "misi": [m.ke_dict() for m in self._misi.values()],
            "pencapaian": [a.ke_dict() for a in self._pencapaian.values()],
            "riwayat": list(self._riwayat),
        }

    def muat(self, data):
        """Muat status dari dict `ke_dict()` (menimpa yang ada)."""
        data = data or {}
        self._misi = {}
        for d in data.get("misi", []):
            m = Misi.dari_dict(d)
            self._misi[m.id] = m
        self._pencapaian = {}
        for d in data.get("pencapaian", []):
            a = Pencapaian.dari_dict(d)
            self._pencapaian[a.id] = a
        self._riwayat = list(data.get("riwayat", []))
        return self


def buat_manajer():
    """Buat ManajerMisi baru."""
    return ManajerMisi()


module = SimpleNamespace(
    Misi=Misi,
    Pencapaian=Pencapaian,
    ManajerMisi=ManajerMisi,
    buat_manajer=buat_manajer,
)
