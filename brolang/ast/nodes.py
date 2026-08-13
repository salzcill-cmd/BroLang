"""
Definisi Node AST BroLang
=========================

Setiap node AST mewakili konstruksi bahasa BroLang.
Menggunakan dataclass untuk kesederhanaan dan readability.
Mendukung visitor pattern untuk traversal.
"""

from dataclasses import dataclass, field
from typing import Any, List, Optional, TypeVar, Generic, Dict, Callable

T = TypeVar("T")


class ASTVisitor:
    """Visitor pattern untuk AST traversal.

    Penggunaan:
        class MyVisitor(ASTVisitor):
            def visit_ProgramNode(self, node):
                for child in node.statements:
                    self.visit(child)

            def visit_NumberNode(self, node):
                print(f"Number: {node.value}")
    """

    def visit(self, node: "ASTNode") -> Any:
        """Kunjungi sebuah node AST.

        Method dispatch dilakukan berdasarkan nama class node.
        """
        method_name = f"visit_{node.__class__.__name__}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node: "ASTNode") -> None:
        """Default visitor jika tidak ada method spesifik."""
        for child in node.get_children():
            if isinstance(child, ASTNode):
                self.visit(child)
            elif isinstance(child, list):
                for item in child:
                    if isinstance(item, ASTNode):
                        self.visit(item)


@dataclass
class ASTNode:
    """Base class untuk semua node AST.

    Setiap node memiliki informasi posisi (line, column)
    untuk error reporting yang akurat.
    """
    line: int = 0
    column: int = 0

    def get_children(self) -> List[Any]:
        """Mengembalikan daftar child nodes."""
        return []

    def accept(self, visitor: ASTVisitor) -> Any:
        """Accept visitor (alternative dispatch)."""
        return visitor.visit(self)


# ============= Literals =============

@dataclass
class NumberNode(ASTNode):
    """Node untuk literal angka integer."""
    value: int = 0

    def get_children(self) -> List[Any]:
        return []


@dataclass
class DecimalNode(ASTNode):
    """Node untuk literal angka desimal."""
    value: float = 0.0

    def get_children(self) -> List[Any]:
        return []


@dataclass
class StringNode(ASTNode):
    """Node untuk literal string."""
    value: str = ""

    def get_children(self) -> List[Any]:
        return []


@dataclass
class BooleanNode(ASTNode):
    """Node untuk literal boolean."""
    value: bool = False

    def get_children(self) -> List[Any]:
        return []


@dataclass
class KosongNode(ASTNode):
    """Node untuk literal kosong/null."""
    def get_children(self) -> List[Any]:
        return []


# ============= Variables =============

@dataclass
class IdentifierNode(ASTNode):
    """Node untuk identifier (nama variabel, fungsi, dll)."""
    name: str = ""

    def get_children(self) -> List[Any]:
        return []


@dataclass
class AssignmentNode(ASTNode):
    """Node untuk assignment: buat x = nilai (v6.0: buat x: Tipe = nilai; v6.5: konstanta)"""
    target: ASTNode = field(default_factory=lambda: IdentifierNode(""))
    value: ASTNode = field(default_factory=lambda: NumberNode())
    is_declaration: bool = True
    type_annotation: Optional[str] = None  # v6.0: 'buat x: Angka = 5'
    is_const: bool = False  # v6.5: 'konstanta x = 5' (immutable)

    def get_children(self) -> List[Any]:
        return [self.target, self.value]


@dataclass
class VariableNode(ASTNode):
    """Node untuk referensi variabel."""
    name: str = ""

    def get_children(self) -> List[Any]:
        return []


# ============= Operations =============

@dataclass
class BinaryOpNode(ASTNode):
    """Node untuk operasi biner: kiri + kanan, kiri == kanan, dll."""
    left: ASTNode = field(default_factory=lambda: NumberNode())
    operator: str = "+"
    right: ASTNode = field(default_factory=lambda: NumberNode())

    def get_children(self) -> List[Any]:
        return [self.left, self.right]


@dataclass
class UnaryOpNode(ASTNode):
    """Node untuk operasi unary: -angka, bukan kondisi"""
    operator: str = "-"
    operand: ASTNode = field(default_factory=lambda: NumberNode())

    def get_children(self) -> List[Any]:
        return [self.operand]


# ============= Control Flow =============

@dataclass
class IfNode(ASTNode):
    """Node untuk if-else: jika kondisi maka ... lainnya ... selesai"""
    condition: ASTNode = field(default_factory=lambda: BooleanNode())
    body: List[ASTNode] = field(default_factory=list)
    else_body: List[ASTNode] = field(default_factory=list)
    elif_conditions: List[ASTNode] = field(default_factory=list)
    elif_bodies: List[List[ASTNode]] = field(default_factory=list)

    def get_children(self) -> List[Any]:
        children = [self.condition] + self.body
        for ec, eb in zip(self.elif_conditions, self.elif_bodies):
            children.append(ec)
            children.extend(eb)
        children.extend(self.else_body)
        return children


@dataclass
class WhileNode(ASTNode):
    """Node untuk while loop: selama kondisi lakukan ... lainnya ... selesai"""
    condition: ASTNode = field(default_factory=lambda: BooleanNode())
    body: List[ASTNode] = field(default_factory=list)
    else_body: Optional[List[ASTNode]] = None

    def get_children(self) -> List[Any]:
        children = [self.condition] + self.body
        if self.else_body:
            children.extend(self.else_body)
        return children


# ============= V6.5: Do-Until Loop =============

@dataclass
class DoUntilNode(ASTNode):
    """Node untuk do-until loop (v6.5): ulangi ... sampai kondisi

    Body dijalankan minimal sekali, lalu kondisi dicek setelah body:
        ulangi
            tulis x
            x = x + 1
        sampai x >= 10
    """
    body: List[ASTNode] = field(default_factory=list)
    condition: ASTNode = field(default_factory=lambda: BooleanNode())

    def get_children(self) -> List[Any]:
        return self.body + [self.condition]


# ============= V6.5: Range For Loop =============

@dataclass
class RangeForNode(ASTNode):
    """Node untuk range for loop (v6.5): untuk i dari 1 sampai 10 langkah 2

    Iterasi angka inklusif dari start sampai end dengan langkah opsional:
        untuk i dari 1 sampai 10 lakukan
            tulis i
        selesai

        untuk i dari 10 sampai 1 langkah -1 lakukan
            tulis i
        selesai
    """
    variable: str = ""
    start: ASTNode = field(default_factory=lambda: NumberNode(0))
    end: ASTNode = field(default_factory=lambda: NumberNode(0))
    step: Optional[ASTNode] = None  # default: otomatis 1 atau -1
    body: List[ASTNode] = field(default_factory=list)
    else_body: Optional[List[ASTNode]] = None

    def get_children(self) -> List[Any]:
        children = [self.start, self.end]
        if self.step:
            children.append(self.step)
        children.extend(self.body)
        if self.else_body:
            children.extend(self.else_body)
        return children


@dataclass
class ForNode(ASTNode):
    """Node untuk for loop: untuk item dalam iterable lakukan ... lainnya ... selesai"""
    variable: str = ""
    iterable: ASTNode = field(default_factory=lambda: IdentifierNode(""))
    body: List[ASTNode] = field(default_factory=list)
    else_body: Optional[List[ASTNode]] = None

    def get_children(self) -> List[Any]:
        children = [self.iterable] + self.body
        if self.else_body:
            children.extend(self.else_body)
        return children


@dataclass
class BreakNode(ASTNode):
    """Node untuk break: hentikan (v6.8: dukungan guard `hentikan jika x`)"""
    guard: Optional[ASTNode] = None

    def get_children(self) -> List[Any]:
        if self.guard is not None:
            return [self.guard]
        return []


@dataclass
class ContinueNode(ASTNode):
    """Node untuk continue: lanjutkan (v6.8: dukungan guard `lanjutkan jika x`)"""
    guard: Optional[ASTNode] = None

    def get_children(self) -> List[Any]:
        if self.guard is not None:
            return [self.guard]
        return []


# ============= V3.1: Pass Statement =============

@dataclass
class PassNode(ASTNode):
    """Node untuk pass: pass (no-op placeholder)"""
    pass


# ============= V3.1: Del Statement =============

@dataclass
class DelNode(ASTNode):
    """Node untuk del: hapus variabel/indeks"""
    target: ASTNode = field(default_factory=lambda: IdentifierNode(""))

    def get_children(self) -> List[Any]:
        return [self.target]


# ============= V3.1: Assert Statement =============

@dataclass
class AssertNode(ASTNode):
    """Node untuk assert: pastikan kondisi"""
    condition: ASTNode = field(default_factory=lambda: BooleanNode())
    message: Optional[ASTNode] = None

    def get_children(self) -> List[Any]:
        children = [self.condition]
        if self.message:
            children.append(self.message)
        return children


# ============= V3.1: Tuple Type =============

@dataclass
class TupleNode(ASTNode):
    """Node untuk tuple literal: (1, 2, 3)"""
    elements: List[ASTNode] = field(default_factory=list)

    def get_children(self) -> List[Any]:
        return self.elements


# ============= V3.1: Set Type =============

@dataclass
class SetNode(ASTNode):
    """Node untuk set literal: {1, 2, 3}"""
    elements: List[ASTNode] = field(default_factory=list)

    def get_children(self) -> List[Any]:
        return self.elements


# ============= V3.1: Dictionary Comprehension =============

@dataclass
class DictComprehensionNode(ASTNode):
    """Node untuk dict comprehension: {k: v for k, v in items}"""
    key_expr: ASTNode = field(default_factory=lambda: NumberNode(0))
    value_expr: ASTNode = field(default_factory=lambda: NumberNode(0))
    key_var: str = ""
    value_var: Optional[str] = None
    iterable: ASTNode = field(default_factory=lambda: IdentifierNode(""))
    condition: Optional[ASTNode] = None

    def get_children(self) -> List[Any]:
        children = [self.key_expr, self.value_expr, self.iterable]
        if self.condition:
            children.append(self.condition)
        return children


# ============= V3.1: For-Else / While-Else =============


# ============= Functions =============

@dataclass
class FunctionNode(ASTNode):
    """Node untuk deklarasi fungsi: fungsi nama(params) ... selesai"""
    name: str = ""
    params: List[str] = field(default_factory=list)
    defaults: List[Optional[ASTNode]] = field(default_factory=list)
    body: List[ASTNode] = field(default_factory=list)
    is_static: bool = False
    param_types: List[Optional[str]] = field(default_factory=list)  # v6.0
    return_type: Optional[str] = None  # v6.0: 'fungsi f() -> Angka'
    rest_param: Optional[str] = None  # v6.7: 'fungsi f(a, ...sisa)' — menangkap sisa argumen

    def get_children(self) -> List[Any]:
        return self.body


# ============= V6.7: Spread Operator =============

@dataclass
class SpreadNode(ASTNode):
    """Node untuk spread operator (v6.7): ...ekspresi

    Dipakai di 3 konteks:
    - Rest parameter: fungsi f(a, ...sisa) — parameter terakhir menangkap
      semua argumen tambahan sebagai list.
    - Spread call: f(...args) — list di-unpack menjadi argumen posisi.
    - Spread list: [...a, 1, 2] — elemen list di-unpack.
    """
    value: ASTNode = field(default_factory=lambda: IdentifierNode(""))

    def get_children(self) -> List[Any]:
        return [self.value]


@dataclass
class ReturnNode(ASTNode):
    """Node untuk return: kembali nilai (v6.8: dukungan guard `kembali x jika c`)"""
    value: ASTNode = field(default_factory=lambda: KosongNode())
    guard: Optional[ASTNode] = None

    def get_children(self) -> List[Any]:
        if self.guard is not None:
            return [self.value, self.guard]
        return [self.value]


@dataclass
class CallNode(ASTNode):
    """Node untuk pemanggilan fungsi: fungsi(args)"""
    function: ASTNode = field(default_factory=lambda: IdentifierNode(""))
    args: List[ASTNode] = field(default_factory=list)
    is_method: bool = False
    object_name: Optional[str] = None
    kwargs: List[tuple] = field(default_factory=list)  # [(nama, ASTNode)]

    def get_children(self) -> List[Any]:
        children = [self.function] + self.args
        for _, v in self.kwargs:
            children.append(v)
        return children


# ============= V5.2: Pipeline Operator =============

@dataclass
class PipelineNode(ASTNode):
    """Node untuk pipeline operator: nilai | > fungsi

    Semantik: nilai | > f  =>  f(nilai)
             nilai | > lalu(x) x * 2  =>  (lalu(x) x * 2)(nilai)
    """
    left: ASTNode = field(default_factory=lambda: NumberNode(0))
    right: ASTNode = field(default_factory=lambda: IdentifierNode(""))

    def get_children(self) -> List[Any]:
        return [self.left, self.right]


# ============= V5.2: Destructuring Assignment =============

@dataclass
class DestructuringAssignmentNode(ASTNode):
    """Node untuk destructuring assignment: buat [a, b] = list / buat {x, y} = objek"""
    targets: List[str] = field(default_factory=list)
    is_array: bool = True  # True untuk [a, b], False untuk {x, y}
    value: ASTNode = field(default_factory=lambda: ListNode())

    def get_children(self) -> List[Any]:
        return [self.value]


# ============= V7.0: Multiple Assignment =============

@dataclass
class MultiAssignNode(ASTNode):
    """Node untuk multiple assignment (v7.0):

        a, b = 1, 2          # reassignment ganda
        a, b = b, a          # swap — nilai kanan dievaluasi DULU semua
        buat a, b = 1, 2     # deklarasi ganda

    Semua nilai kanan dievaluasi sebelum assignment (swap aman).
    """
    targets: List[str] = field(default_factory=list)
    values: List[ASTNode] = field(default_factory=list)
    is_declaration: bool = False

    def get_children(self) -> List[Any]:
        return self.values


@dataclass
class ErrorPropagationNode(ASTNode):
    """Node untuk error propagation operator (v7.0): ekspresi?

    Membuka (unwrap) nilai Result (`Benar`/`Salah`) atau Option
    (`Ada`/`Kosong`):
        buat data = baca_file()?     # Salah(e) -> lempar e; Benar(v) -> v
        buat nama = cari_nama()?     # Kosong()  -> lempar error; Ada(v) -> v

    Nilai non-Result/Option dikembalikan apa adanya.
    """
    value: ASTNode = field(default_factory=lambda: IdentifierNode(""))

    def get_children(self) -> List[Any]:
        return [self.value]


@dataclass
class SetComprehensionNode(ASTNode):
    """Node untuk set comprehension (v7.2): {expr lalu var dalam iterable}

    Mirror list comprehension tapi menghasilkan set (unik):
        buat s = {x * 2 lalu x dalam [1, 2, 2, 3]}   # {2, 4, 6}
    """
    expr: ASTNode = field(default_factory=lambda: NumberNode(0))
    variable: str = ""
    iterable: ASTNode = field(default_factory=lambda: IdentifierNode(""))
    condition: Optional[ASTNode] = None  # optional filter

    def get_children(self) -> List[Any]:
        children = [self.expr, self.iterable]
        if self.condition:
            children.append(self.condition)
        return children


@dataclass
class NullSafeIndexNode(ASTNode):
    """Node untuk null-safe indexing (v7.2): ekspresi?[indeks]

    Mirror `objek?.atribut` tapi untuk index:
        buat x = data?[0]         # data kosong -> kosong; selain itu data[0]
        buat y = data?[0] ?? 0    # aman digabung dengan null-coalescing

    Target kosong (None) menghasilkan None tanpa error.
    """
    target: ASTNode = field(default_factory=lambda: IdentifierNode(""))
    index: ASTNode = field(default_factory=lambda: NumberNode(0))

    def get_children(self) -> List[Any]:
        return [self.target, self.index]


# ============= Classes =============

@dataclass
class ClassNode(ASTNode):
    """Node untuk deklarasi kelas: kelas Nama ... selesai"""
    name: str = ""
    parent: Optional[str] = None
    methods: List["MethodNode"] = field(default_factory=list)
    body: List[ASTNode] = field(default_factory=list)

    def get_children(self) -> List[Any]:
        return self.body


@dataclass
class AttributeNode(ASTNode):
    """Node untuk akses atribut: objek.atribut"""
    object: ASTNode = field(default_factory=lambda: IdentifierNode(""))
    attribute: str = ""

    def get_children(self) -> List[Any]:
        return [self.object]


@dataclass
class MethodNode(ASTNode):
    """Node untuk method dalam kelas."""
    name: str = ""
    params: List[str] = field(default_factory=list)
    body: List[ASTNode] = field(default_factory=list)
    is_static: bool = False
    rest_param: Optional[str] = None  # v6.7: 'fungsi f(a, ...sisa)'

    def get_children(self) -> List[Any]:
        return self.body


# ============= Modules =============

@dataclass
class ImportNode(ASTNode):
    """Node untuk import: impor module"""
    module: str = ""
    alias: Optional[str] = None

    def get_children(self) -> List[Any]:
        return []


@dataclass
class FromImportNode(ASTNode):
    """Node untuk from import: dari module impor nama"""
    module: str = ""
    names: List[str] = field(default_factory=list)

    def get_children(self) -> List[Any]:
        return []


# ============= Error Handling =============

@dataclass
class TryNode(ASTNode):
    """Node untuk try-catch-finally: coba ... tangkap error ... akhirnya ... selesai"""
    body: List[ASTNode] = field(default_factory=list)
    catch_var: str = "error"
    catch_body: List[ASTNode] = field(default_factory=list)
    finally_body: Optional[List[ASTNode]] = None

    def get_children(self) -> List[Any]:
        children = self.body + self.catch_body
        if self.finally_body:
            children.extend(self.finally_body)
        return children


@dataclass
class CatchNode(ASTNode):
    """Node untuk catch dalam try."""
    variable: str = "error"
    body: List[ASTNode] = field(default_factory=list)

    def get_children(self) -> List[Any]:
        return self.body


@dataclass
class KelasErrorNode(ASTNode):
    """Node untuk custom error class (v6.0): kelas_error Nama extends Induk ... selesai

    Error kustom memudahkan penanganan error profesional:
        kelas_error SaldoTidakCukup extends Kesalahan
            fungsi __init__(pesan, saldo)
                self.pesan = pesan
                self.saldo = saldo
            selesai
        selesai
    """
    name: str = ""
    parent: Optional[str] = None  # default: 'Kesalahan'
    methods: List["MethodNode"] = field(default_factory=list)
    body: List[ASTNode] = field(default_factory=list)

    def get_children(self) -> List[Any]:
        return self.body


# ============= Data Structures =============

@dataclass
class ListNode(ASTNode):
    """Node untuk list literal: [1, 2, 3]"""
    elements: List[ASTNode] = field(default_factory=list)

    def get_children(self) -> List[Any]:
        return self.elements


@dataclass
class IndexNode(ASTNode):
    """Node untuk indexing: list[indeks] atau list[start:stop:step]"""
    target: ASTNode = field(default_factory=lambda: IdentifierNode(""))
    index: ASTNode = field(default_factory=lambda: NumberNode())
    slice_start: Optional[ASTNode] = None
    slice_stop: Optional[ASTNode] = None
    slice_step: Optional[ASTNode] = None
    is_slice: bool = False

    def get_children(self) -> List[Any]:
        children = [self.target, self.index]
        if self.slice_start:
            children.append(self.slice_start)
        if self.slice_stop:
            children.append(self.slice_stop)
        if self.slice_step:
            children.append(self.slice_step)
        return children


@dataclass
class ObjectNode(ASTNode):
    """Node untuk object/dict literal: {"kunci": nilai}"""
    entries: Dict[str, ASTNode] = field(default_factory=dict)

    def get_children(self) -> List[Any]:
        return list(self.entries.values())


@dataclass
class ObjectAccessNode(ASTNode):
    """Node untuk akses properti objek: objek.nama"""
    object: ASTNode = field(default_factory=lambda: IdentifierNode(""))
    property: str = ""

    def get_children(self) -> List[Any]:
        return [self.object]


# ============= I/O =============

@dataclass
class PrintNode(ASTNode):
    """Node untuk print: tulis ekspresi"""
    expression: ASTNode = field(default_factory=lambda: StringNode(""))
    args: List[ASTNode] = field(default_factory=list)

    def get_children(self) -> List[Any]:
        return [self.expression] + self.args


@dataclass
class InputNode(ASTNode):
    """Node untuk input: input(prompt)"""
    prompt: Optional[ASTNode] = None

    def get_children(self) -> List[Any]:
        return [self.prompt] if self.prompt else []


# ============= Program =============

@dataclass
class ProgramNode(ASTNode):
    """Node root program. Berisi daftar statement."""
    statements: List[ASTNode] = field(default_factory=list)
    name: str = "<main>"

    def get_children(self) -> List[Any]:
        return self.statements


# ============= V2: Lambda =============

@dataclass
class LambdaNode(ASTNode):
    """Node untuk lambda: lalu(x) x + 1"""
    params: List[str] = field(default_factory=list)
    body: ASTNode = field(default_factory=lambda: NumberNode(0))
    rest_param: Optional[str] = None  # v6.7: lalu(...sisa) ekspresi

    def get_children(self) -> List[Any]:
        return [self.body]


# ============= V2: List Comprehension =============

@dataclass
class ComprehensionNode(ASTNode):
    """Node untuk list comprehension: [expr lalu var dalam iterable]"""
    expr: ASTNode = field(default_factory=lambda: NumberNode(0))
    variable: str = ""
    iterable: ASTNode = field(default_factory=lambda: IdentifierNode(""))
    condition: Optional[ASTNode] = None  # optional filter

    def get_children(self) -> List[Any]:
        children = [self.expr, self.iterable]
        if self.condition:
            children.append(self.condition)
        return children


# ============= V2: F-String =============

@dataclass
class FStringNode(ASTNode):
    """Node untuk f-string: f"Halo {nama}" """
    parts: List[tuple] = field(default_factory=list)  # [("literal", str), ("expr", ASTNode)]

    def get_children(self) -> List[Any]:
        children = []
        for ptype, pval in self.parts:
            if ptype == "expr" and isinstance(pval, ASTNode):
                children.append(pval)
        return children


# ============= V2: Enum =============

@dataclass
class EnumNode(ASTNode):
    """Node untuk enum: enum Warna { MERAH, BIRU, HIJAU }"""
    name: str = ""
    members: List[str] = field(default_factory=list)

    def get_children(self) -> List[Any]:
        return []


# ============= V2: Struct =============

@dataclass
class StructNode(ASTNode):
    """Node untuk struktur: struktur Titik { x, y }"""
    name: str = ""
    fields: List[str] = field(default_factory=list)

    def get_children(self) -> List[Any]:
        return []


# ============= V2: Struct Instantiation =============

@dataclass
class StructInstanceNode(ASTNode):
    """Node untuk struct instantiation: Titik(10, 20)"""
    struct_name: str = ""
    args: List[ASTNode] = field(default_factory=list)

    def get_children(self) -> List[Any]:
        return self.args


# ============= V2: Match/Case =============

@dataclass
class MatchNode(ASTNode):
    """Node untuk match/case: cocokkan expr { ... }"""
    value: ASTNode = field(default_factory=lambda: NumberNode(0))
    cases: List[tuple] = field(default_factory=list)  # [(pattern_node, body_nodes)]
    guards: List[Optional[ASTNode]] = field(default_factory=list)  # v6.0 per-case
    default_case: Optional[List[ASTNode]] = None  # _ case

    def get_children(self) -> List[Any]:
        children = [self.value]
        for pattern, body in self.cases:
            if isinstance(pattern, ASTNode):
                children.append(pattern)
            children.extend(body)
        if self.default_case:
            children.extend(self.default_case)
        return children


@dataclass
class WildcardNode(ASTNode):
    """Node untuk wildcard _ dalam match."""
    pass


# ============= V3: Augmented Assignment =============

@dataclass
class AugmentedAssignmentNode(ASTNode):
    """Node untuk augmented assignment: x += 1, x -= 2, dll."""
    target: ASTNode = field(default_factory=lambda: IdentifierNode(""))
    operator: str = "+="
    value: ASTNode = field(default_factory=lambda: NumberNode())

    def get_children(self) -> List[Any]:
        return [self.target, self.value]


# ============= V3: Ternary Expression =============

@dataclass
class TernaryNode(ASTNode):
    """Node untuk ternary: nilai_a jika kondisi lainnya nilai_b"""
    true_value: ASTNode = field(default_factory=lambda: NumberNode())
    condition: ASTNode = field(default_factory=lambda: BooleanNode())
    false_value: ASTNode = field(default_factory=lambda: NumberNode())

    def get_children(self) -> List[Any]:
        return [self.true_value, self.condition, self.false_value]


# ============= V3: Raise Statement =============

@dataclass
class RaiseNode(ASTNode):
    """Node untuk raise: lempar nilai"""
    value: ASTNode = field(default_factory=lambda: StringNode(""))

    def get_children(self) -> List[Any]:
        return [self.value]


# ============= V3: Global/Nonlocal =============

@dataclass
class GlobalNode(ASTNode):
    """Node untuk global: global nama_var"""
    names: List[str] = field(default_factory=list)

    def get_children(self) -> List[Any]:
        return []


@dataclass
class NonlocalNode(ASTNode):
    """Node untuk nonlokal: nonlokal nama_var"""
    names: List[str] = field(default_factory=list)

    def get_children(self) -> List[Any]:
        return []


# ============= V4: Async/Await =============

@dataclass
class AsyncFunctionDefNode(ASTNode):
    """Node untuk async function: asinkron fungsi nama() ... selesai"""
    name: str = ""
    params: List[str] = field(default_factory=list)
    defaults: List[Optional[ASTNode]] = field(default_factory=list)
    body: List[ASTNode] = field(default_factory=list)
    decorators: List[ASTNode] = field(default_factory=list)
    rest_param: Optional[str] = None  # v6.7

    def get_children(self) -> List[Any]:
        return self.body


@dataclass
class AwaitNode(ASTNode):
    """Node untuk await: tunggu ekspresi"""
    value: ASTNode = field(default_factory=lambda: NumberNode(0))

    def get_children(self) -> List[Any]:
        return [self.value]


# ============= V4: Generators =============

@dataclass
class YieldNode(ASTNode):
    """Node untuk yield: hasilkan ekspresi"""
    value: Optional[ASTNode] = None

    def get_children(self) -> List[Any]:
        if self.value:
            return [self.value]
        return []


@dataclass
class YieldFromNode(ASTNode):
    """Node untuk yield from: hasilkandari ekspresi"""
    value: ASTNode = field(default_factory=lambda: IdentifierNode(""))

    def get_children(self) -> List[Any]:
        return [self.value]


@dataclass
class GeneratorFunctionNode(ASTNode):
    """Node untuk generator function: fungsi nama() ... hasilkan ... selesai"""
    name: str = ""
    params: List[str] = field(default_factory=list)
    defaults: List[Optional[ASTNode]] = field(default_factory=list)
    body: List[ASTNode] = field(default_factory=list)
    rest_param: Optional[str] = None  # v6.7

    def get_children(self) -> List[Any]:
        return self.body


# ============= V4: Decorators =============

@dataclass
class DecoratorNode(ASTNode):
    """Node untuk decorator: @dekorator sebelum fungsi/kelas"""
    decorator_expr: ASTNode = field(default_factory=lambda: IdentifierNode(""))
    target: ASTNode = field(default_factory=lambda: FunctionNode())

    def get_children(self) -> List[Any]:
        return [self.decorator_expr, self.target]


@dataclass
class DecoratedFunctionNode(ASTNode):
    """Node untuk fungsi yang didekorasi"""
    name: str = ""
    params: List[str] = field(default_factory=list)
    defaults: List[Optional[ASTNode]] = field(default_factory=list)
    body: List[ASTNode] = field(default_factory=list)
    decorators: List[ASTNode] = field(default_factory=list)
    rest_param: Optional[str] = None  # v6.7
    param_types: List[Optional[str]] = field(default_factory=list)  # v6.7
    return_type: Optional[str] = None  # v6.7

    def get_children(self) -> List[Any]:
        return self.body


@dataclass
class DecoratedClassNode(ASTNode):
    """Node untuk kelas yang didekorasi"""
    name: str = ""
    parent: Optional[str] = None
    methods: List["MethodNode"] = field(default_factory=list)
    body: List[ASTNode] = field(default_factory=list)
    decorators: List[ASTNode] = field(default_factory=list)

    def get_children(self) -> List[Any]:
        return self.body


# ============= V4: Walrus Operator =============

@dataclass
class WalrusNode(ASTNode):
    """Node untuk walrus operator: x := ekspresi"""
    name: str = ""
    value: ASTNode = field(default_factory=lambda: NumberNode(0))

    def get_children(self) -> List[Any]:
        return [self.value]


# ============= V4: Context Manager =============

@dataclass
class WithNode(ASTNode):
    """Node untuk with statement: dengan ekspresi sebagai nama ... selesai"""
    context_expr: ASTNode = field(default_factory=lambda: IdentifierNode(""))
    as_name: Optional[str] = None
    body: List[ASTNode] = field(default_factory=list)

    def get_children(self) -> List[Any]:
        children = [self.context_expr]
        children.extend(self.body)
        return children


# ============= V4: Typed Except =============

@dataclass
class TypedExceptNode(ASTNode):
    """Node untuk typed except: kecuali TipeError sebagai e ... selesai"""
    exception_type: Optional[str] = None
    variable: str = "error"
    body: List[ASTNode] = field(default_factory=list)

    def get_children(self) -> List[Any]:
        return self.body


@dataclass
class MultiExceptNode(ASTNode):
    """Node untuk multiple except: coba ... kecuali Tipe1 ... kecuali Tipe2 ... selesai"""
    body: List[ASTNode] = field(default_factory=list)
    except_clauses: List[TypedExceptNode] = field(default_factory=list)
    else_body: Optional[List[ASTNode]] = None
    finally_body: Optional[List[ASTNode]] = None

    def get_children(self) -> List[Any]:
        children = self.body.copy()
        for clause in self.except_clauses:
            children.extend(clause.body)
        if self.else_body:
            children.extend(self.else_body)
        if self.finally_body:
            children.extend(self.finally_body)
        return children


# ============= V4: Star Import =============

@dataclass
class StarImportNode(ASTNode):
    """Node untuk star import: dari module impor *"""
    module: str = ""

    def get_children(self) -> List[Any]:
        return []


# ============= V4: Chained Method Call =============

@dataclass
class ChainedCallNode(ASTNode):
    """Node untuk chained method call: obj.method1().method2()"""
    calls: List[CallNode] = field(default_factory=list)

    def get_children(self) -> List[Any]:
        return self.calls


# ============= V4: Switch Statement =============

@dataclass
class SwitchNode(ASTNode):
    """Node untuk switch statement (enhanced match): switch expr { case ... }"""
    value: ASTNode = field(default_factory=lambda: NumberNode(0))
    cases: List[tuple] = field(default_factory=list)  # [(pattern_node, body_nodes, guard_node)]
    default_case: Optional[List[ASTNode]] = None

    def get_children(self) -> List[Any]:
        children = [self.value]
        for pattern, body, guard in self.cases:
            if isinstance(pattern, ASTNode):
                children.append(pattern)
            if guard:
                children.append(guard)
            children.extend(body)
        if self.default_case:
            children.extend(self.default_case)
        return children


# ============= V5.0: Type System =============

@dataclass
class TypeAnnotationNode(ASTNode):
    """Node untuk type annotation: nama: tipe"""
    name: str = ""
    type_name: str = ""
    is_optional: bool = False
    default_value: Optional[ASTNode] = None

    def get_children(self) -> List[Any]:
        children = []
        if self.default_value:
            children.append(self.default_value)
        return children


@dataclass
class TypeAliasNode(ASTNode):
    """Node untuk type alias: tipe NamaTipe = definisi"""
    name: str = ""
    definition: ASTNode = field(default_factory=lambda: IdentifierNode(""))

    def get_children(self) -> List[Any]:
        return [self.definition]


@dataclass
class UnionTypeNode(ASTNode):
    """Node untuk union type: tipe1 | tipe2"""
    types: List[str] = field(default_factory=list)

    def get_children(self) -> List[Any]:
        return []


@dataclass
class GenericTypeNode(ASTNode):
    """Node untuk generic type: List<angka>"""
    base_type: str = ""
    type_args: List[str] = field(default_factory=list)

    def get_children(self) -> List[Any]:
        return []


@dataclass
class FunctionTypeNode(ASTNode):
    """Node untuk function type: (angka, teks) -> benar"""
    param_types: List[str] = field(default_factory=list)
    return_type: str = "kosong"

    def get_children(self) -> List[Any]:
        return []


# ============= V5.0: Interfaces/Traits =============

@dataclass
class InterfaceNode(ASTNode):
    """Node untuk interface: antarmuka Nama { ... }"""
    name: str = ""
    methods: List["MethodSignatureNode"] = field(default_factory=list)
    parent_interfaces: List[str] = field(default_factory=list)

    def get_children(self) -> List[Any]:
        return self.methods


@dataclass
class MethodSignatureNode(ASTNode):
    """Node untuk method signature dalam interface"""
    name: str = ""
    params: List[TypeAnnotationNode] = field(default_factory=list)
    return_type: Optional[str] = None
    is_abstract: bool = True

    def get_children(self) -> List[Any]:
        return self.params


@dataclass
class ImplementsNode(ASTNode):
    """Node untuk implements: kelas Nama: Interface1, Interface2"""
    class_name: str = ""
    interfaces: List[str] = field(default_factory=list)

    def get_children(self) -> List[Any]:
        return []


@dataclass
class AbstractClassNode(ASTNode):
    """Node untuk abstract class: abstrak kelas Nama { ... }"""
    name: str = ""
    parent: Optional[str] = None
    methods: List["MethodNode"] = field(default_factory=list)
    body: List[ASTNode] = field(default_factory=list)
    abstract_methods: List[str] = field(default_factory=list)

    def get_children(self) -> List[Any]:
        return self.body


@dataclass
class AbstractMethodNode(ASTNode):
    """Node untuk abstract method: abstrak fungsi nama() ... selesai"""
    name: str = ""
    params: List[str] = field(default_factory=list)
    return_type: Optional[str] = None

    def get_children(self) -> List[Any]:
        return []


# ============= V5.0: Enhanced Pattern Matching =============

@dataclass
class DestructuringPatternNode(ASTNode):
    """Node untuk destructuring pattern: [a, b, c] atau {nama, umur}"""
    variables: List[str] = field(default_factory=list)
    is_array: bool = True  # True untuk [a,b], False untuk {a,b}

    def get_children(self) -> List[Any]:
        return []


@dataclass
class GuardPatternNode(ASTNode):
    """Node untuk guard pattern: x jika x > 0"""
    variable: str = ""
    condition: ASTNode = field(default_factory=lambda: BooleanNode())
    body: List[ASTNode] = field(default_factory=list)

    def get_children(self) -> List[Any]:
        children = [self.condition]
        children.extend(self.body)
        return children


@dataclass
class ObjectPatternNode(ASTNode):
    """Pola objek dengan rename: {"x": a, "y": b} — bind nilai kunci ke variabel."""
    entries: Dict[str, str] = field(default_factory=dict)  # {kunci: variabel}

    def get_children(self) -> List[Any]:
        return []


@dataclass
class BindingPatternNode(ASTNode):
    """Pola binding: identifier menangkap seluruh nilai."""
    name: str = ""

    def get_children(self) -> List[Any]:
        return []


# ============= V5.0: Higher-Order Functions =============

@dataclass
class MapNode(ASTNode):
    """Node untuk map: peta(iterable, fungsi)"""
    iterable: ASTNode = field(default_factory=lambda: IdentifierNode(""))
    function: ASTNode = field(default_factory=lambda: IdentifierNode(""))

    def get_children(self) -> List[Any]:
        return [self.iterable, self.function]


@dataclass
class FilterNode(ASTNode):
    """Node untuk filter: saring(iterable, kondisi)"""
    iterable: ASTNode = field(default_factory=lambda: IdentifierNode(""))
    condition: ASTNode = field(default_factory=lambda: BooleanNode())

    def get_children(self) -> List[Any]:
        return [self.iterable, self.condition]


@dataclass
class ReduceNode(ASTNode):
    """Node untuk reduce: kurangi(iterable, fungsi, awal)"""
    iterable: ASTNode = field(default_factory=lambda: IdentifierNode(""))
    function: ASTNode = field(default_factory=lambda: IdentifierNode(""))
    initial: Optional[ASTNode] = None

    def get_children(self) -> List[Any]:
        children = [self.iterable, self.function]
        if self.initial:
            children.append(self.initial)
        return children


# ============= V5.0: Result/Option Types =============

@dataclass
class ResultNode(ASTNode):
    """Node untuk Result type: Benar(value) atau Salah(error)"""
    is_success: bool = True
    value: ASTNode = field(default_factory=lambda: KosongNode())

    def get_children(self) -> List[Any]:
        return [self.value]


@dataclass
class OptionNode(ASTNode):
    """Node untuk Option type: Ada(value) atau Kosong()"""
    has_value: bool = True
    value: Optional[ASTNode] = None

    def get_children(self) -> List[Any]:
        if self.value:
            return [self.value]
        return []


@dataclass
class MatchResultNode(ASTNode):
    """Node untuk pattern matching on Result"""
    value: ASTNode = field(default_factory=lambda: IdentifierNode(""))
    success_var: str = "v"
    success_body: List[ASTNode] = field(default_factory=list)
    error_var: str = "e"
    error_body: List[ASTNode] = field(default_factory=list)

    def get_children(self) -> List[Any]:
        children = [self.value]
        children.extend(self.success_body)
        children.extend(self.error_body)
        return children


# ============= V5.0: Macros =============

@dataclass
class MacroDefNode(ASTNode):
    """Node untuk macro definition: makro Nama() { ... }"""
    name: str = ""
    params: List[str] = field(default_factory=list)
    body: List[ASTNode] = field(default_factory=list)

    def get_children(self) -> List[Any]:
        return self.body


@dataclass
class MacroCallNode(ASTNode):
    """Node untuk macro call: Nama(args...)"""
    name: str = ""
    args: List[ASTNode] = field(default_factory=list)

    def get_children(self) -> List[Any]:
        return self.args


# ============= V5.0: Enhanced Async =============

@dataclass
class TaskNode(ASTNode):
    """Node untuk async task: tugas nama = asinkron fungsi()"""
    name: str = ""
    function: ASTNode = field(default_factory=lambda: IdentifierNode(""))

    def get_children(self) -> List[Any]:
        return [self.function]


@dataclass
class PromiseNode(ASTNode):
    """Node untuk promise: janji(fungsi)"""
    function: ASTNode = field(default_factory=lambda: IdentifierNode(""))

    def get_children(self) -> List[Any]:
        return [self.function]


@dataclass
class AwaitAllNode(ASTNode):
    """Node untuk await all: tunggu_semua([task1, task2])"""
    tasks: List[ASTNode] = field(default_factory=list)

    def get_children(self) -> List[Any]:
        return self.tasks


# ============= V5.0: Module System =============

@dataclass
class NamespaceNode(ASTNode):
    """Node untuk namespace: ruang nama MyModule { ... }"""
    name: str = ""
    body: List[ASTNode] = field(default_factory=list)

    def get_children(self) -> List[Any]:
        return self.body


@dataclass
class UseNode(ASTNode):
    """Node untuk use statement: pakai MyModule"""
    module: str = ""
    alias: Optional[str] = None

    def get_children(self) -> List[Any]:
        return []


# ============= V5.0: Access Modifiers =============

@dataclass
class AccessModifierNode(ASTNode):
    """Node untuk access modifier: publik/privat/terlindungi"""
    modifier: str = "publik"  # publik, privat, terlindungi
    target: ASTNode = field(default_factory=lambda: FunctionNode())

    def get_children(self) -> List[Any]:
        return [self.target]


# ============= V5.0: Generic Functions =============

@dataclass
class GenericFunctionNode(ASTNode):
    """Node untuk generic function: fungsi nama<T>(param: T) -> T"""
    name: str = ""
    type_params: List[str] = field(default_factory=list)
    params: List[TypeAnnotationNode] = field(default_factory=list)
    return_type: Optional[str] = None
    body: List[ASTNode] = field(default_factory=list)

    def get_children(self) -> List[Any]:
        return self.body


# ============= V5.0: For Each with Index =============

@dataclass
class ForEachNode(ASTNode):
    """Node untuk for-each with index: untuk setiap (item, index) dalam iterable"""
    variable: str = ""
    index_variable: Optional[str] = None
    iterable: ASTNode = field(default_factory=lambda: IdentifierNode(""))
    body: List[ASTNode] = field(default_factory=list)

    def get_children(self) -> List[Any]:
        children = [self.iterable]
        children.extend(self.body)
        return children


# ============= V5.0: Switch Expression =============

@dataclass
class SwitchExprNode(ASTNode):
    """Node untuk switch expression: cocokkan expr { ... } sebagai nilai"""
    value: ASTNode = field(default_factory=lambda: NumberNode(0))
    cases: List[tuple] = field(default_factory=list)
    default_case: Optional[ASTNode] = None

    def get_children(self) -> List[Any]:
        children = [self.value]
        for pattern, body in self.cases:
            if isinstance(pattern, ASTNode):
                children.append(pattern)
            children.extend(body)
        if self.default_case:
            children.append(self.default_case)
        return children


# ============= V5.0: Chained Comparisons =============

@dataclass
class ChainedComparisonNode(ASTNode):
    """Node untuk chained comparison: 0 < x < 10"""
    left: ASTNode = field(default_factory=lambda: NumberNode(0))
    operators: List[str] = field(default_factory=list)
    comparators: List[ASTNode] = field(default_factory=list)

    def get_children(self) -> List[Any]:
        children = [self.left]
        children.extend(self.comparators)
        return children


# ============= V5.0: Walrus in Comprehension =============

@dataclass
class WalrusComprehensionNode(ASTNode):
    """Node untuk walrus in comprehension: [y := x + 1 untuk x dalam range(5)]"""
    target: str = ""
    value: ASTNode = field(default_factory=lambda: NumberNode(0))
    iterable: ASTNode = field(default_factory=lambda: IdentifierNode(""))
    condition: Optional[ASTNode] = None

    def get_children(self) -> List[Any]:
        children = [self.value, self.iterable]
        if self.condition:
            children.append(self.condition)
        return children


# ============= V5.0: Null Coalescing =============

@dataclass
class NullCoalescingNode(ASTNode):
    """Node untuk null coalescing: x ?? nilai_default"""
    left: ASTNode = field(default_factory=lambda: KosongNode())
    right: ASTNode = field(default_factory=lambda: NumberNode(0))

    def get_children(self) -> List[Any]:
        return [self.left, self.right]


# ============= V5.0: Optional Chaining =============

@dataclass
class OptionalChainingNode(ASTNode):
    """Node untuk optional chaining: objek?.atribut"""
    object: ASTNode = field(default_factory=lambda: IdentifierNode(""))
    property: str = ""

    def get_children(self) -> List[Any]:
        return [self.object]
