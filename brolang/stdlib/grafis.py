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
    if _screen is not None:
        return _screen
    # Fallback: pakai display pygame yang aktif (misalnya window dibuat lewat
    # game.buat_jendela() atau pygame.display.set_mode langsung).
    # TIDAK di-cache ke _screen — setelah pygame.quit(), get_surface() kembali
    # None sehingga error "Jendela belum dibuat" tetap muncul di pemakaian baru.
    if pygame is not None:
        surf = pygame.display.get_surface()
        if surf is not None:
            return surf
    raise RuntimeError(
        "Jendela belum dibuat. Panggil grafis.mulai_jendela() dulu."
    )


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


def poligon(titik_titik, warna):
    """Menggambar poligon dari daftar titik [(x1, y1), (x2, y2), ...].

    Contoh:
        grafis.poligon([(100, 100), (200, 50), (250, 180)], "ungu")
    """
    _ensure_init()
    screen = _get_screen()
    color = _COLORS.get(warna, warna) if isinstance(warna, str) else warna
    points = [(int(px), int(py)) for px, py in titik_titik]
    if len(points) >= 3:
        pygame.draw.polygon(screen, color, points)


def segi_panjang_bulat(x, y, lebar, tinggi, radius, warna):
    """Menggambar persegi panjang dengan sudut membulat.

    Contoh:
        grafis.segi_panjang_bulat(100, 100, 200, 60, 15, "biru")
    """
    _ensure_init()
    screen = _get_screen()
    color = _COLORS.get(warna, warna) if isinstance(warna, str) else warna
    r = max(0, min(int(radius), int(min(lebar, tinggi) / 2)))
    pygame.draw.rect(screen, color,
                     (int(x), int(y), int(lebar), int(tinggi)),
                     border_radius=r)


def lingkaran_garis(x, y, radius, warna, ketebalan=1):
    """Menggambar lingkaran outline (tanpa isi)."""
    _ensure_init()
    screen = _get_screen()
    color = _COLORS.get(warna, warna) if isinstance(warna, str) else warna
    pygame.draw.circle(screen, color, (int(x), int(y)), int(radius), int(ketebalan))


def elips(x, y, lebar, tinggi, warna):
    """Menggambar elips di dalam bounding box."""
    _ensure_init()
    screen = _get_screen()
    color = _COLORS.get(warna, warna) if isinstance(warna, str) else warna
    pygame.draw.ellipse(screen, color,
                        (int(x), int(y), int(lebar), int(tinggi)))


def titik(x, y, warna, ukuran=1):
    """Menggambar titik/pixel kecil."""
    _ensure_init()
    screen = _get_screen()
    color = _COLORS.get(warna, warna) if isinstance(warna, str) else warna
    if ukuran <= 1:
        pygame.draw.circle(screen, color, (int(x), int(y)), 1)
    else:
        pygame.draw.circle(screen, color, (int(x), int(y)), int(ukuran))


# --- Teks ---

def _get_font(size: int):
    _ensure_init()
    if size not in _font_cache:
        _font_cache[size] = pygame.font.SysFont(None, size)
    return _font_cache[size]


def tulis_teks(teks: str, x: int, y: int, warna="putih", ukuran=24,
               tengah=False, kanan=False):
    """Menggambar teks di layar (v6.6: opsi perataan).

    Contoh:
        grafis.tulis_teks("Skor: 100", 10, 10, "kuning", 32)
        grafis.tulis_teks("MENU", 400, 100, "putih", 40, tengah=True)
    """
    _ensure_init()
    screen = _get_screen()
    color = _COLORS.get(warna, warna) if isinstance(warna, str) else warna
    font = _get_font(int(ukuran))
    surface = font.render(str(teks), True, color)
    gx = int(x)
    if kanan:
        gx = int(x) - surface.get_width()
    elif tengah:
        gx = int(x) - surface.get_width() // 2
    screen.blit(surface, (gx, int(y)))


def dapatkan_ukuran_teks(teks: str, ukuran=24) -> tuple:
    """Mendapatkan ukuran bounding box teks (lebar, tinggi)."""
    _ensure_init()
    font = _get_font(int(ukuran))
    rect = font.size(str(teks))
    return rect


def tulis_teks_multi(teks: str, x: int, y: int, warna="putih", ukuran=24,
                     jarak_baris=6, tengah=False):
    """Menggambar teks multi-baris (dipisah \n).

    Contoh:
        grafis.tulis_teks_multi("Baris 1\\nBaris 2\\nBaris 3", 50, 50, "kuning", 28)
    """
    _ensure_init()
    screen = _get_screen()
    color = _COLORS.get(warna, warna) if isinstance(warna, str) else warna
    font = _get_font(int(ukuran))
    baris = str(teks).split("\n")
    line_h = int(ukuran) + int(jarak_baris)
    for i, baris_teks in enumerate(baris):
        surface = font.render(baris_teks, True, color)
        bx = int(x)
        if tengah:
            bx = int(x) - surface.get_width() // 2
        screen.blit(surface, (bx, int(y) + i * line_h))


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


def buat_surface(lebar: int, tinggi: int, transparan: bool = False):
    """Membuat surface offscreen untuk menggambar (canvas).

    Contoh:
        buat canvas = grafis.buat_surface(200, 100)
        # ... gambar ke canvas ...
        grafis.gambar_surface(canvas, 100, 100)
    """
    _ensure_init()
    flags = pygame.SRCALPHA if transparan else 0
    return pygame.Surface((int(lebar), int(tinggi)), flags)


def gambar_surface(surface, x: int, y: int):
    """Menggambar surface offscreen ke layar."""
    _ensure_init()
    screen = _get_screen()
    screen.blit(surface, (int(x), int(y)))


def gambar_gambar_alpha(gambar, x: int, y: int, alpha: int = 255):
    """Menggambar gambar dengan tingkat transparansi 0..255 — v6.6.

    Contoh:
        grafis.gambar_gambar_alpha(logo, 100, 100, 128)
    """
    _ensure_init()
    screen = _get_screen()
    alpha = max(0, min(int(alpha), 255))
    if alpha >= 255:
        screen.blit(gambar, (int(x), int(y)))
        return
    try:
        salinan = gambar.copy()
        salinan.set_alpha(alpha)
        screen.blit(salinan, (int(x), int(y)))
    except (pygame.error, ValueError, TypeError):
        screen.blit(gambar, (int(x), int(y)))


# --- Gradien & Efek (v6.6) ---

def gradien_vertikal(x, y, lebar, tinggi, warna_atas, warna_bawah):
    """Gambar persegi panjang dengan gradien vertikal — v6.6.

    Contoh:
        grafis.gradien_vertikal(0, 0, 800, 600, "langit", "biru_gelap")
    """
    _ensure_init()
    screen = _get_screen()
    atas = _COLORS.get(warna_atas, warna_atas) if isinstance(warna_atas, str) else warna_atas
    bawah = _COLORS.get(warna_bawah, warna_bawah) if isinstance(warna_bawah, str) else warna_bawah
    lebar, tinggi = int(lebar), int(tinggi)
    langkah = max(2, min(tinggi, 64))
    for i in range(langkah):
        t = i / max(langkah - 1, 1)
        warna = (int(atas[0] + (bawah[0] - atas[0]) * t),
                 int(atas[1] + (bawah[1] - atas[1]) * t),
                 int(atas[2] + (bawah[2] - atas[2]) * t))
        baris_y = int(y) + int(tinggi * i / langkah)
        baris_tinggi = max(1, int(tinggi / langkah) + 1)
        pygame.draw.rect(screen, warna,
                         (int(x), baris_y, lebar, baris_tinggi))


def gradien_horizontal(x, y, lebar, tinggi, warna_kiri, warna_kanan):
    """Gambar persegi panjang dengan gradien horizontal — v6.6.

    Contoh:
        grafis.gradien_horizontal(100, 400, 300, 50, "merah", "kuning")
    """
    _ensure_init()
    screen = _get_screen()
    kiri = _COLORS.get(warna_kiri, warna_kiri) if isinstance(warna_kiri, str) else warna_kiri
    kanan = _COLORS.get(warna_kanan, warna_kanan) if isinstance(warna_kanan, str) else warna_kanan
    lebar, tinggi = int(lebar), int(tinggi)
    langkah = max(2, min(lebar, 64))
    for i in range(langkah):
        t = i / max(langkah - 1, 1)
        warna = (int(kiri[0] + (kanan[0] - kiri[0]) * t),
                 int(kiri[1] + (kanan[1] - kiri[1]) * t),
                 int(kiri[2] + (kanan[2] - kiri[2]) * t))
        kolom_x = int(x) + int(lebar * i / langkah)
        kolom_lebar = max(1, int(lebar / langkah) + 1)
        pygame.draw.rect(screen, warna,
                         (kolom_x, int(y), kolom_lebar, tinggi))


def glow_lingkaran(x, y, radius, warna, lapisan=4):
    """Gambar lingkaran dengan efek glow (beberapa lapisan) — v6.6.

    Contoh:
        grafis.glow_lingkaran(400, 300, 40, "emas")
    """
    _ensure_init()
    screen = _get_screen()
    warna = _COLORS.get(warna, warna) if isinstance(warna, str) else warna
    cx, cy = int(x), int(y)
    r = max(1, int(radius))
    for i in range(int(lapisan), 0, -1):
        lap = i / max(int(lapisan), 1)
        pygame.draw.circle(screen,
                           (int(warna[0] * lap), int(warna[1] * lap), int(warna[2] * lap)),
                           (cx, cy), int(r * (1.0 + 0.5 * (1.0 - lap))))
    pygame.draw.circle(screen, warna, (cx, cy), max(1, int(r * 0.6)))


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
    poligon=poligon,
    segi_panjang_bulat=segi_panjang_bulat,
    lingkaran_garis=lingkaran_garis,
    elips=elips,
    titik=titik,
    tulis_teks=tulis_teks,
    tulis_teks_multi=tulis_teks_multi,
    dapatkan_ukuran_teks=dapatkan_ukuran_teks,
    muat_gambar=muat_gambar,
    gambar_gambar=gambar_gambar,
    gambar_gambar_putar=gambar_gambar_putar,
    gambar_gambar_scala=gambar_gambar_scala,
    buat_surface=buat_surface,
    gambar_surface=gambar_surface,
    gambar_gambar_alpha=gambar_gambar_alpha,
    gradien_vertikal=gradien_vertikal,
    gradien_horizontal=gradien_horizontal,
    glow_lingkaran=glow_lingkaran,
    tabrakan_segi_panjang=tabrakan_segi_panjang,
    tabrakan_lingkaran=tabrakan_lingkaran,
    tabrakan_titik_segi_panjang=tabrakan_titik_segi_panjang,
    tutup=tutup_jendela,
    warna=_COLORS,
)
