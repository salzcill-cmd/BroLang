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
- visualisasi: Chart & grafik data (ASCII, SVG, HTML)

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
    # v4.0 modules
    elif name == "pencocok":
        from brolang.stdlib.pencocok import module as pencocok_module
        register_module("pencocok", pencocok_module)
    elif name == "antrian":
        from brolang.stdlib.antrian import module as antrian_module
        register_module("antrian", antrian_module)
    elif name == "tumpukan":
        from brolang.stdlib.tumpukan import module as tumpukan_module
        register_module("tumpukan", tumpukan_module)
    elif name == "serialisasi":
        from brolang.stdlib.serialisasi import module as serialisasi_module
        register_module("serialisasi", serialisasi_module)
    elif name == "dasar":
        from brolang.stdlib.dasar import module as dasar_module
        register_module("dasar", dasar_module)
    elif name == "sprite":
        from brolang.stdlib.sprite import module as sprite_module
        register_module("sprite", sprite_module)
    elif name == "animasi":
        from brolang.stdlib.animasi import module as animasi_module
        register_module("animasi", animasi_module)
    elif name == "tilemap":
        from brolang.stdlib.tilemap import module as tilemap_module
        register_module("tilemap", tilemap_module)
    elif name == "kamera":
        from brolang.stdlib.kamera import module as kamera_module
        register_module("kamera", kamera_module)
    elif name == "partikel":
        from brolang.stdlib.partikel import module as partikel_module
        register_module("partikel", partikel_module)
    elif name == "ui":
        from brolang.stdlib.ui import module as ui_module
        register_module("ui", ui_module)
    elif name == "fisika":
        from brolang.stdlib.fisika import module as fisika_module
        register_module("fisika", fisika_module)
    elif name == "debugger":
        from brolang.stdlib.debugger import module as debugger_module
        register_module("debugger", debugger_module)
    elif name == "profil":
        from brolang.stdlib.profil import module as profil_module
        register_module("profil", profil_module)
    elif name == "tes":
        from brolang.stdlib.tes import module as tes_module
        register_module("tes", tes_module)
    elif name == "visualisasi":
        from brolang.stdlib.visualisasi import module as vis_module
        register_module("visualisasi", vis_module)
    elif name == "sejajar":
        from brolang.stdlib.sejajar import module as sejajar_module
        register_module("sejajar", sejajar_module)
    # v6.0 modules
    elif name == "tanggal":
        from brolang.stdlib.tanggal import module as tanggal_module
        register_module("tanggal", tanggal_module)
    elif name == "catat":
        from brolang.stdlib.catat import module as catat_module
        register_module("catat", catat_module)
    elif name == "lingkungan":
        from brolang.stdlib.lingkungan import module as lingkungan_module
        register_module("lingkungan", lingkungan_module)
    elif name == "proses":
        from brolang.stdlib.proses import module as proses_module
        register_module("proses", proses_module)
    elif name == "csv":
        from brolang.stdlib.csv import module as csv_module
        register_module("csv", csv_module)
    elif name == "registri":
        from brolang.stdlib.registri import module as registri_module
        register_module("registri", registri_module)
    # v6.2 modules (dijanjikan docs/STDLIB.md)
    elif name == "angka":
        from brolang.stdlib.angka import module as angka_module
        register_module("angka", angka_module)
    elif name == "sistem":
        from brolang.stdlib.sistem import module as sistem_module
        register_module("sistem", sistem_module)
    elif name == "sistem_operasi":
        from brolang.stdlib.sistem_operasi import module as sistem_operasi_module
        register_module("sistem_operasi", sistem_operasi_module)
    elif name == "web":
        from brolang.stdlib.web import module as web_module
        register_module("web", web_module)
    elif name == "database":
        from brolang.stdlib.database import module as database_module
        register_module("database", database_module)
