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
    """Node untuk assignment: buat x = nilai"""
    target: ASTNode = field(default_factory=lambda: IdentifierNode(""))
    value: ASTNode = field(default_factory=lambda: NumberNode())
    is_declaration: bool = True

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
    """Node untuk while loop: selama kondisi lakukan ... selesai"""
    condition: ASTNode = field(default_factory=lambda: BooleanNode())
    body: List[ASTNode] = field(default_factory=list)

    def get_children(self) -> List[Any]:
        return [self.condition] + self.body


@dataclass
class ForNode(ASTNode):
    """Node untuk for loop: untuk item dalam iterable lakukan ... selesai"""
    variable: str = ""
    iterable: ASTNode = field(default_factory=lambda: IdentifierNode(""))
    body: List[ASTNode] = field(default_factory=list)

    def get_children(self) -> List[Any]:
        return [self.iterable] + self.body


@dataclass
class BreakNode(ASTNode):
    """Node untuk break: hentikan"""
    pass


@dataclass
class ContinueNode(ASTNode):
    """Node untuk continue: lanjutkan"""
    pass


# ============= Functions =============

@dataclass
class FunctionNode(ASTNode):
    """Node untuk deklarasi fungsi: fungsi nama(params) ... selesai"""
    name: str = ""
    params: List[str] = field(default_factory=list)
    body: List[ASTNode] = field(default_factory=list)

    def get_children(self) -> List[Any]:
        return self.body


@dataclass
class ReturnNode(ASTNode):
    """Node untuk return: kembali nilai"""
    value: ASTNode = field(default_factory=lambda: KosongNode())

    def get_children(self) -> List[Any]:
        return [self.value]


@dataclass
class CallNode(ASTNode):
    """Node untuk pemanggilan fungsi: fungsi(args)"""
    function: ASTNode = field(default_factory=lambda: IdentifierNode(""))
    args: List[ASTNode] = field(default_factory=list)
    is_method: bool = False
    object_name: Optional[str] = None

    def get_children(self) -> List[Any]:
        return [self.function] + self.args


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
    """Node untuk try-catch: coba ... tangkap error ... selesai"""
    body: List[ASTNode] = field(default_factory=list)
    catch_var: str = "error"
    catch_body: List[ASTNode] = field(default_factory=list)

    def get_children(self) -> List[Any]:
        return self.body + self.catch_body


@dataclass
class CatchNode(ASTNode):
    """Node untuk catch dalam try."""
    variable: str = "error"
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
    """Node untuk indexing: list[indeks]"""
    target: ASTNode = field(default_factory=lambda: IdentifierNode(""))
    index: ASTNode = field(default_factory=lambda: NumberNode())

    def get_children(self) -> List[Any]:
        return [self.target, self.index]


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
