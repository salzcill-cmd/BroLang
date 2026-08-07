"""
Unit tests: BroLang v5.5 — Operator Overloading, Threading (sejajar), LSP.
"""

import io
import contextlib
import time

import pytest

from brolang.lexer import Lexer
from brolang.parser import Parser
from brolang.interpreter import Interpreter
from brolang.vm.transpiler import Transpiler
from brolang.stdlib import get_stdlib_module


def _mod(nama):
    return get_stdlib_module(nama)


def _jalankan(kode):
    """Jalankan kode BroLang lewat interpreter dan kembalikan output."""
    ast = Parser(Lexer(kode).tokenize()).parse()
    interp = Interpreter()
    interp.interpret(ast)
    return interp.output


def _transpile(kode):
    """Transpile kode BroLang → Python source."""
    ast = Parser(Lexer(kode).tokenize()).parse()
    return Transpiler().transpile(ast)


def _jalankan_transpiler(kode):
    """Jalankan kode via transpiler dan kembalikan output (seperti print)."""
    py = _transpile(kode)
    exec_globals = {"__builtins__": __builtins__}
    stdout_capture = io.StringIO()
    with contextlib.redirect_stdout(stdout_capture):
        exec(py, exec_globals)
    return [l for l in stdout_capture.getvalue().split("\n") if l]


# ============================================================
# Operator Overloading — Interpreter
# ============================================================

_KODE_TITIK = """
kelas Titik
    fungsi __init__(x, y)
        self.x = x
        self.y = y
    selesai
    fungsi _tambah_(lain)
        kembali Titik(self.x + lain.x, self.y + lain.y)
    selesai
    fungsi _kurang_(lain)
        kembali Titik(self.x - lain.x, self.y - lain.y)
    selesai
    fungsi _sama_(lain)
        kembali self.x == lain.x dan self.y == lain.y
    selesai
    fungsi _negasi_()
        kembali Titik(-self.x, -self.y)
    selesai
    fungsi _teks_()
        kembali "(" + teks(self.x) + ", " + teks(self.y) + ")"
    selesai
selesai
buat a = Titik(1, 2)
buat b = Titik(3, 4)
buat c = a + b
tulis c
buat d = b - a
tulis d
tulis a == Titik(1, 2)
tulis a != b
tulis -b
tulis a + Titik(100, 0)
"""


class TestOperatorOverloadInterpreter:
    def test_aritmatika_teks_perbandingan(self):
        out = _jalankan(_KODE_TITIK)
        assert out == [
            "(4, 6)",      # a + b
            "(2, 2)",      # b - a
            "True",        # a == Titik(1, 2)
            "True",        # a != b (negasi _sama_)
            "(-3, -4)",    # -b (unary _negasi_)
            "(101, 2)",    # a + Titik(100, 0) — refleksi operan kiri tetap
        ]

    def test_transpiler_konsisten(self):
        assert _jalankan_transpiler(_KODE_TITIK) == _jalankan(_KODE_TITIK)

    def test_panjang_index_index_set(self):
        out = _jalankan("""
kelas DaftarKustom
    fungsi __init__()
        self.items = []
    selesai
    fungsi _panjang_()
        kembali panjang(self.items)
    selesai
    fungsi _index_(i)
        kembali self.items[i]
    selesai
    fungsi _index_set_(i, v)
        self.items[i] = v
    selesai
    fungsi _tambah_(v)
        self.items.tambah(v)
        kembali self
    selesai
selesai
buat d = DaftarKustom()
d = d + 10
d = d + 20
tulis panjang(d)
tulis d[0]
d[1] = 99
tulis d[1]
""")
        assert out == ["2", "10", "99"]

    def test_operator_dalam(self):
        out = _jalankan("""
kelas Kotak
    fungsi __init__(items)
        self.items = items
    selesai
    fungsi _dalam_(x)
        kembali x dalam self.items
    selesai
selesai
buat k = Kotak([1, 2, 3])
tulis 2 dalam k
tulis 9 dalam k
""")
        assert out == ["True", "False"]

    def test_operator_tanpa_overload_tetap_error_atau_default(self):
        # Kelas TANPA overload: penjumlahan harus error jelas
        code = """
kelas X
    fungsi __init__(v)
        self.v = v
    selesai
selesai
buat x = X(1)
buat y = x + x
"""
        with pytest.raises(Exception):
            _jalankan(code)


# ============================================================
# Modul Sejajar (Threading)
# ============================================================

class TestSejajar:
    def test_jalankan_fungsi_python(self):
        sejajar = _mod("sejajar")
        tugas = sejajar.jalankan(lambda: 42)
        assert tugas.hasil() == 42
        assert tugas.selesai() is True

    def test_jalankan_fungsi_brolang_dari_interpreter(self):
        out = _jalankan("""
impor sejajar
fungsi kali2(x)
    kembali x * 2
selesai
buat t = sejajar.jalankan(kali2, 21)
tulis t.hasil()
""")
        assert out == ["42"]

    def test_tunggu_dan_tunggu_semua(self):
        sejajar = _mod("sejajar")
        t1 = sejajar.jalankan(lambda: 1)
        t2 = sejajar.jalankan(lambda: 2)
        assert sejajar.tunggu(t1) == 1
        assert sejajar.tunggu_semua([t1, t2]) == [1, 2]

    def test_peta_sejajar(self):
        out = _jalankan("""
impor sejajar
fungsi kali2(x)
    kembali x * 2
selesai
tulis sejajar.peta_sejajar(kali2, [1, 2, 3, 4])
""")
        assert out == ["[2, 4, 6, 8]"]

    def test_benar_paralel_untuk_callable_python(self):
        """Callable Python murni harus jalan benar-benar paralel (tanpa lock)."""
        sejajar = _mod("sejajar")
        mulai = time.monotonic()

        def lambat():
            time.sleep(0.25)
            return "ok"

        # 3 tugas sleep 0.25s — paralel => total jauh di bawah 0.75s
        tugas = [sejajar.jalankan(lambat) for _ in range(3)]
        hasil = sejajar.tunggu_semua(tugas)
        durasi = time.monotonic() - mulai
        assert hasil == ["ok", "ok", "ok"]
        assert durasi < 0.7, f"tidak paralel? durasi={durasi:.2f}s"

    def test_atur_jumlah_thread(self):
        sejajar = _mod("sejajar")
        sejajar.atur_thread(8)
        assert sejajar.jumlah_thread() == 8
        sejajar.atur_thread(1)
        assert sejajar.jumlah_thread() == 1


# ============================================================
# LSP Upgrade — Completion / Definition / Hover
# ============================================================

class TestLSP:
    def _server(self, teks):
        from brolang.lsp.server import BroLangLSP
        server = BroLangLSP()
        server.documents["file:///x.bro"] = teks
        return server

    def test_completion_simbol_dokumen(self):
        server = self._server(
            "buat skor = 10\n"
            "fungsi main()\n"
            "    tulis skor\n"
            "selesai\n")
        res = server._handle_completion({
            "textDocument": {"uri": "file:///x.bro"},
            "position": {"line": 2, "character": 0},
        })
        labels = [i["label"] for i in res["items"]]
        assert "skor" in labels
        assert "main" in labels
        assert "fungsi" in labels  # keyword tetap muncul

    def test_completion_member_setelah_titik(self):
        server = self._server("impor teks\nteks.\n")
        res = server._handle_completion({
            "textDocument": {"uri": "file:///x.bro"},
            "position": {"line": 1, "character": 5},
        })
        labels = [i["label"] for i in res["items"]]
        assert labels  # ada member

    def test_definition_ke_deklarasi(self):
        server = self._server("buat skor = 10\nfungsi main()\n    tulis skor\nselesai\n")
        loc = server._handle_definition({
            "textDocument": {"uri": "file:///x.bro"},
            "position": {"line": 2, "character": 12},
        })
        assert loc is not None
        assert loc["range"]["start"]["line"] == 0  # deklarasi 'buat skor'

    def test_hover_simbol(self):
        server = self._server("buat skor = 10\n")
        h = server._handle_hover({
            "textDocument": {"uri": "file:///x.bro"},
            "position": {"line": 0, "character": 5},
        })
        assert h is not None
        assert "skor" in h["contents"]["value"]
        assert "Variable" in h["contents"]["value"]

    def test_hover_keyword(self):
        server = self._server("fungsi main()\n    pass\nselesai\n")
        h = server._handle_hover({
            "textDocument": {"uri": "file:///x.bro"},
            "position": {"line": 0, "character": 2},
        })
        assert h is not None
        assert "Keyword" in h["contents"]["value"]
