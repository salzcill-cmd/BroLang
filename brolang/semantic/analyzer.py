"""
Semantic Analyzer BroLang
==========================

Menganalisis AST untuk memastikan kebenaran semantik sebelum eksekusi.
Melewati semua node dan memeriksa:
- Variabel dideklarasikan sebelum digunakan
- Tidak ada deklarasi ganda dalam scope yang sama
- Fungsi dipanggil dengan jumlah argumen yang benar
- Tipe data kompatibel untuk operasi

Design:
    Menggunakan SymbolTable untuk tracking scope.
    Setiap scope baru (fungsi, kelas, if, loop) membuat
    child scope yang baru.
"""

from typing import List, Dict, Optional, Any, Set
from dataclasses import dataclass, field
from brolang.ast.nodes import (
    ASTNode, ASTVisitor,
    ProgramNode, NumberNode, DecimalNode, StringNode,
    BooleanNode, KosongNode, IdentifierNode, VariableNode,
    AssignmentNode, BinaryOpNode, UnaryOpNode,
    IfNode, WhileNode, ForNode, BreakNode, ContinueNode,
    FunctionNode, ReturnNode, CallNode,
    ClassNode, MethodNode, AttributeNode,
    ImportNode, FromImportNode,
    TryNode, CatchNode,
    ListNode, IndexNode, ObjectNode, ObjectAccessNode,
    PrintNode, InputNode,
    LambdaNode, ComprehensionNode, FStringNode,
    EnumNode, StructNode, StructInstanceNode,
    MatchNode, WildcardNode,
)
from brolang.exceptions import SemanticError


@dataclass
class SymbolInfo:
    """Informasi tentang sebuah symbol (variabel/fungsi/kelas)."""
    name: str
    kind: str  # "variable", "function", "class", "parameter"
    type_hint: Optional[str] = None
    line: int = 0
    column: int = 0
    is_initialized: bool = False


class SymbolTable:
    """Symbol table untuk tracking scope.

    Mengelola scope bertingkat dengan parent-child relationship.
    """

    def __init__(self, parent: Optional["SymbolTable"] = None, scope_name: str = "global"):
        self.symbols: Dict[str, SymbolInfo] = {}
        self.parent: Optional[SymbolTable] = parent
        self.children: List[SymbolTable] = []
        self.scope_name: str = scope_name

    def define(self, name: str, kind: str, line: int = 0, column: int = 0,
               type_hint: Optional[str] = None, is_initialized: bool = False) -> None:
        """Mendefinisikan symbol baru dalam scope ini."""
        if name in self.symbols:
            existing = self.symbols[name]
            raise SemanticError(
                message=f"'{name}' sudah dideklarasikan di scope ini.",
                line=line,
                column=column,
                solution=f"Ganti nama '{name}' dengan nama lain, atau hapus deklarasi sebelumnya (baris {existing.line}).",
                hint=f"Deklarasi sebelumnya di baris {existing.line}.",
            )
        self.symbols[name] = SymbolInfo(
            name=name,
            kind=kind,
            type_hint=type_hint,
            line=line,
            column=column,
            is_initialized=is_initialized,
        )

    def lookup(self, name: str) -> Optional[SymbolInfo]:
        """Mencari symbol di scope ini dan parent scope."""
        if name in self.symbols:
            return self.symbols[name]
        if self.parent is not None:
            return self.parent.lookup(name)
        return None

    def lookup_current(self, name: str) -> Optional[SymbolInfo]:
        """Mencari symbol hanya di scope saat ini."""
        return self.symbols.get(name)

    def is_defined(self, name: str) -> bool:
        """Memeriksa apakah symbol sudah didefinisikan."""
        return self.lookup(name) is not None

    def is_defined_current(self, name: str) -> bool:
        """Memeriksa apakah symbol sudah didefinisikan di scope saat ini."""
        return name in self.symbols

    def mark_initialized(self, name: str) -> None:
        """Menandai symbol sebagai sudah diinisialisasi."""
        info = self.lookup(name)
        if info:
            info.is_initialized = True


class SemanticAnalyzer(ASTVisitor):
    """Semantic Analyzer utama.

    Attributes:
        current_scope: Symbol table untuk scope saat ini
        errors: Daftar error yang ditemukan
        current_function: Nama fungsi saat ini (untuk return checking)
        current_class: Nama kelas saat ini (untuk method checking)
    """

    def __init__(self):
        self.current_scope: SymbolTable = SymbolTable(scope_name="global")
        self.errors: List[SemanticError] = []
        self.current_function: Optional[str] = None
        self.current_class: Optional[str] = None
        self._has_errors: bool = False
        self._loop_depth: int = 0

    def analyze(self, node: ASTNode) -> bool:
        """Menjalankan analisis semantik pada AST.

        Args:
            node: Root AST node (ProgramNode)

        Returns:
            bool: True jika tidak ada error
        """
        self._has_errors = False
        try:
            self.visit(node)
        except SemanticError as e:
            self.errors.append(e)
            self._has_errors = True
        return not self._has_errors

    def _error(self, message: str, line: int = 0, column: int = 0,
               solution: str = "", example: str = "") -> SemanticError:
        """Membuat SemanticError."""
        return SemanticError(
            message=message,
            line=line,
            column=column,
            solution=solution,
            example=example,
        )

    def _enter_scope(self, name: str = "block") -> SymbolTable:
        """Masuk ke scope baru."""
        new_scope = SymbolTable(parent=self.current_scope, scope_name=name)
        self.current_scope.children.append(new_scope)
        self.current_scope = new_scope
        return new_scope

    def _exit_scope(self) -> None:
        """Keluar dari scope saat ini."""
        if self.current_scope.parent is not None:
            self.current_scope = self.current_scope.parent

    # ============= Visitor Methods =============

    def visit_ProgramNode(self, node: ProgramNode) -> None:
        """Visit root program."""
        for stmt in node.statements:
            self.visit(stmt)

    def visit_NumberNode(self, node: NumberNode) -> str:
        return "angka"

    def visit_DecimalNode(self, node: DecimalNode) -> str:
        return "desimal"

    def visit_StringNode(self, node: StringNode) -> str:
        return "teks"

    def visit_BooleanNode(self, node: BooleanNode) -> str:
        return "boolean"

    def visit_KosongNode(self, node: KosongNode) -> str:
        return "kosong"

    def visit_IdentifierNode(self, node: IdentifierNode) -> Optional[str]:
        """Memeriksa identifier merujuk ke symbol yang terdefinisi."""
        info = self.current_scope.lookup(node.name)
        if info is None:
            # Check if it's a built-in function
            if node.name in ("input", "len", "angka", "teks", "desimal"):
                return None
            raise self._error(
                message=f"Variabel '{node.name}' belum didefinisikan.",
                line=node.line,
                column=node.column,
                solution=f"Tambahkan 'buat {node.name} = ...' sebelum menggunakan '{node.name}'.",
                example=f"buat {node.name} = nilai",
            )
        if not info.is_initialized and info.kind == "variable":
            pass  # Warn but don't error for now
        return info.type_hint

    def visit_VariableNode(self, node: VariableNode) -> None:
        self.visit_IdentifierNode(IdentifierNode(name=node.name, line=node.line, column=node.column))

    def visit_AssignmentNode(self, node: AssignmentNode) -> None:
        """Memeriksa assignment."""
        if isinstance(node.target, IdentifierNode):
            name = node.target.name

            if node.is_declaration:
                # Define new variable
                value_type = self.visit(node.value) if node.value else None
                self.current_scope.define(
                    name=name,
                    kind="variable",
                    line=node.line,
                    column=node.column,
                    type_hint=value_type,
                    is_initialized=True,
                )
            else:
                # Assignment to existing variable
                info = self.current_scope.lookup(name)
                if info is None:
                    raise self._error(
                        message=f"Variabel '{name}' belum dideklarasikan.",
                        line=node.line,
                        column=node.column,
                        solution=f"Deklarasikan '{name}' dengan 'buat {name} = ...' terlebih dahulu.",
                    )
                if node.value:
                    self.visit(node.value)
                self.current_scope.mark_initialized(name)
        else:
            # Array index assignment: list[0] = value
            if node.value:
                self.visit(node.value)

    def visit_BinaryOpNode(self, node: BinaryOpNode) -> str:
        """Memeriksa operasi biner."""
        left_type = self.visit(node.left)
        right_type = self.visit(node.right)

        op = node.operator

        # Skip type checking when return type is unknown
        if left_type is None or right_type is None:
            return "teks"

        # Numerical operations
        if op in ("+", "-", "*", "/", "%", "**"):
            if left_type in ("angka", "desimal") and right_type in ("angka", "desimal"):
                if left_type == "desimal" or right_type == "desimal":
                    return "desimal"
                return "angka"
            if op == "+" and left_type == "teks" and right_type == "teks":
                return "teks"
            if op == "+" and left_type == "teks":
                return "teks"
            if op == "*" and left_type == "teks" and right_type == "angka":
                return "teks"
            raise self._error(
                message=f"Operator '{op}' tidak bisa digunakan untuk tipe {left_type} dan {right_type}.",
                line=node.line,
                column=node.column,
                solution=f"Pastikan kedua operand memiliki tipe yang sesuai untuk operator '{op}'.",
            )

        # Comparison operations
        if op in ("==", "!=", ">", "<", ">=", "<="):
            if left_type == right_type:
                return "boolean"
            if left_type in ("angka", "desimal") and right_type in ("angka", "desimal"):
                return "boolean"
            return "boolean"

        # Logical operations
        if op in ("dan", "atau"):
            if left_type == "boolean" and right_type == "boolean":
                return "boolean"
            raise self._error(
                message=f"Operator '{op}' hanya bisa digunakan untuk tipe boolean.",
                line=node.line,
                column=node.column,
            )

        return "angka"

    def visit_UnaryOpNode(self, node: UnaryOpNode) -> str:
        """Memeriksa operasi unary."""
        operand_type = self.visit(node.operand)

        if node.operator == "-":
            if operand_type in ("angka", "desimal"):
                return operand_type
            raise self._error(
                message=f"Operator '-' tidak bisa digunakan untuk tipe {operand_type}.",
                line=node.line,
                column=node.column,
            )

        if node.operator == "bukan":
            if operand_type == "boolean":
                return "boolean"
            raise self._error(
                message=f"Operator 'bukan' hanya bisa digunakan untuk tipe boolean.",
                line=node.line,
                column=node.column,
            )

        if node.operator == "+":
            return operand_type

        return operand_type

    def visit_IfNode(self, node: IfNode) -> None:
        """Memeriksa if statement."""
        cond_type = self.visit(node.condition)
        if cond_type is not None and cond_type not in ("boolean", None):
            pass  # Allow implicit truthiness

        self._enter_scope("if")
        for stmt in node.body:
            self.visit(stmt)
        self._exit_scope()

        for cond, body in zip(node.elif_conditions, node.elif_bodies):
            self.visit(cond)
            self._enter_scope("elif")
            for stmt in body:
                self.visit(stmt)
            self._exit_scope()

        if node.else_body:
            self._enter_scope("else")
            for stmt in node.else_body:
                self.visit(stmt)
            self._exit_scope()

    def visit_WhileNode(self, node: WhileNode) -> None:
        """Memeriksa while loop."""
        self.visit(node.condition)
        self._loop_depth += 1
        self._enter_scope("while")
        for stmt in node.body:
            self.visit(stmt)
        self._exit_scope()
        self._loop_depth -= 1

    def visit_ForNode(self, node: ForNode) -> None:
        """Memeriksa for loop."""
        iter_type = self.visit(node.iterable)

        self._loop_depth += 1
        self._enter_scope("for")
        self.current_scope.define(
            name=node.variable,
            kind="variable",
            line=node.line,
            column=node.column,
            is_initialized=True,
        )
        for stmt in node.body:
            self.visit(stmt)
        self._exit_scope()
        self._loop_depth -= 1

    def visit_BreakNode(self, node: BreakNode) -> None:
        """Memeriksa break dalam loop."""
        if self._loop_depth == 0:
            raise self._error(
                message="'hentikan' harus digunakan di dalam loop.",
                line=node.line,
                column=node.column,
                solution="Gunakan 'hentikan' hanya di dalam 'untuk' atau 'selama'.",
                example="selama x < 10 lakukan\n    jika x == 5 maka\n        hentikan\n    selesai\nselesai",
            )

    def visit_ContinueNode(self, node: ContinueNode) -> None:
        """Memeriksa continue dalam loop."""
        if self._loop_depth == 0:
            raise self._error(
                message="'lanjutkan' harus digunakan di dalam loop.",
                line=node.line,
                column=node.column,
            )

    def visit_FunctionNode(self, node: FunctionNode) -> None:
        """Memeriksa deklarasi fungsi."""
        # Define function in current scope FIRST (for recursion support)
        self.current_scope.define(
            name=node.name,
            kind="function",
            line=node.line,
            column=node.column,
            is_initialized=True,
        )

        # Enter function scope
        old_function = self.current_function
        self.current_function = node.name
        self._enter_scope(f"function:{node.name}")

        # Define parameters
        for param in node.params:
            self.current_scope.define(
                name=param,
                kind="parameter",
                line=node.line,
                column=node.column,
                is_initialized=True,
                type_hint="angka",  # Default type for parameters
            )

        # Parse body
        for stmt in node.body:
            self.visit(stmt)

        self._exit_scope()
        self.current_function = old_function

    def visit_ReturnNode(self, node: ReturnNode) -> None:
        """Memeriksa return statement."""
        if self.current_function is None and self.current_class is None:
            raise self._error(
                message="'kembali' harus digunakan di dalam fungsi.",
                line=node.line,
                column=node.column,
                solution="Gunakan 'kembali' hanya di dalam blok 'fungsi'.",
            )
        if node.value:
            self.visit(node.value)

    def visit_CallNode(self, node: CallNode) -> Optional[str]:
        """Memeriksa pemanggilan fungsi."""
        # Check if it's a method call
        if node.is_method:
            return None  # Method return type unknown

        # Check function name
        if isinstance(node.function, IdentifierNode):
            func_name = node.function.name
            info = self.current_scope.lookup(func_name)
            if info is None and func_name not in ("input", "len", "angka", "teks", "desimal", "tulis", "range", "tipe", "jumlah", "peta", "saring"):
                raise self._error(
                    message=f"Fungsi '{func_name}' belum didefinisikan.",
                    line=node.line,
                    column=node.column,
                    solution=f"Buat fungsi '{func_name}' terlebih dahulu atau impor dari modul.",
                )

            # Known return types for built-in functions
            builtin_types = {
                "angka": "angka",
                "teks": "teks",
                "desimal": "desimal",
                "len": "angka",
                "tipe": "teks",
                "input": "teks",
                "range": "list",
                "jumlah": "angka",
            }
            if func_name in builtin_types:
                # Check arguments
                for arg in node.args:
                    self.visit(arg)
                return builtin_types[func_name]

        # Check arguments
        for arg in node.args:
            self.visit(arg)

        return None  # Return type unknown for user-defined functions

    def visit_ClassNode(self, node: ClassNode) -> None:
        """Memeriksa deklarasi kelas."""
        self.current_scope.define(
            name=node.name,
            kind="class",
            line=node.line,
            column=node.column,
            is_initialized=True,
        )

        old_class = self.current_class
        self.current_class = node.name
        self._enter_scope(f"class:{node.name}")

        # Define `self` parameter implicitly
        self.current_scope.define(
            name="self",
            kind="parameter",
            line=node.line,
            column=node.column,
            is_initialized=True,
        )

        # Parse methods
        for stmt in node.body:
            if isinstance(stmt, FunctionNode):
                self.visit(stmt)
            else:
                self.visit(stmt)

        self._exit_scope()
        self.current_class = old_class

    def visit_MethodNode(self, node: MethodNode) -> None:
        """Memeriksa method dalam kelas."""
        self._enter_scope(f"method:{node.name}")

        for param in node.params:
            self.current_scope.define(
                name=param,
                kind="parameter",
                line=node.line,
                column=node.column,
                is_initialized=True,
            )

        for stmt in node.body:
            self.visit(stmt)

        self._exit_scope()

    def visit_AttributeNode(self, node: AttributeNode) -> None:
        """Memeriksa akses atribut."""
        self.visit(node.object)

    def visit_ObjectAccessNode(self, node: ObjectAccessNode) -> str:
        """Memeriksa akses properti objek."""
        self.visit(node.object)
        return "teks"

    def visit_ImportNode(self, node: ImportNode) -> None:
        """Memeriksa import statement."""
        self.current_scope.define(
            name=node.module.split(".")[0],
            kind="module",
            line=node.line,
            column=node.column,
            is_initialized=True,
        )

    def visit_FromImportNode(self, node: FromImportNode) -> None:
        """Memeriksa from-import statement."""
        for name in node.names:
            self.current_scope.define(
                name=name,
                kind="function",
                line=node.line,
                column=node.column,
                is_initialized=True,
            )

    def visit_TryNode(self, node: TryNode) -> None:
        """Memeriksa try-catch."""
        self._enter_scope("try")
        for stmt in node.body:
            self.visit(stmt)
        self._exit_scope()

        self._enter_scope("catch")
        self.current_scope.define(
            name=node.catch_var,
            kind="variable",
            line=node.line,
            column=node.column,
            is_initialized=True,
        )
        for stmt in node.catch_body:
            self.visit(stmt)
        self._exit_scope()

    def visit_ListNode(self, node: ListNode) -> str:
        """Memeriksa list literal."""
        element_type = None
        for elem in node.elements:
            elem_type = self.visit(elem)
            if element_type is None:
                element_type = elem_type
        return "list"

    def visit_IndexNode(self, node: IndexNode) -> str:
        """Memeriksa indexing."""
        target_type = self.visit(node.target)
        index_type = self.visit(node.index)

        if target_type not in ("list", "teks"):
            raise self._error(
                message=f"Tipe {target_type} tidak bisa di-index.",
                line=node.line,
                column=node.column,
                solution="Indexing hanya untuk list dan string.",
            )

        if index_type not in ("angka", None):
            raise self._error(
                message="Indeks harus berupa angka.",
                line=node.line,
                column=node.column,
            )

        return "teks"

    def visit_ObjectNode(self, node: ObjectNode) -> str:
        """Memeriksa object literal."""
        for value in node.entries.values():
            self.visit(value)
        return "objek"

    def visit_PrintNode(self, node: PrintNode) -> None:
        """Memeriksa print statement."""
        self.visit(node.expression)
        for arg in node.args:
            self.visit(arg)

    def visit_InputNode(self, node: InputNode) -> str:
        """Memeriksa input statement."""
        if node.prompt:
            self.visit(node.prompt)
        return "teks"

    # ============= V2: Lambda =============

    def visit_LambdaNode(self, node: LambdaNode) -> str:
        """Memeriksa lambda expression."""
        self._enter_scope("lambda")
        for param in node.params:
            self.current_scope.define(
                name=param,
                kind="parameter",
                line=node.line,
                column=node.column,
                is_initialized=True,
            )
        self.visit(node.body)
        self._exit_scope()
        return "fungsi"

    # ============= V2: Comprehension =============

    def visit_ComprehensionNode(self, node: ComprehensionNode) -> str:
        """Memeriksa list comprehension."""
        self.visit(node.iterable)
        self._enter_scope("comprehension")
        self.current_scope.define(
            name=node.variable,
            kind="variable",
            line=node.line,
            column=node.column,
            is_initialized=True,
        )
        if node.condition:
            self.visit(node.condition)
        self.visit(node.expr)
        self._exit_scope()
        return "list"

    # ============= V2: F-String =============

    def visit_FStringNode(self, node: FStringNode) -> str:
        """Memeriksa f-string."""
        for ptype, pval in node.parts:
            if ptype == "expr" and isinstance(pval, ASTNode):
                self.visit(pval)
        return "teks"

    # ============= V2: Enum =============

    def visit_EnumNode(self, node: EnumNode) -> None:
        """Memeriksa enum declaration."""
        self.current_scope.define(
            name=node.name,
            kind="class",
            line=node.line,
            column=node.column,
            is_initialized=True,
        )

    # ============= V2: Struct =============

    def visit_StructNode(self, node: StructNode) -> None:
        """Memeriksa struktur declaration."""
        self.current_scope.define(
            name=node.name,
            kind="class",
            line=node.line,
            column=node.column,
            is_initialized=True,
        )

    def visit_StructInstanceNode(self, node: StructInstanceNode) -> str:
        """Memeriksa struktur instantiation."""
        info = self.current_scope.lookup(node.struct_name)
        if info is None:
            raise self._error(
                message=f"Struktur '{node.struct_name}' belum didefinisikan.",
                line=node.line,
                column=node.column,
                solution=f"Definisikan struktur '{node.struct_name}' terlebih dahulu.",
            )
        for arg in node.args:
            self.visit(arg)
        return node.struct_name

    # ============= V2: Match/Case =============

    def visit_MatchNode(self, node: MatchNode) -> None:
        """Memeriksa match/case."""
        self.visit(node.value)
        for pattern, body in node.cases:
            if not isinstance(pattern, WildcardNode):
                self.visit(pattern)
            self._enter_scope("match_case")
            for stmt in body:
                self.visit(stmt)
            self._exit_scope()
        if node.default_case:
            self._enter_scope("match_default")
            for stmt in node.default_case:
                self.visit(stmt)
            self._exit_scope()

    def visit_WildcardNode(self, node: WildcardNode) -> None:
        """Memeriksa wildcard."""
        pass
