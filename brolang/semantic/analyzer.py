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
    IfNode, WhileNode, ForNode, DoUntilNode, RangeForNode,
    BreakNode, ContinueNode,
    FunctionNode, ReturnNode, CallNode,
    ClassNode, MethodNode, AttributeNode,
    ImportNode, FromImportNode,
    TryNode, CatchNode,
    TypedExceptNode, MultiExceptNode,
    ListNode, IndexNode, ObjectNode, ObjectAccessNode,
    PrintNode, InputNode,
    ForEachNode,
    LambdaNode, ComprehensionNode, FStringNode,
    EnumNode, StructNode, StructInstanceNode,
    MatchNode, WildcardNode,
    AugmentedAssignmentNode, TernaryNode, RaiseNode,
    GlobalNode, NonlocalNode,
    PassNode, DelNode, AssertNode,
    TupleNode, SetNode, DictComprehensionNode,
    PipelineNode, DestructuringAssignmentNode,
    # V4 Nodes
    DecoratedFunctionNode, AsyncFunctionDefNode,
    # V6.0 Nodes
    KelasErrorNode, ObjectPatternNode, BindingPatternNode,
    DestructuringPatternNode, TypeAliasNode,
    # V6.7 Nodes
    SpreadNode,
    # V7.0 Nodes
    MultiAssignNode, ErrorPropagationNode, SwitchExprNode, AwaitNode,
    WalrusNode,
    # V7.2 Nodes
    NullSafeIndexNode, SetComprehensionNode,
)
from brolang.exceptions import SemanticError
from brolang.suggestions import saran_keyword


@dataclass
class SymbolInfo:
    """Informasi tentang sebuah symbol (variabel/fungsi/kelas)."""
    name: str
    kind: str  # "variable", "function", "class", "parameter"
    type_hint: Optional[str] = None
    line: int = 0
    column: int = 0
    is_initialized: bool = False
    is_const: bool = False  # v6.5: 'konstanta x = 5'


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
               type_hint: Optional[str] = None, is_initialized: bool = False,
               is_const: bool = False) -> None:
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
            is_const=is_const,
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
        self._current_return_type: Optional[str] = None  # v6.0: `fungsi f() -> Tipe`

    def analyze(self, node: ASTNode) -> bool:
        """Menjalankan analisis semantik pada AST.

        Args:
            node: Root AST node (ProgramNode)

        Returns:
            bool: True jika tidak ada error
        """
        self._has_errors = False
        # Scope global di-reset tiap panggilan supaya analyze() re-entrant
        # (bisa dipanggil berkali-kali pada instance yang sama).
        self.current_scope = SymbolTable(scope_name="global")
        # v6.0: `Kesalahan` adalah kelas dasar error kustom bawaan
        # (didefinisikan di interpreter & transpiler) — daftarkan sebagai
        # simbol kelas global supaya `lempar Kesalahan(...)` valid.
        self.current_scope.define(
            name="Kesalahan", kind="class", line=0, column=0, is_initialized=True,
        )
        try:
            self.visit(node)
        except SemanticError as e:
            self.errors.append(e)
            self._has_errors = True
        return not self._has_errors

    # ============= V6.0: Type System =============

    _TIPE_PEMETAAN = {
        "Angka": ("angka", "desimal"),
        "Desimal": ("desimal",),
        "Teks": ("teks",),
        "String": ("teks",),
        "Boolean": ("boolean",),
        "Daftar": ("list",),
        "List": ("list",),
        "Array": ("list",),
        "Objek": ("objek",),
        "Dict": ("objek",),
        "Map": ("objek",),
        "Tupel": ("tuple",),
        "Tuple": ("tuple",),
        "Set": ("set",),
        "Kosong": ("kosong",),
        "Null": ("kosong",),
    }

    def _tipe_dari_anotasi(self, anotasi: Optional[str]) -> Optional[str]:
        """Konversi anotasi tipe v6.0 → nama tipe analyzer (atau None jika tak dikenal)."""
        if not anotasi:
            return None
        anotasi = anotasi.strip()
        if anotasi in ("ApaSaja", "Any"):
            return None
        if "|" in anotasi:
            return None  # union — tipe dinamis, tidak bisa dipastikan statis
        if "<" in anotasi:  # generik: Daftar<Angka>
            anotasi = anotasi[:anotasi.index("<")].strip()
        if anotasi in self._TIPE_PEMETAAN:
            return self._TIPE_PEMETAAN[anotasi][0]
        return None  # kelas user / alias — tidak diketahui statis

    def _anotasi_cocok(self, nilai_tipe: Optional[str], anotasi: Optional[str]) -> bool:
        """Cek statis apakah tipe nilai cocok dengan anotasi v6.0.

        Mengembalikan True bila tipe tidak bisa dipastikan (None) supaya
        tidak ada false-positive; penegakan runtime tetap di interpreter.
        """
        if not anotasi or nilai_tipe is None:
            return True
        # `kosong` (null) cocok dengan anotasi apa pun — pola "tidak
        # ditemukan → kembali kosong" sangat umum; interpreter tidak
        # menegakkan tipe return sama sekali.
        if nilai_tipe == "kosong":
            return True
        anotasi = anotasi.strip()
        if anotasi in ("ApaSaja", "Any"):
            return True
        if "|" in anotasi:  # union: Angka | Teks
            return any(
                self._anotasi_cocok(nilai_tipe, bagian.strip())
                for bagian in anotasi.split("|")
            )
        if "<" in anotasi:  # generik: Daftar<Angka> — cek tipe dasar
            anotasi = anotasi[:anotasi.index("<")].strip()
        if anotasi in self._TIPE_PEMETAAN:
            return nilai_tipe in self._TIPE_PEMETAAN[anotasi]
        return True  # alias / kelas user — serahkan ke runtime

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
            message = f"Variabel '{node.name}' belum didefinisikan."
            message += saran_keyword(node.name)
            raise self._error(
                message=message,
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
                # v6.0: `buat x: Angka = 5` — cek statis kalau tipe nilai diketahui
                if not self._anotasi_cocok(value_type, node.type_annotation):
                    raise self._error(
                        message=f"Tipe tidak cocok untuk '{name}': diharapkan "
                                f"{node.type_annotation}, tapi mendapat {value_type or 'tak dikenal'}.",
                        line=node.line,
                        column=node.column,
                        solution=f"Ubah nilai menjadi {node.type_annotation} atau ubah anotasi tipe.",
                    )
                # v6.5: `konstanta x = 5` — tandai sebagai immutable
                self.current_scope.define(
                    name=name,
                    kind="variable",
                    line=node.line,
                    column=node.column,
                    type_hint=value_type,
                    is_initialized=True,
                    is_const=node.is_const,
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
                # v6.5: konstanta tidak bisa diubah
                if info.is_const:
                    raise self._error(
                        message=f"Konstanta '{name}' tidak bisa diubah.",
                        line=node.line,
                        column=node.column,
                        solution=f"Hapus assignment ke '{name}' atau ubah deklarasi menjadi 'buat {name} = ...'.",
                        example=f"konstanta {name} = 10\n{name} = 20  # error!",
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
            return None

        # Numerical operations (v6.8: // floor division)
        if op in ("+", "-", "*", "/", "//", "%", "**"):
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
            if op == "+" and left_type == "list" and right_type == "list":
                return "list"
            if op == "+" and left_type == "list":
                return "list"
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

        # Bitwise operations
        if op in ("&", "|", "^", "<<", ">>"):
            if left_type is None or right_type is None:
                return None
            if left_type in ("angka", "desimal") and right_type in ("angka", "desimal"):
                return "angka"
            raise self._error(
                message=f"Operator '{op}' hanya bisa digunakan untuk tipe angka.",
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
            # bukan works with any type (like Python's not)
            return "boolean"

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

    def visit_ForEachNode(self, node: ForEachNode) -> None:
        """Memeriksa for-each: untuk setiap item dalam iterable (v6.7 fix)."""
        self.visit(node.iterable)

        self._loop_depth += 1
        self._enter_scope("for_each")
        self.current_scope.define(
            name=node.variable,
            kind="variable",
            line=node.line,
            column=node.column,
            is_initialized=True,
        )
        if node.index_variable:
            self.current_scope.define(
                name=node.index_variable,
                kind="variable",
                line=node.line,
                column=node.column,
                is_initialized=True,
            )
        for stmt in node.body:
            self.visit(stmt)
        self._exit_scope()
        self._loop_depth -= 1

    def visit_DoUntilNode(self, node: DoUntilNode) -> None:
        """Memeriksa do-until loop (v6.5): ulangi ... sampai kondisi."""
        self._loop_depth += 1
        self._enter_scope("do_until")
        for stmt in node.body:
            self.visit(stmt)
        self._exit_scope()
        self.visit(node.condition)
        self._loop_depth -= 1

    def visit_RangeForNode(self, node: RangeForNode) -> None:
        """Memeriksa range for loop (v6.5): untuk i dari 1 sampai 10."""
        self.visit(node.start)
        self.visit(node.end)
        if node.step:
            self.visit(node.step)

        self._loop_depth += 1
        self._enter_scope("range_for")
        self.current_scope.define(
            name=node.variable,
            kind="variable",
            line=node.line,
            column=node.column,
            is_initialized=True,
        )
        for stmt in node.body:
            self.visit(stmt)
        if node.else_body:
            for stmt in node.else_body:
                self.visit(stmt)
        self._exit_scope()
        self._loop_depth -= 1

    def visit_BreakNode(self, node: BreakNode) -> None:
        """Memeriksa break dalam loop. (v6.8: guard `hentikan jika x`)"""
        if self._loop_depth == 0:
            raise self._error(
                message="'hentikan' harus digunakan di dalam loop.",
                line=node.line,
                column=node.column,
                solution="Gunakan 'hentikan' hanya di dalam 'untuk' atau 'selama'.",
                example="selama x < 10 lakukan\n    jika x == 5 maka\n        hentikan\n    selesai\nselesai",
            )
        guard = getattr(node, "guard", None)
        if guard is not None:
            self.visit(guard)

    def visit_ContinueNode(self, node: ContinueNode) -> None:
        """Memeriksa continue dalam loop. (v6.8: guard `lanjutkan jika x`)"""
        if self._loop_depth == 0:
            raise self._error(
                message="'lanjutkan' harus digunakan di dalam loop.",
                line=node.line,
                column=node.column,
            )
        guard = getattr(node, "guard", None)
        if guard is not None:
            self.visit(guard)

    def visit_PassNode(self, node: PassNode) -> None:
        """Pass statement - no-op."""
        pass

    def visit_DelNode(self, node: DelNode) -> None:
        """Del statement."""
        self.visit(node.target)

    def visit_AssertNode(self, node: AssertNode) -> None:
        """Assert statement."""
        self.visit(node.condition)
        if node.message:
            self.visit(node.message)

    def visit_TupleNode(self, node: TupleNode) -> str:
        """Tuple literal type."""
        for elem in node.elements:
            self.visit(elem)
        return "tuple"

    def visit_SetNode(self, node: SetNode) -> None:
        """Set literal."""
        for elem in node.elements:
            self.visit(elem)

    def visit_DictComprehensionNode(self, node: DictComprehensionNode) -> None:
        """Dict comprehension."""
        self.visit(node.iterable)
        self._enter_scope("dict_comprehension")
        self.current_scope.define(
            name=node.key_var,
            kind="variable",
            line=node.line,
            column=node.column,
            is_initialized=True,
        )
        if node.value_var:
            self.current_scope.define(
                name=node.value_var,
                kind="variable",
                line=node.line,
                column=node.column,
                is_initialized=True,
            )
        if node.condition:
            self.visit(node.condition)
        self.visit(node.key_expr)
        self.visit(node.value_expr)
        self._exit_scope()

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

        # Define parameters (v6.0: hormati anotasi tipe `a: Angka`)
        param_types = getattr(node, 'param_types', None) or []
        for i, param in enumerate(node.params):
            anotasi = param_types[i] if i < len(param_types) else None
            type_hint = self._tipe_dari_anotasi(anotasi) or "angka"
            if i < len(node.defaults) and node.defaults[i] is not None:
                default_type = self.visit(node.defaults[i])
                if not self._anotasi_cocok(default_type, anotasi):
                    raise self._error(
                        message=f"Nilai default parameter '{param}' tidak cocok "
                                f"dengan tipe {anotasi}.",
                        line=node.line,
                        column=node.column,
                        solution=f"Ubah nilai default menjadi {anotasi}.",
                    )
            self.current_scope.define(
                name=param,
                kind="parameter",
                line=node.line,
                column=node.column,
                is_initialized=True,
                type_hint=type_hint,
            )

        # v6.7: rest parameter `...sisa` — tangkap argumen tambahan sebagai list
        rest_param = getattr(node, 'rest_param', None)
        if rest_param:
            self.current_scope.define(
                name=rest_param,
                kind="parameter",
                line=node.line,
                column=node.column,
                is_initialized=True,
            )

        # v6.0: return type `fungsi f() -> Angka` — cek di visit_ReturnNode
        old_return_type = self._current_return_type
        self._current_return_type = getattr(node, 'return_type', None)

        # Validasi: default parameter tidak boleh mendahului parameter non-default
        seen_default = False
        for i, param in enumerate(node.params):
            has_default = i < len(node.defaults) and node.defaults[i] is not None
            if has_default:
                seen_default = True
            elif seen_default:
                raise self._error(
                    message=f"Parameter '{param}' tidak boleh tanpa nilai default setelah parameter ber-default.",
                    line=node.line,
                    column=node.column,
                    solution="Letakkan parameter dengan nilai default di akhir daftar parameter.",
                    example=f"fungsi {node.name}(a=1, {param})  ->  fungsi {node.name}({param}, a=1)",
                )

        # Parse body
        for stmt in node.body:
            self.visit(stmt)

        self._exit_scope()
        self.current_function = old_function
        self._current_return_type = old_return_type

    def visit_DecoratedFunctionNode(self, node: DecoratedFunctionNode) -> None:
        """Fungsi berdekorator: cek decorator lalu periksa seperti fungsi
        biasa (v6.7 — sebelumnya analyzer tidak mengenali ini sebagai
        konteks fungsi, sehingga 'kembali' di dalamnya ditolak)."""
        for dec in node.decorators:
            self.visit(dec)
        self.visit_FunctionNode(node)

    def visit_AsyncFunctionDefNode(self, node: AsyncFunctionDefNode) -> None:
        """Memeriksa deklarasi fungsi asinkron (v7.0) — diperlakukan sebagai
        konteks fungsi agar 'kembali'/'tunggu' di dalamnya valid."""
        self.current_scope.define(
            name=node.name,
            kind="function",
            line=node.line,
            column=node.column,
            is_initialized=True,
        )
        old_function = self.current_function
        self.current_function = node.name
        self._enter_scope(f"async:{node.name}")
        for i, param in enumerate(node.params):
            self.current_scope.define(
                name=param,
                kind="parameter",
                line=node.line,
                column=node.column,
                is_initialized=True,
            )
        rest_param = getattr(node, "rest_param", None)
        if rest_param:
            self.current_scope.define(
                name=rest_param,
                kind="parameter",
                line=node.line,
                column=node.column,
                is_initialized=True,
            )
        for stmt in node.body:
            self.visit(stmt)
        self._exit_scope()
        self.current_function = old_function

    def visit_ReturnNode(self, node: ReturnNode) -> None:
        """Memeriksa return statement (v6.0: cek cocok dengan `-> Tipe`).
        v6.8: guard `kembali x jika c` — kondisi ikut diperiksa."""
        if self.current_function is None and self.current_class is None:
            raise self._error(
                message="'kembali' harus digunakan di dalam fungsi.",
                line=node.line,
                column=node.column,
                solution="Gunakan 'kembali' hanya di dalam blok 'fungsi'.",
            )
        guard = getattr(node, "guard", None)
        if guard is not None:
            self.visit(guard)
        if node.value:
            nilai_type = self.visit(node.value)
            if not self._anotasi_cocok(nilai_type, self._current_return_type):
                raise self._error(
                    message=f"Nilai kembali tidak cocok dengan tipe return "
                            f"{self._current_return_type} (mendapat {nilai_type or 'tak dikenal'}).",
                    line=node.line,
                    column=node.column,
                    solution=f"Ubah nilai kembali menjadi {self._current_return_type}.",
                )

    def visit_CallNode(self, node: CallNode) -> Optional[str]:
        """Memeriksa pemanggilan fungsi."""
        # Check if it's a method call
        if node.is_method:
            return None  # Method return type unknown

        # Check function name
        if isinstance(node.function, IdentifierNode):
            func_name = node.function.name
            info = self.current_scope.lookup(func_name)
            if info is None and func_name not in ("input", "len", "angka", "teks", "desimal", "tulis", "range", "tipe", "jumlah", "peta", "saring", "cek_tipe", "pastikan", "zip", "enumerate", "min", "max", "urutkan", "terbalik", "ada", "semua", "isinstance", "punya", "id", "hash", "abs", "round", "panjang", "boolean", "angka_desimal", "hentikan_iterasi"):
                message = f"Fungsi '{func_name}' belum didefinisikan."
                message += saran_keyword(func_name)
                raise self._error(
                    message=message,
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

        # Check arguments (termasuk nilai keyword arguments)
        for arg in node.args:
            self.visit(arg)
        for _, kwarg_value in node.kwargs:
            self.visit(kwarg_value)

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

    def visit_TypeAliasNode(self, node: TypeAliasNode) -> None:
        """Type alias: `tipe ID = Angka` — daftarkan nama tipe.

        Definition berisi nama tipe (Angka, Teks, Daftar<Angka>, ...) yang
        bukan variabel runtime — jadi tidak di-visit sebagai lookup variabel
        (kalau di-visit, analyzer salah melaporkan 'Variabel Angka belum
        didefinisikan').
        """
        self.current_scope.define(
            name=node.name,
            kind="type",
            line=node.line,
            column=node.column,
            is_initialized=True,
        )

    def visit_KelasErrorNode(self, node: KelasErrorNode) -> None:
        """v6.0: `kelas_error Nama extends Induk` — daftarkan kelas error."""
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
        """Memeriksa method dalam kelas (v6.7: dukung rest param)."""
        self._enter_scope(f"method:{node.name}")

        for param in node.params:
            self.current_scope.define(
                name=param,
                kind="parameter",
                line=node.line,
                column=node.column,
                is_initialized=True,
            )
        if node.rest_param:
            self.current_scope.define(
                name=node.rest_param,
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

    def visit_ObjectAccessNode(self, node: ObjectAccessNode) -> Optional[str]:
        """Memeriksa akses properti objek."""
        self.visit(node.object)
        return None

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
        """Memeriksa try-catch-finally."""
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

        if node.finally_body:
            self._enter_scope("finally")
            for stmt in node.finally_body:
                self.visit(stmt)
            self._exit_scope()

    def visit_MultiExceptNode(self, node: MultiExceptNode) -> None:
        """Memeriksa coba...kecuali... (multiple except clauses)."""
        self._enter_scope("try")
        for stmt in node.body:
            self.visit(stmt)
        self._exit_scope()

        # Setiap klausa kecuali punya scope sendiri + variabel exception
        for clause in node.except_clauses:
            self._enter_scope("except")
            self.current_scope.define(
                name=clause.variable,
                kind="variable",
                line=clause.line,
                column=clause.column,
                is_initialized=True,
            )
            for stmt in clause.body:
                self.visit(stmt)
            self._exit_scope()

        if node.else_body:
            self._enter_scope("else")
            for stmt in node.else_body:
                self.visit(stmt)
            self._exit_scope()

        if node.finally_body:
            self._enter_scope("finally")
            for stmt in node.finally_body:
                self.visit(stmt)
            self._exit_scope()

    def visit_TypedExceptNode(self, node: TypedExceptNode) -> None:
        """Klausa kecuali — ditangani visit_MultiExceptNode."""
        pass

    def visit_ListNode(self, node: ListNode) -> str:
        """Memeriksa list literal."""
        element_type = None
        for elem in node.elements:
            elem_type = self.visit(elem)
            if element_type is None:
                element_type = elem_type
        return "list"

    def visit_IndexNode(self, node: IndexNode) -> str:
        """Memeriksa indexing (v6.0: objek di-index dengan kunci teks)."""
        target_type = self.visit(node.target)
        index_type = self.visit(node.index)

        # Tipe target tak dikenal (mis. hasil pemanggilan fungsi) — serahkan
        # ke runtime, jangan sampai false-positive.
        if target_type is None:
            return None

        # Objek (dict) di-index dengan kunci teks — konsisten dengan interpreter
        if target_type == "objek":
            if index_type not in ("teks", "angka", None):
                raise self._error(
                    message="Indeks objek harus berupa kunci teks.",
                    line=node.line,
                    column=node.column,
                )
            return None

        if target_type not in ("list", "teks", "tuple"):
            raise self._error(
                message=f"Tipe {target_type} tidak bisa di-index.",
                line=node.line,
                column=node.column,
                solution="Indexing hanya untuk list, string, tuple, dan objek.",
            )

        if index_type not in ("angka", None):
            raise self._error(
                message="Indeks harus berupa angka.",
                line=node.line,
                column=node.column,
            )

        return None

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
        """Memeriksa lambda expression (v6.7: dukung rest param)."""
        self._enter_scope("lambda")
        for param in node.params:
            self.current_scope.define(
                name=param,
                kind="parameter",
                line=node.line,
                column=node.column,
                is_initialized=True,
            )
        if node.rest_param:
            self.current_scope.define(
                name=node.rest_param,
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
        """Memeriksa match/case (v6.0: binding pattern + guard)."""
        self.visit(node.value)
        guards = getattr(node, 'guards', None) or []
        for idx, (pattern, body) in enumerate(node.cases):
            self._enter_scope("match_case")
            # Pola binding (v6.0) mendefinisikan variabel yang dipakai
            # di body & guard: `[a, b]: ...` atau `x jika x > 10: ...`
            if not isinstance(pattern, WildcardNode):
                self.visit(pattern)
            if idx < len(guards) and guards[idx] is not None:
                self.visit(guards[idx])
            for stmt in body:
                self.visit(stmt)
            self._exit_scope()
        if node.default_case:
            self._enter_scope("match_default")
            for stmt in node.default_case:
                self.visit(stmt)
            self._exit_scope()

    # ============= V6.0: Pattern Binding =============

    def visit_BindingPatternNode(self, node: BindingPatternNode) -> None:
        """Pola binding `n:` — variabel menangkap seluruh nilai."""
        self.current_scope.define(
            name=node.name,
            kind="variable",
            line=node.line,
            column=node.column,
            is_initialized=True,
        )

    def visit_DestructuringPatternNode(self, node: DestructuringPatternNode) -> None:
        """Pola destructuring `[a, b]` / `{x, y}` — definisikan semua target."""
        for name in node.variables:
            self.current_scope.define(
                name=name,
                kind="variable",
                line=node.line,
                column=node.column,
                is_initialized=True,
            )

    def visit_ObjectPatternNode(self, node: ObjectPatternNode) -> None:
        """Pola objek `{"x": a, "y": b}` — definisikan variabel binding."""
        for entry in node.entries.values():
            if isinstance(entry, tuple) and entry and entry[0] == "var":
                self.current_scope.define(
                    name=entry[1],
                    kind="variable",
                    line=node.line,
                    column=node.column,
                    is_initialized=True,
                )
            elif isinstance(entry, str):
                self.current_scope.define(
                    name=entry,
                    kind="variable",
                    line=node.line,
                    column=node.column,
                    is_initialized=True,
                )

    def visit_WildcardNode(self, node: WildcardNode) -> None:
        """Memeriksa wildcard."""
        pass

    # ============= V3: Augmented Assignment =============

    def visit_AugmentedAssignmentNode(self, node: AugmentedAssignmentNode) -> None:
        """Memeriksa augmented assignment: x += 1, x -= 2, dll. (v6.5: konstanta ditolak)"""
        if isinstance(node.target, IdentifierNode):
            name = node.target.name
            info = self.current_scope.lookup(name)
            if info is None:
                raise self._error(
                    message=f"Variabel '{name}' belum dideklarasikan.",
                    line=node.line,
                    column=node.column,
                    solution=f"Deklarasikan '{name}' dengan 'buat {name} = ...' terlebih dahulu.",
                )
            if info.is_const:
                raise self._error(
                    message=f"Konstanta '{name}' tidak bisa diubah.",
                    line=node.line,
                    column=node.column,
                    solution=f"Hapus assignment ke '{name}' atau ubah deklarasi menjadi 'buat {name} = ...'.",
                )
        self.visit(node.value)

    # ============= V3: Ternary Expression =============

    def visit_TernaryNode(self, node: TernaryNode) -> str:
        """Memeriksa ternary expression."""
        self.visit(node.condition)
        true_type = self.visit(node.true_value)
        false_type = self.visit(node.false_value)
        if true_type and false_type:
            return true_type
        return None

    # ============= V3: Raise Statement =============

    def visit_RaiseNode(self, node: RaiseNode) -> None:
        """Memeriksa raise statement."""
        self.visit(node.value)

    # ============= V3: Global/Nonlocal =============

    def visit_GlobalNode(self, node: GlobalNode) -> None:
        """Memeriksa global statement."""
        for name in node.names:
            info = self.current_scope.lookup(name)
            if info is None:
                self.current_scope.define(
                    name=name,
                    kind="variable",
                    line=node.line,
                    column=node.column,
                    is_initialized=True,
                )

    def visit_NonlocalNode(self, node: NonlocalNode) -> None:
        """Memeriksa nonlocal statement."""
        for name in node.names:
            info = self.current_scope.lookup(name)
            if info is None:
                self.current_scope.define(
                    name=name,
                    kind="variable",
                    line=node.line,
                    column=node.column,
                    is_initialized=True,
                )

    # ============= V5.2: Pipeline & Destructuring =============

    def visit_PipelineNode(self, node: PipelineNode) -> Optional[str]:
        """Memeriksa pipeline: nilai | > fungsi  =>  fungsi(nilai)."""
        self.visit(node.left)
        self.visit(node.right)
        return None

    # ============= V6.7: Spread Operator =============

    def visit_SpreadNode(self, node: SpreadNode) -> str:
        """Memeriksa spread operator (v6.7): ...nilai."""
        self.visit(node.value)
        return "list"

    def visit_DestructuringAssignmentNode(self, node: DestructuringAssignmentNode) -> None:
        """Memeriksa destructuring assignment: buat [a, b] = list / buat {x, y} = objek."""
        if node.value:
            self.visit(node.value)
        # Definisikan semua variabel target dalam scope saat ini
        for name in node.targets:
            self.current_scope.define(
                name=name,
                kind="variable",
                line=node.line,
                column=node.column,
                is_initialized=True,
            )

    def visit_MultiAssignNode(self, node: MultiAssignNode) -> None:
        """Memeriksa multiple assignment (v7.0): a, b = 1, 2 / a, b = b, a."""
        for v in node.values:
            self.visit(v)
        for name in node.targets:
            if node.is_declaration:
                self.current_scope.define(
                    name=name,
                    kind="variable",
                    line=node.line,
                    column=node.column,
                    is_initialized=True,
                )
            else:
                info = self.current_scope.lookup(name)
                if info is None:
                    raise self._error(
                        message=f"Variabel '{name}' belum dideklarasikan.",
                        line=node.line,
                        column=node.column,
                        solution=f"Deklarasikan '{name}' dengan 'buat {name} = ...' terlebih dahulu.",
                    )
                if info.is_const:
                    raise self._error(
                        message=f"Konstanta '{name}' tidak bisa diubah.",
                        line=node.line,
                        column=node.column,
                        solution=f"Hapus assignment ke '{name}' atau ubah deklarasi menjadi 'buat {name} = ...'.",
                    )
                self.current_scope.mark_initialized(name)

    def visit_ErrorPropagationNode(self, node: ErrorPropagationNode) -> str:
        """Memeriksa error propagation (v7.0): ekspresi?"""
        return self.visit(node.value)

    def visit_WalrusNode(self, node: WalrusNode) -> str:
        """Memeriksa walrus operator (v7.2): x := nilai — assignment di
        dalam ekspresi; variabel didefinisikan di scope saat ini."""
        self.visit(node.value)
        if not self.current_scope.is_defined(node.name):
            self.current_scope.define(
                name=node.name,
                kind="variable",
                line=node.line,
                column=node.column,
                is_initialized=True,
            )
        else:
            self.current_scope.mark_initialized(node.name)
        return "angka"

    def visit_SetComprehensionNode(self, node: SetComprehensionNode) -> str:
        """Memeriksa set comprehension (v7.2)."""
        self.visit(node.iterable)
        self._enter_scope("set_comprehension")
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
        return "set"

    def visit_NullSafeIndexNode(self, node: NullSafeIndexNode) -> str:
        """Memeriksa null-safe indexing (v7.2): ekspresi?[indeks]"""
        self.visit(node.target)
        self.visit(node.index)
        return "kosong?"

    def visit_AwaitNode(self, node: AwaitNode) -> str:
        """Memeriksa await (v7.0): tunggu ekspresi."""
        return self.visit(node.value)

    def visit_SwitchExprNode(self, node: SwitchExprNode) -> str:
        """Memeriksa switch expression (v7.0): cocokkan nilai { pola: ekspresi }."""
        self.visit(node.value)
        for pattern, body in node.cases:
            if isinstance(pattern, ASTNode):
                self.visit(pattern)
            for stmt in body:
                self.visit(stmt)
        if node.default_case is not None:
            self.visit(node.default_case)
        return "tak dikenal"
