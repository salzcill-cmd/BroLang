"""
Modul Grafis BroLang
====================

Wrapper Pygame untuk rendering 2D.

Contoh:
    impor grafis
    grafis.mulai_jendela(800, 600, "Gameku")
    grafis.segi_panjang(100, 100, 50, 50, "biru")
    grafis.perbarui()
"""

import sys
from types import SimpleNamespace

try:
    import pygame
except ImportError:
    pygame = None

_initialized = False
_screen = None
_clock = None
_surface_cache = {}
_font_cache = {}


def _ensure_init():
    global _initialized, _clock
    if not _initialized:
        if pygame is None:
            raise RuntimeError(
                "Pygame tidak terinstal. Jalankan: pip install pygame"
            )
        pygame.init()
        _clock = pygame.time.Clock()
        _initialized = True


def _get_screen():
    global _screen
    if _screen is None:
        raise RuntimeError(
            "Jendela belum dibuat. Panggil grafis.mulai_jendela() dulu."
        )
    return _screen


# --- Warna ---

_COLORS = {
    "putih": (255, 255, 255),
    "hitam": (0, 0, 0),
    "merah": (255, 0, 0),
    "hijau": (0, 255, 0),
    "biru": (0, 0, 255),
    "kuning": (255, 255, 0),
    "cyan": (0, 255, 255),
    "magenta": (255, 0, 255),
    "abu-abu": (128, 128, 128),
    "abu-abu_terang": (192, 192, 192),
    "abu-abu_gelap": (64, 64, 64),
    "jingga": (255, 165, 0),
    "ungu": (128, 0, 128),
    "coklat": (139, 69, 19),
    "pink": (255, 192, 203),
    "hijau_gelap": (0, 128, 0),
    "biru_gelap": (0, 0, 128),
    "merah_gelap": (128, 0, 0),
    "langit": (135, 206, 235),
    "emas": (255, 215, 0),
}


def buat_warna(nama_atau_r, g=None, b=None, a=255):
    """Membuat warna. Bisa dari nama atau RGB/RGBA.

    Contoh:
        grafis.buat_warna("merah")
        grafis.buat_warna(255, 0, 0)
        grafis.buat_warna(255, 0, 0, 128)
    """
    if g is None and b is None:
        if isinstance(nama_atau_r, str):
            if nama_atau_r in _COLORS:
                c = _COLORS[nama_atau_r]
                return (c[0], c[1], c[2], 255) if a != 255 else c
            raise ValueError(f"Warna '{nama_atau_r}' tidak dikenal.")
        if isinstance(nama_atau_r, (list, tuple)):
            return tuple(nama_atau_r)
    return (int(nama_atau_r), int(g), int(b), int(a))


# --- Jendela ---

def mulai_jendela(lebar: int, tinggi: int, judul: str = "BroLang Game"):
    """Membuat jendela game.

    Contoh:
        grafis.mulai_jendela(800, 600, "Gameku")
    """
    global _screen
    _ensure_init()
    _screen = pygame.display.set_mode((lebar, tinggi))
    pygame.display.set_caption(judul)
    return True


def tutup_jendela():
    """Menutup jendela dan membersihkan Pygame."""
    global _screen, _initialized
    if _initialized:
        pygame.quit()
        _initialized = False
        _screen = None


def perbarui():
    """Update tampilan layar."""
    _ensure_init()
    pygame.display.flip()


def bersihkan(warna=None):
    """Membersihkan layar dengan warna tertentu.

    Contoh:
        grafis.bersihkan("hitam")
        grafis.bersihkan((0, 0, 0))
    """
    _ensure_init()
    screen = _get_screen()
    if warna is None:
        warna = (0, 0, 0)
    elif isinstance(warna, str):
        warna = _COLORS.get(warna, (0, 0, 0))
    screen.fill(warna)


def dapatkan_lebar() -> int:
    """Lebar jendela."""
    return _get_screen().get_width()


def dapatkan_tinggi() -> int:
    """Tinggi jendela."""
    return _get_screen().get_height()


def dapatkan_ukuran() -> tuple:
    """Ukuran jendela (lebar, tinggi)."""
    s = _get_screen()
    return (s.get_width(), s.get_height())


# --- Frame Rate ---

def atur_fps(fps: int):
    """Mengatur frame rate.

    Contoh:
        grafis.atur_fps(60)
    """
    _ensure_init()
    _clock.tick(fps)


def dapatkan_fps() -> float:
    """Mendapatkan FPS aktual."""
    _ensure_init()
    return _clock.get_fps()


def dapatkan_delta() -> float:
    """Delta time dalam detik sejak frame terakhir."""
    _ensure_init()
    return _clock.get_time() / 1000.0


# --- Menggambar ---

def segi_panjang(x, y, lebar, tinggi, warna):
    """Menggambar persegi panjang.

    Contoh:
        grafis.segi_panjang(100, 100, 50, 50, "biru")
    """
    _ensure_init()
    screen = _get_screen()
    color = _COLORS.get(warna, warna) if isinstance(warna, str) else warna
    pygame.draw.rect(screen, color, (int(x), int(y), int(lebar), int(tinggi)))


def lingkaran(x, y, radius, warna):
    """Menggambar lingkaran.

    Contoh:
        grafis.lingkaran(400, 300, 50, "merah")
    """
    _ensure_init()
    screen = _get_screen()
    color = _COLORS.get(warna, warna) if isinstance(warna, str) else warna
    pygame.draw.circle(screen, color, (int(x), int(y)), int(radius))


def garis(x1, y1, x2, y2, warna, ketebalan=1):
    """Menggambar garis.

    Contoh:
        grafis.garis(0, 0, 800, 600, "putih", 2)
    """
    _ensure_init()
    screen = _get_screen()
    color = _COLORS.get(warna, warna) if isinstance(warna, str) else warna
    pygame.draw.line(screen, color, (int(x1), int(y1)), (int(x2), int(y2)), int(ketebalan))


def segitiga(x1, y1, x2, y2, x3, y3, warna):
    """Menggambar segitiga.

    Contoh:
        grafis.segitiga(400, 100, 350, 200, 450, 200, "hijau")
    """
    _ensure_init()
    screen = _get_screen()
    color = _COLORS.get(warna, warna) if isinstance(warna, str) else warna
    pygame.draw.polygon(screen, color, [
        (int(x1), int(y1)), (int(x2), int(y2)), (int(x3), int(y3))
    ])


def persegi(x, y, sisi, warna):
    """Menggambar persegi.

    Contoh:
        grafis.persegi(100, 100, 50, "kuning")
    """
    segi_panjang(x, y, sisi, sisi, warna)


def busur(x, y, radius, sudut_mulai, sudut_akhir, warna, ketebalan=1):
    """Menggambar busur (arc).

    Contoh:
        grafis.busur(400, 300, 50, 0, 180, "cyan")
    """
    _ensure_init()
    screen = _get_screen()
    color = _COLORS.get(warna, warna) if isinstance(warna, str) else warna
    import math
    rect = pygame.Rect(int(x) - int(radius), int(y) - int(radius),
                       int(radius) * 2, int(radius) * 2)
    pygame.draw.arc(screen, color, rect,
                    math.radians(sudut_mulai), math.radians(sudut_akhir), int(ketebalan))


# --- Teks ---

def _get_font(size: int):
    _ensure_init()
    if size not in _font_cache:
        _font_cache[size] = pygame.font.SysFont(None, size)
    return _font_cache[size]


def tulis_teks(teks: str, x: int, y: int, warna="putih", ukuran=24):
    """Menggambar teks di layar.

    Contoh:
        grafis.tulis_teks("Skor: 100", 10, 10, "kuning", 32)
    """
    _ensure_init()
    screen = _get_screen()
    color = _COLORS.get(warna, warna) if isinstance(warna, str) else warna
    font = _get_font(int(ukuran))
    surface = font.render(str(teks), True, color)
    screen.blit(surface, (int(x), int(y)))


def dapatkan_ukuran_teks(teks: str, ukuran=24) -> tuple:
    """Mendapatkan ukuran bounding box teks (lebar, tinggi)."""
    _ensure_init()
    font = _get_font(int(ukuran))
    rect = font.size(str(teks))
    return rect


# --- Gambar/Sprite ---

def muat_gambar(path: str):
    """Memuat gambar dari file.

    Contoh:
        grafis.muat_gambar("assets/player.png")
    """
    _ensure_init()
    return pygame.image.load(path).convert_alpha()


def gambar_gambar(gambar, x: int, y: int):
    """Menggambar gambar di layar.

    Contoh:
        buat player_img = grafis.muat_gambar("player.png")
        grafis.gambar_gambar(player_img, 100, 200)
    """
    _ensure_init()
    screen = _get_screen()
    screen.blit(gambar, (int(x), int(y)))


def gambar_gambar_putar(gambar, x: int, y: int, sudut: float):
    """Menggambar gambar yang dirotasi.

    Contoh:
        grafis.gambar_gambar_putar(player_img, 100, 200, 45)
    """
    _ensure_init()
    screen = _get_screen()
    import math
    rotated = pygame.transform.rotate(gambar, -sudut)
    rect = rotated.get_rect(center=(int(x), int(y)))
    screen.blit(rotated, rect)


def gambar_gambar_scala(gambar, x: int, y: int, sx: float, sy: float):
    """Menggambar gambar yang di-scala.

    Contoh:
        grafis.gambar_gambar_scala(player_img, 100, 200, 2.0, 2.0)
    """
    _ensure_init()
    screen = _get_screen()
    scaled = pygame.transform.scale(gambar, (int(gambar.get_width() * sx),
                                              int(gambar.get_height() * sy)))
    screen.blit(scaled, (int(x), int(y)))


# --- Deteksi Tabrakan ---

def tabrakan_segi_panjang(x1, y1, w1, h1, x2, y2, w2, h2) -> bool:
    """Deteksi tabrakan AABB antara dua persegi panjang.

    Contoh:
        grafis.tabrakan_segi_panjang(px, py, 32, 32, ex, ey, 32, 32)
    """
    return (int(x1) < int(x2) + int(w2) and
            int(x1) + int(w1) > int(x2) and
            int(y1) < int(y2) + int(h2) and
            int(y1) + int(h1) > int(y2))


def tabrakan_lingkaran(x1, y1, r1, x2, y2, r2) -> bool:
    """Deteksi tabrakan antara dua lingkaran."""
    dx = int(x1) - int(x2)
    dy = int(y1) - int(y2)
    dist = dx * dx + dy * dy
    radius_sum = int(r1) + int(r2)
    return dist <= radius_sum * radius_sum


def tabrakan_titik_segi_panjang(px, py, rx, ry, rw, rh) -> bool:
    """Deteksi apakah titik berada di dalam persegi panjang."""
    return (int(rx) <= int(px) <= int(rx) + int(rw) and
            int(ry) <= int(py) <= int(ry) + int(rh))


module = SimpleNamespace(
    mulai_jendela=mulai_jendela,
    tutup_jendela=tutup_jendela,
    perbarui=perbarui,
    bersihkan=bersihkan,
    dapatkan_lebar=dapatkan_lebar,
    dapatkan_tinggi=dapatkan_tinggi,
    dapatkan_ukuran=dapatkan_ukuran,
    atur_fps=atur_fps,
    dapatkan_fps=dapatkan_fps,
    dapatkan_delta=dapatkan_delta,
    buat_warna=buat_warna,
    segi_panjang=segi_panjang,
    lingkaran=lingkaran,
    garis=garis,
    segitiga=segitiga,
    persegi=persegi,
    busur=busur,
    tulis_teks=tulis_teks,
    dapatkan_ukuran_teks=dapatkan_ukuran_teks,
    muat_gambar=muat_gambar,
    gambar_gambar=gambar_gambar,
    gambar_gambar_putar=gambar_gambar_putar,
    gambar_gambar_scala=gambar_gambar_scala,
    tabrakan_segi_panjang=tabrakan_segi_panjang,
    tabrakan_lingkaran=tabrakan_lingkaran,
    tabrakan_titik_segi_panjang=tabrakan_titik_segi_panjang,
    tutup=tutup_jendela,
    warna=_COLORS,
)
