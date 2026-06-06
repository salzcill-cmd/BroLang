"""
Compiler BroLang
================

Compiler mengubah AST BroLang menjadi Python bytecode.
Ini memungkinkan eksekusi cepat dengan memanfaatkan
runtime Python yang sudah mature.

Pipeline:
    AST → [Compiler] → Python AST → Python Bytecode → Eksekusi

Tahap 1: BroLang AST → Python AST
Tahap 2: Python AST → Python Bytecode (via compile())

Roadmap masa depan:
    Tahap 3: BroLang AST → LLVM IR → Native Binary

Contoh:
    from brolang.compiler import Compiler

    compiler = Compiler()
    py_code = compiler.compile(ast)
    exec(py_code)
"""

from brolang.compiler.compiler import Compiler, compile_source
