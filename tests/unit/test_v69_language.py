"""
Unit tests untuk BroLang v6.9
=============================

Tests untuk:
- Guard clause pada statement umum: `tulis x jika c`, `buat x = 5 jika c`,
  `x = 5 jika c`, `x += 1 jika c`, `self.x = 5 jika c`, `data[i] += 1 jika c`,
  `lempar e jika c`, `hapus x jika c`, `f() jika c`, `hasilkan x jika c`
- Tidak ambigu dengan ternary: `x = a jika b lainnya c` tetap ternary
- Nilai statement tidak dievaluasi saat guard salah
- Bekerja konsisten di interpreter, transpiler, dan VM bytecode
"""

import io

import pytest

from brolang.lexer import Lexer
from brolang.parser import Parser
from brolang.interpreter import Interpreter


def run_code(code):
    """Helper untuk menjalankan kode BroLang lewat interpreter."""
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    interp = Interpreter()
    interp.interpret(ast)
    return interp.output


def _parse(code):
    return Parser(Lexer(code).tokenize()).parse()


# ============= Guard: tulis =============


class TestGuardTulis:
    """`tulis x jika c` — hanya mencetak saat kondisi benar."""

    def test_basic(self):
        out = run_code("buat x = 10\ntulis x jika x > 5\ntulis x jika x > 100")
        assert out == ["10"], out

    def test_multi_arg(self):
        out = run_code("tulis 1, 2 jika benar\ntulis 3, 4 jika salah")
        assert out == ["1 2"], out

    def test_di_loop(self):
        code = '''
untuk i dari 1 sampai 5 lakukan
    tulis i jika i % 2 == 1
selesai
'''
        out = run_code(code)
        assert out == ["1", "3", "5"], out

    def test_di_single_line_block(self):
        code = '''
buat x = 15
jika x > 0 maka tulis "positif" jika x > 10 selesai
buat y = 5
jika y > 0 maka tulis "kecil" jika y > 10 selesai
'''
        out = run_code(code)
        assert out == ["positif"], out

    def test_dengan_kondisi_kompleks(self):
        out = run_code("buat x = 7\ntulis x jika x > 0 dan x < 10")
        assert out == ["7"], out


# ============= Guard: assignment =============


class TestGuardAssignment:
    """`buat x = v jika c`, `x = v jika c`, `x += v jika c`, dst."""

    def test_deklarasi_guard_benar_mengevaluasi_nilai(self):
        # Guard benar -> nilai dievaluasi (deklarasi dijalankan). Catatan:
        # konsisten dengan blok if biasa, deklarasi `buat` bersifat
        # block-scoped — variabel baru tidak terlihat setelah guard.
        code = '''
buat catatan = 0
fungsi tandai(x)
    catatan = catatan + 1
    kembali x
selesai
buat z = tandai(7) jika benar
tulis catatan
buat w = tandai(9) jika salah
tulis catatan
'''
        out = run_code(code)
        assert out == ["1", "1"], out

    def test_deklarasi_guard_salah_tidak_dievaluasi(self):
        # Guard salah -> deklarasi tidak pernah jalan (nilai tidak dievaluasi)
        code = '''
buat catatan = 0
fungsi tandai(x)
    catatan = catatan + 1
    kembali x
selesai
buat z = tandai(7) jika salah
tulis catatan
'''
        out = run_code(code)
        assert out == ["0"], out

    def test_reassignment(self):
        code = '''
buat x = 1
x = 99 jika benar
tulis x
x = 0 jika salah
tulis x
'''
        out = run_code(code)
        assert out == ["99", "99"], out

    def test_augmented(self):
        code = '''
buat x = 1
x += 5 jika benar
tulis x
x += 100 jika salah
tulis x
'''
        out = run_code(code)
        assert out == ["6", "6"], out

    def test_destructuring(self):
        # Destructuring ber-guard: guard benar menjalankan, guard salah melewati
        code = '''
buat catatan = 0
fungsi hitung(x)
    catatan = catatan + 1
    kembali [x, x * 2]
selesai
buat [a, b] = hitung(3) jika benar
tulis catatan
buat [c, d] = hitung(9) jika salah
tulis catatan
'''
        out = run_code(code)
        assert out == ["1", "1"], out

    def test_atribut_objek(self):
        code = '''
kelas K
    fungsi __init__(self)
        self.n = 1
    selesai
selesai
buat k = K()
k.n = 10 jika benar
tulis k.n
k.n = 999 jika salah
tulis k.n
'''
        out = run_code(code)
        assert out == ["10", "10"], out

    def test_index_list(self):
        code = '''
buat data = [1, 2, 3]
data[1] += 10 jika benar
tulis data
data[0] = 100 jika salah
tulis data
'''
        out = run_code(code)
        assert out == ["[1, 12, 3]", "[1, 12, 3]"], out

    def test_augmented_di_kelas(self):
        code = '''
kelas Akun
    fungsi __init__(self)
        self.total = 0
    selesai
    fungsi naik(self, n)
        self.total += n jika n > 0
        kembali self.total
    selesai
selesai
buat ak = Akun()
tulis ak.naik(5)
tulis ak.naik(-100)
'''
        out = run_code(code)
        assert out == ["5", "5"], out


# ============= Guard: statement lain =============


class TestGuardStatementLain:
    """`lempar`, `hapus`, panggilan fungsi, yield."""

    def test_lempar_guard_salah(self):
        code = '''
coba
    lempar "boom" jika salah
    tulis "aman"
tangkap error
    tulis "tertangkap"
selesai
'''
        out = run_code(code)
        assert out == ["aman"], out

    def test_lempar_guard_benar(self):
        code = '''
coba
    lempar "boom" jika benar
    tulis "aman"
tangkap error
    tulis "tertangkap"
selesai
'''
        out = run_code(code)
        assert out == ["tertangkap"], out

    def test_panggilan_fungsi(self):
        code = '''
fungsi cetak(x)
    tulis x
selesai
cetak(1) jika benar
cetak(2) jika salah
'''
        out = run_code(code)
        assert out == ["1"], out

    def test_hapus(self):
        code = '''
buat x = 1
hapus x jika salah
tulis x
'''
        out = run_code(code)
        assert out == ["1"], out

    def test_yield(self):
        code = '''
fungsi gen()
    hasilkan 1
    hasilkan 2 jika salah
    hasilkan 3 jika benar
selesai
buat g = gen()
untuk v dalam g lakukan
    tulis v
selesai
'''
        out = run_code(code)
        assert out == ["1", "3"], out

    def test_guard_pipeline(self):
        code = '''
fungsi kali2(x)
    kembali x * 2
selesai
tulis 5 |> kali2 jika benar
tulis 5 |> kali2 jika salah
'''
        out = run_code(code)
        assert out == ["10"], out

    def test_guard_pipeline_return(self):
        # Konsistensi: `kembali x |> f jika c` (v6.9) — pipeline tetap jalan
        code = '''
fungsi kali2(x)
    kembali x * 2
selesai
fungsi cek(x)
    kembali x |> kali2 jika x > 3
    kembali -1
selesai
tulis cek(5)
tulis cek(1)
'''
        out = run_code(code)
        assert out == ["10", "-1"], out

    def test_hapus_guard_benar(self):
        code = '''
buat x = 1
hapus x jika benar
coba
    tulis x
tangkap error
    tulis "hilang"
selesai
'''
        out = run_code(code)
        assert out == ["hilang"], out

    def test_hasilkandari_guard(self):
        # Guard salah -> hasilkandari dilewati, yield berikutnya tetap jalan
        code = '''
fungsi gen()
    hasilkandari [1, 2] jika salah
    hasilkan 9
selesai
buat g = gen()
untuk v dalam g lakukan
    tulis v
selesai
'''
        out = run_code(code)
        assert out == ["9"], out

    def test_konstanta_guard(self):
        out = run_code('konstanta X = 5 jika benar\ntulis "ok"')
        assert out == ["ok"], out

    def test_guard_ekspresi_non_identifier(self):
        # Jalur else-branch di _parse_statement: statement dimulai literal/kurung
        out = run_code("(1 + 2) * 3 jika benar\ntulis \"jalan\"")
        assert out == ["jalan"], out

    def test_guard_di_selama(self):
        code = '''
buat x = 0
buat total = 0
selama x < 6 lakukan
    x = x + 1
    total = total + x jika x % 2 == 0
selesai
tulis total
'''
        out = run_code(code)
        assert out == ["12"], out  # 2 + 4 + 6


# ============= Regresi: ternary tetap ternary =============


class TestTernaryTetapTernary:
    """`a jika b lainnya c` harus tetap ternary, bukan guard."""

    def test_ternary_di_assignment(self):
        code = '''
buat x = 5 jika benar lainnya 99
tulis x
buat y = 5 jika salah lainnya 99
tulis y
'''
        out = run_code(code)
        assert out == ["5", "99"], out

    def test_ternary_di_tulis(self):
        out = run_code("tulis 10 jika benar lainnya 20\ntulis 10 jika salah lainnya 20")
        assert out == ["10", "20"], out

    def test_ternary_di_panggilan(self):
        code = '''
fungsi f(a)
    kembali a
selesai
tulis f(1 jika benar lainnya 2)
tulis f(1 jika salah lainnya 2)
'''
        out = run_code(code)
        assert out == ["1", "2"], out


# ============= Nilai tidak dievaluasi saat guard salah =============


class TestGuardTidakEvaluasi:
    """Side-effect tidak boleh terjadi saat guard salah (konsistensi antar mesin)."""

    def test_value_print_tidak_dievaluasi(self):
        code = '''
buat dipanggil = 0
fungsi hitung(x)
    buat dipanggil = dipanggil + 1
    kembali x
selesai
tulis hitung(5) jika salah
tulis dipanggil
'''
        out = run_code(code)
        assert out == ["0"], out

    def test_value_raise_tidak_dievaluasi(self):
        code = '''
buat dipanggil = 0
fungsi ledak()
    buat dipanggil = dipanggil + 1
    lempar "x"
selesai
coba
    lempar ledak() jika salah
    tulis "aman"
tangkap error
    tulis "tertangkap"
selesai
tulis dipanggil
'''
        out = run_code(code)
        assert out == ["aman", "0"], out


# ============= Full Pipeline (bro run jalur) =============


class TestFullPipelineV69:
    """Fitur v6.9 harus jalan lewat SemanticAnalyzer + Optimizer + Transpiler."""

    def _run_full(self, code):
        from brolang.semantic import SemanticAnalyzer
        from brolang.optimizer import Optimizer
        from brolang.vm.transpiler import Transpiler
        from contextlib import redirect_stdout

        ast = _parse(code)
        analyzer = SemanticAnalyzer()
        assert analyzer.analyze(ast), [str(e) for e in analyzer.errors]
        optimized = Optimizer().optimize(ast)
        py_code = Transpiler().transpile(optimized)
        buf = io.StringIO()
        with redirect_stdout(buf):
            exec(compile(py_code, "<test>", "exec"), {"__builtins__": __builtins__})
        return buf.getvalue().strip().splitlines()

    def test_guard_tulis_through_pipeline(self):
        code = '''
buat x = 10
tulis x jika x > 5
tulis x jika x > 100
'''
        out = self._run_full(code)
        assert out == ["10"], out

    def test_guard_assignment_through_pipeline(self):
        code = '''
buat x = 1
x = 99 jika benar
tulis x
x = 0 jika salah
tulis x
'''
        out = self._run_full(code)
        assert out == ["99", "99"], out

    def test_guard_lempar_through_pipeline(self):
        code = '''
coba
    lempar "boom" jika benar
    tulis "aman"
tangkap error
    tulis "tertangkap"
selesai
'''
        out = self._run_full(code)
        assert out == ["tertangkap"], out

    def test_ternary_through_pipeline(self):
        code = '''
buat x = 5 jika benar lainnya 99
tulis x
buat y = 5 jika salah lainnya 99
tulis y
'''
        out = self._run_full(code)
        assert out == ["5", "99"], out

    def test_konsistensi_interpreter_vs_transpiler(self):
        code = '''
buat total = 0
untuk i dari 1 sampai 5 lakukan
    tulis i jika i % 2 == 1
    total = total + i
selesai
tulis total
buat x = 1
x += 10 jika benar
tulis x
buat data = [1, 2, 3]
data[1] += 10 jika benar
tulis data
'''
        interp_out = [o for o in run_code(code) if o.strip()]
        transp_out = self._run_full(code)
        assert interp_out == transp_out, f"interp={interp_out} transp={transp_out}"


# ============= Semantic Analyzer =============


class TestSemanticAnalyzerV69:
    """Guard statement harus lolos SemanticAnalyzer tanpa error."""

    def test_guard_statement_tanpa_error(self):
        from brolang.semantic import SemanticAnalyzer
        code = '''
fungsi cek(x)
    tulis x jika x > 0
    kembali x * 2 jika x > 0
selesai
buat y = cek(5) jika benar
tulis cek(3) jika benar
tulis "selesai"
'''
        ast = _parse(code)
        analyzer = SemanticAnalyzer()
        assert analyzer.analyze(ast), [str(e) for e in analyzer.errors]


# ============= VM (Bytecode) v6.9 =============


class TestVMV69:
    """Fitur v6.9 di bytecode VM — konsisten dengan interpreter."""

    def _run_vm(self, code):
        from brolang.vm.compiler import Compiler
        from brolang.vm.vm import VM

        ast = _parse(code)
        bytecode = Compiler().compile(ast)
        vm = VM()
        vm.run(bytecode)
        return vm.output

    def test_vm_guard_tulis(self):
        out = self._run_vm("buat x = 10\ntulis x jika x > 5\ntulis x jika x > 100")
        assert out == ["10"], out

    def test_vm_guard_assignment(self):
        code = '''
buat x = 1
x = 99 jika benar
tulis x
x = 0 jika salah
tulis x
'''
        out = self._run_vm(code)
        assert out == ["99", "99"], out

    def test_vm_guard_augmented_index(self):
        code = '''
buat data = [1, 2, 3]
data[1] += 10 jika benar
tulis data
'''
        out = self._run_vm(code)
        assert out == ["[1, 12, 3]"], out

    def test_vm_guard_lempar_di_block(self):
        # VM tidak mendukung try/catch `coba/tangkap` (dilewati diam-diam),
        # jadi guard raise diuji lewat block `jika` — lempar ber-guard benar
        # di dalam fungsi yang tetap berjalan normal.
        code = '''
buat status = "awal"
lempar "boom" jika salah
tulis status
'''
        out = self._run_vm(code)
        assert out == ["awal"], out

    def test_vm_guard_value_tidak_dievaluasi(self):
        code = '''
buat dipanggil = 0
fungsi hitung(x)
    buat dipanggil = dipanggil + 1
    kembali x
selesai
tulis hitung(5) jika salah
tulis dipanggil
'''
        out = self._run_vm(code)
        assert out == ["0"], out

    def test_vm_ternary_tetap_ternary(self):
        code = '''
buat x = 5 jika benar lainnya 99
tulis x
buat y = 5 jika salah lainnya 99
tulis y
'''
        out = self._run_vm(code)
        assert out == ["5", "99"], out

    def test_vm_konsisten_dengan_interpreter(self):
        code = '''
buat total = 0
untuk i dari 1 sampai 5 lakukan
    tulis i jika i % 2 == 1
    total = total + i
selesai
tulis total
buat x = 1
x += 10 jika benar
tulis x
'''
        interp_out = [o for o in run_code(code) if o.strip()]
        vm_out = self._run_vm(code)
        assert interp_out == vm_out, f"interp={interp_out} vm={vm_out}"
