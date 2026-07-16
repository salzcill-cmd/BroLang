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
        print("BroLang 1.0")
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
        "new-game": _cmd_new_game,
        "run-game": _cmd_run_game,
        "version": _cmd_version,
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
BroLang 1.1 - Bahasa Pemrograman Edukatif Profesional

Penggunaan:
    bro run <file>         : Menjalankan file BroLang
    bro build <file>       : Mengompilasi ke Python
    bro repl               : Memulai REPL interaktif
    bro fmt <file>         : Memformat kode
    bro lint <file>        : Analisis kode statis
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

Contoh:
    bro run app.bro
    bro build app.bro -o output.py
    bro new-game rpg_game
    bro run-game main.bro
""")
    return 0


if __name__ == "__main__":
    sys.exit(main())
