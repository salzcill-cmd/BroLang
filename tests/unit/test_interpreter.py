"""
Unit tests untuk Interpreter BroLang.

Test coverage:
- Variable assignment dan akses
- Aritmatika (+, -, *, /, %, **)
- Perbandingan (==, !=, >, <, >=, <=)
- Logika (dan, atau, bukan)
- If-else
- While loop
- For loop
- Function definition dan call
- Return
- Class instantiation dan method
- List dan indexing
- Print
- Error handling runtime
"""

import pytest
from brolang.lexer import Lexer
from brolang.parser import Parser
from brolang.interpreter import Interpreter
from brolang.exceptions import (
    RuntimeError_, NameError_, ZeroDivisionError_,
)


def run(source: str):
    """Helper untuk menjalankan kode BroLang."""
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    interpreter = Interpreter()
    result = interpreter.interpret(ast)
    return result, interpreter.output


class TestInterpreterVariable:
    """Test variable operations."""

    def test_assign_and_access(self):
        run('buat nama = "Budi"')
        _, output = run('buat nama = "Budi"\ntulis nama')
        assert "Budi" in output

    def test_number_variable(self):
        _, output = run("buat x = 42\ntulis x")
        assert "42" in output


class TestInterpreterArithmetic:
    """Test arithmetic operations."""

    def test_addition(self):
        _, output = run("tulis 2 + 3")
        assert "5" in output

    def test_subtraction(self):
        _, output = run("tulis 10 - 3")
        assert "7" in output

    def test_multiplication(self):
        _, output = run("tulis 4 * 3")
        assert "12" in output

    def test_division(self):
        _, output = run("tulis 10 / 2")
        assert "5.0" in output or "5" in output

    def test_modulo(self):
        _, output = run("tulis 7 % 3")
        assert "1" in output

    def test_power(self):
        _, output = run("tulis 2 ** 3")
        assert "8" in output

    def test_complex_expression(self):
        _, output = run("tulis 2 + 3 * 4")
        assert "14" in output


class TestInterpreterComparison:
    """Test comparison operations."""

    def test_equal(self):
        _, output = run("tulis 5 == 5")
        assert "True" in output or "benar" in output

    def test_not_equal(self):
        _, output = run("tulis 5 != 3")
        assert "True" in output or "benar" in output

    def test_greater_than(self):
        _, output = run("tulis 5 > 3")
        assert "True" in output or "benar" in output

    def test_less_than(self):
        _, output = run("tulis 3 < 5")
        assert "True" in output or "benar" in output


class TestInterpreterLogical:
    """Test logical operations."""

    def test_and(self):
        _, output = run("tulis benar dan benar")
        assert "True" in output or "benar" in output

    def test_or(self):
        _, output = run("tulis salah atau benar")
        assert "True" in output or "benar" in output

    def test_not(self):
        _, output = run("tulis bukan benar")
        assert "False" in output or "salah" in output


class TestInterpreterIf:
    """Test if statements."""

    def test_if_true(self):
        source = """
buat x = 5
jika x > 0 maka
    tulis "positif"
selesai
"""
        _, output = run(source)
        assert "positif" in output

    def test_if_else(self):
        source = """
buat x = -1
jika x > 0 maka
    tulis "positif"
lainnya
    tulis "negatif"
selesai
"""
        _, output = run(source)
        assert "negatif" in output

    def test_if_elif_else(self):
        source = """
buat x = 0
jika x > 0 maka
    tulis "positif"
lainnya jika x < 0 maka
    tulis "negatif"
lainnya
    tulis "nol"
selesai
"""
        _, output = run(source)
        assert "nol" in output


class TestInterpreterLoop:
    """Test loops."""

    def test_while_loop(self):
        source = """
buat i = 1
selama i <= 3 lakukan
    tulis i
    i = i + 1
selesai
"""
        _, output = run(source)
        assert len(output) == 3
        assert "1" in output
        assert "2" in output
        assert "3" in output

    def test_for_range(self):
        source = """
untuk i dalam range(1, 4) lakukan
    tulis i
selesai
"""
        _, output = run(source)
        assert len(output) == 3
        assert "1" in output
        assert "2" in output
        assert "3" in output


class TestInterpreterFunction:
    """Test functions."""

    def test_function_call(self):
        source = """
fungsi sapa()
    tulis "Halo"
selesai
sapa()
"""
        _, output = run(source)
        assert "Halo" in output

    def test_function_with_params(self):
        source = """
fungsi tambah(a, b)
    kembali a + b
selesai
tulis tambah(3, 4)
"""
        _, output = run(source)
        assert "7" in output

    def test_function_return_string(self):
        source = """
fungsi sapa(nama)
    kembali "Halo " + nama
selesai
tulis sapa("Budi")
"""
        _, output = run(source)
        assert "Halo Budi" in output


class TestInterpreterClass:
    """Test classes."""

    def test_class_instantiation(self):
        source = """
kelas Mobil
    fungsi __init__(merk)
        buat self.merk = merk
    selesai
    fungsi info()
        kembali self.merk
    selesai
selesai
buat m = Mobil("Toyota")
tulis m.info()
"""
        _, output = run(source)
        assert "Toyota" in output


class TestInterpreterList:
    """Test list operations."""

    def test_list_literal(self):
        _, output = run("tulis [1, 2, 3]")
        assert "[1, 2, 3]" in output or "1" in output

    def test_list_index(self):
        source = """
buat data = [10, 20, 30]
tulis data[1]
"""
        _, output = run(source)
        assert "20" in output


class TestInterpreterErrors:
    """Test runtime errors."""

    def test_undefined_variable(self):
        with pytest.raises(NameError_):
            run("tulis x")

    def test_zero_division(self):
        with pytest.raises(ZeroDivisionError_):
            run("tulis 1 / 0")
