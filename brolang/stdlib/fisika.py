"""
Modul Fisika untuk BroLang Game Development
============================================

Menyediakan simulasi fisika dasar untuk game.

Contoh:
    impor fisika

    buat bodi = fisika.Bodi(100, 100, massa=5.0)
    bodi.tambah_gaya(0, 9.8)
    bodi.update(dt)
"""

import math
from types import SimpleNamespace


class Vektor2D:
    """Vektor 2D untuk fisika."""

    def __init__(self, x=0, y=0):
        self.x = float(x)
        self.y = float(y)

    def tambah(self, other):
        return Vektor2D(self.x + other.x, self.y + other.y)

    def kurang(self, other):
        return Vektor2D(self.x - other.x, self.y - other.y)

    def kali(self, skalar):
        return Vektor2D(self.x * skalar, self.y * skalar)

    def bagi(self, skalar):
        if skalar == 0:
            return Vektor2D(0, 0)
        return Vektor2D(self.x / skalar, self.y / skalar)

    def magnitude(self):
        return math.sqrt(self.x * self.x + self.y * self.y)

    def normalisasi(self):
        mag = self.magnitude()
        if mag == 0:
            return Vektor2D(0, 0)
        return self.bagi(mag)

    def dot(self, other):
        return self.x * other.x + self.y * other.y

    def cross(self, other):
        return self.x * other.y - self.y * other.x

    def angle(self):
        return math.atan2(self.y, self.x)

    def rotate(self, angle):
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        return Vektor2D(
            self.x * cos_a - self.y * sin_a,
            self.x * sin_a + self.y * cos_a
        )

    def distance_to(self, other):
        return (self.kurang(other)).magnitude()

    def copy(self):
        return Vektor2D(self.x, self.y)

    def __repr__(self):
        return f"Vektor2D({self.x}, {self.y})"


class Bodi:
    """Bodi fisika dengan massa, kecepatan, dan ukuran."""

    def __init__(self, x=0, y=0, massa=1.0, radius=16):
        self.posisi = Vektor2D(x, y)
        self.kecepatan = Vektor2D(0, 0)
        self.percepatan = Vektor2D(0, 0)
        self.gaya = Vektor2D(0, 0)
        self.massa = massa
        this = self

        this.radius = radius
        this.lebar = radius * 2
        this.tinggi = radius * 2
        this.gesekan = 0.99
        this.elastisitas = 0.8
        this.bounce = 0.8
        this.grounded = False
        this.gravitasi_diterapkan = False

    def set_radius(self, radius):
        """Set radius bodi (untuk collision lingkaran)."""
        self.radius = radius
        self.lebar = radius * 2
        self.tinggi = radius * 2

    def set_ukuran(self, lebar, tinggi):
        """Set ukuran bodi (untuk collision kotak / bounds)."""
        self.lebar = lebar
        self.tinggi = tinggi
        self.radius = min(lebar, tinggi) / 2

    def tambah_gaya(self, x, y):
        """Menambahkan gaya ke bodi."""
        self.gaya = self.gaya.tambah(Vektor2D(x, y))

    def tambah_gaya_vec(self, gaya_vec):
        """Menambahkan gaya vektor."""
        self.gaya = self.gaya.tambah(gaya_vec)

    def update(self, dt):
        """Update fisika bodi."""
        self.grounded = False
        if self.massa > 0:
            # F = ma => a = F/m
            self.percepatan = self.gaya.bagi(self.massa)
            # v = v + a*dt
            self.kecepatan = self.kecepatan.tambah(self.percepatan.kali(dt))
            # Apply friction (hanya sumbu x agar tidak mengganggu lompatan)
            self.kecepatan.x *= self.gesekan
            # p = p + v*dt
            self.posisi = self.posisi.tambah(self.kecepatan.kali(dt))

        # Reset gaya
        self.gaya = Vektor2D(0, 0)
        self.gravitasi_diterapkan = False

    def set_posisi(self, x, y):
        """Set posisi bodi."""
        self.posisi = Vektor2D(x, y)

    def set_kecepatan(self, vx, vy):
        """Set kecepatan bodi."""
        self.kecepatan = Vektor2D(vx, vy)

    def apply_impulse(self, impulse_x, impulse_y):
        """Menerapkan impulse."""
        if self.massa > 0:
            self.kecepatan = self.kecepatan.tambah(
                Vektor2D(impulse_x, impulse_y).bagi(self.massa)
            )


class FisikaWorld:
    """Dunia fisika untuk simulasi."""

    def __init__(self, gravitasi_y=490.0):
        self.bodies = []
        this = self

        # Gravitasi dalam pixel/detik^2 (default ~9.8 m/s2 di-skala 50x)
        this.gravitasi = Vektor2D(0, gravitasi_y)
        this.aktif = True

    def set_gravitasi(self, x, y):
        """Set gravitasi dunia (pixel/detik^2)."""
        self.gravitasi = Vektor2D(x, y)

    def tambah_bodi(self, bodi):
        """Menambahkan bodi ke dunia."""
        self.bodies.append(bodi)

    def hapus_bodi(self, bodi):
        """Menghapus bodi dari dunia."""
        if bodi in self.bodies:
            self.bodies.remove(bodi)

    def bersihkan(self):
        """Hapus semua bodi dari dunia."""
        self.bodies.clear()

    def update(self, dt):
        """Update seluruh dunia fisika."""
        if not self.aktif:
            return

        for bodi in self.bodies:
            # Apply gravity (sekali per frame)
            if not bodi.gravitasi_diterapkan:
                bodi.tambah_gaya_vec(self.gravitasi.kali(bodi.massa))
                bodi.gravitasi_diterapkan = True
            bodi.update(dt)

    def check_collision(self, bodi1, bodi2):
        """Mengecek tabrakan antar bodi (pakai radius tiap bodi)."""
        jarak = bodi1.posisi.distance_to(bodi2.posisi)
        radius_total = bodi1.radius + bodi2.radius
        return jarak < radius_total

    def resolve_collision(self, bodi1, bodi2):
        """Menyelesaikan tabrakan (impulse + koreksi posisi)."""
        if not self.check_collision(bodi1, bodi2):
            return

        dx = bodi2.posisi.x - bodi1.posisi.x
        dy = bodi2.posisi.y - bodi1.posisi.y
        jarak = math.sqrt(dx * dx + dy * dy)
        radius_total = bodi1.radius + bodi2.radius

        if jarak == 0:
            return

        # Normal vector
        nx = dx / jarak
        ny = dy / jarak

        # Relative velocity
        dvx = bodi1.kecepatan.x - bodi2.kecepatan.x
        dvy = bodi1.kecepatan.y - bodi2.kecepatan.y

        # Relative velocity in collision normal
        dvn = dvx * nx + dvy * ny

        # Do not resolve if velocities are separating
        if dvn > 0:
            return

        # Restitution
        e = min(bodi1.elastisitas, bodi2.elastisitas)

        # Impulse scalar
        total_massa = bodi1.massa + bodi2.massa
        if total_massa == 0:
            return
        j = -(1 + e) * dvn
        j /= 1 / bodi1.massa + 1 / bodi2.massa

        # Apply impulse
        bodi1.kecepatan.x += j * nx / bodi1.massa
        bodi1.kecepatan.y += j * ny / bodi1.massa
        bodi2.kecepatan.x -= j * nx / bodi2.massa
        bodi2.kecepatan.y -= j * ny / bodi2.massa

        # Koreksi posisi agar tidak saling menembus
        overlap = radius_total - jarak
        if overlap > 0:
            kor = overlap / total_massa * 0.8
            bodi1.posisi.x -= nx * kor * bodi2.massa
            bodi1.posisi.y -= ny * kor * bodi2.massa
            bodi2.posisi.x += nx * kor * bodi1.massa
            bodi2.posisi.y += ny * kor * bodi1.massa

    def check_bounds(self, bodi, lebar, tinggi, bounce=True):
        """Mengecek tabrakan dengan batas layar (pakai radius bodi)."""
        r = bodi.radius

        if bodi.posisi.x - r < 0:
            bodi.posisi.x = r
            if bounce:
                bodi.kecepatan.x *= -bodi.bounce
            else:
                bodi.kecepatan.x = 0
        elif bodi.posisi.x + r > lebar:
            bodi.posisi.x = lebar - r
            if bounce:
                bodi.kecepatan.x *= -bodi.bounce
            else:
                bodi.kecepatan.x = 0

        if bodi.posisi.y - r < 0:
            bodi.posisi.y = r
            if bounce:
                bodi.kecepatan.y *= -bodi.bounce
            else:
                bodi.kecepatan.y = 0
        elif bodi.posisi.y + r > tinggi:
            bodi.posisi.y = tinggi - r
            bodi.grounded = True
            if bounce:
                bodi.kecepatan.y *= -bodi.bounce
            else:
                bodi.kecepatan.y = 0

    def bodi_di_posisi(self, x, y, radius=None):
        """Mencari bodi yang mengandung titik (x, y)."""
        for bodi in self.bodies:
            r = radius if radius is not None else bodi.radius
            dx = bodi.posisi.x - x
            dy = bodi.posisi.y - y
            if dx * dx + dy * dy <= r * r:
                return bodi
        return None


def buat_bodi(x=0, y=0, massa=1.0, radius=16):
    """Membuat bodi baru."""
    return Bodi(x, y, massa, radius)


def buat_dunia(gravitasi_y=490.0):
    """Membuat dunia fisika baru."""
    return FisikaWorld(gravitasi_y)


def buat_vektor(x=0, y=0):
    """Membuat vektor 2D baru."""
    return Vektor2D(x, y)


module = SimpleNamespace(
    Vektor2D=Vektor2D,
    Bodi=Bodi,
    FisikaWorld=FisikaWorld,
    buat_bodi=buat_bodi,
    buat_dunia=buat_dunia,
    buat_vektor=buat_vektor,
)
