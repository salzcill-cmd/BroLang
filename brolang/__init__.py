"""
BroLang - Bahasa Pemrograman Profesional untuk Game Development
================================================================

BroLang adalah bahasa pemrograman modern yang dirancang untuk:
- Kemudahan belajar dengan sintaks Bahasa Indonesia
- Arsitektur profesional dan scalable
- Cocok untuk pendidikan dan produksi
- Game development dengan fitur lengkap

Filosofi:
    "Belajar coding harus semudah membaca bahasa manusia."

Fitur v4.0:
- Async/Await (asinkron/tunggu)
- Generators (hasilkan)
- Decorators (@dekorator)
- Walrus Operator (:=)
- Context Manager (dengan...sebagai)
- Typed Exceptions (kecuali tipe)
- Test Framework (tes)
- Profiler (profil)
- Debugger (debugger)
- 25+ modul standard library
- Sprite, Animasi, Tilemap, Kamera, Fisika

Penggunaan:
    from brolang.interpreter import Interpreter
    from brolang.lexer import Lexer
    from brolang.parser import Parser

    lexer = Lexer(source_code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    interpreter = Interpreter()
    interpreter.interpret(ast)
"""

__version__ = "4.0.0"
__author__ = "BroLang Team"
__license__ = "MIT"

from brolang.exceptions import BroLangError
