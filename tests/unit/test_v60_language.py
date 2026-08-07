"""
Unit tests: BroLang v6.0 — Type System, Pattern Matching Modern,
Error Handling Profesional, Ekosistem Stdlib, Package Registry Online.
"""

import io
import contextlib
import os
import shutil
import tempfile

import pytest

from brolang.lexer import Lexer
from brolang.parser import Parser
from brolang.interpreter import Interpreter
from brolang.vm.transpiler import Transpiler


def _jalankan(kode):
    """Jalankan kode BroLang lewat interpreter dan kembalikan output."""
    ast = Parser(Lexer(kode).tokenize()).parse()
    interp = Interpreter()
    interp.interpret(ast)
    return interp.output


def _transpile(kode):
    """Transpile kode BroLang → Python source."""
    ast = Parser(Lexer(kode).tokenize()).parse()
    return Transpiler().transpile(ast)


def _jalankan_transpiler(kode):
    """Jalankan kode via transpiler dan kembalikan output."""
    py = _transpile(kode)
    exec_globals = {"__builtins__": __builtins__}
    stdout_capture = io.StringIO()
    with contextlib.redirect_stdout(stdout_capture):
        exec(py, exec_globals)
    output = stdout_capture.getvalue().strip().split("\n")
    return [line for line in output if line]


def _jalankan_pipeline(kode):
    """Jalankan kode lewat pipeline lengkap CLI (mirip `bro run`):
    lexer → parser → analyzer → optimizer → transpiler → exec.
    """
    from brolang.semantic import SemanticAnalyzer
    from brolang.optimizer import Optimizer
    ast = Parser(Lexer(kode).tokenize()).parse()
    analyzer = SemanticAnalyzer()
    assert analyzer.analyze(ast), [str(e) for e in analyzer.errors]
    optimized = Optimizer().optimize(ast)
    py = Transpiler().transpile(optimized)
    exec_globals = {"__builtins__": __builtins__}
    stdout_capture = io.StringIO()
    with contextlib.redirect_stdout(stdout_capture):
        exec(py, exec_globals)
    output = stdout_capture.getvalue().strip().split("\n")
    return [line for line in output if line]


def _analisa(kode):
    """Analisis semantik AST — kembalikan (ok, errors)."""
    from brolang.semantic import SemanticAnalyzer
    ast = Parser(Lexer(kode).tokenize()).parse()
    analyzer = SemanticAnalyzer()
    ok = analyzer.analyze(ast)
    return ok, analyzer.errors


# ============= V6.0: Type System =============

class TestTypeSystem:
    def test_anotasi_variabel(self):
        out = _jalankan("""
buat umur: Angka = 25
buat nama: Teks = "Budi"
buat aktif: Boolean = benar
tulis umur
tulis nama
tulis aktif
""")
        assert out == ["25", "Budi", "True"]

    def test_anotasi_salah_menolak(self):
        from brolang.exceptions import BroLangError
        with pytest.raises(BroLangError):
            _jalankan('buat umur: Angka = "salah"')

    def test_param_dan_return_type(self):
        out = _jalankan("""
fungsi kali2(a: Angka) -> Angka
    kembali a * 2
selesai
tulis kali2(21)
""")
        assert out == ["42"]

    def test_param_type_salah_menolak(self):
        from brolang.exceptions import BroLangError
        with pytest.raises(BroLangError):
            _jalankan('''
fungsi sapa(nama: Teks) -> Teks
    kembali nama
selesai
tulis sapa(42)
''')

    def test_union_type(self):
        out = _jalankan('''
fungsi cetak(nilai: Angka | Teks)
    tulis nilai
selesai
cetak(5)
cetak("lima")
''')
        assert out == ["5", "lima"]

    def test_generik_daftar(self):
        out = _jalankan('''
buat angka2: Daftar<Angka> = [1, 2, 3]
tulis angka2[0] + angka2[2]
''')
        assert out == ["4"]

    def test_type_alias(self):
        out = _jalankan('''
tipe ID = Angka
buat kode: ID = 12345
tulis kode + 1
''')
        assert out == ["12346"]

    def test_kelas_sebagai_tipe(self):
        out = _jalankan('''
kelas Mobil
    fungsi __init__(merk)
        self.merk = merk
    selesai
selesai
fungsi info(m: Mobil) -> Teks
    kembali m.merk
selesai
buat mobil = Mobil("Toyota")
tulis info(mobil)
''')
        assert out == ["Toyota"]

    def test_konsisten_transpiler(self):
        kode = '''
fungsi kali2(a: Angka) -> Angka
    kembali a * 2
selesai
tulis kali2(21)
'''
        assert _jalankan_transpiler(kode) == ["42"]


# ============= V6.0: Pattern Matching Modern =============

class TestPatternMatchingModern:
    def test_pola_list(self):
        out = _jalankan('''
buat data = [1, 2]
cocokkan data {
    [a, b]: tulis a + b
    _: tulis "lain"
}
''')
        assert out == ["3"]

    def test_pola_objek_literal(self):
        out = _jalankan('''
buat orang = {"nama": "Ani", "umur": 20}
cocokkan orang {
    {"nama": "Ani"}: tulis "hai Ani"
    {"nama": "Budi"}: tulis "hai Budi"
    _: tulis "siapa?"
}
''')
        assert out == ["hai Ani"]

    def test_pola_objek_binding(self):
        out = _jalankan('''
buat orang = {"nama": "Ani", "umur": 20}
cocokkan orang {
    {"nama": n, "umur": u}: tulis "Nama: " + n + ", Umur: " + teks(u)
}
''')
        assert out == ["Nama: Ani, Umur: 20"]

    def test_guard(self):
        out = _jalankan('''
buat skor = 15
cocokkan skor {
    x jika x > 10: tulis "tinggi"
    _: tulis "rendah"
}
''')
        assert out == ["tinggi"]

    def test_guard_tidak_lolos(self):
        out = _jalankan('''
buat skor = 5
cocokkan skor {
    x jika x > 10: tulis "tinggi"
    _: tulis "rendah"
}
''')
        assert out == ["rendah"]

    def test_binding(self):
        out = _jalankan('''
buat angka = 42
cocokkan angka {
    n: tulis "nilai: " + teks(n)
}
''')
        assert out == ["nilai: 42"]

    def test_perilaku_lama_masih_jalan(self):
        out = _jalankan('''
buat nilai = 5
cocokkan nilai {
    1: tulis "satu"
    5: tulis "lima"
    _: tulis "lain"
}
''')
        assert out == ["lima"]

    def test_konsisten_transpiler(self):
        kode = '''
buat data = [1, 2]
cocokkan data {
    [a, b]: tulis a + b
    _: tulis "lain"
}
buat orang = {"nama": "Ani"}
cocokkan orang {
    {"nama": "Ani"}: tulis "hai"
    _: tulis "siapa"
}
'''
        assert _jalankan_transpiler(kode) == ["3", "hai"]


# ============= V6.0: Error Handling Profesional =============

class TestErrorHandling:
    def test_kelas_error_dasar(self):
        out = _jalankan('''
kelas_error SaldoTidakCukup extends Kesalahan
    fungsi __init__(pesan, saldo)
        self.pesan = pesan
        self.saldo = saldo
    selesai
selesai
coba
    lempar SaldoTidakCukup("Saldo tidak cukup", 5000)
kecuali SaldoTidakCukup sebagai e
    tulis "Tertangkap: " + e.pesan + ", saldo=" + teks(e.saldo)
selesai
''')
        assert out == ["Tertangkap: Saldo tidak cukup, saldo=5000"]

    def test_hierarki_error(self):
        out = _jalankan('''
kelas_error ErrorValidasi extends Kesalahan
    fungsi __init__(pesan)
        self.pesan = pesan
    selesai
selesai
kelas_error ErrorNama extends ErrorValidasi
    fungsi __init__(pesan)
        self.pesan = pesan
    selesai
selesai
coba
    lempar ErrorNama("Nama kosong")
kecuali ErrorValidasi sebagai e
    tulis "Validasi: " + e.pesan
selesai
coba
    lempar ErrorNama("Nama kosong")
kecuali Kesalahan sebagai e
    tulis "Base: " + e.pesan
selesai
''')
        assert out == ["Validasi: Nama kosong", "Base: Nama kosong"]

    def test_kecuali_lainnya(self):
        out = _jalankan('''
kelas_error ErrorX extends Kesalahan
    fungsi __init__(pesan)
        self.pesan = pesan
    selesai
selesai
coba
    lempar ErrorX("boom")
kecuali ErrorLain sebagai e
    tulis "salah tipe"
kecuali lainnya sebagai e
    tulis "default: " + e.pesan
selesai
''')
        assert out == ["default: boom"]

    def test_error_tanpa_tangkap_propagates(self):
        from brolang.exceptions import BroLangError
        with pytest.raises(BroLangError):
            _jalankan('''
kelas_error ErrorX extends Kesalahan
    fungsi __init__(pesan)
        self.pesan = pesan
    selesai
selesai
lempar ErrorX("booom")
''')

    def test_kelas_error_konsisten_transpiler(self):
        kode = '''
kelas_error SaldoTidakCukup extends Kesalahan
    fungsi __init__(pesan, saldo)
        self.pesan = pesan
        self.saldo = saldo
    selesai
selesai
coba
    lempar SaldoTidakCukup("Saldo tidak cukup", 5000)
kecuali SaldoTidakCukup sebagai e
    tulis e.pesan
selesai
'''
        assert _jalankan_transpiler(kode) == ["Saldo tidak cukup"]

    def test_error_tersedia_di_interpret_ast_parser(self):
        # kelas_error bisa diparse sebagai node KelasErrorNode
        from brolang.ast.nodes import KelasErrorNode
        kode = '''
kelas_error ErrorX extends Kesalahan
    fungsi __init__(pesan)
        self.pesan = pesan
    selesai
selesai
'''
        ast = Parser(Lexer(kode).tokenize()).parse()
        assert any(isinstance(s, KelasErrorNode) for s in ast.statements)


# ============= V6.0: Ekosistem Stdlib =============

class TestStdlibV60:
    def test_tanggal(self):
        out = _jalankan('''
impor tanggal
tulis tanggal.selisih_hari("2026-08-07", "2026-08-01")
tulis tanggal.tambah_hari("2026-08-07", 3)
tulis tanggal.komponen("2026-08-07")["nama_bulan"]
''')
        assert out == ["6", "2026-08-10", "Agustus"]

    def test_tanggal_parse(self):
        out = _jalankan('''
impor tanggal
tulis tanggal.parse("07/08/2026")
tulis tanggal.parse("7 Agustus 2026")
''')
        assert out == ["2026-08-07", "2026-08-07"]

    def test_catat_level(self, capsys):
        _jalankan('''
impor catat
catat.atur_level("error")
catat.info("tidak muncul")
catat.error("muncul")
''')
        captured = capsys.readouterr().out
        assert "muncul" in captured
        assert "INFO" not in captured

    def test_catat_file(self):
        path = os.path.join(tempfile.mkdtemp(), "log.txt")
        _jalankan(f'''
impor catat
catat.atur_file("{path}")
catat.error("pesan ke file")
''')
        assert os.path.exists(path)
        with open(path) as f:
            assert "pesan ke file" in f.read()

    def test_lingkungan(self):
        out = _jalankan('''
impor lingkungan
lingkungan.set("BROLANG_TEST_VAR", "nilai123")
tulis lingkungan.get("BROLANG_TEST_VAR")
tulis lingkungan.ada("BROLANG_TEST_VAR")
''')
        assert out == ["nilai123", "True"]

    def test_proses(self):
        out = _jalankan('''
impor proses
buat hasil = proses.jalankan("echo halo dari proses")
tulis hasil.keluaran
tulis hasil.kode
''')
        assert out == ["halo dari proses", "0"]

    def test_csv_roundtrip(self):
        folder = tempfile.mkdtemp()
        path = os.path.join(folder, "data.csv")
        out = _jalankan(f'''
impor csv
buat data = [{{"nama": "Budi", "umur": 20}}, {{"nama": "Ani", "umur": 25}}]
csv.tulis("{path}", data)
buat dibaca = csv.baca("{path}")
tulis dibaca[0]["nama"]
tulis dibaca[1]["umur"]
''')
        assert out == ["Budi", "25"]

    def test_registri_buat_tar(self):
        from brolang.stdlib import get_stdlib_module
        registri = get_stdlib_module("registri")
        tar = registri.buat_tar({"nama": "x", "versi": "1.0.0"},
                                {"main.bro": "fungsi x()\nselesai\n"})
        assert tar[:2] == b"\x1f\x8b"  # gzip magic


# ============= V6.0: Regresi — fungsi bernama keyword & pipeline lengkap =============

class TestFungsiNamaKeyword:
    """Fungsi yang dinamai keyword reserved (mis. `cetak`) tetap bisa dipanggil."""

    def test_panggil_cetak_interpreter(self):
        out = _jalankan('''
fungsi cetak(nilai: Angka | Teks)
    tulis nilai
selesai
cetak(5)
cetak("lima")
''')
        assert out == ["5", "lima"]

    def test_panggil_cetak_transpiler(self):
        kode = '''
fungsi cetak(nilai: Angka | Teks)
    tulis nilai
selesai
cetak(42)
cetak("empat dua")
'''
        assert _jalankan_transpiler(kode) == ["42", "empat dua"]


class TestPipelineV60:
    """Fitur v6.0 harus jalan lewat pipeline lengkap CLI (`bro run`):
    analyzer → optimizer → transpiler.
    """

    def test_kelas_error_pipeline(self):
        out = _jalankan_pipeline('''
kelas_error SaldoTidakCukup extends Kesalahan
    fungsi __init__(pesan, saldo)
        self.pesan = pesan
        self.saldo = saldo
    selesai
selesai
coba
    lempar SaldoTidakCukup("Saldo tidak cukup", 5000)
kecuali SaldoTidakCukup sebagai e
    tulis e.pesan + " / " + teks(e.saldo)
selesai
''')
        assert out == ["Saldo tidak cukup / 5000"]

    def test_match_binding_pipeline(self):
        out = _jalankan_pipeline('''
buat data = [1, 2]
cocokkan data {
    [a, b]: tulis teks(a + b)
    _: tulis "lain"
}
''')
        assert out == ["3"]

    def test_match_objek_binding_pipeline(self):
        out = _jalankan_pipeline('''
buat orang = {"nama": "Ani", "umur": 20}
cocokkan orang {
    {"nama": n, "umur": u}: tulis n + "/" + teks(u)
    _: tulis "siapa"
}
''')
        assert out == ["Ani/20"]

    def test_guard_pipeline(self):
        out = _jalankan_pipeline('''
buat skor = 15
cocokkan skor {
    x jika x > 10: tulis "tinggi"
    _: tulis "rendah"
}
''')
        assert out == ["tinggi"]

    def test_tipe_anotasi_pipeline(self):
        out = _jalankan_pipeline('''
fungsi kali2(a: Angka) -> Angka
    kembali a * 2
selesai
tulis kali2(21)
''')
        assert out == ["42"]

    def test_type_alias_pipeline(self):
        # Analyzer tidak boleh salah lapor "Variabel 'Angka' belum didefinisikan"
        # untuk `tipe ID = Angka` — nama tipe bukan variabel runtime.
        out = _jalankan_pipeline('''
tipe ID = Angka
buat kode: ID = 12345
tulis kode + 1
''')
        assert out == ["12346"]

    def test_anotasi_tipe_salah_ditolak_analyzer(self):
        # `bro run` memakai analyzer dulu — mismatch tipe ditolak statis
        ok, errors = _analisa('buat umur: Angka = "salah"')
        assert not ok
        assert any("Tipe tidak cocok" in str(e) for e in errors)

    def test_anotasi_param_salah_ditolak_analyzer(self):
        ok, errors = _analisa('''
fungsi sapa(nama: Teks = 42)
    tulis nama
selesai
''')
        assert not ok
        assert any("default" in str(e).lower() for e in errors)

    def test_return_kosong_diizinkan(self):
        # Pola umum "tidak ditemukan → kembali kosong" tidak boleh
        # ditolak analyzer walau fungsi ber-anotasi tipe konkret.
        out = _jalankan_pipeline('''
fungsi cari(id: Angka) -> Objek
    jika id == 0 maka
        kembali kosong
    selesai
    kembali {"id": id}
selesai
buat hasil = cari(0)
jika hasil == kosong maka
    tulis "tidak ditemukan"
selesai
buat ada = cari(7)
tulis teks(ada["id"])
''')
        assert out == ["tidak ditemukan", "7"]

    def test_kelas_error_dikenal_analyzer(self):
        # Tanpa dukungan KelasErrorNode, analyzer melaporkan
        # "Fungsi 'SaldoTidakCukup' belum didefinisikan".
        ok, errors = _analisa('''
kelas_error ErrorX extends Kesalahan
    fungsi __init__(pesan)
        self.pesan = pesan
    selesai
selesai
coba
    lempar ErrorX("boom")
kecuali ErrorX sebagai e
    tulis e.pesan
selesai
''')
        assert ok, [str(e) for e in errors]

    def test_kesalahan_bawaan_dikenal_analyzer(self):
        ok, errors = _analisa('lempar Kesalahan("oops")')
        assert ok, [str(e) for e in errors]


# ============= V6.0: Package Registry Online =============

class TestPackageRegistry:
    def _setelah(self, server):
        pass

    def test_publish_install_roundtrip(self):
        from brolang.package_manager.manager import PackageManager
        from brolang.stdlib.registri import jalankan_async

        tmp = tempfile.mkdtemp(prefix="brolang_v60_reg_")
        try:
            proj = os.path.join(tmp, "paket-uji")
            os.makedirs(proj)
            import json as _json
            with open(os.path.join(proj, "brolang.json"), "w") as f:
                _json.dump({"nama": "paket-uji", "versi": "2.0.0",
                            "deskripsi": "Paket uji", "main": "main.bro",
                            "dependencies": []}, f)
            with open(os.path.join(proj, "main.bro"), "w") as f:
                f.write('fungsi halo()\n    kembali "halo paket"\nselesai\n')

            srv = jalankan_async(8790, "127.0.0.1",
                                 folder=os.path.join(tmp, "registry"))
            try:
                cwd = os.getcwd()
                os.chdir(proj)
                try:
                    pub = PackageManager(packages_dir=os.path.join(tmp, "pk1"))
                    assert pub.publish_remote("http://127.0.0.1:8790")

                    hasil = pub.cari_remote("paket-uji",
                                            registry_url="http://127.0.0.1:8790")
                    assert len(hasil) == 1
                    assert hasil[0]["version"] == "2.0.0"

                    konsumen = PackageManager(packages_dir=os.path.join(tmp, "pk2"))
                    assert konsumen.install("paket-uji",
                                            registry_url="http://127.0.0.1:8790")
                    assert konsumen.find_package("paket-uji")
                finally:
                    os.chdir(cwd)
            finally:
                srv.berhenti()
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
