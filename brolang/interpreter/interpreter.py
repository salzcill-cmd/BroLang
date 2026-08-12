"""
Interpreter BroLang
===================

Interpreter mengeksekusi AST BroLang menggunakan visitor pattern.
Memiliki environment sendiri dengan scoping yang tepat.

Fitur:
- Eksekusi semua node AST
- Function call dengan argument passing
- Class instantiation dan method call
- Error handling (try-catch)
- Scope management
- Standard library integration
"""

from typing import Any, Dict, List, Optional, Callable, Set
from dataclasses import dataclass, field
import os
from brolang.ast.nodes import (
    ASTNode,
    ASTVisitor,
    ProgramNode,
    NumberNode,
    DecimalNode,
    StringNode,
    BooleanNode,
    KosongNode,
    IdentifierNode,
    VariableNode,
    AssignmentNode,
    BinaryOpNode,
    UnaryOpNode,
    IfNode,
    WhileNode,
    ForNode,
    DoUntilNode,
    RangeForNode,
    BreakNode,
    ContinueNode,
    FunctionNode,
    ReturnNode,
    CallNode,
    ClassNode,
    MethodNode,
    AttributeNode,
    ImportNode,
    FromImportNode,
    TryNode,
    CatchNode,
    ListNode,
    IndexNode,
    ObjectNode,
    ObjectAccessNode,
    PrintNode,
    InputNode,
    LambdaNode,
    ComprehensionNode,
    FStringNode,
    EnumNode,
    StructNode,
    StructInstanceNode,
    MatchNode,
    WildcardNode,
    AugmentedAssignmentNode,
    TernaryNode,
    RaiseNode,
    GlobalNode,
    NonlocalNode,
    PassNode,
    DelNode,
    AssertNode,
    TupleNode,
    SetNode,
    DictComprehensionNode,
    AsyncFunctionDefNode,
    AwaitNode,
    YieldNode,
    YieldFromNode,
    GeneratorFunctionNode,
    DecoratorNode,
    DecoratedFunctionNode,
    DecoratedClassNode,
    WalrusNode,
    WithNode,
    TypedExceptNode,
    MultiExceptNode,
    StarImportNode,
    ChainedCallNode,
    SwitchNode,
    # V5.0 Nodes
    TypeAnnotationNode,
    TypeAliasNode,
    UnionTypeNode,
    GenericTypeNode,
    FunctionTypeNode,
    InterfaceNode,
    MethodSignatureNode,
    ImplementsNode,
    AbstractClassNode,
    AbstractMethodNode,
    DestructuringPatternNode,
    GuardPatternNode,
    ObjectPatternNode,
    BindingPatternNode,
    MapNode,
    FilterNode,
    ReduceNode,
    ResultNode,
    OptionNode,
    MacroDefNode,
    MacroCallNode,
    NamespaceNode,
    UseNode,
    AccessModifierNode,
    NullCoalescingNode,
    OptionalChainingNode,
    ForEachNode,
    ChainedComparisonNode,
    # V5.2 Nodes
    PipelineNode,
    DestructuringAssignmentNode,
    # V6.0 Nodes
    KelasErrorNode,
    # V6.7 Nodes
    SpreadNode,
)
from brolang.exceptions import (
    RuntimeError_,
    TypeError_,
    NameError_,
    ZeroDivisionError_,
    IndexError_,
    YieldException,
    StopGenerator,
)
from brolang.exceptions import BroLangError as _BroLangErrorBase
from brolang.stdlib import get_stdlib_module
from brolang.interpreter.builtins import BUILTINS
from brolang.suggestions import saran_keyword


@dataclass
class Environment:
    """Lingkungan eksekusi dengan scoping.

    Menyimpan variabel, fungsi, dan kelas dalam scope saat ini.
    """

    parent: Optional["Environment"] = None
    variables: Dict[str, Any] = field(default_factory=dict)
    functions: Dict[str, Callable] = field(default_factory=dict)
    classes: Dict[str, "BroLangClass"] = field(default_factory=dict)
    interfaces: Dict[str, Any] = field(default_factory=dict)
    modules: Dict[str, Any] = field(default_factory=dict)
    return_value: Any = None
    should_return: bool = False
    should_break: bool = False
    should_continue: bool = False
    constants: Set[str] = field(default_factory=set)  # v6.5: nama variabel immutable

    def define_variable(self, name: str, value: Any, is_const: bool = False) -> None:
        self.variables[name] = value
        if is_const:
            self.constants.add(name)

    def get_variable(self, name: str) -> Any:
        if name in self.variables:
            return self.variables[name]
        if self.parent is not None:
            return self.parent.get_variable(name)
        raise NameError_(
            message=f"Variabel '{name}' tidak ditemukan.",
            line=0,
            column=0,
            solution=f"Pastikan '{name}' sudah dideklarasikan dengan 'buat'.",
        )

    def set_variable(self, name: str, value: Any, line: int = 0, column: int = 0) -> None:
        if name in self.variables:
            # v6.5: konstanta tidak bisa diubah setelah deklarasi
            if name in self.constants:
                raise RuntimeError_(
                    message=f"Konstanta '{name}' tidak bisa diubah.",
                    line=line,
                    column=column,
                    solution=f"Hapus assignment ke '{name}' atau ubah deklarasi menjadi 'buat {name} = ...'.",
                    example=f"konstanta {name} = 10\n{name} = 20  # error!",
                )
            self.variables[name] = value
            return
        if self.parent is not None:
            self.parent.set_variable(name, value, line, column)
            return
        raise NameError_(
            message=f"Variabel '{name}' tidak ditemukan.",
            line=0,
            column=0,
            solution=f"Pastikan '{name}' sudah dideklarasikan.",
        )

    def has_variable(self, name: str) -> bool:
        if name in self.variables:
            return True
        if self.parent is not None:
            return self.parent.has_variable(name)
        return False


class ReturnException(Exception):
    """Exception untuk menangani return value."""

    def __init__(self, value: Any):
        self.value = value


class BreakException(Exception):
    """Exception untuk break."""

    pass


class ContinueException(Exception):
    """Exception untuk continue."""

    pass


def _struct_init(instance, fields, args):
    """Helper untuk inisialisasi struct instance."""
    for i, field in enumerate(fields):
        if i < len(args):
            setattr(instance, field, args[i])
        else:
            setattr(instance, field, None)


def _has_yield_in_body(body):
    """Cek apakah ada yield atau yield-from di dalam fungsi."""
    for stmt in body:
        if isinstance(stmt, (YieldNode, YieldFromNode)):
            return True
        if hasattr(stmt, "body") and _has_yield_in_body(stmt.body):
            return True
        if hasattr(stmt, "else_body") and stmt.else_body and _has_yield_in_body(stmt.else_body):
            return True
        if hasattr(stmt, "if_branches") and stmt.if_branches:
            for cond, block in stmt.if_branches:
                if _has_yield_in_body(block):
                    return True
        if hasattr(stmt, "except_handlers") and stmt.except_handlers:
            for handler in stmt.except_handlers:
                if hasattr(handler, "body") and _has_yield_in_body(handler.body):
                    return True
    return False


# ============= V6.0: Custom Error Classes =============


class Kesalahan(_BroLangErrorBase):
    """Kelas dasar untuk error kustom di BroLang (v6.0).

    User bisa mendefinisikan error kustom dengan `kelas_error`:

        kelas_error SaldoTidakCukup extends Kesalahan
            fungsi __init__(pesan)
                self.pesan = pesan
            selesai
        selesai

    Lalu melempar & menangkapnya:
        lempar SaldoTidakCukup("Saldo tidak cukup")
        ...
        kecuali SaldoTidakCukup sebagai e
            tulis e.pesan
    """

    def __init__(self, message: str = ""):
        self.pesan = str(message)
        self.message = str(message)
        super().__init__(message=str(message), line=0, column=0)


class BroLangClass:
    """Representasi kelas dalam BroLang runtime."""

    def __init__(
        self,
        name: str,
        methods: Dict[str, Callable],
        parent: Optional["BroLangClass"] = None,
        is_abstract: bool = False,
        abstract_methods: Optional[List[str]] = None,
        required_interfaces: Optional[List[str]] = None,
        method_access: Optional[Dict[str, str]] = None,
    ):
        self.name = name
        self.methods = methods
        self.parent = parent
        self.is_abstract = is_abstract
        self.abstract_methods = abstract_methods or []
        self.required_interfaces = required_interfaces or []
        self.method_access = method_access or {}  # name -> "publik"/"privat"/"terlindungi"

    def get_method(self, name: str) -> Optional[Callable]:
        if name in self.methods:
            return self.methods[name]
        if self.parent is not None:
            return self.parent.get_method(name)
        return None

    def get_method_access(self, name: str) -> str:
        if name in self.method_access:
            return self.method_access[name]
        if self.parent is not None:
            return self.parent.get_method_access(name)
        return "publik"


class BroLangInstance:
    """Instance dari sebuah kelas BroLang."""

    def __init__(self, klass: BroLangClass):
        self.klass = klass
        self.attributes: Dict[str, Any] = {}

    def get(self, name: str, caller_class: Optional[str] = None) -> Any:
        if name in self.attributes:
            return self.attributes[name]
        # Property getter: _<name> method
        prop_getter = self.klass.get_method(f"_{name}")
        if prop_getter is not None:
            return prop_getter(self)
        method = self.klass.get_method(name)
        if method is not None:
            access = self.klass.get_method_access(name)
            if access == "privat" and caller_class != self.klass.name:
                raise RuntimeError_(
                    message=f"Akses ditolak: '{name}' bersifat privat di kelas '{self.klass.name}'.",
                    line=0,
                    column=0,
                    solution=f"Hapus modifier 'privat' atau akses dari dalam kelas {self.klass.name}.",
                )
            if access == "terlindungi" and caller_class not in (
                self.klass.name,
                _get_subclass_names(self.klass),
            ):
                raise RuntimeError_(
                    message=f"Akses ditolak: '{name}' bersifat terlindungi di kelas '{self.klass.name}'.",
                    line=0,
                    column=0,
                    solution=f"Akses '{name}' hanya bisa dari kelas {self.klass.name} atau keturunannya.",
                )
            return method
        raise RuntimeError_(
            message=f"'{self.klass.name}' tidak memiliki atribut '{name}'.",
            line=0,
            column=0,
            solution=f"Periksa apakah '{name}' sudah didefinisikan di kelas {self.klass.name}.",
        )

    def set(self, name: str, value: Any) -> None:
        # Property setter: _<name>_set method
        prop_setter = self.klass.get_method(f"_{name}_set")
        if prop_setter is not None:
            prop_setter(self, value)
            return
        self.attributes[name] = value


class BroLangGenerator:
    """Generator object yang bisa di-iterate.

    Karena ini tree-walking interpreter, generator dieksekusi sekali
    untuk mengumpulkan semua nilai yield, lalu dilayani satu per satu.
    For-loop dijalankan item per item supaya yield bisa ditangkap.
    """

    def __init__(self, body, params, args, defaults, closure_env, interpreter):
        self._values = []
        self._collected = False
        self._index = 0
        self._body = body
        self._params = params
        self._args = args
        self._defaults = defaults
        self._closure_env = closure_env
        self._interpreter = interpreter

    def _setup_env(self):
        env = Environment(parent=self._closure_env)
        for i, param in enumerate(self._params):
            if i < len(self._args):
                env.define_variable(param, self._args[i])
            elif i < len(self._defaults):
                dv = self._defaults[i]
                env.define_variable(param, self._interpreter.visit(dv) if dv else None)
            else:
                env.define_variable(param, None)
        return env

    def _collect_stmts(self, stmts):
        """Eksekusi list statement, tangkap yield di setiap level."""
        for stmt in stmts:
            cls = stmt.__class__.__name__
            if cls == "ForNode":
                self._collect_for(stmt)
            elif cls == "RangeForNode":
                self._collect_range_for(stmt)
            elif cls == "WhileNode":
                self._collect_while(stmt)
            elif cls == "DoUntilNode":
                self._collect_do_until(stmt)
            elif cls == "IfNode":
                self._collect_if(stmt)
            elif cls == "YieldFromNode":
                self._collect_yield_from(stmt)
            else:
                try:
                    self._interpreter.visit(stmt)
                except YieldException as e:
                    self._values.append(e.value)
                if self._interpreter.current_env.should_return:
                    return

    def _collect_if(self, node):
        """Eksekusi if/elif/else statement per-statement supaya yield bisa
        ditangkap di setiap cabang (v6.9).

        Tanpa ini, yield di dalam blok `jika` menghentikan eksekusi sisa
        blok (YieldException melewati visit_IfNode), dan `hasilkandari`
        hanya menghasilkan elemen pertama.
        """
        condition = self._interpreter.visit(node.condition)
        if condition:
            self._interpreter._push_env()
            try:
                self._collect_stmts(node.body)
            finally:
                self._interpreter._pop_env()
            return
        for i, ec in enumerate(node.elif_conditions):
            if self._interpreter.visit(ec):
                self._interpreter._push_env()
                try:
                    self._collect_stmts(node.elif_bodies[i])
                finally:
                    self._interpreter._pop_env()
                return
        if node.else_body:
            self._interpreter._push_env()
            try:
                self._collect_stmts(node.else_body)
            finally:
                self._interpreter._pop_env()

    def _collect_range_for(self, node):
        """Eksekusi range-for item per item supaya yield bisa ditangkap (v6.5)."""
        start = self._interpreter.visit(node.start)
        end = self._interpreter.visit(node.end)
        if node.step is not None:
            step = self._interpreter.visit(node.step)
            if step == 0:
                return
        else:
            step = 1 if start <= end else -1
        for item in range(start, end + step, step):
            self._interpreter._push_env()
            self._interpreter.current_env.define_variable(node.variable, item)
            try:
                self._collect_stmts(node.body)
            finally:
                self._interpreter._pop_env()
            if self._interpreter.current_env.should_return:
                return

    def _collect_do_until(self, node):
        """Eksekusi do-until item per item supaya yield bisa ditangkap (v6.5)."""
        while True:
            self._interpreter._push_env()
            try:
                self._collect_stmts(node.body)
            finally:
                self._interpreter._pop_env()
            if self._interpreter.current_env.should_return:
                return
            if self._interpreter.visit(node.condition):
                break

    def _collect_for(self, node):
        """Eksekusi for-loop item per item supaya yield bisa ditangkap."""
        iterable = self._interpreter.visit(node.iterable)
        for item in iterable:
            self._interpreter._push_env()
            self._interpreter.current_env.define_variable(node.variable, item)
            try:
                self._collect_stmts(node.body)
            finally:
                self._interpreter._pop_env()
            if self._interpreter.current_env.should_return:
                return

    def _collect_while(self, node):
        """Eksekusi while-loop item per item supaya yield bisa ditangkap."""
        while True:
            condition = self._interpreter.visit(node.condition)
            if not condition:
                break
            self._interpreter._push_env()
            try:
                self._collect_stmts(node.body)
            finally:
                self._interpreter._pop_env()
            if self._interpreter.current_env.should_return:
                return

    def _collect_yield_from(self, node):
        """Yield from — yield setiap item dari iterable."""
        iterable = self._interpreter.visit(node.value)
        items = list(iterable) if not isinstance(iterable, list) else iterable
        for item in items:
            self._values.append(item)

    def _collect(self):
        if self._collected:
            return
        self._collected = True

        old_env = self._interpreter.current_env
        # v6.9: generator aktif dilacak supaya `hasilkandari` di dalam
        # blok (jika/guard/loop) bisa menambahkan SEMUA item ke koleksi.
        old_gen = getattr(self._interpreter, "_active_generator", None)
        self._interpreter._active_generator = self
        self._interpreter.current_env = self._setup_env()
        try:
            self._collect_stmts(self._body)
        except ReturnException:
            pass
        finally:
            self._interpreter.current_env = old_env
            self._interpreter._active_generator = old_gen

    def __iter__(self):
        self._collect()
        return self

    def __next__(self):
        self._collect()
        if self._index >= len(self._values):
            raise StopIteration
        value = self._values[self._index]
        self._index += 1
        return value


def _get_subclass_names(klass: BroLangClass) -> List[str]:
    """Kumpulkan nama kelas turunan."""
    names = []
    for env_var in [globals(), locals()]:
        for v in env_var.values():
            if isinstance(v, BroLangClass) and v.parent is klass:
                names.append(v.name)
                names.extend(_get_subclass_names(v))
    return names


# ============= Operator Overloading (v5.5) =============
# Method khusus yang dipanggil saat operator dipakai pada instance kelas.
_OVERLOAD_BINARY_MAP = {
    "+": "_tambah_",
    "-": "_kurang_",
    "*": "_kali_",
    "/": "_bagi_",
    "%": "_modulo_",
    "**": "_pangkat_",
    "==": "_sama_",
    "!=": "_tidak_sama_",
    "<": "_kurang_dari_",
    ">": "_lebih_dari_",
    "<=": "_kurang_sama_",
    ">=": "_lebih_sama_",
    "dalam": "_dalam_",
}

_OVERLOAD_UNARY_MAP = {
    "-": "_negasi_",
    "+": "_positif_",
    "bukan": "_bukan_",
    "~": "_bukan_bit_",
}


class Interpreter(ASTVisitor):
    """Interpreter utama BroLang.

    Mengunjungi setiap node AST dan mengeksekusinya.

    Attributes:
        global_env: Environment global
        current_env: Environment saat ini
        output: Menangkap output untuk testing
    """

    def __init__(self):
        self.global_env = Environment()
        self.current_env = self.global_env
        self.output: List[str] = []
        self._current_class_name: Optional[str] = None

        # Register built-in functions
        for name, func in BUILTINS.items():
            self.global_env.functions[name] = func

        # V6.0: kelas dasar error kustom — tersedia sebagai kelas & variabel
        self.global_env.variables["Kesalahan"] = Kesalahan
        self.global_env.classes["Kesalahan"] = BroLangClass(
            "Kesalahan",
            methods={},
            parent=None,
            is_abstract=False,
            abstract_methods=[],
            required_interfaces=[],
        )
        self.global_env.classes["Kesalahan"].is_error_class = True

    def interpret(self, node: ASTNode) -> Any:
        """Menjalankan interpretasi.

        Args:
            node: Root AST node

        Returns:
            Hasil eksekusi
        """
        self.output = []
        try:
            result = self.visit(node)
            return result
        except ReturnException as e:
            return e.value
        except (RuntimeError_, TypeError_, NameError_, ZeroDivisionError_, IndexError_):
            raise
        except Exception as e:
            raise RuntimeError_(
                message=f"Terjadi error runtime: {str(e)}",
                line=getattr(e, "line", 0),
                column=getattr(e, "column", 0),
            )

    def _push_env(self) -> Environment:
        """Membuat environment baru (untuk scope baru)."""
        env = Environment(parent=self.current_env)
        self.current_env = env
        return env

    def _pop_env(self) -> None:
        """Kembali ke environment parent."""
        if self.current_env.parent is not None:
            self.current_env = self.current_env.parent

    def _bind_params(self, params, defaults, args, kwargs, node=None, rest_param=None):
        """Gabungkan argumen posisi + keyword arguments sesuai urutan params.

        v6.7: rest_param menangkap semua argumen tambahan sebagai list.

        Returns:
            List[(nama_param, nilai)]
        """
        values = list(args)
        for name, val in kwargs.items():
            if name not in params:
                raise RuntimeError_(
                    message=f"Keyword argument '{name}' tidak dikenal.",
                    line=getattr(node, "line", 0) if node else 0,
                    column=getattr(node, "column", 0) if node else 0,
                    solution=f"Parameter yang tersedia: {', '.join(params)}.",
                )
            idx = params.index(name)
            while len(values) <= idx:
                values.append(None)
            values[idx] = val

        bound = []
        for i, param in enumerate(params):
            if i < len(values):
                bound.append((param, values[i]))
            elif i < len(defaults) and defaults[i] is not None:
                bound.append((param, self.visit(defaults[i])))
            else:
                bound.append((param, None))

        # v6.7: rest parameter — semua argumen yang tidak terikat ke param
        # biasa (indeks >= jumlah params) dikumpulkan menjadi list.
        if rest_param:
            bound.append((rest_param, values[len(params):]))

        # Type enforcement v6.0 pada parameter fungsi ber-tipe
        param_types = getattr(node, "param_types", None) or []
        for i, (param, val) in enumerate(bound):
            if i < len(param_types) and param_types[i]:
                if not self._type_matches(val, param_types[i]):
                    raise TypeError_(
                        message=f"Parameter '{param}' diharapkan {param_types[i]}, "
                        f"tapi mendapat {self._type_name_of(val)}.",
                        line=getattr(node, "line", 0) if node else 0,
                        column=getattr(node, "column", 0) if node else 0,
                        solution=f"Berikan nilai {param_types[i]} untuk parameter '{param}'.",
                    )
        return bound

    # ============= V6.0: Type System =============

    _TIPE_MAP = {
        "Angka": (int, float),
        "Desimal": float,
        "Teks": str,
        "String": str,
        "Boolean": bool,
        "Daftar": list,
        "List": list,
        "Array": list,
        "Objek": dict,
        "Dict": dict,
        "Map": dict,
        "Tupel": tuple,
        "Tuple": tuple,
        "Set": set,
        "Kosong": type(None),
        "Null": type(None),
    }

    def _type_name_of(self, value: Any) -> str:
        """Nama tipe BroLang dari sebuah nilai (untuk pesan error)."""
        if value is None:
            return "kosong"
        if isinstance(value, bool):
            return "boolean"
        if isinstance(value, int):
            return "angka"
        if isinstance(value, float):
            return "desimal"
        if isinstance(value, str):
            return "teks"
        if isinstance(value, list):
            return "list"
        if isinstance(value, dict):
            return "objek"
        if isinstance(value, tuple):
            return "tuple"
        if isinstance(value, set):
            return "set"
        if isinstance(value, BroLangInstance):
            return value.klass.name
        return type(value).__name__

    def _type_matches(self, value: Any, type_name: Optional[str]) -> bool:
        """Cek apakah nilai cocok dengan anotasi tipe (v6.0)."""
        if not type_name:
            return True
        type_name = type_name.strip()
        if type_name in ("ApaSaja", "Any"):
            return True

        # Union: Angka | Teks
        if "|" in type_name:
            return any(self._type_matches(value, part.strip()) for part in type_name.split("|"))

        # Generics: Daftar<Angka>
        if "<" in type_name and ">" in type_name:
            base = type_name[: type_name.index("<")].strip()
            inner = type_name[type_name.index("<") + 1 : type_name.rindex(">")]
            if not self._type_matches_base(value, base):
                return False
            if isinstance(value, list):
                return all(self._type_matches(item, inner) for item in value)
            return True

        # Alias tipe: tipe ID = Angka
        alias = self.current_env.variables.get(type_name)
        if isinstance(alias, str) and alias != type_name:
            return self._type_matches(value, alias)

        return self._type_matches_base(value, type_name)

    def _type_matches_base(self, value: Any, type_name: str) -> bool:
        type_name = type_name.strip()
        if type_name in ("ApaSaja", "Any"):
            return True
        target = self._TIPE_MAP.get(type_name)
        if target is not None:
            if target == (int, float):
                return isinstance(value, (int, float))
            return isinstance(value, target)
        # Kelas user: value adalah instance (termasuk turunan)
        if isinstance(value, BroLangInstance):
            klass = value.klass
            while klass is not None:
                if klass.name == type_name:
                    return True
                klass = klass.parent
            return False
        # Objek Python/modul
        return type(value).__name__ == type_name

    # ============= Visitor Methods =============

    def visit_ProgramNode(self, node: ProgramNode) -> Any:
        """Visit root program."""
        result = None
        for stmt in node.statements:
            try:
                result = self.visit(stmt)
            except BreakException:
                raise RuntimeError_(
                    message="'hentikan' harus digunakan di dalam loop.",
                )
            except ContinueException:
                raise RuntimeError_(
                    message="'lanjutkan' harus digunakan di dalam loop.",
                )
        return result

    def _make_iterable(self, obj: BroLangInstance):
        """Konversi objek BroLangInstance jadi Python iterable."""
        try:
            iter_func = obj.get("__iter__")
            if callable(iter_func) and not isinstance(iter_func, BroLangInstance):
                result = iter_func(obj)
            else:
                result = iter_func()
            if hasattr(result, "__iter__") and hasattr(result, "__next__"):
                return result
            if isinstance(result, list):
                return result
            # BroLang-style iterator: call __next__ repeatedly
            if hasattr(result, "get"):
                next_func = result.get("__next__")
                if callable(next_func):
                    items = []
                    while True:
                        try:
                            val = next_func(result)
                            items.append(val)
                        except (StopIteration, Exception):
                            break
                    return items
            return list(result) if hasattr(result, "__iter__") else [result]
        except RuntimeError_:
            pass
        try:
            getitem_func = obj.get("__getitem__")
            idx = 0
            result = []
            while True:
                try:
                    if callable(getitem_func) and not isinstance(getitem_func, BroLangInstance):
                        result.append(getitem_func(obj, idx))
                    else:
                        result.append(getitem_func(idx))
                    idx += 1
                except Exception:
                    break
            return result
        except RuntimeError_:
            pass
        return list(obj.attributes.values()) if hasattr(obj, "attributes") else []

    def visit_NumberNode(self, node: NumberNode) -> int:
        return node.value

    def visit_DecimalNode(self, node: DecimalNode) -> float:
        return node.value

    def visit_StringNode(self, node: StringNode) -> str:
        return node.value

    def visit_BooleanNode(self, node: BooleanNode) -> bool:
        return node.value

    def visit_KosongNode(self, node: KosongNode) -> None:
        return None

    def visit_IdentifierNode(self, node: IdentifierNode) -> Any:
        """Mengambil nilai variabel dari environment."""
        name = node.name

        # Check variables first (user variables shadow builtins),
        # naik ke parent env sampai global.
        env = self.current_env
        while env is not None:
            if env.has_variable(name):
                return env.get_variable(name)
            # Fungsi didefinisikan di env (global/local scope)
            if name in env.functions:
                return env.functions[name]
            env = env.parent

        raise NameError_(
            message=f"Variabel '{name}' tidak ditemukan." + saran_keyword(name),
            line=node.line,
            column=node.column,
            solution=f"Deklarasikan '{name}' dengan 'buat {name} = nilai' terlebih dahulu.",
        )

    def visit_VariableNode(self, node: VariableNode) -> Any:
        return self.current_env.get_variable(node.name)

    def visit_AssignmentNode(self, node: AssignmentNode) -> Any:
        """Assignment: buat x = value atau x = value. (v6.0: cek anotasi tipe)"""
        value = self.visit(node.value) if node.value else None

        # Type enforcement v6.0: buat x: Angka = 5
        if node.type_annotation and not self._type_matches(value, node.type_annotation):
            raise TypeError_(
                message=f"Tipe tidak cocok untuk '{node.target.name}': "
                f"diharapkan {node.type_annotation}, "
                f"tapi mendapat {self._type_name_of(value)}.",
                line=node.line,
                column=node.column,
                solution=f"Ubah nilai menjadi {node.type_annotation} atau ubah anotasi tipe.",
            )

        if isinstance(node.target, IdentifierNode):
            name = node.target.name
            if node.is_declaration:
                # v6.5: `konstanta x = 5` — variabel immutable
                self.current_env.define_variable(name, value, is_const=node.is_const)
            else:
                self.current_env.set_variable(name, value, line=node.line, column=node.column)
            return value
        elif isinstance(node.target, IndexNode):
            # Array assignment: list[index] = value
            target = self.visit(node.target.target)
            index = self.visit(node.target.index)
            if isinstance(target, list):
                target[index] = value
            elif isinstance(target, BroLangInstance):
                # Operator overloading: obj[i] = v -> _index_set_(i, v)
                setter = self._get_overload_method(target, "_index_set_")
                if setter is not None:
                    setter(target, index, value)
                else:
                    raise TypeError_(
                        message=f"Objek '{target.klass.name}' tidak bisa di-index assignment.",
                        line=node.line,
                        column=node.column,
                        solution="Implementasikan method _index_set_(self, index, nilai) di kelas.",
                    )
            else:
                raise TypeError_(
                    message="Hanya list yang bisa di-index assignment.",
                    line=node.line,
                    column=node.column,
                )
            return value
        elif isinstance(node.target, ObjectAccessNode):
            # Object attribute assignment: obj.attr = value
            obj = self.visit(node.target.object)
            if isinstance(obj, BroLangInstance):
                obj.set(node.target.property, value)
                return value
            # Python/stdlib object (Sprite, Vec2, ui, partikel, dll):
            # set atribut langsung — konsisten dengan transpiler.
            # Module (SimpleNamespace) tetap error agar typo tidak tertutup.
            import types as _types

            if isinstance(obj, _types.SimpleNamespace):
                raise RuntimeError_(
                    message=f"Objek tidak memiliki atribut '{node.target.property}'.",
                    line=node.line,
                    column=node.column,
                )
            try:
                setattr(obj, node.target.property, value)
                return value
            except (AttributeError, TypeError):
                pass
            raise RuntimeError_(
                message=f"Objek tidak memiliki atribut '{node.target.property}'.",
                line=node.line,
                column=node.column,
            )

        return value

    def visit_BinaryOpNode(self, node: BinaryOpNode) -> Any:
        """Operasi biner dengan type checking runtime."""
        left = self.visit(node.left)
        right = self.visit(node.right)
        op = node.operator

        # Operator overloading (v5.5): instance kelas bisa definisikan
        # method `_tambah_`, `_kurang_`, `_sama_`, dst.
        # Fast path: hanya cek overload bila salah satu operan adalah
        # instance kelas BroLang (objek Python menangani operator sendiri).
        overloaded = None
        if isinstance(left, BroLangInstance) or isinstance(right, BroLangInstance):
            overloaded = self._overload_binary(op, left, right)
        if overloaded is not None:
            return overloaded

        # Comparison operators
        if op == "==":
            return left == right
        elif op == "!=":
            return left != right
        elif op == ">":
            return left > right
        elif op == "<":
            return left < right
        elif op == ">=":
            return left >= right
        elif op == "<=":
            return left <= right
        elif op == "is":
            return left is right
        elif op == "is not":
            return left is not right
        elif op == "dalam":
            return left in right

        # Logical operators
        elif op == "dan":
            return bool(left) and bool(right)
        elif op == "atau":
            return bool(left) or bool(right)

        # Arithmetic operators
        elif op == "+":
            return left + right
        elif op == "-":
            return left - right
        elif op == "*":
            return left * right
        elif op == "/":
            if right == 0:
                raise ZeroDivisionError_(
                    message="Tidak bisa membagi dengan nol.",
                    line=node.line,
                    column=node.column,
                    solution="Pastikan pembagi tidak bernilai 0.",
                )
            return left / right
        elif op == "//":  # v6.8: floor division
            if right == 0:
                raise ZeroDivisionError_(
                    message="Tidak bisa membagi dengan nol.",
                    line=node.line,
                    column=node.column,
                    solution="Pastikan pembagi tidak bernilai 0.",
                )
            return left // right
        elif op == "%":
            if right == 0:
                raise ZeroDivisionError_(
                    message="Tidak bisa modulo dengan nol.",
                    line=node.line,
                    column=node.column,
                )
            return left % right
        elif op == "**":
            return left**right

        # Bitwise operators
        elif op == "&":
            return int(left) & int(right)
        elif op == "|":
            return int(left) | int(right)
        elif op == "^":
            return int(left) ^ int(right)
        elif op == "<<":
            return int(left) << int(right)
        elif op == ">>":
            return int(left) >> int(right)

        raise RuntimeError_(
            message=f"Operator '{op}' tidak dikenal.",
            line=node.line,
            column=node.column,
        )

    def visit_UnaryOpNode(self, node: UnaryOpNode) -> Any:
        """Operasi unary."""
        operand = self.visit(node.operand)

        # Operator overloading (v5.5): `_negasi_`, `_positif_`, dst.
        method = self._get_overload_method(operand, _OVERLOAD_UNARY_MAP.get(node.operator, ""))
        if method is not None:
            return method(operand)

        if node.operator == "-":
            return -operand
        elif node.operator == "+":
            return +operand
        elif node.operator == "bukan":
            return not operand
        elif node.operator == "~":
            return ~int(operand)

        raise RuntimeError_(
            message=f"Operator unary '{node.operator}' tidak dikenal.",
            line=node.line,
            column=node.column,
        )

    def _get_overload_method(self, obj: Any, name: str) -> Optional[Callable]:
        """Ambil method overload dari objek (kalau ada).

        Hanya untuk BroLangInstance — objek Python/stdlib menangani
        operator-nya sendiri via dunder Python.
        """
        if not name or not isinstance(obj, BroLangInstance):
            return None
        try:
            method = obj.get(name)
        except RuntimeError_:
            return None
        if callable(method) and not isinstance(method, BroLangInstance):
            return method
        return None

    def _overload_binary(self, op: str, left: Any, right: Any):
        """Coba panggil method overload untuk operator biner.

        Kembalikan hasilnya, atau None kalau tidak ada overload.
        Operator `dalam` (in) hanya di-overload lewat operand kanan.
        """
        method_name = _OVERLOAD_BINARY_MAP.get(op)
        if method_name is None:
            return None
        pairs = ((right, left),) if op == "dalam" else ((left, right), (right, left))
        for operand, other in pairs:
            method = self._get_overload_method(operand, method_name)
            if method is not None:
                # Method instance: panggil dengan operand sebagai `self`.
                return method(operand, other)
        # `!=` tanpa _tidak_sama_ = negasi `_sama_` (konsisten dengan Python
        # dan transpiler yang menghasilkan dunder __ne__ otomatis).
        if op == "!=":
            for operand, other in pairs:
                eq = self._get_overload_method(operand, "_sama_")
                if eq is not None:
                    return not eq(operand, other)
        return None

    def visit_IfNode(self, node: IfNode) -> Optional[Any]:
        """If-else execution."""
        condition = self.visit(node.condition)

        if condition:
            self._push_env()
            result = None
            for stmt in node.body:
                result = self.visit(stmt)
                if self.current_env.should_return:
                    break
            self._pop_env()
            return result
        else:
            # Check elif
            for i, elif_cond in enumerate(node.elif_conditions):
                if self.visit(elif_cond):
                    self._push_env()
                    result = None
                    for stmt in node.elif_bodies[i]:
                        result = self.visit(stmt)
                        if self.current_env.should_return:
                            break
                    self._pop_env()
                    return result

            # Else
            if node.else_body:
                self._push_env()
                result = None
                for stmt in node.else_body:
                    result = self.visit(stmt)
                    if self.current_env.should_return:
                        break
                self._pop_env()
                return result

        return None

    def visit_WhileNode(self, node: WhileNode) -> None:
        """While loop execution with optional else clause."""
        broke = False
        while True:
            condition = self.visit(node.condition)
            if not condition:
                break

            try:
                self._push_env()
                for stmt in node.body:
                    self.visit(stmt)
                    if self.current_env.should_return:
                        self._pop_env()
                        return
                self._pop_env()
            except BreakException:
                self._pop_env()
                broke = True
                break
            except ContinueException:
                self._pop_env()
                continue

        # Execute else clause if loop completed normally (not via break)
        if not broke and node.else_body:
            self._push_env()
            for stmt in node.else_body:
                self.visit(stmt)
            self._pop_env()

    def visit_DoUntilNode(self, node: DoUntilNode) -> None:
        """Do-until loop (v6.5): ulangi ... sampai kondisi.

        Body dijalankan minimal sekali, lalu kondisi dicek setelah body.
        Loop berhenti saat kondisi bernilai benar (true).
        """
        while True:
            try:
                self._push_env()
                for stmt in node.body:
                    self.visit(stmt)
                    if self.current_env.should_return:
                        self._pop_env()
                        return
                self._pop_env()
            except BreakException:
                self._pop_env()
                break
            except ContinueException:
                self._pop_env()
                continue

            condition = self.visit(node.condition)
            if condition:
                break

    def visit_RangeForNode(self, node: RangeForNode) -> None:
        """Range for loop (v6.5): untuk i dari 1 sampai 10 langkah 2.

        Iterasi angka inklusif dari start sampai end. Langkah default
        otomatis 1 (atau -1 jika start > end).
        """
        start = self.visit(node.start)
        end = self.visit(node.end)

        if node.step is not None:
            step = self.visit(node.step)
            if step == 0:
                raise RuntimeError_(
                    message="Langkah range tidak boleh nol.",
                    line=node.line,
                    column=node.column,
                    solution="Gunakan langkah selain 0, misal 'langkah 1' atau 'langkah -1'.",
                )
        else:
            step = 1 if start <= end else -1

        # Inklusif: batas atas end + 1 (step positif) atau end - 1 (step negatif)
        items = list(range(start, end + (1 if step > 0 else -1), step))

        broke = False
        for item in items:
            self._push_env()
            self.current_env.define_variable(node.variable, item)

            try:
                for stmt in node.body:
                    self.visit(stmt)
                    if self.current_env.should_return:
                        self._pop_env()
                        return
                self._pop_env()
            except BreakException:
                self._pop_env()
                broke = True
                break
            except ContinueException:
                self._pop_env()
                continue

        if not broke and node.else_body:
            self._push_env()
            for stmt in node.else_body:
                self.visit(stmt)
            self._pop_env()

    def visit_ForNode(self, node: ForNode) -> None:
        """For loop execution with optional else clause."""
        iterable = self.visit(node.iterable)

        if isinstance(iterable, BroLangInstance):
            iterable = self._make_iterable(iterable)
        elif isinstance(iterable, dict):
            iterable = list(iterable.keys())

        broke = False

        for item in iterable:
            self._push_env()
            self.current_env.define_variable(node.variable, item)

            try:
                for stmt in node.body:
                    self.visit(stmt)
                    if self.current_env.should_return:
                        self._pop_env()
                        return
                self._pop_env()
            except BreakException:
                self._pop_env()
                broke = True
                break
            except ContinueException:
                self._pop_env()
                continue

        # Execute else clause if loop completed normally (not via break)
        if not broke and node.else_body:
            self._push_env()
            for stmt in node.else_body:
                self.visit(stmt)
            self._pop_env()

    def visit_BreakNode(self, node: BreakNode) -> None:
        """Break statement. (v6.8: guard `hentikan jika x` — lewati jika x salah)"""
        guard = getattr(node, "guard", None)
        if guard is not None and not self.visit(guard):
            return None
        raise BreakException()

    def visit_ContinueNode(self, node: ContinueNode) -> None:
        """Continue statement. (v6.8: guard `lanjutkan jika x` — lewati jika x salah)"""
        guard = getattr(node, "guard", None)
        if guard is not None and not self.visit(guard):
            return None
        raise ContinueException()

    def visit_PassNode(self, node: PassNode) -> None:
        """Pass statement (no-op)."""
        pass

    def visit_DelNode(self, node: DelNode) -> None:
        """Del statement."""
        if isinstance(node.target, IdentifierNode):
            name = node.target.name
            # Search for variable in environments
            env = self.current_env
            while env is not None:
                if name in env.variables:
                    del env.variables[name]
                    return
                env = env.parent
            raise NameError_(
                message=f"Variabel '{name}' tidak ditemukan untuk dihapus.",
                line=node.line,
                column=node.column,
            )
        elif isinstance(node.target, IndexNode):
            target = self.visit(node.target.target)
            index = self.visit(node.target.index)
            if isinstance(target, (list, dict)):
                try:
                    del target[index]
                except Exception as e:
                    raise RuntimeError_(
                        message=f"Gagal menghapus elemen: {e}",
                        line=node.line,
                        column=node.column,
                    )
            else:
                raise TypeError_(
                    message=f"Tipe {type(target).__name__} tidak bisa dihapus elemennya.",
                    line=node.line,
                    column=node.column,
                )
        elif isinstance(node.target, ObjectAccessNode):
            obj = self.visit(node.target.object)
            prop = node.target.property
            if isinstance(obj, dict):
                if prop in obj:
                    del obj[prop]
                else:
                    raise RuntimeError_(
                        message=f"Kunci '{prop}' tidak ditemukan.",
                        line=node.line,
                        column=node.column,
                    )
            elif isinstance(obj, BroLangInstance):
                if prop in obj.attributes:
                    del obj.attributes[prop]
                else:
                    raise RuntimeError_(
                        message=f"Atribut '{prop}' tidak ditemukan.",
                        line=node.line,
                        column=node.column,
                    )
        else:
            raise RuntimeError_(
                message="Target 'hapus' tidak valid.",
                line=node.line,
                column=node.column,
            )

    def visit_AssertNode(self, node: AssertNode) -> None:
        """Assert statement."""
        condition = self.visit(node.condition)
        if not condition:
            msg = self.visit(node.message) if node.message else "Assertion gagal"
            raise RuntimeError_(
                message=f"Pastikan: {msg}",
                line=node.line,
                column=node.column,
            )

    def visit_FunctionNode(self, node: FunctionNode) -> None:
        """Deklarasi fungsi dengan closure support."""
        closure_env = self.current_env

        def bro_function(*args, **kwargs):
            old_env = self.current_env
            self._push_env()
            self.current_env.parent = closure_env

            for param, val in self._bind_params(
                node.params, node.defaults, args, kwargs, node, node.rest_param
            ):
                self.current_env.define_variable(param, val)

            try:
                result = None
                for stmt in node.body:
                    result = self.visit(stmt)
                    if self.current_env.should_return:
                        result = self.current_env.return_value
                        break
                self._pop_env()
                self.current_env = old_env
                return result
            except ReturnException as e:
                self._pop_env()
                self.current_env = old_env
                return e.value

        def generator_func(*args, **kwargs):
            bound = self._bind_params(
                node.params, node.defaults, args, kwargs, node, node.rest_param
            )
            return BroLangGenerator(
                body=node.body,
                params=[p for p, _ in bound],
                args=[v for _, v in bound],
                defaults=node.defaults,
                closure_env=closure_env,
                interpreter=self,
            )

        # Penanda fungsi BroLang — dipakai modul `sejajar` untuk serialisasi
        # aman saat dijalankan dari thread (interpreter tidak thread-safe).
        bro_function._brolang_fn = True
        generator_func._brolang_fn = True

        if _has_yield_in_body(node.body):
            self.current_env.functions[node.name] = generator_func
        else:
            self.current_env.functions[node.name] = bro_function

    def visit_ReturnNode(self, node: ReturnNode) -> None:
        """Return statement. (v6.8: guard `kembali x jika c` — lewati jika c salah)"""
        guard = getattr(node, "guard", None)
        if guard is not None and not self.visit(guard):
            return None
        value = self.visit(node.value) if node.value else None
        self.current_env.should_return = True
        self.current_env.return_value = value
        raise ReturnException(value)

    def visit_CallNode(self, node: CallNode) -> Any:
        """Function/method call (v6.7: dukung spread call f(...daftar))."""
        args = []
        for arg in node.args:
            if isinstance(arg, SpreadNode):
                args.extend(self.visit(arg))
            else:
                args.append(self.visit(arg))
        kwargs = {name: self.visit(val) for name, val in node.kwargs}

        # Method call
        if node.is_method and node.object_name:
            # This is a method call; function is an ObjectAccessNode
            if isinstance(node.function, ObjectAccessNode):
                obj = self.visit(node.function.object)
                method_name = node.function.property
                if isinstance(obj, BroLangInstance):
                    # Check if class has this method first
                    method = obj.klass.get_method(method_name)
                    if method is not None:
                        access = obj.klass.get_method_access(method_name)
                        caller = self._current_class_name
                        if access == "privat" and caller != obj.klass.name:
                            raise RuntimeError_(
                                message=f"Akses ditolak: '{method_name}' bersifat privat di kelas '{obj.klass.name}'.",
                                line=node.line,
                                column=node.column,
                                solution=f"Hapus modifier 'privat' atau akses dari dalam kelas {obj.klass.name}.",
                            )
                        if access == "terlindungi" and caller not in (
                            obj.klass.name,
                            _get_subclass_names(obj.klass),
                        ):
                            raise RuntimeError_(
                                message=f"Akses ditolak: '{method_name}' bersifat terlindungi di kelas '{obj.klass.name}'.",
                                line=node.line,
                                column=node.column,
                                solution=f"Akses '{method_name}' hanya bisa dari kelas {obj.klass.name} atau keturunannya.",
                            )
                        if not getattr(method, "_brolang_static", False):
                            return method(obj, *args, **kwargs)
                        return method(*args, **kwargs)
                    # Built-in get/set for property access (only if no class method)
                    if method_name == "get":
                        return (
                            obj.get(args[0], caller_class=self._current_class_name) if args else obj
                        )
                    if method_name == "set" and len(args) >= 2:
                        obj.set(args[0], args[1])
                        return None
                # Stdlib module method
                if hasattr(obj, method_name):
                    bound_method = getattr(obj, method_name)
                    if callable(bound_method):
                        return bound_method(*args, **kwargs)
                # List methods
                if isinstance(obj, list):
                    methods = self._get_list_methods(obj)
                    if method_name in methods:
                        return methods[method_name](*args, **kwargs)
                # Dict methods
                if isinstance(obj, dict):
                    methods = self._get_dict_methods(obj)
                    if method_name in methods:
                        return methods[method_name](*args, **kwargs)
                # String methods
                if isinstance(obj, str):
                    methods = self._get_string_methods(obj)
                    if method_name in methods:
                        return methods[method_name](*args, **kwargs)
                raise RuntimeError_(
                    message=f"Objek tidak memiliki method '{method_name}'.",
                )

        # Direct function call
        if isinstance(node.function, IdentifierNode):
            func_name = node.function.name

            # Check all environments for function
            env = self.current_env
            while env is not None:
                if func_name in env.functions:
                    func = env.functions[func_name]
                    return func(*args, **kwargs)
                if env.has_variable(func_name):
                    func = env.get_variable(func_name)
                    if callable(func):
                        return func(*args, **kwargs)
                env = env.parent

            raise NameError_(
                message=f"Fungsi '{func_name}' tidak ditemukan." + saran_keyword(func_name),
                line=node.line,
                column=node.column,
                solution=f"Definisikan fungsi '{func_name}' dengan 'fungsi {func_name}(...)'.",
            )

        # Call on expression result
        func = self.visit(node.function)
        if callable(func):
            return func(*args, **kwargs)

        raise RuntimeError_(
            message=f"'{func}' bukan fungsi yang bisa dipanggil.",
        )

    def visit_ClassNode(self, node: ClassNode) -> None:
        """Deklarasi kelas."""
        methods = {}
        method_access = {}
        old_class_name = self._current_class_name
        self._current_class_name = node.name

        for stmt in node.body:
            if isinstance(stmt, AccessModifierNode):
                modifier = stmt.modifier
                target = stmt.target
                if isinstance(target, FunctionNode):
                    method_func = self._create_method(target)
                    methods[target.name] = method_func
                    method_access[target.name] = modifier
            elif isinstance(stmt, FunctionNode):
                method_func = self._create_method(stmt)
                methods[stmt.name] = method_func
                method_access[stmt.name] = "publik"
            elif isinstance(stmt, MethodNode):
                method_func = self._create_method(stmt)
                methods[stmt.name] = method_func
                method_access[stmt.name] = "publik"

        parent_class = None
        if node.parent:
            if node.parent in self.current_env.classes:
                parent_class = self.current_env.classes[node.parent]

        is_abstract = getattr(node, "is_abstract", False)
        abstract_methods = getattr(node, "abstract_methods", [])
        required_interfaces = getattr(node, "implements", []) or []

        klass = BroLangClass(
            node.name,
            methods,
            parent_class,
            is_abstract=is_abstract,
            abstract_methods=abstract_methods,
            required_interfaces=required_interfaces,
            method_access=method_access,
        )

        # Cek interface enforcement
        for iface_name in required_interfaces:
            if iface_name in self.current_env.interfaces:
                iface = self.current_env.interfaces[iface_name]
                for method_sig in iface["methods"]:
                    if method_sig not in methods:
                        raise RuntimeError_(
                            message=f"Kelas '{node.name}' harus mengimplementasi method '{method_sig}' dari antarmuka '{iface_name}'.",
                            line=node.line,
                            column=node.column,
                            solution=f"Tambahkan method '{method_sig}' ke kelas '{node.name}'.",
                        )

        # Constructor: create instance
        def class_constructor(*args, **kwargs):
            if klass.is_abstract:
                raise RuntimeError_(
                    message=f"Tidak bisa membuat instance dari kelas abstrak '{node.name}'.",
                    line=node.line,
                    column=node.column,
                    solution=f"Buat kelas turunan yang mengimplementasi semua method abstrak dari '{node.name}'.",
                )
            instance = BroLangInstance(klass)
            old_class_name = self._current_class_name
            self._current_class_name = node.name
            init_method = klass.get_method("__init__")
            if init_method:
                init_method(instance, *args, **kwargs)
            self._current_class_name = old_class_name
            return instance

        self.current_env.variables[node.name] = class_constructor
        self.current_env.classes[node.name] = klass

        # Attach static methods to constructor for Class.method() access
        for name, method in methods.items():
            for stmt in node.body:
                if (
                    isinstance(stmt, FunctionNode)
                    and stmt.name == name
                    and getattr(stmt, "is_static", False)
                ):
                    setattr(class_constructor, name, method)
                    break
                elif isinstance(stmt, AccessModifierNode) and isinstance(stmt.target, FunctionNode):
                    if stmt.target.name == name and getattr(stmt.target, "is_static", False):
                        setattr(class_constructor, name, method)
                        break

        self._current_class_name = old_class_name

    def visit_KelasErrorNode(self, node: KelasErrorNode) -> None:
        """Kelas error kustom (v6.0): kelas_error Nama extends Induk ... selesai.

        Error kustom membuat penanganan error profesional:
            kelas_error SaldoTidakCukup extends Kesalahan
                fungsi __init__(pesan)
                    self.pesan = pesan
                selesai
            selesai

            coba
                lempar SaldoTidakCukup("Saldo tidak cukup")
            kecuali SaldoTidakCukup sebagai e
                tulis e.pesan
            selesai
        """
        methods = {}
        method_access = {}
        old_class_name = self._current_class_name
        self._current_class_name = node.name

        for stmt in node.body:
            if isinstance(stmt, AccessModifierNode):
                modifier = stmt.modifier
                target = stmt.target
                if isinstance(target, FunctionNode):
                    method_func = self._create_method(target)
                    methods[target.name] = method_func
                    method_access[target.name] = modifier
            elif isinstance(stmt, FunctionNode):
                method_func = self._create_method(stmt)
                methods[stmt.name] = method_func
                method_access[stmt.name] = "publik"
            elif isinstance(stmt, MethodNode):
                method_func = self._create_method(stmt)
                methods[stmt.name] = method_func
                method_access[stmt.name] = "publik"

        parent_class = None
        # Default parent: Kesalahan (kelas dasar error kustom)
        parent_name = node.parent or "Kesalahan"
        if parent_name in self.current_env.classes:
            parent_class = self.current_env.classes[parent_name]

        klass = BroLangClass(
            node.name,
            methods,
            parent_class,
            is_abstract=False,
            abstract_methods=[],
            required_interfaces=[],
            method_access=method_access,
        )
        klass.is_error_class = True  # penanda kelas error kustom

        def error_constructor(*args, **kwargs):
            instance = BroLangInstance(klass)
            old_cn = self._current_class_name
            self._current_class_name = node.name
            init_method = klass.get_method("__init__")
            if init_method:
                init_method(instance, *args, **kwargs)
            self._current_class_name = old_cn
            return instance

        self.current_env.variables[node.name] = error_constructor
        self.current_env.classes[node.name] = klass
        self._current_class_name = old_class_name

    def _create_method(self, node) -> Callable:
        """Membuat method dari FunctionNode atau MethodNode."""
        owner_class_name = self._current_class_name
        is_static = getattr(node, "is_static", False)

        if is_static:

            def static_method(*args, **kwargs):
                old_env = self.current_env
                old_class_name = self._current_class_name
                self._current_class_name = owner_class_name
                self._push_env()

                for param, val in self._bind_params(
                    node.params, node.defaults, args, kwargs, node, node.rest_param
                ):
                    self.current_env.define_variable(param, val)

                try:
                    result = None
                    for stmt in node.body:
                        result = self.visit(stmt)
                        if self.current_env.should_return:
                            result = self.current_env.return_value
                            break
                    self._pop_env()
                    self.current_env = old_env
                    self._current_class_name = old_class_name
                    return result
                except ReturnException as e:
                    self._pop_env()
                    self.current_env = old_env
                    self._current_class_name = old_class_name
                    return e.value

            static_method._brolang_static = True
            static_method._brolang_fn = True
            return static_method

        def method(self_instance, *args, **kwargs):
            old_env = self.current_env
            old_class_name = self._current_class_name
            self._current_class_name = owner_class_name
            self._push_env()
            self.current_env.define_variable("self", self_instance)

            # Params tanpa 'self'
            real_params = [p for p in node.params if p != "self"]
            real_defaults = []
            for p in node.params:
                if p != "self":
                    idx = node.params.index(p)
                    real_defaults.append(node.defaults[idx] if idx < len(node.defaults) else None)

            for param, val in self._bind_params(
                real_params, real_defaults, args, kwargs, node, node.rest_param
            ):
                self.current_env.define_variable(param, val)

            try:
                result = None
                for stmt in node.body:
                    result = self.visit(stmt)
                    if self.current_env.should_return:
                        result = self.current_env.return_value
                        break
                self._pop_env()
                self.current_env = old_env
                self._current_class_name = old_class_name
                return result
            except ReturnException as e:
                self._pop_env()
                self.current_env = old_env
                self._current_class_name = old_class_name
                return e.value

        method._brolang_fn = True
        return method

    def visit_AttributeNode(self, node: AttributeNode) -> Any:
        """Akses atribut (deprecated, use ObjectAccessNode)."""
        obj = self.visit(node.object)
        if isinstance(obj, BroLangInstance):
            return obj.get(node.attribute)
        if hasattr(obj, node.attribute):
            return getattr(obj, node.attribute)
        raise RuntimeError_(
            message=f"Objek tidak memiliki atribut '{node.attribute}'.",
            line=node.line,
            column=node.column,
        )

    def visit_ObjectAccessNode(self, node: ObjectAccessNode) -> Any:
        """Akses properti/method objek."""
        obj = self.visit(node.object)
        prop = node.property

        if isinstance(obj, BroLangInstance):
            # Expose Python-level get/set for property access
            if prop == "get":
                return lambda name: obj.get(name, caller_class=self._current_class_name)
            if prop == "set":
                return lambda name, value: obj.set(name, value)
            return obj.get(prop, caller_class=self._current_class_name)

        if isinstance(obj, dict):
            if prop in obj:
                return obj[prop]
            methods = self._get_dict_methods(obj)
            if prop in methods:
                return methods[prop]
            raise RuntimeError_(
                message=f"Objek tidak memiliki properti '{prop}'.",
                line=node.line,
                column=node.column,
            )

        if isinstance(obj, list):
            methods = self._get_list_methods(obj)
            if prop in methods:
                return methods[prop]
            raise RuntimeError_(
                message=f"List tidak memiliki method '{prop}'.",
                line=node.line,
                column=node.column,
            )

        if isinstance(obj, str):
            methods = self._get_string_methods(obj)
            if prop in methods:
                return methods[prop]
            raise RuntimeError_(
                message=f"String tidak memiliki method '{prop}'.",
                line=node.line,
                column=node.column,
            )

        if isinstance(obj, str):
            methods = self._get_string_methods(obj)
            if prop in methods:
                return methods[prop]
            raise RuntimeError_(
                message=f"String tidak memiliki method '{prop}'.",
                line=node.line,
                column=node.column,
            )

        if isinstance(obj, BroLangClass):
            method = obj.get_method(prop)
            if method is not None:
                return method
            raise RuntimeError_(
                message=f"Kelas '{obj.name}' tidak memiliki method '{prop}'.",
                line=node.line,
                column=node.column,
            )

        if hasattr(obj, prop):
            return getattr(obj, prop)

        raise RuntimeError_(
            message=f"Tidak bisa mengakses '{prop}' pada tipe {type(obj).__name__}.",
            line=node.line,
            column=node.column,
        )

    def visit_ImportNode(self, node: ImportNode) -> None:
        """Import module."""
        module_name = node.module
        try:
            module = get_stdlib_module(module_name)
            alias = node.alias or module_name.split(".")[0]
            self.current_env.variables[alias] = module
        except ImportError:
            # Coba package BroLang yang terinstall (bro pkg install)
            try:
                from brolang.package_manager.manager import PackageManager

                pkg_manager = PackageManager()
                pkg_dir = pkg_manager.find_package(module_name)
                if pkg_dir:
                    module_obj = self._load_brolang_package(pkg_dir, module_name)
                    alias = node.alias or module_name
                    self.current_env.variables[alias] = module_obj
                    return
            except Exception:
                pass
            # Try Python import
            try:
                import importlib

                py_module = importlib.import_module(module_name)
                alias = node.alias or module_name
                self.current_env.variables[alias] = py_module
            except ImportError:
                raise RuntimeError_(
                    message=f"Module '{module_name}' tidak ditemukan.",
                    line=node.line,
                    column=node.column,
                    solution=f"Pastikan modul '{module_name}' sudah terinstal (bro pkg install {module_name}).",
                )

    def _load_brolang_package(self, pkg_dir: str, module_name: str) -> Any:
        """Memuat package BroLang (.bro) dari folder terinstall sebagai module.

        Mengeksekusi file main package (brolang.json / __init__.bro) dalam
        interpreter terpisah dan mengumpulkan fungsi/kelas yang didefinisikan.
        """
        import types
        import json
        from brolang.lexer import Lexer
        from brolang.parser import Parser

        # Tentukan file main
        main_file = "__init__.bro"
        manifest_path = os.path.join(pkg_dir, "brolang.json")
        if os.path.exists(manifest_path):
            try:
                with open(manifest_path, "r", encoding="utf-8") as f:
                    manifest = json.load(f)
                main_file = manifest.get("main", main_file)
            except json.JSONDecodeError:
                pass

        main_path = os.path.join(pkg_dir, main_file)
        if not os.path.exists(main_path):
            # Cari file .bro pertama sebagai fallback
            for f in sorted(os.listdir(pkg_dir)):
                if f.endswith(".bro"):
                    main_path = os.path.join(pkg_dir, f)
                    break
            else:
                raise RuntimeError_(
                    message=f"Package '{module_name}' tidak memiliki file .bro.",
                )

        with open(main_path, "r", encoding="utf-8") as f:
            source = f.read()

        sub_interp = Interpreter()
        ast = Parser(Lexer(source, file_path=main_path).tokenize(), file_path=main_path).parse()
        sub_interp.interpret(ast)

        # Kumpulkan API publik: fungsi + kelas + variabel
        module_obj = types.SimpleNamespace()
        env = sub_interp.global_env
        for name in list(env.functions.keys()):
            setattr(module_obj, name, env.functions[name])
        for name in list(env.classes.keys()):
            setattr(module_obj, name, env.variables[name])
        for name, val in env.variables.items():
            if not name.startswith("_"):
                setattr(module_obj, name, val)
        module_obj.__name__ = module_name
        return module_obj

    def visit_FromImportNode(self, node: FromImportNode) -> None:
        """From-import statement."""
        try:
            module = get_stdlib_module(node.module)
            for name in node.names:
                if hasattr(module, name):
                    self.current_env.variables[name] = getattr(module, name)
                else:
                    raise RuntimeError_(
                        message=f"Module '{node.module}' tidak memiliki '{name}'.",
                    )
        except ImportError:
            try:
                import importlib

                py_module = importlib.import_module(node.module)
                for name in node.names:
                    if hasattr(py_module, name):
                        self.current_env.variables[name] = getattr(py_module, name)
            except ImportError:
                raise RuntimeError_(
                    message=f"Module '{node.module}' tidak ditemukan.",
                    line=node.line,
                    column=node.column,
                )

    def visit_TryNode(self, node: TryNode) -> Optional[Any]:
        """Try-catch-finally execution."""
        try:
            self._push_env()
            result = None
            for stmt in node.body:
                result = self.visit(stmt)
            self._pop_env()
            if node.finally_body:
                self._push_env()
                for stmt in node.finally_body:
                    self.visit(stmt)
                self._pop_env()
            return result
        except Exception as e:
            self._pop_env()
            self._push_env()
            self.current_env.define_variable(node.catch_var, e)
            result = None
            for stmt in node.catch_body:
                result = self.visit(stmt)
            self._pop_env()
            if node.finally_body:
                self._push_env()
                for stmt in node.finally_body:
                    self.visit(stmt)
                self._pop_env()
            return result

    def visit_SpreadNode(self, node: SpreadNode) -> Any:
        """Spread operator (v6.7): ...nilai.

        Nilai harus iterable; hasilnya didorong ke konteks pemakai
        (list literal, tuple, atau argumen pemanggilan).
        """
        value = self.visit(node.value)
        if not hasattr(value, "__iter__") or isinstance(value, (str, dict)):
            raise TypeError_(
                message=f"Spread (...) membutuhkan list/tuple, tapi mendapat {self._type_name_of(value)}.",
                line=node.line,
                column=node.column,
                solution="Berikan list atau tuple untuk di-spread.",
                example="buat a = [1, 2]\nbuat b = [...a, 3]  # [1, 2, 3]",
            )
        return list(value)

    def visit_ListNode(self, node: ListNode) -> List[Any]:
        """List literal (v6.7: dukung spread [...a, 1])."""
        result = []
        for elem in node.elements:
            if isinstance(elem, SpreadNode):
                result.extend(self.visit(elem))
            else:
                result.append(self.visit(elem))
        return result

    def visit_TupleNode(self, node: TupleNode) -> tuple:
        """Tuple literal (v6.7: dukung spread (...a))."""
        result = []
        for elem in node.elements:
            if isinstance(elem, SpreadNode):
                result.extend(self.visit(elem))
            else:
                result.append(self.visit(elem))
        return tuple(result)

    def visit_SetNode(self, node: SetNode) -> set:
        """Set literal."""
        return set(self.visit(elem) for elem in node.elements)

    def visit_DictComprehensionNode(self, node: DictComprehensionNode) -> Dict[str, Any]:
        """Dict comprehension."""
        iterable = self.visit(node.iterable)
        result = {}
        for item in iterable:
            self._push_env()
            if node.value_var:
                self.current_env.define_variable(node.key_var, item[0])
                self.current_env.define_variable(node.value_var, item[1])
            else:
                self.current_env.define_variable(node.key_var, item)

            if node.condition:
                cond_result = self.visit(node.condition)
                if not cond_result:
                    self._pop_env()
                    continue

            key = self.visit(node.key_expr)
            value = self.visit(node.value_expr)
            result[key] = value
            self._pop_env()
        return result

    def visit_IndexNode(self, node: IndexNode) -> Any:
        """Indexing or slicing operation."""
        target = self.visit(node.target)

        if node.is_slice:
            # Slicing operation
            if not isinstance(target, (list, str)):
                raise TypeError_(
                    message=f"Tipe {type(target).__name__} tidak bisa di-slice.",
                    line=node.line,
                    column=node.column,
                )
            start = self.visit(node.slice_start) if node.slice_start else None
            stop = self.visit(node.slice_stop) if node.slice_stop else None
            step = self.visit(node.slice_step) if node.slice_step else None
            try:
                return target[start:stop:step]
            except Exception as e:
                raise RuntimeError_(
                    message=f"Error slicing: {e}",
                    line=node.line,
                    column=node.column,
                )

        # Regular indexing
        index = self.visit(node.index)

        if isinstance(target, (list, str, tuple)):
            try:
                return target[index]
            except IndexError:
                raise IndexError_(
                    message=f"Indeks {index} di luar batas. Panjang: {len(target)}.",
                    line=node.line,
                    column=node.column,
                    solution=f"Gunakan indeks antara 0 dan {len(target) - 1}.",
                )

        if isinstance(target, dict):
            # Indexing objek: objek["kunci"] (v6.0 — stdlib mengembalikan dict)
            if index in target:
                return target[index]
            raise RuntimeError_(
                message=f"Kunci '{index}' tidak ditemukan di objek.",
                line=node.line,
                column=node.column,
                solution="Periksa nama kunci yang digunakan.",
            )

        # BroLangInstance __getitem__ support (v5.5: `_index_`)
        if isinstance(target, BroLangInstance):
            for nama in ("_index_", "__getitem__"):
                try:
                    getitem_func = target.get(nama)
                    if callable(getitem_func) and not isinstance(getitem_func, BroLangInstance):
                        return getitem_func(target, index)
                except RuntimeError_:
                    continue
            raise TypeError_(
                message=f"Objek '{target.klass.name}' tidak bisa di-index.",
                line=node.line,
                column=node.column,
                solution="Implementasikan method _index_(self, index) di kelas.",
            )

        raise TypeError_(
            message=f"Tipe {type(target).__name__} tidak bisa di-index.",
            line=node.line,
            column=node.column,
        )

    def visit_ObjectNode(self, node: ObjectNode) -> Dict[str, Any]:
        """Object/dict literal."""
        return {k: self.visit(v) for k, v in node.entries.items()}

    def visit_PrintNode(self, node: PrintNode) -> None:
        """Print statement."""
        values = [self.visit(node.expression)]
        for arg in node.args:
            values.append(self.visit(arg))

        output = " ".join(self._format_value(v) for v in values)
        self.output.append(output)
        print(output)

    def _format_value(self, value: Any) -> str:
        """Format nilai untuk output — hormati overload `_teks_`."""
        method = self._get_overload_method(value, "_teks_")
        if method is not None:
            try:
                return str(method(value))
            except Exception:
                pass
        return str(value)

    def visit_InputNode(self, node: InputNode) -> str:
        """Input statement."""
        if node.prompt:
            prompt = str(self.visit(node.prompt))
            return input(prompt)
        return input()

    # ============= V2: Lambda =============

    def visit_LambdaNode(self, node: LambdaNode) -> Callable:
        """Lambda expression with closure: lalu(x) x + 1"""
        # Capture the enclosing environment at definition time (closure)
        closure_env = self.current_env

        def lambda_func(*args, **kwargs):
            old_env = self.current_env
            # Create new env with captured closure env as parent
            self._push_env()
            self.current_env.parent = closure_env
            for param, val in self._bind_params(node.params, [], args, kwargs, node, node.rest_param):
                self.current_env.define_variable(param, val)
            try:
                result = self.visit(node.body)
                self._pop_env()
                self.current_env = old_env
                return result
            except ReturnException as e:
                self._pop_env()
                self.current_env = old_env
                return e.value
            except Exception as e:
                self._pop_env()
                self.current_env = old_env
                raise e

        lambda_func._brolang_fn = True
        return lambda_func

    # ============= V2: Comprehension =============

    def visit_ComprehensionNode(self, node: ComprehensionNode) -> List[Any]:
        """List comprehension: [expr lalu var dalam iterable]"""
        iterable = self.visit(node.iterable)
        result = []
        for item in iterable:
            self._push_env()
            self.current_env.define_variable(node.variable, item)
            if node.condition:
                cond_val = self.visit(node.condition)
                if cond_val:
                    result.append(self.visit(node.expr))
            else:
                result.append(self.visit(node.expr))
            self._pop_env()
        return result

    # ============= V2: F-String =============

    def visit_FStringNode(self, node: FStringNode) -> str:
        """F-string interpolation: f"Halo {nama}" """
        result = []
        for ptype, pval in node.parts:
            if ptype == "literal":
                result.append(str(pval))
            elif ptype == "expr":
                val = self.visit(pval)
                result.append(str(val))
        return "".join(result)

    # ============= V2: Enum =============

    def visit_EnumNode(self, node: EnumNode) -> None:
        """Enum declaration: enum Warna { MERAH, BIRU, HIJAU }"""
        enum_members = {}
        enum_class = type(
            node.name,
            (),
            {
                "__init__": lambda self, val=None: setattr(self, "value", val),
                "__repr__": lambda self: f"{self.__class__.__name__}.{getattr(self, '_member_name', '?')}",
                "__eq__": lambda self, other: isinstance(other, type(self))
                and self.value == other.value,
                "__hash__": lambda self: hash(getattr(self, "value", 0)),
            },
        )
        for i, member in enumerate(node.members):
            instance = enum_class(val=i)
            instance._member_name = member
            instance._enum_name = node.name
            enum_members[member] = instance
            setattr(enum_class, member, instance)
        enum_class._members = enum_members
        enum_class._member_names = node.members
        self.current_env.variables[node.name] = enum_class

    # ============= V2: Struct =============

    def visit_StructNode(self, node: StructNode) -> None:
        """Struct declaration: struktur Titik { x, y }"""
        struct_class = type(
            node.name,
            (),
            {
                "__init__": lambda self, *args: _struct_init(self, node.fields, args),
                "__repr__": lambda self: f"{node.name}({', '.join(str(getattr(self, f)) for f in node.fields)})",
            },
        )
        struct_class._fields = node.fields
        self.current_env.variables[node.name] = struct_class

    def visit_StructInstanceNode(self, node: StructInstanceNode) -> Any:
        """Struct instantiation: Titik(10, 20)"""
        struct_class = self.current_env.get_variable(node.struct_name)
        args = [self.visit(arg) for arg in node.args]
        return struct_class(*args)

    # ============= V2: Match/Case =============

    def visit_MatchNode(self, node: MatchNode) -> Any:
        """Match/case (v6.0): pola list/objek/binding/guard/literal."""
        value = self.visit(node.value)
        for idx, (pattern, body) in enumerate(node.cases):
            bindings: Dict[str, Any] = {}
            if not self._match_pattern(value, pattern, bindings):
                continue

            # Guard: cocokkan x jika x > 10
            guard = node.guards[idx] if idx < len(node.guards) else None
            if guard is not None:
                self._push_env()
                for k, v in bindings.items():
                    self.current_env.define_variable(k, v)
                try:
                    if not self.visit(guard):
                        continue
                finally:
                    self._pop_env()

            self._push_env()
            for k, v in bindings.items():
                self.current_env.define_variable(k, v)
            result = None
            for stmt in body:
                result = self.visit(stmt)
                if self.current_env.should_return:
                    break
            self._pop_env()
            return result

        # Default case (_)
        if node.default_case:
            self._push_env()
            result = None
            for stmt in node.default_case:
                result = self.visit(stmt)
                if self.current_env.should_return:
                    break
            self._pop_env()
            return result

        return None

    def _match_pattern(self, value: Any, pattern: ASTNode, bindings: Dict[str, Any]) -> bool:
        """Cocokkan nilai dengan pola (v6.0). Isi bindings kalau cocok."""
        if isinstance(pattern, DestructuringPatternNode):
            if pattern.is_array:
                if not isinstance(value, (list, tuple)) or len(value) != len(pattern.variables):
                    return False
                for var, item in zip(pattern.variables, value):
                    bindings[var] = item
                return True
            if not isinstance(value, dict):
                return False
            for var in pattern.variables:
                if var not in value:
                    return False
                bindings[var] = value[var]
            return True
        if isinstance(pattern, ObjectPatternNode):
            if not isinstance(value, dict):
                return False
            for key, entry in pattern.entries.items():
                if key not in value:
                    return False
                # Entri dari parser: ("var", nama) = binding, ("lit", v) = literal
                if isinstance(entry, tuple) and entry[0] == "var":
                    bindings[entry[1]] = value[key]
                elif isinstance(entry, tuple) and entry[0] == "lit":
                    if value[key] != entry[1]:
                        return False
                else:
                    bindings[entry] = value[key]
            return True
        if isinstance(pattern, BindingPatternNode):
            bindings[pattern.name] = value
            return True
        if isinstance(pattern, WildcardNode):
            return True
        # Literal / expression pattern (perilaku lama)
        pattern_val = self.visit(pattern)
        return value == pattern_val

    def visit_WildcardNode(self, node: WildcardNode) -> None:
        return None

    # ============= V3: Augmented Assignment =============

    def visit_AugmentedAssignmentNode(self, node: AugmentedAssignmentNode) -> Any:
        """Augmented assignment: x += 1, self.x += 1, data[i] //= 2, dll.

        v6.5: konstanta ditolak.
        v6.8: target atribut objek & index list didukung.
        """
        target = node.target
        obj = None
        index = None
        name = None

        # Baca nilai target saat ini
        if isinstance(target, IdentifierNode):
            name = target.name
            # v6.5: konstanta tidak bisa diubah lewat augmented assignment
            env = self.current_env
            while env is not None:
                if name in env.variables:
                    if name in env.constants:
                        raise RuntimeError_(
                            message=f"Konstanta '{name}' tidak bisa diubah.",
                            line=node.line,
                            column=node.column,
                            solution=f"Hapus assignment ke '{name}' atau ubah deklarasi menjadi 'buat {name} = ...'.",
                        )
                    break
                env = env.parent
            current = self.current_env.get_variable(name)
        elif isinstance(target, ObjectAccessNode):
            obj = self.visit(target.object)
            prop = target.property
            if isinstance(obj, BroLangInstance):
                current = obj.get(prop, caller_class=self._current_class_name)
            else:
                current = getattr(obj, prop)
        elif isinstance(target, IndexNode):
            obj = self.visit(target.target)
            index = self.visit(target.index)
            current = obj[index]
        else:
            raise RuntimeError_(
                message="Target augmented assignment harus berupa variabel, atribut, atau index.",
                line=node.line,
                column=node.column,
            )

        right = self.visit(node.value)
        op = node.operator
        if op == "+=":
            result = current + right
        elif op == "-=":
            result = current - right
        elif op == "*=":
            result = current * right
        elif op == "/=":
            if right == 0:
                raise ZeroDivisionError_(
                    message="Tidak bisa membagi dengan nol.",
                    line=node.line,
                    column=node.column,
                )
            result = current / right
        elif op == "//=":
            if right == 0:
                raise ZeroDivisionError_(
                    message="Tidak bisa membagi dengan nol.",
                    line=node.line,
                    column=node.column,
                )
            result = current // right
        elif op == "%=":
            if right == 0:
                raise ZeroDivisionError_(
                    message="Tidak bisa modulo dengan nol.",
                    line=node.line,
                    column=node.column,
                )
            result = current % right
        elif op == "**=":
            result = current**right
        else:
            raise RuntimeError_(
                message=f"Operator augmented assignment '{op}' tidak dikenal.",
                line=node.line,
                column=node.column,
            )

        # Simpan hasil
        if isinstance(target, IdentifierNode):
            self.current_env.set_variable(name, result)
        elif isinstance(target, ObjectAccessNode):
            if isinstance(obj, BroLangInstance):
                obj.set(target.property, result)
            else:
                setattr(obj, target.property, result)
        elif isinstance(target, IndexNode):
            obj[index] = result
        return result

    # ============= V3: Ternary Expression =============

    def visit_TernaryNode(self, node: TernaryNode) -> Any:
        """Ternary: nilai_a jika kondisi lainnya nilai_b"""
        condition = self.visit(node.condition)
        if condition:
            return self.visit(node.true_value)
        return self.visit(node.false_value)

    # ============= V3: Raise Statement =============

    def visit_RaiseNode(self, node: RaiseNode) -> None:
        """Raise: lempar nilai (v6.0: dukung instance kelas error kustom)."""
        value = self.visit(node.value)
        if isinstance(value, BroLangInstance):
            # Error kustom: lempar SaldoTidakCukup("pesan")
            klass_name = value.klass.name
            pesan = None
            # Pesan dari atribut `pesan`/`message` atau method _teks_
            try:
                pesan = value.attributes.get("pesan")
            except Exception:
                pesan = None
            if pesan is None:
                try:
                    pesan = value.attributes.get("message")
                except Exception:
                    pesan = None
            if pesan is None:
                try:
                    metode = self._get_overload_method(value, "_teks_")
                    if metode is not None:
                        pesan = metode(value)
                except Exception:
                    pesan = None
            msg = f"{klass_name}: {pesan}" if pesan is not None else klass_name
            err = RuntimeError_(message=msg, line=node.line, column=node.column)
            err.error_class = klass_name
            err.error_instance = value
            raise err
        raise RuntimeError_(
            message=str(value),
            line=node.line,
            column=node.column,
        )

    # ============= V3: Global/Nonlocal =============

    def visit_GlobalNode(self, node: GlobalNode) -> None:
        """Global statement: global nama_var"""
        pass  # Global is handled by set_variable walking up scopes

    def visit_NonlocalNode(self, node: NonlocalNode) -> None:
        """Nonlocal statement: nonlokal nama_var"""
        pass  # Nonlocal is handled by set_variable walking up scopes

    # ============= V3: List/Dict Methods =============

    def _get_list_methods(self, lst: list) -> dict:
        """Membuat method dictionary untuk list."""

        def tambah(item):
            lst.append(item)
            return None

        def sisipkan(index, item):
            lst.insert(index, item)
            return None

        def urutkan():
            lst.sort()
            return lst

        def balik():
            lst.reverse()
            return lst

        def hapus(item):
            try:
                lst.remove(item)
            except ValueError:
                raise RuntimeError_(
                    message=f"Elemen '{item}' tidak ditemukan dalam list.",
                )
            return None

        def pop(index=None):
            if index is None:
                return lst.pop()
            return lst.pop(index)

        def jumlah():
            return len(lst)

        def indeks(item):
            try:
                return lst.index(item)
            except ValueError:
                return -1

        def hitung(item):
            return lst.count(item)

        def perpanjang(other):
            lst.extend(other)
            return None

        def salin():
            return lst[:]

        def kosongkan():
            lst.clear()
            return None

        return {
            "tambah": tambah,
            "sisipkan": sisipkan,
            "urutkan": urutkan,
            "balik": balik,
            "hapus": hapus,
            "pop": pop,
            "jumlah": jumlah,
            "indeks": indeks,
            "hitung": hitung,
            "perpanjang": perpanjang,
            "salin": salin,
            "kosongkan": kosongkan,
        }

    def _get_dict_methods(self, d: dict) -> dict:
        """Membuat method dictionary untuk dict."""

        def kunci():
            return list(d.keys())

        def nilai():
            return list(d.values())

        def item():
            return list(d.items())

        def ambil(key, default=None):
            return d.get(key, default)

        def hapus_kunci(key):
            try:
                del d[key]
            except KeyError:
                raise RuntimeError_(
                    message=f"Kunci '{key}' tidak ditemukan dalam objek.",
                )
            return None

        def pop(key, default=None):
            return d.pop(key, default)

        def jumlah():
            return len(d)

        def punya(key):
            return key in d

        def perbarui(other):
            d.update(other)
            return None

        def kosongkan():
            d.clear()
            return None

        def salin():
            return d.copy()

        return {
            "kunci": kunci,
            "nilai": nilai,
            "item": item,
            "ambil": ambil,
            "hapus_kunci": hapus_kunci,
            "pop": pop,
            "jumlah": jumlah,
            "punya": punya,
            "perbarui": perbarui,
            "kosongkan": kosongkan,
            "salin": salin,
        }

    def _get_string_methods(self, s: str) -> dict:
        """Membuat method dictionary untuk string."""
        return {
            "atas": lambda: s.upper(),
            "bawah": lambda: s.lower(),
            "kapital": lambda: s.capitalize(),
            "judul": lambda: s.title(),
            "potong": lambda *a: s.split(*a),
            "ganti": lambda old, new: s.replace(old, new),
            "cari": lambda sub: s.find(sub),
            "mulai": lambda prefix: s.startswith(prefix),
            "berakhir": lambda suffix: s.endswith(suffix),
            "strip": lambda: s.strip(),
            "panjang": lambda: len(s),
            # v4.0 string methods
            "cocok": lambda pattern: bool(__import__("re").search(pattern, s)),
            "cocok_semua": lambda pattern: __import__("re").findall(pattern, s),
            "ganti_regexp": lambda pattern, replacement: __import__("re").sub(
                pattern, replacement, s
            ),
            "bagi_regexp": lambda pattern: __import__("re").split(pattern, s),
            "encode": lambda enc="utf-8": s.encode(enc),
            "isalnum": lambda: s.isalnum(),
            "isalpha": lambda: s.isalpha(),
            "isdigit": lambda: s.isdigit(),
            "islower": lambda: s.islower(),
            "isupper": lambda: s.isupper(),
            "isspace": lambda: s.isspace(),
            "join": lambda iterable: s.join(str(i) for i in iterable),
            "zfill": lambda width: s.zfill(width),
            "center": lambda width: s.center(width),
            "ljust": lambda width: s.ljust(width),
            "rjust": lambda width: s.rjust(width),
            "count_sub": lambda sub: s.count(sub),
            "startswith_any": lambda prefixes: any(s.startswith(p) for p in prefixes),
            "endswith_any": lambda suffixes: any(s.endswith(suf) for suf in suffixes),
        }

    # ============= V4: Async/Await =============

    def visit_AsyncFunctionDefNode(self, node: AsyncFunctionDefNode) -> None:
        """Async function declaration — in sync interpreter, just treat as regular function."""
        # In a sync interpreter, async functions are treated as regular functions
        # The 'tunggu' (await) just calls the function directly
        closure_env = self.current_env

        def async_function(*args, **kwargs):
            old_env = self.current_env
            self._push_env()
            self.current_env.parent = closure_env

            for param, val in self._bind_params(
                node.params, node.defaults, args, kwargs, node, node.rest_param
            ):
                self.current_env.define_variable(param, val)

            try:
                result = None
                for stmt in node.body:
                    result = self.visit(stmt)
                    if self.current_env.should_return:
                        result = self.current_env.return_value
                        break
                self._pop_env()
                self.current_env = old_env
                return result
            except ReturnException as e:
                self._pop_env()
                self.current_env = old_env
                return e.value
            except Exception as e:
                self._pop_env()
                self.current_env = old_env
                raise e

        async_function._brolang_fn = True
        self.current_env.functions[node.name] = async_function

    def visit_AwaitNode(self, node: AwaitNode) -> Any:
        """Await expression — in sync interpreter, just evaluate the expression."""
        return self.visit(node.value)

    # ============= V4: Generators =============

    def visit_YieldNode(self, node: YieldNode) -> Any:
        """Yield statement — suspend generator dan return value."""
        value = self.visit(node.value) if node.value else None
        raise YieldException(value)

    def visit_YieldFromNode(self, node: YieldFromNode) -> Any:
        """Yield from — hasilkan SEMUA item dari iterable (v6.9 fix).

        Sebelumnya `for item in items: raise YieldException(item)` hanya
        menghasilkan item PERTAMA — raise pertama menghentikan loop, jadi
        elemen sisanya tidak pernah terlempar. Kini semua item ditambahkan
        langsung ke koleksi generator aktif, dan eksekusi blok sekitar
        tetap berlanjut (konsisten dengan `yield from` Python).
        """
        iterable = self.visit(node.value)
        # Konversi ke list dulu supaya bisa di-iterate tanpa masalah
        items = list(iterable) if not isinstance(iterable, list) else iterable
        gen = getattr(self, "_active_generator", None)
        if gen is not None and hasattr(gen, "_values"):
            gen._values.extend(items)
            return None
        # Fallback: hasilkandari di luar konteks generator (sumber tidak valid)
        for item in items:
            raise YieldException(item)
        return None

    # ============= V4: Decorators =============

    def visit_DecoratorNode(self, node: DecoratorNode) -> Any:
        """Decorator application."""
        decorator_func = self.visit(node.decorator_expr)
        target = self.visit(node.target)
        if callable(decorator_func):
            return decorator_func(target)
        return target

    def visit_DecoratedFunctionNode(self, node: DecoratedFunctionNode) -> None:
        """Decorated function — apply decorators then define."""
        # First define the function
        closure_env = self.current_env

        def bro_function(*args, **kwargs):
            old_env = self.current_env
            self._push_env()
            self.current_env.parent = closure_env

            for param, val in self._bind_params(
                node.params, node.defaults, args, kwargs, node, node.rest_param
            ):
                self.current_env.define_variable(param, val)

            try:
                result = None
                for stmt in node.body:
                    result = self.visit(stmt)
                    if self.current_env.should_return:
                        result = self.current_env.return_value
                        break
                self._pop_env()
                self.current_env = old_env
                return result
            except ReturnException as e:
                self._pop_env()
                self.current_env = old_env
                return e.value
            except Exception as e:
                self._pop_env()
                self.current_env = old_env
                raise e

        # Apply decorators in reverse order (bottom to top)
        func = bro_function
        for decorator_expr in reversed(node.decorators):
            decorator = self.visit(decorator_expr)
            if callable(decorator):
                func = decorator(func)

        self.current_env.functions[node.name] = func

    def visit_DecoratedClassNode(self, node: DecoratedClassNode) -> None:
        """Decorated class — apply decorators then define."""
        methods = {}
        for stmt in node.body:
            if isinstance(stmt, FunctionNode):
                method_func = self._create_method(stmt)
                methods[stmt.name] = method_func
            elif isinstance(stmt, MethodNode):
                method_func = self._create_method(stmt)
                methods[stmt.name] = method_func

        parent_class = None
        if node.parent:
            if node.parent in self.current_env.classes:
                parent_class = self.current_env.classes[node.parent]

        klass = BroLangClass(node.name, methods, parent_class)

        def class_constructor(*args, **kwargs):
            instance = BroLangInstance(klass)
            init_method = klass.get_method("__init__")
            if init_method:
                init_method(instance, *args, **kwargs)
            return instance

        # Apply decorators
        cls = class_constructor
        for decorator_expr in reversed(node.decorators):
            decorator = self.visit(decorator_expr)
            if callable(decorator):
                cls = decorator(cls)

        self.current_env.variables[node.name] = cls
        self.current_env.classes[node.name] = klass

    # ============= V4: Walrus Operator =============

    def visit_WalrusNode(self, node: WalrusNode) -> Any:
        """Walrus operator: x := expr — assign and return value."""
        value = self.visit(node.value)
        self.current_env.define_variable(node.name, value)
        return value

    # ============= V4: Context Manager =============

    def visit_WithNode(self, node: WithNode) -> None:
        """With statement: dengan expr sebagai name ... selesai"""
        context = self.visit(node.context_expr)

        # Try to call __enter__
        enter_result = None
        if hasattr(context, "__enter__"):
            enter_result = context.__enter__()
        elif hasattr(context, "masuk"):
            enter_result = context.masuk()

        self._push_env()
        if node.as_name:
            self.current_env.define_variable(node.as_name, enter_result or context)

        try:
            for stmt in node.body:
                self.visit(stmt)
        finally:
            self._pop_env()
            # Try to call __exit__
            if hasattr(context, "__exit__"):
                context.__exit__(None, None, None)
            elif hasattr(context, "keluar"):
                context.keluar()

    # ============= V4: Multi-Except =============

    def visit_MultiExceptNode(self, node: MultiExceptNode) -> Optional[Any]:
        """Try-catch with multiple except clauses."""
        result = None
        try:
            self._push_env()
            for stmt in node.body:
                result = self.visit(stmt)
            self._pop_env()
        except Exception as e:
            self._pop_env()
            matched = False
            for clause in node.except_clauses:
                if clause.exception_type is None:
                    # Bare except
                    self._push_env()
                    self.current_env.define_variable(clause.variable, e)
                    for stmt in clause.body:
                        result = self.visit(stmt)
                    self._pop_env()
                    matched = True
                    break
                else:
                    # Typed except
                    exc_type_name = clause.exception_type
                    exc_type_map = {
                        "RuntimeError": RuntimeError_,
                        "TypeError": TypeError_,
                        "NameError": NameError_,
                        "ZeroDivisionError": ZeroDivisionError_,
                        "IndexError": IndexError_,
                        "ValueError": ValueError,
                        "KeyError": KeyError,
                        "AttributeError": AttributeError,
                    }
                    exc_class = exc_type_map.get(exc_type_name)
                    # V6.0: error kustom (kelas_error) — cocokkan nama kelas
                    # beserta hierarki induknya (kecuali Induk menangkap semua turunan)
                    inst = getattr(e, "error_instance", None)
                    if inst is not None and isinstance(inst, BroLangInstance):
                        k = inst.klass
                        while k is not None:
                            if k.name == exc_type_name:
                                self._push_env()
                                self.current_env.define_variable(clause.variable, inst)
                                for stmt in clause.body:
                                    result = self.visit(stmt)
                                self._pop_env()
                                matched = True
                                break
                            k = k.parent
                        if matched:
                            break
                    if exc_class and isinstance(e, exc_class):
                        self._push_env()
                        self.current_env.define_variable(clause.variable, e)
                        for stmt in clause.body:
                            result = self.visit(stmt)
                        self._pop_env()
                        matched = True
                        break
                    elif exc_type_name == "semua":
                        # Catch-all: binding instance error kustom (kalau ada)
                        val = getattr(e, "error_instance", None) or e
                        self._push_env()
                        self.current_env.define_variable(clause.variable, val)
                        for stmt in clause.body:
                            result = self.visit(stmt)
                        self._pop_env()
                        matched = True
                        break

            if not matched:
                raise e

        # Execute else if no exception
        if node.else_body and not matched:
            self._push_env()
            for stmt in node.else_body:
                result = self.visit(stmt)
            self._pop_env()

        # Execute finally
        if node.finally_body:
            self._push_env()
            for stmt in node.finally_body:
                self.visit(stmt)
            self._pop_env()

        return result

    def visit_TypedExceptNode(self, node: TypedExceptNode) -> None:
        """Typed except clause — handled by MultiExceptNode."""
        pass

    # ============= V4: Star Import =============

    def visit_StarImportNode(self, node: StarImportNode) -> None:
        """Star import: dari module impor *"""
        try:
            module = get_stdlib_module(node.module)
            # Import all public attributes
            for attr in dir(module):
                if not attr.startswith("_"):
                    self.current_env.variables[attr] = getattr(module, attr)
        except ImportError:
            try:
                import importlib

                py_module = importlib.import_module(node.module)
                for attr in dir(py_module):
                    if not attr.startswith("_"):
                        self.current_env.variables[attr] = getattr(py_module, attr)
            except ImportError:
                raise RuntimeError_(
                    message=f"Module '{node.module}' tidak ditemukan.",
                    line=node.line,
                    column=node.column,
                )

    # ============= V4: Chained Call =============

    def visit_ChainedCallNode(self, node: ChainedCallNode) -> Any:
        """Chained method call: obj.method1().method2()"""
        result = None
        for call in node.calls:
            result = self.visit(call)
        return result

    # ============= V4: Switch =============

    def visit_SwitchNode(self, node: SwitchNode) -> Any:
        """Switch statement (enhanced match with guards)."""
        value = self.visit(node.value)
        for pattern, body, guard in node.cases:
            if isinstance(pattern, WildcardNode):
                if guard:
                    guard_val = self.visit(guard)
                    if not guard_val:
                        continue
                self._push_env()
                result = None
                for stmt in body:
                    result = self.visit(stmt)
                    if self.current_env.should_return:
                        break
                self._pop_env()
                return result
            pattern_val = self.visit(pattern)
            if value == pattern_val:
                if guard:
                    guard_val = self.visit(guard)
                    if not guard_val:
                        continue
                self._push_env()
                result = None
                for stmt in body:
                    result = self.visit(stmt)
                    if self.current_env.should_return:
                        break
                self._pop_env()
                return result

        if node.default_case:
            self._push_env()
            result = None
            for stmt in node.default_case:
                result = self.visit(stmt)
                if self.current_env.should_return:
                    break
            self._pop_env()
            return result

        return None

    # ============= V4: Generator Function =============

    def visit_GeneratorFunctionNode(self, node: GeneratorFunctionNode) -> None:
        """Generator function declaration — returns BroLangGenerator."""
        closure_env = self.current_env

        def generator_func(*args):
            return BroLangGenerator(
                body=node.body,
                params=node.params,
                args=args,
                defaults=node.defaults,
                closure_env=closure_env,
                interpreter=self,
            )

        self.current_env.functions[node.name] = generator_func

    # ============= V5.0: Type System =============

    def visit_TypeAnnotationNode(self, node: TypeAnnotationNode) -> Any:
        """Type annotation - stores type info for later use."""
        # Type annotations are mostly for documentation in an interpreter
        # We just return the type name as a string
        return node.type_name

    def visit_TypeAliasNode(self, node: TypeAliasNode) -> None:
        """Type alias: tipe NamaTipe = definisi (v6.0: resolve nama tipe)."""
        if isinstance(node.definition, IdentifierNode):
            # tipe ID = Angka -> simpan nama tipe (resolve nanti saat cek)
            self.current_env.variables[node.name] = node.definition.name
        elif isinstance(node.definition, (GenericTypeNode, UnionTypeNode, TypeAnnotationNode)):
            self.current_env.variables[node.name] = self.visit(node.definition)
        else:
            self.current_env.variables[node.name] = self.visit(node.definition)

    def visit_UnionTypeNode(self, node: UnionTypeNode) -> str:
        """Union type: tipe1 | tipe2"""
        return " | ".join(node.types)

    def visit_GenericTypeNode(self, node: GenericTypeNode) -> str:
        """Generic type: List<angka>"""
        return f"{node.base_type}<{', '.join(node.type_args)}>"

    def visit_FunctionTypeNode(self, node: FunctionTypeNode) -> str:
        """Function type: (angka, teks) -> benar"""
        return f"({', '.join(node.param_types)}) -> {node.return_type}"

    # ============= V5.0: Interfaces =============

    def visit_InterfaceNode(self, node: InterfaceNode) -> None:
        """Interface declaration - stores interface definition."""
        method_names = []
        for m in node.methods:
            if isinstance(m, MethodSignatureNode):
                method_names.append(m.name)
            elif hasattr(m, "name"):
                method_names.append(m.name)

        interface = {
            "name": node.name,
            "methods": method_names,
            "raw_methods": node.methods,
            "parent_interfaces": node.parent_interfaces,
        }
        self.current_env.interfaces[node.name] = interface

    def visit_MethodSignatureNode(self, node: MethodSignatureNode) -> Any:
        """Method signature - returns signature info."""
        return {
            "name": node.name,
            "params": [(p.name, p.type_name) for p in node.params],
            "return_type": node.return_type,
        }

    def visit_ImplementsNode(self, node: ImplementsNode) -> None:
        """Implements statement - records interface requirement."""
        if node.class_name in self.current_env.classes:
            klass = self.current_env.classes[node.class_name]
            klass.required_interfaces = node.interfaces

    def visit_AbstractClassNode(self, node: AbstractClassNode) -> None:
        """Abstract class declaration."""
        methods = {}
        method_access = {}
        for stmt in node.body:
            if isinstance(stmt, AccessModifierNode):
                modifier = stmt.modifier
                target = stmt.target
                if isinstance(target, FunctionNode):
                    method_func = self._create_method(target)
                    methods[target.name] = method_func
                    method_access[target.name] = modifier
            elif isinstance(stmt, FunctionNode):
                method_func = self._create_method(stmt)
                methods[stmt.name] = method_func
                method_access[stmt.name] = "publik"

        parent_class = None
        if node.parent:
            if node.parent in self.current_env.classes:
                parent_class = self.current_env.classes[node.parent]

        klass = BroLangClass(
            node.name,
            methods,
            parent_class,
            is_abstract=True,
            abstract_methods=node.abstract_methods,
            method_access=method_access,
        )

        def class_constructor(*args):
            raise RuntimeError_(
                message=f"Tidak bisa membuat instance dari kelas abstrak '{node.name}'.",
                line=node.line,
                column=node.column,
                solution=f"Buat kelas turunan yang mengimplementasi semua method abstrak dari '{node.name}'.",
            )

        self.current_env.variables[node.name] = class_constructor
        self.current_env.classes[node.name] = klass

    def visit_AbstractMethodNode(self, node: AbstractMethodNode) -> None:
        """Abstract method - no-op, handled by AbstractClassNode."""
        pass

    # ============= V5.0: Higher-Order Functions =============

    def visit_MapNode(self, node: MapNode) -> list:
        """Map: peta(iterable, fungsi)"""
        iterable = self.visit(node.iterable)
        func = self.visit(node.function)

        if not callable(func):
            raise RuntimeError_(
                message="Parameter kedua 'peta' harus berupa fungsi.",
                line=node.line,
                column=node.column,
            )

        return [func(item) for item in iterable]

    def visit_FilterNode(self, node: FilterNode) -> list:
        """Filter: saring(iterable, kondisi)"""
        iterable = self.visit(node.iterable)
        func = self.visit(node.condition)

        if not callable(func):
            raise RuntimeError_(
                message="Parameter kedua 'saring' harus berupa fungsi/predicate.",
                line=node.line,
                column=node.column,
            )

        return [item for item in iterable if func(item)]

    def visit_ReduceNode(self, node: ReduceNode) -> Any:
        """Reduce: kurangi(iterable, fungsi, awal?)"""
        iterable = self.visit(node.iterable)
        func = self.visit(node.function)

        if not callable(func):
            raise RuntimeError_(
                message="Parameter kedua 'kurangi' harus berupa fungsi.",
                line=node.line,
                column=node.column,
            )

        if node.initial is not None:
            initial = self.visit(node.initial)
            result = initial
            for item in iterable:
                result = func(result, item)
        else:
            result = next(iter(iterable))
            for item in iterable:
                result = func(result, item)

        return result

    # ============= V5.0: Result/Option Types =============

    def visit_ResultNode(self, node: ResultNode) -> dict:
        """Result type: Benar(value) atau Salah(error)"""
        value = self.visit(node.value)
        return {"type": "Result", "is_success": node.is_success, "value": value}

    def visit_OptionNode(self, node: OptionNode) -> dict:
        """Option type: Ada(value) atau Kosong()"""
        if node.has_value and node.value:
            value = self.visit(node.value)
            return {"type": "Option", "has_value": True, "value": value}
        return {"type": "Option", "has_value": False, "value": None}

    # ============= V5.0: Macros =============

    def visit_MacroDefNode(self, node: MacroDefNode) -> None:
        """Macro definition - stores macro for later expansion and also as callable."""
        macro = {
            "type": "macro",
            "params": node.params,
            "body": node.body,
        }
        self.current_env.variables[node.name] = macro

        # Also register as a callable function for direct invocation
        closure_env = self.current_env

        def macro_func(*args):
            old_env = self.current_env
            self._push_env()
            self.current_env.parent = closure_env

            for i, param in enumerate(node.params):
                if i < len(args):
                    self.current_env.define_variable(param, args[i])
                else:
                    self.current_env.define_variable(param, None)

            result = None
            try:
                for stmt in node.body:
                    result = self.visit(stmt)
                    if self.current_env.should_return:
                        break
            except ReturnException as e:
                result = e.value
            self._pop_env()
            self.current_env = old_env
            return result

        self.current_env.functions[node.name] = macro_func

    def visit_MacroCallNode(self, node: MacroCallNode) -> Any:
        """Macro call - expands and executes macro."""
        macro = self.current_env.get_variable(node.name)
        if not macro or macro.get("type") != "macro":
            raise RuntimeError_(
                message=f"'{node.name}' bukan sebuah macro.",
                line=node.line,
                column=node.column,
            )

        # Evaluate arguments
        args = [self.visit(arg) for arg in node.args]

        # Create new environment for macro expansion
        self._push_env()
        for i, param in enumerate(macro["params"]):
            if i < len(args):
                self.current_env.define_variable(param, args[i])

        # Execute macro body
        result = None
        for stmt in macro["body"]:
            result = self.visit(stmt)

        self._pop_env()
        return result

    # ============= V5.0: Module System =============

    def visit_NamespaceNode(self, node: NamespaceNode) -> None:
        """Namespace: ruang nama NamaModule { ... }"""
        self._push_env()
        for stmt in node.body:
            self.visit(stmt)
        # Store namespace as a module-like object
        namespace_vars = dict(self.current_env.variables)
        namespace_funcs = dict(self.current_env.functions)
        self._pop_env()

        # Create a SimpleNamespace-like object that supports attribute access
        from types import SimpleNamespace

        ns = SimpleNamespace(**namespace_vars)
        # Also add functions as attributes
        for fname, ffunc in namespace_funcs.items():
            setattr(ns, fname, ffunc)
        self.current_env.variables[node.name] = ns

    def visit_UseNode(self, node: UseNode) -> None:
        """Use statement: pakai NamaModule"""
        # Try to get from stdlib first
        try:
            module = get_stdlib_module(node.module)
            alias = node.alias or node.module
            self.current_env.variables[alias] = module
        except ImportError:
            # Try to get from current environment (namespace)
            if node.module in self.current_env.variables:
                alias = node.alias or node.module
                self.current_env.variables[alias] = self.current_env.variables[node.module]
            else:
                raise RuntimeError_(
                    message=f"Module '{node.module}' tidak ditemukan.",
                    line=node.line,
                    column=node.column,
                )

    # ============= V5.0: Access Modifiers =============

    def visit_AccessModifierNode(self, node: AccessModifierNode) -> Any:
        """Access modifier: publik/privat/terlindungi.

        Di dalam class body, ini ditangani oleh visit_ClassNode.
        Di luar class, langsung eksekusi target-nya.
        """
        return self.visit(node.target)

    # ============= V5.0: Null Coalescing =============

    def visit_NullCoalescingNode(self, node: NullCoalescingNode) -> Any:
        """Null coalescing: x ?? default"""
        left = self.visit(node.left)
        if left is None:
            return self.visit(node.right)
        return left

    # ============= V5.0: Optional Chaining =============

    def visit_OptionalChainingNode(self, node: OptionalChainingNode) -> Any:
        """Optional chaining: obj?.attr"""
        obj = self.visit(node.object)
        if obj is None:
            return None

        if isinstance(obj, BroLangInstance):
            try:
                return obj.get(node.property)
            except:
                return None

        if isinstance(obj, dict):
            return obj.get(node.property)

        if hasattr(obj, node.property):
            return getattr(obj, node.property)

        return None

    # ============= V5.0: For Each with Index =============

    def visit_ForEachNode(self, node: ForEachNode) -> None:
        """For-each with index: untuk setiap (item, index) dalam iterable"""
        iterable = self.visit(node.iterable)

        for index, item in enumerate(iterable):
            self._push_env()
            self.current_env.define_variable(node.variable, item)
            if node.index_variable:
                self.current_env.define_variable(node.index_variable, index)

            try:
                for stmt in node.body:
                    self.visit(stmt)
                    if self.current_env.should_return:
                        self._pop_env()
                        return
                self._pop_env()
            except BreakException:
                self._pop_env()
                break
            except ContinueException:
                self._pop_env()
                continue

    # ============= V5.0: Chained Comparisons =============

    def visit_ChainedComparisonNode(self, node: ChainedComparisonNode) -> bool:
        """Chained comparison: 0 < x < 10"""
        left = self.visit(node.left)

        for i, (op, comparator) in enumerate(zip(node.operators, node.comparators)):
            right = self.visit(comparator)

            if op == "<":
                result = left < right
            elif op == ">":
                result = left > right
            elif op == "<=":
                result = left <= right
            elif op == ">=":
                result = left >= right
            else:
                raise RuntimeError_(
                    message=f"Operator '{op}' tidak didukung dalam chained comparison.",
                    line=node.line,
                    column=node.column,
                )

            if not result:
                return False
            left = right

        return True

    # ============= V5.0: Destructuring Pattern =============

    def visit_DestructuringPatternNode(self, node: DestructuringPatternNode) -> Any:
        """Destructuring pattern - returns the variables to bind."""
        return node.variables

    def visit_GuardPatternNode(self, node: GuardPatternNode) -> Any:
        """Guard pattern - evaluates guard condition."""
        self.current_env.define_variable(node.variable, None)
        # The actual matching is handled by the match expression
        return None

    # ============= V5.2: Pipeline Operator =============

    def visit_PipelineNode(self, node: PipelineNode) -> Any:
        """Pipeline operator: nilai | > fungsi atau nilai | > lalu(x) x * 2

        Semantik:
          - nilai | > f            => f(nilai)
          - nilai | > lalu(x) x*2  => (lalu(x) x*2)(nilai)
          - nilai | > f(args)      => f(nilai, args...)
          - nilai | > peta(f)      => peta(nilai, f)
        """
        left = self.visit(node.left)
        right = node.right

        # Higher-order functions dengan iterable dari pipeline
        if isinstance(right, MapNode):
            func = self.visit(right.function)
            return [func(x) for x in left]
        if isinstance(right, FilterNode):
            cond = self.visit(right.condition)
            return [x for x in left if cond(x)]
        if isinstance(right, ReduceNode):
            func = self.visit(right.function)
            initial = self.visit(right.initial) if right.initial else None
            if initial is not None:
                result = initial
                for x in left:
                    result = func(result, x)
                return result
            items = list(left)
            if not items:
                return None
            result = items[0]
            for x in items[1:]:
                result = func(result, x)
            return result

        # Jika sisi kanan adalah CallNode, sisipkan nilai kiri sebagai argumen pertama
        if isinstance(right, CallNode):
            args = [self.visit(a) for a in right.args]
            kwargs = {name: self.visit(v) for name, v in right.kwargs}
            func = self.visit(right.function)
            if callable(func):
                return func(left, *args, **kwargs)
            raise RuntimeError_(
                message=f"'{right.function}' bukan fungsi yang bisa dipanggil.",
                line=node.line,
                column=node.column,
            )

        # Jika sisi kanan adalah lambda atau identifier, panggil dengan nilai kiri
        func = self.visit(right)
        if callable(func):
            return func(left)

        raise RuntimeError_(
            message=f"Sisi kanan pipeline harus berupa fungsi, tapi mendapatkan {type(right).__name__}.",
            line=node.line,
            column=node.column,
            solution="Gunakan: nilai |> fungsi atau nilai |> lalu(x) ekspresi",
        )

    # ============= V5.2: Destructuring Assignment =============

    def visit_DestructuringAssignmentNode(self, node: DestructuringAssignmentNode) -> Any:
        """Destructuring assignment: buat [a, b] = list / buat {x, y} = objek"""
        value = self.visit(node.value)

        if node.is_array:
            if not isinstance(value, (list, tuple)):
                raise TypeError_(
                    message=f"Destructuring list membutuhkan list/tuple, tapi mendapatkan {type(value).__name__}.",
                    line=node.line,
                    column=node.column,
                    solution="Gunakan: buat [a, b] = [1, 2]",
                )
            if len(value) < len(node.targets):
                raise RuntimeError_(
                    message=f"Tidak cukup elemen untuk destructuring: butuh {len(node.targets)}, ada {len(value)}.",
                    line=node.line,
                    column=node.column,
                )
            for i, name in enumerate(node.targets):
                self.current_env.define_variable(name, value[i])
        else:
            if not isinstance(value, dict):
                raise TypeError_(
                    message=f"Destructuring objek membutuhkan objek/dict, tapi mendapatkan {type(value).__name__}.",
                    line=node.line,
                    column=node.column,
                    solution='Gunakan: buat {x, y} = {"x": 1, "y": 2}',
                )
            for name in node.targets:
                if name in value:
                    self.current_env.define_variable(name, value[name])
                else:
                    self.current_env.define_variable(name, None)

        return value
