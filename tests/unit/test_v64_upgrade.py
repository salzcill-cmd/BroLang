"""
Test BroLang v6.4 — Keamanan, Arsip, Terminal UX & Tooling
==========================================================

Mencakup:
1. Modul `kripto` — hash md5/sha1/sha256/sha512, base64, password PBKDF2+salt, token
2. Modul `arsip` — ZIP (buat/tambah/ekstrak/daftar) & kompresi teks
3. Modul `terminal` — warna ANSI, gaya teks, progress bar, banner
4. CLI — `bro test --nama/--detail`, perintah baru `bro upgrade`, versi 6.4.0
"""

import os
import subprocess
import sys
import tempfile
import zipfile

import pytest

from brolang.lexer import Lexer
from brolang.parser import Parser
from brolang.interpreter import Interpreter
from brolang.stdlib import get_stdlib_module


def _jalankan_bro(kode: str):
    """Jalankan kode BroLang via interpreter, kembalikan list output."""
    ast = Parser(Lexer(kode).tokenize()).parse()
    interp = Interpreter()
    interp.interpret(ast)
    return interp.output


# ================= 1. Modul Kripto =================


class TestKripto:
    def test_md5_nilai_terkenal(self):
        kripto = get_stdlib_module("kripto")
        assert kripto.md5("halo dunia") == "13542524cdae2fd81293384cd60c69c5"

    def test_sha_panjang_digest(self):
        kripto = get_stdlib_module("kripto")
        assert len(kripto.sha1("bro")) == 40
        assert len(kripto.sha256("bro")) == 64
        assert len(kripto.sha512("bro")) == 128

    def test_sha_deterministik(self):
        kripto = get_stdlib_module("kripto")
        assert kripto.sha256("x") == kripto.sha256("x")
        assert kripto.sha256("x") != kripto.sha256("y")

    def test_base64_bulat_balik(self):
        kripto = get_stdlib_module("kripto")
        kode = kripto.base64_encode("BroLang")
        assert kode == "QnJvTGFuZw=="
        assert kripto.base64_decode(kode) == "BroLang"

    def test_hash_password_dan_cek(self):
        kripto = get_stdlib_module("kripto")
        hash1 = kripto.hash_password("rahasia123")
        hash2 = kripto.hash_password("rahasia123")
        # Salt acak → hash berbeda walau password sama
        assert hash1 != hash2
        assert hash1.startswith("pbkdf2_sha256$")
        assert kripto.cek_password("rahasia123", hash1) is True
        assert kripto.cek_password("tebakan", hash1) is False

    def test_cek_password_input_rusak(self):
        kripto = get_stdlib_module("kripto")
        assert kripto.cek_password("x", "bukan-format-hash") is False

    def test_token_panjang_dan_unik(self):
        kripto = get_stdlib_module("kripto")
        assert len(kripto.token(32)) == 32
        assert len(kripto.token(8)) == 8
        assert kripto.token(32) != kripto.token(32)

    def test_modul_dipakai_dari_bro(self):
        out = _jalankan_bro('impor kripto\ntulis kripto.sha256("halo")\n')
        assert len(out[0]) == 64


# ================= 2. Modul Arsip =================


class TestArsip:
    def test_kompres_dekompres(self):
        arsip = get_stdlib_module("arsip")
        teks = "BroLang keren! " * 50
        padat = arsip.kompres(teks)
        assert len(padat) < len(teks)
        assert arsip.dekompres(padat) == teks

    def test_dekompres_data_rusak(self):
        arsip = get_stdlib_module("arsip")
        assert arsip.dekompres("###bukan-base64###") == ""

    def test_zip_buat_daftar_ekstrak(self):
        arsip = get_stdlib_module("arsip")
        with tempfile.TemporaryDirectory() as tmp:
            a = os.path.join(tmp, "a.txt")
            b = os.path.join(tmp, "b.txt")
            with open(a, "w") as f:
                f.write("isi A")
            with open(b, "w") as f:
                f.write("isi B")

            zip_path = os.path.join(tmp, "backup.zip")
            assert arsip.buat_zip(zip_path, [a, b]) is True
            isi = arsip.daftar_zip(zip_path)
            assert set(isi) == {"a.txt", "b.txt"}

            tujuan = os.path.join(tmp, "keluar")
            hasil = arsip.ekstrak_zip(zip_path, tujuan)
            assert set(hasil) == {"a.txt", "b.txt"}
            with open(os.path.join(tujuan, "a.txt")) as f:
                assert f.read() == "isi A"

    def test_zip_tambah_dan_gagal(self):
        arsip = get_stdlib_module("arsip")
        with tempfile.TemporaryDirectory() as tmp:
            a = os.path.join(tmp, "a.txt")
            with open(a, "w") as f:
                f.write("A")
            zip_path = os.path.join(tmp, "x.zip")
            assert arsip.buat_zip(zip_path, [a]) is True

            c = os.path.join(tmp, "c.txt")
            with open(c, "w") as f:
                f.write("C")
            assert arsip.tambah_ke_zip(zip_path, [c]) is True
            assert set(arsip.daftar_zip(zip_path)) == {"a.txt", "c.txt"}

            # File tidak ada → salah (tidak ada yang ditambahkan), tanpa crash
            assert arsip.tambah_ke_zip(zip_path, "tidak_ada.txt") is False
            assert "tidak_ada.txt" not in arsip.daftar_zip(zip_path)

    def test_zip_file_rusak(self):
        arsip = get_stdlib_module("arsip")
        with tempfile.TemporaryDirectory() as tmp:
            buruk = os.path.join(tmp, "buruk.zip")
            with open(buruk, "w") as f:
                f.write("bukan zip")
            assert arsip.daftar_zip(buruk) == []
            assert arsip.ekstrak_zip(buruk) == []

    def test_ekstrak_zip_aman_dari_zip_slip(self):
        """Member ZIP berbahaya (`../keluar.txt`) dilewati saat ekstrak."""
        arsip = get_stdlib_module("arsip")
        with tempfile.TemporaryDirectory() as tmp:
            zip_path = os.path.join(tmp, "jahat.zip")
            with zipfile.ZipFile(zip_path, "w") as z:
                z.writestr("../keluar.txt", "jahat")
                z.writestr("aman.txt", "ok")
            hasil = arsip.ekstrak_zip(zip_path, tmp)
            assert "aman.txt" in hasil
            assert "../keluar.txt" not in hasil
            # Pastikan tidak ada file yang bocor keluar dari folder tujuan
            assert not os.path.exists(os.path.join(os.path.dirname(tmp), "keluar.txt"))

    def test_modul_dipakai_dari_bro(self):
        out = _jalankan_bro(
            'impor arsip\n'
            'buat padat = arsip.kompres("halo" * 10)\n'
            'tulis arsip.dekompres(padat)\n'
        )
        assert out[0] == "halo" * 10


# ================= 3. Modul Terminal =================


class TestTerminal:
    def test_warna_ansi(self):
        terminal = get_stdlib_module("terminal")
        assert terminal.merah("x") == "\033[31mx\033[0m"
        assert terminal.hijau("x") == "\033[32mx\033[0m"
        assert terminal.kuning("x") == "\033[33mx\033[0m"
        assert terminal.tebal("x") == "\033[1mx\033[0m"
        assert terminal.warna("x", "biru") == "\033[34mx\033[0m"

    def test_bilah_progress(self):
        terminal = get_stdlib_module("terminal")
        assert terminal.bilah_progress(0, 10).endswith("] 0%")
        assert terminal.bilah_progress(5, 10).endswith("] 50%")
        assert terminal.bilah_progress(10, 10).endswith("] 100%")
        # Panjang bilah sesuai lebar
        lebar_bilah = terminal.bilah_progress(5, 10, 20)
        assert lebar_bilah.index("]") - lebar_bilah.index("[") - 1 == 20

    def test_bilah_progress_batas(self):
        terminal = get_stdlib_module("terminal")
        assert terminal.bilah_progress(-5, 10).endswith("] 0%")
        assert terminal.bilah_progress(99, 10).endswith("] 100%")
        assert terminal.bilah_progress(5, 0).endswith("] 100%")  # total 0 tidak crash

    def test_banner(self):
        terminal = get_stdlib_module("terminal")
        banner = terminal.banner("Aplikasi Saya")
        assert "Aplikasi Saya" in banner
        assert "═" in banner

    def test_pesan_status_mencetak(self, capsys):
        terminal = get_stdlib_module("terminal")
        assert terminal.sukses("oke") == ""
        captured = capsys.readouterr()
        assert "✓ oke" in captured.out

    def test_modul_dipakai_dari_bro(self):
        out = _jalankan_bro('impor terminal\ntulis terminal.merah("x")\n')
        assert out[0] == "\033[31mx\033[0m"


# ================= 4. CLI v6.4 =================


class TestCLIv64:
    def test_version_6_4(self):
        result = subprocess.run(
            [sys.executable, "-m", "brolang.cli", "--version"],
            capture_output=True, text=True,
        )
        assert result.returncode == 0
        assert "6.4.0" in result.stdout

    def test_upgrade_terdaftar(self):
        result = subprocess.run(
            [sys.executable, "-m", "brolang.cli", "--help"],
            capture_output=True, text=True,
        )
        assert result.returncode == 0
        assert "upgrade" in result.stdout

    def test_doc_topik_kripto(self):
        result = subprocess.run(
            [sys.executable, "-m", "brolang.cli", "doc", "kripto"],
            capture_output=True, text=True,
        )
        assert result.returncode == 0
        assert "kripto.sha256" in result.stdout

    def test_bro_test_nama_filter(self):
        with tempfile.TemporaryDirectory(prefix="brolang_test_") as tmp:
            os.makedirs(os.path.join(tmp, "tests"))
            with open(os.path.join(tmp, "tests", "test_alpha.bro"), "w") as f:
                f.write('tulis "dari-alpha"\n')
            with open(os.path.join(tmp, "tests", "test_beta.bro"), "w") as f:
                f.write('tulis "dari-beta"\n')

            result = subprocess.run(
                [sys.executable, "-m", "brolang.cli", "test", "--nama", "alpha"],
                capture_output=True, text=True, cwd=tmp,
            )
            assert result.returncode == 0, result.stdout + result.stderr
            assert "dari-alpha" in result.stdout
            assert "dari-beta" not in result.stdout
            assert "1 berhasil" in result.stdout

    def test_bro_test_detail(self):
        with tempfile.TemporaryDirectory(prefix="brolang_test_") as tmp:
            with open(os.path.join(tmp, "test_satu.bro"), "w") as f:
                f.write('tulis "ok-satu"\n')

            result = subprocess.run(
                [sys.executable, "-m", "brolang.cli", "test", "--detail"],
                capture_output=True, text=True, cwd=tmp,
            )
            assert result.returncode == 0, result.stdout + result.stderr
            assert "ok-satu" in result.stdout
            assert "✓" in result.stdout
