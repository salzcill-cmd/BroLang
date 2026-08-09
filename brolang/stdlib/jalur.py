"""
Modul Jalur untuk BroLang Game Development (v6.6)
================================================

Pathfinding & navigasi waypoint: A* untuk tilemap, mengikuti jalur,
dan patroli antar titik.

Contoh:
    impor jalur
    impor tilemap

    buat peta = tilemap.buat_peta(20, 15, 32)
    peta.dari_array([...])

    # Cari jalur dari tile (1, 1) ke (10, 5)
    buat titik_titik = jalur.cari_jalur(peta, (1, 1), (10, 5))
    jika titik_titik bukan kosong maka
        tulis "Jalur ditemukan, " + jalur.panjang_jalur(titik_titik) + " tile"
    selesai

    # Patroli antar waypoint (loop / bolak-balik / sekali)
    buat penjaga = jalur.Patroli([(100, 100), (400, 100), (400, 400)],
                                 kecepatan=120, mode="bolak-balik")
    penjaga.update(dt)
    buat (gx, gy) = penjaga.posisi()
"""

import heapq
import math
from types import SimpleNamespace


# ================= Pathfinding A* =================


def _peta_is_solid(peta, tx, ty):
    """Cek soliditas tile. Terima objek tilemap atau list 2D."""
    if hasattr(peta, "is_solid"):
        return peta.is_solid(tx, ty)
    # List 2D: nilai != 0 dianggap solid
    try:
        if ty < 0 or tx < 0 or ty >= len(peta) or tx >= len(peta[ty]):
            return True
        return bool(peta[ty][tx])
    except (TypeError, IndexError):
        return True


def cari_jalur(peta, mulai, tujuan, diagonal=False):
    """Mencari jalur terpendek (A*) antar dua tile.

    Args:
        peta: objek tilemap (punya `is_solid(tx, ty)`) ATAU list 2D
            (0 = kosong, selain 0 = solid).
        mulai: (tx, ty) koordinat tile awal.
        tujuan: (tx, ty) koordinat tile tujuan.
        diagonal: izinkan gerakan diagonal (default False).

    Returns:
        List koordinat tile [(tx, ty), ...] dari mulai sampai tujuan,
        atau None jika tidak ada jalur.

    Contoh:
        buat jalur_tiles = jalur.cari_jalur(peta, (1, 1), (10, 5))
    """
    if _peta_is_solid(peta, mulai[0], mulai[1]) or _peta_is_solid(peta, tujuan[0], tujuan[1]):
        return None
    if mulai == tujuan:
        return [mulai]

    def heuristik(a, b):
        # Manhattan (atau chebyshev jika diagonal diizinkan)
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return max(dx, dy) if diagonal else dx + dy

    open_set = [(0, mulai)]
    g_score = {mulai: 0}
    came_from = {}

    arah = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    if diagonal:
        arah += [(1, 1), (1, -1), (-1, 1), (-1, -1)]

    while open_set:
        _, saat_ini = heapq.heappop(open_set)
        if saat_ini == tujuan:
            # Rekonstruksi jalur
            jalur = [saat_ini]
            while saat_ini in came_from:
                saat_ini = came_from[saat_ini]
                jalur.append(saat_ini)
            jalur.reverse()
            return jalur

        for dx, dy in arah:
            tetangga = (saat_ini[0] + dx, saat_ini[1] + dy)
            if _peta_is_solid(peta, tetangga[0], tetangga[1]):
                continue
            # Potong pojok: jangan lewat diagonal menembus dinding
            if dx != 0 and dy != 0:
                if _peta_is_solid(peta, saat_ini[0] + dx, saat_ini[1]) or \
                   _peta_is_solid(peta, saat_ini[0], saat_ini[1] + dy):
                    continue
            cost = 1.414 if dx != 0 and dy != 0 else 1.0
            tentatif = g_score[saat_ini] + cost
            if tentatif < g_score.get(tetangga, float("inf")):
                came_from[tetangga] = saat_ini
                g_score[tetangga] = tentatif
                f = tentatif + heuristik(tetangga, tujuan)
                heapq.heappush(open_set, (f, tetangga))

    return None


def panjang_jalur(jalur):
    """Panjang jalur dalam jumlah tile (atau 0 jika None)."""
    if not jalur:
        return 0
    return len(jalur)


def jalur_ke_pixel(jalur, ukuran_tile=32, tengah=True):
    """Konversi jalur tile ke koordinat pixel (pusat tile).

    Args:
        jalur: hasil cari_jalur().
        ukuran_tile: ukuran tile dalam pixel.
        tengah: offset ke tengah tile (default True).

    Returns:
        List (px, py) pixel, atau [] jika jalur None.
    """
    if not jalur:
        return []
    offset = ukuran_tile / 2 if tengah else 0
    return [(tx * ukuran_tile + offset, ty * ukuran_tile + offset) for tx, ty in jalur]


# ================= Ikuti Jalur =================


class IkutiJalur:
    """Mengikuti jalur waypoint secara berurutan.

    Contoh:
        buat pengikut = jalur.IkutiJalur(titik_pixel, kecepatan=150)
        pengikut.on_selesai = fungsi_sampai
        pengikut.update(dt)
        buat (px, py) = pengikut.posisi()
    """

    def __init__(self, titik_titik, kecepatan=100.0, loop=False):
        self.titik = [tuple(t) for t in titik_titik] or [(0, 0)]
        self.kecepatan = float(kecepatan)
        self.loop = bool(loop)
        self._indeks = 0
        self.selesai = False
        self.x = float(self.titik[0][0])
        self.y = float(self.titik[0][1])
        self.on_selesai = None  # callback saat semua waypoint selesai
        self.on_titik = None    # callback saat mencapai satu waypoint

    def update(self, dt):
        """Gerak menuju waypoint berikutnya. Kembalikan False jika selesai."""
        if self.selesai:
            return False
        langkah = self.kecepatan * dt
        # Iteratif (bukan rekursif) supaya aman saat jarak 0 / langkah besar
        for _ in range(len(self.titik) + 1):
            if self._indeks >= len(self.titik) - 1:
                if self.loop:
                    self._indeks = 0
                else:
                    self.selesai = True
                    if self.on_selesai:
                        self.on_selesai()
                    return False

            tx, ty = self.titik[self._indeks + 1]
            dx = tx - self.x
            dy = ty - self.y
            jarak = math.hypot(dx, dy)

            if langkah >= jarak:
                # Sampai di waypoint
                self.x, self.y = float(tx), float(ty)
                self._indeks += 1
                langkah -= jarak
                if self.on_titik:
                    self.on_titik(self._indeks)
                if langkah <= 0:
                    break
            else:
                self.x += dx / jarak * langkah
                self.y += dy / jarak * langkah
                break
        return True

    def posisi(self):
        """Posisi saat ini (x, y)."""
        return self.x, self.y

    def titik_sekarang(self):
        """Index waypoint tujuan saat ini."""
        return min(self._indeks + 1, len(self.titik) - 1)

    def sisa_jarak(self):
        """Sisa jarak ke waypoint tujuan (pixel)."""
        if self.selesai:
            return 0.0
        tx, ty = self.titik[self.titik_sekarang()]
        return math.hypot(tx - self.x, ty - self.y)

    def reset(self):
        """Kembali ke waypoint pertama."""
        self._indeks = 0
        self.selesai = False
        self.x = float(self.titik[0][0])
        self.y = float(self.titik[0][1])
        return self

    def tambah_titik(self, x, y):
        """Tambahkan waypoint baru di akhir."""
        self.titik.append((float(x), float(y)))
        return self


# ================= Patroli =================


class Patroli:
    """Patroli antar waypoint dengan mode gerak.

    Mode:
        - "loop"        : ulang dari waypoint pertama setelah sampai akhir
        - "bolak-balik" : ping-pong (maju lalu mundur)
        - "sekali"      : berhenti di waypoint terakhir

    Contoh:
        buat penjaga = jalur.Patroli([(100, 100), (400, 100)], kecepatan=120)
        penjaga.update(dt)
        buat (px, py) = penjaga.posisi()
    """

    def __init__(self, titik_titik, kecepatan=100.0, mode="loop", jarak_berhenti=2.0):
        self.titik = [tuple(t) for t in titik_titik] or [(0, 0)]
        self.kecepatan = float(kecepatan)
        self.mode = mode if mode in ("loop", "bolak-balik", "sekali") else "loop"
        self.jarak_berhenti = float(jarak_berhenti)
        self._indeks = 0
        self._arah = 1  # 1 = maju, -1 = mundur (untuk bolak-balik)
        self.selesai = False
        self.x = float(self.titik[0][0])
        self.y = float(self.titik[0][1])
        self.on_titik = None   # callback saat sampai di waypoint
        self.on_selesai = None  # callback saat patroli selesai (mode sekali)

    def update(self, dt):
        """Gerak sepanjang patroli. Kembalikan False jika selesai (mode sekali)."""
        if self.selesai:
            return False
        if len(self.titik) == 1:
            self.x, self.y = float(self.titik[0][0]), float(self.titik[0][1])
            return True

        langkah = self.kecepatan * dt
        # Iteratif (bukan rekursif) supaya aman saat jarak 0 / langkah besar
        for _ in range(len(self.titik) + 2):
            tx, ty = self.titik[self._indeks]
            dx = tx - self.x
            dy = ty - self.y
            jarak = math.hypot(dx, dy)

            if langkah >= jarak:
                self.x, self.y = float(tx), float(ty)
                self._maju()
                langkah -= jarak
                if self.on_titik:
                    self.on_titik(self._indeks)
                if self.selesai or langkah <= 0:
                    break
            else:
                self.x += dx / jarak * langkah
                self.y += dy / jarak * langkah
                break
        return not self.selesai

    def _maju(self):
        """Pindah ke waypoint berikutnya sesuai mode."""
        if self.mode == "loop":
            self._indeks = (self._indeks + 1) % len(self.titik)
        elif self.mode == "bolak-balik":
            self._indeks += self._arah
            if self._indeks >= len(self.titik):
                self._indeks = len(self.titik) - 2
                self._arah = -1
            elif self._indeks < 0:
                self._indeks = 1
                self._arah = 1
        else:  # sekali
            if self._indeks < len(self.titik) - 1:
                self._indeks += 1
            else:
                self.selesai = True
                if self.on_selesai:
                    self.on_selesai()

    def posisi(self):
        """Posisi saat ini (x, y)."""
        return self.x, self.y

    def indeks_sekarang(self):
        """Index waypoint tujuan saat ini."""
        return self._indeks

    def titik_tujuan(self):
        """Koordinat waypoint tujuan saat ini."""
        return self.titik[self._indeks]

    def reset(self):
        """Kembali ke awal patroli."""
        self._indeks = 0
        self._arah = 1
        self.selesai = False
        self.x = float(self.titik[0][0])
        self.y = float(self.titik[0][1])
        return self


module = SimpleNamespace(
    cari_jalur=cari_jalur,
    panjang_jalur=panjang_jalur,
    jalur_ke_pixel=jalur_ke_pixel,
    IkutiJalur=IkutiJalur,
    Patroli=Patroli,
)
