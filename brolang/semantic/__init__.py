"""
Semantic Analyzer untuk BroLang
=================================

Semantic Analyzer bertugas memeriksa kebenaran semantik kode:
- Scope checking
- Undefined variable detection
- Duplicate declaration detection
- Type checking
- Function validation

Pipeline:
    AST → [Semantic Analyzer] → Validated AST → Optimizer → ...

Contoh:
    from brolang.semantic import SemanticAnalyzer

    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
"""

from brolang.semantic.analyzer import SemanticAnalyzer, SymbolTable, SymbolInfo
