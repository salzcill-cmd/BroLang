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

    def lerp(self, other, t):
        """Interpolasi linier menuju vektor lain (t: 0..1)."""
        t = max(0.0, min(1.0, float(t)))
        return Vektor2D(
            self.x + (other.x - self.x) * t,
            self.y + (other.y - self.y) * t,
        )

    def panjang_kuadrat(self):
        """Kuadrat panjang vektor (lebih cepat dari magnitude)."""
        return self.x * self.x + self.y * self.y

    def arah(self):
        """Vektor satuan (alias normalisasi)."""
        return self.normalisasi()

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
        this.mode_collider = "lingkaran"  # "lingkaran" atau "persegi" (v6.6)
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
        self.mode_collider = "lingkaran"
        return self

    def set_persegi(self, lebar, tinggi):
        """Set ukuran & mode collider persegi (AABB) — v6.6.

        Posisi bodi tetap titik tengah; lebar/tinggi dipakai untuk
        tabrakan kotak-kotak dan bounds.
        """
        self.lebar = float(lebar)
        self.tinggi = float(tinggi)
        self.radius = min(self.lebar, self.tinggi) / 2
        self.mode_collider = "persegi"
        return self

    def set_ukuran(self, lebar, tinggi):
        """Set ukuran bodi (untuk collision kotak / bounds)."""
        self.lebar = lebar
        self.tinggi = tinggi
        self.radius = min(lebar, tinggi) / 2
        return self

    def _rect(self):
        """Rect bodi persegi: (kiri, atas, kanan, bawah) — posisi di tengah."""
        return (self.posisi.x - self.lebar / 2,
                self.posisi.y - self.tinggi / 2,
                self.posisi.x + self.lebar / 2,
                self.posisi.y + self.tinggi / 2)

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

    def set_massa(self, massa):
        """Set massa bodi."""
        self.massa = float(massa)
        return self

    def berhenti(self):
        """Hentikan bodi: kecepatan & percepatan jadi nol."""
        self.kecepatan = Vektor2D(0, 0)
        self.percepatan = Vektor2D(0, 0)
        self.gaya = Vektor2D(0, 0)
        return self

    def batasi_kecepatan(self, maks):
        """Batasi besar kecepatan (speed) ke nilai maksimum."""
        mag = self.kecepatan.magnitude()
        if mag > maks > 0:
            self.kecepatan = self.kecepatan.kali(maks / mag)
        return self


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

    def jumlah_bodi(self):
        """Jumlah bodi dalam dunia."""
        return len(self.bodies)

    def gravitasi_sekarang(self):
        """Salinan vektor gravitasi saat ini."""
        return self.gravitasi.copy()

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
        """Mengecek tabrakan antar bodi (lingkaran & persegi, bisa campuran)."""
        if bodi1.mode_collider == "persegi" and bodi2.mode_collider == "persegi":
            x1, y1, x2, y2 = bodi1._rect()
            x3, y3, x4, y4 = bodi2._rect()
            return x1 < x4 and x2 > x3 and y1 < y4 and y2 > y3
        if bodi1.mode_collider == "lingkaran" and bodi2.mode_collider == "lingkaran":
            return bodi1.posisi.distance_to(bodi2.posisi) < bodi1.radius + bodi2.radius
        # Campuran: lingkaran vs persegi
        lingkaran, persegi = (bodi1, bodi2) if bodi1.mode_collider == "lingkaran" else (bodi2, bodi1)
        x1, y1, x2, y2 = persegi._rect()
        cx, cy = lingkaran.posisi.x, lingkaran.posisi.y
        tx = max(x1, min(cx, x2))
        ty = max(y1, min(cy, y2))
        dx = cx - tx
        dy = cy - ty
        return dx * dx + dy * dy < lingkaran.radius * lingkaran.radius

    def resolve_collision(self, bodi1, bodi2):
        """Menyelesaikan tabrakan (impulse + koreksi posisi).

        Mendukung lingkaran, persegi, dan campuran. Untuk persegi-persegi
        koreksi posisi dipisah sepanjang sumbu penetrasi terkecil.
        """
        if not self.check_collision(bodi1, bodi2):
            return

        # ---- Persegi vs persegi: dorong sepanjang sumbu penetrasi terkecil
        if bodi1.mode_collider == "persegi" and bodi2.mode_collider == "persegi":
            x1, y1, x2, y2 = bodi1._rect()
            x3, y3, x4, y4 = bodi2._rect()
            overlap_x = min(x2, x4) - max(x1, x3)
            overlap_y = min(y2, y4) - max(y1, y3)
            # Bodi massa 0 = statis (tidak terdorong). Yang lain didorong penuh.
            m1 = bodi1.massa
            m2 = bodi2.massa
            total_massa = m1 + m2
            if total_massa <= 0:
                return
            # Bobot dorongan: statis (m=0) tidak bergerak, dinamis bergerak penuh
            if m2 == 0:
                w1, w2 = 1.0, 0.0
            elif m1 == 0:
                w1, w2 = 0.0, 1.0
            else:
                w1 = m2 / total_massa
                w2 = m1 / total_massa
            if overlap_x < overlap_y:
                arah = 1.0 if bodi1.posisi.x < bodi2.posisi.x else -1.0
                dorong = overlap_x
                bodi1.posisi.x -= arah * dorong * w1
                bodi2.posisi.x += arah * dorong * w2
                # Impulse sumbu x: hanya jika relatif bergerak mendekat
                # (arah * dv >= 0). Bodi statis (m=0) dihentikan dinamisnya.
                dvx = bodi1.kecepatan.x - bodi2.kecepatan.x
                if arah * dvx >= 0:
                    e = min(bodi1.elastisitas, bodi2.elastisitas)
                    if m2 == 0:
                        bodi1.kecepatan.x = 0
                    elif m1 == 0:
                        bodi2.kecepatan.x = 0
                    else:
                        j = -(1 + e) * dvx * arah
                        j /= 1 / m1 + 1 / m2
                        bodi1.kecepatan.x += j * arah / m1
                        bodi2.kecepatan.x -= j * arah / m2
            else:
                arah = 1.0 if bodi1.posisi.y < bodi2.posisi.y else -1.0
                dorong = overlap_y
                bodi1.posisi.y -= arah * dorong * w1
                bodi2.posisi.y += arah * dorong * w2
                dvy = bodi1.kecepatan.y - bodi2.kecepatan.y
                if arah * dvy >= 0:
                    e = min(bodi1.elastisitas, bodi2.elastisitas)
                    if m2 == 0:
                        # Pemain mendarat di lantai statis
                        bodi1.kecepatan.y = 0
                        bodi1.grounded = True
                    elif m1 == 0:
                        bodi2.kecepatan.y = 0
                        bodi2.grounded = True
                    else:
                        j = -(1 + e) * dvy * arah
                        j /= 1 / m1 + 1 / m2
                        bodi1.kecepatan.y += j * arah / m1
                        bodi2.kecepatan.y -= j * arah / m2
            return

        # ---- Lingkaran (atau campuran): normal dari pusat / titik terdekat
        if bodi1.mode_collider == "persegi" or bodi2.mode_collider == "persegi":
            lingkaran, persegi = (bodi1, bodi2) if bodi1.mode_collider == "lingkaran" else (bodi2, bodi1)
            x1, y1, x2, y2 = persegi._rect()
            cx, cy = lingkaran.posisi.x, lingkaran.posisi.y
            tx = max(x1, min(cx, x2))
            ty = max(y1, min(cy, y2))
            nx = cx - tx
            ny = cy - ty
            jarak = math.hypot(nx, ny)
            if jarak == 0:
                nx, ny, jarak = 0.0, -1.0, 0.0001
            else:
                nx, ny = nx / jarak, ny / jarak
            overlap = lingkaran.radius - jarak
            total_massa = lingkaran.massa + persegi.massa
            if total_massa <= 0:
                return
            # Bodi massa 0 = statis (tidak bergerak)
            m_ling = lingkaran.massa
            m_pers = persegi.massa
            if m_pers == 0:
                w_ling, w_pers = 1.0, 0.0
            elif m_ling == 0:
                w_ling, w_pers = 0.0, 1.0
            else:
                w_ling = m_pers / total_massa
                w_pers = m_ling / total_massa
            lingkaran.posisi.x += nx * overlap * w_ling
            lingkaran.posisi.y += ny * overlap * w_ling
            persegi.posisi.x -= nx * overlap * w_pers
            persegi.posisi.y -= ny * overlap * w_pers
            # Impulse: hentikan komponen kecepatan yang menembus (normal
            # menunjuk dari persegi ke lingkaran, jadi mendekat = dvn < 0)
            dvx = lingkaran.kecepatan.x - persegi.kecepatan.x
            dvy = lingkaran.kecepatan.y - persegi.kecepatan.y
            dvn = dvx * nx + dvy * ny
            if dvn < 0 and jarak > 0:
                e = min(lingkaran.elastisitas, persegi.elastisitas)
                if m_pers == 0:
                    if ny < -0.5:
                        # Mendarat di atas lantai statis -> berhenti (tanpa
                        # pantul), anti-jitter. Normal menunjuk dari permukaan
                        # ke pusat lingkaran: bola DI ATAS lantai -> ny < 0
                        lingkaran.kecepatan.x -= dvn * nx
                        lingkaran.kecepatan.y -= dvn * ny
                        lingkaran.grounded = True
                    else:
                        # Tabrakan samping dinding: pantulkan dengan elastisitas
                        lingkaran.kecepatan.x -= (1 + e) * dvn * nx
                        lingkaran.kecepatan.y -= (1 + e) * dvn * ny
                elif m_ling == 0:
                    persegi.kecepatan.x += (1 + e) * dvn * nx
                    persegi.kecepatan.y += (1 + e) * dvn * ny
                else:
                    j = -(1 + e) * dvn
                    j /= 1 / m_ling + 1 / m_pers
                    lingkaran.kecepatan.x += j * nx / m_ling
                    lingkaran.kecepatan.y += j * ny / m_ling
                    persegi.kecepatan.x -= j * nx / m_pers
                    persegi.kecepatan.y -= j * ny / m_pers
            return

        # ---- Lingkaran vs lingkaran
        dx = bodi2.posisi.x - bodi1.posisi.x
        dy = bodi2.posisi.y - bodi1.posisi.y
        jarak = math.sqrt(dx * dx + dy * dy)
        radius_total = bodi1.radius + bodi2.radius

        if jarak == 0:
            return

        # Normal vector (dari bodi1 ke bodi2)
        nx = dx / jarak
        ny = dy / jarak

        total_massa = bodi1.massa + bodi2.massa
        if total_massa <= 0:
            return

        # ---- Satu bodi statis (massa 0): bodi statis diam, yang dinamis
        # didorong keluar & dipantulkan. Normal diarahkan dari bodi statis ke
        # bodi dinamis (konsisten dengan branch campuran), sehingga urutan
        # argumen resolve_collision tidak memengaruhi hasil.
        if bodi1.massa == 0 and bodi2.massa > 0:
            # bodi1 statis: normal dari bodi1 ke bodi2 = (nx, ny)
            snx, sny = nx, ny
            dinamis, statis = bodi2, bodi1
        elif bodi2.massa == 0 and bodi1.massa > 0:
            # bodi2 statis: normal dari bodi2 ke bodi1 = -(nx, ny)
            snx, sny = -nx, -ny
            dinamis, statis = bodi1, bodi2
        else:
            snx = sny = None
            dinamis = statis = None

        if dinamis is not None:
            # Koreksi posisi: dorong dinamis keluar dari statis (statis diam)
            overlap = radius_total - jarak
            if overlap > 0:
                dinamis.posisi.x += snx * overlap
                dinamis.posisi.y += sny * overlap
            # Impulse: hentikan komponen kecepatan yang menembus (mendekat
            # = dvn < 0; normal menunjuk dari statis ke dinamis)
            dvn = ((dinamis.kecepatan.x - statis.kecepatan.x) * snx
                   + (dinamis.kecepatan.y - statis.kecepatan.y) * sny)
            if dvn < 0:
                # Mendarat di atas bodi statis -> berhenti (tanpa pantul),
                # konsisten dengan lantai statis persegi (anti-jitter).
                if sny < -0.5:
                    dinamis.kecepatan.x -= dvn * snx
                    dinamis.kecepatan.y -= dvn * sny
                    dinamis.grounded = True
                else:
                    # Tabrakan samping: pantulkan dengan elastisitas
                    e = min(dinamis.elastisitas, statis.elastisitas)
                    dinamis.kecepatan.x -= (1 + e) * dvn * snx
                    dinamis.kecepatan.y -= (1 + e) * dvn * sny
            return

        # ---- Keduanya dinamis: impulse + koreksi posisi standar
        # Relative velocity
        dvx = bodi1.kecepatan.x - bodi2.kecepatan.x
        dvy = bodi1.kecepatan.y - bodi2.kecepatan.y

        # Relative velocity in collision normal. Normal menunjuk dari bodi1
        # ke bodi2, jadi bodi1 MENDEKAT saat dvn > 0.
        dvn = dvx * nx + dvy * ny

        # Resolve hanya saat mendekat; bodi yang saling menjauh diabaikan
        if dvn <= 0:
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

        # Koreksi posisi agar tidak saling menembus
        overlap = radius_total - jarak
        if overlap > 0:
            kor = overlap / total_massa * 0.8
            bodi1.posisi.x -= nx * kor * bodi2.massa
            bodi1.posisi.y -= ny * kor * bodi2.massa
            bodi2.posisi.x += nx * kor * bodi1.massa
            bodi2.posisi.y += ny * kor * bodi1.massa

    def check_bounds(self, bodi, lebar, tinggi, bounce=True):
        """Mengecek tabrakan dengan batas layar (pakai radius/half-size bodi)."""
        if bodi.mode_collider == "persegi":
            setengah_x = bodi.lebar / 2
            setengah_y = bodi.tinggi / 2
        else:
            setengah_x = bodi.radius
            setengah_y = bodi.radius

        if bodi.posisi.x - setengah_x < 0:
            bodi.posisi.x = setengah_x
            if bounce:
                bodi.kecepatan.x *= -bodi.bounce
            else:
                bodi.kecepatan.x = 0
        elif bodi.posisi.x + setengah_x > lebar:
            bodi.posisi.x = lebar - setengah_x
            if bounce:
                bodi.kecepatan.x *= -bodi.bounce
            else:
                bodi.kecepatan.x = 0

        if bodi.posisi.y - setengah_y < 0:
            bodi.posisi.y = setengah_y
            if bounce:
                bodi.kecepatan.y *= -bodi.bounce
            else:
                bodi.kecepatan.y = 0
        elif bodi.posisi.y + setengah_y > tinggi:
            bodi.posisi.y = tinggi - setengah_y
            bodi.grounded = True
            if bounce:
                bodi.kecepatan.y *= -bodi.bounce
            else:
                bodi.kecepatan.y = 0

    def bodi_di_posisi(self, x, y, radius=None):
        """Mencari bodi yang mengandung titik (x, y)."""
        for bodi in self.bodies:
            if bodi.mode_collider == "persegi":
                x1, y1, x2, y2 = bodi._rect()
                if x1 <= x <= x2 and y1 <= y <= y2:
                    return bodi
                continue
            r = radius if radius is not None else bodi.radius
            dx = bodi.posisi.x - x
            dy = bodi.posisi.y - y
            if dx * dx + dy * dy <= r * r:
                return bodi
        return None

    def cari_bodi_di_area(self, x, y, lebar, tinggi):
        """Mencari semua bodi yang menabrak area persegi (broadphase) — v6.6.

        Args:
            x, y: Posisi kiri-atas area.
            lebar, tinggi: Ukuran area.

        Returns:
            List bodi yang tumpang tindih dengan area.
        """
        hasil = []
        for bodi in self.bodies:
            if bodi.mode_collider == "persegi":
                x1, y1, x2, y2 = bodi._rect()
                if x1 < x + lebar and x2 > x and y1 < y + tinggi and y2 > y:
                    hasil.append(bodi)
            else:
                cx, cy = bodi.posisi.x, bodi.posisi.y
                r = bodi.radius
                # Rect terdekat ke pusat lingkaran
                tx = max(x, min(cx, x + lebar))
                ty = max(y, min(cy, y + tinggi))
                dx = cx - tx
                dy = cy - ty
                if dx * dx + dy * dy <= r * r:
                    hasil.append(bodi)
        return hasil

    def raycast(self, x1, y1, x2, y2):
        """Raycast segmen garis terhadap semua bodi — v6.6.

        Args:
            x1, y1: Titik awal (pixel).
            x2, y2: Titik akhir (pixel).

        Returns:
            (bodi, titik_x, titik_y) untuk tabrakan TERDEKAT, atau None.
        """
        terdekat = None
        t_terdekat = float("inf")
        for bodi in self.bodies:
            if bodi.mode_collider == "persegi":
                t = self._ray_rect(x1, y1, x2, y2, bodi._rect())
            else:
                t = self._ray_lingkaran(x1, y1, x2, y2, bodi.posisi.x, bodi.posisi.y, bodi.radius)
            if t is not None and 0 <= t <= 1 and t < t_terdekat:
                t_terdekat = t
                terdekat = bodi
        if terdekat is None:
            return None
        titik_x = x1 + (x2 - x1) * t_terdekat
        titik_y = y1 + (y2 - y1) * t_terdekat
        return (terdekat, titik_x, titik_y)

    @staticmethod
    def _ray_lingkaran(x1, y1, x2, y2, cx, cy, r):
        """t di mana segmen menyentuh lingkaran, atau None."""
        dx = x2 - x1
        dy = y2 - y1
        fx = x1 - cx
        fy = y1 - cy
        a = dx * dx + dy * dy
        if a == 0:
            return None
        b = 2 * (fx * dx + fy * dy)
        c = fx * fx + fy * fy - r * r
        disc = b * b - 4 * a * c
        if disc < 0:
            return None
        sqrt_disc = math.sqrt(disc)
        t = (-b - sqrt_disc) / (2 * a)
        if t < 0:
            t = (-b + sqrt_disc) / (2 * a)
        if 0 <= t <= 1:
            return t
        return None

    @staticmethod
    def _ray_rect(x1, y1, x2, y2, rect):
        """t di mana segmen menyentuh rect (slab method), atau None."""
        kiri, atas, kanan, bawah = rect
        dx = x2 - x1
        dy = y2 - y1
        tmin, tmax = 0.0, 1.0
        if dx == 0:
            if x1 < kiri or x1 > kanan:
                return None
        else:
            t1 = (kiri - x1) / dx
            t2 = (kanan - x1) / dx
            if t1 > t2:
                t1, t2 = t2, t1
            tmin = max(tmin, t1)
            tmax = min(tmax, t2)
            if tmin > tmax:
                return None
        if dy == 0:
            if y1 < atas or y1 > bawah:
                return None
        else:
            t1 = (atas - y1) / dy
            t2 = (bawah - y1) / dy
            if t1 > t2:
                t1, t2 = t2, t1
            tmin = max(tmin, t1)
            tmax = min(tmax, t2)
            if tmin > tmax:
                return None
        return tmin


def buat_bodi(x=0, y=0, massa=1.0, radius=16):
    """Membuat bodi baru."""
    return Bodi(x, y, massa, radius)


def buat_dunia(gravitasi_y=490.0):
    """Membuat dunia fisika baru."""
    return FisikaWorld(gravitasi_y)


def buat_vektor(x=0, y=0):
    """Membuat vektor 2D baru."""
    return Vektor2D(x, y)


def vektor_dari_sudut(sudut, panjang=1.0):
    """Vektor 2D dari sudut (radian) dan panjang (v7.1).

    Contoh:
        buat v = fisika.vektor_dari_sudut(0)      # (1, 0)
        buat v = fisika.vektor_dari_sudut(1.5708, 5)  # ~(0, 5)
    """
    return Vektor2D(math.cos(sudut) * panjang, math.sin(sudut) * panjang)


def gravitasi_bumi():
    """Vektor gravitasi bumi standar (~9.8 m/s² diskala ke pixel)."""
    return Vektor2D(0, 490.0)


def gravitasi_bulan():
    """Vektor gravitasi bulan (~1.62 m/s² diskala ke pixel)."""
    return Vektor2D(0, 81.0)


module = SimpleNamespace(
    Vektor2D=Vektor2D,
    Bodi=Bodi,
    FisikaWorld=FisikaWorld,
    buat_bodi=buat_bodi,
    buat_dunia=buat_dunia,
    buat_vektor=buat_vektor,
    # v7.1
    vektor_dari_sudut=vektor_dari_sudut,
    gravitasi_bumi=gravitasi_bumi,
    gravitasi_bulan=gravitasi_bulan,
)
