"""
Unit tests untuk BroLang v6.8
=============================

Tests untuk:
- Floor Division (17 // 5, -17 // 5, x //= 2)
- Guard Clause (kembali x jika c, hentikan jika c, lanjutkan jika c)
- Augmented Assignment pada atribut objek & index list (self.x += 1, data[i] += 1)
- Perbaikan VM: %= dan **= (sebelumnya diam-diam rusak)
- Game dev: BGM prosedural (buat_bgm/mainkan_bgm + pola siap pakai)
"""

import io
import wave

import pytest

from brolang.lexer import Lexer
from brolang.parser import Parser
from brolang.interpreter import Interpreter
from brolang.exceptions import RuntimeError_, TypeError_, ZeroDivisionError_


def run_code(code):
    """Helper untuk menjalankan kode BroLang lewat interpreter."""
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    interp = Interpreter()
    interp.interpret(ast)
    return interp.output


def _mod(nama):
    """Ambil modul stdlib BroLang."""
    from brolang.stdlib import get_stdlib_module
    return get_stdlib_module(nama)


# ============= Lexer: Floor Division =============


class TestLexerFloorDiv:
    """Token `//` dan `//=` harus dikenali lexer."""

    def test_floor_div_token(self):
        from brolang.token_types import TokenType
        types = [t.type for t in Lexer("a // b").tokenize()]
        assert TokenType.TOKEN_FLOOR_DIV in types

    def test_floor_div_assign_token(self):
        from brolang.token_types import TokenType
        types = [t.type for t in Lexer("a //= b").tokenize()]
        assert TokenType.TOKEN_FLOOR_DIV_ASSIGN in types

    def test_divide_slash_masih_berfungsi(self):
        from brolang.token_types import TokenType
        types = [t.type for t in Lexer("a / b").tokenize()]
        assert TokenType.TOKEN_DIVIDE in types
        assert TokenType.TOKEN_FLOOR_DIV not in types

    def test_komen_slash_tidak_rusak(self):
        # `//` di dalam string harus tetap string biasa
        out = run_code('tulis "http://brolang"')
        assert "http://brolang" in out[0]


# ============= Floor Division =============


class TestFloorDivision:
    """17 // 5 = 3, -17 // 5 = -4, dst. (konsisten Python)."""

    def test_basic(self):
        out = run_code("tulis 17 // 5")
        assert "3" in out[0]

    def test_negatif(self):
        out = run_code("tulis -17 // 5")
        assert "-4" in out[0]

    def test_desimal(self):
        out = run_code("tulis 17.5 // 5")
        assert "3.0" in out[0]

    def test_augmented(self):
        out = run_code("buat x = 10\nx //= 3\ntulis x")
        assert "3" in out[0]

    def test_precedence(self):
        # // sama presedens dengan * dan /
        out = run_code("tulis 2 + 17 // 5 * 2")
        assert "8" in out[0]  # 2 + (17//5)*2 = 2 + 3*2 = 8

    def test_bagi_nol_error(self):
        with pytest.raises(ZeroDivisionError_, match="nol"):
            run_code("tulis 10 // 0")


# ============= Augmented Assignment (atribut & index) =============


class TestAugmentedAssignment:
    """v6.8: self.x += 1 dan data[i] += 1 kini berfungsi di semua mesin."""

    def test_attr_augmented(self):
        code = '''
kelas Akun
    fungsi __init__(self)
        self.total = 0
    selesai
    fungsi naik(self, n)
        self.total += n
        kembali self.total
    selesai
selesai
buat ak = Akun()
tulis ak.naik(5)
tulis ak.naik(7)
'''
        out = run_code(code)
        assert out == ["5", "12"], out

    def test_attr_augmented_gabungan(self):
        code = '''
kelas Kalkulator
    fungsi __init__(self)
        self.nilai = 10
    selesai
    fungsi proses(self)
        self.nilai *= 3
        self.nilai //= 2
        self.nilai -= 1
        kembali self.nilai
    selesai
selesai
buat k = Kalkulator()
tulis k.proses()
'''
        out = run_code(code)
        assert "14" in out[0]  # 10*3=30, 30//2=15, 15-1=14

    def test_index_augmented(self):
        out = run_code("buat data = [1, 2, 3]\ndata[1] += 10\ntulis data")
        assert "[1, 12, 3]" in out[0]

    def test_index_augmented_berulang(self):
        code = '''
buat skor = [0, 0, 0]
untuk i dari 0 sampai 2 lakukan
    skor[i] += 10
selesai
tulis skor
'''
        out = run_code(code)
        assert "[10, 10, 10]" in out[0]

    def test_index_augmented_div(self):
        out = run_code("buat d = [10, 20]\nd[0] //= 3\ntulis d")
        assert "[3, 20]" in out[0]

    def test_index_augmented_mod_pow(self):
        out = run_code("buat d = [7, 2]\nd[0] %= 3\nd[1] **= 3\ntulis d")
        assert "[1, 8]" in out[0]

    def test_konstanta_tetap_ditolak(self):
        with pytest.raises(RuntimeError_, match="Konstanta"):
            run_code("konstanta X = 5\nX += 1")


# ============= Guard Clause =============


class TestGuardClause:
    """kembali x jika c — early return; hentikan/lanjutkan jika c."""

    def test_guard_return_basic(self):
        code = '''
fungsi cek(x)
    kembali "negatif" jika x < 0
    kembali "nol" jika x == 0
    kembali "positif"
selesai
tulis cek(-5), cek(0), cek(7)
'''
        out = run_code(code)
        assert "negatif nol positif" in out[0]

    def test_guard_return_tanpa_nilai(self):
        code = '''
fungsi cek(x)
    kembali jika x < 0
    kembali 42
selesai
tulis cek(-1), cek(5)
'''
        out = run_code(code)
        # cek(-1) -> None (kosong), cek(5) -> 42
        assert "None 42" in out[0]

    def test_guard_return_di_loop(self):
        code = '''
fungsi cari(daftar, target)
    untuk setiap nilai dalam daftar lakukan
        kembali nilai jika nilai == target
    selesai
    kembali -1
selesai
tulis cari([1, 5, 9], 9)
tulis cari([1, 5, 9], 100)
'''
        out = run_code(code)
        assert out == ["9", "-1"], out

    def test_guard_break(self):
        code = '''
buat total = 0
untuk i dari 1 sampai 10 lakukan
    hentikan jika i > 5
    total = total + i
selesai
tulis total
'''
        out = run_code(code)
        assert "15" in out[0]  # 1+2+3+4+5

    def test_guard_continue(self):
        code = '''
buat total = 0
untuk i dari 1 sampai 6 lakukan
    lanjutkan jika i % 2 == 0
    total = total + i
selesai
tulis total
'''
        out = run_code(code)
        assert "9" in out[0]  # 1+3+5

    def test_guard_break_false_tetap_lanjut(self):
        """Guard yang salah tidak boleh menghentikan loop (regresi: loop
        VM lama menghentikan kompilasi body setelah break)."""
        code = '''
buat hasil = []
untuk i dari 1 sampai 4 lakukan
    hentikan jika i > 10
    hasil = hasil + [i]
selesai
tulis hasil
'''
        out = run_code(code)
        assert "[1, 2, 3, 4]" in out[0]

    def test_guard_continue_dan_break_bersama(self):
        code = '''
buat total = 0
untuk i dari 1 sampai 10 lakukan
    lanjutkan jika i % 2 == 0
    hentikan jika i > 5
    total = total + i
selesai
tulis total
'''
        out = run_code(code)
        assert "9" in out[0]  # 1+3+5 (break saat i=6 genap sudah di-continue)

    def test_guard_di_selama(self):
        code = '''
buat x = 0
buat total = 0
selama benar lakukan
    x = x + 1
    lanjutkan jika x < 3
    total = total + x
    hentikan jika x >= 5
selesai
tulis total
'''
        out = run_code(code)
        assert "12" in out[0]  # x=3,4,5 -> 3+4+5=12

    def test_ternary_di_return_masih_berfungsi(self):
        """Regresi: `kembali a jika b lainnya c` tetap ternary."""
        code = '''
fungsi f(x)
    kembali x jika x > 0 lainnya 0
selesai
tulis f(5), f(-3)
'''
        out = run_code(code)
        assert "5 0" in out[0]

    def test_ternary_di_paren_dan_guard(self):
        code = '''
fungsi g(x)
    kembali (x * 2) jika x > 10 lainnya (x * 3)
selesai
tulis g(20), g(5)
'''
        out = run_code(code)
        assert "40 15" in out[0]

    def test_guard_multiple_return(self):
        """kembali a, b jika c — guard pada multiple return harus berfungsi."""
        code = '''
fungsi pasangan(x)
    kembali x, x * 2 jika x > 0
    kembali 0, 0
selesai
tulis pasangan(3)
tulis pasangan(-1)
'''
        out = run_code(code)
        assert out[0] == "(3, 6)", out
        assert out[1] == "(0, 0)", out

    def test_guard_return_value_tidak_dievaluasi(self):
        """Saat guard salah, value tidak boleh dievaluasi (konsistensi
        side-effect antar mesin — regresi VM yang mengeval value dulu)."""
        code = '''
buat dipanggil = 0
fungsi hitung(x)
    buat dipanggil = dipanggil + 1
    kembali x * 10
selesai
fungsi cek(x)
    kembali hitung(x) jika x > 100
    kembali -1
selesai
tulis cek(5)
tulis dipanggil
'''
        out = run_code(code)
        assert out == ["-1", "0"], out

    def test_trailing_comma_call_multi_baris(self):
        """Trailing comma + `)` di baris sendiri harus valid (v6.8)."""
        code = '''
fungsi f(a, b)
    kembali a + b
selesai
tulis f(
    1,
    2,
)
'''
        out = run_code(code)
        assert "3" in out[0]

    def test_guard_return_tanpa_analyser_error(self):
        """Guard return harus lolos SemanticAnalyzer (regresi: analyzer
        menolak 'kembali' pada decorated function karena konteks hilang)."""
        from brolang.semantic import SemanticAnalyzer
        code = '''
fungsi cek(x)
    kembali "ya" jika x > 0
    kembali "tidak"
selesai
tulis cek(1)
'''
        ast = Parser(Lexer(code).tokenize()).parse()
        analyzer = SemanticAnalyzer()
        assert analyzer.analyze(ast), [str(e) for e in analyzer.errors]


# ============= Full Pipeline (bro run jalur) =============


class TestFullPipelineV68:
    """Fitur v6.8 harus jalan lewat SemanticAnalyzer + Optimizer + Transpiler."""

    def _run_full(self, code):
        from brolang.semantic import SemanticAnalyzer
        from brolang.optimizer import Optimizer
        from brolang.vm.transpiler import Transpiler
        from contextlib import redirect_stdout

        ast = Parser(Lexer(code).tokenize()).parse()
        analyzer = SemanticAnalyzer()
        assert analyzer.analyze(ast), [str(e) for e in analyzer.errors]
        optimized = Optimizer().optimize(ast)
        py_code = Transpiler().transpile(optimized)
        buf = io.StringIO()
        with redirect_stdout(buf):
            exec(compile(py_code, "<test>", "exec"), {"__builtins__": __builtins__})
        return buf.getvalue().strip().splitlines()

    def test_floor_div_through_pipeline(self):
        out = self._run_full("tulis 17 // 5\ntulis -17 // 5")
        assert out == ["3", "-4"], out

    def test_floor_div_fold_optimizer(self):
        # Optimizer harus melipat konstanta 20 // 3 -> 6
        out = self._run_full("tulis 20 // 3")
        assert out == ["6"], out

    def test_guard_return_through_pipeline(self):
        code = '''
fungsi cek(x)
    kembali "negatif" jika x < 0
    kembali "positif"
selesai
tulis cek(-2)
tulis cek(3)
'''
        out = self._run_full(code)
        assert out == ["negatif", "positif"], out

    def test_guard_break_continue_through_pipeline(self):
        code = '''
buat total = 0
untuk i dari 1 sampai 10 lakukan
    lanjutkan jika i % 2 == 0
    hentikan jika i > 5
    total = total + i
selesai
tulis total
'''
        out = self._run_full(code)
        assert out == ["9"], out

    def test_attr_augmented_through_pipeline(self):
        code = '''
kelas Akun
    fungsi __init__(self)
        self.total = 0
    selesai
    fungsi naik(self, n)
        self.total += n
        kembali self.total
    selesai
selesai
buat ak = Akun()
tulis ak.naik(5)
'''
        out = self._run_full(code)
        assert out == ["5"], out

    def test_konsistensi_interpreter_vs_transpiler(self):
        """Output interpreter & transpiler harus identik untuk fitur v6.8."""
        code = '''
fungsi cek(x)
    kembali "negatif" jika x < 0
    kembali "nol" jika x == 0
    kembali "positif"
selesai
tulis cek(-5), cek(0), cek(7)
buat data = [1, 2, 3]
data[1] += 10
tulis data
buat x = 17
x //= 5
tulis x
buat total = 0
untuk i dari 1 sampai 10 lakukan
    lanjutkan jika i % 2 == 0
    hentikan jika i > 5
    total = total + i
selesai
tulis total
'''
        interp_out = [o for o in run_code(code) if o.strip()]
        transp_out = self._run_full(code)
        assert interp_out == transp_out, f"interp={interp_out} transp={transp_out}"


# ============= VM (Bytecode) v6.8 =============


class TestVMV68:
    """Fitur v6.8 di bytecode VM + regresi %= / **= yang diperbaiki."""

    def _run_vm(self, code):
        from brolang.vm.compiler import Compiler
        from brolang.vm.vm import VM

        ast = Parser(Lexer(code).tokenize()).parse()
        bytecode = Compiler().compile(ast)
        vm = VM()
        vm.run(bytecode)
        return vm.output

    def test_vm_floor_div(self):
        out = self._run_vm("tulis 17 // 5\ntulis -17 // 5")
        assert out == ["3", "-4"], out

    def test_vm_floor_div_augmented(self):
        out = self._run_vm("buat x = 10\nx //= 3\ntulis x")
        assert out == ["3"], out

    def test_vm_mod_pow_augmented(self):
        """Regresi: %= dan **= dulu diam-diam jadi `x = y` di VM."""
        out = self._run_vm("buat x = 7\nx %= 3\ntulis x\nbuat y = 2\ny **= 3\ntulis y")
        assert out == ["1", "8"], out

    def test_vm_attr_augmented(self):
        code = '''
kelas Akun
    fungsi __init__(self)
        self.total = 0
    selesai
    fungsi naik(self, n)
        self.total += n
        kembali self.total
    selesai
selesai
buat ak = Akun()
tulis ak.naik(5)
tulis ak.naik(7)
'''
        out = self._run_vm(code)
        assert out == ["5", "12"], out

    def test_vm_index_augmented(self):
        out = self._run_vm("buat data = [1, 2, 3]\ndata[1] += 10\ntulis data")
        assert out == ["[1, 12, 3]"], out

    def test_vm_index_augmented_loop(self):
        code = '''
buat skor = [0, 0, 0]
untuk i dari 0 sampai 2 lakukan
    skor[i] += 10
selesai
tulis skor
'''
        out = self._run_vm(code)
        assert out == ["[10, 10, 10]"], out

    def test_vm_guard_return(self):
        code = '''
fungsi cek(x)
    kembali "negatif" jika x < 0
    kembali "nol" jika x == 0
    kembali "positif"
selesai
tulis cek(-5), cek(0), cek(7)
'''
        out = self._run_vm(code)
        assert out == ["negatif nol positif"], out

    def test_vm_guard_break_continue(self):
        code = '''
buat total = 0
untuk i dari 1 sampai 10 lakukan
    lanjutkan jika i % 2 == 0
    hentikan jika i > 5
    total = total + i
selesai
tulis total
'''
        out = self._run_vm(code)
        assert out == ["9"], out

    def test_vm_guard_break_false_tetap_lanjut(self):
        code = '''
buat hasil = []
untuk i dari 1 sampai 4 lakukan
    hentikan jika i > 10
    hasil = hasil + [i]
selesai
tulis hasil
'''
        out = self._run_vm(code)
        assert out == ["[1, 2, 3, 4]"], out

    def test_vm_guard_return_value_tidak_dievaluasi(self):
        """VM: value tidak boleh dievaluasi saat guard salah (regresi review)."""
        code = '''
buat dipanggil = 0
fungsi hitung(x)
    buat dipanggil = dipanggil + 1
    kembali x * 10
selesai
fungsi cek(x)
    kembali hitung(x) jika x > 100
    kembali -1
selesai
tulis cek(5)
tulis dipanggil
'''
        interp_out = [o for o in run_code(code) if o.strip()]
        vm_out = self._run_vm(code)
        assert vm_out == interp_out == ["-1", "0"], (interp_out, vm_out)

    def test_vm_konsisten_dengan_interpreter(self):
        code = '''
fungsi cek(x)
    kembali x jika x < 0
    kembali 99
selesai
tulis cek(-1), cek(7)
buat d = [1, 2, 3]
d[0] += 100
tulis d
kelas K
    fungsi __init__(self)
        self.n = 10
    selesai
    fungsi p(self)
        self.n *= 2
        kembali self.n
    selesai
selesai
buat k = K()
tulis k.p()
buat total = 0
untuk i dari 1 sampai 6 lakukan
    lanjutkan jika i % 2 == 0
    total = total + i
selesai
tulis total
'''
        interp_out = [o for o in run_code(code) if o.strip()]
        vm_out = self._run_vm(code)
        assert interp_out == vm_out, f"interp={interp_out} vm={vm_out}"


# ============= Game Dev: BGM Prosedural =============


class TestBGMAudio:
    """Generator musik latar prosedural — WAV valid tanpa file eksternal."""

    def test_buat_bgm_menghasilkan_wav_valid(self):
        audio = _mod("audio")
        wav = audio.buat_bgm(["C4", "E4", "G4"])
        assert wav[:4] == b"RIFF"
        assert wav[8:12] == b"WAVE"
        w = wave.open(io.BytesIO(wav))
        assert w.getnchannels() == 1
        assert w.getframerate() == 22050
        assert w.getnframes() > 0

    def test_buat_bgm_frekuensi_langsung(self):
        audio = _mod("audio")
        wav = audio.buat_bgm([440.0, 0, 660.0])
        assert wav[:4] == b"RIFF"

    def test_buat_bgm_durasi_ketuk(self):
        audio = _mod("audio")
        pendek = audio.buat_bgm(["C4", "E4"], tempo=120)
        w1 = wave.open(io.BytesIO(pendek))
        # 2 ketuk @120bpm = 2 * 0.5 dtk = 1 dtk @22050 Hz
        assert abs(w1.getnframes() - 22050) < 500

    def test_buat_bgm_tuple_durasi(self):
        audio = _mod("audio")
        wav = audio.buat_bgm([("C4", 2), ("G4", 1)], tempo=120)
        w = wave.open(io.BytesIO(wav))
        # (2 + 1) ketuk = 3 * 0.5 = 1.5 dtk
        assert abs(w.getnframes() - 33075) < 800

    def test_nada_name_ke_frekuensi(self):
        audio = _mod("audio")
        c4 = audio.frekuensi_nada("C4")
        assert abs(c4 - 261.63) < 1.0
        a4 = audio.frekuensi_nada("A4")
        assert abs(a4 - 440.0) < 1.0

    def test_pola_siap_pakai(self):
        audio = _mod("audio")
        for nama in ("pola_arcade", "pola_epik", "pola_tenang"):
            pola = getattr(audio, nama)
            assert len(pola) > 0
            wav = audio.buat_bgm(pola)
            assert wav[:4] == b"RIFF", nama

    def test_simpan_bgm(self, tmp_path):
        audio = _mod("audio")
        path = tmp_path / "bgm.wav"
        audio.simpan_wav(audio.buat_bgm(audio.pola_arcade), str(path))
        assert path.exists()
        w = wave.open(str(path))
        assert w.getnframes() > 0
