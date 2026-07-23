"""
REPL BroLang
============

REPL (Read-Eval-Print Loop) interaktif untuk BroLang.
Memungkinkan pengguna mengetik dan mengeksekusi kode
BroLang secara interaktif.

Mendukung transpiler (cepat) dengan fallback ke interpreter.
"""

import sys
import os
import io
import contextlib
from typing import List, Optional, Any
from brolang.lexer import Lexer
from brolang.parser import Parser
from brolang.semantic import SemanticAnalyzer
from brolang.optimizer import Optimizer
from brolang.interpreter import Interpreter
from brolang.vm.transpiler import Transpiler
from brolang import __version__


class BroLangREPL:
    """REPL interaktif BroLang.

    Attributes:
        interpreter: Interpreter yang digunakan
        history: Riwayat perintah
        multiline: Apakah dalam mode multi-line
        buffer: Buffer untuk multi-line input
        exec_globals: Global namespace untuk transpiler
    """

    def __init__(self):
        self.interpreter = Interpreter()
        self.history: List[str] = []
        self.multiline: bool = False
        self.buffer: List[str] = []
        self.prompt_count: int = 0
        # Persistent namespace untuk transpiler
        self.exec_globals = {'__builtins__': __builtins__}

    def start(self) -> None:
        """Memulai REPL."""
        self._print_welcome()
        self._run_loop()

    def _print_welcome(self) -> None:
        """Menampilkan pesan selamat datang."""
        print(f"\nBroLang {__version__}")
        print("Bahasa Pemrograman Profesional untuk Game Development")
        print("Ketik 'exit' atau Ctrl+C untuk keluar")
        print()

    def _run_loop(self) -> None:
        """Loop utama REPL."""
        while True:
            try:
                if self.multiline:
                    line = input("... ")
                else:
                    self.prompt_count += 1
                    line = input(f"[{self.prompt_count}]>> ")

                if line.strip().lower() in ("exit", "quit", "keluar"):
                    print("Sampai jumpa!")
                    break

                if line.strip() == "" and self.multiline:
                    # Execute buffer
                    self._execute_multiline()
                    continue

                if line.rstrip().endswith(":"):
                    # Start multiline mode
                    self.multiline = True
                    self.buffer.append(line)
                    continue

                if self.multiline:
                    self.buffer.append(line)
                    # Check if we should end multiline
                    if line.strip() == "":
                        self._execute_multiline()
                    continue

                # Execute single line
                self._execute(line)

            except KeyboardInterrupt:
                print("\nSampai jumpa!")
                break
            except EOFError:
                print("\nSampai jumpa!")
                break

    def _execute(self, source: str) -> None:
        """Mengeksekusi satu baris kode."""
        if not source.strip():
            return

        self.history.append(source)

        try:
            lexer = Lexer(source)
            tokens = lexer.tokenize()

            parser = Parser(tokens)
            ast = parser.parse()

            if not ast.statements:
                return

            analyzer = SemanticAnalyzer()
            if not analyzer.analyze(ast):
                for error in analyzer.errors:
                    print(str(error))
                return

            optimizer = Optimizer()
            optimized = optimizer.optimize(ast)

            # Coba transpiler dulu (lebih cepat)
            try:
                transpiler = Transpiler()
                py_code = transpiler.transpile(optimized)
                # Jalankan dengan output capture
                stdout_capture = io.StringIO()
                with contextlib.redirect_stdout(stdout_capture):
                    exec(compile(py_code, '<repl>', 'exec'), self.exec_globals)
                # Tampilkan output
                output = stdout_capture.getvalue()
                if output:
                    print(output, end='')
                # Tampilkan hasil expression jika ada
                # (Expression results are shown via tulis() in transpiled code)
                return
            except Exception:
                # Fallback ke interpreter
                pass

            # Interpreter fallback
            result = self.interpreter.interpret(optimized)

            # Show result for expressions
            if result is not None:
                print(f"=> {result}")

        except Exception as e:
            print(str(e))

    def _execute_multiline(self) -> None:
        """Mengeksekusi multi-line buffer."""
        source = "\n".join(self.buffer)
        self.buffer = []
        self.multiline = False

        if source.strip():
            self._execute(source)


def start_repl() -> None:
    """Convenience function untuk memulai REPL."""
    repl = BroLangREPL()
    repl.start()


if __name__ == "__main__":
    start_repl()
