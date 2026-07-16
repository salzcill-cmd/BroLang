"""
Standard Library BroLang
========================

Standard library menyediakan modul-modul bawaan yang dapat
digunakan dalam program BroLang.

Modul yang tersedia:
- matematika  : Fungsi matematika (akar, sin, cos, dll)
- teks       : Manipulasi teks (upper, lower, split, dll)
- waktu      : Fungsi waktu (now, sleep, dll)
- file       : Operasi file (baca, tulis, dll)
- json       : JSON parsing
- jaringan   : HTTP client
- acak       : Random number generation

Modul Game:
- vektor     : Vektor 2D/3D (Vec2, Vec3) untuk game
- grafis     : Rendering 2D (Pygame wrapper)
- audio      : Sound effects & musik
- input      : Keyboard & mouse input
- game       : Game loop & scene management

Contoh:
    impor matematika
    matematika.akar(25)

    impor game
    game.buat_jendela(800, 600, "Gameku")
    game.mulai()
"""

from typing import Any, Dict, Optional
from types import SimpleNamespace


# Module registry
_STDLIB_MODULES: Dict[str, Any] = {}


def register_module(name: str, module: Any) -> None:
    """Mendaftarkan modul standard library."""
    _STDLIB_MODULES[name] = module


def get_stdlib_module(name: str) -> Any:
    """Mendapatkan modul standard library.

    Args:
        name: Nama modul

    Returns:
        Module object

    Raises:
        ImportError: Jika modul tidak ditemukan
    """
    # Lazy loading
    if name not in _STDLIB_MODULES:
        _load_module(name)

    if name in _STDLIB_MODULES:
        return _STDLIB_MODULES[name]

    raise ImportError(f"Modul standard library '{name}' tidak ditemukan.")


def _load_module(name: str) -> None:
    """Load modul standard library secara lazy."""
    if name == "matematika":
        from brolang.stdlib.matematika import module as mat_module
        register_module("matematika", mat_module)
    elif name == "teks":
        from brolang.stdlib.teks import module as teks_module
        register_module("teks", teks_module)
    elif name == "waktu":
        from brolang.stdlib.waktu import module as waktu_module
        register_module("waktu", waktu_module)
    elif name == "file":
        from brolang.stdlib.file import module as file_module
        register_module("file", file_module)
    elif name == "json":
        from brolang.stdlib.json import module as json_module
        register_module("json", json_module)
    elif name == "jaringan":
        from brolang.stdlib.jaringan import module as jaringan_module
        register_module("jaringan", jaringan_module)
    elif name == "acak":
        from brolang.stdlib.acak import module as acak_module
        register_module("acak", acak_module)
    elif name == "vektor":
        from brolang.stdlib.vektor import module as vektor_module
        register_module("vektor", vektor_module)
    elif name == "grafis":
        from brolang.stdlib.grafis import module as grafis_module
        register_module("grafis", grafis_module)
    elif name == "audio":
        from brolang.stdlib.audio import module as audio_module
        register_module("audio", audio_module)
    elif name == "input":
        from brolang.stdlib import input as input_module
        register_module("input", input_module.module)
    elif name == "game":
        from brolang.stdlib.game import module as game_module
        register_module("game", game_module)
