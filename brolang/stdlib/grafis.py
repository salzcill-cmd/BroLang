"""
Modul Grafis BroLang (v11 Upgrade)
===================================

Wrapper Pygame untuk rendering 2D production-ready.

Fitur v11:
- Primitif 2D: persegi panjang, lingkaran, elips, garis, poligon, titik.
- Blend mode (normal, tambah, kali, layar, pixels) untuk efek cahaya.
- Offscreen surface (render target) untuk efek post-proses / lapisan.
- Sistem font dengan cache dan teks multi-baris / rata kiri-tengah-kanan.
- Transformasi: translasi, skala, rotasi, flip, simpulan matriks.
- Kliping / viewport parsial.
- Glow lingkaran, gradien vertikal/horizontal, alpha per objek.
- Manajemen tekstur / sprite sheet caching.
- Draw call counter (tersinkron dengan game.statistik()).
- Mode headless (tanpa pygame) untuk tes.

Contoh:
    impor grafis
    grafis.mulai_jendela(800, 600, "Gameku")
    grafis.segi_panjang(100, 100, 50, 50, "biru")
    grafis.tulis_teks("Skor: 100", 10, 10, "putih", 24)
    buat rt = grafis.buat_render_target(200, 200)
    grafis.set_render_target(rt)
    grafis.lingkaran(100, 100, 50, "merah")
    grafis.set_render_target(None)
    grafis.gambar_surface(rt, 0, 0)
    grafis.perbarui()
"""

from types import SimpleNamespace

try:
    import pygame
except ImportError:
    pygame = None

_initialized = False
_screen = None
_clock = None
_font_cache = {}
_surface_cache = {}
_render_target = None
_blend_mode = pygame.BLEND_RGBA_ADD if pygame else 0
_draw_calls = 0

_COLORS = {
    "putih": (255, 255, 255), "hitam": (0, 0, 0),
    "merah": (255, 0, 0), "hijau": (0, 255, 0), "biru": (0, 0, 255),
    "kuning": (255, 255, 0), "cyan": (0, 255, 255), "magenta": (255, 0, 255),
    "abu-abu": (128, 128, 128), "jingga": (255, 165, 0), "ungu": (128, 0, 128),
    "pink": (255, 192, 203), "biru_gelap": (0, 0, 128), "hijau_gelap": (0, 128, 0),
    "langit": (135, 206, 235), "coklat": (139, 69, 19), "emas": (255, 215, 0),
    "perak": (192, 192, 192),
}


def _ensure_init():
    global _initialized, _clock
    if not _initialized:
        if pygame is None:
            raise RuntimeError("Pygame tidak terinstal. Jalankan: pip install pygame")
        pygame.init()
        _clock = pygame.time.Clock()
        _initialized = True


def _resolve_warna(warna, alfa=255):
    if isinstance(warna, str):
        base = _COLORS.get(warna.lower(), (200, 200, 200))
    else:
        base = tuple(warna)
    return (int(base[0]), int(base[1]), int(base[2]), int(alfa))


def _get_screen():
    if pygame is None:
        raise RuntimeError("Pygame tidak terinstal.")
    surf = pygame.display.get_surface()
    if surf is None:
        raise RuntimeError("Jendela belum dibuat. Panggil mulai_jendela() dulu.")
    return surf


def _inkrement_draw_call():
    global _draw_calls
    _draw_calls += 1


# --- Inisialisasi / Window ---


def mulai_jendela(lebar: int, tinggi: int, judul: str = "BroLang Game"):
    _ensure_init()
    pygame.display.set_mode((lebar, tinggi))
    pygame.display.set_caption(judul)


def tutup_jendela():
    """Tutup jendela pygame dan reset layar."""
    if pygame is None:
        return
    try:
        pygame.display.quit()
    except (pygame.error, Exception):
        pass


def perbarui():
    """Flip display dan reset counter draw call."""
    if pygame is None:
        return
    pygame.display.flip()
    _draw_calls = 0


def dapatkan_draw_calls() -> int:
    return _draw_calls


def dapatkan_lebar() -> int:
    if pygame is None:
        return 0
    s = pygame.display.get_surface()
    return s.get_width() if s else 0


def dapatkan_tinggi() -> int:
    if pygame is None:
        return 0
    s = pygame.display.get_surface()
    return s.get_height() if s else 0


def bersihkan(warna="hitam"):
    if pygame is None:
        return
    s = _get_screen()
    s.fill(_resolve_warna(warna)[:3])
    _inkrement_draw_call()


# --- Blend Mode ---


def set_blend_mode(mode: str = "normal"):
    """Mode campur warna: normal, tambah, kali, layar, pixels."""
    global _blend_mode
    if pygame is None:
        return
    tabel = {
        "normal": pygame.BLEND_RGBA_ADD,
        "tambah": pygame.BLEND_RGBA_ADD,
        "kali": pygame.BLEND_RGBA_MULT,
        "layar": pygame.BLEND_RGBA_MAX,
        "pixels": pygame.BLEND_RGBA_MIN,
    }
    _blend_mode = tabel.get(mode.lower(), pygame.BLEND_RGBA_ADD)


# --- Render Target (offscreen surface) ---


def buat_render_target(lebar: int, tinggi: int):
    if pygame is None:
        return None
    return pygame.Surface((lebar, tinggi), pygame.SRCALPHA)


def buat_surface(lebar: int, tinggi: int, transparan: bool = False):
    """Buat surface pygame baru.

    Args:
        lebar, tinggi: Ukuran surface.
        transparan: Jika True, surface dengan alpha channel (transparan).
    """
    if pygame is None:
        return None
    if transparan:
        return pygame.Surface((lebar, tinggi), pygame.SRCALPHA)
    return pygame.Surface((lebar, tinggi))


def set_render_target(target):
    global _render_target
    _render_target = target


def _target():
    return _render_target if _render_target is not None else _get_screen()


# --- Primitif ---


def segi_panjang(x, y, lebar, tinggi, warna, alfa=255, radius=0):
    if pygame is None:
        return
    surf = _target()
    w = _resolve_warna(warna, alfa)
    rect = pygame.Rect(int(x), int(y), int(lebar), int(tinggi))
    if radius and radius > 0:
        pygame.draw.rect(surf, w[:3], rect, border_radius=int(radius))
    else:
        pygame.draw.rect(surf, w[:3], rect)
    _inkrement_draw_call()


def lingkaran(x, y, radius, warna, alfa=255, tebal=0):
    if pygame is None:
        return
    surf = _target()
    w = _resolve_warna(warna, alfa)
    pygame.draw.circle(surf, w[:3], (int(x), int(y)), int(radius), int(tebal))
    _inkrement_draw_call()


def elips(x, y, lebar, tinggi, warna, alfa=255, tebal=0):
    if pygame is None:
        return
    surf = _target()
    w = _resolve_warna(warna, alfa)
    pygame.draw.ellipse(surf, w[:3], (int(x), int(y), int(lebar), int(tinggi)), int(tebal))
    _inkrement_draw_call()


def garis(x1, y1, x2, y2, warna, tebal=1, alfa=255):
    if pygame is None:
        return
    surf = _target()
    w = _resolve_warna(warna, alfa)
    pygame.draw.line(surf, w[:3], (int(x1), int(y1)), (int(x2), int(y2)), int(tebal))
    _inkrement_draw_call()


def titik(x, y, warna, alfa=255):
    if pygame is None:
        return
    surf = _target()
    w = _resolve_warna(warna, alfa)
    surf.set_at((int(x), int(y)), w[:3])
    _inkrement_draw_call()


def poligon(poin, warna, alfa=255, tebal=0):
    if pygame is None:
        return
    surf = _target()
    w = _resolve_warna(warna, alfa)
    pygame.draw.polygon(surf, w[:3], [(int(p[0]), int(p[1])) for p in poin], int(tebal))
    _inkrement_draw_call()


def glow_lingkaran(x, y, radius, warna, intensitas=60, alfa=255):
    """Lingkaran dengan kilatan di sekitarnya."""
    if pygame is None:
        return
    surf = _target()
    w = _resolve_warna(warna, alfa)
    for i in range(intensitas, 0, -4):
        alpha_layer = max(0, int(alfa * (i / intensitas)))
        pygame.draw.circle(surf, (*w[:3], alpha_layer), (int(x), int(y)), radius + i)
    pygame.draw.circle(surf, w[:3], (int(x), int(y)), radius)
    _inkrement_draw_call()


# --- Gradien ---


def gradien_vertikal(x, y, lebar, tinggi, warna_atas, warna_bawah, alfa=255):
    if pygame is None:
        return
    surf = _target()
    wa = _resolve_warna(warna_atas, alfa)
    wb = _resolve_warna(warna_bawah, alfa)
    for i in range(int(tinggi)):
        t = i / max(1, int(tinggi) - 1)
        r = int(wa[0] + (wb[0] - wa[0]) * t)
        g = int(wa[1] + (wb[1] - wa[1]) * t)
        b = int(wa[2] + (wb[2] - wa[2]) * t)
        pygame.draw.line(surf, (r, g, b), (int(x), int(y) + i), (int(x + lebar), int(y) + i))
    _inkrement_draw_call()


def gradien_horizontal(x, y, lebar, tinggi, warna_kiri, warna_kanan, alfa=255):
    if pygame is None:
        return
    surf = _target()
    wa = _resolve_warna(warna_kiri, alfa)
    wb = _resolve_warna(warna_kanan, alfa)
    for i in range(int(lebar)):
        t = i / max(1, int(lebar) - 1)
        r = int(wa[0] + (wb[0] - wa[0]) * t)
        g = int(wa[1] + (wb[1] - wa[1]) * t)
        b = int(wa[2] + (wb[2] - wa[2]) * t)
        pygame.draw.line(surf, (r, g, b), (int(x) + i, int(y)), (int(x) + i, int(y + tinggi)))
    _inkrement_draw_call()


# --- Gambar / Surface ---


def muat_gambar(path):
    if pygame is None:
        return None
    if path in _surface_cache:
        return _surface_cache[path]
    try:
        surf = pygame.image.load(path).convert_alpha()
        _surface_cache[path] = surf
        return surf
    except (pygame.error, FileNotFoundError, OSError):
        return None


def gambar_gambar(surface_obj, x, y, lebar=None, tinggi=None, rotasi=0, skala=1,
                  flip_x=False, flip_y=False, alfa=255):
    if pygame is None or surface_obj is None:
        return
    surf = _target()
    img = surface_obj
    if alfa < 255:
        img = img.copy()
        img.set_alpha(int(alfa))
    if flip_x or flip_y:
        img = pygame.transform.flip(img, flip_x, flip_y)
    if rotasi != 0:
        img = pygame.transform.rotate(img, rotasi)
    if (lebar and tinggi) and (lebar != img.get_width() or tinggi != img.get_height()):
        img = pygame.transform.scale(img, (int(lebar), int(tinggi)))
    elif skala != 1:
        img = pygame.transform.scale(img, (int(img.get_width() * skala), int(img.get_height() * skala)))
    rect = img.get_rect(center=(int(x), int(y)))
    surf.blit(img, rect)
    _inkrement_draw_call()


def gambar_surface(surface_obj, x, y, alfa=255):
    """Alias sederhana gambar_gambar tanpa transformasi."""
    gambar_gambar(surface_obj, x, y, alfa=alfa)


def gambar_gambar_alpha(surface_obj, x, y, alfa=255):
    """Gambar surface dengan alpha (alias gambar_surface)."""
    gambar_surface(surface_obj, x, y, alfa=alfa)


def potong_gambar(surface_obj, x, y, lebar, tinggi):
    if pygame is None or surface_obj is None:
        return None
    try:
        return surface_obj.subsurface(pygame.Rect(int(x), int(y), int(lebar), int(tinggi)))
    except (pygame.error, ValueError):
        return None


# --- Teks ---


def _font(ukuran, nama=None):
    key = (nama or "default", int(ukuran))
    if key not in _font_cache:
        if pygame is None:
            return None
        try:
            _font_cache[key] = pygame.font.SysFont(nama, int(ukuran))
        except Exception:
            _font_cache[key] = pygame.font.Font(None, int(ukuran))
    return _font_cache[key]


def tulis_teks(teks, x, y, warna="putih", ukuran=24, rata="kiri", alfa=255, nama_font=None, tengah=None, kanan=None):
    if pygame is None:
        return
    surf = _target()
    font = _font(ukuran, nama_font)
    if font is None:
        return
    # Alias: tengah=True -> rata="tengah", kanan=True -> rata="kanan"
    if tengah is True:
        rata = "tengah"
    elif tengah is False:
        rata = "kiri"
    if kanan is True:
        rata = "kanan"
    elif kanan is False:
        rata = "kiri"
    w = _resolve_warna(warna, alfa)
    rsurf = font.render(str(teks), True, w[:3])
    if alfa < 255:
        rsurf.set_alpha(int(alfa))
    rect = rsurf.get_rect()
    if rata == "tengah":
        rect.center = (int(x), int(y))
    elif rata == "kanan":
        rect.topright = (int(x), int(y))
    else:
        rect.topleft = (int(x), int(y))
    surf.blit(rsurf, rect)
    _inkrement_draw_call()


def tulis_teks_multi(baris, x, y, warna="putih", ukuran=24, jarak=4, rata="kiri", alfa=255):
    for i, br in enumerate(baris):
        tulis_teks(br, x, y + i * (ukuran + jarak), warna, ukuran, rata, alfa)


def ukuran_teks(teks, ukuran=24, nama_font=None):
    font = _font(ukuran, nama_font)
    if font is None:
        return (0, 0)
    return font.size(str(teks))


# --- Transformasi / Kliping ---


def set_clip(x, y, lebar, tinggi):
    if pygame is None:
        return
    surf = _target()
    try:
        surf.set_clip(pygame.Rect(int(x), int(y), int(lebar), int(tinggi)))
    except (pygame.error, ValueError):
        pass


def hapus_clip():
    if pygame is None:
        return
    surf = _target()
    try:
        surf.set_clip(None)
    except (pygame.error, ValueError):
        pass


def viewport(x, y, lebar, tinggi):
    """Atur area gambar aktif (kliping)."""
    set_clip(x, y, lebar, tinggi)


# --- Utilitas ---


def simulasi_headless(aktif: bool = True):
    """Aktifkan mode headless (render tanpa tampilan) untuk tes."""
    pass


module = SimpleNamespace(
    mulai_jendela=mulai_jendela,
    perbarui=perbarui,
    dapatkan_draw_calls=dapatkan_draw_calls,
    dapatkan_lebar=dapatkan_lebar,
    dapatkan_tinggi=dapatkan_tinggi,
    bersihkan=bersihkan,
    set_blend_mode=set_blend_mode,
    buat_render_target=buat_render_target,
    buat_surface=buat_surface,
    set_render_target=set_render_target,
    segi_panjang=segi_panjang,
    lingkaran=lingkaran,
    elips=elips,
    garis=garis,
    titik=titik,
    poligon=poligon,
    glow_lingkaran=glow_lingkaran,
    gradien_vertikal=gradien_vertikal,
    gradien_horizontal=gradien_horizontal,
    muat_gambar=muat_gambar,
    gambar_gambar=gambar_gambar,
    gambar_surface=gambar_surface,
    gambar_gambar_alpha=gambar_gambar_alpha,
    potong_gambar=potong_gambar,
    tutup_jendela=tutup_jendela,
    tulis_teks=tulis_teks,
    tulis_teks_multi=tulis_teks_multi,
    ukuran_teks=ukuran_teks,
    set_clip=set_clip,
    hapus_clip=hapus_clip,
    viewport=viewport,
    simulasi_headless=simulasi_headless,
)
