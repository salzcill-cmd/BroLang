"""
Unit tests: BroLang v7.2 — Fitur Sintaks + Konsistensi VM + Perluasan Library.

Fitur bahasa baru:
- Walrus operator `x := nilai` (sebelumnya rusak di VM)
- List comprehension `[x lalu x dalam list]` (sebelumnya rusak di VM)
- Dict comprehension `{k: v lalu k dalam list}` (sebelumnya rusak di VM)
- Set comprehension `{x lalu x dalam list}`
- Generator `hasilkan` / `hasilkandari` (sebelumnya rusak di VM)
- `dengan` statement (sebelumnya rusak di VM)
- Null-safe indexing `arr?[0]`

Perluasan library: `waktu`, `file`, `dasar`, `acak`.
"""

import pytest

from brolang.stdlib import get_stdlib_module
from brolang.lexer import Lexer
from brolang.parser import Parser
from brolang.interpreter import Interpreter
from brolang.vm.compiler import Compiler
from brolang.vm.vm import VM


def _mod(nama):
    return get_stdlib_module(nama)


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
# Walrus operator
# ============================================================


class TestWalrus:
    def test_walrus_di_ekspresi(self):
        kode = 'buat hasil = (x := 10) + 5\ntulis hasil\ntulis x\n'
        assert _jalankan(kode) == ["15", "10"]
        assert _jalankan_vm(kode) == ["15", "10"]
        assert _jalankan_transpiler(kode) == ["15", "10"]

    def test_walrus_assign_ulang(self):
        kode = 'buat x = 0\nbuat y = (x := 7) * 2\ntulis y\ntulis x\n'
        assert _jalankan(kode) == _jalankan_vm(kode) == ["14", "7"]


# ============================================================
# Comprehension
# ============================================================


class TestComprehension:
    def test_list_comprehension(self):
        kode = 'buat r = [x * 2 lalu x dalam [1, 2, 3]]\ntulis r\n'
        assert _jalankan(kode) == _jalankan_vm(kode) == ["[2, 4, 6]"]
        assert _jalankan_transpiler(kode) == ["[2, 4, 6]"]

    def test_list_comprehension_filter(self):
        kode = ('buat data = [1, 2, 3, 4, 5, 6]\n'
                'buat genap = [x lalu x dalam data jika x % 2 == 0]\n'
                'tulis genap\n')
        assert _jalankan(kode) == _jalankan_vm(kode) == ["[2, 4, 6]"]
        assert _jalankan_transpiler(kode) == ["[2, 4, 6]"]

    def test_dict_comprehension(self):
        kode = 'buat d = {x: x * 2 lalu x dalam [1, 2, 3]}\ntulis d\n'
        assert _jalankan(kode) == _jalankan_vm(kode) == ["{1: 2, 2: 4, 3: 6}"]

    def test_set_comprehension(self):
        kode = 'buat s = {x * 2 lalu x dalam [1, 2, 2, 3]}\ntulis s\n'
        assert _jalankan(kode) == _jalankan_vm(kode) == ["{2, 4, 6}"]
        assert _jalankan_transpiler(kode) == ["{2, 4, 6}"]

    def test_set_comprehension_filter(self):
        kode = ('buat s = {x lalu x dalam [1, 2, 3, 4, 5, 6] jika x % 2 == 0}\n'
                'tulis s\n')
        assert _jalankan(kode) == _jalankan_vm(kode) == ["{2, 4, 6}"]


# ============================================================
# Generator
# ============================================================


class TestGenerator:
    def test_yield_dasar(self):
        kode = ('fungsi gen()\n'
                '    hasilkan 1\n'
                '    hasilkan 2\n'
                'selesai\n'
                'buat g = gen()\n'
                'untuk setiap item dalam g lakukan\n'
                '    tulis item\n'
                'selesai\n')
        assert _jalankan(kode) == _jalankan_vm(kode) == ["1", "2"]
        assert _jalankan_transpiler(kode) == ["1", "2"]

    def test_yield_from(self):
        kode = ('fungsi gen()\n'
                '    hasilkandari [3, 4]\n'
                '    hasilkan 5\n'
                'selesai\n'
                'buat g = gen()\n'
                'untuk setiap item dalam g lakukan\n'
                '    tulis item\n'
                'selesai\n')
        assert _jalankan(kode) == _jalankan_vm(kode) == ["3", "4", "5"]

    def test_yield_di_while(self):
        kode = ('fungsi gen()\n'
                '    buat i = 0\n'
                '    selama i < 3 lakukan\n'
                '        hasilkan i\n'
                '        i += 1\n'
                '    selesai\n'
                'selesai\n'
                'buat g = gen()\n'
                'untuk setiap item dalam g lakukan\n'
                '    tulis item\n'
                'selesai\n')
        assert _jalankan(kode) == _jalankan_vm(kode) == ["0", "1", "2"]


# ============================================================
# dengan (with) statement
# ============================================================


class TestDengan:
    def test_dengan_sederhana(self):
        kode = 'dengan 5 sebagai x\n    tulis x\nselesai\n'
        assert _jalankan(kode) == _jalankan_vm(kode) == ["5"]

    def test_dengan_enter_exit(self):
        kode = ('kelas K\n'
                '    fungsi masuk(self)\n'
                '        kembali "masuk!"\n'
                '    selesai\n'
                '    fungsi keluar(self)\n'
                '        tulis "keluar!"\n'
                '    selesai\n'
                'selesai\n'
                'buat k = K()\n'
                'dengan k sebagai m\n'
                '    tulis m\n'
                'selesai\n')
        assert _jalankan(kode) == _jalankan_vm(kode) == ["masuk!", "keluar!"]

    def test_dengan_exit_saat_error(self):
        kode = ('buat keluar_dipanggil = salah\n'
                'kelas K\n'
                '    fungsi keluar(self)\n'
                '        buat keluar_dipanggil = benar\n'
                '    selesai\n'
                'selesai\n'
                'buat k = K()\n'
                'dengan k sebagai m\n'
                '    lempar "boom"\n'
                'selesai\n')
        # keluar dipanggil sebelum error naik
        with pytest.raises(Exception):
            _jalankan(kode)


# ============================================================
# Null-safe indexing
# ============================================================


class TestNullSafeIndex:
    def test_target_kosong(self):
        kode = 'buat data = kosong\ntulis data?[0] ?? "default"\n'
        assert _jalankan(kode) == _jalankan_vm(kode) == ["default"]
        assert _jalankan_transpiler(kode) == ["default"]

    def test_index_normal(self):
        kode = 'buat data = [10, 20, 30]\ntulis data?[0]\n'
        assert _jalankan(kode) == _jalankan_vm(kode) == ["10"]

    def test_index_di_luar_jangkauan(self):
        kode = 'buat data = [10, 20]\ntulis data?[5] ?? "x"\n'
        assert _jalankan(kode) == _jalankan_vm(kode) == ["x"]

    def test_dict_key(self):
        kode = 'buat d = {"a": 1}\ntulis d?["a"] ?? 0\n'
        assert _jalankan(kode) == _jalankan_vm(kode) == ["1"]

    def test_chain_null_safe(self):
        kode = 'buat a = kosong\nbuat b = [1, 2, 3]\ntulis a?[0] ?? b?[1]\n'
        assert _jalankan(kode) == _jalankan_vm(kode) == ["2"]


# ============================================================
# Perluasan library
# ============================================================


class TestLibraryV72:
    def test_waktu_baru(self):
        w = _mod("waktu")
        assert w.timestamp() > 1_000_000_000
        assert w.milidetik() > 1_000_000_000_000
        assert isinstance(w.zona_waktu(), str) and w.zona_waktu()
        assert len(w.dari_timestamp(w.timestamp())) > 10
        assert len(w.hari_ini()) == 10

    def test_waktu_baru_v72(self):
        w = _mod("waktu")
        assert "T" in w.waktu_iso()
        assert w.tambah_hari("2026-01-01", 10) == "2026-01-11"
        assert w.tambah_hari("2026-01-01", -1) == "2025-12-31"
        assert w.umur("2000-01-01") >= 20
        assert w.selisih_waktu("2026-01-01 00:00:00", "2026-01-01 01:00:00") == 3600
        assert abs(w.detik_sejak(w.timestamp() - 5) - 5) < 0.01

    def test_file_biner(self, tmp_path):
        f = _mod("file")
        path = str(tmp_path / "data.bin")
        f.tulis_biner(path, bytes([1, 2, 3]))
        assert f.baca_biner(path) == bytes([1, 2, 3])
        f.ubah_nama(path, str(tmp_path / "data2.bin"))
        assert f.ada(str(tmp_path / "data2.bin"))
        f.ubah_waktu(str(tmp_path / "data2.bin"))

    def test_dasar_baru(self):
        db = _mod("dasar")
        assert db.unik([1, 2, 2, 3]) == [1, 2, 3]
        assert db.terbalik("abc") == "cba"
        assert db.urutkan([3, 1, 2]) == [1, 2, 3]
        assert db.kunci({"a": 1}) == ["a"]
        assert db.nilai({"a": 1}) == [1]

    def test_acak_baru(self):
        ac = _mod("acak")
        assert len(ac.kocok([1, 2, 3])) == 3
        assert ac.koin() in ("kepala", "ekor")
        assert 1 <= ac.dadu() <= 6
        assert len(ac.unik([1, 2, 3, 4], 2)) == 2

    def test_waktu_dari_bro(self):
        out = _jalankan(
            "impor waktu\n"
            "tulis waktu.hari_ini() == waktu.tanggal()\n"
            "tulis waktu.timestamp() > 1000000\n"
        )
        assert out == ["True", "True"]

    def test_dasar_dari_bro(self):
        out = _jalankan(
            "impor dasar\n"
            "tulis dasar.unik([1, 2, 2, 3])\n"
            "tulis dasar.terbalik(\"abc\")\n"
            "tulis dasar.urutkan([3, 1, 2])\n"
        )
        assert out == ["[1, 2, 3]", "cba", "[1, 2, 3]"]

    def test_acak_dari_bro(self):
        out = _jalankan(
            "impor acak\n"
            "buat k = acak.koin()\n"
            "tulis k == \"kepala\" atau k == \"ekor\"\n"
            "tulis acak.dadu() >= 1\n"
        )
        assert out == ["True", "True"]


# ============================================================
# Konsistensi lintas mesin (audit v7.2) — bug yang ditemukan
# ============================================================


class TestKonsistensiLintasMesin:
    def test_slicing_string_konsisten(self):
        kode = 'buat s = "abcd"\ntulis s[1:3]\ntulis s[:2]\ntulis s[::2]\n'
        out = _jalankan(kode)
        assert out == ["bc", "ab", "ac"]
        assert _jalankan_vm(kode) == out
        assert _jalankan_transpiler(kode) == out

    def test_slicing_list_konsisten(self):
        kode = "buat a = [0, 1, 2, 3, 4]\ntulis a[1:3]\ntulis a[:2]\ntulis a[::2]\ntulis a[::-1]\n"
        out = _jalankan(kode)
        assert out == ["[1, 2]", "[0, 1]", "[0, 2, 4]", "[4, 3, 2, 1, 0]"]
        assert _jalankan_vm(kode) == out
        assert _jalankan_transpiler(kode) == out

    def test_list_method_konsisten(self):
        kode = (
            "buat a = [3, 1, 2]\n"
            "tulis a.urutkan()\n"
            "a.tambah(4)\n"
            "a.sisipkan(0, 0)\n"
            "tulis a\n"
            "tulis a.jumlah()\n"
        )
        out = _jalankan(kode)
        assert out == ["[1, 2, 3]", "[0, 1, 2, 3, 4]", "5"]
        assert _jalankan_vm(kode) == out
        assert _jalankan_transpiler(kode) == out

    def test_dict_method_konsisten(self):
        kode = (
            'buat d = {"a": 1, "b": 2}\n'
            "tulis d.kunci()\n"
            "tulis d.nilai()\n"
            'tulis d.punya("a")\n'
            'd["c"] = 3\n'
            "tulis d\n"
        )
        out = _jalankan(kode)
        assert out == ["['a', 'b']", "[1, 2]", "True", "{'a': 1, 'b': 2, 'c': 3}"]
        assert _jalankan_vm(kode) == out
        assert _jalankan_transpiler(kode) == out

    def test_closure_vm(self):
        kode = (
            "fungsi buat_penambah(n)\n"
            "    fungsi tambah(x)\n"
            "        kembali x + n\n"
            "    selesai\n"
            "    kembali tambah\n"
            "selesai\n"
            "buat tambah5 = buat_penambah(5)\n"
            "tulis tambah5(10)\n"
            "buat ganda = buat_penambah(100)\n"
            "tulis ganda(1)\n"
        )
        out = _jalankan(kode)
        assert out == ["15", "101"]
        assert _jalankan_vm(kode) == out

    def test_multiple_return_unpack_konsisten(self):
        kode = (
            "fungsi f()\n"
            "    kembali 1, 2, 3\n"
            "selesai\n"
            "buat a, b, c = f()\n"
            "tulis a, b, c\n"
        )
        out = _jalankan(kode)
        assert out == ["1 2 3"]
        assert _jalankan_vm(kode) == out
        assert _jalankan_transpiler(kode) == out

    def test_method_object_repr_konsisten(self):
        """v7.2.1: `tulis k.x` (method) → `<method K.x>` di ketiga mesin."""
        kode = (
            "kelas K\n"
            "    fungsi __init__(self)\n"
            "        self._x = 5\n"
            "    selesai\n"
            "    fungsi x(self)\n"
            "        kembali self._x\n"
            "    selesai\n"
            "selesai\n"
            "buat k = K()\n"
            "tulis k.x\n"
        )
        out = _jalankan(kode)
        assert out == ["<method K.x>"]
        assert _jalankan_vm(kode) == out
        assert _jalankan_transpiler(kode) == out

    def test_generator_call_returns_list_konsisten(self):
        """v7.2.1: `tulis gen(3)` → `[1, 2, 3]` di ketiga mesin."""
        kode = (
            "fungsi gen(n)\n"
            "    untuk i dari 1 sampai n lakukan\n"
            "        hasilkan i\n"
            "    selesai\n"
            "selesai\n"
            "tulis gen(3)\n"
        )
        out = _jalankan(kode)
        assert out == ["[1, 2, 3]"]
        assert _jalankan_vm(kode) == out
        assert _jalankan_transpiler(kode) == out

    def test_generator_yield_from_konsisten(self):
        """v7.2.1: `hasilkandari` → list di ketiga mesin."""
        kode = (
            "fungsi a()\n"
            "    hasilkan 1\n"
            "    hasilkan 2\n"
            "selesai\n"
            "fungsi b()\n"
            "    hasilkandari a()\n"
            "    hasilkan 3\n"
            "selesai\n"
            "tulis b()\n"
        )
        out = _jalankan(kode)
        assert out == ["[1, 2, 3]"]
        assert _jalankan_vm(kode) == out
        assert _jalankan_transpiler(kode) == out
