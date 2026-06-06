"""
Integration tests untuk pipeline lengkap BroLang.

Test seluruh pipeline: Source → Lexer → Parser → Semantic → Optimizer → Interpreter
"""

import pytest
from brolang.lexer import Lexer
from brolang.parser import Parser
from brolang.semantic import SemanticAnalyzer
from brolang.optimizer import Optimizer
from brolang.interpreter import Interpreter
from brolang.compiler import Compiler


def run_full_pipeline(source: str):
    """Menjalankan pipeline lengkap BroLang."""
    lexer = Lexer(source)
    tokens = lexer.tokenize()

    parser = Parser(tokens)
    ast = parser.parse()

    analyzer = SemanticAnalyzer()
    assert analyzer.analyze(ast), f"Semantic errors: {[str(e) for e in analyzer.errors]}"

    optimizer = Optimizer()
    optimized_ast = optimizer.optimize(ast)

    interpreter = Interpreter()
    result = interpreter.interpret(optimized_ast)
    return result, interpreter.output


class TestFullPipeline:
    """Test pipeline lengkap dengan program nyata."""

    def test_hello_world(self):
        _, output = run_full_pipeline('tulis "Halo Dunia"')
        assert "Halo Dunia" in output

    def test_variable_and_arithmetic(self):
        source = """
buat a = 10
buat b = 20
buat c = a + b
tulis c
"""
        _, output = run_full_pipeline(source)
        assert "30" in output

    def test_conditional(self):
        source = """
buat nilai = 85
jika nilai >= 80 maka
    tulis "Lulus"
lainnya
    tulis "Tidak Lulus"
selesai
"""
        _, output = run_full_pipeline(source)
        assert "Lulus" in output

    def test_loop_and_function(self):
        source = """
fungsi kuadrat(x)
    kembali x * x
selesai

untuk i dalam range(1, 4) lakukan
    tulis kuadrat(i)
selesai
"""
        _, output = run_full_pipeline(source)
        assert len(output) == 3

    def test_complex_program(self):
        source = """
# Program kalkulator sederhana
fungsi tambah(a, b)
    kembali a + b
selesai

fungsi kurang(a, b)
    kembali a - b
selesai

fungsi kali(a, b)
    kembali a * b
selesai

buat x = 10
buat y = 5

tulis "Tambah:", tambah(x, y)
tulis "Kurang:", kurang(x, y)
tulis "Kali:", kali(x, y)
"""
        _, output = run_full_pipeline(source)
        assert "Tambah: 15" in output
        assert "Kurang: 5" in output
        assert "Kali: 50" in output

    def test_list_operations(self):
        source = """
buat buah = ["apel", "pisang", "jeruk"]
tulis buah[0]
tulis buah[2]
"""
        _, output = run_full_pipeline(source)
        assert "apel" in output
        assert "jeruk" in output

    def test_nested_if(self):
        source = """
buat x = 5
buat y = 10

jika x > 0 maka
    jika y > 5 maka
        tulis "Keduanya positif besar"
    selesai
lainnya
    tulis "x negatif"
selesai
"""
        _, output = run_full_pipeline(source)
        assert "Keduanya positif besar" in output

    def test_while_with_break(self):
        source = """
buat i = 0
selama benar lakukan
    i = i + 1
    jika i > 3 maka
        hentikan
    selesai
    tulis i
selesai
"""
        _, output = run_full_pipeline(source)
        assert "1" in output
        assert "2" in output
        assert "3" in output

    def test_fibonacci(self):
        source = """
fungsi fibonacci(n)
    jika n <= 1 maka
        kembali n
    lainnya
        kembali fibonacci(n - 1) + fibonacci(n - 2)
    selesai
selesai

tulis fibonacci(5)
"""
        _, output = run_full_pipeline(source)
        assert "5" in output


class TestCompilerIntegration:
    """Test compiler menghasilkan Python yang benar."""

    def test_compile_and_execute(self):
        source = 'tulis 2 + 3'
        compiler = Compiler(optimize=True)
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()

        py_code = compiler.compile(ast)
        namespace = {}
        exec(py_code, namespace)
        # Compiler should produce valid Python
