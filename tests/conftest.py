"""
Pytest configuration untuk BroLang tests.
"""

import sys
import os
from typing import Any, List

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def run_brolang(source: str) -> Any:
    """Helper untuk menjalankan kode BroLang dan mengembalikan hasil.

    Args:
        source: Kode sumber BroLang

    Returns:
        Hasil eksekusi dan output
    """
    from brolang.lexer import Lexer
    from brolang.parser import Parser
    from brolang.interpreter import Interpreter

    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()

    interpreter = Interpreter()
    result = interpreter.interpret(ast)

    return result, interpreter.output


def run_brolang_full(source: str) -> Any:
    """Menjalankan pipeline lengkap BroLang."""
    from brolang.lexer import Lexer
    from brolang.parser import Parser
    from brolang.semantic import SemanticAnalyzer
    from brolang.optimizer import Optimizer
    from brolang.interpreter import Interpreter

    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()

    analyzer = SemanticAnalyzer()
    assert analyzer.analyze(ast), f"Semantic errors: {analyzer.errors}"

    optimizer = Optimizer()
    optimized = optimizer.optimize(ast)

    interpreter = Interpreter()
    result = interpreter.interpret(optimized)

    return result, interpreter.output
