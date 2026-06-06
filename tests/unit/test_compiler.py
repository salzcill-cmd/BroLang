"""
Unit tests untuk Compiler BroLang.
"""

import pytest
from brolang.lexer import Lexer
from brolang.parser import Parser
from brolang.compiler import Compiler


def compile_source(source: str) -> str:
    """Helper untuk mengompilasi kode BroLang."""
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    compiler = Compiler(optimize=True)
    return compiler.compile(ast)


class TestCompilerOutput:
    """Test Python output dari compiler."""

    def test_compile_print(self):
        result = compile_source('tulis "Halo"')
        assert "print(" in result
        assert "Halo" in result

    def test_compile_assignment(self):
        result = compile_source('buat x = 5')
        assert "x = 5" in result

    def test_compile_if(self):
        source = """
jika x > 0 maka
    tulis x
selesai
"""
        result = compile_source(source)
        assert "if" in result

    def test_compile_while(self):
        source = """
selama x < 10 lakukan
    x = x + 1
selesai
"""
        result = compile_source(source)
        assert "while" in result

    def test_compile_for(self):
        source = """
untuk i dalam range(5) lakukan
    tulis i
selesai
"""
        result = compile_source(source)
        assert "for" in result

    def test_compile_function(self):
        source = """
fungsi tambah(a, b)
    kembali a + b
selesai
"""
        result = compile_source(source)
        assert "def tambah" in result
        assert "return" in result

    def test_compile_class(self):
        source = """
kelas Mobil
    fungsi __init__(merk)
        buat self.merk = merk
    selesai
selesai
"""
        result = compile_source(source)
        assert "class Mobil" in result

    def test_compile_executable(self):
        """Test bahwa hasil kompilasi bisa dieksekusi."""
        source = 'tulis 2 + 3'
        py_source = compile_source(source)
        namespace = {}
        exec(py_source, namespace)
        # Should not raise
