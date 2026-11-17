"""
Modul Partikel BroLang (v11 Upgrade)
====================================

Sistem partikel untuk game: ledakan, hujan, api, asap, jejak, bintang, dll.

Fitur v11:
- Emitter partikel dengan kelahiran, umur, kecepatan, gravitasi, gesekan.
- Generator gaya: gravitasi point, angin, tarik (attractor), tolak.
- Jejak (trail) partikel yang menjejak gerak objek.
- Per-partikel warna gradien (awal -> akhir), ukuran berkurang seiring umur.
- Blend mode tambahan untuk efek cahaya ledakan.
- Pooling partikel (reuse objek) untuk menghindari lag GC.
- Emisi berbasis waktu atau burst (ledakan seketak).

Contoh:
    impor partikel
    impor grafis

    buat emiter = partikel.buat_emiter(400, 300)
    emiter.tambah_partikel(ledakan=True, jumlah=60,
                           warna_awal="kuning", warna_akhir="merah",
                           kecepatan=150, umur=1.0, ukuran=6)
    # tiap frame:
    emiter.update(dt)
    emiter.gambar(screen)
"""

import math
import random
from types import SimpleNamespace

try:
    import pygame
except ImportError:
    pygame = None


class Partikel:
    """Satu partikel dengan posisi, kecepatan, umur, warna, ukuran."""

    __slots__ = ('x', 'y', 'vx', 'vy', 'umur', 'umur_maks', 'umur_max',
                 'warna_awal', 'warna_akhir', 'ukuran_awal', 'ukuran_akhir',
                 'aktif', 'gravitasi', 'gesekan', 'rotasi', 'kecepatan_rotasi')

    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.vx = 0.0
        self.vy = 0.0
        self.umur = 0.0
        self.umur_maks = 1.0
        self.umur_max = 1.0
        self.warna_awal = (255, 255, 255)
        self.warna_akhir = (255, 255, 255)
        self.ukuran_awal = 4.0
        self.ukuran_akhir = 0.0
        self.aktif = False
        self.gravitasi = 0.0
        self.gesekan = 0.0
        self.rotasi = 0.0
        self.kecepatan_rotasi = 0.0

    def hidupkan(self, x, y, vx, vy, umur_maks, warna_awal, warna_akhir,
                 ukuran_awal, ukuran_akhir, gravitasi=0, gesekan=0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.umur = 0.0
        self.umur_maks = umur_maks
        self.umur_max = umur_maks
        self.warna_awal = warna_awal
        self.warna_akhir = warna_akhir
        self.ukuran_awal = ukuran_awal
        self.ukuran_akhir = ukuran_akhir
        self.gravitasi = gravitasi
        self.gesekan = gesekan
        self.rotasi = 0.0
        self.aktif = True

    def update(self, dt):
        if not self.aktif:
            return
        self.umur += dt
        if self.umur >= self.umur_maks:
            self.aktif = False
            return
        # Gaya
        self.vy += self.gravitasi * dt
        # Gesekan
        if self.gesekan > 0:
            self.vx *= max(0.0, 1.0 - self.gesekan * dt)
            self.vy *= max(0.0, 1.0 - self.gesekan * dt)
        # Posisi
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.rotasi += self.kecepatan_rotasi * dt

    def progres(self) -> float:
        """Progres kehidupan 0.0 (baru lahir) .. 1.0 (mati)."""
        if self.umur_maks <= 0:
            return 1.0
        return min(self.umur / self.umur_maks, 1.0)

    def warna_saat_ini(self):
        p = self.progres()
        return tuple(int(self.warna_awal[i] +
                         (self.warna_akhir[i] - self.warna_awal[i]) * p)
                     for i in range(3))

    def warna_sekarang(self):
        """Alias legacy untuk warna_saat_ini()."""
        return self.warna_saat_ini()

    def ukuran_saat_ini(self) -> float:
        p = self.progres()
        return self.ukuran_awal + (self.ukuran_akhir - self.ukuran_awal) * p


class Emitter:
    """Emitter partikel: menghasilkan partikel di posisi tertentu."""

    def __init__(self, x=0, y=0, emisi_detik=10, jumlah_max=512):
        self.x = float(x)
        self.y = float(y)
        self.emisi_detik = float(emisi_detik)
        self.jumlah_max = int(jumlah_max)
        self.aktif = True
        self.terlihat = True
        # Pool partikel
        self._pool = [Partikel() for _ in range(jumlah_max)]
        self._aktif_list = []
        self._waktu_emisi = 0.0
        # Default properti partikel baru
        self.default_warna_awal = (255, 255, 255)
        self.default_warna_akhir = (255, 255, 255)
        self.default_ukuran_awal = 4.0
        self.default_ukuran_akhir = 0.0
        self.default_umur = 1.0
        self.default_kecepatan = 50.0
        self.default_arah = 0.0          # derajat
        self.default_serangkaian = 30.0  # derajat penyebaran
        self.default_gravitasi = 0.0
        self.default_gesekan = 0.0

    # --- Alias API untuk kompatibilitas lama (v6.6 / v8.x) ---

    @property
    def kecepatan(self):
        return self.default_kecepatan

    @kecepatan.setter
    def kecepatan(self, v):
        self.default_kecepatan = float(v)

    @property
    def umur(self):
        return self.default_umur

    @umur.setter
    def umur(self, v):
        self.default_umur = float(v)

    @property
    def jumlah(self):
        return self.jumlah_max

    @jumlah.setter
    def jumlah(self, v):
        self.jumlah_max = int(v)

    @property
    def emisi_per_detik(self):
        return self.emisi_detik

    @emisi_per_detik.setter
    def emisi_per_detik(self, v):
        self.emisi_detik = float(v)

    @property
    def warna_awal(self):
        return self.default_warna_awal

    @warna_awal.setter
    def warna_awal(self, v):
        self.default_warna_awal = tuple(v)

    @property
    def warna_akhir(self):
        return self.default_warna_akhir

    @warna_akhir.setter
    def warna_akhir(self, v):
        self.default_warna_akhir = tuple(v)

    @property
    def partikel(self):
        return self._aktif_list

    def emitir(self, jumlah=None):
        """Emit partikel (alias legacy untuk tambah_partikel)."""
        j = self.jumlah_max if jumlah is None else int(jumlah)
        self.tambah_partikel(jumlah=j)

    def jumlah_aktif(self):
        """Jumlah partikel aktif saat ini."""
        return len(self._aktif_list)

    def _ambil_dari_pool(self):
        for p in self._pool:
            if not p.aktif:
                return p
        return None  # pool penuh

    def tambah_partikel(self, x=None, y=None, vx=None, vy=None,
                        umur=None, warna_awal=None, warna_akhir=None,
                        ukuran_awal=None, ukuran_akhir=None,
                        gravitasi=None, gesekan=None, jumlah=1,
                        ledakan=False):
        """Tambah satu atau beberapa partikel.

        Jika vx/vy None, arah default + serangkaian digunakan.
        Jika ledakan=True, partikel tersebar ke segala arah.
        """
        x = self.x if x is None else float(x)
        y = self.y if y is None else float(y)
        umur = self.default_umur if umur is None else float(umur)
        warna_awal = self.default_warna_awal if warna_awal is None else warna_awal
        warna_akhir = self.default_warna_akhir if warna_akhir is None else warna_akhir
        ukuran_awal = self.default_ukuran_awal if ukuran_awal is None else float(ukuran_awal)
        ukuran_akhir = self.default_ukuran_akhir if ukuran_akhir is None else float(ukuran_akhir)
        gravitasi = self.default_gravitasi if gravitasi is None else float(gravitasi)
        gesekan = self.default_gesekan if gesekan is None else float(gesekan)

        for _ in range(jumlah):
            if len(self._aktif_list) >= self.jumlah_max:
                break
            p = self._ambil_dari_pool()
            if p is None:
                break
            if ledakan:
                arah = random.random() * 2 * math.pi
                kecepatan = random.uniform(self.default_kecepatan * 0.5,
                                           self.default_kecepatan * 1.5)
                vx = math.cos(arah) * kecepatan
                vy = math.sin(arah) * kecepatan
            else:
                if vx is None:
                    arah = math.radians(self.default_arah +
                                        random.uniform(-self.default_serangkaian / 2,
                                                       self.default_serangkaian / 2))
                    kecepatan = self.default_kecepatan
                    vx = math.cos(arah) * kecepatan
                    vy = math.sin(arah) * kecepatan
                if vy is None:
                    vy = self.default_kecepatan * math.sin(math.radians(self.default_arah))
            p.hidupkan(x, y, float(vx), float(vy), umur, warna_awal, warna_akhir,
                       ukuran_awal, ukuran_akhir, gravitasi, gesekan)
            self._aktif_list.append(p)

    def ledakan(self, jumlah=40, kecepatan=150, umur=1.0,
                warna_awal=(255, 255, 0), warna_akhir=(255, 0, 0),
                ukuran=6):
        """Ledakan partikel di posisi emitter."""
        self.default_kecepatan = kecepatan
        self.default_umur = umur
        self.default_warna_awal = warna_awal
        self.default_warna_akhir = warna_akhir
        self.default_ukuran_awal = ukuran
        self.default_ukuran_akhir = 0.0
        self.tambah_partikel(jumlah=jumlah, ledakan=True)

    def update(self, dt):
        if not self.aktif:
            return
        # Emisi berkelanjutan
        if self.emisi_detik > 0:
            self._waktu_emisi += dt
            while self._waktu_emisi >= 1.0 / self.emisi_detik:
                self.tambah_partikel()
                self._waktu_emisi -= 1.0 / self.emisi_detik
        # Update partikel aktif
        masih_aktif = []
        for p in self._aktif_list:
            p.update(dt)
            if p.aktif:
                masih_aktif.append(p)
            else:
                self._pool.append(p)  # kembali ke pool
        self._aktif_list = masih_aktif

    def gambar(self, screen, kamera=None):
        if not self.terlihat or pygame is None:
            return
        for p in self._aktif_list:
            ukuran = int(max(1, p.ukuran_saat_ini()))
            warna = p.warna_saat_ini()
            if kamera is not None:
                px, py = kamera.world_to_screen(p.x, p.y)
            else:
                px, py = p.x, p.y
            try:
                pygame.draw.circle(screen, warna, (int(px), int(py)), ukuran)
            except (pygame.error, ValueError):
                pass


class Trail:
    """Jejak partikel yang mengikuti objek bergerak."""

    def __init__(self, target, panjang=10, warna=(200, 200, 200),
                 ukuran=4, umur=0.5):
        self.target = target        # objek dengan .x dan .y
        self.panjang = int(panjang)
        self.warna = warna
        self.ukuran = ukuran
        self.umur = float(umur)
        self._titik = []            # (x, y, waktu_lahir)

    def update(self, dt):
        if self.target is None:
            return
        tx, ty = self.target.x, self.target.y
        now = 0.0
        self._titik.append((tx, ty, now))
        if len(self._titik) > self.panjang:
            self._titik.pop(0)
        # Kurangi umur titik lama
        baru = []
        for (x, y, t) in self._titik:
            if t + self.umur > 0:
                baru.append((x, y, t + dt))
        self._titik = baru

    def jumlah_aktif(self):
        """Jumlah titik jejak saat ini (legacy kompatibel)."""
        return len(self._titik)

    def gambar(self, screen):
        if pygame is None:
            return
        for i, (x, y, t) in enumerate(self._titik):
            p = min(1.0, t / self.umur)
            alfa = int(255 * p)
            uk = max(1, int(self.ukuran * p))
            try:
                pygame.draw.circle(screen, (*self.warna[:3], alfa),
                                   (int(x), int(y)), uk)
            except (pygame.error, TypeError):
                pygame.draw.circle(screen, self.warna[:3], (int(x), int(y)), uk)


# ---------- Gaya ----------

class Gaya:
    """Generator gaya yang diterapkan ke partikel (angin, gravitasi, tarik)."""

    def __init__(self, jenis="angin", kekuatan=50.0, x=0, y=0, radius=200):
        self.jenis = jenis       # "angin", "tarik", "tolak", "gravitasi"
        self.kekuatan = float(kekuatan)
        self.x = float(x)
        self.y = float(y)
        self.radius = float(radius)

    def apply(self, partikel, dt):
        if self.jenis == "angin":
            partikel.vx += self.kekuatan * dt
        elif self.jenis == "gravitasi":
            partikel.vy += self.kekuatan * dt
        elif self.jenis in ("tarik", "tolak"):
            dx = self.x - partikel.x
            dy = self.y - partikel.y
            jarak = math.hypot(dx, dy)
            if jarak == 0 or jarak > self.radius:
                return
            arah_x = dx / jarak
            arah_y = dy / jarak
            faktor = (1.0 - jarak / self.radius) * self.kekuatan * dt
            if self.jenis == "tarik":
                partikel.vx += arah_x * faktor
                partikel.vy += arah_y * faktor
            else:
                partikel.vx -= arah_x * faktor
                partikel.vy -= arah_y * faktor


class SistemPartikel:
    """Kelola banyak emitter + gaya secara terpusat."""

    def __init__(self):
        self.emitters = []
        self.gaya_list = []

    def tambah_emitter(self, emitter):
        self.emitters.append(emitter)

    def tambah_gaya(self, gaya):
        self.gaya_list.append(gaya)

    def update(self, dt):
        for emitter in self.emitters:
            emitter.update(dt)
        # Terapkan gaya ke semua partikel aktif
        for emitter in self.emitters:
            for p in emitter._aktif_list:
                for gaya in self.gaya_list:
                    gaya.apply(p, dt)

    def gambar(self, screen, kamera=None):
        for emitter in self.emitters:
            emitter.gambar(screen, kamera=kamera)


# ---------- Fungsi pembuat ----------

def buat_partikel():
    return Partikel()


def buat_emiter(x=0, y=0, emisi_detik=10, jumlah_max=512):
    return Emitter(x=x, y=y, emisi_detik=emisi_detik, jumlah_max=jumlah_max)


def buat_trail(target, panjang=10, warna=(200, 200, 200), ukuran=4, umur=0.5):
    return Trail(target=target, panjang=panjang, warna=warna,
                 ukuran=ukuran, umur=umur)


def buat_gaya(jenis="angin", kekuatan=50.0, x=0, y=0, radius=200):
    return Gaya(jenis=jenis, kekuatan=kekuatan, x=x, y=y, radius=radius)


def buat_sistem():
    return SistemPartikel()


def buat_titik_ledakan(x, y, jumlah=40, kecepatan=150, umur=1.0,
                       warna_awal=(255, 255, 0), warna_akhir=(255, 0, 0),
                       ukuran=6):
    """Ledakan seketak di (x, y) tanpa emitter persisten."""
    em = Emitter(x=x, y=y, jumlah_max=jumlah)
    em.ledakan(jumlah=jumlah, kecepatan=kecepatan, umur=umur,
               warna_awal=warna_awal, warna_akhir=warna_akhir, ukuran=ukuran)
    return em


# ---------- Legacy API (v6.6 / v8.x kompatibel) ----------


class PartikelEmiter(Emitter):
    """Alias legacy untuk Emitter (nama lama v6.6)."""

    def ledak(self, x, y, jumlah):
        """Ledakan partikel di (x, y) (nama lama: ledak)."""
        self.x = float(x)
        self.y = float(y)
        self.tambah_partikel(jumlah=jumlah, ledakan=True)
        return self


def buat_ledakan(x, y, jumlah=25, warna="jingga"):
    """Ledakan partikel di (x, y) — legacy factory."""
    em = Emitter(x=x, y=y, jumlah_max=jumlah)
    warna_map = {
        "jingga": (255, 150, 40), "merah": (220, 60, 60),
        "kuning": (255, 220, 60), "putih": (255, 255, 255),
        "emas": (255, 215, 0), "merah_gelap": (160, 30, 30),
    }
    wc = warna_map.get(warna, (255, 150, 40))
    em.ledakan(jumlah=jumlah, kecepatan=150, umur=1.0,
               warna_awal=wc, warna_akhir=(255, 0, 0), ukuran=6)
    return em


def buat_hujan(lebar_layar=800, jumlah=20, warna="biru"):
    """Emitter hujan di seluruh lebar layar — legacy factory."""
    em = Emitter(x=lebar_layar / 2, y=0, emisi_detik=0, jumlah_max=jumlah)
    em.default_kecepatan = 120.0
    em.default_arah = 90.0      # jatuh ke bawah
    em.default_serangkaian = 10.0
    em.default_umur = 2.0
    em.default_gravitasi = 200.0
    em.default_warna_awal = warna_map_warna(warna)
    em.default_warna_akhir = em.default_warna_awal
    em.default_ukuran_awal = 2.0
    em.default_ukuran_akhir = 0.0
    # Emit semua sekaligus
    em.tambah_partikel(jumlah=jumlah)
    return em


def buat_asap(x=0, y=0):
    """Emitter asap di (x, y) — legacy factory."""
    em = Emitter(x=x, y=y, emisi_detik=0, jumlah_max=20)
    em.default_kecepatan = 20.0
    em.default_arah = 90.0
    em.default_serangkaian = 40.0
    em.default_umur = 2.0
    em.default_gravitasi = -40.0  # naik ke atas
    em.default_warna_awal = (170, 170, 170)
    em.default_warna_akhir = (90, 90, 90)
    em.default_ukuran_awal = 6.0
    em.default_ukuran_akhir = 12.0
    em.tambah_partikel(jumlah=10)
    return em


def buat_bintang(x=0, y=0, warna="emas"):
    """Emitter bintang di (x, y) — legacy factory. 12 partikel."""
    em = Emitter(x=x, y=y, emisi_detik=0, jumlah_max=12)
    em.default_kecepatan = 60.0
    em.default_umur = 1.0
    wc = warna_map_warna(warna)
    em.default_warna_awal = wc
    em.default_warna_akhir = wc
    em.default_ukuran_awal = 4.0
    em.default_ukuran_akhir = 0.0
    em.tambah_partikel(jumlah=12)
    return em


def buat_trail(x=0, y=0, warna=(200, 200, 200)):
    """Trail sederhana di (x, y) — legacy factory (v6.6 signature)."""
    # Target dummy yang berposisi di (x, y)
    target = SimpleNamespace(x=float(x), y=float(y))
    return Trail(target=target, panjang=10, warna=warna, ukuran=4, umur=0.5)


def warna_map_warna(warna):
    """Resolve nama warna ke tuple RGB."""
    if isinstance(warna, tuple):
        return warna
    tabel = {
        "biru": (70, 130, 255), "merah": (220, 60, 60),
        "hijau": (60, 200, 90), "kuning": (255, 220, 60),
        "jingga": (255, 150, 40), "ungu": (170, 90, 255),
        "cyan": (60, 220, 255), "pink": (255, 90, 180),
        "magenta": (255, 60, 255), "coklat": (150, 90, 50),
        "putih": (255, 255, 255), "hitam": (0, 0, 0),
        "abu-abu": (150, 150, 150), "emas": (255, 215, 0),
        "hijau_gelap": (40, 120, 60), "biru_gelap": (30, 40, 100),
        "merah_gelap": (160, 30, 30), "abu-abu_gelap": (50, 50, 50),
        "langit": (135, 206, 235),
    }
    return tabel.get(str(warna), (200, 200, 200))


module = SimpleNamespace(
    Partikel=Partikel,
    Emitter=Emitter,
    PartikelEmiter=PartikelEmiter,
    Trail=Trail,
    Gaya=Gaya,
    SistemPartikel=SistemPartikel,
    buat_partikel=buat_partikel,
    buat_emiter=buat_emiter,
    buat_trail=buat_trail,
    buat_gaya=buat_gaya,
    buat_sistem=buat_sistem,
    buat_titik_ledakan=buat_titik_ledakan,
    buat_ledakan=buat_ledakan,
    buat_hujan=buat_hujan,
    buat_asap=buat_asap,
    buat_bintang=buat_bintang,
)
