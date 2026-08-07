"""
Modul Vektor BroLang
====================

Kelas vektor untuk game development: Vec2, Vec3, dan fungsi utilitas vektor.

Contoh:
    impor vektor
    buat posisi = vektor.Vec2(10, 20)
    buat kecepatan = vektor.Vec2(5, 0)
    buat posisi_baru = posisi + kecepatan
"""

import math
from types import SimpleNamespace


class Vec2:
    """Vektor 2D."""

    __slots__ = ('x', 'y')

    def __init__(self, x: float = 0.0, y: float = 0.0):
        self.x = float(x)
        self.y = float(y)

    def __add__(self, other: "Vec2") -> "Vec2":
        return Vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Vec2") -> "Vec2":
        return Vec2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> "Vec2":
        return Vec2(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar: float) -> "Vec2":
        return self.__mul__(scalar)

    def __truediv__(self, scalar: float) -> "Vec2":
        if scalar == 0:
            raise ValueError("Tidak bisa membagi vektor dengan nol.")
        return Vec2(self.x / scalar, self.y / scalar)

    def __neg__(self) -> "Vec2":
        return Vec2(-self.x, -self.y)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Vec2):
            return False
        return abs(self.x - other.x) < 1e-9 and abs(self.y - other.y) < 1e-9

    def __repr__(self) -> str:
        return f"Vec2({self.x}, {self.y})"

    def to_dict(self) -> dict:
        return {"x": self.x, "y": self.y}

    def copy(self) -> "Vec2":
        return Vec2(self.x, self.y)

    def panjang(self) -> float:
        """Panjang/magnitudo vektor."""
        return math.sqrt(self.x * self.x + self.y * self.y)

    def panjang_kuadrat(self) -> float:
        """Panjang kuadrat (lebih cepat, tanpa sqrt)."""
        return self.x * self.x + self.y * self.y

    def normalisasi(self) -> "Vec2":
        """Vektor satuan (normalized)."""
        p = self.panjang()
        if p == 0:
            return Vec2(0, 0)
        return Vec2(self.x / p, self.y / p)

    def dot(self, other: "Vec2") -> float:
        """Dot product."""
        return self.x * other.x + self.y * other.y

    def cross(self, other: "Vec2") -> float:
        """Cross product (menghasilkan skalar untuk 2D)."""
        return self.x * other.y - self.y * other.x

    def distance(self, other: "Vec2") -> float:
        """Jarak ke vektor lain."""
        return (self - other).panjang()

    def angle(self) -> float:
        """Sudut vektor dalam radian terhadap sumbu X."""
        return math.atan2(self.y, self.x)

    def sudut(self) -> float:
        """Sudut vektor dalam derajat terhadap sumbu X."""
        return math.degrees(math.atan2(self.y, self.x))

    def rotate(self, radians: float) -> "Vec2":
        """Rotasi vektor sejumlah radian."""
        cos_a = math.cos(radians)
        sin_a = math.sin(radians)
        return Vec2(
            self.x * cos_a - self.y * sin_a,
            self.x * sin_a + self.y * cos_a,
        )

    def rotasi(self, derajat: float) -> "Vec2":
        """Rotasi vektor sejumlah derajat."""
        return self.rotate(math.radians(derajat))

    def lerp(self, other: "Vec2", t: float) -> "Vec2":
        """Linear interpolation antara dua vektor."""
        return Vec2(
            self.x + (other.x - self.x) * t,
            self.y + (other.y - self.y) * t,
        )

    def clamp_panjang(self, max_len: float) -> "Vec2":
        """Batasi panjang vektor."""
        p = self.panjang()
        if p <= max_len:
            return self.copy()
        return self.normalisasi() * max_len

    def proyeksi(self, other: "Vec2") -> "Vec2":
        """Proyeksi vektor ini ke arah vektor lain."""
        d = other.dot(other)
        if d == 0:
            return Vec2(0, 0)
        return other * (self.dot(other) / d)

    def refleksi(self, normal: "Vec2") -> "Vec2":
        """Refleksi vektor terhadap garis normal."""
        n = normal.normalisasi()
        return self - n * (2 * self.dot(n))

    def arah_ke(self, other: "Vec2") -> "Vec2":
        """Vektor satuan dari vektor ini menuju vektor lain."""
        return (other - self).normalisasi()

    def tengah(self, other: "Vec2") -> "Vec2":
        """Titik tengah antara dua vektor."""
        return Vec2((self.x + other.x) / 2, (self.y + other.y) / 2)

    @classmethod
    def dari_polar(cls, panjang: float, sudut_deg: float) -> "Vec2":
        """Membuat vektor dari panjang dan sudut (derajat).

        Contoh:
            buat v = vektor.Vec2.dari_polar(10, 45)  # panjang 10, arah 45 derajat
        """
        rad = math.radians(sudut_deg)
        return cls(math.cos(rad) * panjang, math.sin(rad) * panjang)


class Vec3:
    """Vektor 3D."""

    __slots__ = ('x', 'y', 'z')

    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def __add__(self, other: "Vec3") -> "Vec3":
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: "Vec3") -> "Vec3":
        return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar: float) -> "Vec3":
        return Vec3(self.x * scalar, self.y * scalar, self.z * scalar)

    def __rmul__(self, scalar: float) -> "Vec3":
        return self.__mul__(scalar)

    def __truediv__(self, scalar: float) -> "Vec3":
        if scalar == 0:
            raise ValueError("Tidak bisa membagi vektor dengan nol.")
        return Vec3(self.x / scalar, self.y / scalar, self.z / scalar)

    def __neg__(self) -> "Vec3":
        return Vec3(-self.x, -self.y, -self.z)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Vec3):
            return False
        return (abs(self.x - other.x) < 1e-9 and
                abs(self.y - other.y) < 1e-9 and
                abs(self.z - other.z) < 1e-9)

    def __repr__(self) -> str:
        return f"Vec3({self.x}, {self.y}, {self.z})"

    def to_dict(self) -> dict:
        return {"x": self.x, "y": self.y, "z": self.z}

    def copy(self) -> "Vec3":
        return Vec3(self.x, self.y, self.z)

    def panjang(self) -> float:
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)

    def panjang_kuadrat(self) -> float:
        return self.x * self.x + self.y * self.y + self.z * self.z

    def normalisasi(self) -> "Vec3":
        p = self.panjang()
        if p == 0:
            return Vec3(0, 0, 0)
        return Vec3(self.x / p, self.y / p, self.z / p)

    def dot(self, other: "Vec3") -> float:
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other: "Vec3") -> "Vec3":
        return Vec3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x,
        )

    def distance(self, other: "Vec3") -> float:
        return (self - other).panjang()

    def lerp(self, other: "Vec3", t: float) -> "Vec3":
        return Vec3(
            self.x + (other.x - self.x) * t,
            self.y + (other.y - self.y) * t,
            self.z + (other.z - self.z) * t,
        )


def buat_vec2(x: float = 0.0, y: float = 0.0) -> Vec2:
    """Membuat vektor 2D baru."""
    return Vec2(x, y)


def buat_vec3(x: float = 0.0, y: float = 0.0, z: float = 0.0) -> Vec3:
    """Membuat vektor 3D baru."""
    return Vec3(x, y, z)


def jarak(a: Vec2, b: Vec2) -> float:
    """Jarak antara dua vektor 2D."""
    return a.distance(b)


def dot2(a: Vec2, b: Vec2) -> float:
    """Dot product dua vektor 2D."""
    return a.dot(b)


def buat_polar(panjang: float, sudut_deg: float) -> Vec2:
    """Membuat vektor 2D dari panjang dan sudut derajat."""
    return Vec2.dari_polar(panjang, sudut_deg)


def refleksi(a: Vec2, normal: Vec2) -> Vec2:
    """Refleksi vektor a terhadap normal."""
    return a.refleksi(normal)


def proyeksi(a: Vec2, ke: Vec2) -> Vec2:
    """Proyeksi vektor a ke arah vektor ke."""
    return a.proyeksi(ke)


module = SimpleNamespace(
    Vec2=Vec2,
    Vec3=Vec3,
    buat_vec2=buat_vec2,
    buat_vec3=buat_vec3,
    buat_polar=buat_polar,
    jarak=jarak,
    dot=dot2,
    refleksi=refleksi,
    proyeksi=proyeksi,
)
