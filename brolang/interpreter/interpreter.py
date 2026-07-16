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

from typing import Any, Dict, List, Optional, Callable
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
from brolang.exceptions import (
    RuntimeError_, TypeError_, NameError_,
    ZeroDivisionError_, IndexError_,
)
from brolang.stdlib import get_stdlib_module
from brolang.interpreter.builtins import BUILTINS


@dataclass
class Environment:
    """Lingkungan eksekusi dengan scoping.

    Menyimpan variabel, fungsi, dan kelas dalam scope saat ini.
    """

    parent: Optional["Environment"] = None
    variables: Dict[str, Any] = field(default_factory=dict)
    functions: Dict[str, Callable] = field(default_factory=dict)
    classes: Dict[str, "BroLangClass"] = field(default_factory=dict)
    modules: Dict[str, Any] = field(default_factory=dict)
    return_value: Any = None
    should_return: bool = False
    should_break: bool = False
    should_continue: bool = False

    def define_variable(self, name: str, value: Any) -> None:
        self.variables[name] = value

    def get_variable(self, name: str) -> Any:
        if name in self.variables:
            return self.variables[name]
        if self.parent is not None:
            return self.parent.get_variable(name)
        raise NameError_(message=f"Variabel '{name}' tidak ditemukan.", line=0, column=0,
                         solution=f"Pastikan '{name}' sudah dideklarasikan dengan 'buat'.")

    def set_variable(self, name: str, value: Any) -> None:
        if name in self.variables:
            self.variables[name] = value
            return
        if self.parent is not None:
            self.parent.set_variable(name, value)
            return
        raise NameError_(message=f"Variabel '{name}' tidak ditemukan.", line=0, column=0,
                         solution=f"Pastikan '{name}' sudah dideklarasikan.")

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


class BroLangClass:
    """Representasi kelas dalam BroLang runtime."""

    def __init__(self, name: str, methods: Dict[str, Callable], parent: Optional["BroLangClass"] = None):
        self.name = name
        self.methods = methods
        self.parent = parent

    def get_method(self, name: str) -> Optional[Callable]:
        if name in self.methods:
            return self.methods[name]
        if self.parent is not None:
            return self.parent.get_method(name)
        return None


class BroLangInstance:
    """Instance dari sebuah kelas BroLang."""

    def __init__(self, klass: BroLangClass):
        self.klass = klass
        self.attributes: Dict[str, Any] = {}

    def get(self, name: str) -> Any:
        if name in self.attributes:
            return self.attributes[name]
        method = self.klass.get_method(name)
        if method is not None:
            return method
        raise RuntimeError_(
            message=f"'{self.klass.name}' tidak memiliki atribut '{name}'.",
            line=0, column=0,
            solution=f"Periksa apakah '{name}' sudah didefinisikan di kelas {self.klass.name}.",
        )

    def set(self, name: str, value: Any) -> None:
        self.attributes[name] = value


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

        # Register built-in functions
        for name, func in BUILTINS.items():
            self.global_env.functions[name] = func

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
                line=getattr(e, 'line', 0),
                column=getattr(e, 'column', 0),
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

        # Check variables first (user variables shadow builtins)
        if self.current_env.has_variable(name):
            return self.current_env.get_variable(name)

        # Check built-in functions
        if name in self.current_env.functions:
            return self.current_env.functions[name]

        raise NameError_(
            message=f"Variabel '{name}' tidak ditemukan.",
            line=node.line,
            column=node.column,
            solution=f"Deklarasikan '{name}' dengan 'buat {name} = nilai' terlebih dahulu.",
        )

    def visit_VariableNode(self, node: VariableNode) -> Any:
        return self.current_env.get_variable(node.name)

    def visit_AssignmentNode(self, node: AssignmentNode) -> Any:
        """Assignment: buat x = value atau x = value."""
        value = self.visit(node.value) if node.value else None

        if isinstance(node.target, IdentifierNode):
            name = node.target.name
            if node.is_declaration:
                self.current_env.define_variable(name, value)
            else:
                self.current_env.set_variable(name, value)
            return value
        elif isinstance(node.target, IndexNode):
            # Array assignment: list[index] = value
            target = self.visit(node.target.target)
            index = self.visit(node.target.index)
            if isinstance(target, list):
                target[index] = value
            else:
                raise TypeError_(
                    message="Hanya list yang bisa di-index assignment.",
                    line=node.line, column=node.column,
                )
            return value
        elif isinstance(node.target, ObjectAccessNode):
            # Object attribute assignment: obj.attr = value
            obj = self.visit(node.target.object)
            if isinstance(obj, BroLangInstance):
                obj.set(node.target.property, value)
                return value
            raise RuntimeError_(
                message=f"Objek tidak memiliki atribut '{node.target.property}'.",
                line=node.line, column=node.column,
            )

        return value

    def visit_BinaryOpNode(self, node: BinaryOpNode) -> Any:
        """Operasi biner dengan type checking runtime."""
        left = self.visit(node.left)
        right = self.visit(node.right)
        op = node.operator

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
                    line=node.line, column=node.column,
                    solution="Pastikan pembagi tidak bernilai 0.",
                )
            return left / right
        elif op == "%":
            if right == 0:
                raise ZeroDivisionError_(
                    message="Tidak bisa modulo dengan nol.",
                    line=node.line, column=node.column,
                )
            return left % right
        elif op == "**":
            return left ** right

        raise RuntimeError_(
            message=f"Operator '{op}' tidak dikenal.",
            line=node.line, column=node.column,
        )

    def visit_UnaryOpNode(self, node: UnaryOpNode) -> Any:
        """Operasi unary."""
        operand = self.visit(node.operand)

        if node.operator == "-":
            return -operand
        elif node.operator == "+":
            return +operand
        elif node.operator == "bukan":
            return not operand

        raise RuntimeError_(
            message=f"Operator unary '{node.operator}' tidak dikenal.",
            line=node.line, column=node.column,
        )

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
        """While loop execution."""
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
                break
            except ContinueException:
                self._pop_env()
                continue

    def visit_ForNode(self, node: ForNode) -> None:
        """For loop execution."""
        iterable = self.visit(node.iterable)

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
                break
            except ContinueException:
                self._pop_env()
                continue

    def visit_BreakNode(self, node: BreakNode) -> None:
        """Break statement."""
        raise BreakException()

    def visit_ContinueNode(self, node: ContinueNode) -> None:
        """Continue statement."""
        raise ContinueException()

    def visit_FunctionNode(self, node: FunctionNode) -> None:
        """Deklarasi fungsi."""
        def bro_function(*args):
            old_env = self.current_env
            self._push_env()

            # Bind parameters
            for i, param in enumerate(node.params):
                if i < len(args):
                    self.current_env.define_variable(param, args[i])
                else:
                    self.current_env.define_variable(param, None)

            # Execute body
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

        self.current_env.functions[node.name] = bro_function

    def visit_ReturnNode(self, node: ReturnNode) -> None:
        """Return statement."""
        value = self.visit(node.value) if node.value else None
        self.current_env.should_return = True
        self.current_env.return_value = value
        raise ReturnException(value)

    def visit_CallNode(self, node: CallNode) -> Any:
        """Function/method call."""
        args = [self.visit(arg) for arg in node.args]

        # Method call
        if node.is_method and node.object_name:
            # This is a method call; function is an ObjectAccessNode
            if isinstance(node.function, ObjectAccessNode):
                obj = self.visit(node.function.object)
                method_name = node.function.property
                if isinstance(obj, BroLangInstance):
                    method = obj.klass.get_method(method_name)
                    if method is None:
                        raise RuntimeError_(
                            message=f"Kelas '{obj.klass.name}' tidak memiliki method '{method_name}'.",
                        )
                    # Bind self
                    return method(obj, *args)
                # Stdlib module method
                if hasattr(obj, method_name):
                    bound_method = getattr(obj, method_name)
                    if callable(bound_method):
                        return bound_method(*args)
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
                    return func(*args)
                if env.has_variable(func_name):
                    func = env.get_variable(func_name)
                    if callable(func):
                        return func(*args)
                env = env.parent

            raise NameError_(
                message=f"Fungsi '{func_name}' tidak ditemukan.",
                line=node.line, column=node.column,
                solution=f"Definisikan fungsi '{func_name}' dengan 'fungsi {func_name}(...)'.",
            )

        # Call on expression result
        func = self.visit(node.function)
        if callable(func):
            return func(*args)

        raise RuntimeError_(
            message=f"'{func}' bukan fungsi yang bisa dipanggil.",
        )

    def visit_ClassNode(self, node: ClassNode) -> None:
        """Deklarasi kelas."""
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

        # Constructor: create instance
        def class_constructor(*args):
            instance = BroLangInstance(klass)
            # Call __init__ if exists
            init_method = klass.get_method("__init__")
            if init_method:
                init_method(instance, *args)
            return instance

        self.current_env.variables[node.name] = class_constructor
        self.current_env.classes[node.name] = klass

    def _create_method(self, node) -> Callable:
        """Membuat method dari FunctionNode atau MethodNode."""
        def method(self_instance, *args):
            old_env = self.current_env
            self._push_env()
            self.current_env.define_variable("self", self_instance)

            for i, param in enumerate(node.params):
                # Skip 'self' if present in params
                if param == "self":
                    continue
                adjusted_idx = i - 1 if node.params[0] == "self" else i
                if adjusted_idx >= 0 and adjusted_idx < len(args):
                    self.current_env.define_variable(param, args[adjusted_idx])
                else:
                    self.current_env.define_variable(param, None)

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
            line=node.line, column=node.column,
        )

    def visit_ObjectAccessNode(self, node: ObjectAccessNode) -> Any:
        """Akses properti/method objek."""
        obj = self.visit(node.object)
        prop = node.property

        if isinstance(obj, BroLangInstance):
            return obj.get(prop)

        if isinstance(obj, dict):
            if prop in obj:
                return obj[prop]
            raise RuntimeError_(
                message=f"Objek tidak memiliki properti '{prop}'.",
                line=node.line, column=node.column,
            )

        if hasattr(obj, prop):
            return getattr(obj, prop)

        raise RuntimeError_(
            message=f"Tidak bisa mengakses '{prop}' pada tipe {type(obj).__name__}.",
            line=node.line, column=node.column,
        )

    def visit_ImportNode(self, node: ImportNode) -> None:
        """Import module."""
        module_name = node.module
        try:
            module = get_stdlib_module(module_name)
            alias = node.alias or module_name.split(".")[0]
            self.current_env.variables[alias] = module
        except ImportError:
            # Try Python import
            try:
                import importlib
                py_module = importlib.import_module(module_name)
                alias = node.alias or module_name
                self.current_env.variables[alias] = py_module
            except ImportError:
                raise RuntimeError_(
                    message=f"Module '{module_name}' tidak ditemukan.",
                    line=node.line, column=node.column,
                    solution=f"Pastikan modul '{module_name}' sudah terinstal.",
                )

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
                    line=node.line, column=node.column,
                )

    def visit_TryNode(self, node: TryNode) -> Optional[Any]:
        """Try-catch execution."""
        try:
            self._push_env()
            result = None
            for stmt in node.body:
                result = self.visit(stmt)
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
            return result

    def visit_ListNode(self, node: ListNode) -> List[Any]:
        """List literal."""
        return [self.visit(elem) for elem in node.elements]

    def visit_IndexNode(self, node: IndexNode) -> Any:
        """Indexing operation."""
        target = self.visit(node.target)
        index = self.visit(node.index)

        if isinstance(target, (list, str)):
            try:
                return target[index]
            except IndexError:
                raise IndexError_(
                    message=f"Indeks {index} di luar batas. Panjang: {len(target)}.",
                    line=node.line, column=node.column,
                    solution=f"Gunakan indeks antara 0 dan {len(target) - 1}.",
                )

        raise TypeError_(
            message=f"Tipe {type(target).__name__} tidak bisa di-index.",
            line=node.line, column=node.column,
        )

    def visit_ObjectNode(self, node: ObjectNode) -> Dict[str, Any]:
        """Object/dict literal."""
        return {k: self.visit(v) for k, v in node.entries.items()}

    def visit_PrintNode(self, node: PrintNode) -> None:
        """Print statement."""
        values = [self.visit(node.expression)]
        for arg in node.args:
            values.append(self.visit(arg))

        output = " ".join(str(v) for v in values)
        self.output.append(output)
        print(output)

    def visit_InputNode(self, node: InputNode) -> str:
        """Input statement."""
        if node.prompt:
            prompt = str(self.visit(node.prompt))
            return input(prompt)
        return input()

    # ============= V2: Lambda =============

    def visit_LambdaNode(self, node: LambdaNode) -> Callable:
        """Lambda expression: lalu(x) x + 1"""
        def lambda_func(*args):
            old_env = self.current_env
            self._push_env()
            for i, param in enumerate(node.params):
                if i < len(args):
                    self.current_env.define_variable(param, args[i])
                else:
                    self.current_env.define_variable(param, None)
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
        return ''.join(result)

    # ============= V2: Enum =============

    def visit_EnumNode(self, node: EnumNode) -> None:
        """Enum declaration: enum Warna { MERAH, BIRU, HIJAU }"""
        enum_members = {}
        enum_class = type(node.name, (), {
            '__init__': lambda self, val=None: setattr(self, 'value', val),
            '__repr__': lambda self: f"{self.__class__.__name__}.{getattr(self, '_member_name', '?')}",
            '__eq__': lambda self, other: isinstance(other, type(self)) and self.value == other.value,
            '__hash__': lambda self: hash(getattr(self, 'value', 0)),
        })
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
        struct_class = type(node.name, (), {
            '__init__': lambda self, *args: _struct_init(self, node.fields, args),
            '__repr__': lambda self: f"{node.name}({', '.join(str(getattr(self, f)) for f in node.fields)})",
        })
        struct_class._fields = node.fields
        self.current_env.variables[node.name] = struct_class

    def visit_StructInstanceNode(self, node: StructInstanceNode) -> Any:
        """Struct instantiation: Titik(10, 20)"""
        struct_class = self.current_env.get_variable(node.struct_name)
        args = [self.visit(arg) for arg in node.args]
        return struct_class(*args)

    # ============= V2: Match/Case =============

    def visit_MatchNode(self, node: MatchNode) -> Any:
        """Match/case: cocokkan expr { pattern: body, ... }"""
        value = self.visit(node.value)
        for pattern, body in node.cases:
            if isinstance(pattern, WildcardNode):
                continue
            pattern_val = self.visit(pattern)
            if value == pattern_val:
                self._push_env()
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

    def visit_WildcardNode(self, node: WildcardNode) -> None:
        return None
