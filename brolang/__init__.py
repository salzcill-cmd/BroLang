"""
BroLang - Bahasa Pemrograman Edukatif Profesional
==================================================

BroLang adalah bahasa pemrograman modern yang dirancang untuk:
- Kemudahan belajar dengan sintaks Bahasa Indonesia
- Arsitektur profesional dan scalable
- Cocok untuk pendidikan dan produksi

Filosofi:
    "Belajar coding harus semudah membaca bahasa manusia."

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

__version__ = "2.0.0"
__author__ = "BroLang Team"
__license__ = "MIT"

from brolang.exceptions import BroLangError
