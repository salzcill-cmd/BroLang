"""
Output Consistency Tests: Transpiler vs Interpreter
===================================================

Memastikan transpiler dan interpreter menghasilkan output yang sama
untuk kode BroLang yang sama. Ini penting untuk menjaga kenyamanan user.

Kode yang diuji harus menghasilkan output identik melalui kedua mesin.
"""

import pytest
import io
import contextlib
from brolang.lexer import Lexer
from brolang.parser import Parser
from brolang.interpreter import Interpreter
from brolang.vm.transpiler import Transpiler
from brolang.vm.compiler import Compiler
from brolang.vm.vm import VM


def run_interpreter(code):
    """Jalankan kode melalui interpreter tree-walking."""
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    interp = Interpreter()
    interp.interpret(ast)
    return interp.output


def run_transpiler(code):
    """Jalankan kode melalui transpiler (AST → Python)."""
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    transpiler = Transpiler()
    py_code = transpiler.transpile(ast)
    exec_globals = {'__builtins__': __builtins__}
    stdout_capture = io.StringIO()
    with contextlib.redirect_stdout(stdout_capture):
        exec(py_code, exec_globals)
    output = stdout_capture.getvalue().strip().split('\n')
    return [line for line in output if line]


def run_vm(code):
    """Jalankan kode melalui bytecode VM."""
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    compiler = Compiler()
    bytecode = compiler.compile(ast)
    vm = VM()
    vm.run(bytecode)
    return vm.output


# ============= Test Cases =============

class TestBasicOutputConsistency:
    """Test output konsisten untuk fitur dasar."""

    def test_tulis_basic(self):
        code = 'tulis("Halo BroLang!")'
        interp = run_interpreter(code)
        trans = run_transpiler(code)
        assert interp == trans, f"Interpreter: {interp}, Transpiler: {trans}"

    def test_tulis_multiple(self):
        code = '''
tulis("Satu")
tulis("Dua")
tulis("Tiga")
'''
        interp = run_interpreter(code)
        trans = run_transpiler(code)
        assert interp == trans

    def test_variable_and_tulis(self):
        code = '''
buat nama = "Bro"
tulis("Halo " + nama + "!")
'''
        interp = run_interpreter(code)
        trans = run_transpiler(code)
        assert interp == trans

    def test_arithmetic(self):
        code = '''
buat x = 10
buat y = 20
tulis(x + y)
tulis(x * y)
tulis(x - y)
'''
        interp = run_interpreter(code)
        trans = run_transpiler(code)
        assert interp == trans

    def test_string_interpolation(self):
        code = '''
buat nama = "World"
tulis("Hello $nama!")
'''
        interp = run_interpreter(code)
        trans = run_transpiler(code)
        assert interp == trans


class TestControlFlowConsistency:
    """Test output konsisten untuk control flow."""

    def test_if_else(self):
        code = '''
buat x = 10
jika x > 5 maka
    tulis("Besar")
lainnya
    tulis("Kecil")
selesai
'''
        interp = run_interpreter(code)
        trans = run_transpiler(code)
        assert interp == trans

    def test_for_loop(self):
        code = '''
buat angka = [0, 1, 2, 3, 4]
untuk i dalam angka lakukan
    tulis(i)
selesai
'''
        interp = run_interpreter(code)
        trans = run_transpiler(code)
        assert interp == trans

    def test_while_loop(self):
        code = '''
buat i = 0
selama i < 3 lakukan
    tulis(i)
    i = i + 1
selesai
'''
        interp = run_interpreter(code)
        trans = run_transpiler(code)
        assert interp == trans

    def test_for_each(self):
        code = '''
buat fruits = ["apel", "mangga", "jeruk"]
untuk setiap buah dalam fruits lakukan
    tulis(buah)
selesai
'''
        interp = run_interpreter(code)
        trans = run_transpiler(code)
        assert interp == trans


class TestFunctionConsistency:
    """Test output konsisten untuk fungsi."""

    def test_simple_function(self):
        code = '''
fungsi sapa(nama)
    tulis("Halo " + nama + "!")
selesai
sapa("Bro")
'''
        interp = run_interpreter(code)
        trans = run_transpiler(code)
        assert interp == trans

    def test_function_with_return(self):
        code = '''
fungsi tambah(a, b)
    kembali a + b
selesai
tulis(tambah(3, 4))
'''
        interp = run_interpreter(code)
        trans = run_transpiler(code)
        assert interp == trans

    def test_recursive_function(self):
        code = '''
fungsi faktorial(n)
    jika n <= 1 maka
        kembali 1
    lainnya
        kembali n * faktorial(n - 1)
    selesai
selesai
tulis(faktorial(5))
'''
        interp = run_interpreter(code)
        trans = run_transpiler(code)
        assert interp == trans

    def test_lambda(self):
        code = '''
buat kali = lalu(x, y) x * y
tulis(kali(3, 4))
'''
        interp = run_interpreter(code)
        trans = run_transpiler(code)
        assert interp == trans


class TestClassConsistency:
    """Test output konsisten untuk kelas."""

    def test_simple_class(self):
        code = '''
kelas Counter
    fungsi __init__(self)
        self.n = 0
    selesai
    fungsi tambah(self, x)
        self.n = self.n + x
    selesai
    fungsi get(self)
        kembali self.n
    selesai
selesai
buat c = Counter()
c.tambah(42)
tulis(c.get())
'''
        interp = run_interpreter(code)
        trans = run_transpiler(code)
        assert interp == trans

    def test_inheritance(self):
        code = '''
kelas Hewan
    fungsi __init__(self, nama)
        self.nama = nama
    selesai
    fungsi suara(self)
        tulis("??")
    selesai
selesai
kelas Kucing : Hewan
    fungsi suara(self)
        tulis(self.nama + " bilang meong")
    selesai
selesai
buat k = Kucing("Kitty")
k.suara()
'''
        interp = run_interpreter(code)
        trans = run_transpiler(code)
        assert interp == trans

    def test_static_method(self):
        code = '''
kelas Math
    statis fungsi kali(a, b)
        kembali a * b
    selesai
selesai
tulis(Math.kali(3, 4))
'''
        interp = run_interpreter(code)
        trans = run_transpiler(code)
        assert interp == trans


class TestHigherOrderConsistency:
    """Test output konsisten untuk higher-order functions."""

    def test_map_function(self):
        code = '''
buat angka = [1, 2, 3, 4, 5]
buat hasil = peta(angka, lalu(x) x * 2)
tulis(hasil)
'''
        interp = run_interpreter(code)
        trans = run_transpiler(code)
        assert interp == trans

    def test_filter_function(self):
        code = '''
buat angka = [1, 2, 3, 4, 5, 6]
buat genap = saring(angka, lalu(x) x % 2 == 0)
tulis(genap)
'''
        interp = run_interpreter(code)
        trans = run_transpiler(code)
        assert interp == trans

    def test_reduce_function(self):
        code = '''
buat angka = [1, 2, 3, 4, 5]
buat total = kurangi(angka, lalu(a, b) a + b, 0)
tulis(total)
'''
        interp = run_interpreter(code)
        trans = run_transpiler(code)
        assert interp == trans


class TestNullCoalescingConsistency:
    """Test output konsisten untuk null coalescing."""

    def test_null_coalescing(self):
        code = '''
buat x = kosong
buat hasil = x ?? "default"
tulis(hasil)
'''
        interp = run_interpreter(code)
        trans = run_transpiler(code)
        assert interp == trans

    def test_null_coalescing_with_value(self):
        code = '''
buat x = 42
buat hasil = x ?? 0
tulis(hasil)
'''
        interp = run_interpreter(code)
        trans = run_transpiler(code)
        assert interp == trans


class TestStringMethodConsistency:
    """Test output konsisten untuk string methods."""

    def test_string_methods(self):
        code = '''
buat teks = "  Halo BroLang  "
tulis(teks.strip())
tulis(teks.strip().panjang())
'''
        interp = run_interpreter(code)
        trans = run_transpiler(code)
        assert interp == trans


class TestListMethodConsistency:
    """Test output konsisten untuk list methods."""

    def test_list_methods(self):
        code = '''
buat daftar = [3, 1, 4, 1, 5]
daftar.append(9)
tulis(daftar)
daftar.urutkan()
tulis(daftar)
'''
        interp = run_interpreter(code)
        trans = run_transpiler(code)
        assert interp == trans


class TestVMConsistency:
    """Test output konsisten untuk bytecode VM."""

    def test_vm_basic(self):
        code = '''
tulis("Hello from VM!")
buat x = 42
tulis(x)
'''
        interp = run_interpreter(code)
        vm = run_vm(code)
        assert interp == vm

    def test_vm_function(self):
        code = '''
fungsi sapa(nama)
    tulis("Halo " + nama)
selesai
sapa("VM")
'''
        interp = run_interpreter(code)
        vm = run_vm(code)
        assert interp == vm

    def test_vm_class(self):
        code = '''
kelas Counter
    fungsi __init__(self)
        self.n = 0
    selesai
    fungsi tambah(self, x)
        self.n = self.n + x
    selesai
    fungsi get(self)
        kembali self.n
    selesai
selesai
buat c = Counter()
c.tambah(10)
tulis(c.get())
'''
        interp = run_interpreter(code)
        vm = run_vm(code)
        assert interp == vm


class TestTranspilerRegresi:
    """Regresi transpiler: fitur yang dulu bikin `bro run` jatuh ke interpreter
    (output dobel). Semua harus konsisten interpreter vs transpiler."""

    def test_tipe_builtin(self):
        """tipe(nilai) harus jalan di kedua mesin dengan nama tipe BroLang."""
        code = '''
buat a = 42
buat b = 3.14
buat c = "halo"
tulis(tipe(a))
tulis(tipe(b))
tulis(tipe(c))
'''
        interp = run_interpreter(code)
        trans = run_transpiler(code)
        assert interp == trans
        assert interp == ["angka", "desimal", "teks"]

    def test_stdlib_import(self):
        """impor matematika harus jalan di transpiler (fallback stdlib)."""
        code = '''
impor matematika
tulis(matematika.akar(25))
'''
        interp = run_interpreter(code)
        trans = run_transpiler(code)
        assert interp == trans

    def test_stdlib_module_function(self):
        """teks.potong(...) = fungsi modul (split), bukan method string strip."""
        code = '''
impor teks
buat pesan = "Halo Dunia"
tulis(teks.potong(pesan, " "))
'''
        interp = run_interpreter(code)
        trans = run_transpiler(code)
        assert interp == trans
        assert trans == ["['Halo', 'Dunia']"]

    def test_comprehension_filter(self):
        """[x lalu x dalam data jika kondisi] konsisten di kedua mesin."""
        code = '''
buat data = [1, 2, 3, 4, 5, 6]
buat genap = [x lalu x dalam data jika x % 2 == 0]
tulis(genap)
'''
        interp = run_interpreter(code)
        trans = run_transpiler(code)
        assert interp == trans

    def test_try_catch(self):
        """coba/tangkap (MultiExceptNode) konsisten di kedua mesin."""
        code = '''
coba
    buat x = 10 / 0
tangkap error
    tulis("error ditangkap")
selesai
tulis("lanjut")
'''
        interp = run_interpreter(code)
        trans = run_transpiler(code)
        assert interp == trans
        assert trans == ["error ditangkap", "lanjut"]

    def test_string_method_potong_tetap_bekerja(self):
        """Method string .potong(...) = split tetap jalan di transpiler."""
        code = '''
buat pesan = "satu-dua-tiga"
tulis(pesan.potong("-"))
'''
        interp = run_interpreter(code)
        trans = run_transpiler(code)
        assert interp == trans


class TestEdgeCases:
    """Test edge cases yang sering bikin bug."""

    def test_nested_if(self):
        code = '''
buat x = 10
buat y = 20
jika x > 5 maka
    jika y > 15 maka
        tulis("Dua-duanya besar")
    lainnya
        tulis("X besar, Y kecil")
    selesai
lainnya
    tulis("X kecil")
selesai
'''
        interp = run_interpreter(code)
        trans = run_transpiler(code)
        assert interp == trans

    def test_nested_loop(self):
        code = '''
buat matrix = [[1, 2], [3, 4]]
untuk baris dalam matrix lakukan
    untuk item dalam baris lakukan
        tulis(item)
    selesai
selesai
'''
        interp = run_interpreter(code)
        trans = run_transpiler(code)
        assert interp == trans

    def test_function_in_loop(self):
        code = '''
fungsi kuadrat(x)
    kembali x * x
selesai
buat angka = [1, 2, 3, 4, 5]
untuk i dalam angka lakukan
    tulis(kuadrat(i))
selesai
'''
        interp = run_interpreter(code)
        trans = run_transpiler(code)
        assert interp == trans

    def test_chained_comparison(self):
        code = '''
buat x = 5
jika 0 < x < 10 maka
    tulis("Valid")
lainnya
    tulis("Invalid")
selesai
'''
        interp = run_interpreter(code)
        trans = run_transpiler(code)
        assert interp == trans

    def test_fstring(self):
        code = '''
buat nama = "Bro"
buat umur = 20
tulis(f"Halo {nama}, umur {umur} tahun")
'''
        interp = run_interpreter(code)
        trans = run_transpiler(code)
        assert interp == trans
