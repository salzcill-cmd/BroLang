"""
Unit tests untuk GUI (Pygame) modul visualisasi.

Test geometry & logika murni berjalan tanpa pygame.
Test rendering PNG memakai pygame (di-skip jika belum terinstall).
"""

import os

import pytest

from brolang.stdlib import get_stdlib_module
from brolang.stdlib.visualisasi import (
    _batang_geom,
    _bin_data,
    _colors_for,
    _garis_geom,
    _hex_color,
    _hist_geom,
    _kue_geom,
    _norm_spec,
    _pygame_safe,
    _sebar_geom,
)


@pytest.fixture(scope="module")
def vis():
    return get_stdlib_module("visualisasi")


class TestPygameSafe:
    """Sanitasi teks untuk font pygame."""

    def test_ascii_unchanged(self):
        assert _pygame_safe("Hello 123") == "Hello 123"

    def test_unicode_replaced(self):
        assert "?" not in _pygame_safe("Halo Dunia")
        assert _pygame_safe("Senin — Rabu ✓ 100%") == "Senin - Rabu OK 100%"

    def test_non_string(self):
        assert _pygame_safe(42) == "42"


class TestWarna:
    """Konversi warna."""

    def test_hex(self):
        assert _hex_color("#6366f1") == (99, 102, 241)

    def test_rgb_tuple(self):
        assert _hex_color((10, 20, 30)) == (10, 20, 30)

    def test_invalid_falls_back(self):
        c = _hex_color("bukan warna")
        assert len(c) == 3

    def test_colors_for_single(self):
        colors = _colors_for(4, "#ff0000")
        assert colors == [(255, 0, 0)] * 4

    def test_colors_for_list(self):
        colors = _colors_for(3, ["#ff0000", "#00ff00"])
        assert colors == [(255, 0, 0), (0, 255, 0), (255, 0, 0)]

    def test_colors_for_palette(self):
        assert len(_colors_for(5, None)) == 5

    def test_colors_for_rgb_triple(self):
        # tuple RGB tunggal harus dianggap SATU warna, bukan list 3 warna
        colors = _colors_for(3, (255, 0, 0))
        assert colors == [(255, 0, 0)] * 3


class TestNormSpec:
    """Validasi spec chart."""

    def test_valid(self):
        assert _norm_spec({"jenis": "batang", "data": [1]}) == (
            "batang", {"jenis": "batang", "data": [1]}
        )

    def test_jenis_unknown(self):
        with pytest.raises(ValueError):
            _norm_spec({"jenis": "pizza", "data": [1]})

    def test_missing_data(self):
        with pytest.raises(ValueError):
            _norm_spec({"jenis": "batang"})

    def test_not_dict(self):
        with pytest.raises(ValueError):
            _norm_spec([1, 2, 3])

    def test_sebar_tanpa_data_ok(self):
        _norm_spec({"jenis": "sebar", "x": [1], "y": [2]})


class TestGeometry:
    """Geometry murni (tanpa pygame)."""

    def test_batang_geom(self):
        geom = _batang_geom([1, 2, 3], ["a", "b", "c"], (0, 0, 300, 200), None)
        assert len(geom["bars"]) == 3
        assert len(geom["ticks"]) >= 2
        assert geom["baseline"] == 200

    def test_batang_geom_all_zero(self):
        geom = _batang_geom([0, 0], ["a", "b"], (0, 0, 100, 100), None)
        assert len(geom["bars"]) == 2  # tidak crash

    def test_garis_geom(self):
        geom = _garis_geom([[1, 2, 3], [4, 5, 6]], [1, 2, 3], ["A", "B"], (0, 0, 300, 200), None)
        assert len(geom["series"]) == 2
        assert len(geom["series"][0]["points"]) == 3

    def test_garis_geom_flat(self):
        geom = _garis_geom([[5, 5, 5]], [1, 2, 3], None, (0, 0, 300, 200), None)
        assert len(geom["series"][0]["points"]) == 3  # tidak crash

    def test_garis_geom_panjang_beda(self):
        with pytest.raises(ValueError):
            _garis_geom([[1, 2], [3, 4, 5]], [1, 2], None, (0, 0, 300, 200), None)

    def test_kue_geom(self):
        geom = _kue_geom([30, 40, 30], ["a", "b", "c"], (0, 0, 300, 200), None)
        assert len(geom["slices"]) == 3
        assert abs(sum(s["frac"] for s in geom["slices"]) - 1.0) < 1e-9
        assert geom["total"] == 100

    def test_kue_geom_zero_total_raises(self):
        with pytest.raises(ValueError):
            _kue_geom([0, 0, 0], ["a", "b", "c"], (0, 0, 300, 200), None)

    def test_kue_geom_negative_raises(self):
        with pytest.raises(ValueError):
            _kue_geom([30, -5, 25], ["a", "b", "c"], (0, 0, 300, 200), None)

    def test_sebar_geom(self):
        geom = _sebar_geom([1, 2, 3], [3, 1, 2], (0, 0, 300, 200), "#ff0000")
        assert len(geom["points"]) == 3
        assert geom["color"] == (255, 0, 0)

    def test_sebar_geom_flat(self):
        geom = _sebar_geom([1, 1, 1], [2, 2, 2], (0, 0, 300, 200), None)
        assert len(geom["points"]) == 3

    def test_hist_geom(self):
        geom = _hist_geom([3, 5, 2], ["0-1", "1-2", "2-3"], (0, 0, 300, 200), None)
        assert len(geom["bars"]) == 3

    def test_bin_data(self):
        counts, labels = _bin_data([1, 1, 2, 2, 2, 3, 3, 4], 4)
        assert sum(counts) == 8
        assert len(labels) == 4


class TestExports:
    """Fungsi GUI terdaftar di modul."""

    def test_gui_exports(self, vis):
        for name in ("tampilkan_jendela", "tampilkan_batang", "tampilkan_garis",
                     "tampilkan_kue", "tampilkan_sebar", "tampilkan_histogram",
                     "simpan_png"):
            assert hasattr(vis, name)


class TestGracefulError:
    """Perilaku saat pygame tidak terinstall."""

    def test_tampilkan_raise_tanpa_pygame(self, vis, monkeypatch):
        import brolang.stdlib.visualisasi as v
        monkeypatch.setattr(v, "_pygame", None)
        with pytest.raises(RuntimeError, match="pygame"):
            vis.tampilkan_jendela([{"jenis": "batang", "data": [1]}], judul="X")

    def test_simpan_png_raise_tanpa_pygame(self, vis, monkeypatch, tmp_path):
        import brolang.stdlib.visualisasi as v
        monkeypatch.setattr(v, "_pygame", None)
        with pytest.raises(RuntimeError, match="pygame"):
            vis.simpan_png(str(tmp_path / "x.png"), {"jenis": "batang", "data": [1]})


class TestDrawFrame:
    """Render satu frame penuh GUI tanpa crash (headless)."""

    @pytest.fixture(autouse=True)
    def _headless(self):
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        yield

    def test_semua_jenis_dan_help(self):
        pg = pytest.importorskip("pygame")
        import brolang.stdlib.visualisasi as v
        pg.init()
        screen = pg.Surface((900, 600))
        fonts = v._make_fonts(pg)
        specs = [
            v._norm_spec({"jenis": "batang", "data": [1, 2, 3], "judul": "B"}),
            v._norm_spec({"jenis": "garis", "data": [1, 3, 2], "judul": "G"}),
            v._norm_spec({"jenis": "kue", "data": {"a": 30, "b": 70}, "judul": "K"}),
            v._norm_spec({"jenis": "sebar", "x": [1, 2, 3], "y": [3, 1, 2], "judul": "S"}),
            v._norm_spec({"jenis": "histogram", "data": [1, 1, 2, 2, 3], "judul": "H"}),
        ]
        # Frame normal + frame dengan help overlay, untuk tiap chart
        for i in range(len(specs)):
            v._draw_frame(pg, screen, fonts, specs, "Dashboard", 900, 600, i, 0, 0, (100, 100), False)
            v._draw_frame(pg, screen, fonts, specs, "Dashboard", 900, 600, i, 0, 0, (100, 100), True)


class TestRenderPng:
    """Render chart ke PNG (headless, butuh pygame)."""

    @pytest.fixture(autouse=True)
    def _headless(self):
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        yield

    def test_render_semua_jenis(self, vis, tmp_path):
        pg = pytest.importorskip("pygame")
        specs = [
            {"jenis": "batang", "data": [12, 45, 23], "judul": "Batang"},
            {"jenis": "garis", "data": [[1, 3, 2], [4, 2, 6]], "judul": "Garis"},
            {"jenis": "kue", "data": {"A": 30, "B": 40}, "judul": "Kue"},
            {"jenis": "sebar", "x": [1, 2, 3], "y": [3, 1, 2], "judul": "Sebar"},
            {"jenis": "histogram", "data": [1, 1, 2, 2, 3, 3, 4], "jumlah_bin": 3,
             "judul": "Histo"},
        ]
        for i, spec in enumerate(specs):
            fn = str(tmp_path / f"chart_{i}.png")
            vis.simpan_png(fn, spec)
            assert os.path.exists(fn)
            assert os.path.getsize(fn) > 1000
            surf = pg.image.load(fn)
            # Harus ada konten (bukan gambar polos)
            px = {surf.get_at((x, y))[:3]
                  for x in range(0, surf.get_width(), 19)
                  for y in range(0, surf.get_height(), 19)}
            assert len(px) >= 3, f"chart {i} terlihat polos"

    def test_render_warna_dan_judul(self, vis, tmp_path):
        pg = pytest.importorskip("pygame")
        fn = str(tmp_path / "warna.png")
        vis.simpan_png(fn, {"jenis": "batang", "data": [1, 2], "warna": "#ff0000",
                            "judul": "Judul Spesial"})
        surf = pg.image.load(fn)
        # Cari pixel merah (warna bar)
        found_red = False
        for x in range(0, surf.get_width(), 3):
            for y in range(0, surf.get_height(), 3):
                r, g, b, _ = surf.get_at((x, y))
                if r > 200 and g < 100 and b < 100:
                    found_red = True
                    break
            if found_red:
                break
        assert found_red

    def test_spec_tidak_valid_raise(self, vis, tmp_path):
        pytest.importorskip("pygame")
        with pytest.raises(ValueError):
            vis.simpan_png(str(tmp_path / "x.png"), {"jenis": "bogus"})

    def test_sebar_kosong_tetap_render(self, vis, tmp_path):
        """Scatter dengan data kosong tidak boleh crash (sama seperti chart lain)."""
        pytest.importorskip("pygame")
        fn = str(tmp_path / "sebar_kosong.png")
        vis.simpan_png(fn, {"jenis": "sebar", "x": [], "y": []})
        assert os.path.exists(fn)

    def test_garis_kosong_tetap_render(self, vis, tmp_path):
        pytest.importorskip("pygame")
        fn = str(tmp_path / "garis_kosong.png")
        vis.simpan_png(fn, {"jenis": "garis", "data": []})
        assert os.path.exists(fn)


class TestE2EGui:
    """End-to-end: pakai fungsi GUI dari kode BroLang asli."""

    def test_simpan_png_dari_brolang(self, tmp_path):
        pytest.importorskip("pygame")
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        from brolang.lexer import Lexer
        from brolang.parser import Parser
        from brolang.interpreter import Interpreter

        target = str(tmp_path / "dari_bro.png")
        code = (
            "impor visualisasi\n"
            f'visualisasi.simpan_png("{target}", '
            '{"jenis": "batang", "data": [5, 10, 15], "judul": "Dari BroLang"})\n'
            'tulis "OK"\n'
        )
        interp = Interpreter()
        interp.interpret(Parser(Lexer(code).tokenize()).parse())
        assert interp.output == ["OK"]
        assert os.path.exists(target)
        assert os.path.getsize(target) > 1000
