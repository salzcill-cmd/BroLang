"""
Test BroLang v6.5 — Fitur Bahasa Baru
=====================================

Mencakup:
1. `konstanta` — variabel immutable (reassignment & augmented assignment → error)
2. `ulangi ... sampai` — do-until loop (body jalan minimal sekali)
3. `untuk i dari A sampai B langkah S` — range-based for loop (inklusif)

Setiap fitur diuji di interpreter DAN transpiler (jalur `bro run`).
"""

import subprocess
import sys
import tempfile
import os

import pytest

from brolang.lexer import Lexer
from brolang.parser import Parser
from brolang.semantic import SemanticAnalyzer
from brolang.optimizer import Optimizer
from brolang.interpreter import Interpreter
from brolang.ast.nodes import AssignmentNode, DoUntilNode, RangeForNode
from brolang.exceptions import RuntimeError_


def _parse(kode: str):
    """Lex + parse kode BroLang."""
    return Parser(Lexer(kode).tokenize()).parse()


def _jalankan(kode: str, pakai_optimizer: bool = False):
    """Jalankan kode via interpreter, kembalikan list output."""
    ast = _parse(kode)
    if pakai_optimizer:
        ast = Optimizer().optimize(ast)
    interp = Interpreter()
    interp.interpret(ast)
    return interp.output


def _jalankan_transpiler(kode: str):
    """Jalankan kode via transpiler (jalur cepat `bro run`), kembalikan list output."""
    from brolang.vm.transpiler import Transpiler
    import io
    import contextlib

    ast = _parse(kode)
    analyzer = SemanticAnalyzer()
    assert analyzer.analyze(ast), analyzer.errors
    ast = Optimizer().optimize(ast)
    py = Transpiler().transpile(ast)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        exec(compile(py, "<bro>", "exec"), {"__builtins__": __builtins__})
    return buf.getvalue().splitlines()


# ================= 1. Konstanta (immutable) =================


class TestKonstanta:
    def test_deklarasi_dan_baca(self):
        out = _jalankan('konstanta PI = 3.14\ntulis PI\n')
        assert out == ["3.14"]

    def test_konstanta_teks(self):
        out = _jalankan('konstanta NAMA = "BroLang"\ntulis NAMA\n')
        assert out == ["BroLang"]

    def test_reassignment_error_interpreter(self):
        ast = _parse('konstanta A = 1\nA = 5\n')
        with pytest.raises(Exception) as exc:
            Interpreter().interpret(ast)
        assert "Konstanta" in str(exc.value) or "tidak bisa diubah" in str(exc.value)

    def test_reassignment_error_analyzer(self):
        """bro run memakai analyzer → reassignment konstanta ditolak statis."""
        ast = _parse('konstanta A = 1\nA = 5\n')
        analyzer = SemanticAnalyzer()
        assert analyzer.analyze(ast) is False
        assert any("Konstanta" in str(e) for e in analyzer.errors)

    def test_augmented_assignment_error(self):
        ast = _parse('konstanta A = 1\nA += 5\n')
        with pytest.raises(Exception) as exc:
            Interpreter().interpret(ast)
        assert "Konstanta" in str(exc.value)

    def test_augmented_assignment_error_analyzer(self):
        ast = _parse('konstanta A = 1\nA += 5\n')
        analyzer = SemanticAnalyzer()
        assert analyzer.analyze(ast) is False

    def test_variabel_biasa_masih_bisa_diubah(self):
        out = _jalankan('buat x = 1\nx = 2\nx += 3\ntulis x\n')
        assert out == ["5"]

    def test_konstanta_di_scope_fungsi(self):
        out = _jalankan(
            'fungsi hitung()\n'
            '    konstanta BONUS = 10\n'
            '    kembali BONUS * 2\n'
            'selesai\n'
            'tulis hitung()\n'
        )
        assert out == ["20"]

    def test_konstanta_parse_ast(self):
        ast = _parse('konstanta PI = 3.14\n')
        stmt = ast.statements[0]
        assert isinstance(stmt, AssignmentNode)
        assert stmt.is_const is True
        assert stmt.target.name == "PI"

    def test_konstanta_dengan_anotasi_tipe(self):
        out = _jalankan('konstanta umur: Angka = 25\ntulis umur\n')
        assert out == ["25"]

    def test_konstanta_via_transpiler(self):
        out = _jalankan_transpiler('konstanta PI = 3.14\ntulis PI\n')
        assert out == ["3.14"]

    def test_konstanta_optimizer_preserve(self):
        ast = _parse('konstanta PI = 3.14\n')
        optimized = Optimizer().optimize(ast)
        stmt = optimized.statements[0]
        assert stmt.is_const is True

    def test_konstanta_reassignment_transpiler_ditolak_analyzer(self):
        """Konsisten: analyzer menolak sebelum transpiler jalan (bro run)."""
        ast = _parse('konstanta A = 1\nA = 5\n')
        analyzer = SemanticAnalyzer()
        assert analyzer.analyze(ast) is False

    def test_konstanta_destructuring_ditolak(self):
        """konstanta [a, b] = ... tidak didukung — tolak jelas, bukan diam-diam."""
        with pytest.raises(Exception) as exc:
            _parse('konstanta [a, b] = [1, 2]\n')
        assert "konstanta" in str(exc.value).lower()


# ================= 2. ulangi ... sampai (do-until) =================


class TestUlangiSampai:
    def test_body_jalan_minimal_sekali(self):
        """Kondisi sudah true sejak awal, tapi body tetap jalan sekali."""
        out = _jalankan('buat x = 0\nulangi\n    x = x + 1\nsampai x >= 1\ntulis x\n')
        assert out == ["1"]

    def test_loop_normal(self):
        out = _jalankan(
            'buat x = 0\n'
            'ulangi\n'
            '    tulis x\n'
            '    x = x + 1\n'
            'sampai x >= 3\n'
        )
        assert out == ["0", "1", "2"]

    def test_hentikan_di_dalam(self):
        out = _jalankan(
            'buat x = 0\n'
            'ulangi\n'
            '    x = x + 1\n'
            '    jika x == 2 maka\n'
            '        hentikan\n'
            '    selesai\n'
            'sampai x >= 10\n'
            'tulis x\n'
        )
        assert out == ["2"]

    def test_lanjutkan_di_dalam(self):
        out = _jalankan(
            'buat x = 0\n'
            'buat total = 0\n'
            'ulangi\n'
            '    x = x + 1\n'
            '    jika x % 2 == 0 maka\n'
            '        lanjutkan\n'
            '    selesai\n'
            '    total = total + x\n'
            'sampai x >= 5\n'
            'tulis total\n'
        )
        # 1 + 3 + 5 = 9
        assert out == ["9"]

    def test_parse_ast(self):
        ast = _parse('ulangi\n    pass\nsampai benar\n')
        stmt = ast.statements[0]
        assert isinstance(stmt, DoUntilNode)
        assert len(stmt.body) == 1

    def test_via_transpiler(self):
        out = _jalankan_transpiler(
            'buat x = 0\n'
            'ulangi\n'
            '    x = x + 1\n'
            'sampai x >= 3\n'
            'tulis x\n'
        )
        assert out == ["3"]

    def test_transpiler_body_minimal_sekali(self):
        out = _jalankan_transpiler(
            'buat x = 5\n'
            'ulangi\n'
            '    x = x + 1\n'
            'sampai x > 5\n'
            'tulis x\n'
        )
        assert out == ["6"]

    def test_bersarang(self):
        out = _jalankan(
            'buat i = 0\n'
            'buat hasil = 0\n'
            'ulangi\n'
            '    i = i + 1\n'
            '    buat j = 0\n'
            '    ulangi\n'
            '        j = j + 1\n'
            '        hasil = hasil + 1\n'
            '    sampai j >= 2\n'
            'sampai i >= 3\n'
            'tulis hasil\n'
        )
        assert out == ["6"]

    def test_analyzer_hentikan_valid(self):
        ast = _parse('ulangi\n    hentikan\nsampai benar\n')
        analyzer = SemanticAnalyzer()
        assert analyzer.analyze(ast) is True


# ================= 3. untuk i dari A sampai B (range for) =================


class TestRangeFor:
    def test_inklusif_naik(self):
        out = _jalankan('untuk i dari 1 sampai 5 lakukan\n    tulis i\nselesai\n')
        assert out == ["1", "2", "3", "4", "5"]

    def test_inklusif_turun_otomatis(self):
        """Tanpa langkah, start > end → langkah otomatis -1."""
        out = _jalankan('untuk i dari 3 sampai 1 lakukan\n    tulis i\nselesai\n')
        assert out == ["3", "2", "1"]

    def test_langkah_positif(self):
        out = _jalankan('untuk i dari 1 sampai 10 langkah 3 lakukan\n    tulis i\nselesai\n')
        assert out == ["1", "4", "7", "10"]

    def test_langkah_negatif(self):
        out = _jalankan('untuk i dari 10 sampai 1 langkah -2 lakukan\n    tulis i\nselesai\n')
        assert out == ["10", "8", "6", "4", "2"]

    def test_else_body_eksekusi(self):
        out = _jalankan(
            'untuk i dari 1 sampai 3 lakukan\n'
            '    tulis i\n'
            'lainnya\n'
            '    tulis "selesai"\n'
            'selesai\n'
        )
        assert out == ["1", "2", "3", "selesai"]

    def test_else_body_tidak_eksekusi_saat_hentikan(self):
        out = _jalankan(
            'untuk i dari 1 sampai 5 lakukan\n'
            '    jika i == 2 maka\n'
            '        hentikan\n'
            '    selesai\n'
            'lainnya\n'
            '    tulis "selesai"\n'
            'selesai\n'
            'tulis "akhir"\n'
        )
        assert out == ["akhir"]

    def test_variabel_range_pakai_ekspresi(self):
        out = _jalankan(
            'buat n = 3\n'
            'untuk i dari n sampai n + 2 lakukan\n'
            '    tulis i\n'
            'selesai\n'
        )
        assert out == ["3", "4", "5"]

    def test_parse_ast(self):
        ast = _parse('untuk i dari 1 sampai 10 langkah 2 lakukan\n    tulis i\nselesai\n')
        stmt = ast.statements[0]
        assert isinstance(stmt, RangeForNode)
        assert stmt.variable == "i"
        assert stmt.step is not None

    def test_parse_ast_tanpa_langkah(self):
        ast = _parse('untuk i dari 1 sampai 5 lakukan\n    tulis i\nselesai\n')
        stmt = ast.statements[0]
        assert isinstance(stmt, RangeForNode)
        assert stmt.step is None

    def test_via_transpiler_naik(self):
        out = _jalankan_transpiler('untuk i dari 1 sampai 5 lakukan\n    tulis i\nselesai\n')
        assert out == ["1", "2", "3", "4", "5"]

    def test_via_transpiler_turun(self):
        out = _jalankan_transpiler('untuk i dari 3 sampai 1 lakukan\n    tulis i\nselesai\n')
        assert out == ["3", "2", "1"]

    def test_via_transpiler_langkah_negatif(self):
        out = _jalankan_transpiler('untuk i dari 5 sampai 1 langkah -2 lakukan\n    tulis i\nselesai\n')
        assert out == ["5", "3", "1"]

    def test_via_transpiler_else(self):
        out = _jalankan_transpiler(
            'untuk i dari 1 sampai 2 lakukan\n'
            '    tulis i\n'
            'lainnya\n'
            '    tulis "habis"\n'
            'selesai\n'
        )
        assert out == ["1", "2", "habis"]

    def test_analyzer_valid(self):
        ast = _parse('untuk i dari 1 sampai 10 lakukan\n    tulis i\nselesai\n')
        analyzer = SemanticAnalyzer()
        assert analyzer.analyze(ast) is True

    def test_lanjutkan_di_range_for(self):
        """`lanjutkan` melewati sisa body, loop tetap lanjut (interpreter)."""
        out = _jalankan(
            'buat hasil = []\n'
            'untuk i dari 1 sampai 6 lakukan\n'
            '    jika i % 2 == 0 maka\n'
            '        lanjutkan\n'
            '    selesai\n'
            '    hasil.append(i)\n'
            'selesai\n'
            'tulis hasil\n'
        )
        assert out == ["[1, 3, 5]"]

    def test_lanjutkan_via_transpiler(self):
        out = _jalankan_transpiler(
            'buat hasil = []\n'
            'untuk i dari 1 sampai 6 lakukan\n'
            '    jika i % 2 == 0 maka\n'
            '        lanjutkan\n'
            '    selesai\n'
            '    hasil.append(i)\n'
            'selesai\n'
            'tulis hasil\n'
        )
        assert out == ["[1, 3, 5]"]

    def test_langkah_nol_error(self):
        ast = _parse('untuk i dari 1 sampai 5 langkah 0 lakukan\n    tulis i\nselesai\n')
        with pytest.raises(Exception) as exc:
            Interpreter().interpret(ast)
        assert "nol" in str(exc.value).lower() or "0" in str(exc.value)


# ================= 3b. Compiler package (bro build) =================


class TestBroBuild:
    """Compiler package (jalur `bro build`) harus konsisten dengan interpreter."""

    @staticmethod
    def _compile_exec(kode: str):
        from brolang.compiler import compile_source
        import io
        import contextlib

        py = compile_source(kode)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            exec(compile(py, "<bro>", "exec"))
        return buf.getvalue().splitlines()

    def test_range_for_build(self):
        out = self._compile_exec(
            'untuk i dari 1 sampai 5 lakukan\n    tulis i\nselesai\n'
        )
        assert out == ["1", "2", "3", "4", "5"]

    def test_range_for_langkah_negatif_build(self):
        out = self._compile_exec(
            'untuk i dari 5 sampai 1 langkah -2 lakukan\n    tulis i\nselesai\n'
        )
        assert out == ["5", "3", "1"]

    def test_ekspresi_dievaluasi_sekali(self):
        """start/end/step dievaluasi sekali via temp — ekspresi asli tak diduplikasi."""
        from brolang.compiler import compile_source

        py = compile_source(
            'untuk i dari mulai() sampai akhir() langkah jalan() lakukan\n'
            '    tulis i\n'
            'selesai\n'
        )
        # Setiap ekspresi muncul persis sekali (di assignment temp),
        # bukan diduplikasi inline di range/if seperti versi sebelum fix.
        assert py.count("mulai()") == 1
        assert py.count("akhir()") == 1
        assert py.count("jalan()") == 1
        assert "_bro_tmp_" in py

    def test_do_until_build(self):
        out = self._compile_exec(
            'buat x = 0\n'
            'ulangi\n'
            '    x = x + 1\n'
            'sampai x >= 3\n'
            'tulis x\n'
        )
        assert out == ["3"]

    def test_konstanta_build(self):
        out = self._compile_exec('konstanta PI = 3.14\ntulis PI\n')
        assert out == ["3.14"]


# ================= 3c. VM bytecode (bro benchmark) =================


class TestVMv65:
    """VM fast-path: do-until harus jalan benar termasuk `hentikan`/`lanjutkan`."""

    @staticmethod
    def _vm_run(kode: str):
        from brolang.vm import Compiler, VM

        ast = _parse(kode)
        bytecode = Compiler().compile(ast)
        vm = VM()
        vm.run(bytecode)
        return vm.output

    def test_do_until_vm(self):
        out = self._vm_run(
            'buat x = 0\n'
            'ulangi\n'
            '    x = x + 1\n'
            'sampai x >= 3\n'
            'tulis x\n'
        )
        assert out == ["3"]

    def test_do_until_hentikan_vm(self):
        """Break di do-until harus lompat keluar, bukan infinite loop saat
        kondisi masih FALSE (regresi fix jump target)."""
        out = self._vm_run(
            'buat x = 0\n'
            'ulangi\n'
            '    x = x + 1\n'
            '    jika x == 2 maka\n'
            '        hentikan\n'
            '    selesai\n'
            'sampai x >= 100\n'
            'tulis x\n'
        )
        assert out == ["2"]

    def test_do_until_lanjutkan_vm(self):
        out = self._vm_run(
            'buat x = 0\n'
            'buat total = 0\n'
            'ulangi\n'
            '    x = x + 1\n'
            '    jika x % 2 == 0 maka\n'
            '        lanjutkan\n'
            '    selesai\n'
            '    total = total + x\n'
            'sampai x >= 5\n'
            'tulis total\n'
        )
        assert out == ["9"]

    def test_do_until_lanjutkan_cek_kondisi(self):
        """Regresi: `lanjutkan` di do-until harus ke cek kondisi, bukan infinite
        loop. Program ini tidak akan pernah berhenti jika continue salah arah
        ke awal body — dijalankan via subprocess dengan timeout supaya regresi
        tidak menggantung seluruh suite."""
        script = (
            "import sys\n"
            "from brolang.lexer import Lexer\n"
            "from brolang.parser import Parser\n"
            "from brolang.vm import Compiler, VM\n"
            "kode = '''buat x = 0\n"
            "ulangi\n"
            "    x = x + 1\n"
            "    lanjutkan\n"
            "sampai x >= 3\n"
            "tulis x\n'''\n"
            "ast = Parser(Lexer(kode).tokenize()).parse()\n"
            "vm = VM()\n"
            "vm.run(Compiler().compile(ast))\n"
            "print(vm.output[0])\n"
        )
        result = subprocess.run(
            [sys.executable, "-c", script],
            capture_output=True, text=True, timeout=15,
        )
        assert result.returncode == 0, result.stderr
        assert result.stdout.strip() == "3"


# ================= 4. Konsistensi interpreter vs transpiler =================


class TestKonsistensi:
    KASUS = [
        'konstanta PI = 3.14\ntulis PI\n',
        'buat x = 0\nulangi\n    x = x + 1\nsampai x >= 4\ntulis x\n',
        'untuk i dari 1 sampai 7 langkah 2 lakukan\n    tulis i\nselesai\n',
        'untuk i dari 5 sampai 1 lakukan\n    tulis i\nselesai\n',
        (
            'buat total = 0\n'
            'untuk i dari 1 sampai 10 lakukan\n'
            '    jika i % 2 == 0 maka\n'
            '        total = total + i\n'
            '    selesai\n'
            'selesai\n'
            'tulis total\n'
        ),
    ]

    @pytest.mark.parametrize("kode", KASUS)
    def test_output_identik(self, kode):
        interp = _jalankan(kode, pakai_optimizer=True)
        transp = _jalankan_transpiler(kode)
        assert interp == transp


# ================= 5. CLI bro run (pipeline penuh) =================


class TestCLIv65:
    def test_bro_run_fitur_baru(self):
        with tempfile.TemporaryDirectory(prefix="brolang_v65_") as tmp:
            file_path = os.path.join(tmp, "fitur.bro")
            with open(file_path, "w") as f:
                f.write(
                    'konstanta NAMA = "v6.5"\n'
                    'tulis NAMA\n'
                    'buat x = 0\n'
                    'ulangi\n'
                    '    x = x + 1\n'
                    'sampai x >= 3\n'
                    'tulis x\n'
                    'untuk i dari 1 sampai 3 lakukan\n'
                    '    tulis i\n'
                    'selesai\n'
                )
            result = subprocess.run(
                [sys.executable, "-m", "brolang.cli", "run", file_path],
                capture_output=True, text=True,
            )
            assert result.returncode == 0, result.stdout + result.stderr
            lines = result.stdout.splitlines()
            assert lines[0] == "v6.5"
            assert lines[1] == "3"
            assert lines[2:] == ["1", "2", "3"]

    def test_bro_run_konstanta_error(self):
        """bro run menolak reassignment konstanta (via analyzer)."""
        with tempfile.TemporaryDirectory(prefix="brolang_v65_") as tmp:
            file_path = os.path.join(tmp, "const_error.bro")
            with open(file_path, "w") as f:
                f.write('konstanta A = 1\nA = 5\n')
            result = subprocess.run(
                [sys.executable, "-m", "brolang.cli", "run", file_path],
                capture_output=True, text=True,
            )
            assert result.returncode == 1
            assert "Konstanta" in result.stdout or "Konstanta" in result.stderr
