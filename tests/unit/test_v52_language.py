"""
Unit tests untuk BroLang v5.2 Features
=======================================

Tests untuk:
- Keyword Arguments (nama=nilai)
- Pipeline Operator (|>)
- Destructuring Assignment (buat [a,b] = list / buat {x,y} = objek)
- Package Manager (brolang.json, publish, install, import)
"""

import os
import sys
import json
import shutil
import tempfile

import pytest

from brolang.lexer import Lexer
from brolang.parser import Parser
from brolang.interpreter import Interpreter
from brolang.exceptions import RuntimeError_, TypeError_


def run_code(code):
    """Helper untuk menjalankan kode BroLang."""
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    interp = Interpreter()
    interp.interpret(ast)
    return interp.output


# ============= Keyword Arguments =============


class TestKeywordArguments:
    """Tests untuk Keyword Arguments v5.2."""

    def test_kwargs_basic(self):
        code = '''
fungsi sapa(nama, umur)
    kembali nama + " (" + teks(umur) + ")"
selesai
tulis sapa(nama="Budi", umur=25)
'''
        output = run_code(code)
        assert "Budi (25)" in output[0]

    def test_kwargs_mixed(self):
        code = '''
fungsi gabung(a, b, c)
    kembali a + b + c
selesai
tulis gabung("x", c="z", b="y")
'''
        output = run_code(code)
        assert "xyz" in output[0]

    def test_kwargs_with_defaults(self):
        code = '''
fungsi sapa(nama, umur=0)
    kembali "Halo " + nama + " umur " + teks(umur)
selesai
tulis sapa(nama="Ani")
'''
        output = run_code(code)
        assert "Halo Ani umur 0" in output[0]

    def test_kwargs_unknown_raises(self):
        code = '''
fungsi f(a)
    kembali a
selesai
f(b=1)
'''
        with pytest.raises(RuntimeError_):
            run_code(code)

    def test_kwargs_on_method(self):
        code = '''
kelas Kalkulator
    fungsi __init__(self, nilai=0)
        self.nilai = nilai
    selesai

    fungsi tambah(self, x, y=1)
        kembali self.nilai + x + y
    selesai
selesai

buat k = Kalkulator(nilai=10)
tulis(k.tambah(x=5))
'''
        output = run_code(code)
        assert "16" in output[0]

    def test_kwargs_on_lambda(self):
        code = '''
buat kali = lalu(a, b) a * b
tulis kali(b=5, a=4)
'''
        output = run_code(code)
        assert "20" in output[0]

    def test_kwargs_on_class_constructor(self):
        code = '''
kelas Titik
    fungsi __init__(self, x, y)
        self.x = x
        self.y = y
    selesai
selesai
buat p = Titik(y=2, x=3)
tulis p.x + p.y
'''
        output = run_code(code)
        assert "5" in output[0]


# ============= Pipeline Operator =============


class TestPipelineOperator:
    """Tests untuk Pipeline Operator (|>) v5.2."""

    def test_pipeline_with_function(self):
        code = '''
fungsi kali2(x)
    kembali x * 2
selesai
buat hasil = 21 |> kali2
tulis hasil
'''
        output = run_code(code)
        assert "42" in output[0]

    def test_pipeline_with_lambda(self):
        code = '''
buat hasil = 5 |> lalu(x) x * 10
tulis hasil
'''
        output = run_code(code)
        assert "50" in output[0]

    def test_pipeline_chained(self):
        code = '''
fungsi tambah1(x)
    kembali x + 1
selesai
fungsi kali2(x)
    kembali x * 2
selesai
buat hasil = 10 |> tambah1 |> kali2
tulis hasil
'''
        output = run_code(code)
        assert "22" in output[0]

    def test_pipeline_with_map(self):
        code = '''
buat hasil = [1, 2, 3] |> peta(lalu(x) x + 1)
tulis hasil
'''
        output = run_code(code)
        assert "[2, 3, 4]" in output[0]

    def test_pipeline_with_filter(self):
        code = '''
buat hasil = [1, 2, 3, 4] |> saring(lalu(x) x % 2 == 0)
tulis hasil
'''
        output = run_code(code)
        assert "[2, 4]" in output[0]

    def test_pipeline_with_reduce(self):
        code = '''
buat hasil = [1, 2, 3, 4, 5] |> kurangi(lalu(a, b) a + b, 0)
tulis hasil
'''
        output = run_code(code)
        assert "15" in output[0]

    def test_pipeline_returns_value(self):
        code = '''
fungsi kali3(x)
    kembali x * 3
selesai
buat hasil = 7 |> kali3
tulis hasil * 2
'''
        output = run_code(code)
        assert "42" in output[0]


# ============= Destructuring Assignment =============


class TestDestructuringAssignment:
    """Tests untuk Destructuring Assignment v5.2."""

    def test_destructure_list(self):
        code = '''
buat [a, b, c] = [1, 2, 3]
tulis a + b + c
'''
        output = run_code(code)
        assert "6" in output[0]

    def test_destructure_list_2(self):
        code = '''
buat [x, y] = [10, 20]
tulis x * y
'''
        output = run_code(code)
        assert "200" in output[0]

    def test_destructure_object(self):
        code = '''
buat {nama, umur} = {"nama": "Budi", "umur": 17}
tulis nama, umur
'''
        output = run_code(code)
        assert "Budi 17" in output[0]

    def test_destructure_swap(self):
        code = '''
buat [a, b] = [1, 2]
buat temp = a
a = b
b = temp
tulis a, b
'''
        output = run_code(code)
        assert "2 1" in output[0]

    def test_destructure_too_few_elements(self):
        code = '''
buat [a, b, c] = [1, 2]
'''
        with pytest.raises(RuntimeError_):
            run_code(code)

    def test_destructure_wrong_type(self):
        code = '''
buat [a, b] = "notalist"
'''
        with pytest.raises(TypeError_):
            run_code(code)

    def test_destructure_tuple_source(self):
        code = '''
buat [x, y] = (5, 7)
tulis x + y
'''
        output = run_code(code)
        assert "12" in output[0]

    def test_destructure_object_missing_key(self):
        code = '''
buat {x, y} = {"x": 1}
tulis x, y
'''
        output = run_code(code)
        assert "1 None" in output[0]


# ============= Package Manager =============


class TestPackageManager:
    """Tests untuk Package Manager v5.2."""

    @pytest.fixture()
    def pkg_env(self):
        """Buat environment package manager terisolasi."""
        from brolang.package_manager.manager import PackageManager

        tmp = tempfile.mkdtemp(prefix="brolang_pkg_test_")
        packages_dir = os.path.join(tmp, "packages")
        registry_dir = os.path.join(tmp, "registry")

        manager = PackageManager(packages_dir=packages_dir, registry_url=registry_dir)

        # Paket sumber
        src = os.path.join(tmp, "src")
        os.makedirs(src)
        with open(os.path.join(src, "brolang.json"), "w") as f:
            json.dump({
                "nama": "paket_uji",
                "versi": "1.0.0",
                "deskripsi": "Paket untuk testing",
                "main": "main.bro",
            }, f)
        with open(os.path.join(src, "main.bro"), "w") as f:
            f.write('''
fungsi sapa()
    kembali "Halo dari paket uji!"
selesai
''')

        yield manager, src, tmp
        shutil.rmtree(tmp, ignore_errors=True)

    def test_create_manifest(self):
        from brolang.package_manager.manager import PackageManager
        manifest = PackageManager.create_manifest("testpkg", "2.0.0", "desc")
        assert manifest["nama"] == "testpkg"
        assert manifest["versi"] == "2.0.0"
        assert manifest["deskripsi"] == "desc"
        assert "main" in manifest

    def test_install_from_dir(self, pkg_env):
        manager, src, _ = pkg_env
        assert manager.install(src) is True
        packages = manager.list_packages()
        assert any(p.name == "paket_uji" for p in packages)

    def test_publish_then_install(self, pkg_env):
        manager, src, tmp = pkg_env

        # Publish butuh cwd di folder source
        old_cwd = os.getcwd()
        os.chdir(src)
        try:
            assert manager.publish() is True
        finally:
            os.chdir(old_cwd)

        # Install di project lain
        other = os.path.join(tmp, "other")
        os.makedirs(other)
        os.chdir(other)
        try:
            assert manager.install("paket_uji") is True
        finally:
            os.chdir(old_cwd)

    def test_import_installed_package(self, pkg_env):
        """Package terinstall bisa di-import dari bahasa BroLang."""
        manager, src, tmp = pkg_env
        assert manager.install(src) is True

        code = '''
impor paket_uji
tulis paket_uji.sapa()
'''
        old = os.environ.get("BROLANG_PACKAGES_DIR")
        os.environ["BROLANG_PACKAGES_DIR"] = manager.packages_dir
        try:
            output = run_code(code)
            assert "Halo dari paket uji!" in output[0]
        finally:
            if old is None:
                os.environ.pop("BROLANG_PACKAGES_DIR", None)
            else:
                os.environ["BROLANG_PACKAGES_DIR"] = old

    def test_remove(self, pkg_env):
        manager, src, _ = pkg_env
        manager.install(src)
        assert manager.remove("paket_uji") is True
        assert manager.remove("paket_uji") is False

    def test_search(self, pkg_env):
        manager, src, _ = pkg_env
        manager.install(src)
        results = manager.search("uji")
        assert any(r["name"] == "paket_uji" for r in results)


# ============= Lexer: Pipeline Token =============


class TestPipelineToken:
    """Tests untuk token |> di lexer."""

    def test_pipeline_token(self):
        from brolang.token_types import TokenType
        tokens = Lexer("x |> f").tokenize()
        types = [t.type for t in tokens]
        assert TokenType.TOKEN_PIPE_GREATER in types

    def test_pipe_or_still_works(self):
        tokens = Lexer("a || b").tokenize()
        types = [t.type for t in tokens]
        from brolang.token_types import TokenType
        assert TokenType.TOKEN_ATAU in types
        assert TokenType.TOKEN_PIPE_GREATER not in types

    def test_bitwise_pipe_still_works(self):
        tokens = Lexer("a | b").tokenize()
        types = [t.type for t in tokens]
        from brolang.token_types import TokenType
        assert TokenType.TOKEN_PIPE in types
        assert TokenType.TOKEN_PIPE_GREATER not in types


# ============= Regression: Full Pipeline (Lexer→Parser→Analyzer→Optimizer→Transpiler) =============


class TestFullPipelineV52:
    """Fitur v5.2 harus jalan lewat jalur penuh yang dipakai `bro run`
    (SemanticAnalyzer + Optimizer + Transpiler), bukan cuma interpreter."""

    def _run_full(self, code):
        from brolang.semantic import SemanticAnalyzer
        from brolang.optimizer import Optimizer
        from brolang.vm.transpiler import Transpiler

        ast = Parser(Lexer(code).tokenize()).parse()
        analyzer = SemanticAnalyzer()
        assert analyzer.analyze(ast), [str(e) for e in analyzer.errors]
        optimized = Optimizer().optimize(ast)
        py_code = Transpiler().transpile(optimized)
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with redirect_stdout(buf):
            exec(compile(py_code, "<test>", "exec"), {"__builtins__": __builtins__})
        return buf.getvalue().strip().splitlines()

    def test_kwargs_survive_optimizer(self):
        """Optimizer tidak boleh menghilangkan keyword arguments."""
        code = '''
fungsi sapa(nama, umur=0)
    kembali "Halo " + nama + " umur " + teks(umur)
selesai
tulis sapa(nama="Budi", umur=25)
tulis sapa(nama="Ani")
'''
        out = self._run_full(code)
        assert out[0] == "Halo Budi umur 25", out
        assert out[1] == "Halo Ani umur 0", out

    def test_pipeline_through_full_pipeline(self):
        code = '''
fungsi kali2(x)
    kembali x * 2
selesai
buat hasil = 21 |> kali2
tulis hasil
'''
        out = self._run_full(code)
        assert out[0] == "42", out

    def test_destructuring_survives_analyzer(self):
        """SemanticAnalyzer harus mengenali variabel dari destructuring."""
        code = '''
buat [a, b, c] = [1, 2, 3]
tulis a + b + c
'''
        out = self._run_full(code)
        assert out[0] == "6", out

    def test_destructuring_object_through_full_pipeline(self):
        code = '''
buat {nama, umur} = {"nama": "Budi", "umur": 17}
tulis nama, umur
'''
        out = self._run_full(code)
        assert "Budi" in out[0] and "17" in out[0], out

    def test_kwargs_with_defaults_through_interpreter(self):
        """Default parameter + kwargs harus jalan di interpreter juga."""
        code = '''
fungsi sapa(nama, umur=0)
    kembali "Halo " + nama + " umur " + teks(umur)
selesai
tulis sapa(nama="Budi")
'''
        output = run_code(code)
        assert "Halo Budi umur 0" in output[0]


# ============= Regression: VM (Bytecode) =============


class TestVMV52:
    """Fitur & perbaikan VM v5.2."""

    def _run_vm(self, code):
        from brolang.vm.compiler import Compiler
        from brolang.vm.vm import VM
        ast = Parser(Lexer(code).tokenize()).parse()
        bytecode = Compiler().compile(ast)
        vm = VM()
        vm.run(bytecode)
        return vm.output

    def test_builtin_shadowing_invalidates_cache(self):
        """User menimpa nama builtin setelah cache terisi harus terlihat."""
        code = '''
tulis panjang([1, 2, 3])
buat panjang = 5
tulis panjang
tulis panjang + 1
'''
        out = self._run_vm(code)
        assert out == ["3", "5", "6"], out

    def test_for_loop_in_vm(self):
        """VM for-loop tidak boleh error (regresi stack fix)."""
        code = '''
buat total = 0
untuk i dalam range(1, 5) lakukan
    total = total + i
selesai
tulis total
'''
        out = self._run_vm(code)
        assert out == ["10"], out

    def test_while_loop_in_vm(self):
        code = '''
buat i = 0
selama i < 3 lakukan
    tulis i
    i = i + 1
selesai
'''
        out = self._run_vm(code)
        assert out == ["0", "1", "2"], out

    def test_function_in_vm(self):
        code = '''
fungsi kali2(x)
    kembali x * 2
selesai
tulis kali2(5)
'''
        out = self._run_vm(code)
        assert out == ["10"], out

    def test_vm_pipeline_raises_clear_error(self):
        """Pipeline di VM harus error jelas, bukan silent wrong result."""
        from brolang.vm.compiler import Compiler
        code = '''
buat hasil = 5 |> lalu(x) x * 2
'''
        ast = Parser(Lexer(code).tokenize()).parse()
        with pytest.raises(NotImplementedError, match="Pipeline"):
            Compiler().compile(ast)

    def test_vm_destructuring_raises_clear_error(self):
        """Destructuring di VM harus error jelas, bukan silent no-op."""
        from brolang.vm.compiler import Compiler
        code = '''
buat [a, b] = [1, 2]
'''
        ast = Parser(Lexer(code).tokenize()).parse()
        with pytest.raises(NotImplementedError, match="Destructuring"):
            Compiler().compile(ast)


# ============= Regression: Konsistensi Interpreter vs Transpiler =============


class TestOutputConsistencyV52:
    """Interpreter dan transpiler harus memberi hasil yang sama untuk fitur v5.2."""

    def _run_both(self, code):
        interp_out = run_code(code)
        ast = Parser(Lexer(code).tokenize()).parse()
        from brolang.vm.transpiler import Transpiler
        py_code = Transpiler().transpile(ast)
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with redirect_stdout(buf):
            exec(compile(py_code, "<test>", "exec"), {"__builtins__": __builtins__})
        transp_out = buf.getvalue().strip().splitlines()
        assert interp_out == transp_out, f"interp={interp_out} transp={transp_out}"

    def test_object_destructuring_missing_key_consistent(self):
        """Kunci objek yang hilang harus None di interpreter DAN transpiler."""
        code = '''
buat {x, y} = {"x": 1}
tulis x, y
'''
        self._run_both(code)

    def test_kwargs_with_defaults_consistent(self):
        code = '''
fungsi sapa(nama, umur=0)
    kembali "Halo " + nama + " umur " + teks(umur)
selesai
tulis sapa(nama="Ani")
'''
        self._run_both(code)

    def test_pipeline_consistent(self):
        code = '''
fungsi kali2(x)
    kembali x * 2
selesai
tulis 21 |> kali2
'''
        self._run_both(code)


# ============= Regression: Semantic Analyzer v5.2 =============


class TestSemanticV52:
    """Cek semantik tambahan untuk fitur v5.2."""

    def test_default_param_order_rejected(self):
        """Parameter non-default tidak boleh setelah parameter ber-default."""
        from brolang.semantic import SemanticAnalyzer
        code = '''
fungsi f(a=1, b)
    kembali a + b
selesai
'''
        ast = Parser(Lexer(code).tokenize()).parse()
        analyzer = SemanticAnalyzer()
        assert analyzer.analyze(ast) is False
        assert any("default" in str(e).lower() for e in analyzer.errors)

    def test_kwargs_value_undefined_variable_caught(self):
        """Nilai kwargs yang merujuk variabel tak dikenal harus terdeteksi analyzer."""
        from brolang.semantic import SemanticAnalyzer
        code = '''
fungsi f(a)
    kembali a
selesai
f(a=belum_ada)
'''
        ast = Parser(Lexer(code).tokenize()).parse()
        analyzer = SemanticAnalyzer()
        assert analyzer.analyze(ast) is False
        assert any("belum_ada" in str(e) for e in analyzer.errors)
