# Arsitektur BroLang

> **Mau tau cara kerja BroLang di belakang layar?** Baca sini.

## 🔄 Pipeline Eksekusi

```
Source Code (.bro)
    ↓
┌─────────┐
│  Lexer  │ ← Tokenisasi
└─────────┘
    ↓
┌──────────┐
│  Parser  │ ← Bikin AST (Abstract Syntax Tree)
└──────────┘
    ↓
┌─────────────────────┐
│ SemanticAnalyzer    │ ← Cek tipe, scope, error
└─────────────────────┘
    ↓
┌────────────┐
│ Optimizer  │ ← Dead code elim, constant folding
└────────────┘
    ↓
┌─────────────┐
│ Interpreter │ ← Eksekusi AST langsung
└─────────────┘
    ↓
┌─────────┐
│ Output  │
└─────────┘
```

## 📁 Struktur Project

```
BroLang/
├── brolang/
│   ├── __init__.py          # Package init + versi
│   ├── cli/
│   │   ├── main.py          # Entry point utama
│   │   └── __init__.py
│   ├── token_types.py       # 130+ token types
│   ├── lexer/
│   │   ├── lexer.py         # Tokenisasi
│   │   ├── lexer_handlers.py # Handler per karakter
│   │   ├── file_source.py   # Baca file
│   │   └── errors.py        # Lexer errors
│   ├── parser/
│   │   ├── parser.py        # Parser utama
│   │   ├── token_iterator.py # Iterator tokens
│   │   └── errors.py        # Parser errors
│   ├── ast/
│   │   ├── __init__.py      # 110+ AST node types
│   │   ├── nodes.py         # Node definitions
│   │   └── visitor.py       # Visitor pattern
│   ├── semantic/
│   │   └── analyzer.py      # Semantic analysis
│   ├── optimizer.py         # Code optimization
│   ├── interpreter/
│   │   ├── interpreter.py   # Interpreter utama
│   │   ├── runtime.py       # Runtime values
│   │   ├── environment.py   # Variable scopes
│   │   └── errors.py        # Runtime errors
│   ├── compiler/
│   │   └── compiler.py      # Bytecode compiler
│   └── stdlib/
│       ├── __init__.py      # Module loader
│       ├── math.py          # modul_angka
│       ├── game.py          # modul_game
│       ├── vektor.py        # modul_vektor
│       └── ...              # 20+ modules
├── tests/                   # 183 test cases
├── examples/                # Contoh program
├── docs/                    # Dokumentasi
└── setup.py                 # Package config
```

## 🧩 Komponen Utama

### Lexer
- Tokenisasi karakter per karakter
- Handle string, number, identifier, keyword
- Multi-word operators (is bukan, bukan dalam)
- 130+ token types

### Parser
- Recursive descent parser
- Operator precedence parsing
- Ternary expression support
- Nested expression support

### AST Nodes
- 110+ node types
- Visitor pattern untuk traversal
- Semua node punya `accept(visitor)` method

### Semantic Analyzer
- Type checking
- Scope analysis
- Error detection
- Duplicate variable detection

### Optimizer
- Dead code elimination
- Constant folding
- Variable reference tracking
- Function analysis

### Interpreter
- Tree-walking interpreter
- Closures support
- Environment chain (scope)
- Runtime error handling

---

## 🧬 Visitor Pattern

BroLang pake **Visitor Pattern** buat traverse AST:

```python
class Interpreter:
    def visit(self, node):
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def visit_NumberNode(self, node):
        return node.value

    def visit_BinaryOpNode(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        # ...
```

**Setiap node types punya visitor method sendiri.** Ini bikin code lebih organized dan gampang di-extend.

## 🔗 References

- [CLI Documentation](CLI.md)
- [Fitur Lengkap](FITUR.md)
- [Standard Library](STDLIB.md)
