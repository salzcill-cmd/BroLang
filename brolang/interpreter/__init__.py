"""
Interpreter untuk BroLang
=========================

Interpreter mengeksekusi AST yang sudah dioptimasi.
Menggunakan visitor pattern untuk traversal AST.

Pipeline:
    Optimized AST → [Interpreter] → Output/Runtime Values

Contoh:
    from brolang.interpreter import Interpreter

    interpreter = Interpreter()
    result = interpreter.interpret(ast)
"""

from brolang.interpreter.interpreter import Interpreter, Environment
