"""
Lexer untuk BroLang
====================

Lexer bertugas mengubah kode sumber menjadi token-token.
Ini adalah tahap pertama dalam pipeline kompilasi/interpretasi.

Pipeline:
    Source Code → [Lexer] → Tokens → Parser → AST → ...

Contoh:
    from brolang.lexer import Lexer

    lexer = Lexer('tulis "Halo Dunia"')
    tokens = lexer.tokenize()
"""

from brolang.lexer.lexer import Lexer
