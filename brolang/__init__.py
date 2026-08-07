"""
BroLang - Bahasa Pemrograman Profesional untuk Game Development
================================================

BroLang adalah bahasa pemrograman modern yang dirancang untuk:
- Kemudahan belajar dengan sintaks Bahasa Indonesia
- Arsitektur profesional dan scalable
- Cocok untuk pendidikan dan produksi
- Game development dengan fitur lengkap

Filosofi:
    "Belajar coding harus semudah membaca bahasa manusia."

Fitur v6.0:
- Type System lengkap: `buat x: Angka = 5`, `fungsi f(a: Angka) -> Teks`,
  union (`Angka | Teks`), generik (`Daftar<Angka>`), alias tipe
- Pattern Matching Modern: pola list/objek, binding, guard
- Error Handling Profesional: `kelas_error` (custom error class)
- Ekosistem stdlib: tanggal, catat, lingkungan, proses, csv, registri
- Package Registry Online (publish/install via HTTP)

Fitur v5.0:
- Type System (tipe data dengan anotasi)
- Interfaces/Antarmuka
- Abstract Classes (kelas abstrak)
- Higher-Order Functions (peta, saring, kurangi)
- Result/Option Types (penanganan error)
- Macros (metaprogramming)
- Module System (ruang nama)
- Access Modifiers (publik, privat, terlindungi)
- Null Coalescing (??)
- Optional Chaining (?.)
- Chained Comparisons (0 < x < 10)
- For Each with Index
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

__version__ = "6.1.0"
__author__ = "BroLang Team"
__license__ = "MIT"

from brolang.exceptions import BroLangError
