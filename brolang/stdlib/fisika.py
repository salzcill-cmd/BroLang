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
    """Bodi fisika dengan massa dan kecepatan."""

    def __init__(self, x=0, y=0, massa=1.0):
        self.posisi = Vektor2D(x, y)
        self.kecepatan = Vektor2D(0, 0)
        self.percepatan = Vektor2D(0, 0)
        self.gaya = Vektor2D(0, 0)
        self.massa = massa
        this = self

        this.gesekan = 0.99
        this.elastisitas = 0.8
        this.bounce = 0.8
        this.grounded = False

    def tambah_gaya(self, x, y):
        """Menambahkan gaya ke bodi."""
        self.gaya = self.gaya.tambah(Vektor2D(x, y))

    def tambah_gaya_vec(self, gaya_vec):
        """Menambahkan gaya vektor."""
        self.gaya = self.gaya.tambah(gaya_vec)

    def update(self, dt):
        """Update fisika bodi."""
        if self.massa > 0:
            # F = ma => a = F/m
            self.percepatan = self.gaya.bagi(self.massa)
            # v = v + a*dt
            self.kecepatan = self.kecepatan.tambah(self.percepatan.kali(dt))
            # Apply friction
            self.kecepatan = self.kecepatan.kali(self.gesekan)
            # p = p + v*dt
            self.posisi = self.posisi.tambah(self.kecepatan.kali(dt))

        # Reset gaya
        self.gaya = Vektor2D(0, 0)

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

    def __init__(self):
        self.bodies = []
        this = self

        this.gravitasi = Vektor2D(0, 9.8 * 50)  # Scale for pixels
        this.aktif = True

    def tambah_bodi(self, bodi):
        """Menambahkan bodi ke dunia."""
        self.bodies.append(bodi)

    def hapus_bodi(self, bodi):
        """Menghapus bodi dari dunia."""
        if bodi in self.bodies:
            self.bodies.remove(bodi)

    def update(self, dt):
        """Update seluruh dunia fisika."""
        if not self.aktif:
            return

        for bodi in self.bodies:
            # Apply gravity
            bodi.tambah_gaya_vec(self.gravitasi.kali(bodi.massa))
            bodi.update(dt)

    def check_collision(self, bodi1, bodi2):
        """Mengecek tabrakan antar bodi."""
        jarak = bodi1.posisi.distance_to(bodi2.posisi)
        # Simple circle collision
        radius1 = 16  # Default radius
        radius2 = 16
        return jarak < radius1 + radius2

    def resolve_collision(self, bodi1, bodi2):
        """Menyelesaikan tabrakan."""
        if not self.check_collision(bodi1, bodi2):
            return

        # Simple elastic collision
        dx = bodi2.posisi.x - bodi1.posisi.x
        dy = bodi2.posisi.y - bodi1.posisi.y
        jarak = math.sqrt(dx * dx + dy * dy)

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
        j = -(1 + e) * dvn
        j /= 1 / bodi1.massa + 1 / bodi2.massa

        # Apply impulse
        bodi1.kecepatan.x += j * nx / bodi1.massa
        bodi1.kecepatan.y += j * ny / bodi1.massa
        bodi2.kecepatan.x -= j * nx / bodi2.massa
        bodi2.kecepatan.y -= j * ny / bodi2.massa

    def check_bounds(self, bodi, lebar, tinggi, bounce=True):
        """Mengecek tabrakan dengan batas layar."""
        radius = 16

        if bodi.posisi.x - radius < 0:
            bodi.posisi.x = radius
            if bounce:
                bodi.kecepatan.x *= -bodi.bounce
            else:
                bodi.kecepatan.x = 0
        elif bodi.posisi.x + radius > lebar:
            bodi.posisi.x = lebar - radius
            if bounce:
                bodi.kecepatan.x *= -bodi.bounce
            else:
                bodi.kecepatan.x = 0

        if bodi.posisi.y - radius < 0:
            bodi.posisi.y = radius
            if bounce:
                bodi.kecepatan.y *= -bodi.bounce
            else:
                bodi.kecepatan.y = 0
        elif bodi.posisi.y + radius > tinggi:
            bodi.posisi.y = tinggi - radius
            bodi.grounded = True
            if bounce:
                bodi.kecepatan.y *= -bodi.bounce
            else:
                bodi.kecepatan.y = 0


def buat_bodi(x=0, y=0, massa=1.0):
    """Membuat bodi baru."""
    return Bodi(x, y, massa)


def buat_dunia():
    """Membuat dunia fisika baru."""
    return FisikaWorld()


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
