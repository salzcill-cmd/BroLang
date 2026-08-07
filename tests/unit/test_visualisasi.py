"""
Unit tests untuk modul standard library visualisasi (data visualization).
"""

import pytest

from brolang.stdlib import get_stdlib_module
from brolang.lexer import Lexer
from brolang.parser import Parser
from brolang.interpreter import Interpreter


def _run(code):
    interp = Interpreter()
    interp.interpret(Parser(Lexer(code).tokenize()).parse())
    return interp.output


@pytest.fixture(scope="module")
def vis():
    return get_stdlib_module("visualisasi")


class TestBatang:
    """Chart batang ASCII."""

    def test_list_input(self, vis):
        out = vis.batang([10, 20, 30])
        assert "█" in out
        assert "1" in out and "3" in out

    def test_dict_input(self, vis):
        out = vis.batang({"A": 5, "B": 15})
        assert "A" in out and "B" in out
        assert "█" in out

    def test_pairs_input(self, vis):
        out = vis.batang([["Senin", 12], ["Selasa", 45]])
        assert "Senin" in out and "Selasa" in out

    def test_label_param(self, vis):
        out = vis.batang([3, 7], label=["x", "y"])
        assert out.startswith("x") or "x " in out
        assert "y" in out

    def test_judul(self, vis):
        out = vis.batang([1, 2], judul="Judul Test")
        assert out.splitlines()[0] == "Judul Test"

    def test_satuan(self, vis):
        out = vis.batang([10], satuan="kg")
        assert "kg" in out

    def test_empty_data(self, vis):
        assert vis.batang([]) == "(data kosong)"

    def test_zero_values(self, vis):
        out = vis.batang([0, 0, 0])
        assert "█" in out  # tidak crash dengan semua nol


class TestGaris:
    """Chart garis ASCII."""

    def test_output(self, vis):
        out = vis.garis([3, 7, 2, 9, 5])
        assert isinstance(out, str)
        assert len(out.splitlines()) > 8

    def test_judul(self, vis):
        out = vis.garis([1, 2, 3], judul="Tren")
        assert out.splitlines()[0] == "Tren"

    def test_single_point(self, vis):
        out = vis.garis([42])
        assert "42" in out or "maks" in out

    def test_empty(self, vis):
        assert vis.garis([]) == "(data kosong)"


class TestKue:
    """Chart pie/donat ASCII."""

    def test_output(self, vis):
        out = vis.kue([30, 40, 25, 5])
        assert isinstance(out, str)
        assert "30.0%" in out or "30.0" in out

    def test_label(self, vis):
        out = vis.kue([10, 20], label=["A", "B"])
        assert "A" in out and "B" in out

    def test_empty(self, vis):
        assert vis.kue([]) == "(data kosong)"

    def test_negative_returns_message(self, vis):
        out = vis.kue([30, -5, 25])
        assert "negatif" in out


class TestSebar:
    """Scatter plot ASCII."""

    def test_output(self, vis):
        out = vis.sebar([1, 2, 3, 4], [2, 4, 1, 5])
        assert isinstance(out, str)
        assert "X:" in out

    def test_empty(self, vis):
        assert vis.sebar([], []) == "(data kosong)"


class TestHistogram:
    """Histogram ASCII."""

    def test_output(self, vis):
        out = vis.histogram([1, 1, 2, 2, 2, 3, 3, 3, 3, 4])
        assert "█" in out
        assert "n = 10" in out

    def test_bin_count(self, vis):
        out = vis.histogram([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], jumlah_bin=5)
        assert isinstance(out, str)

    def test_empty(self, vis):
        assert vis.histogram([]) == "(data kosong)"


class TestSvg:
    """Chart SVG."""

    def _check_svg(self, svg):
        assert svg.startswith("<svg")
        assert svg.endswith("</svg>")
        assert len(svg) > 300

    def test_batang_svg(self, vis):
        self._check_svg(vis.batang_svg([12, 45, 23, 67], judul="Penjualan"))

    def test_batang_svg_judul(self, vis):
        svg = vis.batang_svg([1, 2], judul="Chart Saya")
        assert "Chart Saya" in svg

    def test_garis_svg(self, vis):
        self._check_svg(vis.garis_svg([1, 3, 2, 5, 4], judul="Tren"))

    def test_garis_svg_multi_series(self, vis):
        svg = vis.garis_svg([[1, 3, 2], [4, 2, 6]], label=["Seri A", "Seri B"])
        self._check_svg(svg)
        assert "Seri A" in svg and "Seri B" in svg

    def test_garis_svg_with_x(self, vis):
        svg = vis.garis_svg([10, 20, 30], x=[2020, 2021, 2022])
        self._check_svg(svg)
        assert "2020" in svg

    def test_kue_svg(self, vis):
        svg = vis.kue_svg([30, 40, 25, 5], label=["A", "B", "C", "D"], judul="Pasar")
        self._check_svg(svg)
        assert "Pasar" in svg

    def test_sebar_svg(self, vis):
        svg = vis.sebar_svg([1, 2, 3, 4, 5], [2, 5, 3, 8, 6], judul="Sebaran")
        self._check_svg(svg)
        assert "Sebaran" in svg

    def test_histogram_svg(self, vis):
        svg = vis.histogram_svg([1, 1, 2, 2, 2, 3, 3, 4, 5], jumlah_bin=4, judul="Histo")
        self._check_svg(svg)
        assert "Histo" in svg

    def test_empty_data_svg(self, vis):
        svg = vis.batang_svg([], judul="Kosong")
        assert "tidak ada data" in svg

    def test_warna_param(self, vis):
        svg = vis.batang_svg([1, 2, 3], warna="#ff0000")
        assert "#ff0000" in svg

    def test_garis_svg_x_mismatch_raises(self, vis):
        with pytest.raises(ValueError):
            vis.garis_svg([1, 2, 3], x=[1, 2])

    def test_kue_svg_negative_raises(self, vis):
        with pytest.raises(ValueError):
            vis.kue_svg([30, -5, 25])

    def test_garis_svg_series_length_mismatch_raises(self, vis):
        with pytest.raises(ValueError):
            vis.garis_svg([[1, 2], [4, 5, 6]])

    def test_svg_id_unik_per_chart(self, vis):
        # Gradient id tidak boleh bentrok antar chart (untuk laporan HTML)
        svg1 = vis.batang_svg([1, 2], warna="#ff0000")
        svg2 = vis.batang_svg([1, 2], warna="#00ff00")
        ids1 = set()
        for part in svg1.split('id="')[1:]:
            ids1.add(part.split('"')[0])
        ids2 = set()
        for part in svg2.split('id="')[1:]:
            ids2.add(part.split('"')[0])
        assert ids1 & ids2 == set()


class TestExport:
    """Fungsi export ke file."""

    def test_simpan_svg(self, vis, tmp_path):
        path = str(tmp_path / "chart.svg")
        vis.simpan_svg(path, vis.batang_svg([1, 2]))
        content = path and open(path).read()
        assert content.startswith("<svg")

    def test_simpan_txt(self, vis, tmp_path):
        path = str(tmp_path / "chart.txt")
        vis.simpan_txt(path, vis.batang([1, 2]))
        assert "█" in open(path).read()

    def test_simpan_html(self, vis, tmp_path):
        path = str(tmp_path / "laporan.html")
        svgs = [vis.batang_svg([1, 2]), vis.kue_svg([30, 70], label=["a", "b"])]
        vis.simpan_html(path, svgs, judul="Laporan Bulanan")
        content = open(path).read()
        assert "<html" in content
        assert "Laporan Bulanan" in content
        assert content.count("<svg") == 2
        assert "BroLang" in content

    def test_simpan_html_single_string(self, vis, tmp_path):
        path = str(tmp_path / "satu.html")
        vis.simpan_html(path, vis.batang_svg([1, 2]))
        assert open(path).read().count("<svg") == 1


class TestModuleRegistry:
    """Modul terdaftar dengan benar."""

    def test_module_registered(self):
        module = get_stdlib_module("visualisasi")
        assert hasattr(module, "batang")
        assert hasattr(module, "garis")
        assert hasattr(module, "kue")
        assert hasattr(module, "sebar")
        assert hasattr(module, "histogram")
        assert hasattr(module, "batang_svg")
        assert hasattr(module, "garis_svg")
        assert hasattr(module, "kue_svg")
        assert hasattr(module, "sebar_svg")
        assert hasattr(module, "histogram_svg")
        assert hasattr(module, "simpan_svg")
        assert hasattr(module, "simpan_html")
        assert hasattr(module, "simpan_txt")


class TestE2EBroLang:
    """End-to-end: pakai modul dari kode BroLang asli."""

    def test_impor_dan_batang(self):
        out = _run(
            """
impor visualisasi
tulis visualisasi.batang([10, 25, 5], label=["A", "B", "C"], judul="Tes")
"""
        )
        assert len(out) == 1
        assert "█" in out[0]
        assert "Tes" in out[0]

    def test_impor_dan_svg(self):
        out = _run(
            """
impor visualisasi
buat svg = visualisasi.batang_svg([1, 2, 3], judul="Chart")
tulis teks(panjang(svg)) + " karakter"
"""
        )
        # SVG dihasilkan dari dalam BroLang (bukan error)
        assert out and "karakter" in out[0]

    def test_dict_dari_brolang(self):
        out = _run(
            """
impor visualisasi
buat data = {"Senin": 12, "Selasa": 45}
tulis visualisasi.batang(data)
"""
        )
        assert "Senin" in out[0]
        assert "Selasa" in out[0]
