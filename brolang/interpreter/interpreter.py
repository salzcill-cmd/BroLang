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
    AugmentedAssignmentNode, TernaryNode, RaiseNode,
    GlobalNode, NonlocalNode,
    PassNode, DelNode, AssertNode,
    TupleNode, SetNode, DictComprehensionNode,
    AsyncFunctionDefNode, AwaitNode,
    YieldNode, YieldFromNode, GeneratorFunctionNode,
    DecoratorNode, DecoratedFunctionNode, DecoratedClassNode,
    WalrusNode, WithNode, TypedExceptNode, MultiExceptNode,
    StarImportNode, ChainedCallNode, SwitchNode,
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
        elif node.operator == "~":
            return ~int(operand)

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

    def visit_ForNode(self, node: ForNode) -> None:
        """For loop execution with optional else clause."""
        iterable = self.visit(node.iterable)
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
        """Break statement."""
        raise BreakException()

    def visit_ContinueNode(self, node: ContinueNode) -> None:
        """Continue statement."""
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
                line=node.line, column=node.column,
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
                        line=node.line, column=node.column,
                    )
            else:
                raise TypeError_(
                    message=f"Tipe {type(target).__name__} tidak bisa dihapus elemennya.",
                    line=node.line, column=node.column,
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
                        line=node.line, column=node.column,
                    )
            elif isinstance(obj, BroLangInstance):
                if prop in obj.attributes:
                    del obj.attributes[prop]
                else:
                    raise RuntimeError_(
                        message=f"Atribut '{prop}' tidak ditemukan.",
                        line=node.line, column=node.column,
                    )
        else:
            raise RuntimeError_(
                message="Target 'hapus' tidak valid.",
                line=node.line, column=node.column,
            )

    def visit_AssertNode(self, node: AssertNode) -> None:
        """Assert statement."""
        condition = self.visit(node.condition)
        if not condition:
            msg = self.visit(node.message) if node.message else "Assertion gagal"
            raise RuntimeError_(
                message=f"Pastikan: {msg}",
                line=node.line, column=node.column,
            )

    def visit_FunctionNode(self, node: FunctionNode) -> None:
        """Deklarasi fungsi dengan closure support."""
        # Capture the enclosing environment at definition time (closure)
        closure_env = self.current_env
        
        def bro_function(*args):
            old_env = self.current_env
            self._push_env()
            # Set parent to captured closure env for proper scope chain
            self.current_env.parent = closure_env

            # Bind parameters with default values
            for i, param in enumerate(node.params):
                if i < len(args):
                    self.current_env.define_variable(param, args[i])
                elif i < len(node.defaults):
                    dv = node.defaults[i]
                    if dv is not None:
                        default_val = self.visit(dv)
                        self.current_env.define_variable(param, default_val)
                    else:
                        self.current_env.define_variable(param, None)
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
                # List methods
                if isinstance(obj, list):
                    methods = self._get_list_methods(obj)
                    if method_name in methods:
                        return methods[method_name](*args)
                # Dict methods
                if isinstance(obj, dict):
                    methods = self._get_dict_methods(obj)
                    if method_name in methods:
                        return methods[method_name](*args)
                # String methods
                if isinstance(obj, str):
                    methods = self._get_string_methods(obj)
                    if method_name in methods:
                        return methods[method_name](*args)
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
            methods = self._get_dict_methods(obj)
            if prop in methods:
                return methods[prop]
            raise RuntimeError_(
                message=f"Objek tidak memiliki properti '{prop}'.",
                line=node.line, column=node.column,
            )

        if isinstance(obj, list):
            methods = self._get_list_methods(obj)
            if prop in methods:
                return methods[prop]
            raise RuntimeError_(
                message=f"List tidak memiliki method '{prop}'.",
                line=node.line, column=node.column,
            )

        if isinstance(obj, str):
            methods = self._get_string_methods(obj)
            if prop in methods:
                return methods[prop]
            raise RuntimeError_(
                message=f"String tidak memiliki method '{prop}'.",
                line=node.line, column=node.column,
            )

        if isinstance(obj, str):
            methods = self._get_string_methods(obj)
            if prop in methods:
                return methods[prop]
            raise RuntimeError_(
                message=f"String tidak memiliki method '{prop}'.",
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

    def visit_ListNode(self, node: ListNode) -> List[Any]:
        """List literal."""
        return [self.visit(elem) for elem in node.elements]

    def visit_TupleNode(self, node: TupleNode) -> tuple:
        """Tuple literal."""
        return tuple(self.visit(elem) for elem in node.elements)

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
                    line=node.line, column=node.column,
                )
            start = self.visit(node.slice_start) if node.slice_start else None
            stop = self.visit(node.slice_stop) if node.slice_stop else None
            step = self.visit(node.slice_step) if node.slice_step else None
            try:
                return target[start:stop:step]
            except Exception as e:
                raise RuntimeError_(
                    message=f"Error slicing: {e}",
                    line=node.line, column=node.column,
                )

        # Regular indexing
        index = self.visit(node.index)

        if isinstance(target, (list, str, tuple)):
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
        """Lambda expression with closure: lalu(x) x + 1"""
        # Capture the enclosing environment at definition time (closure)
        closure_env = self.current_env
        
        def lambda_func(*args):
            old_env = self.current_env
            # Create new env with captured closure env as parent
            self._push_env()
            self.current_env.parent = closure_env
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

    # ============= V3: Augmented Assignment =============

    def visit_AugmentedAssignmentNode(self, node: AugmentedAssignmentNode) -> Any:
        """Augmented assignment: x += 1, x -= 2, dll."""
        if not isinstance(node.target, IdentifierNode):
            raise RuntimeError_(
                message="Target augmented assignment harus berupa variabel.",
                line=node.line, column=node.column,
            )

        name = node.target.name
        current = self.current_env.get_variable(name)
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
                    line=node.line, column=node.column,
                )
            result = current / right
        elif op == "%=":
            if right == 0:
                raise ZeroDivisionError_(
                    message="Tidak bisa modulo dengan nol.",
                    line=node.line, column=node.column,
                )
            result = current % right
        elif op == "**=":
            result = current ** right
        else:
            raise RuntimeError_(
                message=f"Operator augmented assignment '{op}' tidak dikenal.",
                line=node.line, column=node.column,
            )

        self.current_env.set_variable(name, result)
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
        """Raise: lempar nilai"""
        value = self.visit(node.value)
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
            "cocok": lambda pattern: bool(__import__('re').search(pattern, s)),
            "cocok_semua": lambda pattern: __import__('re').findall(pattern, s),
            "ganti_regexp": lambda pattern, replacement: __import__('re').sub(pattern, replacement, s),
            "bagi_regexp": lambda pattern: __import__('re').split(pattern, s),
            "encode": lambda enc='utf-8': s.encode(enc),
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

        def async_function(*args):
            old_env = self.current_env
            self._push_env()
            self.current_env.parent = closure_env

            for i, param in enumerate(node.params):
                if i < len(args):
                    self.current_env.define_variable(param, args[i])
                elif i < len(node.defaults):
                    dv = node.defaults[i]
                    if dv is not None:
                        default_val = self.visit(dv)
                        self.current_env.define_variable(param, default_val)
                    else:
                        self.current_env.define_variable(param, None)
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
            except Exception as e:
                self._pop_env()
                self.current_env = old_env
                raise e

        self.current_env.functions[node.name] = async_function

    def visit_AwaitNode(self, node: AwaitNode) -> Any:
        """Await expression — in sync interpreter, just evaluate the expression."""
        return self.visit(node.value)

    # ============= V4: Generators =============

    def visit_YieldNode(self, node: YieldNode) -> Any:
        """Yield statement — creates a generator."""
        value = self.visit(node.value) if node.value else None
        # In a sync interpreter, we'll collect all yields into a list
        # This is a simplified generator implementation
        return value

    def visit_YieldFromNode(self, node: YieldFromNode) -> Any:
        """Yield from — delegates to another iterable."""
        iterable = self.visit(node.value)
        result = []
        for item in iterable:
            result.append(item)
        return result

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

        def bro_function(*args):
            old_env = self.current_env
            self._push_env()
            self.current_env.parent = closure_env

            for i, param in enumerate(node.params):
                if i < len(args):
                    self.current_env.define_variable(param, args[i])
                elif i < len(node.defaults):
                    dv = node.defaults[i]
                    if dv is not None:
                        default_val = self.visit(dv)
                        self.current_env.define_variable(param, default_val)
                    else:
                        self.current_env.define_variable(param, None)
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

        def class_constructor(*args):
            instance = BroLangInstance(klass)
            init_method = klass.get_method("__init__")
            if init_method:
                init_method(instance, *args)
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
        if hasattr(context, '__enter__'):
            enter_result = context.__enter__()
        elif hasattr(context, 'masuk'):
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
            if hasattr(context, '__exit__'):
                context.__exit__(None, None, None)
            elif hasattr(context, 'keluar'):
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
                        'RuntimeError': RuntimeError_,
                        'TypeError': TypeError_,
                        'NameError': NameError_,
                        'ZeroDivisionError': ZeroDivisionError_,
                        'IndexError': IndexError_,
                        'ValueError': ValueError,
                        'KeyError': KeyError,
                        'AttributeError': AttributeError,
                    }
                    exc_class = exc_type_map.get(exc_type_name)
                    if exc_class and isinstance(e, exc_class):
                        self._push_env()
                        self.current_env.define_variable(clause.variable, e)
                        for stmt in clause.body:
                            result = self.visit(stmt)
                        self._pop_env()
                        matched = True
                        break
                    elif exc_type_name == 'semua':
                        self._push_env()
                        self.current_env.define_variable(clause.variable, e)
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
                if not attr.startswith('_'):
                    self.current_env.variables[attr] = getattr(module, attr)
        except ImportError:
            try:
                import importlib
                py_module = importlib.import_module(node.module)
                for attr in dir(py_module):
                    if not attr.startswith('_'):
                        self.current_env.variables[attr] = getattr(py_module, attr)
            except ImportError:
                raise RuntimeError_(
                    message=f"Module '{node.module}' tidak ditemukan.",
                    line=node.line, column=node.column,
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
        """Generator function declaration."""
        closure_env = self.current_env

        def generator_func(*args):
            old_env = self.current_env
            self._push_env()
            self.current_env.parent = closure_env

            for i, param in enumerate(node.params):
                if i < len(args):
                    self.current_env.define_variable(param, args[i])
                elif i < len(node.defaults):
                    dv = node.defaults[i]
                    if dv is not None:
                        default_val = self.visit(dv)
                        self.current_env.define_variable(param, default_val)
                    else:
                        self.current_env.define_variable(param, None)
                else:
                    self.current_env.define_variable(param, None)

            # Collect all yielded values
            results = []
            try:
                for stmt in node.body:
                    result = self.visit(stmt)
                    if isinstance(result, (int, float, str, bool, list, tuple)):
                        results.append(result)
                    if self.current_env.should_return:
                        break
            except ReturnException:
                pass
            except BreakException:
                pass
            finally:
                self._pop_env()
                self.current_env = old_env

            return results

        self.current_env.functions[node.name] = generator_func
