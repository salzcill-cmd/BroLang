"""
Regression tests: ekspresi multi-baris (bracket-aware lexer).

Bug lama: kondisi `jika (...)` yang ditulis di beberapa baris gagal dengan
"Indentasi tidak konsisten" karena lexer memperlakukan indentasi baris
lanjutan sebagai blok baru. Sekarang lexer bracket-aware.
"""

import os

import pytest

from brolang.lexer import Lexer
from brolang.parser import Parser
from brolang.interpreter import Interpreter
from brolang.token_types import TokenType


def _lex(code):
    return Lexer(code).tokenize()


def _parse(code):
    return Parser(Lexer(code).tokenize()).parse()


def _run(code):
    interp = Interpreter()
    interp.interpret(_parse(code))
    return interp.output


class TestLexerBracketAware:
    """Lexer tidak boleh mengeluarkan INDENT/DEDENT/NEWLINE di dalam bracket."""

    def test_no_indent_error_multi_line_parens(self):
        code = (
            "buat x = 5\n"
            "jika (x > 0 dan\n"
            "      x < 10 dan\n"
            "      x != 7) maka\n"
            "    tulis \"ok\"\n"
            "selesai\n"
        )
        tokens = _lex(code)  # tidak boleh raise LexerError
        types = [t.type for t in tokens]
        # Tidak ada INDENT/DEDENT/NEWLINE di antara 'dan' baris lanjutan
        assert TokenType.TOKEN_NEWLINE not in types[5:12]

    def test_multi_line_call(self):
        code = (
            "tulis tambah(1,\n"
            "          2)\n"
        )
        tokens = _lex(code)  # tidak boleh error indentasi
        # Cek tidak ada NEWLINE di antara '(' dan ')'
        types = [t.type for t in tokens]
        idx_paren = types.index(TokenType.TOKEN_LPAREN)
        idx_rparen = types.index(TokenType.TOKEN_RPAREN)
        assert TokenType.TOKEN_NEWLINE not in types[idx_paren:idx_rparen]

    def test_multi_line_list(self):
        code = (
            "buat data = [1,\n"
            "             2,\n"
            "             3]\n"
            "tulis data\n"
        )
        _lex(code)  # tidak boleh error indentasi


class TestParserMultiLine:
    """Parser menerima ekspresi multi-baris."""

    def test_multi_line_if_condition(self):
        code = (
            "buat x = 5\n"
            "jika (x > 0 dan\n"
            "      x < 10) maka\n"
            "    tulis \"dalam range\"\n"
            "selesai\n"
        )
        ast = _parse(code)
        assert ast is not None

    def test_multi_line_call_args(self):
        code = (
            "fungsi tambah(a, b)\n"
            "    kembali a + b\n"
            "selesai\n"
            "tulis tambah(10,\n"
            "             20)\n"
        )
        ast = _parse(code)
        assert ast is not None

    def test_multi_line_list_literal(self):
        code = (
            "buat angka = [1,\n"
            "              2,\n"
            "              3]\n"
            "tulis panjang(angka)\n"
        )
        ast = _parse(code)
        assert ast is not None


class TestInterpreterMultiLine:
    """Interpreter mengeksekusi ekspresi multi-baris dengan benar."""

    def test_multi_line_if_output(self):
        out = _run(
            "buat x = 7\n"
            "jika (x > 0 dan\n"
            "      x < 10 dan\n"
            "      x != 5) maka\n"
            "    tulis \"lolos\"\n"
            "lainnya\n"
            "    tulis \"gagal\"\n"
            "selesai\n"
        )
        assert out == ["lolos"]

    def test_multi_line_call_output(self):
        out = _run(
            "fungsi tambah(a, b)\n"
            "    kembali a + b\n"
            "selesai\n"
            "tulis tambah(10,\n"
            "             20)\n"
        )
        assert out == ["30"]

    def test_multi_line_list_output(self):
        out = _run(
            "buat angka = [1,\n"
            "              2,\n"
            "              3]\n"
            "tulis panjang(angka)\n"
        )
        assert out == ["3"]


class TestGameExamples:
    """Contoh game harus lolos lexer + parser (window-nya butuh pygame)."""

    @pytest.mark.parametrize("nama", ["game_pong.bro", "game_paddle.bro"])
    def test_lex_dan_parse(self, nama):
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__)))), "examples", nama)
        source = open(path, encoding="utf-8").read()
        _parse(source)  # lexer + parser tanpa error

    def test_interpret_sampai_game_loop(self):
        """Semua kode contoh (fungsi + setup) terinterpretasi tanpa error.

        Bagian sebelum `game.mulai()` dijalankan penuh; loop game sendiri
        sengaja tidak dijalankan karena memblokir selamanya (butuh window).
        """
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__)))), "examples", "game_paddle.bro")
        source = open(path, encoding="utf-8").read()
        before_loop = source.split("game.mulai()")[0]
        interp = Interpreter()
        interp.interpret(_parse(before_loop))  # tidak boleh raise apa pun


class TestRegresiParser:
    """Regresi: fitur yang dipakai contoh tapi dulu gagal parse."""

    def test_tipe_sebagai_fungsi(self):
        """tipe(nilai) harus parse + jalan (tipe = builtin, bukan type alias)."""
        out = _run('buat x = 42\ntulis tipe(x)\ntulis tipe("halo")')
        assert out == ["angka", "teks"]

    def test_comprehension_dengan_filter_jika(self):
        """[x lalu x dalam data jika kondisi] — 'jika' = filter, bukan ternary."""
        out = _run('buat data = [1, 2, 3, 4, 5, 6]\n'
                   'buat genap = [x lalu x dalam data jika x % 2 == 0]\n'
                   'tulis genap')
        assert out == ["[2, 4, 6]"]

    def test_ternary_tetap_bekerja(self):
        """Ternary biasa tidak rusak oleh fix comprehension."""
        out = _run('buat status = "besar" jika 10 > 5 lainnya "kecil"\ntulis status')
        assert out == ["besar"]

    def test_ternary_dalam_iterable_comprehension(self):
        """Ternary ber-kurung dalam iterable comprehension tetap valid:
        [x lalu x dalam (a jika b lainnya c)]."""
        out = _run('buat hasil = [x lalu x dalam ([1, 2] jika benar lainnya [9])]\n'
                   'tulis hasil')
        assert out == ["[1, 2]"]


def _analyze(code):
    from brolang.semantic import SemanticAnalyzer
    analyzer = SemanticAnalyzer()
    ok = analyzer.analyze(_parse(code))
    return ok, analyzer.errors


class TestRegresiAnalyzer:
    """Regresi: MultiExceptNode harus dikenal semantic analyzer."""

    def test_catch_variable_dikenal_analyzer(self):
        """`tangkap error` mendefinisikan variabel `error` untuk analisis."""
        ok, errors = _analyze(
            "coba\n"
            "    buat x = 10 / 0\n"
            "tangkap error\n"
            "    tulis error\n"
            "selesai\n"
        )
        assert ok, [str(e) for e in errors]

    def test_kecuali_typed_dikenal_analyzer(self):
        """`kecuali TipeError sebagai e` juga mendefinisikan variabelnya."""
        ok, errors = _analyze(
            "coba\n"
            "    buat x = 10 / 0\n"
            "kecuali ZeroDivisionError sebagai e\n"
            "    tulis e\n"
            "selesai\n"
        )
        assert ok, [str(e) for e in errors]
