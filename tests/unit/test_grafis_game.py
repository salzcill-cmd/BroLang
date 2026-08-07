"""
Regression tests: integrasi modul `grafis` dengan `game`.

Bug lama: contoh game (game_paddle.bro / game_pong.bro) membuat window lewat
`game.buat_jendela()`, tapi fungsi gambar `grafis.bersihkan(...)` dll. hanya
mengenal window dari `grafis.mulai_jendela()` → error "Jendela belum dibuat".

Fix: `_get_screen()` fallback ke `pygame.display.get_surface()` bila window
dibuat di luar modul grafis.
"""

import os

import pytest

import brolang.stdlib.grafis as g


@pytest.fixture(autouse=True)
def _headless():
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    g._screen = None
    yield
    g.tutup_jendela()
    g._screen = None


class TestScreenFallback:
    """Menggambar lewat window yang dibuat di luar grafis (modul game)."""

    def test_get_screen_fallback(self):
        pg = pytest.importorskip("pygame")
        pg.init()
        pg.display.set_mode((320, 240))  # window dibuat game.buat_jendela()
        screen = g._get_screen()  # tidak boleh raise
        assert screen is not None
        assert (screen.get_width(), screen.get_height()) == (320, 240)

    def test_bersihkan_tanpa_mulai_jendela(self):
        pg = pytest.importorskip("pygame")
        pg.init()
        pg.display.set_mode((320, 240))
        g.bersihkan((10, 20, 30))  # memakai fallback display
        px = pg.display.get_surface().get_at((5, 5))[:3]
        assert px == (10, 20, 30)

    def test_gambar_di_window_game(self):
        """Alur persis game: buat_jendela + mulai() lalu gambar via grafis."""
        pg = pytest.importorskip("pygame")
        from brolang.stdlib import get_stdlib_module
        game = get_stdlib_module("game")
        game.buat_jendela(200, 150, "Test")
        g.bersihkan((0, 0, 0))
        g.segi_panjang(10, 10, 50, 50, "putih")
        g.lingkaran(100, 75, 20, "merah")
        g.tulis_teks("Halo", 5, 5, "hijau", 16)
        surf = pg.display.get_surface()
        # Ada pixel non-hitam (bukan layar polos)
        colors = {surf.get_at((x, y))[:3]
                  for x in range(0, 200, 7) for y in range(0, 150, 7)}
        assert len(colors) >= 2

    def test_error_jika_tanpa_display(self):
        pg = pytest.importorskip("pygame")
        if pg.display.get_init():
            pg.display.quit()
        with pytest.raises(RuntimeError, match="Jendela belum dibuat"):
            g._get_screen()

    def test_berhenti_lalu_pakai_lagi_error(self):
        """Setelah pygame.quit() (akhir game), _get_screen harus error lagi
        — fallback TIDAK boleh di-cache jadi surface mati."""
        pg = pytest.importorskip("pygame")
        pg.init()
        pg.display.set_mode((100, 100))
        assert g._get_screen() is not None  # fallback aktif
        pg.quit()  # game.mulai() selesai
        with pytest.raises(RuntimeError, match="Jendela belum dibuat"):
            g._get_screen()
