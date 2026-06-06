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


def _cmd_help(args: List[str]) -> int:
    """Menampilkan bantuan."""
    print("""
BroLang 1.0 - Bahasa Pemrograman Edukatif Profesional

Penggunaan:
    bro run <file>         : Menjalankan file BroLang
    bro build <file>       : Mengompilasi ke Python
    bro repl               : Memulai REPL interaktif
    bro fmt <file>         : Memformat kode
    bro lint <file>        : Analisis kode statis
    bro version            : Informasi versi

Contoh:
    bro run app.bro
    bro build app.bro -o output.py
    bro repl
""")
    return 0


if __name__ == "__main__":
    sys.exit(main())
