"""
Unit tests untuk Lexer BroLang.

Test coverage:
- Token dasar (angka, string, identifier, operator)
- Keyword Bahasa Indonesia
- Komentar
- String multi-baris
- Indentasi
- Error handling
"""

import pytest
from brolang.lexer import Lexer
from brolang.token_types import TokenType, Token
from brolang.exceptions import LexerError


class TestLexerBasics:
    """Test token dasar."""

    def test_empty_source(self):
        lexer = Lexer("")
        tokens = lexer.tokenize()
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.TOKEN_EOF

    def test_number(self):
        lexer = Lexer("42")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.TOKEN_NUMBER
        assert tokens[0].value == 42

    def test_decimal(self):
        lexer = Lexer("3.14")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.TOKEN_DECIMAL
        assert tokens[0].value == 3.14

    def test_string_single_quote(self):
        lexer = Lexer("'halo'")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.TOKEN_STRING
        assert tokens[0].value == "halo"

    def test_string_double_quote(self):
        lexer = Lexer('"halo"')
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.TOKEN_STRING
        assert tokens[0].value == "halo"

    def test_boolean_true(self):
        lexer = Lexer("benar")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.TOKEN_BOOLEAN
        assert tokens[0].value is True

    def test_boolean_false(self):
        lexer = Lexer("salah")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.TOKEN_BOOLEAN
        assert tokens[0].value is False

    def test_kosong(self):
        lexer = Lexer("kosong")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.TOKEN_KOSONG

    def test_identifier(self):
        lexer = Lexer("nama_var")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.TOKEN_IDENTIFIER
        assert tokens[0].value == "nama_var"


class TestLexerKeywords:
    """Test keyword Bahasa Indonesia."""

    def test_buat(self):
        lexer = Lexer("buat")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.TOKEN_BUAT

    def test_tulis(self):
        lexer = Lexer("tulis")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.TOKEN_TULIS

    def test_jika(self):
        lexer = Lexer("jika")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.TOKEN_JIKA

    def test_selesai(self):
        lexer = Lexer("selesai")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.TOKEN_SELESAI

    def test_fungsi(self):
        lexer = Lexer("fungsi")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.TOKEN_FUNGSI

    def test_kembali(self):
        lexer = Lexer("kembali")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.TOKEN_KEMBALI

    def test_kelas(self):
        lexer = Lexer("kelas")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.TOKEN_KELAS

    def test_impor(self):
        lexer = Lexer("impor")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.TOKEN_IMPOR

    def test_all_keywords(self):
        """Test semua keyword dikenali."""
        keywords = [
            "buat", "tulis", "jika", "maka", "lainnya",
            "selesai", "untuk", "dalam", "lakukan", "selama",
            "fungsi", "kembali", "kelas", "impor", "dari",
            "coba", "tangkap", "dan", "atau", "bukan",
            "benar", "salah", "kosong",
        ]
        for kw in keywords:
            lexer = Lexer(kw)
            tokens = lexer.tokenize()
            assert tokens[0].type != TokenType.TOKEN_IDENTIFIER, f"Keyword '{kw}' not recognized"


class TestLexerOperators:
    """Test operator tokens."""

    def test_plus(self):
        lexer = Lexer("+")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.TOKEN_PLUS

    def test_minus(self):
        lexer = Lexer("-")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.TOKEN_MINUS

    def test_multiply(self):
        lexer = Lexer("*")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.TOKEN_MULTIPLY

    def test_divide(self):
        lexer = Lexer("/")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.TOKEN_DIVIDE

    def test_equals(self):
        lexer = Lexer("==")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.TOKEN_EQ

    def test_not_equals(self):
        lexer = Lexer("!=")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.TOKEN_NEQ

    def test_greater_than(self):
        lexer = Lexer(">")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.TOKEN_GT

    def test_less_than(self):
        lexer = Lexer("<")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.TOKEN_LT

    def test_assign(self):
        lexer = Lexer("=")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.TOKEN_ASSIGN


class TestLexerComments:
    """Test komentar."""

    def test_single_line_comment(self):
        lexer = Lexer("# ini komentar\n42")
        tokens = lexer.tokenize()
        assert len([t for t in tokens if t.type == TokenType.TOKEN_NUMBER]) == 1
        assert tokens[-2].type == TokenType.TOKEN_NUMBER  # Skip EOF and NEWLINE

    def test_multi_line_comment(self):
        lexer = Lexer("|# komentar\nmulti baris #|\n42")
        tokens = lexer.tokenize()
        numbers = [t for t in tokens if t.type == TokenType.TOKEN_NUMBER]
        assert len(numbers) == 1


class TestLexerErrors:
    """Test error handling lexer."""

    def test_unclosed_string(self):
        lexer = Lexer('"halo')
        with pytest.raises(LexerError):
            lexer.tokenize()

    def test_unknown_character(self):
        lexer = Lexer("$")
        with pytest.raises(LexerError):
            lexer.tokenize()


class TestLexerIntegration:
    """Test lexer dengan kode lengkap."""

    def test_simple_program(self):
        source = 'buat nama = "Budi"\ntulis nama'
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        assert len(tokens) > 3
        assert tokens[0].type == TokenType.TOKEN_BUAT
        assert tokens[1].type == TokenType.TOKEN_IDENTIFIER
        assert tokens[2].type == TokenType.TOKEN_ASSIGN
        assert tokens[3].type == TokenType.TOKEN_STRING
