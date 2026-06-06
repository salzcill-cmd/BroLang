"""
Unit tests untuk Semantic Analyzer BroLang.
"""

import pytest
from brolang.lexer import Lexer
from brolang.parser import Parser
from brolang.semantic import SemanticAnalyzer
from brolang.exceptions import SemanticError


def analyze(source: str) -> SemanticAnalyzer:
    """Helper untuk menganalisis kode."""
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    return analyzer


class TestSemanticVariable:
    """Test variable analysis."""

    def test_undefined_variable(self):
        analyzer = analyze("tulis x")
        assert len(analyzer.errors) > 0
        assert any("belum didefinisikan" in str(e) for e in analyzer.errors)

    def test_defined_variable(self):
        analyzer = analyze('buat x = 5\ntulis x')
        assert len(analyzer.errors) == 0


class TestSemanticDuplicate:
    """Test duplicate declaration detection."""

    def test_duplicate_variable(self):
        analyzer = analyze("buat x = 1\nbuat x = 2")
        assert len(analyzer.errors) > 0


class TestSemanticFunction:
    """Test function analysis."""

    def test_undefined_function(self):
        analyzer = analyze("halo()")
        assert len(analyzer.errors) > 0

    def test_defined_function(self):
        code = """
fungsi halo()
    tulis "Hai"
selesai
halo()
"""
        analyzer = analyze(code)
        assert len(analyzer.errors) == 0
