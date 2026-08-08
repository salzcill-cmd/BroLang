"""
Test BroLang v6.3 — Performance boost, Tooling proyek modern, Web framework
===========================================================================

Mencakup:
1. Peephole optimizer di bytecode VM (constant folding, NOP removal, jump remap)
2. Method cache VM (inheritance chain)
3. Fix: binding param method class di VM (slot self)
4. Fix lexer: string multi-baris & f-string multi-baris
5. Tooling: bro init (scaffolding) & bro run tanpa argumen (baca brolang.json)
6. Modul web_server (routing, parameter dinamis, query, JSON body)
"""

import json
import os
import subprocess
import sys
import tempfile
import urllib.request

import pytest

from brolang.lexer import Lexer
from brolang.parser import Parser
from brolang.interpreter import Interpreter
from brolang.vm.compiler import Compiler, apply_peephole
from brolang.vm.opcodes import Op
from brolang.vm.vm import VM
from brolang.stdlib import get_stdlib_module


def _jalankan_bro(kode: str):
    """Jalankan kode BroLang via interpreter, kembalikan list output."""
    ast = Parser(Lexer(kode).tokenize()).parse()
    interp = Interpreter()
    interp.interpret(ast)
    return interp.output


# ================= 1. Peephole Optimizer =================


class TestPeephole:
    def test_fold_konstanta_aritmatika(self):
        kode = "tulis 2 + 3 * 4\ntulis 10 - (2 + 3)\n"
        ast = Parser(Lexer(kode).tokenize()).parse()
        bc = Compiler().compile(ast)
        assert _jalankan_bro(kode) == ["14", "5"]

    def test_fold_konstanta_string(self):
        kode = 'tulis "ha" + "lo"\n'
        bc = Compiler().compile(Parser(Lexer(kode).tokenize()).parse())
        # "ha"+"lo" harus fold jadi satu PUSH_CONST
        ops = [ins.op for ins in bc.instructions]
        assert ops.count(Op.ADD) == 0
        assert _jalankan_bro(kode) == ["halo"]

    def test_fold_perbandingan(self):
        # Pakai konstanta non-fast-path (3, 5) supaya jadi PUSH_CONST
        kode = "tulis 3 < 5\ntulis 7 == 7\n"
        bc = Compiler().compile(Parser(Lexer(kode).tokenize()).parse())
        ops = [ins.op for ins in bc.instructions]
        assert Op.LT not in ops and Op.EQ not in ops
        assert _jalankan_bro(kode) == ["True", "True"]

    def test_fold_negasi_konstanta(self):
        kode = "buat x = -5\ntulis x\n"
        assert _jalankan_bro(kode) == ["-5"]

    def test_nop_dihapus(self):
        kode = "pass\npass\ntulis 1\n"
        bc = Compiler().compile(Parser(Lexer(kode).tokenize()).parse())
        ops = [ins.op for ins in bc.instructions]
        assert Op.NOP not in ops
        assert _jalankan_bro(kode) == ["1"]

    def test_jump_tetap_benar_setelah_fold(self):
        # Constant folding mengubah index instruksi — jump harus tetap benar
        kode = """\
jika 1 + 1 == 2 maka
    tulis "ya"
lainnya
    tulis "tidak"
selesai
"""
        assert _jalankan_bro(kode) == ["ya"]

    def test_loop_tetap_benar(self):
        kode = """\
buat total = 0
untuk i dalam range(0, 5) lakukan
    total = total + i
selesai
tulis total
"""
        assert _jalankan_bro(kode) == ["10"]


# ================= 2. Method Cache & Fix Binding VM =================


class TestVMMethod:
    def test_method_binding_param(self):
        # Fix v6.3: non-static method param_count harus menghitung self
        kode = """\
kelas Karyawan
    fungsi __init__(nama, gaji)
        self.nama = nama
        self.gaji = gaji
    selesai
    fungsi info()
        kembali self.nama + ":" + teks(self.gaji)
    selesai
selesai
buat k = Karyawan("Budi", 5000)
tulis k.info()
"""
        ast = Parser(Lexer(kode).tokenize()).parse()
        bc = Compiler().compile(ast)
        vm = VM()
        vm.run(bc)
        assert vm.output == ["Budi:5000"]

    def test_inheritance_method_cache(self):
        kode = """\
kelas Induk
    fungsi sapa()
        kembali "dari induk"
    selesai
selesai
kelas Anak(Induk)
    fungsi __init__()
        pass
    selesai
selesai
buat a = Anak()
tulis a.sapa()
"""
        ast = Parser(Lexer(kode).tokenize()).parse()
        bc = Compiler().compile(ast)
        vm = VM()
        vm.run(bc)
        assert vm.output == ["dari induk"]

    def test_monkey_patch_invalidasi_cache(self):
        kode = """\
kelas C
    fungsi halo()
        kembali "v1"
    selesai
selesai
buat c = C()
tulis c.halo()
C.halo = lalu() "v2"
tulis c.halo()
"""
        ast = Parser(Lexer(kode).tokenize()).parse()
        bc = Compiler().compile(ast)
        vm = VM()
        vm.run(bc)
        assert vm.output == ["v1", "v2"]

    def test_monkey_patch_parent_invalidasi_subclass_cache(self):
        # Patch method di PARENT harus terlihat oleh instance subclass
        # yang sudah meng-cache lookup lewat parent chain.
        kode = """\
kelas Induk
    fungsi halo()
        kembali "induk"
    selesai
selesai
kelas Anak(Induk)
    fungsi __init__()
        pass
    selesai
selesai
buat a = Anak()
tulis a.halo()
Induk.halo = lalu() "diubah"
tulis a.halo()
"""
        ast = Parser(Lexer(kode).tokenize()).parse()
        bc = Compiler().compile(ast)
        vm = VM()
        vm.run(bc)
        assert vm.output == ["induk", "diubah"]


# ================= 3. Fix Lexer: Multi-line String =================


class TestMultilineString:
    def test_string_multi_baris(self):
        NL = chr(10)
        kode = 'buat x = """halo' + NL + 'dunia"""' + NL + "tulis x" + NL
        assert _jalankan_bro(kode) == ["halo" + NL + "dunia"]

    def test_fstring_multi_baris(self):
        NL = chr(10)
        kode = (
            'buat nama = "Budi"'
            + NL
            + 'buat x = f"""Halo {nama}'
            + NL
            + 'semangat!"""'
            + NL
            + "tulis x"
            + NL
        )
        assert _jalankan_bro(kode) == ["Halo Budi" + NL + "semangat!"]

    def test_fstring_biasa_tetap_jalan(self):
        NL = chr(10)
        kode = 'buat nama = "Budi"' + NL + 'tulis f"Halo {nama}!"' + NL
        assert _jalankan_bro(kode) == ["Halo Budi!"]

    def test_string_biasa_tetap_jalan(self):
        kode = 'tulis "halo"' + chr(10)
        assert _jalankan_bro(kode) == ["halo"]


# ================= 4. Tooling: bro init & bro run =================


class TestTooling:
    def test_bro_init_scaffolding(self):
        with tempfile.TemporaryDirectory(prefix="brolang_init_") as tmp:
            project = os.path.join(tmp, "proyek_ku")
            result = subprocess.run(
                [sys.executable, "-m", "brolang.cli", "init", project],
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            assert result.returncode == 0, result.stdout + result.stderr
            for f in [
                "brolang.json",
                "src/main.bro",
                "tests/test_utama.bro",
                "docs/README.md",
                "README.md",
                ".gitignore",
            ]:
                assert os.path.exists(os.path.join(project, f)), f

    def test_bro_init_tolak_folder_ada(self):
        with tempfile.TemporaryDirectory(prefix="brolang_init_") as tmp:
            project = os.path.join(tmp, "ada")
            os.makedirs(project)
            result = subprocess.run(
                [sys.executable, "-m", "brolang.cli", "init", project],
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            assert result.returncode == 1

    def test_bro_run_tanpa_argumen_manifest(self):
        with tempfile.TemporaryDirectory(prefix="brolang_run_") as tmp:
            subprocess.run(
                [sys.executable, "-m", "brolang.cli", "init", "app"],
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            result = subprocess.run(
                [sys.executable, "-m", "brolang.cli", "run"],
                capture_output=True,
                text=True,
                cwd=os.path.join(tmp, "app"),
            )
            assert result.returncode == 0, result.stdout + result.stderr
            assert "Halo, Dunia!" in result.stdout

    def test_bro_run_tanpa_proyek_error(self):
        with tempfile.TemporaryDirectory(prefix="brolang_run_") as tmp:
            result = subprocess.run(
                [sys.executable, "-m", "brolang.cli", "run"],
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            assert result.returncode == 1


# ================= 5. Modul web_server =================


class TestWebServer:
    def _buat_server(self):
        ws = get_stdlib_module("web_server")
        app = ws.Buat()

        def home(req):
            return req.kirim_json({"pesan": "halo", "angka": 42})

        def detail(req):
            return req.kirim_json({"id": req.parameter["id"], "q": req.query})

        def tambah(req):
            return req.kirim_json({"terima": req.json, "metode": req.metode})

        app.rute("GET", "/", home)
        app.rute("GET", "/pengguna/{id}", detail)
        app.rute("POST", "/kirim", tambah)
        app.jalankan_async(0)
        port = app._server.server_address[1]
        return app, port

    def test_get_dan_parameter(self):
        app, port = self._buat_server()
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/") as r:
                data = json.loads(r.read())
                assert data == {"pesan": "halo", "angka": 42}
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/pengguna/7?q=budi") as r:
                data = json.loads(r.read())
                assert data == {"id": "7", "q": {"q": "budi"}}
        finally:
            app.berhenti()

    def test_post_json(self):
        app, port = self._buat_server()
        try:
            req = urllib.request.Request(
                f"http://127.0.0.1:{port}/kirim",
                data=json.dumps({"x": 1}).encode(),
                method="POST",
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req) as r:
                data = json.loads(r.read())
                assert data == {"terima": {"x": 1}, "metode": "POST"}
        finally:
            app.berhenti()

    def test_route_tidak_ditemukan_404(self):
        app, port = self._buat_server()
        try:
            with pytest.raises(urllib.error.HTTPError) as exc:
                urllib.request.urlopen(f"http://127.0.0.1:{port}/tidak/ada")
            assert exc.value.code == 404
        finally:
            app.berhenti()

    def test_kirim_file_tolak_path_traversal(self):
        # Anti path traversal: kirim_file harus menolak ".."
        ws = get_stdlib_module("web_server")
        app = ws.Buat()

        def serve(req):
            return req.kirim_file("../../etc/passwd")

        app.rute("GET", "/f", serve)
        app.jalankan_async(0)
        port = app._server.server_address[1]
        try:
            with pytest.raises(urllib.error.HTTPError) as exc:
                urllib.request.urlopen(f"http://127.0.0.1:{port}/f")
            assert exc.value.code == 403
        finally:
            app.berhenti()

    def test_integrasi_dari_brolang(self):
        kode = """\
impor web_server
impor web

fungsi halaman(req)
    kembali req.kirim_json({"pesan": "Halo dari BroLang!"})
selesai

buat app = web_server.Buat()
app.rute("GET", "/", halaman)
app.jalankan_async(0)
buat port = app._server.server_address[1]
buat resp = web.get("http://127.0.0.1:" + teks(port) + "/")
tulis resp.json["pesan"]
app.berhenti()
"""
        assert _jalankan_bro(kode) == ["Halo dari BroLang!"]
