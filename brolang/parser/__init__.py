"""
Parser untuk BroLang
====================

Parser menggunakan Recursive Descent Parsing untuk
mengubah token menjadi AST (Abstract Syntax Tree).

Pipeline:
    Tokens → [Parser] → AST → Semantic Analyzer → ...

Contoh:
    from brolang.lexer import Lexer
    from brolang.parser import Parser

    lexer = Lexer('tulis "Halo Dunia"')
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
"""

from brolang.parser.parser import Parser
