"""
Test cases untuk BroLang v8.2
==============================

1. properti decorator — clean getter/setter syntax
2. Modul statistik — rerata, median, modus, varians, simpangan baku
3. Modul zaman — stopwatch, timer, waktu berlalu
4. Modul penampilan — tabel, pohon, format angka
5. Modul warna — ANSI, hex, RGB, gradient
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from brolang.lexer.lexer import Lexer
from brolang.parser.parser import Parser
from brolang.interpreter.interpreter import Interpreter


def run_bro(code):
    """Helper: jalankan kode BroLang dan return output."""
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    interp = Interpreter()
    result = interp.interpret(ast)
    return interp.output, result


class TestPropertiDecorator:
    """Test properti decorator (v8.2)."""
    
    def test_basic_property_getter(self):
        """@properti pada fungsi getter."""
        code = """
kelas Suhu
    fungsi __init__(self, derajat)
        self._derajat = derajat
    selesai
    
    @properti
    fungsi derajat(self)
        kembali self._derajat
    selesai
selesai

buat s = Suhu(36)
tulis s.derajat
"""
        output, _ = run_bro(code)
        assert output[0] == "36"
    
    def test_property_setter(self):
        """@properti dengan @nama.setter."""
        code = """
kelas Suhu
    fungsi __init__(self, derajat)
        self._derajat = derajat
    selesai
    
    @properti
    fungsi derajat(self)
        kembali self._derajat
    selesai
    
    @derajat.setter
    fungsi set_derajat(self, v)
        self._derajat = v
    selesai
selesai

buat s = Suhu(36)
s.derajat = 37
tulis s.derajat
"""
        output, _ = run_bro(code)
        assert output[0] == "37"
    
    def test_property_computed(self):
        """@properti dengan computed getter."""
        code = """
kelas Lingkaran
    fungsi __init__(self, jari)
        self._jari = jari
    selesai
    
    @properti
    fungsi luas(self)
        kembali 3.14 * self._jari * self._jari
    selesai
    
    @properti
    fungsi keliling(self)
        kembali 2 * 3.14 * self._jari
    selesai
selesai

buat l = Lingkaran(5)
tulis l.luas
tulis l.keliling
"""
        output, _ = run_bro(code)
        assert output[0] == "78.5"
        assert output[1] == "31.400000000000002"
    
    def test_property_read_only(self):
        """@properti tanpa setter — read-only."""
        code = """
kelas Suhu
    fungsi __init__(self, derajat)
        self._derajat = derajat
    selesai
    
    @properti
    fungsi derajat(self)
        kembali self._derajat
    selesai
selesai

buat s = Suhu(36)
tulis s.derajat
"""
        output, _ = run_bro(code)
        assert output[0] == "36"
    
    def test_property_with_validation(self):
        """@properti dengan validasi di setter."""
        code = """
kelas Akun
    fungsi __init__(self, saldo)
        self._saldo = saldo
    selesai
    
    @properti
    fungsi saldo(self)
        kembali self._saldo
    selesai
    
    @saldo.setter
    fungsi set_saldo(self, v)
        jika v >= 0 maka
            self._saldo = v
        selesai
    selesai
selesai

buat a = Akun(1000)
a.saldo = 500
tulis a.saldo
a.saldo = -100
tulis a.saldo
"""
        output, _ = run_bro(code)
        assert output[0] == "500"
        assert output[1] == "500"  # tidak berubah karena -100


class TestStatistik:
    """Test modul statistik (v8.2)."""
    
    def test_rerata(self):
        from brolang.stdlib import statistik
        assert statistik.rerata([10, 20, 30]) == 20.0
        assert statistik.rerata([1, 2, 3, 4, 5]) == 3.0
    
    def test_rerata_kosong(self):
        from brolang.stdlib import statistik
        assert statistik.rerata([]) == 0
    
    def test_median_ganjil(self):
        from brolang.stdlib import statistik
        assert statistik.median([1, 3, 5, 7, 9]) == 5
    
    def test_median_genap(self):
        from brolang.stdlib import statistik
        assert statistik.median([1, 2, 3, 4]) == 2.5
    
    def test_median_tidak_terurut(self):
        from brolang.stdlib import statistik
        assert statistik.median([9, 1, 5, 3, 7]) == 5
    
    def test_modus(self):
        from brolang.stdlib import statistik
        assert statistik.modus([1, 1, 2, 3]) == [1]
        assert statistik.modus([1, 1, 2, 2, 3]) == [1, 2]
    
    def test_modus_tidak_ada(self):
        from brolang.stdlib import statistik
        assert statistik.modus([1, 2, 3]) == []
    
    def test_varians(self):
        from brolang.stdlib import statistik
        data = [10, 20, 30]
        v = statistik.variance(data)
        assert abs(v - 66.66666666666667) < 0.001
    
    def test_simpangan_baku(self):
        from brolang.stdlib import statistik
        data = [10, 20, 30]
        sd = statistik.simpangan_baku(data)
        assert abs(sd - 8.16496580927726) < 0.001
    
    def test_kuartil(self):
        from brolang.stdlib import statistik
        data = list(range(1, 101))  # 1-100
        assert statistik.kuartil(data, 1) == 25.75
        assert statistik.kuartil(data, 2) == 50.5
        assert statistik.kuartil(data, 3) == 75.25
    
    def test_persentil(self):
        from brolang.stdlib import statistik
        data = list(range(1, 101))
        assert statistik.persentil(data, 50) == 50.5
    
    def test_korelasi(self):
        from brolang.stdlib import statistik
        x = [1, 2, 3, 4, 5]
        y = [2, 4, 6, 8, 10]
        assert abs(statistik.korelasi(x, y) - 1.0) < 0.001
    
    def test_korelasi_negatif(self):
        from brolang.stdlib import statistik
        x = [1, 2, 3, 4, 5]
        y = [10, 8, 6, 4, 2]
        assert abs(statistik.korelasi(x, y) - (-1.0)) < 0.001
    
    def test_ringkasan(self):
        from brolang.stdlib import statistik
        data = [10, 20, 30, 40, 50]
        r = statistik.ringkasan(data)
        assert r["min"] == 10
        assert r["max"] == 50
        assert r["rerata"] == 30.0
        assert r["median"] == 30
        assert r["jumlah"] == 5
    
    def test_rank(self):
        from brolang.stdlib import statistik
        assert statistik.rank([10, 20, 30], 20) == 2
        assert statistik.rank([10, 20, 30], 10) == 1


class TestZaman:
    """Test modul zaman (v8.2)."""
    
    def test_stopwatch_basic(self):
        from brolang.stdlib.zaman import Stopwatch
        import time
        sw = Stopwatch()
        sw.mulai()
        time.sleep(0.01)
        sw.berhenti()
        assert sw.detik > 0
        assert sw.mili_detik > 0
    
    def test_stopwatch_reset(self):
        from brolang.stdlib.zaman import Stopwatch
        sw = Stopwatch()
        sw.mulai()
        sw.berhenti()
        sw.reset()
        assert sw.detik == 0
    
    def test_stopwatch_lap(self):
        from brolang.stdlib.zaman import Stopwatch
        import time
        sw = Stopwatch()
        sw.mulai()
        time.sleep(0.01)
        lap1 = sw.lap()
        time.sleep(0.01)
        lap2 = sw.lap()
        assert lap1 > 0
        assert lap2 > 0
        assert len(sw.lap_times) == 2
    
    def test_stopwatch_context_manager(self):
        from brolang.stdlib.zaman import Stopwatch
        import time
        with Stopwatch() as sw:
            time.sleep(0.01)
        assert sw.detik > 0
    
    def test_timer_basic(self):
        from brolang.stdlib.zaman import Timer
        t = Timer(5.0)
        t.mulai()
        assert t.sisa() <= 5.0
        assert t.sisa() > 0
    
    def test_timer_habis(self):
        from brolang.stdlib.zaman import Timer
        t = Timer(0.001)
        t.mulai()
        import time
        time.sleep(0.01)
        assert t.habis
    
    def test_timer_persentase(self):
        from brolang.stdlib.zaman import Timer
        t = Timer(1.0)
        assert t.persentase == 0
        t.mulai()
        import time
        time.sleep(0.05)
        assert t.persentase > 0
    
    def test_sekarang(self):
        from brolang.stdlib.zaman import sekarang, berlalu
        t0 = sekarang()
        import time
        time.sleep(0.01)
        assert berlalu(t0) > 0
    
    def testUMAN(self):
        from brolang.stdlib.zaman import uman
        assert "1j" in uman(3725)
        assert "5d" in uman(5)
    
    def test_detik_milidetik(self):
        from brolang.stdlib.zaman import detik_milidetik
        result = detik_milidetik(1.234)
        assert "1d" in result
        assert "234md" in result


class TestPenampilan:
    """Test modul penampilan (v8.2)."""
    
    def test_tabel(self):
        from brolang.stdlib import penampilan
        data = [
            {"nama": "Budi", "umur": 25},
            {"nama": "Ani", "umur": 30},
        ]
        result = penampilan.tabel(data)
        assert "Budi" in result
        assert "Ani" in result
        assert "25" in result
    
    def test_tabel_kosong(self):
        from brolang.stdlib import penampilan
        assert penampilan.tabel([]) == "(kosong)"
    
    def test_daftar_bullet(self):
        from brolang.stdlib import penampilan
        result = penampilan.daftar(["apel", "mangga"])
        assert "• apel" in result
        assert "• mangga" in result
    
    def test_daftar_number(self):
        from brolang.stdlib import penampilan
        result = penampilan.daftar(["apel", "mangga"], style="number")
        assert "1. apel" in result
        assert "2. mangga" in result
    
    def test_daftar_letter(self):
        from brolang.stdlib import penampilan
        result = penampilan.daftar(["apel", "mangga"], style="letter")
        assert "a. apel" in result
        assert "b. mangga" in result
    
    def test_angka(self):
        from brolang.stdlib import penampilan
        assert penampilan.angka(1234567) == "1,234,567"
        assert penampilan.angka(1000) == "1,000"
        assert penampilan.angka(999) == "999"
    
    def test_angka_desimal(self):
        from brolang.stdlib import penampilan
        assert penampilan.angka_desimal(3.14) == "3.14"
        assert penampilan.angka_desimal(2.0, 0) == "2"
    
    def test_persen(self):
        from brolang.stdlib import penampilan
        assert penampilan.persen(0.75) == "75.0%"
        assert penampilan.persen(0.756, 1) == "75.6%"
    
    def test_kvp(self):
        from brolang.stdlib import penampilan
        result = penampilan.kvp({"nama": "Budi", "umur": 25})
        assert "Budi" in result
        assert "25" in result
    
    def test_pohon(self):
        from brolang.stdlib import penampilan
        data = {"akar": {"anak1": {}, "anak2": {"cucu": {}}}}
        result = penampilan.pohon(data)
        assert "akar" in result
        assert "anak1" in result
    
    def test_pohon_kosong(self):
        from brolang.stdlib import penampilan
        assert penampilan.pohon({}) == "(kosong)"
    
    def test_horizontal(self):
        from brolang.stdlib import penampilan
        result = penampilan.horizontal(0.7)
        assert "70%" in result
        assert "█" in result
        assert "░" in result
    
    def test_json_indented(self):
        from brolang.stdlib import penampilan
        result = penampilan.json_indented({"nama": "Budi"})
        assert '"nama"' in result
        assert '"Budi"' in result
    
    def test_bernomic(self):
        from brolang.stdlib import penampilan
        result = penampilan.bernomic(["apel", "mangga"])
        assert "1. apel" in result
        assert "2. mangga" in result


class TestWarna:
    """Test modul warna (v8.2)."""
    
    def test_ansi_basic(self):
        from brolang.stdlib import warna
        result = warna.ansi("Halo", huruf="merah")
        assert "\033[31m" in result
        assert "Halo" in result
        assert "\033[0m" in result
    
    def test_ansi_bold(self):
        from brolang.stdlib import warna
        result = warna.ansi("Halo", tebal=True)
        assert "\033[1m" in result
    
    def test_ansi_background(self):
        from brolang.stdlib import warna
        result = warna.ansi("Halo", latar="biru")
        assert "\033[44m" in result
    
    def test_ansi_rgb(self):
        from brolang.stdlib import warna
        result = warna.ansi("Halo", huruf=(255, 128, 0))
        assert "\033[38;2;255;128;0m" in result
    
    def test_merah(self):
        from brolang.stdlib import warna
        result = warna.merah("Error!")
        assert "\033[31m" in result
        assert "Error!" in result
    
    def test_hijau(self):
        from brolang.stdlib import warna
        result = warna.hijau("Sukses!")
        assert "\033[32m" in result
    
    def test_rgb_to_hex(self):
        from brolang.stdlib import warna
        assert warna.rgb_to_hex(255, 128, 0) == "#ff8000"
        assert warna.rgb_to_hex(0, 0, 0) == "#000000"
    
    def test_hex_to_rgb(self):
        from brolang.stdlib import warna
        assert warna.hex_to_rgb("#ff8000") == (255, 128, 0)
        assert warna.hex_to_rgb("#000000") == (0, 0, 0)
    
    def test_gradient(self):
        from brolang.stdlib import warna
        result = warna.gradient("Hi", (255, 0, 0), (0, 0, 255))
        assert "\033[38;2;" in result
        assert "H" in result
        assert "i" in result
    
    def test_rainbow(self):
        from brolang.stdlib import warna
        result = warna.rainbow("Hi")
        assert "\033[38;2;" in result
    
    def test_kotak(self):
        from brolang.stdlib import warna
        result = warna.kotak("Halo")
        assert "┌" in result
        assert "┐" in result
        assert "Halo" in result
    
    def test_kotak_ganda(self):
        from brolang.stdlib import warna
        result = warna.kotak("Halo", style="ganda")
        assert "╔" in result
        assert "╗" in result
    
    def test_garis(self):
        from brolang.stdlib import warna
        result = warna.garis(10)
        assert len(result) == 10
    
    def test_judul(self):
        from brolang.stdlib import warna
        result = warna.judul("Chapter 1")
        assert "Chapter 1" in result
        assert "═" in result
    
    def test_dim(self):
        from brolang.stdlib import warna
        result = warna.dim("redup")
        assert "\033[2m" in result
        assert "redup" in result
