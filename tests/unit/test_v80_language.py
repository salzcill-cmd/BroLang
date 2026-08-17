"""
Unit tests: BroLang v8.0 — Fitur Bahasa Modern + Konsistensi VM.

Fitur bahasa baru:
- Spread objek `{...a, "b": 1}` (campur dengan pasangan kunci-nilai, urutan
  sumber dipertahankan — kunci item belakang menimpa item depan)
- Null-coalescing assignment `x ??= v` (short-circuit: nilai kanan hanya
  dievaluasi bila nilai saat ini kosong) — variabel, atribut objek, index
- `kecuali (TipeA, TipeB) sebagai e` — multi-tipe exception (cocok bila
  SALAH SATU tipe cocok; selain itu re-raise)

Performa VM v8.0:
- `_execute` fast path tanpa try/except bila bytecode tidak punya handler
- Alokasi frame sesuai jumlah slot lokal (bukan selalu 64)
- `_call_function` fast path untuk pemanggilan fungsi VM biasa
- LOAD_GLOBAL memeriksa globals dulu (satu dict op untuk variabel user)
"""

import pytest

from brolang.lexer import Lexer
from brolang.parser import Parser
from brolang.interpreter import Interpreter
from brolang.vm.compiler import Compiler
from brolang.vm.vm import VM


def _jalankan(kode):
    ast = Parser(Lexer(kode).tokenize()).parse()
    interp = Interpreter()
    interp.interpret(ast)
    return interp.output


def _jalankan_vm(kode):
    ast = Parser(Lexer(kode).tokenize()).parse()
    vm = VM()
    vm.run(Compiler().compile(ast))
    return vm.output


def _jalankan_transpiler(kode):
    from brolang.vm.transpiler import Transpiler
    import contextlib
    import io

    ast = Parser(Lexer(kode).tokenize()).parse()
    py = Transpiler().transpile(ast)
    buf = io.StringIO()
    g = {"__name__": "__main__"}
    with contextlib.redirect_stdout(buf):
        exec(compile(py, "<bro>", "exec"), g)
    return buf.getvalue().strip().splitlines()


# ============================================================
# Spread objek
# ============================================================


class TestSpreadObjek:
    def test_spread_dasar(self):
        kode = 'buat a = {"x": 1, "y": 2}\nbuat b = {...a, "z": 3}\ntulis b\n'
        assert _jalankan(kode) == ["{'x': 1, 'y': 2, 'z': 3}"]
        assert _jalankan_vm(kode) == ["{'x': 1, 'y': 2, 'z': 3}"]
        assert _jalankan_transpiler(kode) == ["{'x': 1, 'y': 2, 'z': 3}"]

    def test_spread_kunci_sama_ditimpa(self):
        kode = 'buat a = {"x": 1, "y": 2}\nbuat b = {...a, "y": 99}\ntulis b\n'
        assert _jalankan(kode) == _jalankan_vm(kode) == ["{'x': 1, 'y': 99}"]

    def test_spread_di_awal(self):
        kode = 'buat a = {"x": 1}\nbuat b = {...a}\ntulis b\n'
        assert _jalankan(kode) == _jalankan_vm(kode) == ["{'x': 1}"]

    def test_spread_di_tengah(self):
        # Item belakang menimpa item depan: a.x menimpa "a": 0, "z" menimpa
        # apa pun dari a (a tidak punya z).
        kode = 'buat a = {"x": 1}\nbuat b = {"a": 0, ...a, "z": 3}\ntulis b\n'
        assert _jalankan(kode) == _jalankan_vm(kode) == ["{'a': 0, 'x': 1, 'z': 3}"]
        assert _jalankan_transpiler(kode) == ["{'a': 0, 'x': 1, 'z': 3}"]

    def test_spread_urutan_kunci_belakang_menang(self):
        # {"x": 1, ...a} — spread BELAKANG menimpa x dari depan.
        kode = 'buat a = {"x": 99}\nbuat b = {"x": 1, ...a}\ntulis b\n'
        assert _jalankan(kode) == _jalankan_vm(kode) == ["{'x': 99}"]
        assert _jalankan_transpiler(kode) == ["{'x': 99}"]

    def test_spread_multi(self):
        kode = ('buat a = {"x": 1}\n'
                'buat b = {"y": 2}\n'
                'buat c = {...a, ...b}\n'
                'tulis c\n')
        assert _jalankan(kode) == _jalankan_vm(kode) == ["{'x': 1, 'y': 2}"]

    def test_spread_dengan_trailing_comma(self):
        kode = 'buat a = {"x": 1}\nbuat b = {...a, "y": 2,}\ntulis b\n'
        assert _jalankan(kode) == _jalankan_vm(kode) == ["{'x': 1, 'y': 2}"]

    def test_spread_nilai_bukan_objek_error(self):
        kode = 'buat a = 5\nbuat b = {...a}\ntulis b\n'
        with pytest.raises(Exception):
            _jalankan(kode)
        with pytest.raises(Exception):
            _jalankan_vm(kode)


# ============================================================
# Null-coalescing assignment ??=
# ============================================================


class TestNullCoalescingAssign:
    def test_variabel_kosong_diisi(self):
        kode = 'buat x = kosong\nx ??= 5\ntulis x\n'
        assert _jalankan(kode) == _jalankan_vm(kode) == ["5"]
        assert _jalankan_transpiler(kode) == ["5"]

    def test_variabel_terisi_tidak_diubah(self):
        kode = 'buat x = 10\nx ??= 5\ntulis x\n'
        assert _jalankan(kode) == _jalankan_vm(kode) == ["10"]
        assert _jalankan_transpiler(kode) == ["10"]

    def test_variabel_falsy_bukan_kosong(self):
        # 0, "", dan False BUKAN kosong — tidak diisi ulang.
        for awal, expect in (("0", "0"), ('""', ""), ("salah", "False")):
            kode = f'buat x = {awal}\nx ??= 5\ntulis x\n'
            assert _jalankan(kode) == _jalankan_vm(kode) == [expect]

    def test_short_circuit_tidak_evaluasi_kanan(self):
        # Nilai kanan (fungsi f) TIDAK boleh dipanggil bila x tidak kosong.
        kode = ('buat hitung = [0]\n'
                'fungsi f()\n'
                '    hitung[0] = hitung[0] + 1\n'
                '    kembali 5\n'
                'selesai\n'
                'buat x = 10\n'
                'x ??= f()\n'
                'tulis x\n'
                'tulis hitung[0]\n')
        assert _jalankan(kode) == _jalankan_vm(kode) == ["10", "0"]
        assert _jalankan_transpiler(kode) == ["10", "0"]

    def test_short_circuit_kosong_evaluasi_kanan(self):
        kode = ('buat hitung = [0]\n'
                'fungsi f()\n'
                '    hitung[0] = hitung[0] + 1\n'
                '    kembali 5\n'
                'selesai\n'
                'buat x = kosong\n'
                'x ??= f()\n'
                'tulis x\n'
                'tulis hitung[0]\n')
        assert _jalankan(kode) == _jalankan_vm(kode) == ["5", "1"]
        assert _jalankan_transpiler(kode) == ["5", "1"]

    def test_atribut_objek(self):
        kode = ('kelas Akun\n'
                '    fungsi __init__(self)\n'
                '        self.nama = kosong\n'
                '    selesai\n'
                'selesai\n'
                'buat a = Akun()\n'
                'a.nama ??= "Budi"\n'
                'tulis a.nama\n')
        assert _jalankan(kode) == _jalankan_vm(kode) == ["Budi"]
        assert _jalankan_transpiler(kode) == ["Budi"]

    def test_atribut_objek_terisi(self):
        kode = ('kelas Akun\n'
                '    fungsi __init__(self)\n'
                '        self.nama = "Ani"\n'
                '    selesai\n'
                'selesai\n'
                'buat a = Akun()\n'
                'a.nama ??= "Budi"\n'
                'tulis a.nama\n')
        assert _jalankan(kode) == _jalankan_vm(kode) == ["Ani"]
        assert _jalankan_transpiler(kode) == ["Ani"]

    def test_index_list_kosong(self):
        kode = 'buat d = [kosong, 2]\nd[0] ??= 99\ntulis d\n'
        assert _jalankan(kode) == _jalankan_vm(kode) == ["[99, 2]"]
        assert _jalankan_transpiler(kode) == ["[99, 2]"]

    def test_index_list_terisi(self):
        kode = 'buat d = [1, 2]\nd[0] ??= 99\ntulis d\n'
        assert _jalankan(kode) == _jalankan_vm(kode) == ["[1, 2]"]
        assert _jalankan_transpiler(kode) == ["[1, 2]"]

    def test_index_objek(self):
        kode = 'buat d = {"a": kosong}\nd["a"] ??= 7\ntulis d\n'
        assert _jalankan(kode) == _jalankan_vm(kode) == ["{'a': 7}"]

    def test_bukan_conflict_dengan_null_coalescing(self):
        # `??` tetap null-coalescing; `??=` assignment.
        kode = 'buat x = kosong\nbuat y = x ?? 3\ntulis y\n'
        assert _jalankan(kode) == _jalankan_vm(kode) == ["3"]


# ============================================================
# kecuali multi-tipe
# ============================================================


class TestKecualiMultiTipe:
    def test_cocok_tipe_pertama(self):
        kode = ('coba\n'
                '    buat x = 1 / 0\n'
                'kecuali (TypeError, ZeroDivisionError) sebagai e\n'
                '    tulis "caught"\n'
                'selesai\n')
        assert _jalankan(kode) == _jalankan_vm(kode) == ["caught"]
        assert _jalankan_transpiler(kode) == ["caught"]

    def test_cocok_tipe_kedua(self):
        kode = ('coba\n'
                '    buat x = 1 / 0\n'
                'kecuali (KeyError, ZeroDivisionError) sebagai e\n'
                '    tulis "caught"\n'
                'selesai\n')
        assert _jalankan(kode) == _jalankan_vm(kode) == ["caught"]
        assert _jalankan_transpiler(kode) == ["caught"]

    def test_binding_variabel(self):
        kode = ('coba\n'
                '    buat x = 1 / 0\n'
                'kecuali (TypeError, ZeroDivisionError) sebagai e\n'
                '    tulis "punya error"\n'
                'selesai\n')
        assert _jalankan(kode) == _jalankan_vm(kode) == ["punya error"]

    def test_tidak_cocok_re_raise(self):
        from brolang.exceptions import ZeroDivisionError_ as ZDE

        kode = ('coba\n'
                '    buat x = 1 / 0\n'
                'kecuali (KeyError, AttributeError) sebagai e\n'
                '    tulis "tidak boleh"\n'
                'selesai\n')
        with pytest.raises(ZDE):
            _jalankan(kode)
        with pytest.raises(Exception):
            _jalankan_vm(kode)
        with pytest.raises(Exception):
            _jalankan_transpiler(kode)

    def test_klausa_multi_lalu_klausa_lain(self):
        # Multi-tipe di klausa pertama, tipe lain di klausa kedua.
        kode = ('coba\n'
                '    buat x = 1 / 0\n'
                'kecuali (KeyError, AttributeError) sebagai e\n'
                '    tulis "salah"\n'
                'kecuali ZeroDivisionError sebagai e2\n'
                '    tulis "benar"\n'
                'selesai\n')
        assert _jalankan(kode) == _jalankan_vm(kode) == ["benar"]
        assert _jalankan_transpiler(kode) == ["benar"]

    def test_satu_tipe_dalam_kurung(self):
        kode = ('coba\n'
                '    buat x = 1 / 0\n'
                'kecuali (ZeroDivisionError) sebagai e\n'
                '    tulis "caught"\n'
                'selesai\n')
        assert _jalankan(kode) == _jalankan_vm(kode) == ["caught"]
        assert _jalankan_transpiler(kode) == ["caught"]


# ============================================================
# Error kustom (kelas_error) di kecuali multi-tipe — konsisten 3 mesin
# ============================================================


class TestKecualiMultiTipeErrorKustom:
    def test_error_kustom_cocok(self):
        kode = ('kelas_error ValidasiGagal extends Kesalahan\n'
                '    fungsi __init__(pesan)\n'
                '        self.pesan = pesan\n'
                '    selesai\n'
                'selesai\n'
                'coba\n'
                '    lempar ValidasiGagal("email kosong")\n'
                'kecuali (TypeError, ValidasiGagal) sebagai e\n'
                '    tulis "caught: " + e.pesan\n'
                'selesai\n')
        expected = ["caught: email kosong"]
        assert _jalankan(kode) == _jalankan_vm(kode) == expected
        assert _jalankan_transpiler(kode) == expected

    def test_error_kustom_tidak_cocok_tipe_lain(self):
        kode = ('kelas_error ErrA extends Kesalahan\n'
                '    fungsi __init__()\n'
                '        pass\n'
                '    selesai\n'
                'selesai\n'
                'coba\n'
                '    lempar ErrA()\n'
                'kecuali (TypeError, ValueError) sebagai e\n'
                '    tulis "salah"\n'
                'kecuali ErrA sebagai e\n'
                '    tulis "benar"\n'
                'selesai\n')
        expected = ["benar"]
        assert _jalankan(kode) == _jalankan_vm(kode) == expected
        assert _jalankan_transpiler(kode) == expected

    def test_induk_menangkap_turunan(self):
        kode = ('kelas_error IndukErr extends Kesalahan\n'
                '    fungsi __init__(pesan)\n'
                '        self.pesan = pesan\n'
                '    selesai\n'
                'selesai\n'
                'kelas_error TurunanErr extends IndukErr\n'
                '    fungsi __init__(pesan)\n'
                '        self.pesan = pesan\n'
                '    selesai\n'
                'selesai\n'
                'coba\n'
                '    lempar TurunanErr("dari turunan")\n'
                'kecuali IndukErr sebagai e\n'
                '    tulis "induk: " + e.pesan\n'
                'selesai\n')
        expected = ["induk: dari turunan"]
        assert _jalankan(kode) == _jalankan_vm(kode) == expected
        assert _jalankan_transpiler(kode) == expected

    def test_error_kustom_multi_tipe_builtin(self):
        # Error kustom & builtin dalam satu klausa multi-tipe.
        kode = ('kelas_error ErrX extends Kesalahan\n'
                '    fungsi __init__(pesan)\n'
                '        self.pesan = pesan\n'
                '    selesai\n'
                'selesai\n'
                'coba\n'
                '    lempar ErrX("x")\n'
                'kecuali (KeyError, ValueError) sebagai e\n'
                '    tulis "salah"\n'
                'kecuali (ErrX, TypeError) sebagai e\n'
                '    tulis "ok: " + e.pesan\n'
                'selesai\n')
        expected = ["ok: x"]
        assert _jalankan(kode) == _jalankan_vm(kode) == expected
        assert _jalankan_transpiler(kode) == expected


# ============================================================
# VM performance — hasil eksekusi tetap identik
# ============================================================


class TestVMKonsistensiPerforma:
    def test_loop_aritmatika_vm_sama(self):
        kode = ('buat total = 0\n'
                'untuk i dalam range(1, 1000) lakukan\n'
                '    total = total + i\n'
                'selesai\n'
                'tulis total\n')
        assert _jalankan(kode) == _jalankan_vm(kode) == ["499500"]

    def test_rekursif_vm_sama(self):
        kode = ('fungsi fib(n)\n'
                '    jika n < 2 maka\n'
                '        kembali n\n'
                '    selesai\n'
                '    kembali fib(n - 1) + fib(n - 2)\n'
                'selesai\n'
                'tulis fib(15)\n')
        assert _jalankan(kode) == _jalankan_vm(kode) == ["610"]

    def test_handler_dan_non_handler_campur(self):
        # Bytecode dengan handler (coba/kecuali) dan tanpa handler — fast
        # path _execute tidak boleh mengubah perilaku.
        kode = ('fungsi aman(x)\n'
                '    coba\n'
                '        kembali 100 / x\n'
                '    kecuali ZeroDivisionError sebagai e\n'
                '        kembali -1\n'
                '    selesai\n'
                'selesai\n'
                'tulis aman(5)\n'
                'tulis aman(0)\n')
        assert _jalankan(kode) == _jalankan_vm(kode) == ["20.0", "-1"]
