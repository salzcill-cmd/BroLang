"""
Unit tests: modul stdlib baru v6.2 — angka, sistem, sistem_operasi, web,
dan database (dijanjikan docs/STDLIB.md tapi sebelumnya belum ada).

Mencakup:
- angka         : pi/e (konstanta), sqr, abs, min, max, dan fungsi lain
- sistem        : versi, platform, nama, prosesor, python, cwd, home
- sistem_operasi: list_dir, buat/hapus/pindah/salin file & folder, jalur
- web           : get/post HTTP + objek respon (teks, status, json, sukses)
- database      : SQLite — eksekusi_sql, query, query_satu, tabel, kolom
"""

import json
import os
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from brolang.interpreter import Interpreter
from brolang.lexer import Lexer
from brolang.parser import Parser
from brolang.stdlib import get_stdlib_module


def _mod(nama):
    return get_stdlib_module(nama)


def _jalankan(kode):
    """Jalankan kode BroLang lewat interpreter dan kembalikan output."""
    ast = Parser(Lexer(kode).tokenize()).parse()
    interp = Interpreter()
    interp.interpret(ast)
    return interp.output


# ============================================================
# angka
# ============================================================


class TestAngka:
    def setup_method(self):
        self.angka = _mod("angka")

    def test_konstanta_pi_dan_e(self):
        assert abs(self.angka.pi - 3.14159) < 0.001
        assert abs(self.angka.e - 2.71828) < 0.001

    def test_sqr(self):
        assert self.angka.sqr(16) == 4.0
        assert self.angka.sqr(9) == 3.0

    def test_abs(self):
        assert self.angka.abs(-5) == 5
        assert self.angka.abs(7) == 7

    def test_min_max(self):
        assert self.angka.min(3, 7) == 3
        assert self.angka.max(3, 7) == 7
        assert self.angka.min([5, 2, 9]) == 2
        assert self.angka.max([5, 2, 9]) == 9

    def test_fungsi_lain(self):
        assert self.angka.lantai(3.7) == 3
        assert self.angka.langit(3.2) == 4
        assert self.angka.bulat(3.14159, 2) == pytest.approx(3.14)
        assert self.angka.pangkat(2, 3) == 8
        assert self.angka.faktorial(5) == 120
        assert self.angka.akar(25) == 5.0

    def test_min_max_dari_brolang(self):
        out = _jalankan("""
impor angka
tulis angka.pi
tulis angka.sqr(16)
tulis angka.abs(-5)
tulis angka.min(3, 7)
tulis angka.max(3, 7)
""")
        assert out == ["3.141592653589793", "4.0", "5", "3", "7"]


# ============================================================
# sistem
# ============================================================


class TestSistem:
    def setup_method(self):
        self.sistem = _mod("sistem")

    def test_versi(self):
        from brolang import __version__

        assert self.sistem.versi() == __version__

    def test_platform(self):
        import platform

        assert self.sistem.platform() == platform.system().lower()

    def test_nama(self):
        import platform

        assert self.sistem.nama() == platform.system()

    def test_prosesor(self):
        import platform

        assert self.sistem.prosesor() == platform.machine()

    def test_python(self):
        import platform

        assert self.sistem.python() == platform.python_version()

    def test_cwd_dan_home(self):
        assert os.path.isdir(self.sistem.cwd())
        assert os.path.isdir(self.sistem.home())

    def test_hostname_dan_lingkungan(self):
        assert isinstance(self.sistem.hostname(), str)
        assert self.sistem.lingkungan() == "development"

    def test_dari_brolang(self):
        out = _jalankan("""
impor sistem
tulis sistem.versi()
tulis sistem.platform()
""")
        import platform

        from brolang import __version__

        assert out == [__version__, platform.system().lower()]


# ============================================================
# sistem_operasi
# ============================================================


class TestSistemOperasi:
    def setup_method(self):
        self.so = _mod("sistem_operasi")

    def test_list_dir(self):
        daftar = self.so.list_dir(".")
        assert isinstance(daftar, list)
        assert len(daftar) > 0
        assert ".git" in daftar or "README.md" in daftar or "brolang" in daftar

    def test_buat_hapus_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "tes.txt")
            with open(path, "w") as f:
                f.write("halo")
            assert self.so.ada(path)
            assert self.so.adalah_file(path)
            assert self.so.hapus_file(path) is True
            assert not self.so.ada(path)
            assert self.so.hapus_file(path) is False  # sudah tidak ada

    def test_buat_folder_dan_isinya(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = os.path.join(tmp, "sub")
            self.so.buat_folder(folder)
            assert self.so.adalah_folder(folder)
            assert "sub" in self.so.list_dir(tmp)  # nama relatif
            # hapus folder
            assert self.so.hapus_folder(folder) is True
            assert not self.so.ada(folder)

    def test_pindah_dan_salin(self):
        with tempfile.TemporaryDirectory() as tmp:
            a = os.path.join(tmp, "a.txt")
            b = os.path.join(tmp, "b.txt")
            with open(a, "w") as f:
                f.write("konten")
            self.so.salin(a, b)
            assert os.path.exists(b)
            tujuan = os.path.join(tmp, "gerak.txt")
            self.so.pindah(a, tujuan)
            assert not os.path.exists(a)
            assert os.path.exists(tujuan)

    def test_ekstensi_dan_jalur(self):
        assert self.so.ekstensi("dokumen.md") == ".md"
        assert self.so.nama_dasar("/a/b/c.txt") == "c.txt"
        assert self.so.nama_tanpa_ekstensi("dokumen.md") == "dokumen"
        assert self.so.folder_induk("/a/b/c.txt") == "/a/b"
        assert self.so.gabung_jalur("x", "y", "z.txt") == os.path.join("x", "y", "z.txt")
        assert self.so.ubah_ekstensi("a.txt", ".md") == "a.md"
        assert self.so.ubah_ekstensi("a.txt", "md") == "a.md"
        assert os.path.isabs(self.so.jalur_absolut("apa"))
        assert self.so.jalur_nyata(".") == os.path.realpath(".")

    def test_daftar_file_vs_folder(self):
        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, "f1.txt"), "w") as f:
                f.write("1")
            os.makedirs(os.path.join(tmp, "dir1"))
            assert self.so.daftar_file(tmp) == ["f1.txt"]
            assert self.so.daftar_folder(tmp) == ["dir1"]

    def test_ukuran_dan_dari_brolang(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "s.txt")
            with open(path, "w") as f:
                f.write("12345")
            assert self.so.ukuran(path) == 5
        out = _jalankan("""
impor sistem_operasi
tulis sistem_operasi.ekstensi("a.txt")
tulis sistem_operasi.nama_tanpa_ekstensi("dokumen.md")
""")
        assert out == [".txt", "dokumen"]


# ============================================================
# web
# ============================================================


class _Handler(BaseHTTPRequestHandler):
    """Server HTTP mini untuk test web."""

    def do_GET(self):
        body = json.dumps({"pesan": "halo", "angka": 42}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        panjang = int(self.headers.get("Content-Length", 0))
        data = self.rfile.read(panjang).decode("utf-8")
        body = json.dumps({"diterima": data}).encode()
        self.send_response(201)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_DELETE(self):
        self.send_response(204)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def log_message(self, *args):
        pass


class TestWeb:
    @classmethod
    def setup_class(cls):
        cls.server = HTTPServer(("127.0.0.1", 0), _Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.server.server_address[1]}"

    @classmethod
    def teardown_class(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def setup_method(self):
        self.web = _mod("web")

    def test_get(self):
        r = self.web.get(f"{self.base}/data")
        assert r.status == 200
        assert r.sukses is True
        assert r.json == {"pesan": "halo", "angka": 42}
        assert '"pesan"' in r.teks
        assert r.error is None

    def test_post(self):
        r = self.web.post(f"{self.base}/kirim", json={"nama": "Budi"})
        assert r.status == 201
        assert r.sukses is True
        assert r.json == {"diterima": '{"nama": "Budi"}'}

    def test_post_form_data(self):
        r = self.web.post(f"{self.base}/form", data={"a": "1"})
        assert r.status == 201

    def test_delete(self):
        r = self.web.hapus_http(f"{self.base}/hapus")
        assert r.status == 204

    def test_kirim_bebas(self):
        r = self.web.kirim("GET", f"{self.base}/x")
        assert r.status == 200

    def test_error_koneksi(self):
        r = self.web.get("http://127.0.0.1:1/tidak-ada", timeout=2)
        assert r.sukses is False
        assert r.status == 0
        assert r.error is not None

    def test_get_dari_brolang(self):
        out = _jalankan(f"""
impor web
buat r = web.get("{self.base}/data")
tulis r.status
tulis r.json["pesan"]
""")
        assert out == ["200", "halo"]


# ============================================================
# database
# ============================================================


class TestDatabase:
    def setup_method(self):
        self.db = _mod("database")

    def test_buat_tabel_dan_insert(self):
        d = self.db.buka()
        d.eksekusi_sql("CREATE TABLE IF NOT EXISTS t (id INTEGER, nama TEXT)")
        d.eksekusi_sql("INSERT INTO t (id, nama) VALUES (?, ?)", 1, "Budi")
        d.eksekusi_sql("INSERT INTO t (id, nama) VALUES (?, ?)", 2, "Ani")
        assert d.jumlah_baris("t") == 2
        d.tutup()

    def test_query_mengembalikan_objek(self):
        d = self.db.buka()
        d.eksekusi_sql("CREATE TABLE IF NOT EXISTS t (id INTEGER, nama TEXT)")
        d.eksekusi_sql("INSERT INTO t (id, nama) VALUES (?, ?)", 7, "Citra")
        baris = d.query("SELECT * FROM t")
        assert baris == [{"id": 7, "nama": "Citra"}]
        d.tutup()

    def test_query_satu_dan_query_nilai(self):
        d = self.db.buka()
        d.eksekusi_sql("CREATE TABLE IF NOT EXISTS t (id INTEGER, nama TEXT)")
        d.eksekusi_sql("INSERT INTO t (id, nama) VALUES (?, ?)", 1, "Budi")
        assert d.query_satu("SELECT * FROM t")["nama"] == "Budi"
        assert d.query_nilai("SELECT nama FROM t") == "Budi"
        assert d.query_satu("SELECT * FROM t WHERE id = 99") is None
        d.tutup()

    def test_tabel_dan_kolom(self):
        d = self.db.buka()
        d.eksekusi_sql("CREATE TABLE IF NOT EXISTS pengguna (id INTEGER, nama TEXT, umur INTEGER)")
        assert "pengguna" in d.tabel()
        assert d.kolom("pengguna") == ["id", "nama", "umur"]
        d.tutup()

    def test_nama_tabel_tidak_valid_ditahan(self):
        """Nama tabel jahat tidak boleh diinterpolasi ke SQL (anti-injection)."""
        d = self.db.buka()
        d.eksekusi_sql("CREATE TABLE IF NOT EXISTS aman (id INTEGER)")
        assert d.jumlah_baris("aman") == 0
        # Nama jahat → tidak crash / tidak mengeksekusi, kembalikan 0 atau []
        assert d.jumlah_baris("aman; DROP TABLE aman") == 0
        assert d.kolom("aman; DROP TABLE aman") == []
        # Pastikan tabel masih utuh setelah percobaan
        assert "aman" in d.tabel()
        d.tutup()

    def test_buka_memori_dan_file(self):
        d = self.db.buka_memori()
        assert d.tersambung()
        d.tutup()
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "data.db")
            d2 = self.db.buka(path)
            d2.eksekusi_sql("CREATE TABLE IF NOT EXISTS t (id INTEGER)")
            d2.tutup()
            assert os.path.exists(path)
            assert os.path.getsize(path) > 0

    def test_eksekusi_banyak(self):
        d = self.db.buka()
        d.eksekusi_sql("CREATE TABLE IF NOT EXISTS t (id INTEGER, nama TEXT)")
        d.eksekusi_banyak("INSERT INTO t (id, nama) VALUES (?, ?)", [(1, "a"), (2, "b"), (3, "c")])
        assert d.jumlah_baris("t") == 3
        d.tutup()

    def test_dari_brolang(self):
        out = _jalankan("""
impor database
buat db = database.buka()
db.eksekusi_sql("CREATE TABLE IF NOT EXISTS t (id INTEGER, nama TEXT)")
db.eksekusi_sql("INSERT INTO t (id, nama) VALUES (?, ?)", 1, "Budi")
buat baris = db.query("SELECT * FROM t")
tulis baris[0]["nama"]
tulis db.jumlah_baris("t")
db.tutup()
""")
        assert out == ["Budi", "1"]
