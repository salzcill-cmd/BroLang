"""Audit konsistensi lintas mesin: interpreter, transpiler, VM.

Menjalankan setiap snippet BroLang di ketiga mesin dan membandingkan
output stdout. Mismatch dicetak agar bisa dianalisis.
"""
import io
import contextlib
import sys
import traceback

from brolang.lexer.lexer import Lexer
from brolang.parser.parser import Parser
from brolang.interpreter.interpreter import Interpreter
from brolang.vm.transpiler import Transpiler
from brolang.vm.compiler import Compiler
from brolang.vm.vm import VM


def run_engine(kode, engine):
    try:
        ast = Parser(Lexer(kode).tokenize()).parse()
    except Exception as e:
        return ("PARSE_ERR", type(e).__name__ + ": " + str(e)[:100])
    buf = io.StringIO()
    try:
        if engine == "interp":
            interp = Interpreter()
            interp.interpret(ast)
            return ("OK", "\n".join(str(x) for x in interp.output))
        elif engine == "transpiler":
            tp = Transpiler()
            py = tp.transpile(ast)
            code = compile(py, "<bro>", "exec")
            with contextlib.redirect_stdout(buf):
                exec(code, {"__builtins__": __builtins__, "__name__": "__main__"})
        elif engine == "vm":
            vm = VM()
            vm.run(Compiler().compile(ast))
            return ("OK", "\n".join(str(x) for x in vm.output))
        else:
            raise ValueError(engine)
        return ("OK", buf.getvalue())
    except Exception as e:
        return ("ERR", type(e).__name__ + ": " + str(e)[:120].replace("\n", " "))


SNIPPETS = {
    # ---------- aritmatika & operator ----------
    "aritmatika_dasar": "tulis 1 + 2 * 3\ntulis (1 + 2) * 3\ntulis 7 / 2\ntulis 7 // 2\ntulis 2 ** 10\ntulis 17 % 5\n",
    "aritmatika_negatif": "tulis -17 // 5\ntulis -17 % 5\ntulis 2 ** -1\n",
    "augmented_assign": "buat x = 10\nx += 5\nx *= 2\nx //= 3\nx %= 4\ntulis x\n",
    "float_precision": "tulis 0.1 + 0.2\ntulis 1 / 3\n",

    # ---------- string ----------
    "string_operasi": 'impor teks\nbuat s = "halo"\ntulis s + " dunia"\ntulis s * 3\ntulis teks.panjang(s)\n',
    "string_methods": 'impor teks\nbuat s = "Halo Dunia"\ntulis teks.upper(s)\ntulis teks.lower(s)\ntulis teks.ganti(s, "Dunia", "Bro")\ntulis teks.potong("a,b,c", ",")\n',
    "fstring": 'buat nama = "Budi"\nbuat umur = 25\ntulis f"Nama: {nama}, umur: {umur}"\n',
    "string_index": 'buat s = "abcd"\ntulis s[0]\ntulis s[1:3]\ntulis s[-1]\n',

    # ---------- list ----------
    "list_basic": "buat a = [1, 2, 3]\na.tambah(4)\ntulis a\ntulis a[0]\ntulis panjang(a)\n",
    "list_ops": "buat a = [3, 1, 2]\ntulis a.urutkan()\ntulis a\n",
    "list_comprehension": "tulis [x * 2 lalu x dalam [1, 2, 3]]\n",
    "list_slicing": "buat a = [0, 1, 2, 3, 4]\ntulis a[1:3]\ntulis a[:2]\ntulis a[::2]\n",
    "list_neg_index": "buat a = [10, 20, 30]\ntulis a[-1]\ntulis a[-2]\n",

    # ---------- dict ----------
    "dict_basic": 'buat d = {"a": 1, "b": 2}\ntulis d["a"]\nd["c"] = 3\ntulis d\ntulis panjang(d)\n',
    "dict_methods": 'buat d = {"a": 1, "b": 2}\ntulis d.kunci()\ntulis d.nilai()\ntulis d.punya("a")\n',

    # ---------- kontrol alur ----------
    "if_elif_else": "buat x = 5\njika x > 10 maka\n    tulis \"besar\"\natau jika x > 3 maka\n    tulis \"sedang\"\nselain itu\n    tulis \"kecil\"\nselesai\n",
    "ternary": "buat x = 5\ntulis \"genap\" jika x % 2 == 0 lainnya \"ganjil\"\n",
    "while_loop": "buat i = 0\nselama i < 5 lakukan\n    tulis i\n    i += 1\nselesai\n",
    "range_for": "untuk i dari 1 sampai 5 lakukan\n    tulis i\nselesai\n",
    "range_for_step": "untuk i dari 0 sampai 10 langkah 2 lakukan\n    tulis i\nselesai\n",
    "foreach": "untuk x dalam [10, 20, 30] lakukan\n    tulis x\nselesai\n",
    "do_until": "buat i = 0\nulangi\n    tulis i\n    i += 1\nsampai i >= 3\n",
    "break_continue": "untuk i dari 1 sampai 10 lakukan\n    jika i == 3 maka\n        lanjutkan\n    selesai\n    jika i == 7 maka\n        hentikan\n    selesai\n    tulis i\nselesai\n",

    # ---------- fungsi ----------
    "fungsi_basic": "fungsi tambah(a, b)\n    kembali a + b\nselesai\ntulis tambah(2, 3)\n",
    "fungsi_default": "fungsi sapa(nama, sapaan = \"Halo\")\n    kembali sapaan + \" \" + nama\nselesai\ntulis sapa(\"Budi\")\ntulis sapa(\"Budi\", \"Hi\")\n",
    "fungsi_kwargs": "fungsi f(a, b, c)\n    kembali a + b + c\nselesai\ntulis f(1, 2, 3)\n",
    "fungsi_rekursif": "fungsi faktorial(n)\n    jika n <= 1 maka\n        kembali 1\n    selesai\n    kembali n * faktorial(n - 1)\nselesai\ntulis faktorial(5)\n",
    "multiple_return": "fungsi f()\n    kembali 1, 2, 3\nselesai\nbuat a, b, c = f()\ntulis a, b, c\n",
    "rest_param": "fungsi f(...args)\n    kembali panjang(args)\nselesai\ntulis f(1, 2, 3)\n",
    "closure": "fungsi buat_penambah(n)\n    fungsi tambah(x)\n        kembali x + n\n    selesai\n    kembali tambah\nselesai\nbuat tambah5 = buat_penambah(5)\ntulis tambah5(10)\n",
    "lambda": "buat ganda = lalu(x) x * 2\ntulis ganda(21)\n",
    "guard_return": "fungsi f(x)\n    kembali 1 jika x > 0\n    kembali 0\nselesai\ntulis f(5)\ntulis f(-5)\n",
    "recursion_fib": "fungsi fib(n)\n    jika n < 2 maka\n        kembali n\n    selesai\n    kembali fib(n - 1) + fib(n - 2)\nselesai\ntulis fib(10)\n",

    # ---------- kelas & OOP ----------
    "kelas_basic": "kelas Titik\n    fungsi __init__(self, x, y)\n        self.x = x\n        self.y = y\n    selesai\n    fungsi jumlah(self)\n        kembali self.x + self.y\n    selesai\nselesai\nbuat t = Titik(3, 4)\ntulis t.x\ntulis t.jumlah()\n",
    "kelas_inherit": "kelas A\n    fungsi halo(self)\n        kembali \"A\"\n    selesai\nselesai\nkelas B dari A\n    fungsi halo(self)\n        kembali \"B\"\n    selesai\nselesai\nbuat b = B()\ntulis b.halo()\n",
    "kelas_static": "kelas K\n    fungsi statis buat()\n        kembali 42\n    selesai\nselesai\ntulis K.buat()\n",
    "property": "kelas K\n    fungsi __init__(self)\n        self._x = 5\n    selesai\n    fungsi x(self)\n        kembali self._x\n    selesai\nselesai\nbuat k = K()\ntulis k.x\n",

    # ---------- error handling ----------
    "try_except": "coba\n    lempar \"boom\"\ntangkap e\n    tulis \"tertangkap:\", e\nselesai\n",
    "try_typed": "kelas MyErr\n    fungsi __init__(self, m)\n        self.pesan = m\n    selesai\nselesai\ncoba\n    lempar MyErr(\"gagal\")\ntangkap MyErr e\n    tulis \"typed:\", e.pesan\ntangkap e\n    tulis \"lain\"\nselesai\n",
    "try_finally": "coba\n    tulis \"coba\"\nakhirnya\n    tulis \"akhirnya\"\nselesai\n",

    # ---------- destructuring ----------
    "destructure_list": "buat [a, b] = [1, 2]\ntulis a, b\n",
    "destructure_obj": 'buat {x, y} = {"x": 1, "y": 2}\ntulis x, y\n',

    # ---------- walrus ----------
    "walrus": "buat r = (x := 10) + 5\ntulis r\ntulis x\n",

    # ---------- generator ----------
    "generator": "fungsi gen(n)\n    untuk i dari 1 sampai n lakukan\n        hasilkan i\n    selesai\nselesai\ntulis gen(3)\n",
    "yield_from": "fungsi a()\n    hasilkan 1\n    hasilkan 2\nselesai\nfungsi b()\n    hasilkandari a()\n    hasilkan 3\nselesai\ntulis b()\n",

    # ---------- multiple assignment & swap ----------
    "multi_assign": "buat a, b = 1, 2\na, b = b, a\ntulis a, b\n",
    "multi_assign_short": "buat x, y, z = 1, 2, 3\ntulis x, y, z\n",

    # ---------- switch ----------
    "switch_stmt": "buat x = 2\ncocokkan x\n    1: tulis \"satu\"\n    2: tulis \"dua\"\n    _: tulis \"lain\"\nselesai\n",
    "switch_expr": "buat x = 2\nbuat s = cocokkan x {\n    1: \"satu\",\n    2: \"dua\",\n    _: \"lain\"\n}\ntulis s\n",

    # ---------- error propagation ----------
    "error_prop_ok": "fungsi cari(id)\n    kembali Benar(\"data\")\nselesai\ntulis cari(1)?\n",
    "option": "buat a = Ada(5)\ntulis a?\n",

    # ---------- null-safe ----------
    "null_safe_attr": 'buat o = kosong\ntulis o?.nama\ntulis o?.nama ?? "default"\n',
    "null_safe_index": "buat a = kosong\ntulis a?[0]\ntulis a?[0] ?? \"x\"\n",

    # ---------- dictionary literals ----------
    "dict_literal_var_key": "buat k = \"nama\"\nbuat d = {k: \"Budi\"}\ntulis d\n",

    # ---------- set ----------
    "set_literal": "tulis {1, 2, 2, 3}\n",
    "set_comp": "tulis {x * 2 lalu x dalam [1, 2, 2, 3]}\n",

    # ---------- pipeline ----------
    "pipeline": "tulis 5 |> lalu(x) x * 2 |> lalu(y) y + 1\n",

    # ---------- spread ----------
    "spread_call": "fungsi f(a, b, c)\n    kembali a + b + c\nselesai\nbuat args = [1, 2, 3]\ntulis f(...args)\n",
    "spread_list": "buat a = [1, 2]\nbuat b = [...a, 3]\ntulis b\n",

    # ---------- v8.0: spread objek ----------
    "spread_objek_dasar": 'buat a = {"x": 1, "y": 2}\nbuat b = {...a, "z": 3}\ntulis b\n',
    "spread_objek_timpa": 'buat a = {"x": 1, "y": 2}\nbuat b = {...a, "y": 99}\ntulis b\n',
    "spread_objek_tengah": 'buat a = {"x": 1}\nbuat b = {"awal": 0, ...a, "z": 3}\ntulis b\n',
    "spread_objek_belakang": 'buat a = {"x": 99}\nbuat b = {"x": 1, ...a}\ntulis b\n',
    "spread_objek_multi": 'buat a = {"x": 1}\nbuat b = {"y": 2}\nbuat c = {...a, ...b}\ntulis c\n',

    # ---------- v8.0: null-coalescing assignment ??= ----------
    "qq_assign_kosong": "buat x = kosong\nx ??= 5\ntulis x\n",
    "qq_assign_terisi": "buat x = 10\nx ??= 5\ntulis x\n",
    "qq_assign_falsy": "buat x = 0\nx ??= 99\ntulis x\n",
    "qq_assign_atribut": "kelas K\n    fungsi __init__(self)\n        self.nama = kosong\n    selesai\nselesai\nbuat k = K()\nk.nama ??= \"Budi\"\ntulis k.nama\n",
    "qq_assign_index": "buat d = [kosong, 2]\nd[0] ??= 99\ntulis d\n",
    "qq_assign_short_circuit": "buat hitung = [0]\nfungsi f()\n    hitung[0] = hitung[0] + 1\n    kembali 5\nselesai\nbuat x = 10\nx ??= f()\ntulis hitung[0]\n",

    # ---------- v8.0: kecuali multi-tipe ----------
    "kecuali_multi_tipe": "coba\n    buat x = 1 / 0\nkecuali (TypeError, ZeroDivisionError) sebagai e\n    tulis \"caught\"\nselesai\n",
    "kecuali_multi_tipe_kedua": "coba\n    buat x = 1 / 0\nkecuali (KeyError, ZeroDivisionError) sebagai e\n    tulis \"caught\"\nselesai\n",
    "kecuali_multi_lalu_tunggal": "coba\n    buat x = 1 / 0\nkecuali (KeyError, AttributeError) sebagai e\n    tulis \"salah\"\nkecuali ZeroDivisionError sebagai e2\n    tulis \"benar\"\nselesai\n",

    # ---------- v8.1: object pooling ----------
    "pool_basic": 'impor kumpulan_objek\nbuat pool = kumpulan_objek.KumpulanObjek(lalu() {"aktif": salah}, ukuran_awal=3)\nbuat a = pool.ambil()\nbuat b = pool.ambil()\ntulis pool.jumlah_aktif()\ntulis pool.jumlah_tersedia()\npool.kembalikan(a)\ntulis pool.jumlah_aktif()\ntulis pool.jumlah_tersedia()\n',
    "pool_kosongkan": 'impor kumpulan_objek\nbuat pool = kumpulan_objek.KumpulanObjek(lalu() {"aktif": salah}, ukuran_awal=2)\nbuat a = pool.ambil()\nbuat b = pool.ambil()\npool.kosongkan()\ntulis pool.jumlah_aktif()\ntulis pool.total()\n',

    # ---------- v8.1: simpan/muat game ----------
    "simpan_muat": 'impor simpan_game\nsimpan_game.simpan("cek_audit", {"level": 3, "kunci": ["emas"]}, folder="/tmp/bro_audit_81")\nbuat d = simpan_game.muat("cek_audit", default={}, folder="/tmp/bro_audit_81")\ntulis d["level"]\ntulis d["kunci"]\ntulis simpan_game.ada("cek_audit", folder="/tmp/bro_audit_81")\ntulis simpan_game.hapus("cek_audit", folder="/tmp/bro_audit_81")\n',
    "simpan_checkpoint": 'impor simpan_game\nsimpan_game.checkpoint({"l": 4}, folder="/tmp/bro_audit_81")\ntulis simpan_game.muat_checkpoint(folder="/tmp/bro_audit_81")["l"]\nsimpan_game.hapus("checkpoint", folder="/tmp/bro_audit_81")\n',

    # ---------- v8.1: dialog ----------
    "dialog_typewriter": 'impor dialog\nbuat d = dialog.Dialog(["Halo dunia!"], kecepatan=10)\nd.update(0.3)\ntulis d.teks_terlihat()\nd.lanjut()\ntulis d.selesai_mengetik()\nd.lanjut()\ntulis d.selesai()\n',
    "dialog_pilihan": 'impor dialog\nbuat d = dialog.Dialog(["Pilih"])\nd.atur_pilihan(["A", "B"])\ntulis d.pilihan_sekarang()\nbuat (teks, selesai) = d.pilih(1)\ntulis teks\ntulis selesai\n',

    # ---------- v8.1: ai FSM & steering ----------
    "ai_fsm": 'impor ai\nfungsi masuk_kejar()\n    tulis "mengejar!"\nselesai\nbuat mesin = ai.FSM("diam")\nmesin.tambah_status("kejar", masuk=masuk_kejar)\nmesin.ganti_status("kejar")\ntulis mesin.status_sekarang()\ntulis mesin.status_sebelumnya()\n',
    "ai_steering": 'impor ai\nbuat (vx, vy) = ai.kejar(0, 0, 100, 0, 50)\ntulis vx\ntulis vy\nbuat (a, b) = ai.lari(0, 0, 100, 0, 50)\ntulis a\nbuat (c, d) = ai.tiba(0, 0, 10, 0, 50, radius=16)\ntulis c\ntulis d\n',
    "ai_agen": 'impor ai\nbuat agen = ai.Agen(100, 100, kecepatan_maks=120)\nagen.atur_target((200, 100), mode="kejar")\nagen.update(1.0)\ntulis agen.x\ntulis agen.y\n',

    # ---------- v8.1: tilemap platform satu arah & bergerak ----------
    "tilemap_satu_arah": 'impor tilemap\nbuat ts = tilemap.buat_tileset("ts", ukuran_tile=32)\nts.tambah_tile(1, solid=benar)\nts.atur_satu_arah(2)\nbuat lantai = tilemap.buat_peta(10, 10, ukuran_tile=32)\nlantai.set_tileset(ts)\nlantai.atur(1, 5, 2)\ntulis lantai.cek_lantai_satu_arah(48, 159, kecepatan_y=100)\ntulis lantai.cek_lantai_satu_arah(48, 159, kecepatan_y=-100)\n',
    "tilemap_platform": 'impor tilemap\nbuat lantai = tilemap.buat_peta(10, 10, ukuran_tile=32)\nbuat p = lantai.tambah_platform_bergerak(0, 100, 320, 100, kecepatan=100)\nlantai.update(1.0)\ntulis p.x\nlantai.update(4.0)\ntulis p.x\n',

    # ---------- v8.1: quest & achievement ----------
    "misi_quest": 'impor misi\nbuat q = misi.Misi("kunci", "Cari Kunci", tujuan=3)\nq.tambah_progres(2)\ntulis q.progres()\ntulis q.tambah_progres(1)\ntulis q.selesai()\ntulis q.status()\n',
    "misi_pencapaian": 'impor misi\nbuat a = misi.Pencapaian("p1", "Ach 1")\ntulis a.buka_kunci()\ntulis a.buka_kunci()\ntulis a.terbuka()\n',
    "misi_manajer": 'impor misi\nbuat m = misi.ManajerMisi()\nm.buat_misi("m1", "Misi 1", tujuan=2)\nm.tambah_progres("m1", 2)\ntulis m.dapatkan("m1").status()\nbuat data = m.ke_dict()\ntulis panjang(data["misi"])\n',


    # ---------- with ----------
    "with_basic": "dengan 5 sebagai x\n    tulis x\nselesai\n",
    "with_class": "kelas K\n    fungsi masuk(self)\n        tulis \"masuk\"\n    selesai\n    fungsi keluar(self)\n        tulis \"keluar\"\n    selesai\nselesai\ndengan K() sebagai k\n    tulis \"body\"\nselesai\n",

    # ---------- stdlib ----------
    "stdlib_math": "impor matematika\ntulis matematika.pangkat(5, 2)\ntulis matematika.akar(16)\ntulis matematika.fpb(12, 18)\n",
    "stdlib_teks": "impor teks\ntulis teks.panjang(\"halo\")\ntulis teks.upper(\"abc\")\n",
    "stdlib_dasar": "impor dasar\ntulis dasar.urutkan([3, 1, 2])\ntulis dasar.unik([1, 1, 2])\n",
    "stdlib_json": "impor json\ntulis json.string({\"a\": 1})\n",
    "stdlib_tanggal": "impor tanggal\ntulis tanggal.hari_ini()\n",
    "stdlib_waktu": "impor waktu\ntulis waktu.timestamp() > 1000000\n",
    "stdlib_antrian": "impor antrian\nbuat q = antrian.buat()\nq.sisipkan(1)\nq.sisipkan(2)\ntulis q.ambil()\n",
    "stdlib_tumpukan": "impor tumpukan\nbuat s = tumpukan.buat()\ns.tumpuk(1)\ns.tumpuk(2)\ntulis s.ambil()\n",

    # ---------- range ----------
    "range_fn": "tulis range(3)\nuntuk i dalam range(3) lakukan\n    tulis i\nselesai\n",

    # ---------- enumerate/zip ----------
    "enumerate": "untuk i, x dalam enumerasi([10, 20]) lakukan\n    tulis i, x\nselesai\n",

    # ---------- string format angka ----------
    "angka_konversi": "tulis angka(\"42\")\ntulis desimal(\"3.14\")\ntulis teks(123)\n",
    "jenis": "tulis tipe(5)\ntulis tipe(\"a\")\ntulis tipe([1])\ntulis tipe(kosong)\n",
}


def _norm(out):
    """Normalisasi output: strip trailing whitespace tiap baris & akhir."""
    return "\n".join(l.rstrip() for l in out.splitlines())


def main():
    ok, fail = 0, 0
    results = {}
    for name, kode in SNIPPETS.items():
        outs = {}
        for eng in ("interp", "transpiler", "vm"):
            status, out = run_engine(kode, eng)
            outs[eng] = (status, _norm(out))
        results[name] = outs
        base = outs["interp"]
        mism = [e for e in ("transpiler", "vm") if outs[e] != base]
        if mism:
            fail += 1
            print(f"### MISMATCH: {name}  (vs interpreter: {', '.join(mism)})")
        else:
            ok += 1

    print()
    print(f"== {ok} cocok, {fail} mismatch ==")
    print()
    print("=== Detail mismatch ===")
    for name, outs in results.items():
        base = outs["interp"]
        for eng in ("transpiler", "vm"):
            if outs[eng] != base:
                print(f"\n----- {name} [{eng}] -----")
                print(f"  interp   : {base[0]} {base[1][:200]!r}")
                print(f"  {eng:<9}: {outs[eng][0]} {outs[eng][1][:200]!r}")


if __name__ == "__main__":
    main()
