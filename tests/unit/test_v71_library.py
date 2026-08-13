"""
Unit tests untuk BroLang v7.1 — Perluasan Library
==================================================

Perluasan modul stdlib yang sudah ada:
- matematika : statistik (rata_rata, median, modus, varians, standar_deviasi),
               teori bilangan (fpb, kpk, prima, bilangan_prima, fibonacci),
               utilitas (maksimal, minimal, clamp, hipotenusa, sudut, kombinatorik)
- teks       : balik, berulang, hapus_spasi, pad_kiri/kanan, terpusat,
               jumlah, hitung_kata, pecah_baris, regex_*
- tanggal    : nama_hari, nama_bulan, kabisat, akhir_bulan, tambah_bulan/tahun,
               selisih_jam, tanggal_baru
"""

import pytest

from brolang.stdlib import get_stdlib_module
from brolang.lexer import Lexer
from brolang.parser import Parser
from brolang.interpreter import Interpreter


def _mod(nama):
    return get_stdlib_module(nama)


def _jalankan(kode):
    ast = Parser(Lexer(kode).tokenize()).parse()
    interp = Interpreter()
    interp.interpret(ast)
    return interp.output


def _jalankan_vm(kode):
    from brolang.vm.compiler import Compiler
    from brolang.vm.vm import VM

    ast = Parser(Lexer(kode).tokenize()).parse()
    vm = VM()
    vm.run(Compiler().compile(ast))
    return vm.output


# ============================================================
# matematika
# ============================================================


class TestMatematikaStatistik:
    def setup_method(self):
        self.m = _mod("matematika")

    def test_rata_rata(self):
        assert self.m.rata_rata([1, 2, 3, 4, 5]) == 3.0
        assert self.m.rata_rata([10, 20]) == 15.0

    def test_median(self):
        assert self.m.median([1, 3, 3, 6, 7]) == 3
        assert self.m.median([1, 2, 3, 4]) == 2.5

    def test_modus(self):
        assert self.m.modus([1, 2, 2, 3]) == 2

    def test_varians(self):
        assert self.m.varians([1, 2, 3, 4]) == 1.25

    def test_standar_deviasi(self):
        assert self.m.standar_deviasi([1, 2, 3, 4]) == pytest.approx(1.118, abs=0.01)


class TestMatematikaTeoriBilangan:
    def setup_method(self):
        self.m = _mod("matematika")

    def test_fpb(self):
        assert self.m.fpb(12, 18) == 6
        assert self.m.fpb(7, 13) == 1

    def test_kpk(self):
        assert self.m.kpk(4, 6) == 12
        assert self.m.kpk(3, 5) == 15

    def test_prima(self):
        assert self.m.prima(2) is True
        assert self.m.prima(17) is True
        assert self.m.prima(1) is False
        assert self.m.prima(15) is False

    def test_bilangan_prima(self):
        assert self.m.bilangan_prima(10) == [2, 3, 5, 7]
        assert self.m.bilangan_prima(30)[-1] == 29

    def test_fibonacci(self):
        assert self.m.fibonacci(0) == 0
        assert self.m.fibonacci(1) == 1
        assert self.m.fibonacci(10) == 55


class TestMatematikaUtilitas:
    def setup_method(self):
        self.m = _mod("matematika")

    def test_maksimal_minimal(self):
        assert self.m.maksimal(3, 9, 5, 7) == 9
        assert self.m.minimal(3, 9, 5, 7) == 3

    def test_clamp(self):
        assert self.m.clamp(5, 0, 10) == 5
        assert self.m.clamp(-3, 0, 10) == 0
        assert self.m.clamp(99, 0, 10) == 10

    def test_hipotenusa(self):
        assert self.m.hipotenusa(3, 4) == 5.0

    def test_konversi_sudut(self):
        assert self.m.derajat_ke_radian(180) == pytest.approx(3.14159, abs=0.001)
        assert self.m.radian_ke_derajat(3.14159) == pytest.approx(180, abs=0.01)

    def test_kombinasi_permutasi(self):
        assert self.m.kombinasi(5, 2) == 10
        assert self.m.permutasi(5, 2) == 20

    def test_log2_log10(self):
        assert self.m.log2(8) == 3.0
        assert self.m.log10(1000) == 3.0


# ============================================================
# teks
# ============================================================


class TestTeksManipulasi:
    def setup_method(self):
        self.t = _mod("teks")

    def test_balik(self):
        assert self.t.balik("abc") == "cba"

    def test_berulang(self):
        assert self.t.berulang("ab", 3) == "ababab"

    def test_hapus_spasi(self):
        assert self.t.hapus_spasi("a b  c") == "abc"

    def test_pad(self):
        assert self.t.pad_kiri("x", 3, "0") == "x00"
        assert self.t.pad_kanan("x", 3, "0") == "00x"
        assert self.t.terpusat("ab", 4, "-") == "-ab-"

    def test_jumlah(self):
        assert self.t.jumlah("abab", "ab") == 2

    def test_hitung_kata(self):
        assert self.t.hitung_kata("Halo dunia, apa kabar") == 4

    def test_pecah_baris(self):
        assert self.t.pecah_baris("a\nb\nc") == ["a", "b", "c"]


class TestTeksRegex:
    def setup_method(self):
        self.t = _mod("teks")

    def test_regex_cari(self):
        assert self.t.regex_cari("Halo 123", r"\d+") == "123"
        assert self.t.regex_cari("abc", r"\d+") is None

    def test_regex_cari_semua(self):
        assert self.t.regex_cari_semua("a1 b22 c333", r"\d+") == ["1", "22", "333"]

    def test_regex_ganti(self):
        assert self.t.regex_ganti("Halo 123 456", r"\d+", "#") == "Halo # #"

    def test_regex_cocok(self):
        assert self.t.regex_cocok("0812-3456", r"\d{4}-\d{4}") is True
        assert self.t.regex_cocok("telp 123", r"\d{4}-\d{4}") is False


# ============================================================
# tanggal
# ============================================================


class TestTanggalNamaDanKalender:
    def setup_method(self):
        self.d = _mod("tanggal")

    def test_nama_hari(self):
        # 2026-08-07 adalah hari Jumat
        assert self.d.nama_hari("2026-08-07") == "Jumat"

    def test_nama_bulan(self):
        assert self.d.nama_bulan("2026-08-07") == "Agustus"

    def test_kabisat(self):
        assert self.d.kabisat(2024) is True
        assert self.d.kabisat(1900) is False
        assert self.d.kabisat(2000) is True
        assert self.d.kabisat(2025) is False

    def test_akhir_bulan(self):
        assert self.d.akhir_bulan("2026-02-10") == "2026-02-28"
        assert self.d.akhir_bulan("2024-02-10") == "2024-02-29"  # kabisat
        assert self.d.akhir_bulan("2026-08-07") == "2026-08-31"

    def test_tambah_bulan(self):
        assert self.d.tambah_bulan("2026-01-31", 1) == "2026-02-28"
        assert self.d.tambah_bulan("2026-08-07", 3) == "2026-11-07"
        assert self.d.tambah_bulan("2026-03-15", -2) == "2026-01-15"

    def test_tambah_tahun(self):
        assert self.d.tambah_tahun("2024-02-29", 1) == "2025-02-28"
        assert self.d.tambah_tahun("2026-08-07", 2) == "2028-08-07"

    def test_selisih_jam(self):
        assert self.d.selisih_jam("2026-08-07 10:00:00", "2026-08-07 08:00:00") == 2.0
        assert self.d.selisih_jam("2026-08-08", "2026-08-07") == 24.0

    def test_tanggal_baru(self):
        assert self.d.tanggal_baru(2026, 8, 7) == "2026-08-07"


# ============================================================
# acak
# ============================================================


class TestAcak:
    def setup_method(self):
        self.m = _mod("acak")

    def test_boolean(self):
        self.m.seed(42)
        assert self.m.boolean() in (True, False)

    def test_huruf(self):
        self.m.seed(1)
        assert self.m.huruf() in "abcdefghijklmnopqrstuvwxyz"
        assert self.m.huruf_besar() in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    def test_kata(self):
        self.m.seed(2)
        assert len(self.m.kata(6)) == 6

    def test_antara(self):
        self.m.seed(3)
        for _ in range(20):
            v = self.m.antara(1, 10)
            assert 1 <= v <= 10


# ============================================================
# angka
# ============================================================


class TestAngkaPerluasan:
    def setup_method(self):
        self.m = _mod("angka")

    def test_genap_ganjil(self):
        assert self.m.genap(4) is True
        assert self.m.genap(3) is False
        assert self.m.ganjil(3) is True

    def test_fpb_kpk(self):
        assert self.m.fpb(12, 18) == 6
        assert self.m.kpk(4, 6) == 12

    def test_prima_dan_angka_prima(self):
        assert self.m.prima(17) is True
        assert self.m.prima(15) is False
        assert self.m.angka_prima(10) == [2, 3, 5, 7]

    def test_fibonacci(self):
        assert self.m.fibonacci(10) == 55

    def test_digit_dan_jumlah(self):
        assert self.m.digit(1234) == [1, 2, 3, 4]
        assert self.m.jumlah_digit(1234) == 10

    def test_terbalik(self):
        assert self.m.terbalik(1234) == 4321
        assert self.m.terbalik(-123) == -321

    def test_konversi_basis(self):
        assert self.m.ke_biner(10) == "1010"
        assert self.m.dari_biner("1010") == 10
        assert self.m.ke_oktal(8) == "10"
        assert self.m.dari_oktal("10") == 8
        assert self.m.ke_heksa(255) == "ff"
        assert self.m.dari_heksa("ff") == 255


# ============================================================
# dasar
# ============================================================


class TestDasarKonversi:
    def setup_method(self):
        self.m = _mod("dasar")

    def test_ke_angka(self):
        assert self.m.ke_angka("42") == 42
        assert self.m.ke_angka("3.5") == 3.5

    def test_ke_teks(self):
        assert self.m.ke_teks(42) == "42"
        assert self.m.ke_teks(True) == "benar"
        assert self.m.ke_teks(None) == "kosong"

    def test_ke_boolean(self):
        assert self.m.ke_boolean("benar") is True
        assert self.m.ke_boolean("false") is False
        assert self.m.ke_boolean(1) is True
        assert self.m.ke_boolean(0) is False

    def test_jenis(self):
        assert self.m.jenis(42) == "angka"
        assert self.m.jenis(3.5) == "desimal"
        assert self.m.jenis("x") == "teks"
        assert self.m.jenis(True) == "boolean"
        assert self.m.jenis([1]) == "list"
        assert self.m.jenis({"a": 1}) == "objek"
        assert self.m.jenis(None) == "kosong"

    def test_panjang_dan_kosong(self):
        assert self.m.panjang([1, 2, 3]) == 3
        assert self.m.adalah_kosong("") is True
        assert self.m.adalah_kosong([]) is True
        assert self.m.adalah_kosong("x") is False


# ============================================================
# file
# ============================================================


class TestFilePerluasan:
    def setup_method(self):
        self.m = _mod("file")

    def test_salin_dan_pindah(self, tmp_path):
        src = tmp_path / "a.txt"
        dst = tmp_path / "b.txt"
        src.write_text("isi")
        self.m.salin(str(src), str(dst))
        assert dst.read_text() == "isi"
        pindah = tmp_path / "c.txt"
        self.m.pindah(str(dst), str(pindah))
        assert pindah.read_text() == "isi"
        assert not dst.exists()

    def test_jalur(self):
        assert self.m.nama_dasar("/a/b/c.txt") == "c.txt"
        assert self.m.folder("/a/b/c.txt") == "/a/b"
        assert self.m.ekstensi("data.txt") == ".txt"
        assert self.m.ekstensi("tanpa_ext") == ""
        assert self.m.gabung_jalur("a", "b", "c").replace("\\", "/").endswith("a/b/c")

    def test_hapus_folder(self, tmp_path):
        folder = tmp_path / "sub"
        folder.mkdir()
        self.m.hapus_folder(str(folder))
        assert not folder.exists()


# ============================================================
# json, jaringan, sistem, proses, catat
# ============================================================


class TestJsonValid:
    def test_valid(self):
        m = _mod("json")
        assert m.valid('{"a": 1}') is True
        assert m.valid("[1, 2]") is True
        assert m.valid("bukan json") is False


class TestJaringan:
    def test_ip_dan_hostname(self):
        m = _mod("jaringan")
        assert m.ip_local()
        assert m.hostname()


class TestSistemPerluasan:
    def test_cpu_dan_arsitektur(self):
        m = _mod("sistem")
        assert m.jumlah_cpu() >= 1
        assert isinstance(m.memori(), dict)
        assert "total" in m.memori()
        assert m.arsitektur()


class TestProsesPerluasan:
    def test_proses_id(self):
        m = _mod("proses")
        assert m.proses_id() > 0

    def test_jalankan_list(self):
        m = _mod("proses")
        hasil = m.jalankan_list(["echo", "halo"])
        assert hasil.keluaran == "halo"
        assert hasil.kode == 0
        assert hasil.sukses is True


class TestCatatPerluasan:
    def test_level_saat_ini_dan_catat(self, capsys):
        m = _mod("catat")
        m.atur_level("info")
        assert m.level_saat_ini() == "info"
        m.catat("info", "pesan umum")
        captured = capsys.readouterr()
        assert "pesan umum" in captured.out


# ============================================================
# Alias aman-keyword (fungsi bernama keyword tidak bisa dipanggil
# dari BroLang — `tulis`, `hapus`, `buat`, `tunggu`, `harusnya`)
# ============================================================


class TestAliasAmanKeyword:
    def test_file_alias(self, tmp_path):
        m = _mod("file")
        path = str(tmp_path / "a.txt")
        m.tulis_file(path, "isi")
        assert m.baca(path) == "isi"
        m.hapus_file(path)
        assert not m.ada(path)

    def test_json_dan_csv_alias(self, tmp_path):
        j = _mod("json")
        p = str(tmp_path / "d.json")
        j.tulis_file(p, {"a": 1})
        assert j.baca(p)["a"] == 1
        c = _mod("csv")
        pc = str(tmp_path / "d.csv")
        c.tulis_file(pc, [["nama", "nilai"], ["budi", "5"]])
        assert c.baca(pc)[0]["nama"] == "budi"

    def test_sejajar_dan_antrian_dan_tumpukan_alias(self):
        s = _mod("sejajar")
        t = s.jalankan(lambda: 7)
        assert s.tunggu_tugas(t) == 7
        a = _mod("antrian")
        q = a.buat_antrian()
        q.sisipkan(1)
        assert q.ambil() == 1
        st = _mod("tumpukan")
        sk = st.buat_tumpukan()
        sk.tumpuk(2)
        assert sk.ambil() == 2

    def test_lingkungan_alias(self):
        m = _mod("lingkungan")
        m.set("BROLANG_TEST_ALIAS", "x")
        assert m.hapus_var("BROLANG_TEST_ALIAS") is True

    def test_alias_dipakai_dari_bro(self):
        out = _jalankan(
            "impor file\n"
            "tulis file.gabung_jalur(\"a\", \"b\")\n"
        )
        assert out == ["a/b"] or out == ["a\\b"]


class TestTranspilerImportFix:
    def test_impor_json_transpiler(self, tmp_path):
        # Fix v7.1: `impor json`/`impor csv` di transpiler harus memakai
        # modul stdlib BroLang, bukan Python stdlib json/csv (yang tidak
        # punya `tulis_file` dll.).
        import contextlib
        import io
        from brolang.vm.transpiler import Transpiler

        path = str(tmp_path / "data.json")
        code = (
            "impor json\n"
            f'json.tulis_file("{path}", {{"a": 1}})\n'
            "tulis json.valid(\"bukan json\")\n"
        )
        ast = Parser(Lexer(code).tokenize()).parse()
        py_code = Transpiler().transpile(ast)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            exec(compile(py_code, "<t>", "exec"), {"__builtins__": __builtins__})
        assert buf.getvalue().strip() == "False"
        # alias tulis_file benar-benar menulis file
        assert _mod("json").baca(path)["a"] == 1

    def test_impor_csv_transpiler(self, tmp_path):
        from brolang.vm.transpiler import Transpiler
        import contextlib
        import io

        path = str(tmp_path / "d.csv")
        code = (
            "impor csv\n"
            f'csv.tulis_file("{path}", [[\"nama\", \"nilai\"], [\"budi\", \"5\"]])\n'
        )
        ast = Parser(Lexer(code).tokenize()).parse()
        py_code = Transpiler().transpile(ast)
        with contextlib.redirect_stdout(io.StringIO()):
            exec(compile(py_code, "<t>", "exec"), {"__builtins__": __builtins__})
        assert "budi" in open(path, encoding="utf-8").read()


# ============================================================
# Integrasi: dipakai dari kode BroLang
# ============================================================


class TestIntegrasiBro:
    def test_matematika_dari_bro(self):
        out = _jalankan(
            "impor matematika\n"
            "tulis matematika.rata_rata([2, 4, 6])\n"
            "tulis matematika.fpb(12, 18)\n"
            "tulis matematika.clamp(50, 0, 10)\n"
            "tulis matematika.fibonacci(7)\n"
        )
        assert out == ["4", "6", "10", "13"]

    def test_teks_dari_bro(self):
        # BroLang tidak punya raw string — pola regex pakai escape \\d
        out = _jalankan(
            "impor teks\n"
            "tulis teks.balik(\"abc\")\n"
            "tulis teks.hitung_kata(\"Halo dunia\")\n"
            "tulis teks.regex_ganti(\"a1 b2\", \"\\\\d\", \"#\")\n"
        )
        assert out == ["cba", "2", "a# b#"]

    def test_tanggal_dari_bro(self):
        out = _jalankan(
            "impor tanggal\n"
            "tulis tanggal.nama_hari(\"2026-08-07\")\n"
            "tulis tanggal.kabisat(2024)\n"
            "tulis tanggal.tambah_bulan(\"2026-01-31\", 1)\n"
        )
        assert out == ["Jumat", "True", "2026-02-28"]

    def test_angka_dan_dasar_dari_bro(self):
        out = _jalankan(
            "impor angka\n"
            "tulis angka.fpb(12, 18)\n"
            "tulis angka.ke_biner(10)\n"
            "impor dasar\n"
            "tulis dasar.ke_angka(\"42\")\n"
            "tulis dasar.jenis([1, 2])\n"
        )
        assert out == ["6", "1010", "42", "list"]

    def test_acak_dan_sistem_dari_bro(self):
        out = _jalankan(
            "impor acak\n"
            "acak.seed(7)\n"
            "buat k = acak.kata(3)\n"
            "impor teks\n"
            "tulis teks.panjang(k)\n"
            "impor sistem\n"
            "tulis sistem.jumlah_cpu() >= 1\n"
        )
        assert out[0] == "3"
        assert out[1] == "True"

    def test_fisika_dari_bro(self):
        out = _jalankan(
            "impor fisika\n"
            "buat v = fisika.vektor_dari_sudut(0)\n"
            "tulis v.x\n"
            "tulis v.y\n"
            "buat g = fisika.gravitasi_bumi()\n"
            "tulis g.y == 490\n"
            "buat b = fisika.buat_bodi(0, 0, 2, 20)\n"
            "tulis b.massa\n"
        )
        assert out == ["1.0", "0.0", "True", "2"]

    def test_sprite_dari_bro(self):
        out = _jalankan(
            "impor sprite\n"
            "buat s = sprite.Sprite()\n"
            "tulis s.visibel()\n"
            "s.sembunyikan()\n"
            "tulis s.visibel()\n"
            "s.tampilkan()\n"
            "buat g = sprite.GrupSprite()\n"
            "g.tambah(s)\n"
            "tulis g.jumlah()\n"
            "tulis g.apakah_kosong()\n"
        )
        assert out == ["True", "False", "1", "False"]

    def test_ui_helper_dari_bro(self):
        out = _jalankan(
            "impor ui\n"
            "buat w = ui.warna(255, 0, 0)\n"
            "tulis w[0]\n"
            "tulis ui.warna_hex(\"#ff8800\")\n"
            "buat l = ui.Label(\"Halo\", 10, 10)\n"
            "l.set_teks(\"Dunia\")\n"
            "tulis l.teks\n"
        )
        assert out[0] == "255"
        assert out[1] == "(255, 136, 0)"
        assert out[2] == "Dunia"

    def test_visualisasi_tabel_dan_area_dari_bro(self):
        out = _jalankan(
            "impor visualisasi\n"
            "buat data = [{\"nama\": \"Budi\", \"nilai\": 90}]\n"
            "tulis panjang(visualisasi.tabel(data)) > 0\n"
            "buat svg = visualisasi.tabel_svg(data)\n"
            "tulis panjang(svg) > 0\n"
            "buat a = visualisasi.area_svg([1, 3, 2], judul=\"Tren\")\n"
            "tulis panjang(a) > 0\n"
        )
        assert out == ["True", "True", "True"]


class TestVmKwargsDanDefault:
    """v7.1: keyword-argumen & default parameter di VM kini berfungsi
    (sebelumnya: kwargs di-call tanpa nama, default diabaikan — bug lama
    yang membuat contoh game gagal di VM)."""

    def test_kwargs_ke_fungsi_bro(self):
        kode = (
            "fungsi hitung(a, b, c)\n"
            "    kembali a * 100 + b * 10 + c\n"
            "selesai\n"
            "tulis hitung(1, c=3, b=2)\n"
        )
        assert _jalankan(kode) == _jalankan_vm(kode) == ["123"]

    def test_kwargs_ke_method(self):
        kode = (
            "kelas K\n"
            "    fungsi tambah(self, a, b)\n"
            "        kembali a + b\n"
            "    selesai\n"
            "selesai\n"
            "buat k = K()\n"
            "tulis k.tambah(a=5, b=7)\n"
        )
        assert _jalankan(kode) == _jalankan_vm(kode) == ["12"]

    def test_default_parameter(self):
        kode = (
            "fungsi sapa(nama, sapaan=\"Halo\")\n"
            "    kembali sapaan + \" \" + nama\n"
            "selesai\n"
            "tulis sapa(\"Budi\")\n"
            "tulis sapa(\"Budi\", sapaan=\"Hi\")\n"
        )
        assert _jalankan(kode) == _jalankan_vm(kode) == ["Halo Budi", "Hi Budi"]

    def test_kwargs_ke_fungsi_python(self):
        kode = (
            "impor visualisasi\n"
            "buat data = [1, 2, 3]\n"
            "buat svg = visualisasi.batang_svg(data, judul=\"J\")\n"
            "tulis panjang(svg) > 0\n"
        )
        assert _jalankan(kode) == _jalankan_vm(kode) == ["True"]

    def test_kwarg_tidak_dikenal_eror(self):
        from brolang.exceptions import RuntimeError_

        kode = "fungsi f(a)\n    kembali a\nselesai\ntulis f(x=1)\n"
        with pytest.raises(RuntimeError_):
            _jalankan_vm(kode)

    def test_transpiler_grup_sprite_kosongkan(self):
        """GrupSprite.kosongkan (method stdlib asli) tidak boleh di-map ke
        list.clear oleh transpiler."""
        from brolang.vm.transpiler import Transpiler
        import contextlib
        import io

        kode = (
            "impor sprite\n"
            "buat g = sprite.GrupSprite()\n"
            "buat s = sprite.Sprite(kosong, 0, 0, lebar=32, tinggi=32)\n"
            "g.tambah(s)\n"
            "tulis g.jumlah()\n"
            "g.kosongkan()\n"
            "tulis g.apakah_kosong()\n"
        )
        ast = Parser(Lexer(kode).tokenize()).parse()
        py = Transpiler().transpile(ast)
        buf = io.StringIO()
        g = {"__name__": "__main__"}
        with contextlib.redirect_stdout(buf):
            exec(compile(py, "<bro>", "exec"), g)
        out = buf.getvalue().strip().splitlines()
        assert out == ["1", "True"]

    def test_transpiler_list_kosongkan_fallback(self):
        """list.kosongkan di transpiler tetap fallback ke list.clear()."""
        from brolang.vm.transpiler import Transpiler
        import contextlib
        import io

        kode = "buat d = [1, 2, 3]\nd.kosongkan()\ntulis panjang(d)\n"
        ast = Parser(Lexer(kode).tokenize()).parse()
        py = Transpiler().transpile(ast)
        buf = io.StringIO()
        g = {"__name__": "__main__"}
        with contextlib.redirect_stdout(buf):
            exec(compile(py, "<bro>", "exec"), g)
        assert buf.getvalue().strip() == "0"
