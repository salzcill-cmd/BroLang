"""
Unit tests untuk Parser BroLang.

Test coverage:
- Assignment
- Expression (aritmatika, perbandingan, logika)
- If-else dengan elif
- Loop (for, while)
- Function definition dan return
- Class definition
- Import
- Try-catch
- Error handling
"""

import pytest
from brolang.lexer import Lexer
from brolang.parser import Parser
from brolang.ast.nodes import (
    ProgramNode, NumberNode, StringNode, BooleanNode,
    AssignmentNode, BinaryOpNode, UnaryOpNode,
    IfNode, WhileNode, ForNode,
    FunctionNode, ReturnNode, CallNode,
    ClassNode, ImportNode, TryNode,
    PrintNode, ListNode, ObjectNode,
    MultiExceptNode, TypedExceptNode,
)
from brolang.exceptions import ParserError


def parse(source: str):
    """Helper untuk mem-parse kode BroLang."""
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    return parser.parse()


class TestParserAssignment:
    """Test assignment."""

    def test_simple_assignment(self):
        ast = parse('buat nama = "Budi"')
        assert len(ast.statements) == 1
        stmt = ast.statements[0]
        assert isinstance(stmt, AssignmentNode)
        assert stmt.target.name == "nama"
        assert isinstance(stmt.value, StringNode)
        assert stmt.value.value == "Budi"

    def test_number_assignment(self):
        ast = parse("buat x = 42")
        stmt = ast.statements[0]
        assert isinstance(stmt.value, NumberNode)
        assert stmt.value.value == 42


class TestParserExpression:
    """Test expression parsing."""

    def test_binary_op(self):
        ast = parse("1 + 2")
        stmt = ast.statements[0]
        assert isinstance(stmt, BinaryOpNode)
        assert stmt.operator == "+"

    def test_complex_expression(self):
        ast = parse("1 + 2 * 3")
        stmt = ast.statements[0]
        assert isinstance(stmt, BinaryOpNode)

    def test_comparison(self):
        ast = parse("x == 5")
        stmt = ast.statements[0]
        assert isinstance(stmt, BinaryOpNode)
        assert stmt.operator == "=="


class TestParserIf:
    """Test if statement."""

    def test_simple_if(self):
        source = """
jika x > 0 maka
    tulis "positif"
selesai
"""
        ast = parse(source)
        assert len(ast.statements) > 0
        found_if = False
        for stmt in ast.statements:
            if isinstance(stmt, IfNode):
                found_if = True
                assert len(stmt.body) > 0
                break
        assert found_if

    def test_if_else(self):
        source = """
jika x > 0 maka
    tulis "positif"
lainnya
    tulis "negatif"
selesai
"""
        ast = parse(source)
        found_if = False
        for stmt in ast.statements:
            if isinstance(stmt, IfNode):
                found_if = True
                assert len(stmt.else_body) > 0
                break
        assert found_if

    def test_if_elif_else(self):
        source = """
jika x > 0 maka
    tulis "positif"
lainnya jika x < 0 maka
    tulis "negatif"
lainnya
    tulis "nol"
selesai
"""
        ast = parse(source)
        found_if = False
        for stmt in ast.statements:
            if isinstance(stmt, IfNode):
                found_if = True
                assert len(stmt.elif_conditions) > 0
                assert len(stmt.else_body) > 0
                break
        assert found_if


class TestParserLoop:
    """Test loop statements."""

    def test_while_loop(self):
        source = """
selama x < 10 lakukan
    tulis x
    x = x + 1
selesai
"""
        ast = parse(source)
        found_while = False
        for stmt in ast.statements:
            if isinstance(stmt, WhileNode):
                found_while = True
                assert len(stmt.body) > 0
                break
        assert found_while

    def test_for_loop(self):
        source = """
untuk i dalam range(5) lakukan
    tulis i
selesai
"""
        ast = parse(source)
        found_for = False
        for stmt in ast.statements:
            if isinstance(stmt, ForNode):
                found_for = True
                assert stmt.variable == "i"
                assert len(stmt.body) > 0
                break
        assert found_for


class TestParserFunction:
    """Test function definition."""

    def test_function_no_params(self):
        source = """
fungsi halo()
    tulis "Halo"
selesai
"""
        ast = parse(source)
        found_func = False
        for stmt in ast.statements:
            if isinstance(stmt, FunctionNode):
                found_func = True
                assert stmt.name == "halo"
                assert len(stmt.params) == 0
                break
        assert found_func

    def test_function_with_params(self):
        source = """
fungsi tambah(a, b)
    kembali a + b
selesai
"""
        ast = parse(source)
        found_func = False
        for stmt in ast.statements:
            if isinstance(stmt, FunctionNode):
                found_func = True
                assert stmt.name == "tambah"
                assert len(stmt.params) == 2
                assert len(stmt.body) > 0
                break
        assert found_func

    def test_function_return(self):
        source = """
fungsi sapa(nama)
    kembali "Halo " + nama
selesai
"""
        ast = parse(source)
        found_func = False
        for stmt in ast.statements:
            if isinstance(stmt, FunctionNode):
                found_func = True
                has_return = any(isinstance(s, ReturnNode) for s in stmt.body)
                assert has_return
                break
        assert found_func


class TestParserClass:
    """Test class definition."""

    def test_simple_class(self):
        source = """
kelas Mobil
    fungsi __init__(merk)
        buat self.merk = merk
    selesai
selesai
"""
        ast = parse(source)
        found_class = False
        for stmt in ast.statements:
            if isinstance(stmt, ClassNode):
                found_class = True
                assert stmt.name == "Mobil"
                assert len(stmt.methods) > 0
                break
        assert found_class


class TestParserImport:
    """Test import statement."""

    def test_import(self):
        source = "impor matematika"
        ast = parse(source)
        assert len(ast.statements) > 0
        assert isinstance(ast.statements[0], ImportNode)
        assert ast.statements[0].module == "matematika"


class TestParserTryCatch:
    """Test try-catch."""

    def test_try_catch(self):
        source = """
coba
    buat x = 1 / 0
tangkap error
    tulis error
selesai
"""
        ast = parse(source)
        found_try = False
        for stmt in ast.statements:
            if isinstance(stmt, (TryNode, MultiExceptNode)):
                found_try = True
                assert len(stmt.body) > 0
                break
        assert found_try


class TestParserPrint:
    """Test print statement."""

    def test_print_string(self):
        source = 'tulis "Halo"'
        ast = parse(source)
        assert len(ast.statements) > 0
        assert isinstance(ast.statements[0], PrintNode)

    def test_print_multiple(self):
        source = 'tulis "Nama:", nama'
        ast = parse(source)
        assert isinstance(ast.statements[0], PrintNode)


class TestParserList:
    """Test list literal."""

    def test_list(self):
        source = "[1, 2, 3]"
        ast = parse(source)
        assert len(ast.statements) > 0
        assert isinstance(ast.statements[0], ListNode)
        assert len(ast.statements[0].elements) == 3


class TestParserErrors:
    """Test parser error handling."""

    def test_missing_maka(self):
        source = "jika x > 0\n    tulis x\nselesai"
        with pytest.raises(ParserError):
            parse(source)

    def test_missing_selesai(self):
        source = "jika x > 0 maka\n    tulis x"
        with pytest.raises(ParserError):
            parse(source)

    def test_invalid_syntax(self):
        source = "buat = 5"
        with pytest.raises(ParserError):
            parse(source)
