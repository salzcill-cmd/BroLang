"""
Unit tests untuk BroLang v7.0
=============================

Tests untuk:
- Multiple assignment: `a, b = 1, 2`, swap `a, b = b, a`, `buat a, b = ...`
- Switch expression: `cocokkan nilai { pola: ekspresi }` sebagai ekspresi bernilai
- Error propagation `?`: buka Result (Benar/Salah) & Option (Ada/Kosong)
- Async/Await sejati: `asinkron fungsi` -> Tugas, `tunggu`, modul `event_loop`
- Konsistensi interpreter vs transpiler; dukungan VM (multi-assign, `?`, try/catch)
"""

import pytest

from brolang.lexer import Lexer
from brolang.parser import Parser
from brolang.interpreter import Interpreter
from brolang.exceptions import RuntimeError_, ZeroDivisionError_, ParserError


def run_code(code):
    """Helper untuk menjalankan kode BroLang lewat interpreter."""
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    interp = Interpreter()
    interp.interpret(ast)
    return interp.output


def run_vm(code):
    """Helper untuk menjalankan kode BroLang lewat bytecode VM."""
    from brolang.vm.compiler import Compiler
    from brolang.vm.vm import VM

    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    bc = Compiler().compile(ast)
    vm = VM()
    vm.run(bc)
    return vm.output


def run_transpiler(code):
    """Helper untuk menjalankan kode lewat transpiler (AST -> Python)."""
    import io
    import contextlib
    from brolang.vm.transpiler import Transpiler

    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    py_code = Transpiler().transpile(ast)
    exec_globals = {"__builtins__": __builtins__}
    stdout_capture = io.StringIO()
    with contextlib.redirect_stdout(stdout_capture):
        exec(py_code, exec_globals)
    out = stdout_capture.getvalue().strip().split("\n")
    return [line for line in out if line]


# ============= Multiple Assignment =============


class TestMultipleAssignment:
    def test_deklarasi_berpasangan(self):
        out = run_code("buat a, b = 1, 2\ntulis a\ntulis b")
        assert out == ["1", "2"]

    def test_swap_aman(self):
        out = run_code("buat a, b = 1, 2\na, b = b, a\ntulis a, b")
        assert out == ["2 1"]

    def test_tiga_variabel(self):
        out = run_code("buat x, y, z = 1, 2, 3\ntulis x, y, z")
        assert out == ["1 2 3"]

    def test_nilai_kurang_dari_target(self):
        # Nilai kanan lebih sedikit: target tersisa bernilai kosong
        out = run_code("buat a, b, c = 1, 2\ntulis a, b, c")
        assert out == ["1 2 None"]

    def test_evaluasi_nilai_kanan_dulu(self):
        # Semua nilai kanan dievaluasi SEBELUM assignment (swap aman
        # bahkan dengan ekspresi yang memakai target).
        out = run_code(
            "buat a = 5\nbuat b = 10\n"
            "a, b = b, a + b\ntulis a, b"
        )
        assert out == ["10 15"]

    def test_di_dalam_fungsi(self):
        out = run_code(
            "fungsi f()\n"
            "    buat p, q = 1, 2\n"
            "    p, q = q, p\n"
            "    kembali p, q\n"
            "selesai\n"
            "tulis f()"
        )
        # Multiple return value dicetak sebagai tuple-style
        assert out == ["(2, 1)"]

    def test_parser_menghasilkan_multi_assign_node(self):
        from brolang.ast.nodes import MultiAssignNode

        toks = Lexer("buat a, b = 1, 2").tokenize()
        ast = Parser(toks).parse()
        assert isinstance(ast.statements[0], MultiAssignNode)
        assert ast.statements[0].targets == ["a", "b"]
        assert ast.statements[0].is_declaration is True

    def test_konstanta_menolak_multiple(self):
        with pytest.raises(ParserError):
            run_code("konstanta a, b = 1, 2")


# ============= Switch Expression =============


class TestSwitchExpression:
    def test_literal_cases(self):
        out = run_code(
            "buat kode = 2\n"
            "buat nama = cocokkan kode { 1: \"satu\", 2: \"dua\", _: \"lainnya\" }\n"
            "tulis nama"
        )
        assert out == ["dua"]

    def test_default_case(self):
        out = run_code(
            "buat nama = cocokkan 99 { 1: \"satu\", _: \"lainnya\" }\n"
            "tulis nama"
        )
        assert out == ["lainnya"]

    def test_tanpa_default(self):
        out = run_code(
            "buat x = cocokkan 5 { 1: \"satu\" }\n"
            "tulis x"
        )
        assert out == ["None"]

    def test_binding_pattern(self):
        out = run_code(
            "buat data = { \"x\": 10, \"y\": 20 }\n"
            "buat hasil = cocokkan data {\n"
            "    { \"x\": a, \"y\": b }: a + b,\n"
            "    _: 0\n"
            "}\n"
            "tulis hasil"
        )
        assert out == ["30"]

    def test_bisa_jadi_argumen_fungsi(self):
        out = run_code(
            "fungsi label(k)\n"
            "    kembali cocokkan k { 1: \"satu\", _: \"lainnya\" }\n"
            "selesai\n"
            "tulis label(1), label(9)"
        )
        assert out == ["satu lainnya"]


# ============= Error Propagation '?' =============


class TestErrorPropagation:
    def test_benar_unwrap(self):
        out = run_code("tulis Benar(42)?")
        assert out == ["42"]

    def test_salah_melempar(self):
        out = run_code(
            "coba\n"
            "    buat x = Salah(\"gagal\")\n"
            "    tulis x?\n"
            "tangkap e\n"
            "    tulis \"tertangkap\"\n"
            "selesai"
        )
        assert out == ["tertangkap"]

    def test_ada_unwrap(self):
        out = run_code("tulis Ada(\"halo\")?")
        assert out == ["halo"]

    def test_kosong_melempar(self):
        out = run_code(
            "coba\n"
            "    buat y = Kosong()\n"
            "    tulis y?\n"
            "tangkap e\n"
            "    tulis \"tertangkap\"\n"
            "selesai"
        )
        assert out == ["tertangkap"]

    def test_nilai_biasa_noop(self):
        out = run_code("tulis 7?")
        assert out == ["7"]

    def test_rantai_pada_pemanggilan(self):
        out = run_code(
            "fungsi cari(id)\n"
            "    jika id == 1 maka\n"
            "        kembali Benar(\"ditemukan\")\n"
            "    lainnya\n"
            "        kembali Salah(\"tidak ada\")\n"
            "    selesai\n"
            "selesai\n"
            "tulis cari(1)?\n"
            "coba\n"
            "    tulis cari(2)?\n"
            "tangkap e\n"
            "    tulis \"error\"\n"
            "selesai"
        )
        assert out == ["ditemukan", "error"]

    def test_salah_dengan_exception(self):
        # Salah(Exception) -> exception dilempar langsung
        out = run_code(
            "coba\n"
            "    buat x = Salah(ZeroDivisionError_(\"bagi nol\"))\n"
            "    tulis x?\n"
            "tangkap e\n"
            "    tulis \"tertangkap\"\n"
            "selesai"
        )
        assert out == ["tertangkap"]


# ============= Async/Await Sejati =============


class TestAsyncAwaitSejati:
    def test_pemanggilan_mengembalikan_tugas(self):
        # Fungsi asinkron mengembalikan objek Tugas (bukan hasil langsung)
        from brolang.interpreter.interpreter import _AsyncTugas

        code = (
            "asinkron fungsi muat()\n"
            "    kembali \"data\"\n"
            "selesai\n"
        )
        toks = Lexer(code).tokenize()
        ast = Parser(toks).parse()
        interp = Interpreter()
        interp.interpret(ast)
        tugas = interp.current_env.functions["muat"]()
        assert isinstance(tugas, _AsyncTugas)
        assert tugas.hasil() == "data"

    def test_tunggu_memblokir_dan_mengambil_hasil(self):
        out = run_code(
            "asinkron fungsi muat(url)\n"
            "    kembali \"data dari \" + url\n"
            "selesai\n"
            "buat t = muat(\"api\")\n"
            "buat hasil = tunggu t\n"
            "tulis hasil"
        )
        assert out == ["data dari api"]

    def test_selesai_tanpa_memblokir(self):
        out = run_code(
            "asinkron fungsi lambat()\n"
            "    kembali 1\n"
            "selesai\n"
            "buat t = lambat()\n"
            "tulis t.selesai()\n"
            "buat r = tunggu t\n"
            "tulis r"
        )
        # selesai() bisa True/False tergantung timing; hasil harus benar
        assert out[-1] == "1"

    def test_event_loop_tunggu_semua(self):
        out = run_code(
            "impor event_loop\n"
            "asinkron fungsi kerja(n)\n"
            "    kembali n * 10\n"
            "selesai\n"
            "buat a = kerja(1)\n"
            "buat b = kerja(2)\n"
            "buat c = kerja(3)\n"
            "tulis event_loop.tunggu_semua([a, b, c])"
        )
        assert out == ["[10, 20, 30]"]

    def test_event_loop_tidur_overlap(self):
        import time

        mulai = time.monotonic()
        out = run_code(
            "impor event_loop\n"
            "asinkron fungsi tidur(lama)\n"
            "    event_loop.tidur(lama)\n"
            "    kembali \"ok\"\n"
            "selesai\n"
            "buat a = tidur(0.15)\n"
            "buat b = tidur(0.15)\n"
            "buat c = tidur(0.15)\n"
            "tulis event_loop.tunggu_semua([a, b, c])"
        )
        durasi = time.monotonic() - mulai
        assert out == ["['ok', 'ok', 'ok']"]
        # Tidur kooperatif: 3 task × 0.15s harus < 0.45s total
        assert durasi < 0.4, f"Task seharusnya overlap, tapi butuh {durasi:.2f}s"

    def test_nested_async_tanpa_deadlock(self):
        out = run_code(
            "asinkron fungsi tugas_dalam()\n"
            "    kembali \"dalam\"\n"
            "selesai\n"
            "asinkron fungsi luar()\n"
            "    buat d = tugas_dalam()\n"
            "    buat r = tunggu d\n"
            "    kembali \"luar + \" + r\n"
            "selesai\n"
            "buat t = luar()\n"
            "tulis tunggu t"
        )
        assert out == ["luar + dalam"]

    def test_task_error_ditangkap_saat_tunggu(self):
        out = run_code(
            "asinkron fungsi gagal()\n"
            "    lempar \"boom\"\n"
            "selesai\n"
            "coba\n"
            "    buat t = gagal()\n"
            "    buat r = tunggu t\n"
            "    tulis \"tidak jalan\"\n"
            "tangkap e\n"
            "    tulis \"tertangkap\"\n"
            "selesai"
        )
        assert out == ["tertangkap"]

    def test_event_loop_module_terdaftar(self):
        from brolang.stdlib import get_stdlib_module

        mod = get_stdlib_module("event_loop")
        for nama in ("tidur", "tunggu_semua", "tunggu_apa_saja", "jalankan"):
            assert hasattr(mod, nama)


# ============= Konsistensi Mesin =============


class TestKonsistensiMesin:
    def test_multi_assign_konsisten(self):
        code = (
            "buat a, b = 1, 2\n"
            "a, b = b, a\n"
            "tulis a, b\n"
        )
        assert run_transpiler(code) == run_code(code)
        assert run_vm(code) == run_code(code)

    def test_error_propagation_konsisten(self):
        code = (
            "tulis Benar(10)?\n"
            "tulis Ada(\"ada\")?\n"
            "coba\n"
            "    tulis Salah(\"gagal\")?\n"
            "tangkap e\n"
            "    tulis \"err\"\n"
            "selesai\n"
        )
        interp_out = run_code(code)
        assert interp_out == ["10", "ada", "err"]
        assert run_transpiler(code) == interp_out

    def test_error_propagation_vm_konsisten(self):
        code = (
            "buat a, b = 1, 2\n"
            "a, b = b, a\n"
            "tulis a, b\n"
            "tulis Benar(42)?\n"
            "coba\n"
            "    buat x = Salah(\"gagal\")\n"
            "    tulis x?\n"
            "tangkap e\n"
            "    tulis \"err\"\n"
            "selesai\n"
        )
        out = run_vm(code)
        # 3 baris terakhir: nilai multi-assign, unwrap, pesan catch
        assert "2 1" in out
        assert "42" in out
        assert any("err" in str(o) for o in out)

    def test_switch_expression_transpiler_konsisten(self):
        code = (
            "buat nama = cocokkan 2 { 1: \"satu\", 2: \"dua\", _: \"lainnya\" }\n"
            "tulis nama\n"
        )
        assert run_transpiler(code) == run_code(code)

    def test_switch_expression_binding_transpiler(self):
        code = (
            "buat data = { \"x\": 10, \"y\": 20 }\n"
            "buat hasil = cocokkan data {\n"
            "    { \"x\": a, \"y\": b }: a + b,\n"
            "    _: 0\n"
            "}\n"
            "tulis hasil\n"
        )
        assert run_transpiler(code) == run_code(code)


# ============= VM: switch expression, import, async (v7.0) =============


class TestVMSwitchExpression:
    def test_switch_expr_literal_vm(self):
        out = run_vm(
            "buat nama = cocokkan 2 { 1: \"satu\", 2: \"dua\", _: \"lainnya\" }\n"
            "tulis nama"
        )
        assert any("dua" in str(o) for o in out)

    def test_switch_expr_default_vm(self):
        out = run_vm(
            "buat x = cocokkan 99 { 1: \"satu\", _: \"lainnya\" }\n"
            "tulis x"
        )
        assert any("lainnya" in str(o) for o in out)

    def test_switch_expr_binding_vm(self):
        out = run_vm(
            "buat data = { \"x\": 10, \"y\": 20 }\n"
            "buat hasil = cocokkan data {\n"
            "    { \"x\": a, \"y\": b }: a + b,\n"
            "    _: 0\n"
            "}\n"
            "tulis hasil"
        )
        assert any("30" in str(o) for o in out)

    def test_switch_expr_inside_function_vm(self):
        out = run_vm(
            "fungsi label(k)\n"
            "    kembali cocokkan k { 1: \"satu\", _: \"lainnya\" }\n"
            "selesai\n"
            "tulis label(1), label(9)"
        )
        assert any("satu lainnya" in str(o) for o in out)

    def test_switch_expr_tanpa_default_vm(self):
        out = run_vm(
            "buat x = cocokkan 5 { 1: \"satu\" }\n"
            "tulis x"
        )
        assert any("None" in str(o) for o in out)


class TestVMErrorPropagationNoop:
    def test_nilai_biasa_noop_vm(self):
        # `7?` (nilai non-Result/Option) tidak boleh crash di VM
        out = run_vm("tulis 7?\ntulis \"halo\"?")
        assert any("7" in str(o) for o in out)
        assert any("halo" in str(o) for o in out)

    def test_ada_unwrap_vm(self):
        out = run_vm("tulis Ada(\"ada\")?")
        assert any("ada" in str(o) for o in out)


class TestVMImport:
    def test_impor_event_loop_vm(self):
        # `impor` di VM dulu crash (ImportNode.parts); kini berfungsi
        out = run_vm(
            "impor event_loop\n"
            "tulis event_loop.tunggu_semua([])"
        )
        assert any("[]" in str(o) for o in out)


class TestVMAsync:
    def test_async_function_mengembalikan_tugas_vm(self):
        out = run_vm(
            "asinkron fungsi muat()\n"
            "    kembali \"data\"\n"
            "selesai\n"
            "buat t = muat()\n"
            "tulis t.selesai()\n"
            "tulis tunggu t"
        )
        assert any("data" in str(o) for o in out)

    def test_async_tunggu_semua_vm(self):
        out = run_vm(
            "impor event_loop\n"
            "asinkron fungsi kerja(n)\n"
            "    kembali n * 10\n"
            "selesai\n"
            "buat a = kerja(1)\n"
            "buat b = kerja(2)\n"
            "tulis event_loop.tunggu_semua([a, b])"
        )
        assert any("10" in str(o) and "20" in str(o) for o in out)

    def test_async_error_task_ditangkap_vm(self):
        out = run_vm(
            "asinkron fungsi gagal()\n"
            "    lempar \"boom\"\n"
            "selesai\n"
            "coba\n"
            "    buat t = gagal()\n"
            "    buat r = tunggu t\n"
            "    tulis \"tidak jalan\"\n"
            "tangkap e\n"
            "    tulis \"tertangkap\"\n"
            "selesai"
        )
        assert any("tertangkap" in str(o) for o in out)


class TestTranspilerAsync:
    def test_async_tunggu_transpiler(self):
        code = (
            "asinkron fungsi muat(url)\n"
            "    kembali \"data dari \" + url\n"
            "selesai\n"
            "buat t = muat(\"api\")\n"
            "tulis tunggu t\n"
        )
        assert run_transpiler(code) == run_code(code)

    def test_async_selesai_transpiler(self):
        code = (
            "asinkron fungsi kerja(n)\n"
            "    kembali n * 10\n"
            "selesai\n"
            "buat a = kerja(1)\n"
            "buat b = kerja(2)\n"
            "tulis a.selesai()\n"
            "tulis event_loop.tunggu_semua([a, b]) jika benar\n"
        )
        # hanya pastikan tidak crash & hasil benar
        interp = run_code("impor event_loop\n" + code)
        transp = run_transpiler("impor event_loop\n" + code)
        assert transp == interp

    def test_async_error_transpiler(self):
        code = (
            "impor event_loop\n"
            "asinkron fungsi gagal()\n"
            "    lempar \"boom\"\n"
            "selesai\n"
            "coba\n"
            "    buat t = gagal()\n"
            "    buat r = tunggu t\n"
            "    tulis \"tidak jalan\"\n"
            "tangkap e\n"
            "    tulis \"tertangkap\"\n"
            "selesai"
        )
        assert run_transpiler(code) == run_code(code)

    def test_string_newline_transpiler(self):
        # Regresi lama: `\n` di string jadi newline literal di Python
        # (transpiler memisah output per baris, jadi gabungkan dulu)
        code = 'tulis "baris1\\nbaris2"'
        assert "\n".join(run_transpiler(code)) == run_code(code)[0]


# ============= Fix: pola enum di cocokkan (bug lama) =============


class TestMatchEnumPattern:
    def test_parser_menerima_pola_enum(self):
        from brolang.ast.nodes import MatchNode, ObjectAccessNode

        code = (
            "enum Warna { MERAH, BIRU, HIJAU }\n"
            "cocokkan warna {\n"
            "    Warna.MERAH: tulis \"panas\"\n"
            "    Warna.HIJAU: tulis \"sejuk\"\n"
            "    _: tulis \"lain\"\n"
            "}"
        )
        ast = Parser(Lexer(code).tokenize()).parse()
        match = next(s for s in ast.statements if isinstance(s, MatchNode))
        assert len(match.cases) == 2
        assert all(isinstance(p, ObjectAccessNode) for p, _ in match.cases)
        assert match.cases[0][0].property == "MERAH"

    def test_interpreter_cocokkan_enum(self):
        out = run_code(
            "enum Warna { MERAH, BIRU, HIJAU }\n"
            "buat warna = Warna.HIJAU\n"
            "cocokkan warna {\n"
            "    Warna.MERAH: tulis \"panas\"\n"
            "    Warna.HIJAU: tulis \"sejuk\"\n"
            "    _: tulis \"lain\"\n"
            "}"
        )
        assert out == ["sejuk"]

    def test_transpiler_cocokkan_enum(self):
        code = (
            "enum Warna { MERAH, BIRU, HIJAU }\n"
            "buat warna = Warna.HIJAU\n"
            "cocokkan warna {\n"
            "    Warna.MERAH: tulis \"panas\"\n"
            "    Warna.HIJAU: tulis \"sejuk\"\n"
            "    _: tulis \"lain\"\n"
            "}"
        )
        assert run_transpiler(code) == run_code(code)

    def test_vm_cocokkan_enum(self):
        out = run_vm(
            "enum Warna { MERAH, BIRU, HIJAU }\n"
            "buat warna = Warna.HIJAU\n"
            "cocokkan warna {\n"
            "    Warna.MERAH: tulis \"panas\"\n"
            "    Warna.HIJAU: tulis \"sejuk\"\n"
            "    _: tulis \"lain\"\n"
            "}"
        )
        assert any("sejuk" in str(o) for o in out)

    def test_vm_cocokkan_enum_default(self):
        out = run_vm(
            "enum Warna { MERAH, BIRU, HIJAU }\n"
            "buat warna = Warna.BIRU\n"
            "cocokkan warna {\n"
            "    Warna.MERAH: tulis \"panas\"\n"
            "    _: tulis \"lain\"\n"
            "}"
        )
        assert any("lain" in str(o) for o in out)

    def test_vm_cocokkan_enum_guard(self):
        out = run_vm(
            "enum Warna { MERAH, BIRU, HIJAU }\n"
            "buat warna = Warna.HIJAU\n"
            "cocokkan warna {\n"
            "    Warna.HIJAU jika benar: tulis \"hijau+guard\"\n"
            "    _: tulis \"lain\"\n"
            "}"
        )
        assert any("hijau+guard" in str(o) for o in out)

    def test_vm_struct_dan_enum(self):
        # Enum + struct + match kombinasi (dulu struct crash di VM:
        # StructNode tidak punya atribut `methods`)
        out = run_vm(
            "enum Aksi { SERANG, BERTAHAN }\n"
            "struktur Entity { nama, hp, aksi }\n"
            "buat musuh = Entity(\"Goblin\", 50, Aksi.SERANG)\n"
            "cocokkan musuh.aksi {\n"
            "    Aksi.SERANG: tulis musuh.nama + \" menyerang!\"\n"
            "    _: tulis \"bertahan\"\n"
            "}\n"
            "tulis musuh"
        )
        assert any("Goblin menyerang" in str(o) for o in out)
        assert any("Entity" in str(o) for o in out)

    def test_vm_switch_expr_pola_enum(self):
        # Switch expression dengan pola enum (v7.0) di VM
        out = run_vm(
            "enum Warna { MERAH, BIRU, HIJAU }\n"
            "buat w = Warna.HIJAU\n"
            "buat label = cocokkan w { Warna.MERAH: \"panas\", Warna.HIJAU: \"sejuk\", _: \"lain\" }\n"
            "tulis label"
        )
        assert any("sejuk" in str(o) for o in out)

    def test_vm_match_pola_terstruktur_dan_guard(self):
        out = run_vm(
            "cocokkan [1, 2] {\n"
            "    [a, b]: tulis a + b\n"
            "    _: tulis 0\n"
            "}"
        )
        assert any("3" in str(o) for o in out)


# ============= VM: try/catch (perbaikan v7.0) =============


class TestVMTryCatch:
    def test_lempar_tangkap_vm(self):
        out = run_vm(
            "coba\n"
            "    lempar \"boom\"\n"
            "    tulis \"tidak jalan\"\n"
            "tangkap e\n"
            "    tulis \"tertangkap\"\n"
            "selesai\n"
            "tulis \"selesai\""
        )
        assert any("tertangkap" in str(o) for o in out)
        assert any("selesai" in str(o) for o in out)

    def test_kecuali_typed_vm(self):
        out = run_vm(
            "coba\n"
            "    lempar \"boom\"\n"
            "kecuali RuntimeError_ sebagai e\n"
            "    tulis \"err\"\n"
            "selesai\n"
            "tulis \"aman\""
        )
        assert any("err" in str(o) for o in out)
        assert any("aman" in str(o) for o in out)

    def test_kecuali_tidak_cocok_re_raise(self):
        from brolang.exceptions import RuntimeError_ as RTE

        with pytest.raises(RTE):
            run_vm(
                "coba\n"
                "    lempar \"boom\"\n"
                "kecuali TypeError_ sebagai e\n"
                "    tulis \"tidak cocok\"\n"
                "selesai"
            )
