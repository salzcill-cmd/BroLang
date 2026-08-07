"""
Unit tests: Ramah Pemula (v6.1)
===============================

Menguji fitur yang membuat BroLang mudah dipelajari pelajar Indonesia:
- Mode belajar `bro belajar` (cek jawaban + integritas kurikulum)
- Saran keyword Inggris → Indonesia (print → tulis, dst.)
- Hint kesalahan umum pemula ('=' vs '==', titik koma ';')
- REPL: blok multi-baris, tampilan hasil ekspresi (=>)
"""

import io
import contextlib
from unittest import mock

import pytest

from brolang.lexer import Lexer
from brolang.parser import Parser
from brolang.interpreter import Interpreter
from brolang.exceptions import ParserError, LexerError
from brolang.suggestions import saran_keyword, BAHASA_INGGRIS
from brolang.belajar import cek_jawaban, BAB, TOTAL_POIN
from brolang.repl.repl import delta_kedalaman


def _jalankan(kode):
    ast = Parser(Lexer(kode).tokenize()).parse()
    interp = Interpreter()
    interp.interpret(ast)
    return interp.output


# ============= Mode Belajar: Pemeriksa Jawaban =============

class TestCekJawaban:
    def test_jawaban_benar(self):
        soal = BAB[0]["soal"][0]  # tulis "Halo Dunia!"
        status, detail = cek_jawaban('tulis "Halo Dunia!"', soal)
        assert status == "benar"
        assert detail == ["Halo Dunia!"]

    def test_jawaban_salah_output(self):
        soal = BAB[0]["soal"][0]
        status, detail = cek_jawaban('tulis "Halo"', soal)
        assert status == "salah"
        assert "Halo Dunia" in str(detail)

    def test_error_sintaks(self):
        soal = BAB[0]["soal"][0]
        status, detail = cek_jawaban('tulis "Halo', soal)
        assert status == "error"

    def test_error_runtime(self):
        soal = BAB[0]["soal"][0]
        status, detail = cek_jawaban('tulis x + 1', soal)
        assert status == "error"

    def test_cek_mengandung(self):
        # Soal bab 1 nomor 2: mengandung "Halo, saya"
        soal = BAB[0]["soal"][1]
        status, _ = cek_jawaban('tulis "Halo, saya Ani!"', soal)
        assert status == "benar"
        status, _ = cek_jawaban('tulis "Halo, kamu!"', soal)
        assert status == "salah"

    def test_kode_multi_baris(self):
        soal = BAB[3]["soal"][1]  # jika/ lainnya LULUS
        kode = 'buat nilai = 80\njika nilai >= 75 maka\n    tulis "LULUS"\nlainnya\n    tulis "TIDAK LULUS"\nselesai'
        status, _ = cek_jawaban(kode, soal)
        assert status == "benar"

    def test_timeout_perulangan_tak_berujung(self):
        """Kode yang terlalu lama berjalan harus dihentikan (bukan hang)."""
        soal = BAB[0]["soal"][0]
        # waktu.tidur(30) — thread tidur (tidak membakar CPU), tapi
        # melewati batas waktu 0.5 detik yang dipasang di test.
        kode = "impor waktu\nwaktu.tidur(30)"
        status, detail = cek_jawaban(kode, soal, timeout=0.5)
        assert status == "error"
        assert "terlalu lama" in detail
        assert "perulangan" in detail

    def test_kode_cepat_tidak_kana_timeout(self):
        """Kode normal selesai sebelum batas waktu."""
        soal = BAB[0]["soal"][0]
        status, _ = cek_jawaban('tulis "Halo Dunia!"', soal, timeout=0.5)
        assert status == "benar"

    def test_stdout_tidak_bocor_setelah_timeout(self):
        """Regresi: redirect_stdout tidak boleh merembes — output di luar
        cek_jawaban (UI belajar) harus tetap terlihat setelah timeout."""
        soal = BAB[0]["soal"][0]
        status, _ = cek_jawaban("impor waktu\nwaktu.tidur(30)", soal, timeout=0.3)
        assert status == "error"
        # print() di main thread setelah timeout harus sampai ke stdout asli
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            print("UI MASIH TERLIHAT")
        assert "UI MASIH TERLIHAT" in out.getvalue()


class TestKurikulum:
    def test_semua_solusi_benar(self):
        """Integritas kurikulum: setiap solusi emas harus lolos cek-nya sendiri."""
        for bab in BAB:
            for soal in bab["soal"]:
                status, detail = cek_jawaban(soal["solusi"], soal)
                assert status == "benar", (
                    f"{bab['judul']} — {soal['teks']}\n{detail}")

    def test_struktur_kurikulum(self):
        assert len(BAB) == 8
        for bab in BAB:
            assert bab["judul"] and bab["materi"] and bab["soal"]
            for soal in bab["soal"]:
                assert soal["teks"] and soal["petunjuk"] and soal["solusi"]
                assert soal["poin"] > 0
                assert soal["cek"] in ("tepat", "mengandung")
        assert TOTAL_POIN > 0

    def test_materi_bertingkat(self):
        # Bab pertama harus soal paling sederhana (tulis string literal)
        assert BAB[0]["soal"][0]["harapan"] == ["Halo Dunia!"]


# ============= Saran Keyword Inggris → Indonesia =============

class TestSaranKeyword:
    def test_pemetaan_lengkap(self):
        # Keyword inti yang sering dipakai pemula harus punya padanan
        for kata in ("print", "let", "if", "else", "for", "while",
                     "def", "class", "return", "import", "true", "false",
                     "null", "and", "or", "not", "try", "except", "in"):
            assert kata in BAHASA_INGGRIS, f"'{kata}' belum dipetakan"

    def test_saran_tidak_ada(self):
        assert saran_keyword("") == ""
        assert saran_keyword("variabel_biasa") == ""
        assert saran_keyword(123) == ""

    def test_interpreter_saran_print(self):
        # print("halo") → "Fungsi 'print' tidak ditemukan. Mungkin maksudmu 'tulis'?"
        ast = Parser(Lexer('print("halo")').tokenize()).parse()
        interp = Interpreter()
        with pytest.raises(Exception) as exc:
            interp.interpret(ast)
        assert "maksudmu 'tulis'" in str(exc.value)

    def test_interpreter_saran_null(self):
        ast = Parser(Lexer("buat x = null").tokenize()).parse()
        interp = Interpreter()
        with pytest.raises(Exception) as exc:
            interp.interpret(ast)
        assert "kosong" in str(exc.value)

    def test_analyzer_saran_fungsi(self):
        from brolang.semantic import SemanticAnalyzer
        ast = Parser(Lexer('print("halo")').tokenize()).parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(ast)
        assert any("maksudmu 'tulis'" in str(e) for e in analyzer.errors)

    def test_parser_saran_def(self):
        # def tidak dikenali sebagai keyword → saran 'fungsi'
        from brolang.semantic import SemanticAnalyzer
        ast = Parser(Lexer("def sapa()").tokenize()).parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(ast)
        assert any("maksudmu 'fungsi'" in str(e) for e in analyzer.errors)


# ============= Hint Kesalahan Umum =============

class TestHintPemula:
    def test_hint_satu_sama_dengan(self):
        # `jika x = 5 maka` → saran pakai '=='
        with pytest.raises(ParserError) as exc:
            Parser(Lexer("jika x = 5 maka").tokenize()).parse()
        assert "==" in str(exc.value)

    def test_hint_while_sama_dengan(self):
        with pytest.raises(ParserError) as exc:
            Parser(Lexer("selama x = 5 lakukan").tokenize()).parse()
        assert "==" in str(exc.value)

    def test_kondisi_eq_tidak_kana_hint(self):
        # `jika x == 5 maka` adalah perbandingan sah (TOKEN_EQ) —
        # tidak boleh kena hint '=' yang berbasis TOKEN_ASSIGN.
        ast = Parser(Lexer(
            "jika x == 5 maka\n    tulis \"lima\"\nselesai").tokenize()).parse()
        assert ast is not None

    def test_kondisi_perbandingan_lain_tidak_kana_hint(self):
        # !=, >=, <= di kondisi juga sah dan tidak boleh kena hint '='
        for kondisi in ("x != 5", "x >= 5", "x <= 5", "x > 5"):
            ast = Parser(Lexer(
                f"jika {kondisi} maka\n    tulis 1\nselesai").tokenize()).parse()
            assert ast is not None

    def test_hint_titik_koma(self):
        with pytest.raises(LexerError) as exc:
            Lexer('tulis "halo";').tokenize()
        assert "titik koma" in str(exc.value)

    def test_titik_koma_bukan_error_hanya_solusi(self):
        # Pesan error tetap jelas, tapi solusinya ramah
        with pytest.raises(LexerError) as exc:
            Lexer('tulis 1;').tokenize()
        assert "Karakter" in str(exc.value)


# ============= REPL =============

def _jalankan_repl(baris_input):
    """Jalankan loop REPL dengan input palsu, kembalikan output stdout."""
    from brolang.repl.repl import BroLangREPL
    repl = BroLangREPL()
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        with mock.patch("builtins.input", side_effect=baris_input + ["keluar"]):
            repl._run_loop()
    return out.getvalue()


class TestREPLPemula:
    def test_delta_kedalaman(self):
        assert delta_kedalaman("tulis 1") == 0
        assert delta_kedalaman("jika x maka") == 1
        assert delta_kedalaman("untuk i dalam range(3) lakukan") == 1
        assert delta_kedalaman("selesai") == -1
        assert delta_kedalaman("fungsi kali2(x)") == 1

    def test_delta_kedalaman_anti_false_positive(self):
        """Nama variabel yang diawali kata kunci blok tidak membuka blok."""
        assert delta_kedalaman("fungsiku = 5") == 0
        assert delta_kedalaman("kelasku = 5") == 0
        assert delta_kedalaman("coba2 = 1") == 0
        assert delta_kedalaman("cocokkanan = 3") == 0
        assert delta_kedalaman("tulis \"maka\"") == 0
        assert delta_kedalaman("tulis \"lakukan\"") == 0
        assert delta_kedalaman("# fungsi contoh") == 0

    def test_delta_kedalaman_komentar_akhir_baris(self):
        """`selesai`/`maka` dengan komentar di belakang tetap terhitung."""
        assert delta_kedalaman("selesai # tutup blok") == -1
        assert delta_kedalaman("jika x maka # kondisi") == 1
        assert delta_kedalaman("fungsi a() # definisi") == 1

    def test_delta_kedalaman_kurung_kurawal(self):
        """Blok kurung kurawal (cocokkan/enum/struktur/literal objek)."""
        assert delta_kedalaman("cocokkan x {") == 1
        assert delta_kedalaman("enum Warna {") == 1
        assert delta_kedalaman("struktur Titik {") == 1
        assert delta_kedalaman("antarmuka Bentuk {") == 1
        assert delta_kedalaman("abstrak kelas K {") == 1
        assert delta_kedalaman("buat obj = {") == 1
        assert delta_kedalaman("}") == -1
        # Satu baris utuh tidak mengubah kedalaman
        assert delta_kedalaman('cocokkan x { 1: tulis "satu", _: tulis "lain" }') == 0
        assert delta_kedalaman('buat obj = {"a": 1}') == 0

    def test_blok_kurung_kurawal_multiline_repl(self):
        """cocokkan ... { ... } ditutup otomatis oleh '}' di REPL."""
        out = _jalankan_repl([
            "cocokkan 2 {",
            "    1: tulis \"satu\"",
            "    2: tulis \"dua\"",
            "    _: tulis \"lain\"",
            "}",
        ])
        assert "dua" in out

    def test_multiline_dibatalkan_saat_keluar(self):
        """Ketik 'keluar' di tengah blok multi-baris membatalkan blok."""
        out = _jalankan_repl([
            "jika 5 > 3 maka",
            '    tulis "besar"',
            "batal",
            "2 + 2",
        ])
        assert "blok dibatalkan" in out
        assert "=> 4" in out  # REPL kembali normal setelah batal

    def test_variabel_fungsiku_tidak_membuka_multiline(self):
        """Regresi: `fungsiku = 5` dulu memicu mode multiline di REPL."""
        out = _jalankan_repl(["buat fungsiku = 5", "fungsiku + 3"])
        assert "=> 8" in out

    def test_kelasku_tidak_membuka_multiline(self):
        """Regresi: variabel berawalan 'kelas' tidak memicu mode multiline."""
        out = _jalankan_repl(["buat kelasku = 2", "kelasku ** 3"])
        assert "=> 8" in out

    def test_ekspresi_menampilkan_hasil(self):
        out = _jalankan_repl(["2 + 3"])
        assert "=> 5" in out

    def test_tulis_langsung(self):
        out = _jalankan_repl(['tulis "halo"'])
        assert "halo" in out
        assert "=>" not in out

    def test_assignment_tidak_menampilkan_panah(self):
        out = _jalankan_repl(["buat x = 5"])
        assert "=> 5" not in out

    def test_state_bertahan(self):
        # Variabel dari input sebelumnya tetap dikenali
        out = _jalankan_repl(["buat x = 7", "x * 6"])
        assert "=> 42" in out

    def test_blok_multiline(self):
        out = _jalankan_repl([
            "jika 5 > 3 maka",
            '    tulis "besar"',
            "selesai",
        ])
        assert "besar" in out

    def test_fungsi_multiline(self):
        out = _jalankan_repl([
            "fungsi kali2(x)",
            "    kembali x * 2",
            "selesai",
            "tulis kali2(21)",
        ])
        assert "42" in out

    def test_error_variabel_tak_dikenal(self):
        out = _jalankan_repl(["x + 1"])
        assert "tidak ditemukan" in out
