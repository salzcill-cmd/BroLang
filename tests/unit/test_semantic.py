"""
Unit tests untuk Semantic Analyzer BroLang.
"""

import pytest
from brolang.lexer import Lexer
from brolang.parser import Parser
from brolang.semantic import SemanticAnalyzer
from brolang.exceptions import SemanticError, ParserError


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


class TestSemanticTypeConsistency:
    """Test konsistensi tipe pada reassignment (v12.0 type inference)."""

    def test_reassign_sama_tipe(self):
        analyzer = analyze("buat x = 5\nx = 10")
        assert len(analyzer.errors) == 0

    def test_reassign_beda_tipe(self):
        analyzer = analyze('buat x = 5\nx = "teks"')
        assert len(analyzer.errors) > 0
        assert any("Tipe tidak cocok" in str(e) for e in analyzer.errors)

    def test_reassign_numerik_campuran(self):
        # Angka <-> Desimal diizinkan
        analyzer = analyze("buat x = 5\nx = 3.5")
        assert len(analyzer.errors) == 0

    def test_reassign_eksplisit_anotasi(self):
        analyzer = analyze("buat x: Angka = 5\nx = 10")
        assert len(analyzer.errors) == 0

    def test_reassign_beda_tipe_anotasi(self):
        analyzer = analyze("buat x: Angka = 5\nx = \"teks\"")
        assert len(analyzer.errors) > 0
        assert any("Tipe tidak cocok" in str(e) for e in analyzer.errors)

    def test_reassign_tipe_tak_dikenal(self):
        # Nilai dari pemanggilan fungsi user -> tipe tak dikenal, tidak error
        code = """fungsi ambil()
    kembali 1
selesai
buat x = 5
x = ambil()
"""
        analyzer = analyze(code)
        assert len(analyzer.errors) == 0


class TestSemanticOwnership:
    """Test kepemilikan tunggal `miliki` dengan move semantics (v12.1)."""

    def test_miliki_deklarasi(self):
        analyzer = analyze("miliki x = 5")
        assert len(analyzer.errors) == 0

    def test_pindah_milik(self):
        # `buat y = x` memindahkan milik dari x (miliki) ke y — tidak error
        analyzer = analyze("miliki x = 5\nbuat y = x")
        assert len(analyzer.errors) == 0

    def test_pakai_setelah_pindah(self):
        # Menggunakan x setelah dipindahkan = error
        analyzer = analyze("miliki x = 5\nbuat y = x\ntulis x")
        assert len(analyzer.errors) > 0
        assert any("sudah dipindahkan" in str(e) for e in analyzer.errors)

    def test_assign_ulang_miliki(self):
        # Variabel miliki bisa ditetapkan ulang (nilai lama di-drop)
        analyzer = analyze("miliki x = 5\nx = 10")
        assert len(analyzer.errors) == 0

    def test_non_miliki_bisa_dibaca_setelah_diassign(self):
        # Variabel biasa (bukan miliki) tetap bisa dibaca setelah dijadikan nilai lain
        analyzer = analyze("buat x = 5\nbuat y = x\ntulis x")
        assert len(analyzer.errors) == 0

    def test_miliki_dengan_destructuring_ditolak(self):
        with pytest.raises(ParserError):
            analyze("miliki [a, b] = [1, 2]")

    def test_miliki_deklarasi_ganda_ditolak(self):
        with pytest.raises(ParserError):
            analyze("miliki a, b = 1, 2")
