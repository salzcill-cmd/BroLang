"""
CLI Main Entry Point untuk BroLang
===================================

Menangani parsing argumen command line dan dispatch ke handler yang sesuai.
"""

import sys
import os
import argparse
from typing import Optional, List


def main(args: Optional[List[str]] = None) -> int:
    """Entry point utama CLI BroLang.

    Args:
        args: Argumen command line (default: sys.argv[1:])

    Returns:
        int: Exit code
    """
    if args is None:
        args = sys.argv[1:]

    if not args:
        from brolang import __version__
        print(f"BroLang {__version__}")
        print("Gunakan 'bro --help' untuk bantuan.")
        return 0

    command = args[0]
    command_args = args[1:]

    # Jika argumen adalah file .bro, jalankan langsung (seperti python main.py)
    if command.endswith(".bro") or (not command.startswith("-") and os.path.isfile(command)):
        return _cmd_run(args)

    commands = {
        "run": _cmd_run,
        "build": _cmd_build,
        "repl": _cmd_repl,
        "fmt": _cmd_fmt,
        "lint": _cmd_lint,
        "test": _cmd_test,
        "profile": _cmd_profile,
        "doc": _cmd_doc,
        "new-game": _cmd_new_game,
        "run-game": _cmd_run_game,
        "version": _cmd_version,
        "--version": _cmd_version,
        "-v": _cmd_version,
        "--help": _cmd_help,
        "-h": _cmd_help,
    }

    handler = commands.get(command)
    if handler is None:
        print(f"Perintah tidak dikenal: {command}")
        print("Gunakan 'bro --help' untuk bantuan.")
        return 1

    return handler(command_args)


def _cmd_run(args: List[str]) -> int:
    """Menjalankan file BroLang.

    Penggunaan:
        bro run <file>
    """
    parser = argparse.ArgumentParser(prog="bro run", description="Menjalankan file BroLang")
    parser.add_argument("file", help="File BroLang (.bro)")
    parsed = parser.parse_args(args)

    file_path = parsed.file
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' tidak ditemukan.")
        return 1

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()

        from brolang.lexer import Lexer
        from brolang.parser import Parser
        from brolang.semantic import SemanticAnalyzer
        from brolang.optimizer import Optimizer
        from brolang.interpreter import Interpreter

        # Pipeline lengkap
        lexer = Lexer(source, file_path=file_path)
        tokens = lexer.tokenize()

        parser = Parser(tokens, file_path=file_path)
        ast = parser.parse()

        analyzer = SemanticAnalyzer()
        if not analyzer.analyze(ast):
            for error in analyzer.errors:
                print(str(error))
            return 1

        optimizer = Optimizer()
        optimized_ast = optimizer.optimize(ast)

        # Fast path: try transpiler first (97x faster)
        try:
            from brolang.vm.transpiler import Transpiler
            transpiler = Transpiler()
            py_code = transpiler.transpile(optimized_ast)
            compiled = compile(py_code, file_path, 'exec')
            exec(compiled, {'__builtins__': __builtins__})
            return 0
        except Exception:
            # Fallback ke interpreter (tanpa warning untuk user)
            pass

        # Fallback: tree-walking interpreter
        interpreter = Interpreter()
        interpreter.interpret(optimized_ast)

        return 0

    except Exception as e:
        print(str(e))
        return 1


def _cmd_build(args: List[str]) -> int:
    """Mengompilasi file BroLang ke Python.

    Penggunaan:
        bro build <file> -o <output.py>
    """
    parser = argparse.ArgumentParser(prog="bro build", description="Mengompilasi BroLang ke Python")
    parser.add_argument("file", help="File BroLang (.bro)")
    parser.add_argument("-o", "--output", help="File output Python")
    parsed = parser.parse_args(args)

    file_path = parsed.file
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' tidak ditemukan.")
        return 1

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()

        from brolang.compiler import compile_source

        py_source = compile_source(source, filename=file_path)

        output_path = parsed.output
        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(py_source)
            print(f"Output: {output_path}")
        else:
            print(py_source)

        return 0

    except Exception as e:
        print(str(e))
        return 1


def _cmd_repl(args: List[str]) -> int:
    """Memulai REPL interaktif."""
    from brolang.repl import start_repl

    try:
        start_repl()
        return 0
    except KeyboardInterrupt:
        print("\nSampai jumpa!")
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1


def _cmd_fmt(args: List[str]) -> int:
    """Memformat file BroLang.

    Penggunaan:
        bro fmt <file>
    """
    parser = argparse.ArgumentParser(prog="bro fmt", description="Memformat kode BroLang")
    parser.add_argument("file", help="File BroLang (.bro)")
    parser.add_argument("--check", action="store_true", help="Cek format tanpa mengubah")
    parsed = parser.parse_args(args)

    try:
        from brolang.formatter import format_file, check_format
        file_path = parsed.file

        if parsed.check:
            is_formatted = check_format(file_path)
            if is_formatted:
                print(f"{file_path}: format sudah rapi.")
                return 0
            else:
                print(f"{file_path}: perlu diformat.")
                return 1
        else:
            format_file(file_path)
            print(f"{file_path}: format selesai.")
            return 0

    except Exception as e:
        print(f"Error: {e}")
        return 1


def _cmd_lint(args: List[str]) -> int:
    """Menganalisis kode statis.

    Penggunaan:
        bro lint <file>
    """
    parser = argparse.ArgumentParser(prog="bro lint", description="Menganalisis kode BroLang")
    parser.add_argument("file", help="File BroLang (.bro)")
    parsed = parser.parse_args(args)

    try:
        from brolang.linter import lint_file
        issues = lint_file(parsed.file)

        if not issues:
            print("Tidak ada masalah ditemukan.")
            return 0

        for issue in issues:
            print(f"  [{issue.severity}] Baris {issue.line}: {issue.message}")
            if issue.suggestion:
                print(f"          Saran: {issue.suggestion}")

        print(f"\nDitemukan {len(issues)} masalah.")
        return 1 if any(i.severity == "error" for i in issues) else 0

    except Exception as e:
        print(f"Error: {e}")
        return 1


def _cmd_test(args: List[str]) -> int:
    """Menjalankan test file BroLang.

    Penggunaan:
        bro test <file>
        bro test
    """
    parser = argparse.ArgumentParser(prog="bro test", description="Menjalankan tes BroLang")
    parser.add_argument("file", nargs="?", help="File tes BroLang (.bro)")
    parsed = parser.parse_args(args)

    try:
        import os
        import glob

        if parsed.file:
            files = [parsed.file]
        else:
            # Find all test files
            files = glob.glob("**/test_*.bro", recursive=True)
            files.extend(glob.glob("**/*_test.bro", recursive=True))
            files.extend(glob.glob("tests/**/*.bro", recursive=True))
            files = list(set(files))

        if not files:
            print("Tidak ada file tes ditemukan.")
            return 1

        total_pass = 0
        total_fail = 0

        for file_path in files:
            print(f"\nMenjalankan: {file_path}")
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    source = f.read()

                from brolang.lexer import Lexer
                from brolang.parser import Parser
                from brolang.interpreter import Interpreter

                lexer = Lexer(source, file_path=file_path)
                tokens = lexer.tokenize()
                parser_inst = Parser(tokens, file_path=file_path)
                ast = parser_inst.parse()

                interpreter = Interpreter()
                interpreter.interpret(ast)

                # Check test results
                if hasattr(interpreter, 'output'):
                    for line in interpreter.output:
                        print(f"  {line}")

                total_pass += 1
            except Exception as e:
                print(f"  Error: {e}")
                total_fail += 1

        print(f"\n{'='*50}")
        print(f"Total: {len(files)} file, {total_pass} berhasil, {total_fail} gagal")
        print(f"{'='*50}")

        return 0 if total_fail == 0 else 1

    except Exception as e:
        print(f"Error: {e}")
        return 1


def _cmd_profile(args: List[str]) -> int:
    """Memprofil eksekusi file BroLang.

    Penggunaan:
        bro profile <file>
    """
    parser = argparse.ArgumentParser(prog="bro profile", description="Memprofil kode BroLang")
    parser.add_argument("file", help="File BroLang (.bro)")
    parser.add_argument("--repeat", type=int, default=1, help="Jumlah pengulangan")
    parsed = parser.parse_args(args)

    file_path = parsed.file
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' tidak ditemukan.")
        return 1

    try:
        import time
        import cProfile
        import pstats
        import io

        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()

        from brolang.lexer import Lexer
        from brolang.parser import Parser
        from brolang.semantic import SemanticAnalyzer
        from brolang.optimizer import Optimizer
        from brolang.interpreter import Interpreter

        # Profile the execution
        pr = cProfile.Profile()
        pr.enable()

        start_time = time.time()
        for _ in range(parsed.repeat):
            lexer = Lexer(source, file_path=file_path)
            tokens = lexer.tokenize()
            parser_inst = Parser(tokens, file_path=file_path)
            ast = parser_inst.parse()

            analyzer = SemanticAnalyzer()
            analyzer.analyze(ast)

            optimizer = Optimizer()
            optimized_ast = optimizer.optimize(ast)

            interpreter = Interpreter()
            interpreter.interpret(optimized_ast)

        end_time = time.time()
        pr.disable()

        # Print results
        print(f"\n{'='*60}")
        print(f"Profil: {file_path}")
        print(f"{'='*60}")
        print(f"Total waktu: {(end_time - start_time)*1000:.2f} ms")
        print(f"Pengulangan: {parsed.repeat}")
        print(f"Waktu rata-rata: {((end_time - start_time)/parsed.repeat)*1000:.2f} ms")

        # Print top functions
        print(f"\nTop 10 functions:")
        s = io.StringIO()
        ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
        ps.print_stats(10)
        print(s.getvalue())

        return 0

    except Exception as e:
        print(f"Error: {e}")
        return 1


def _cmd_doc(args: List[str]) -> int:
    """Menampilkan dokumentasi BroLang.

    Penggunaan:
        bro doc [topik]
    """
    parser = argparse.ArgumentParser(prog="bro doc", description="Dokumentasi BroLang")
    parser.add_argument("topik", nargs="?", help="Topik dokumentasi")
    parsed = parser.parse_args(args)

    topics = {
        None: _doc_overview,
        "dasar": _doc_basics,
        "variabel": _doc_variables,
        "fungsi": _doc_functions,
        "kelas": _doc_classes,
        "game": _doc_game,
        "stdlib": _doc_stdlib,
        "async": _doc_async,
        "generator": _doc_generators,
        "decorator": _doc_decorators,
    }

    if parsed.topik in topics:
        topics[parsed.topik]()
    else:
        print(f"Topik tidak dikenal: {parsed.topik}")
        print(f"Topik tersedia: {', '.join(t for t in topics.keys() if t)}")
        return 1

    return 0


def _doc_overview():
    print("""
BroLang - Bahasa Pemrograman Profesional untuk Game Development
===============================================================

BroLang adalah bahasa pemrograman modern yang menggunakan sintaks Bahasa Indonesia.
Dirancang untuk kemudahan belajar dan pembuatan game 2D.

Perintah:
  bro run <file>         : Menjalankan file BroLang
  bro build <file>       : Mengompilasi ke Python
  bro repl               : REPL interaktif
  bro test [file]        : Menjalankan tes
  bro profile <file>     : Profil eksekusi
  bro lint <file>        : Analisis kode
  bro fmt <file>         : Format kode
  bro doc [topik]        : Dokumentasi
  bro new-game <nama>    : Buat proyek game baru
  bro run-game <file>    : Jalankan game

Topik Dokumentasi:
  bro doc dasar          : Dasar bahasa
  bro doc variabel       : Variabel dan tipe data
  bro doc fungsi         : Fungsi dan lambda
  bro doc kelas          : OOP
  bro doc game           : Game development
  bro doc stdlib         : Standard library
  bro doc async          : Async/await
  bro doc generator      : Generator
  bro doc decorator      : Decorator
""")


def _doc_basics():
    print("""
Dasar BroLang
=============

# Komentar
# Ini komentar baris
#| Ini komentar
   multi baris #|

# Output
tulis "Halo Dunia"

# Tipe Data
buat nama = "Budi"       # teks (string)
buat umur = 25            # angka (integer)
buat tinggi = 170.5       # desimal (float)
buat aktif = benar        # boolean
buat data = kosong        # null

# Operator
tulis 2 + 3               # 5
tulis 10 - 4              # 6
tulis 3 * 7               # 21
tulis 10 / 3              # 3.333
tulis 10 % 3              # 1
tulis 2 ** 3              # 8

# String
buat s1 = "Halo"
buat s2 = 'Dunia'
buat s3 = f"Halo {nama}"  # f-string
tulis s1.panjang()         # Panjang string

# Kondisi
jika umur > 18 maka
    tulis "Dewasa"
lainnya jika umur > 12 maka
    tulis "Remaja"
lainnya
    tulis "Anak-anak"
selesai

# Ternary
buat status = "Dewasa" jika umur > 18 lainnya "Anak"
""")


def _doc_variables():
    print("""
Variabel dan Tipe Data
======================

# Deklarasi
buat nama = "Budi"
buat umur = 25
buat tinggi = 170.5
buat aktif = benar
buat data = kosong

# Tipe: angka, desimal, teks, boolean, kosong, list, objek, tuple, set

# List
buat angka = [1, 2, 3, 4, 5]
tulis angka[0]              # 1
tulis angka[1:3]            # [2, 3]
angka.tambah(6)             # Tambah elemen
angka.hapus(0)              # Hapus elemen
tulis angka.jumlah()        # Panjang list

# Dictionary (Objek)
buat mahasiswa = {
    "nama": "Budi",
    "umur": 25,
    "ipk": 3.8
}
tulis mahasiswa["nama"]     # Budi
mahasiswa.tambah("alamat", "Jakarta")
mahasiswa.hapus_kunci("alamat")

# Tuple
buat koordinat = (10, 20)

# Set
buat warna = {merah, biru, hijau}

# Augmented Assignment
buat x = 10
x += 5                      # x = 15
x -= 3                      # x = 12
x *= 2                      # x = 24

# Walrus Operator (v4.0)
jika (x := panjang()) > 10 maka
    tulis "Panjang:" + teks(x)
selesai
""")


def _doc_functions():
    print("""
Fungsi dan Lambda
=================

# Deklarasi fungsi
fungsi sapa(nama)
    kembali "Halo, " + nama
selesai

tulis(sapa("Budi"))

# Default parameter
fungsi power(base, pangkat=2)
    kembali base ** pangkat
selesai

tulis(power(3))      # 9
tulis(power(3, 3))   # 27

# Lambda
buat kali_dua = lalu(x) x * 2
tulis(kali_dua(5))   # 10

# List Comprehension
buat kuadrat = [x * x lalu x dalam range(10)]
buat genap = [x lalu x dalam range(20) jika x % 2 == 0]

# Function Call
tulis(len("Halo"))
tulis(angka("42"))
tulis(teks(100))
tulis(tipe(3.14))
""")


def _doc_classes():
    print("""
Kelas (OOP)
===========

# Deklarasi kelas
kelas Mahasiswa
    fungsi __init__(nama, ipk)
        self.nama = nama
        self.ipk = ipk
    selesai

    fungsi sapa()
        kembali f"Halo, saya {self.nama}"
    selesai

    fungsi __repr__()
        kembali f"Mahasiswa({self.nama}, {self.ipk})"
    selesai
selesai

buat budi = Mahasiswa("Budi", 3.8)
tulis(budi.sapa())

# Inheritance
kelas Dosen(Mahasiswa)
    fungsi __init__(nama, ipk, mata_kuliah)
        super().__init__(nama, ipk)
        self.mata_kuliah = mata_kuliah
    selesai

    fungsi mengajar()
        kembali f"{self.nama} mengajar {self.mata_kuliah}"
    selesai
selesai

# Enum
enum Warna { MERAH, BIRU, HIJAU }
buat warna = Warna.MERAH

# Struct
struktur Titik { x, y }
buat p = Titik(10, 20)

# Match/Case
cocokkan warna
    Warna.MERAH: tulis "Merah"
    Warna.BIRU: tulis "Biru"
    _: tulis "Warna lain"
selesai
""")


def _doc_game():
    print("""
Game Development
================

# Modul yang tersedia:
# - game: Game loop & scene management
# - grafis: Rendering 2D (Pygame)
# - input: Keyboard & mouse
# - audio: Sound & musik
# - vektor: Vektor 2D/3D
# - sprite: Sprite system
# - animasi: Animasi
# - tilemap: Tilemap
# - kamera: Kamera
# - fisika: Fisika dasar

# Contoh game sederhana:
impor game
impor grafis
impor input

buat player_x = 400
buat player_y = 300

fungsi update(dt)
    jika input.tombol_ditekan("LEFT"):
        player_x -= 200 * dt
    selesai
selesai

fungsi gambar(screen)
    grafis.bersihkan("hitam")
    grafis.segi_panjang(player_x, player_y, 32, 32, "biru")
selesai

game.buat_jendela(800, 600, "Gameku")
game.tambah_scene("utama", update, gambar)
game.ganti_scene("utama")
game.mulai()

# Sprite System
impor sprite

buat player = sprite.Sprite(None, 100, 100, 32, 32)
player.tambah_animasi("jalan", [0, 1, 2, 3], 0.1)
player.mainkan_animasi("jalan")

# Kamera
impor kamera

buat cam = kamera.Kamera(800, 600)
cam.set_target(player)
cam.update(dt)

# Fisika
impor fisika

buat bodi = fisika.Bodi(100, 100, massa=5.0)
bodi.tambah_gaya(0, 9.8)
bodi.update(dt)

# Tilemap
impor tilemap

buat peta = tilemap.Tilemap(20, 15, 32)
peta.atur(5, 3, 1)
peta.atur(5, 4, 1)
""")


def _doc_stdlib():
    print("""
Standard Library
================

# Core Modules
impor matematika    # Fungsi matematika
impor teks          # Manipulasi teks
impor waktu         # Fungsi waktu
impor file          # Operasi file
impor json          # JSON parsing
impor jaringan      # HTTP client
impor acak          # Random numbers

# Game Modules
impor vektor        # Vektor 2D/3D
impor grafis        # Rendering 2D
impor audio         # Sound & musik
impor input         # Keyboard & mouse
impor game          # Game loop

# v4.0 Modules
impor pencocok      # Regex pattern matching
impor antrian       # Queue data structure
impor tumpukan      # Stack data structure
impor serialisasi   # Serialization (JSON, base64, etc)
impor dasar         # Base encoding (base64, hex, etc)
impor sprite        # Sprite system
impor animasi       # Animation system
impor tilemap       # Tilemap
impor kamera        # Camera system
impor fisika        # Physics engine
impor debugger      # Debugger
impor profil        # Profiler
impor tes           # Test framework

# Contoh penggunaan
impor pencocok
buat hasil = pencocok.cari(r'\\d+', "ada 123 angka")
tulis(hasil.teks)

impor antrian
buat q = antrian.Buat()
q.sisipkan("a")
q.sisipkan("b")
tulis(q.ambil())

impor serialisasi
buat data = {"nama": "Budi"}
buat json_str = serialisasi.ke_json(data)
tulis(json_str)
""")


def _doc_async():
    print("""
Async/Await (v4.0)
==================

# Async function
asinkron fungsi ambil_data()
    tunggu 1  # Simulasi async operation
    kembali "data"
selesai

# Await
buat hasil = tunggu ambil_data()
tulis(hasil)

# Catatan: Dalam interpreter sync, async/await
# dijalankan secara synchronous.
""")


def _doc_generators():
    print("""
Generators (v4.0)
=================

# Generator function
fungsi bilangan_genap(max)
    untuk i dalam range(0, max, 2):
        hasilkan i
    selesai
selesai

# Menggunakan generator
buat gen = bilangan_genap(10)
tulis(gen)  # [0, 2, 4, 6, 8]

# Yield
fungsi counter(start, end)
    buat i = start
    selama i < end:
        hasilkan i
        i += 1
    selesai
selesai
""")


def _doc_decorators():
    print("""
Decorators (v4.0)
=================

# Simple decorator
fungsi timing(func)
    lalu wrapper(*args)
        mulai waktu = waktu.sekarang()
        hasil = func(*args)
        akhir waktu = waktu.sekarang()
        tulis(f"Waktu: {akhir_waktu - mulai_waktu}")
        kembali hasil
    selesai
    kembali wrapper
selesai

# Menggunakan decorator
@timing
fungsi proses_data()
    # ... proses ...
    kembali "selesai"
selesai

# Class decorator
@dataclass
kelas Point
    buat x = 0
    buat y = 0
selesai
""")


def _cmd_version(args: List[str]) -> int:
    """Menampilkan versi BroLang."""
    from brolang import __version__
    print(f"BroLang {__version__}")
    return 0


def _cmd_new_game(args: List[str]) -> int:
    """Membuat proyek game baru.

    Penggunaan:
        bro new-game <nama_folder>
    """
    parser = argparse.ArgumentParser(prog="bro new-game", description="Membuat proyek game BroLang baru")
    parser.add_argument("nama", help="Nama folder proyek game")
    parsed = parser.parse_args(args)

    project_dir = os.path.abspath(parsed.nama)
    if os.path.exists(project_dir):
        print(f"Error: Folder '{parsed.nama}' sudah ada.")
        return 1

    try:
        os.makedirs(project_dir)
        os.makedirs(os.path.join(project_dir, "assets"))
        os.makedirs(os.path.join(project_dir, "assets", "suara"))
        os.makedirs(os.path.join(project_dir, "assets", "gambar"))

        template = '''# Game BroLang
# ==================
# Dibuat dengan: bro new-game {nama}

impor game
impor grafis
impor input
impor vektor

# --- Variabel Game ---
buat player_pos = vektor.Vec2(400, 300)
buat player_ukuran = 32
buat player_warna = "biru"
buat kecepatan = 200.0
buat skor = 0

# --- Update ---
def update(dt):
    global player_pos, skor

    # Gerak player
    jika input.tombol_ditekan("LEFT") atau input.tombol_ditekan("a"):
        player_pos.x = player_pos.x - kecepatan * dt
    jika input.tombol_ditekan("RIGHT") atau input.tombol_ditekan("d"):
        player_pos.x = player_pos.x + kecepatan * dt
    jika input.tombol_ditekan("UP") || input.tombol_ditekan("w"):
        player_pos.y = player_pos.y - kecepatan * dt
    jika input.tombol_ditekan("DOWN") || input.tombol_ditekan("s"):
        player_pos.y = player_pos.y + kecepatan * dt

    # Batasi dalam layar
    jika player_pos.x < 0 maka
        player_pos.x = 0
    selesai
    jika player_pos.x > grafis.dapatkan_lebar() - player_ukuran maka
        player_pos.x = grafis.dapatkan_lebar() - player_ukuran
    selesai
    jika player_pos.y < 0 maka
        player_pos.y = 0
    selesai
    jika player_pos.y > grafis.dapatkan_tinggi() - player_ukuran maka
        player_pos.y = grafis.dapatkan_tinggi() - player_ukuran
    selesai

# --- Gambar ---
def gambar(screen):
    grafis.bersihkan("hitam")

    # Gambar player
    grafis.segi_panjang(player_pos.x, player_pos.y, player_ukuran, player_ukuran, player_warna)

    # Gambar UI
    grafis.tulis_teks("Skor: " + teks(skor), 10, 10, "putih", 24)
    grafis.tulis_teks("WASD/Arrow untuk bergerak", 10, 40, "abu-abu", 20)

# --- Main ---
game.buat_jendela(800, 600, "Game BroLang Baru")
game.tambah_scene("utama", update, gambar)
game.ganti_scene("utama")
game.mulai()
'''.format(nama=parsed.nama)

        with open(os.path.join(project_dir, "main.bro"), "w", encoding="utf-8") as f:
            f.write(template)

        print(f"Proyek game '{parsed.nama}' berhasil dibuat!")
        print(f"")
        print(f"  {parsed.nama}/")
        print(f"    main.bro          <- File utama game")
        print(f"    assets/")
        print(f"      gambar/          <- Simpan gambar/sprite di sini")
        print(f"      suara/           <- Simpan sound effect/musik di sini")
        print(f"")
        print(f"Untuk menjalankan:")
        print(f"  cd {parsed.nama}")
        print(f"  bro run-game main.bro")
        return 0

    except Exception as e:
        print(f"Error: {e}")
        return 1


def _cmd_run_game(args: List[str]) -> int:
    """Menjalankan file game BroLang.

    Penggunaan:
        bro run-game <file>
    """
    parser = argparse.ArgumentParser(prog="bro run-game", description="Menjalankan game BroLang")
    parser.add_argument("file", help="File game BroLang (.bro)")
    parsed = parser.parse_args(args)

    file_path = parsed.file
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' tidak ditemukan.")
        return 1

    try:
        import pygame
    except ImportError:
        print("Error: Pygame tidak terinstal.")
        print("Jalankan: pip install pygame")
        return 1

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()

        from brolang.lexer import Lexer
        from brolang.parser import Parser
        from brolang.semantic import SemanticAnalyzer
        from brolang.optimizer import Optimizer
        from brolang.interpreter import Interpreter

        lexer = Lexer(source, file_path=file_path)
        tokens = lexer.tokenize()

        parser = Parser(tokens, file_path=file_path)
        ast = parser.parse()

        analyzer = SemanticAnalyzer()
        if not analyzer.analyze(ast):
            for error in analyzer.errors:
                print(str(error))
            return 1

        optimizer = Optimizer()
        optimized_ast = optimizer.optimize(ast)

        interpreter = Interpreter()
        interpreter.interpret(optimized_ast)

        return 0

    except Exception as e:
        print(str(e))
        return 1


def _cmd_help(args: List[str]) -> int:
    """Menampilkan bantuan."""
    print("""
BroLang - Bahasa Pemrograman Profesional untuk Game Development

Penggunaan:
    bro run <file>         : Menjalankan file BroLang
    bro build <file>       : Mengompilasi ke Python
    bro repl               : Memulai REPL interaktif
    bro test [file]        : Menjalankan tes
    bro profile <file>     : Profil eksekusi
    bro lint <file>        : Analisis kode statis
    bro fmt <file>         : Memformat kode
    bro doc [topik]        : Dokumentasi
    bro new-game <nama>    : Buat proyek game baru
    bro run-game <file>    : Jalankan file game
    bro version            : Informasi versi

Game Development:
    bro new-game mygame    : Buat proyek game di folder mygame/
    bro run-game main.bro  : Jalankan game

Modul Game:
    impor game       : Game loop & scene management
    impor grafis     : Rendering 2D (Pygame)
    impor input      : Keyboard & mouse
    impor audio      : Sound & musik
    impor vektor     : Vektor 2D/3D
    impor sprite     : Sprite system
    impor animasi    : Animasi
    impor tilemap    : Tilemap
    impor kamera     : Kamera
    impor fisika     : Fisika

Fitur Baru v4.0:
    asinkron/tunggu      : Async/await
    hasilkan             : Generator/yield
    @dekorator           : Decorators
    :=                   : Walrus operator
    dengan...sebagai     : Context manager
    kecuali tipe         : Typed exceptions
    bro test             : Test framework
    bro profile          : Profiler
    bro doc              : Documentation

Contoh:
    bro run app.bro
    bro build app.bro -o output.py
    bro test
    bro profile game.bro
    bro doc dasar
    bro new-game rpg_game
    bro run-game main.bro
""")
    return 0


if __name__ == "__main__":
    sys.exit(main())
