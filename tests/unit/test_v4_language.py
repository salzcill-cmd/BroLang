"""Unit tests untuk fitur bahasa BroLang v4.0.

Mencakup:
- Match/Case (cocokkan)
- Enum
- Struct (struktur)
- Lambda (lalu)
- List Comprehension
- Generators (hasilkan)
- Decorators (@)
- Async/Await
- Context Manager (dengan/sebagai)
- Typed Exceptions (kecuali tipe)
- Star import
- String methods baru
"""

import pytest  # noqa: F401
from brolang.lexer import Lexer
from brolang.parser import Parser
from brolang.interpreter import Interpreter
from brolang.ast.nodes import (
    MatchNode, EnumNode, StructNode, LambdaNode,
    ComprehensionNode,
    YieldNode, AsyncFunctionDefNode,
    WithNode, MultiExceptNode,
    DecoratedFunctionNode,
    StarImportNode, FunctionNode, ReturnNode, AssignmentNode,
)


def run_brolang(source: str) -> Interpreter:
    """Helper: run BroLang source code."""
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    interp = Interpreter()
    interp.interpret(ast)
    return interp


# ============= Match/Case =============
class TestMatchCase:
    def test_match_basic(self):
        interp = run_brolang("""
buat x = 2
cocokkan x {
    1: tulis "satu"
    2: tulis "dua"
    _: tulis "lainnya"
}
        """)
        assert interp.output[0] == "dua"

    def test_match_string(self):
        interp = run_brolang("""
buat warna = "merah"
cocokkan warna {
    "merah": tulis "api"
    "biru": tulis "air"
    _: tulis "lainnya"
}
        """)
        assert interp.output[0] == "api"

    def test_match_default(self):
        interp = run_brolang("""
buat x = 99
cocokkan x {
    1: tulis "satu"
    _: tulis "default"
}
        """)
        assert interp.output[0] == "default"

    def test_match_parser(self):
        source = """
buat n = 3
cocokkan n {
    1: tulis "one"
    2: tulis "two"
    _: tulis "other"
}
        """
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        found = False
        for stmt in ast.statements:
            if isinstance(stmt, MatchNode):
                found = True
                break
        assert found


# ============= Enum =============
class TestEnum:
    def test_enum_parser(self):
        source = """
enum Warna {
    MERAH, BIRU, HIJAU
}
        """
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        found = False
        for stmt in ast.statements:
            if isinstance(stmt, EnumNode):
                found = True
                assert stmt.name == "Warna"
                assert len(stmt.members) == 3
                break
        assert found


# ============= Struct =============
class TestStruct:
    def test_struct_parser(self):
        source = """
struktur Posisi {
    x, y
}
        """
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        found = False
        for stmt in ast.statements:
            if isinstance(stmt, StructNode):
                found = True
                assert stmt.name == "Posisi"
                assert len(stmt.fields) == 2
                break
        assert found


# ============= Lambda =============
class TestLambda:
    def test_lambda_parser(self):
        source = "buat kuadrat = lalu(x) x * x"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        found = False
        for stmt in ast.statements:
            if isinstance(stmt, AssignmentNode):
                if isinstance(stmt.value, LambdaNode):
                    found = True
                    break
        assert found

    def test_lambda_exec(self):
        interp = run_brolang("""
buat kuadrat = lalu(x) x * x
tulis kuadrat(5)
        """)
        assert interp.output[0] == "25"


# ============= Comprehensions =============
class TestComprehensions:
    def test_list_comprehension_parser(self):
        source = "buat hasil = [x * 2 lalu x dalam [1, 2, 3]]"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        found = False
        for stmt in ast.statements:
            if isinstance(stmt, AssignmentNode):
                if isinstance(stmt.value, ComprehensionNode):
                    found = True
                    break
        assert found


# ============= Generators =============
class TestGenerators:
    def test_yield_parser(self):
        source = """
fungsi counter(n)
    hasilkan 1
    hasilkan 2
selesai
        """
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        found = False
        for stmt in ast.statements:
            if isinstance(stmt, FunctionNode):
                for child in stmt.body:
                    if isinstance(child, YieldNode):
                        found = True
                        break
        assert found


# ============= Decorators =============
class TestDecorators:
    def test_decorator_parser(self):
        source = """
@dekoratorku
fungsi sapa()
    tulis "hai"
selesai
        """
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        found = False
        for stmt in ast.statements:
            if isinstance(stmt, DecoratedFunctionNode):
                found = True
                assert len(stmt.decorators) == 1
                break
        assert found


# ============= Async/Await =============
class TestAsyncAwait:
    def test_async_function_parser(self):
        source = """
asinkron fungsi ambil_data(url)
    tulis "Mengambil data dari " + url
    kembali "data"
selesai
        """
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        found = False
        for stmt in ast.statements:
            if isinstance(stmt, AsyncFunctionDefNode):
                found = True
                assert stmt.name == "ambil_data"
                break
        assert found

    def test_async_tokens(self):
        source = "asinkron fungsi tes() tunggu"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        token_types = [t.type.name for t in tokens]
        assert "TOKEN_ASYNKRON" in token_types
        assert "TOKEN_TUNGGU" in token_types


# ============= Context Manager =============
class TestContextManager:
    def test_with_parser(self):
        source = """
dengan buka_file("test.txt") sebagai f
    tulis f
selesai
        """
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        found = False
        for stmt in ast.statements:
            if isinstance(stmt, WithNode):
                found = True
                assert stmt.as_name == "f"
                break
        assert found


# ============= Typed Exceptions =============
class TestTypedExceptions:
    def test_typed_except_parser(self):
        source = """
coba
    tulis 10 / 0
kecuali ZeroDivisionError sebagai err
    tulis "Error"
selesai
        """
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        found = False
        for stmt in ast.statements:
            if isinstance(stmt, MultiExceptNode):
                found = True
                assert len(stmt.except_clauses) == 1
                clause = stmt.except_clauses[0]
                assert clause.exception_type == "ZeroDivisionError"
                assert clause.variable == "err"
                break
        assert found

    def test_multi_except_parser(self):
        source = """
coba
    buat x = 5 / 0
kecuali ZeroDivisionError sebagai err
    tulis "bagi nol"
kecuali TypeError sebagai err
    tulis "tipe salah"
kecuali lainnya
    tulis "error"
selesai
        """
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        found = False
        for stmt in ast.statements:
            if isinstance(stmt, MultiExceptNode):
                found = True
                assert len(stmt.except_clauses) == 3
                break
        assert found

    def test_try_except_exec(self):
        interp = run_brolang("""
coba
    tulis 10 / 0
kecuali ZeroDivisionError sebagai err
    tulis "tertangkap"
selesai
        """)
        assert interp.output[0] == "tertangkap"


# ============= Star Import =============
class TestStarImport:
    def test_star_import_parser(self):
        source = "dari math impor *"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        found = False
        for stmt in ast.statements:
            if isinstance(stmt, StarImportNode):
                found = True
                assert stmt.module == "math"
                break
        assert found


# ============= Multi-Return =============
class TestMultiReturn:
    def test_multi_return_parser(self):
        source = """
fungsi swap(a, b)
    kembali (b, a)
selesai
        """
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        found = False
        for stmt in ast.statements:
            if isinstance(stmt, FunctionNode):
                for child in stmt.body:
                    if isinstance(child, ReturnNode):
                        found = True
                        break
        assert found


# ============= Walrus Operator =============
class TestWalrusOperator:
    def test_walrus_token(self):
        source = 'buat x := 5'
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        token_types = [t.type.name for t in tokens]
        assert "TOKEN_WALRUS" in token_types


# ============= F-strings =============
class TestFstrings:
    def test_fstring_in_lexer(self):
        source = 'tulis f"nama adalah {nama}"'
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        assert len(tokens) > 0
        found_fstring = any(
            t.type.name == "TOKEN_FSTRING" for t in tokens
        )
        assert found_fstring


# ============= String Methods =============
class TestStringMethods:
    def test_string_cocok(self):
        interp = run_brolang("""
buat teks = "Hello World"
tulis teks.cocok("World")
            """)
        assert interp.output[0] == "True"

    def test_string_ganti(self):
        interp = run_brolang("""
buat teks = "Hello World"
tulis teks.ganti("World", "BroLang")
            """)
        assert interp.output[0] == "Hello BroLang"

    def test_string_potong(self):
        interp = run_brolang("""
buat teks = "a,b,c"
buat hasil = teks.potong(",")
tulis panjang(hasil)
            """)
        assert interp.output[0] == "3"

    def test_string_join(self):
        interp = run_brolang("""
buat daftar = ["a", "b", "c"]
tulis ", ".join(daftar)
            """)
        assert interp.output[0] == "a, b, c"

    def test_string_strip(self):
        interp = run_brolang("""
buat teks = "  halo  "
tulis teks.strip()
            """)
        assert interp.output[0] == "halo"

    def test_string_mulai(self):
        interp = run_brolang("""
buat teks = "Hello World"
tulis teks.mulai("Hello")
            """)
        assert interp.output[0] == "True"

    def test_string_isdigit(self):
        interp = run_brolang("""
buat teks = "12345"
tulis teks.isdigit()
            """)
        assert interp.output[0] == "True"

    def test_string_len_method(self):
        interp = run_brolang("""
buat teks = "Hello"
tulis teks.panjang()
            """)
        assert interp.output[0] == "5"

    def test_string_atas(self):
        interp = run_brolang("""
buat teks = "hello"
tulis teks.atas()
            """)
        assert interp.output[0] == "HELLO"

    def test_string_bawah(self):
        interp = run_brolang("""
buat teks = "HELLO"
tulis teks.bawah()
            """)
        assert interp.output[0] == "hello"
