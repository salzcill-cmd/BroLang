"""
Modul AI untuk BroLang Game Development
========================================

AI musuh siap pakai: mesin status (FSM) + steering behaviors
(kejar, lari, tiba, jelajah) — murni matematika, tanpa dependensi
pygame, jadi mudah diuji & dipakai dengan sprite/fisika mana pun.

Contoh — FSM musuh penjaga:
    impor ai

    buat mesin = ai.FSM("jaga")

    mesin.tambah_status("jaga",
        update=fungsi(dt, agen)
            jika agen.jarak_ke_pemain() < 120 maka
                mesin.ganti_status("kejar")
            selesai
        selesai)
    mesin.tambah_status("kejar",
        masuk=fungsi() tulis "Musuh mengejar!" selesai,
        update=fungsi(dt, agen)
            buat (vx, vy) = ai.kejar(agen.x, agen.y, pemain.x, pemain.y, agen.kecepatan)
            agen.x += vx * dt
            agen.y += vy * dt
        selesai)

    # Tiap frame:
    mesin.update(dt, agen)

Contoh — steering langsung:
    # Kejar target dengan kecepatan maks 120 px/detik
    buat (vx, vy) = ai.kejar(100, 100, 300, 300, 120)
    # Jelajah acak (arah dalam radian; kembali arah baru)
    buat (vx, vy, arah_baru) = ai.jelajah(100, 100, arah, dt, 80)
"""

import math
import random

from types import SimpleNamespace


class FSM:
    """Mesin status terbatas (Finite State Machine).

    Args:
        awal: Nama status awal (opsional).

    Status punya callback opsional:
        masuk(   *args, **kwargs) — dipanggil saat masuk status
        update(  dt, *args, **kwargs) — dipanggil tiap frame
        keluar(  *args, **kwargs) — dipanggil saat pindah keluar
    """

    def __init__(self, awal=None):
        self._status = {}
        self._sekarang = awal
        self._sebelumnya = None
        self._waktu = 0.0
        if awal is not None:
            self._status[str(awal)] = {}

    def tambah_status(self, nama, masuk=None, update=None, keluar=None):
        """Daftarkan status baru (atau timpa callback-nya)."""
        self._status[str(nama)] = {
            "masuk": masuk,
            "update": update,
            "keluar": keluar,
        }
        return self

    def ganti_status(self, nama):
        """Pindah ke status lain. Kembalikan True bila berhasil.

        Memanggil `keluar` status lama & `masuk` status baru.
        """
        nama = str(nama)
        if nama not in self._status:
            return False
        if nama == self._sekarang:
            return True
        lama = self._status.get(self._sekarang, {}).get("keluar")
        if lama:
            lama()
        self._sebelumnya = self._sekarang
        self._sekarang = nama
        self._waktu = 0.0
        baru = self._status[nama].get("masuk")
        if baru:
            baru()
        return True

    def update(self, dt, *args, **kwargs):
        """Panggil callback `update` status saat ini (bila ada)."""
        self._waktu += float(dt)
        fn = self._status.get(self._sekarang, {}).get("update")
        if fn:
            return fn(dt, *args, **kwargs)
        return None

    def status_sekarang(self):
        """Nama status saat ini (atau None)."""
        return self._sekarang

    def status_sebelumnya(self):
        """Nama status sebelumnya (atau None)."""
        return self._sebelumnya

    def sudah_di(self, nama):
        """Apakah sedang berada di status `nama`?"""
        return self._sekarang == str(nama)

    def waktu_di_status(self):
        """Detik yang sudah dihabiskan di status saat ini."""
        return self._waktu

    def semua_status(self):
        """Daftar semua nama status yang terdaftar."""
        return list(self._status.keys())


# ============================================================
# Steering behaviors — murni matematika vektor
# ============================================================

def jarak(x1, y1, x2, y2):
    """Jarak Euclidean antara dua titik."""
    return math.hypot(x2 - x1, y2 - y1)


def arah_ke(x1, y1, x2, y2):
    """Arah (radian) dari titik 1 ke titik 2."""
    return math.atan2(y2 - y1, x2 - x1)


def kejar(x, y, tx, ty, kecepatan_maks):
    """Seek — kejar target dengan kecepatan penuh.

    Returns:
        (vx, vy) vektor kecepatan menuju target.
    """
    dx, dy = tx - x, ty - y
    panjang = math.hypot(dx, dy)
    if panjang <= 0.0001:
        return (0.0, 0.0)
    skala = float(kecepatan_maks) / panjang
    return (dx * skala, dy * skala)


def lari(x, y, tx, ty, kecepatan_maks):
    """Flee — lari MENJAUHI target dengan kecepatan penuh."""
    dx, dy = x - tx, y - ty
    panjang = math.hypot(dx, dy)
    if panjang <= 0.0001:
        return (0.0, 0.0)
    skala = float(kecepatan_maks) / panjang
    return (dx * skala, dy * skala)


def tiba(x, y, tx, ty, kecepatan_maks, radius=16, radius_lambat=64):
    """Arrive — kejar target lalu MELAMBAT saat mendekat.

    Berhenti total bila sudah dalam `radius`. Mulai melambat di dalam
    `radius_lambat`.

    Returns:
        (vx, vy) — (0, 0) bila sudah di dalam radius berhenti.
    """
    dx, dy = tx - x, ty - y
    jauh = math.hypot(dx, dy)
    if jauh <= radius:
        return (0.0, 0.0)
    kecepatan = float(kecepatan_maks)
    if jauh < radius_lambat:
        kecepatan = kecepatan_maks * (jauh - radius) / max(radius_lambat - radius, 1)
    skala = kecepatan / jauh
    return (dx * skala, dy * skala)


def jelajah(x, y, arah_rad, dt, kecepatan_maks, radius=24, sudut_maks=0.6,
            acak=None):
    """Wander — bergerak acak halus (patroli organik).

    Args:
        arah_rad: Arah gerak saat ini (radian).
        dt: Delta time (detik) — menentukan seberapa sering arah berubah.
        radius: Jari-jari lingkaran wander.
        sudut_maks: Maksimal belokan per detik (radian).
        acak: Fungsi random() opsional (untuk determinisme di test).

    Returns:
        (vx, vy, arah_baru) — vektor kecepatan & arah baru.
    """
    rnd = acak or random.random
    if dt <= 0:
        dt = 0.016
    arah = arah_rad + (rnd() * 2 - 1) * sudut_maks * dt * 60
    vx = math.cos(arah) * kecepatan_maks
    vy = math.sin(arah) * kecepatan_maks
    return (vx, vy, arah)


def hindari(x, y, rintangan, radius=32):
    """Hindari rintangan terdekat — dorong menjauh bila terlalu dekat.

    Args:
        rintangan: List titik (ox, oy) atau (ox, oy, r).
        radius: Jarak aman.

    Returns:
        (vx, vy) vektor dorongan (0, 0) bila aman.
    """
    terbaik = None
    terbaik_jauh = None
    for r in rintangan:
        ox, oy = r[0], r[1]
        jari = r[2] if len(r) > 2 else radius
        d = math.hypot(ox - x, oy - y)
        if d < jari + radius:
            if terbaik_jauh is None or d < terbaik_jauh:
                terbaik = (ox, oy)
                terbaik_jauh = d
    if terbaik is None:
        return (0.0, 0.0)
    dx, dy = x - terbaik[0], y - terbaik[1]
    panjang = math.hypot(dx, dy)
    if panjang <= 0.0001:
        return (0.0, -1.0)  # tepat di atas rintangan -> lari ke atas
    kekuatan = (radius + 16) / panjang
    return (dx * kekuatan, dy * kekuatan)


def gabung(v1, v2, bobot1=1.0, bobot2=1.0):
    """Gabung dua vektor (vx, vy) dengan bobot — untuk blending steering."""
    return (v1[0] * bobot1 + v2[0] * bobot2,
            v1[1] * bobot1 + v2[1] * bobot2)


# ============================================================
# Agen — integrasi posisi + kecepatan + steering
# ============================================================

class Agen:
    """Agen AI sederhana: posisi, kecepatan, dan mode steering.

    Mode: "diam", "kejar", "lari", "tiba", "jelajah".

    Contoh:
        buat musuh = ai.Agen(100, 100, kecepatan_maks=120)
        musuh.atur_target(pemain, mode="kejar")
        # Tiap frame:
        musuh.update(dt)
    """

    def __init__(self, x, y, kecepatan_maks=100.0):
        self.x = float(x)
        self.y = float(y)
        self.kecepatan_maks = float(kecepatan_maks)
        self.vx = 0.0
        self.vy = 0.0
        self.target = None       # objek dengan atribut x, y (atau tuple)
        self.mode = "diam"
        self.radius = 16.0       # radius berhenti untuk mode "tiba"
        self.radius_lambat = 64.0
        self.radius_jelajah = 24.0
        self._arah = random.random() * 2 * math.pi
        self._acak = None

    def atur_target(self, target, mode="kejar"):
        """Set target & mode steering ("kejar"/"lari"/"tiba")."""
        self.target = target
        self.mode = mode
        return self

    def atur_mode(self, mode):
        """Ganti mode tanpa mengganti target ("diam"/"jelajah"/...)."""
        self.mode = mode
        return self

    def posisi_target(self):
        """Koordinat (x, y) target saat ini, atau None."""
        t = self.target
        if t is None:
            return None
        if isinstance(t, (tuple, list)):
            return (float(t[0]), float(t[1]))
        return (float(t.x), float(t.y))

    def update(self, dt):
        """Hitung kecepatan sesuai mode lalu majukan posisi."""
        dt = float(dt)
        pos = self.posisi_target()
        if self.mode == "kejar" and pos:
            self.vx, self.vy = kejar(self.x, self.y, pos[0], pos[1], self.kecepatan_maks)
        elif self.mode == "lari" and pos:
            self.vx, self.vy = lari(self.x, self.y, pos[0], pos[1], self.kecepatan_maks)
        elif self.mode == "tiba" and pos:
            self.vx, self.vy = tiba(self.x, self.y, pos[0], pos[1],
                                    self.kecepatan_maks, self.radius, self.radius_lambat)
        elif self.mode == "jelajah":
            self.vx, self.vy, self._arah = jelajah(
                self.x, self.y, self._arah, dt, self.kecepatan_maks,
                self.radius_jelajah, acak=self._acak)
        else:
            self.vx, self.vy = 0.0, 0.0
        self.x += self.vx * dt
        self.y += self.vy * dt
        return self

    def posisi(self):
        """Posisi saat ini (x, y)."""
        return (self.x, self.y)

    def kecepatan(self):
        """Kecepatan saat ini (vx, vy)."""
        return (self.vx, self.vy)


module = SimpleNamespace(
    FSM=FSM,
    Agen=Agen,
    kejar=kejar,
    lari=lari,
    tiba=tiba,
    jelajah=jelajah,
    hindari=hindari,
    gabung=gabung,
    jarak=jarak,
    arah_ke=arah_ke,
)
