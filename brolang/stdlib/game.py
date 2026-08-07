"""
Modul Game BroLang
==================

Game loop, scene management, dan utilitas game.

Game loop menggunakan modul `input` sebagai satu-satunya konsumen event
queue pygame. Di awal tiap frame: `input._update()` menguras event,
lalu game loop membaca event QUIT/ESC/on_event dari `input.ambil_events()`.
Dengan begitu modul input dan game loop tidak berebut event.

Contoh:
    impor game
    game.buat_jendela(800, 600, "Gameku")
    game.tambah_scene("utama", update_utama, gambar_utama)
    game.ganti_scene("utama")
    game.mulai()
"""

import sys
from types import SimpleNamespace

try:
    import pygame
except ImportError:
    pygame = None


# --- Game State ---

class _GameState:
    def __init__(self):
        self.running = False
        self.paused = False
        self.scenes = {}
        self.current_scene = None
        self.data = {}
        self.lebar = 800
        self.tinggi = 600
        self.judul = "BroLang Game"
        self.fps = 60
        self.latar_warna = (0, 0, 0)
        self.tampil_fps = False
        self.esc_keluar = True
        self.on_init = None
        self.on_event = None
        self.on_pause = None
        self.on_resume = None
        self.on_exit = None

_state = _GameState()


# --- Jendela ---

def atur_fps(fps: int):
    """Mengatur target FPS.

    Contoh:
        game.atur_fps(60)
    """
    _state.fps = int(fps)


def dapatkan_data() -> dict:
    """Akses data global game (untuk menyimpan skor, status, dll).

    Contoh:
        game.dapatkan_data()["skor"] = 0
    """
    return _state.data


def set_latar_warna(warna):
    """Mengatur warna latar layar.

    Contoh:
        game.set_latar_warna("biru_gelap")
        game.set_latar_warna((10, 10, 30))
    """
    _state.latar_warna = _resolve_warna(warna)


def _resolve_warna(warna):
    if isinstance(warna, str):
        _COLORS = {
            "putih": (255, 255, 255), "hitam": (0, 0, 0),
            "merah": (255, 0, 0), "hijau": (0, 255, 0),
            "biru": (0, 0, 255), "kuning": (255, 255, 0),
            "cyan": (0, 255, 255), "magenta": (255, 0, 255),
            "abu-abu": (128, 128, 128), "jingga": (255, 165, 0),
            "ungu": (128, 0, 128), "pink": (255, 192, 203),
            "biru_gelap": (0, 0, 128), "hijau_gelap": (0, 128, 0),
            "langit": (135, 206, 235),
        }
        return _COLORS.get(warna, (0, 0, 0))
    return tuple(warna)


def set_tampil_fps(aktif: bool = True):
    """Tampilkan FPS di pojok layar.

    Contoh:
        game.set_tampil_fps(True)
    """
    _state.tampil_fps = bool(aktif)


def set_esc_keluar(aktif: bool = True):
    """ESC langsung menutup game (default True)."""
    _state.esc_keluar = bool(aktif)


# --- Scene Management ---

def tambah_scene(nama: str, fungsi_update=None, fungsi_gambar=None):
    """Menambah scene baru.

    Contoh:
        game.tambah_scene("menu", update_menu, gambar_menu)
        game.tambah_scene("main", update_main, gambar_main)
    """
    _state.scenes[nama] = {
        "update": fungsi_update,
        "gambar": fungsi_gambar,
    }


def ganti_scene(nama: str):
    """Beralih ke scene lain.

    Contoh:
        game.ganti_scene("main")
    """
    if nama not in _state.scenes:
        raise ValueError(f"Scene '{nama}' tidak ditemukan.")
    _state.current_scene = nama


def dapatkan_scene_sekarang() -> str:
    """Mendapatkan nama scene aktif."""
    return _state.current_scene


def hapus_scene(nama: str):
    """Menghapus scene."""
    _state.scenes.pop(nama, None)


# --- Pause / Resume ---

def pause():
    """Pause game loop (update & gambar di-skip, loop tetap hidup)."""
    if not _state.paused:
        _state.paused = True
        if _state.on_pause:
            _state.on_pause()


def resume():
    """Lanjutkan game loop setelah pause."""
    if _state.paused:
        _state.paused = False
        if _state.on_resume:
            _state.on_resume()


def set_pause(nilai: bool):
    """Set status pause."""
    if nilai:
        pause()
    else:
        resume()


def sedang_pause() -> bool:
    """Cek apakah game sedang pause."""
    return _state.paused


# --- Game Loop ---

def buat_jendela(lebar: int, tinggi: int, judul: str = "BroLang Game"):
    """Setup jendela game.

    Contoh:
        game.buat_jendela(800, 600, "Gameku")
    """
    _state.lebar = lebar
    _state.tinggi = tinggi
    _state.judul = judul

    if pygame is None:
        raise RuntimeError("Pygame tidak terinstal. Jalankan: pip install pygame")

    pygame.init()
    pygame.display.set_mode((lebar, tinggi))
    pygame.display.set_caption(judul)


_clock = None


def mulai():
    """Memulai game loop. Block sampai game selesai.

    Contoh:
        game.buat_jendela(800, 600, "Gameku")
        game.tambah_scene("main", update_main, gambar_main)
        game.ganti_scene("main")
        game.mulai()
    """
    global _clock
    if pygame is None:
        raise RuntimeError("Pygame tidak terinstal. Jalankan: pip install pygame")

    from brolang.stdlib import input as input_mod
    input_mod.reset()

    clock = pygame.time.Clock()
    _clock = clock
    _state.running = True
    _state.paused = False

    if _state.on_init:
        _state.on_init()

    fps_font = None
    if _state.tampil_fps:
        fps_font = pygame.font.SysFont(None, 24)

    while _state.running:
        # Input adalah pemilik event queue — kuras duluan
        input_mod._update()
        events = input_mod.ambil_events()

        # Proses event quit / escape / custom dari event yang sudah dikuras
        for event in events:
            if event.type == pygame.QUIT:
                _state.running = False
                break
            if (_state.esc_keluar and event.type == pygame.KEYDOWN
                    and event.key == pygame.K_ESCAPE):
                _state.running = False
                break
            if _state.on_event:
                _state.on_event(event)

        if not _state.running:
            break

        # dt dalam detik, di-clamp agar tidak meledak saat tab tidak fokus
        dt = clock.get_time() / 1000.0
        dt = min(dt, 0.05)

        screen = pygame.display.get_surface()

        if not _state.paused:
            # Update current scene
            scene = _state.scenes.get(_state.current_scene)
            if scene and scene["update"]:
                scene["update"](dt)

        # Gambar current scene
        screen.fill(_state.latar_warna)
        scene = _state.scenes.get(_state.current_scene)
        if scene and scene["gambar"]:
            scene["gambar"](screen)

        if _state.tampil_fps and fps_font is not None:
            try:
                fps_surf = fps_font.render(
                    f"FPS: {clock.get_fps():.0f}", True, (255, 255, 0))
                screen.blit(fps_surf, (8, 8))
            except Exception:
                pass

        pygame.display.flip()
        clock.tick(_state.fps)

    if _state.on_exit:
        _state.on_exit()

    input_mod.reset()
    pygame.quit()


def berhenti():
    """Menghentikan game loop."""
    _state.running = False


def sedang_berjalan() -> bool:
    """Cek apakah game sedang berjalan."""
    return _state.running


def reset():
    """Reset seluruh state game (scene, data, pause)."""
    _state.scenes = {}
    _state.current_scene = None
    _state.data = {}
    _state.paused = False
    _state.running = False


# --- Utilitas Game ---

def delta_time() -> float:
    """Waktu frame terakhir dalam detik (ter-clamp 0.05s)."""
    if pygame is None:
        return 0.0
    return min(pygame.time.get_time() / 1000.0, 0.05)


def waktu_sekarang() -> float:
    """Waktu dalam milidetik sejak pygame.init()."""
    if pygame is None:
        return 0.0
    return pygame.time.get_ticks()


def dapatkan_fps() -> float:
    """FPS aktual game loop (0 sebelum mulai)."""
    global _clock
    if _clock is None:
        return 0.0
    return _clock.get_fps()


def atur_data(kunci, nilai):
    """Set satu kunci di data global game."""
    _state.data[kunci] = nilai


def dapatkan_ukuran() -> tuple:
    """Ukuran jendela (lebar, tinggi)."""
    return (_state.lebar, _state.tinggi)


module = SimpleNamespace(
    buat_jendela=buat_jendela,
    mulai=mulai,
    berhenti=berhenti,
    sedang_berjalan=sedang_berjalan,
    reset=reset,
    tambah_scene=tambah_scene,
    ganti_scene=ganti_scene,
    dapatkan_scene_sekarang=dapatkan_scene_sekarang,
    hapus_scene=hapus_scene,
    dapatkan_data=dapatkan_data,
    atur_data=atur_data,
    atur_fps=atur_fps,
    set_latar_warna=set_latar_warna,
    set_tampil_fps=set_tampil_fps,
    set_esc_keluar=set_esc_keluar,
    pause=pause,
    resume=resume,
    set_pause=set_pause,
    sedang_pause=sedang_pause,
    delta_time=delta_time,
    waktu_sekarang=waktu_sekarang,
    dapatkan_fps=dapatkan_fps,
    dapatkan_ukuran=dapatkan_ukuran,
)
