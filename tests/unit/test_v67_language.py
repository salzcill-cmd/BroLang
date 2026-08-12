"""
Unit tests untuk BroLang v6.7
=============================

Tests untuk:
- Spread & Rest Parameter (fungsi f(a, ...sisa), f(...args), [...a, 1])
- Multiple Return (kembali a, b + destructuring)
- Perbaikan VM: range-for, destructuring, pipeline di bytecode VM
- Game dev: Guncangan (screen shake) + synth audio (nada/laser/ledakan)
"""

import io
import struct
import wave

import pytest

from brolang.lexer import Lexer
from brolang.parser import Parser
from brolang.interpreter import Interpreter
from brolang.exceptions import RuntimeError_, TypeError_


def run_code(code):
    """Helper untuk menjalankan kode BroLang lewat interpreter."""
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    interp = Interpreter()
    interp.interpret(ast)
    return interp.output


def _mod(nama):
    """Ambil modul stdlib BroLang."""
    from brolang.stdlib import get_stdlib_module
    return get_stdlib_module(nama)


# ============= Lexer: Token Spread =============


class TestLexerSpread:
    """Token `...` (spread) harus dikenali lexer."""

    def test_ellipsis_token(self):
        from brolang.token_types import TokenType
        tokens = Lexer("f(...a)").tokenize()
        types = [t.type for t in tokens]
        assert TokenType.TOKEN_ELLIPSIS in types

    def test_dot_still_works(self):
        tokens = Lexer("objek.atribut").tokenize()
        types = [t.type for t in tokens]
        from brolang.token_types import TokenType
        assert TokenType.TOKEN_DOT in types
        assert TokenType.TOKEN_ELLIPSIS not in types

    def test_number_decimal_still_works(self):
        tokens = Lexer("3.14").tokenize()
        types = [t.type for t in tokens]
        from brolang.token_types import TokenType
        assert TokenType.TOKEN_DECIMAL in types
        assert TokenType.TOKEN_ELLIPSIS not in types


# ============= Rest Parameter =============


class TestRestParameter:
    """fungsi f(a, ...sisa) — tangkap semua argumen tambahan sebagai list."""

    def test_rest_basic(self):
        code = '''
fungsi jumlahkan(...angka)
    buat total = 0
    untuk setiap n dalam angka lakukan
        total = total + n
    selesai
    kembali total
selesai
tulis jumlahkan(1, 2, 3, 4, 5)
'''
        output = run_code(code)
        assert "15" in output[0]

    def test_rest_kosong(self):
        code = '''
fungsi hitung(...angka)
    kembali panjang(angka)
selesai
tulis hitung()
'''
        output = run_code(code)
        assert "0" in output[0]

    def test_rest_setelah_param_biasa(self):
        code = '''
fungsi sapa(nama, ...sisa)
    kembali nama + " " + teks(sisa)
selesai
tulis sapa("Budi", "Ani", "Citra")
'''
        output = run_code(code)
        assert "Budi ['Ani', 'Citra']" in output[0]

    def test_rest_di_lambda(self):
        code = '''
buat gabung = lalu(...s) teks(s)
tulis gabung(1, 2, 3)
'''
        output = run_code(code)
        assert "[1, 2, 3]" in output[0]

    def test_rest_di_method(self):
        code = '''
kelas Kalkulator
    fungsi __init__(self)
        self.total = 0
    selesai
    fungsi tambah_semua(self, ...angka)
        untuk setiap n dalam angka lakukan
            self.total = self.total + n
        selesai
        kembali self.total
    selesai
selesai
buat k = Kalkulator()
tulis k.tambah_semua(1, 2, 3, 4)
'''
        output = run_code(code)
        assert "10" in output[0]

    def test_rest_hanya_boleh_satu(self):
        from brolang.exceptions import ParserError
        code = '''
fungsi f(...a, ...b)
    kembali a
selesai
'''
        with pytest.raises(ParserError):
            run_code(code)


# ============= Spread Call =============


class TestSpreadCall:
    """f(...daftar) — unpack list jadi argumen posisi."""

    def test_spread_call_basic(self):
        code = '''
fungsi kali3(a, b, c)
    kembali a * b * c
selesai
buat nilai = [2, 3, 4]
tulis kali3(...nilai)
'''
        output = run_code(code)
        assert "24" in output[0]

    def test_spread_call_dicampur(self):
        code = '''
fungsi gabung(a, b, c)
    kembali a + b + c
selesai
buat depan = [1, 2]
tulis gabung(...depan, 3)
'''
        output = run_code(code)
        assert "6" in output[0]

    def test_spread_call_ke_method(self):
        code = '''
kelas Penjumlah
    fungsi __init__(self)
        self.total = 0
    selesai
    fungsi tambah(self, a, b, c)
        kembali a + b + c
    selesai
selesai
buat p = Penjumlah()
buat arr = [10, 20, 30]
tulis p.tambah(...arr)
'''
        output = run_code(code)
        assert "60" in output[0]

    def test_spread_call_builtin(self):
        code = '''
buat arr = [3, 1, 2]
tulis max(...arr)
'''
        output = run_code(code)
        assert "3" in output[0]


# ============= Spread List =============


class TestSpreadList:
    """[...a, 1, 2] — gabungkan list."""

    def test_spread_list_basic(self):
        code = '''
buat dasar = [1, 2]
buat gabung = [...dasar, 3, 4]
tulis gabung
'''
        output = run_code(code)
        assert "[1, 2, 3, 4]" in output[0]

    def test_spread_list_multiple(self):
        code = '''
buat a = [1]
buat b = [2, 3]
buat c = [...a, ...b, 4]
tulis c
'''
        output = run_code(code)
        assert "[1, 2, 3, 4]" in output[0]

    def test_spread_list_di_tengah(self):
        code = '''
buat tengah = [20, 30]
buat hasil = [10, ...tengah, 40]
tulis hasil
'''
        output = run_code(code)
        assert "[10, 20, 30, 40]" in output[0]

    def test_spread_non_iterable_error(self):
        code = '''
buat x = 5
buat y = [...x, 1]
'''
        with pytest.raises(TypeError_):
            run_code(code)


# ============= Multiple Return =============


class TestMultipleReturn:
    """kembali a, b — fungsi mengembalikan beberapa nilai sekaligus."""

    def test_multiple_return_basic(self):
        code = '''
fungsi bagi_dan_sisa(a, b)
    kembali a / b, a % b
selesai
buat [hasil_bagi, sisa] = bagi_dan_sisa(17, 5)
tulis hasil_bagi, sisa
'''
        output = run_code(code)
        assert "3.4 2" in output[0]

    def test_multiple_return_tiga_nilai(self):
        code = '''
fungsi tiga()
    kembali 1, 2, 3
selesai
buat [a, b, c] = tiga()
tulis a + b + c
'''
        output = run_code(code)
        assert "6" in output[0]

    def test_multiple_return_dengan_tuple(self):
        code = '''
fungsi posisi()
    kembali 100, 200
selesai
buat (x, y) = posisi()
tulis x + y
'''
        output = run_code(code)
        assert "300" in output[0]


# ============= Full Pipeline (bro run jalur) =============


class TestFullPipelineV67:
    """Fitur v6.7 harus jalan lewat SemanticAnalyzer + Optimizer + Transpiler."""

    def _run_full(self, code):
        from brolang.semantic import SemanticAnalyzer
        from brolang.optimizer import Optimizer
        from brolang.vm.transpiler import Transpiler

        ast = Parser(Lexer(code).tokenize()).parse()
        analyzer = SemanticAnalyzer()
        assert analyzer.analyze(ast), [str(e) for e in analyzer.errors]
        optimized = Optimizer().optimize(ast)
        py_code = Transpiler().transpile(optimized)
        from contextlib import redirect_stdout

        buf = io.StringIO()
        with redirect_stdout(buf):
            exec(compile(py_code, "<test>", "exec"), {"__builtins__": __builtins__})
        return buf.getvalue().strip().splitlines()

    def test_rest_parameter_through_full_pipeline(self):
        code = '''
fungsi jumlahkan(...angka)
    buat total = 0
    untuk setiap n dalam angka lakukan
        total = total + n
    selesai
    kembali total
selesai
tulis jumlahkan(1, 2, 3)
'''
        out = self._run_full(code)
        assert out[0] == "6", out

    def test_spread_call_through_full_pipeline(self):
        code = '''
fungsi kali3(a, b, c)
    kembali a * b * c
selesai
buat nilai = [2, 3, 4]
tulis kali3(...nilai)
'''
        out = self._run_full(code)
        assert out[0] == "24", out

    def test_spread_list_through_full_pipeline(self):
        code = '''
buat dasar = [1, 2]
buat gabung = [...dasar, 3, 4]
tulis gabung
'''
        out = self._run_full(code)
        assert out[0] == "[1, 2, 3, 4]", out

    def test_multiple_return_through_full_pipeline(self):
        code = '''
fungsi bagi_dan_sisa(a, b)
    kembali a / b, a % b
selesai
buat [q, r] = bagi_dan_sisa(17, 5)
tulis q, r
'''
        out = self._run_full(code)
        assert "3.4 2" in out[0], out

    def test_konsistensi_interpreter_vs_transpiler(self):
        """Output interpreter & transpiler harus identik untuk fitur v6.7."""
        code = '''
fungsi jumlahkan(...angka)
    buat total = 0
    untuk setiap n dalam angka lakukan
        total = total + n
    selesai
    kembali total
selesai
buat dasar = [1, 2]
tulis jumlahkan(...dasar, 3, 4)
tulis [...dasar, 99]
fungsi pasangan()
    kembali "a", "b"
selesai
buat [x, y] = pasangan()
tulis x + y
'''
        interp_out = run_code(code)
        interp_out = [o for o in interp_out if o.strip()]
        transp_out = self._run_full(code)
        assert interp_out == transp_out, f"interp={interp_out} transp={transp_out}"

    def test_rest_param_list_konsisten(self):
        """Rest param harus list di kedua mesin (bukan tuple Python)."""
        code = '''
fungsi sapa(nama, ...sisa)
    tulis sisa
selesai
sapa("Budi", "Ani", "Citra")
sapa("Budi")
'''
        interp_out = run_code(code)
        transp_out = self._run_full(code)
        assert interp_out == transp_out, f"interp={interp_out} transp={transp_out}"
        assert "['Ani', 'Citra']" in transp_out[0]
        assert "[]" in transp_out[1]

    def test_lambda_rest_konsisten(self):
        """Lambda dengan rest param harus list di kedua mesin."""
        code = '''
tulis (lalu(...s) s)(1, 2, 3)
'''
        interp_out = run_code(code)
        transp_out = self._run_full(code)
        assert interp_out == transp_out, f"interp={interp_out} transp={transp_out}"
        assert "[1, 2, 3]" in transp_out[0]

    def test_method_rest_param_konsisten(self):
        """Method dengan rest param harus list di interpreter & transpiler."""
        code = '''
kelas Kalkulator
    fungsi __init__(self)
        self.total = 0
    selesai
    fungsi tambah_semua(self, ...angka)
        untuk setiap n dalam angka lakukan
            self.total = self.total + n
        selesai
        kembali self.total
    selesai
selesai
buat k = Kalkulator()
tulis k.tambah_semua(1, 2, 3, 4)
'''
        interp_out = run_code(code)
        transp_out = self._run_full(code)
        assert interp_out == transp_out, f"interp={interp_out} transp={transp_out}"
        assert "10" in transp_out[0]

    def test_lambda_rest_body_falsy(self):
        """Body lambda rest yang falsy (0) tetap dikembalikan (regresi
        walrus `or` yang menelan nilai falsy)."""
        code = '''
tulis (lalu(...s) 0)(1, 2)
'''
        interp_out = run_code(code)
        transp_out = self._run_full(code)
        assert interp_out == transp_out, f"interp={interp_out} transp={transp_out}"
        assert "0" in transp_out[0]

    def test_static_method_rest_konsisten(self):
        """Static method dengan HANYA rest param (tanpa params biasa)
        harus valid di transpiler (regresi `def f(, *rest)` SyntaxError)."""
        code = '''
kelas Gabung
    statis fungsi satukan(...s)
        kembali s
    selesai
selesai
tulis Gabung.satukan(1, 2, 3)
'''
        interp_out = run_code(code)
        transp_out = self._run_full(code)
        assert interp_out == transp_out, f"interp={interp_out} transp={transp_out}"
        assert "[1, 2, 3]" in transp_out[0]

    def test_decorated_function_rest_konsisten(self):
        """Rest param pada fungsi berdekorator harus ikut di-transpile
        (regresi: rest param diam-diam dibuang oleh _emit_decorated_function)."""
        code = '''
fungsi dekorasi(f)
    kembali f
selesai

@dekorasi
fungsi jumlahkan(...angka)
    buat total = 0
    untuk setiap n dalam angka lakukan
        total = total + n
    selesai
    kembali total
selesai

tulis jumlahkan(1, 2, 3, 4)
'''
        interp_out = run_code(code)
        transp_out = self._run_full(code)
        assert interp_out == transp_out, f"interp={interp_out} transp={transp_out}"
        assert "10" in transp_out[0]


# ============= VM (Bytecode) v6.7 =============


class TestVMV67:
    """Fitur yang sebelumnya NotImplementedError kini berfungsi di VM."""

    def _run_vm(self, code):
        from brolang.vm.compiler import Compiler
        from brolang.vm.vm import VM

        ast = Parser(Lexer(code).tokenize()).parse()
        bytecode = Compiler().compile(ast)
        vm = VM()
        vm.run(bytecode)
        return vm.output

    def test_vm_range_for(self):
        code = '''
buat total = 0
untuk i dari 1 sampai 5 lakukan
    total = total + i
selesai
tulis total
'''
        out = self._run_vm(code)
        assert out == ["15"], out

    def test_vm_range_for_langkah(self):
        code = '''
untuk i dari 0 sampai 10 langkah 2 lakukan
    tulis i
selesai
'''
        out = self._run_vm(code)
        assert out == ["0", "2", "4", "6", "8", "10"], out

    def test_vm_range_for_turun(self):
        code = '''
untuk i dari 3 sampai 1 lakukan
    tulis i
selesai
'''
        out = self._run_vm(code)
        assert out == ["3", "2", "1"], out

    def test_vm_destructuring(self):
        code = '''
buat [a, b, c] = [1, 2, 3]
tulis a + b + c
buat {x, y} = {"x": 10, "y": 20}
tulis x + y
'''
        out = self._run_vm(code)
        assert out == ["6", "30"], out

    def test_vm_destructuring_object_missing_key(self):
        code = '''
buat {x, y} = {"x": 7}
tulis x, y
'''
        out = self._run_vm(code)
        assert out == ["7 None"], out

    def test_vm_pipeline(self):
        code = '''
fungsi kali2(x)
    kembali x * 2
selesai
tulis 21 |> kali2
tulis 5 |> lalu(x) x * 10
'''
        out = self._run_vm(code)
        assert out == ["42", "50"], out

    def test_vm_spread_list(self):
        code = '''
buat dasar = [1, 2]
buat gabung = [...dasar, 3]
tulis gabung
'''
        out = self._run_vm(code)
        assert out == ["[1, 2, 3]"], out

    def test_vm_rest_parameter(self):
        code = '''
fungsi jumlahkan(...angka)
    buat total = 0
    untuk setiap n dalam angka lakukan
        total = total + n
    selesai
    kembali total
selesai
tulis jumlahkan(1, 2, 3, 4)
'''
        out = self._run_vm(code)
        assert out == ["10"], out

    def test_vm_rest_setelah_param_biasa(self):
        code = '''
fungsi sapa(nama, ...sisa)
    kembali nama + " " + teks(sisa)
selesai
tulis sapa("Budi", "Ani", "Citra")
'''
        out = self._run_vm(code)
        assert out == ["Budi ['Ani', 'Citra']"], out

    def test_vm_spread_call(self):
        code = '''
fungsi kali3(a, b, c)
    kembali a * b * c
selesai
buat nilai = [2, 3, 4]
tulis kali3(...nilai)
'''
        out = self._run_vm(code)
        assert out == ["24"], out

    def test_vm_for_each_index(self):
        code = '''
buat hasil = 0
untuk setiap n, i dalam [10, 20, 30] lakukan
    hasil = hasil + n + i
selesai
tulis hasil
'''
        out = self._run_vm(code)
        # (10+0) + (20+1) + (30+2) = 63
        assert out == ["63"], out

    def test_vm_method_rest_param(self):
        """Method non-static dengan self eksplisit + rest param (regresi
        off-by-one rest_pos saat `self` ditulis di daftar parameter)."""
        code = '''
kelas Kalkulator
    fungsi __init__(self)
        self.total = 0
    selesai
    fungsi tambah_semua(self, ...angka)
        untuk setiap n dalam angka lakukan
            self.total = self.total + n
        selesai
        kembali self.total
    selesai
selesai
buat k = Kalkulator()
tulis k.tambah_semua(1, 2, 3, 4)
'''
        out = self._run_vm(code)
        assert out == ["10"], out

    def test_vm_multiple_return(self):
        code = '''
fungsi bagi_dan_sisa(a, b)
    kembali a / b, a % b
selesai
buat [q, r] = bagi_dan_sisa(17, 5)
tulis q, r
'''
        out = self._run_vm(code)
        assert out == ["3.4 2"], out

    def test_vm_range_for_step_nol_error(self):
        """langkah 0 harus error ramah di VM (konsisten dengan
        interpreter & transpiler yang melempar 'Langkah range tidak
        boleh nol')."""
        from brolang.exceptions import RuntimeError_

        code = '''
untuk i dari 1 sampai 5 langkah 0 lakukan
    tulis i
selesai
'''
        with pytest.raises(RuntimeError_, match="tidak boleh nol"):
            self._run_vm(code)


# ============= Game Dev: Guncangan (Screen Shake) =============


class TestGuncangan:
    """Screen shake berbasis trauma — testable tanpa pygame."""

    def test_guncang_menambah_trauma(self):
        efek = _mod("efek")
        g = efek.Guncangan()
        assert g.selesai()
        g.guncang(0.5)
        assert not g.selesai()
        assert 0.4 <= g.kekuatan_sekarang() <= 0.5

    def test_trauma_menumpuk_tapi_capped(self):
        efek = _mod("efek")
        g = efek.Guncangan()
        g.guncang(0.8)
        g.guncang(0.8)
        g.guncang(0.8)
        assert g.kekuatan_sekarang() <= 1.0

    def test_trauma_memudar(self):
        efek = _mod("efek")
        g = efek.Guncangan(peluruhan=2.0)
        g.guncang(1.0)
        awal = g.kekuatan_sekarang()
        g.update(0.25)
        assert g.kekuatan_sekarang() < awal

    def test_offset_nol_saat_reda(self):
        efek = _mod("efek")
        g = efek.Guncangan()
        assert g.offset() == (0.0, 0.0)

    def test_offset_besar_saat_guncang_keras(self):
        efek = _mod("efek")
        g = efek.Guncangan(kekuatan_maks=20)
        g.guncang(1.0)
        ox, oy = g.offset()
        assert ox != 0.0 or oy != 0.0
        assert abs(ox) <= 20.0 and abs(oy) <= 20.0

    def test_reda_setelah_update_lama(self):
        efek = _mod("efek")
        g = efek.Guncangan(peluruhan=3.0, durasi=1.0)
        g.guncang(1.0)
        for _ in range(120):  # 2 detik @ 60fps
            if not g.update(1 / 60):
                break
        assert g.selesai()

    def test_buat_guncangan_helper(self):
        efek = _mod("efek")
        g = efek.buat_guncangan(kekuatan_maks=12)
        assert type(g).__name__ == "Guncangan"


# ============= Game Dev: Synth Audio =============


class TestSynthAudio:
    """Efek suara prosedural — WAV valid tanpa file eksternal."""

    def test_nada_menghasilkan_wav_valid(self):
        audio = _mod("audio")
        wav = audio.nada(440, 0.2)
        assert wav[:4] == b"RIFF"
        assert wav[8:12] == b"WAVE"

    def test_nada_durasi_benar(self):
        audio = _mod("audio")
        wav = audio.nada(440, 0.2)
        w = wave.open(io.BytesIO(wav))
        assert w.getnchannels() == 1
        assert w.getframerate() == 22050
        assert w.getnframes() == int(0.2 * 22050)

    def test_laser_ledakan_blip(self):
        audio = _mod("audio")
        for nama in ("laser", "ledakan", "blip"):
            wav = getattr(audio, nama)()
            assert wav[:4] == b"RIFF", nama
            assert len(wav) > 500, nama

    def test_nada_gelombang_berbeda(self):
        audio = _mod("audio")
        for gel in ("sinus", "kotak", "segitiga", "gergaji"):
            wav = audio.nada(300, 0.05, gelombang=gel)
            assert wav[:4] == b"RIFF", gel

    def test_ledakan_deterministik(self):
        audio = _mod("audio")
        assert audio.ledakan() == audio.ledakan()

    def test_simpan_wav(self, tmp_path):
        audio = _mod("audio")
        path = tmp_path / "sfx.wav"
        audio.simpan_wav(audio.blip(), str(path))
        assert path.exists()
        w = wave.open(str(path))
        assert w.getnframes() > 0

    def test_wav_bisa_di_load_wave_module(self):
        audio = _mod("audio")
        wav = audio.laser()
        w = wave.open(io.BytesIO(wav))
        # Semua frame harus bisa dibaca tanpa error
        frame_count = w.getnframes()
        assert frame_count > 0
        data = w.readframes(frame_count)
        assert len(data) == frame_count * 2
