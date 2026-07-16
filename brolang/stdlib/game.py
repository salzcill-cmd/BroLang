"""
Modul Game BroLang
==================

Game loop, scene management, dan utilitas game.

Contoh:
    impor game
    game.buat_jendela(800, 600, "Gameku")
    game.tambah_scehe("utama", update_utama, gambar_utama)
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
        self.scenes = {}
        self.current_scene = None
        self.data = {}
        self.lebar = 800
        self.tinggi = 600
        self.judul = "BroLang Game"
        self.fps = 60
        self.on_init = None
        self.on_event = None
        self.on_exit = None

_state = _GameState()


# --- Jendela ---

def atur_fps(fps: int):
    """Mengatur target FPS.

    Contoh:
        game.atur_fps(60)
    """
    _state.fps = fps


def dapatkan_data() -> dict:
    """Akses data global game (untuk menyimpan skor, status, dll).

    Contoh:
        game.dapatkan_data()["skor"] = 0
    """
    return _state.data


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


def mulai():
    """Memulai game loop. Block sampai game selesai.

    Contoh:
        game.buat_jendela(800, 600, "Gameku")
        game.tambah_scene("main", update_main, gambar_main)
        game.ganti_scene("main")
        game.mulai()
    """
    if pygame is None:
        raise RuntimeError("Pygame tidak terinstal. Jalankan: pip install pygame")

    clock = pygame.time.Clock()
    _state.running = True

    if _state.on_init:
        _state.on_init()

    while _state.running:
        dt = clock.get_time() / 1000.0

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                _state.running = False
                break
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                _state.running = False
                break
            if _state.on_event:
                _state.on_event(event)

        if not _state.running:
            break

        # Update input module
        from brolang.stdlib import input as input_mod
        input_mod._update()

        # Update current scene
        scene = _state.scenes.get(_state.current_scene)
        if scene and scene["update"]:
            scene["update"](dt)

        # Gambar current scene
        screen = pygame.display.get_surface()
        screen.fill((0, 0, 0))
        if scene and scene["gambar"]:
            scene["gambar"](screen)

        pygame.display.flip()
        clock.tick(_state.fps)

    if _state.on_exit:
        _state.on_exit()

    pygame.quit()


def berhenti():
    """Menghentikan game loop."""
    _state.running = False


def sedang_berjalan() -> bool:
    """Cek apakah game sedang berjalan."""
    return _state.running


# --- Utilitas Game ---

def delta_time() -> float:
    """Waktu frame terakhir dalam detik."""
    if pygame is None:
        return 0.0
    return pygame.time.get_time() / 1000.0


def waktu_sekarang() -> float:
    """Waktu dalam milidetik sejak pygame.init()."""
    if pygame is None:
        return 0.0
    return pygame.time.get_ticks()


module = SimpleNamespace(
    buat_jendela=buat_jendela,
    mulai=mulai,
    berhenti=berhenti,
    sedang_berjalan=sedang_berjalan,
    tambah_scene=tambah_scene,
    ganti_scene=ganti_scene,
    dapatkan_scene_sekarang=dapatkan_scene_sekarang,
    hapus_scene=hapus_scene,
    dapatkan_data=dapatkan_data,
    atur_fps=atur_fps,
    delta_time=delta_time,
    waktu_sekarang=waktu_sekarang,
)
