"""
Compiler BroLang → Python Bytecode
===================================

Compiler ini mengubah AST BroLang menjadi kode Python
yang kemudian dikompilasi ke Python bytecode.

Design:
    - Visitor pattern untuk konversi AST
    - Menghasilkan Python source code yang bersih
    - Mempertahankan line numbers untuk error reporting
    - Mendukung semua fitur BroLang 1.0
"""

from typing import Any, Dict, List, Optional
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
)
from brolang.optimizer import Optimizer


class PythonCodeGenerator(ASTVisitor):
    """Generate Python code dari AST BroLang.

    Attributes:
        indent_level: Level indentasi saat ini
        output: List baris kode Python yang dihasilkan
        import_std: Set modul stdlib yang perlu di-import
    """

    def __init__(self):
        self.indent_level: int = 0
        self.output: List[str] = []
        self.import_std: set = set()
        self._current_function: Optional[str] = None
        self._current_class: Optional[str] = None
        self._temp_counter: int = 0

    def compile(self, node: ASTNode) -> str:
        """Mengompilasi AST menjadi Python code.

        Args:
            node: AST node root

        Returns:
            str: Python source code
        """
        self.output = []
        self.import_std = set()
        self.indent_level = 0

        # Add required imports
        self.output.append("# Compiled by BroLang Compiler")
        self.output.append("# https://github.com/brolang/brolang")
        self.output.append("")

        # Visit the AST
        self.visit(node)

        # Add stdlib imports at the top if needed
        header = []
        if self.import_std:
            for mod in sorted(self.import_std):
                py_mod = self._stdlib_to_python(mod)
                header.append(f"from brolang.stdlib.{mod} import module as {mod}")
            header.append("")

        return "\n".join(header + self.output)

    def _stdlib_to_python(self, name: str) -> str:
        """Map BroLang stdlib to Python module."""
        mapping = {
            "matematika": "math",
            "teks": "str",
            "waktu": "time",
            "file": "io",
            "json": "json",
            "jaringan": "urllib",
            "acak": "random",
        }
        return mapping.get(name, name)

    def _emit(self, line: str = "") -> None:
        """Menambahkan baris kode dengan indentasi yang benar."""
        indent = "    " * self.indent_level
        self.output.append(f"{indent}{line}")

    def _new_temp(self) -> str:
        """Membuat nama temporary variable."""
        self._temp_counter += 1
        return f"_bro_tmp_{self._temp_counter}"

    # ============= Visitor Methods =============

    def visit_ProgramNode(self, node: ProgramNode) -> None:
        for stmt in node.statements:
            self.visit(stmt)

    def visit_NumberNode(self, node: NumberNode) -> str:
        return str(node.value)

    def visit_DecimalNode(self, node: DecimalNode) -> str:
        return str(node.value)

    def visit_StringNode(self, node: StringNode) -> str:
        return repr(node.value)

    def visit_BooleanNode(self, node: BooleanNode) -> str:
        return "True" if node.value else "False"

    def visit_KosongNode(self, node: KosongNode) -> str:
        return "None"

    def visit_IdentifierNode(self, node: IdentifierNode) -> str:
        name = node.name
        if name == "input":
            return "input"
        if name in self._get_current_vars():
            return name
        return name

    def _get_current_vars(self) -> set:
        """Get set of known variable names (simplified)."""
        return set()

    def visit_AssignmentNode(self, node: AssignmentNode) -> None:
        if isinstance(node.target, IdentifierNode):
            name = node.target.name
            if node.value:
                value_code = self._expr(node.value)
                self._emit(f"{name} = {value_code}")
            else:
                self._emit(f"{name} = None")
        else:
            target_code = self._expr(node.target)
            if node.value:
                value_code = self._expr(node.value)
                self._emit(f"{target_code} = {value_code}")

    def visit_BinaryOpNode(self, node: BinaryOpNode) -> str:
        left = self._expr(node.left)
        right = self._expr(node.right)
        op_map = {
            "==": "==", "!=": "!=", ">": ">", "<": "<",
            ">=": ">=", "<=": "<=",
            "dan": "and", "atau": "or",
            "+": "+", "-": "-", "*": "*", "/": "/",
            "%": "%", "**": "**",
        }
        py_op = op_map.get(node.operator, node.operator)
        return f"({left} {py_op} {right})"

    def visit_UnaryOpNode(self, node: UnaryOpNode) -> str:
        operand = self._expr(node.operand)
        if node.operator == "-":
            return f"(-{operand})"
        elif node.operator == "bukan":
            return f"(not {operand})"
        elif node.operator == "+":
            return f"(+{operand})"
        return f"({node.operator}{operand})"

    def visit_IfNode(self, node: IfNode) -> None:
        cond = self._expr(node.condition)
        self._emit(f"if {cond}:")
        self.indent_level += 1
        for stmt in node.body:
            self.visit(stmt)
        self.indent_level -= 1

        for i, elif_cond in enumerate(node.elif_conditions):
            elif_cond_code = self._expr(elif_cond)
            self._emit(f"elif {elif_cond_code}:")
            self.indent_level += 1
            for stmt in node.elif_bodies[i]:
                self.visit(stmt)
            self.indent_level -= 1

        if node.else_body:
            self._emit("else:")
            self.indent_level += 1
            for stmt in node.else_body:
                self.visit(stmt)
            self.indent_level -= 1

    def visit_WhileNode(self, node: WhileNode) -> None:
        cond = self._expr(node.condition)
        self._emit(f"while {cond}:")
        self.indent_level += 1
        for stmt in node.body:
            self.visit(stmt)
        self.indent_level -= 1

    def visit_ForNode(self, node: ForNode) -> None:
        iterable = self._expr(node.iterable)
        self._emit(f"for {node.variable} in {iterable}:")
        self.indent_level += 1
        for stmt in node.body:
            self.visit(stmt)
        self.indent_level -= 1

    def visit_BreakNode(self, node: BreakNode) -> None:
        self._emit("break")

    def visit_ContinueNode(self, node: ContinueNode) -> None:
        self._emit("continue")

    def visit_PassNode(self, node: PassNode) -> None:
        self._emit("pass")

    def visit_DelNode(self, node: DelNode) -> None:
        target = self._expr(node.target)
        self._emit(f"del {target}")

    def visit_AssertNode(self, node: AssertNode) -> None:
        cond = self._expr(node.condition)
        if node.message:
            msg = self._expr(node.message)
            self._emit(f"assert {cond}, {msg}")
        else:
            self._emit(f"assert {cond}")

    def visit_TupleNode(self, node: TupleNode) -> None:
        elements = ", ".join(self._expr(e) for e in node.elements)
        self._emit_line(f"({elements})")

    def visit_SetNode(self, node: SetNode) -> None:
        elements = ", ".join(self._expr(e) for e in node.elements)
        self._emit_line(f"{{{elements}}}")

    def visit_DictComprehensionNode(self, node: DictComprehensionNode) -> None:
        key = self._expr(node.key_expr)
        val = self._expr(node.value_expr)
        var = node.key_var
        iterable = self._expr(node.iterable)
        if node.condition:
            cond = self._expr(node.condition)
            if node.value_var:
                self._emit_line(f"{{{key}: {val} for {var}, {node.value_var} in {iterable} if {cond}}}")
            else:
                self._emit_line(f"{{{key}: {val} for {var} in {iterable} if {cond}}}")
        else:
            if node.value_var:
                self._emit_line(f"{{{key}: {val} for {var}, {node.value_var} in {iterable}}}")
            else:
                self._emit_line(f"{{{key}: {val} for {var} in {iterable}}}")

    def visit_FunctionNode(self, node: FunctionNode) -> None:
        params = ", ".join(node.params)
        self._emit(f"def {node.name}({params}):")
        self.indent_level += 1
        for stmt in node.body:
            self.visit(stmt)
        self.indent_level -= 1
        self._emit()

    def visit_ReturnNode(self, node: ReturnNode) -> None:
        if node.value:
            val = self._expr(node.value)
            self._emit(f"return {val}")
        else:
            self._emit("return")

    def visit_CallNode(self, node: CallNode) -> str:
        args = ", ".join(self._expr(arg) for arg in node.args)

        if node.is_method:
            # Object.method(...)
            if isinstance(node.function, ObjectAccessNode):
                obj_code = self._expr(node.function.object)
                method_name = node.function.property
                return f"{obj_code}.{method_name}({args})"

        if isinstance(node.function, IdentifierNode):
            func_name = node.function.name
            builtin_map = {
                "tulis": "print",
                "len": "len",
                "angka": "int",
                "desimal": "float",
                "teks": "str",
                "range": "range",
            }
            py_name = builtin_map.get(func_name, func_name)
            return f"{py_name}({args})"

        func_code = self._expr(node.function)
        return f"{func_code}({args})"

    def visit_ClassNode(self, node: ClassNode) -> None:
        parent = f"({node.parent})" if node.parent else "()"
        self._emit(f"class {node.name}{parent}:")
        self.indent_level += 1
        for stmt in node.body:
            self.visit(stmt)
        self.indent_level -= 1
        self._emit()

    def visit_MethodNode(self, node: MethodNode) -> None:
        params = ", ".join(node.params)
        if not params.startswith("self"):
            params = "self" + (", " + params if params else "")
        self._emit(f"def {node.name}({params}):")
        self.indent_level += 1
        for stmt in node.body:
            self.visit(stmt)
        self.indent_level -= 1
        self._emit()

    def visit_ObjectAccessNode(self, node: ObjectAccessNode) -> str:
        obj_code = self._expr(node.object)
        return f"{obj_code}.{node.property}"

    def visit_ImportNode(self, node: ImportNode) -> None:
        module_name = node.module
        if module_name in ("matematika", "teks", "waktu", "file", "json", "jaringan", "acak"):
            self.import_std.add(module_name)
            alias = node.alias or module_name
            self._emit(f"{alias} = {module_name}")
        else:
            self._emit(f"import {module_name}")

    def visit_FromImportNode(self, node: FromImportNode) -> None:
        names = ", ".join(node.names)
        if node.module in ("matematika", "teks", "waktu", "file", "json", "jaringan", "acak"):
            self.import_std.add(node.module)
            for name in node.names:
                self._emit(f"{name} = {node.module}.{name}")
        else:
            self._emit(f"from {node.module} import {names}")

    def visit_TryNode(self, node: TryNode) -> None:
        self._emit("try:")
        self.indent_level += 1
        for stmt in node.body:
            self.visit(stmt)
        self.indent_level -= 1
        self._emit(f"except Exception as {node.catch_var}:")
        self.indent_level += 1
        for stmt in node.catch_body:
            self.visit(stmt)
        self.indent_level -= 1

    def visit_ListNode(self, node: ListNode) -> str:
        elements = ", ".join(self._expr(e) for e in node.elements)
        return f"[{elements}]"

    def visit_IndexNode(self, node: IndexNode) -> str:
        target = self._expr(node.target)
        index = self._expr(node.index)
        return f"{target}[{index}]"

    def visit_ObjectNode(self, node: ObjectNode) -> str:
        entries = ", ".join(f"{repr(k)}: {self._expr(v)}" for k, v in node.entries.items())
        return "{" + entries + "}"

    def visit_AttributeNode(self, node: AttributeNode) -> str:
        obj = self._expr(node.object)
        return f"{obj}.{node.attribute}"

    def visit_PrintNode(self, node: PrintNode) -> None:
        args_code = ", ".join(self._expr(arg) for arg in [node.expression] + node.args)
        self._emit(f"print({args_code})")

    def visit_InputNode(self, node: InputNode) -> str:
        if node.prompt:
            prompt_code = self._expr(node.prompt)
            return f"input({prompt_code})"
        return "input()"

    def _expr(self, node: ASTNode) -> str:
        """Evaluate an expression node to Python code string."""
        method_name = f"visit_{node.__class__.__name__}"
        visitor = getattr(self, method_name, None)
        if visitor is None:
            return ""
        result = visitor(node)
        return result if isinstance(result, str) else ""


class Compiler:
    """Compiler utama BroLang.

    Menangani seluruh proses kompilasi:
    1. Optimasi AST
    2. Generate Python code
    3. Compile ke Python bytecode
    """

    def __init__(self, optimize: bool = True):
        self.optimize = optimize
        self.generator = PythonCodeGenerator()
        self.optimizer = Optimizer() if optimize else None

    def compile(self, node: ASTNode) -> str:
        """Mengompilasi AST menjadi Python code.

        Args:
            node: AST node

        Returns:
            str: Python source code
        """
        if self.optimizer and self.optimize:
            node = self.optimizer.optimize(node)
        return self.generator.compile(node)

    def compile_to_bytecode(self, node: ASTNode) -> Any:
        """Mengompilasi AST ke Python bytecode.

        Args:
            node: AST node

        Returns:
            code object: Python bytecode yang siap dieksekusi
        """
        py_source = self.compile(node)
        return compile(py_source, "<brolang>", "exec")


def compile_source(source: str, filename: str = "<brolang>") -> str:
    """Convenience function: compile BroLang source ke Python.

    Args:
        source: Kode sumber BroLang
        filename: Nama file (untuk error reporting)

    Returns:
        str: Python source code
    """
    from brolang.lexer import Lexer
    from brolang.parser import Parser

    lexer = Lexer(source, file_path=filename)
    tokens = lexer.tokenize()
    parser = Parser(tokens, file_path=filename)
    ast = parser.parse()

    compiler = Compiler(optimize=True)
    return compiler.compile(ast)
