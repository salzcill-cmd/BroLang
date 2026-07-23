"""
Bytecode Compiler untuk BroLang
================================

Mengkonversi AST BroLang menjadi bytecode yang bisa dijalankan oleh VM.
"""

from typing import Optional, List, Any
from brolang.ast.nodes import (
    ASTNode, ProgramNode, NumberNode, DecimalNode, StringNode,
    BooleanNode, KosongNode, IdentifierNode, VariableNode, AssignmentNode,
    BinaryOpNode, UnaryOpNode, IfNode, WhileNode, ForNode,
    BreakNode, ContinueNode, FunctionNode, ReturnNode, CallNode,
    ClassNode, MethodNode, ListNode, TupleNode, SetNode,
    ObjectNode, ObjectAccessNode, IndexNode, PrintNode,
    FStringNode, LambdaNode, PassNode, DelNode, AssertNode,
    RaiseNode, TryNode, AugmentedAssignmentNode, TernaryNode,
    NullCoalescingNode, OptionalChainingNode,
    EnumNode, StructNode, StructInstanceNode,
    MatchNode, WildcardNode, ComprehensionNode,
    DictComprehensionNode, ImportNode, FromImportNode,
    GlobalNode, NonlocalNode, InputNode,
)
from brolang.vm.opcodes import Op, Bytecode


class Compiler:
    """Kompilasi AST ke bytecode."""

    def __init__(self):
        self.bytecode = Bytecode()
        self.scope_depth = 0
        self.locals = []        # [(name, scope_depth), ...]
        self.free_vars = []     # Closure variable names
        self.breakpoints = []

    def compile(self, node: ASTNode) -> Bytecode:
        """Compile AST ke bytecode."""
        if isinstance(node, ProgramNode):
            for stmt in node.statements:
                self._emit_stmt(stmt)
            self.bytecode.add(Op.HALT)
        else:
            self._emit_stmt(node)
            self.bytecode.add(Op.HALT)
        self.bytecode.finalize()
        return self.bytecode

    # ============= Statement Emitters =============

    def _emit_stmt(self, node: ASTNode):
        if isinstance(node, ProgramNode):
            for stmt in node.statements:
                self._emit_stmt(stmt)
            return

        if isinstance(node, AssignmentNode):
            self._emit_assignment(node)
        elif isinstance(node, FunctionNode):
            self._emit_function(node)
        elif isinstance(node, ClassNode):
            self._emit_class(node)
        elif isinstance(node, ReturnNode):
            self._emit_return(node)
        elif isinstance(node, IfNode):
            self._emit_if(node)
        elif isinstance(node, WhileNode):
            self._emit_while(node)
        elif isinstance(node, ForNode):
            self._emit_for(node)
        elif isinstance(node, PrintNode):
            self._emit_print(node)
        elif isinstance(node, BreakNode):
            self.bytecode.add(Op.JUMP, ('BREAK',), node.line, node.column)
        elif isinstance(node, ContinueNode):
            self.bytecode.add(Op.JUMP, ('CONTINUE',), node.line, node.column)
        elif isinstance(node, PassNode):
            self.bytecode.add(Op.NOP, line=node.line, column=node.column)
        elif isinstance(node, DelNode):
            self._emit_del(node)
        elif isinstance(node, AssertNode):
            self._emit_assert(node)
        elif isinstance(node, RaiseNode):
            self._emit_raise(node)
        elif isinstance(node, ImportNode):
            self._emit_import(node)
        elif isinstance(node, FromImportNode):
            self._emit_import(node)
        elif isinstance(node, GlobalNode):
            pass  # Handled during compilation
        elif isinstance(node, NonlocalNode):
            pass
        elif isinstance(node, EnumNode):
            self._emit_enum(node)
        elif isinstance(node, StructNode):
            self._emit_struct(node)
        elif isinstance(node, AugmentedAssignmentNode):
            self._emit_augmented_assignment(node)
        elif isinstance(node, TryNode):
            self._emit_try(node)
        else:
            # Expression statement — evaluate and pop
            self._emit_expr(node)
            self.bytecode.add(Op.POP_TOP, line=getattr(node, 'line', 0))

    # ============= Assignment =============

    def _emit_assignment(self, node: AssignmentNode):
        self._emit_expr(node.value)
        name = self._get_assign_name(node)
        if node.is_declaration:
            if self.scope_depth == 0:
                idx = self.bytecode.add_name(name)
                self.bytecode.add(Op.DEFINE_GLOBAL, idx, node.line, node.column)
            else:
                idx = self._add_local(name)
                self.bytecode.add(Op.STORE_LOCAL, idx, node.line, node.column)
        else:
            loc = self._resolve_name(name)
            if loc == 'local':
                idx = self._get_local_idx(name)
                self.bytecode.add(Op.STORE_LOCAL, idx, node.line, node.column)
            elif loc == 'free':
                idx = self.bytecode.add_free_var(name)
                self.bytecode.add(Op.STORE_DEREF, idx, node.line, node.column)
            else:
                idx = self.bytecode.add_name(name)
                self.bytecode.add(Op.STORE_GLOBAL, idx, node.line, node.column)

    def _get_assign_name(self, node: AssignmentNode) -> str:
        if isinstance(node.target, IdentifierNode):
            return node.target.name
        if isinstance(node.target, ObjectAccessNode):
            self._emit_expr(node.target.object)
            self._emit_expr(node.value)
            prop = self.bytecode.add_name(node.target.property)
            self.bytecode.add(Op.STORE_ATTR, prop, node.line, node.column)
            return None
        if isinstance(node.target, IndexNode):
            self._emit_expr(node.target.target)
            self._emit_expr(node.target.index)
            self._emit_expr(node.value)
            self.bytecode.add(Op.INDEX_SET, line=node.line, column=node.column)
            return None
        return ''

    # ============= Function =============

    def _emit_function(self, node: FunctionNode, is_lambda=False):
        """Emit function as closure object."""
        func_name = node.name

        # Compile function body into a sub-bytecode
        saved = self.bytecode
        saved_locals = self.locals
        saved_free = self.free_vars
        saved_depth = self.scope_depth

        self.bytecode = Bytecode()
        self.scope_depth += 1
        self.locals = []
        self.free_vars = []

        # Parameters become locals
        for param in node.params:
            self._add_local(param)

        # Compile body
        for stmt in node.body:
            self._emit_stmt(stmt)
        self.bytecode.add(Op.PUSH_NONE)
        self.bytecode.add(Op.RETURN)

        # Capture free vars from enclosing scope
        captured_free = list(self.free_vars)

        func_bytecode = self.bytecode
        func_bytecode.finalize()

        # Restore state
        self.bytecode = saved
        self.locals = saved_locals
        self.free_vars = saved_free
        self.scope_depth = saved_depth

        # Emit closure in parent scope
        const_idx = self.bytecode.add_const(func_bytecode)
        param_count = len(node.params)
        has_defaults = len(node.defaults) > 0 and any(d is not None for d in node.defaults)

        # Create closure instruction
        self.bytecode.add(Op.CLOSURE, (const_idx, param_count, has_defaults),
                         node.line, node.column)

        # Push default values if any
        if has_defaults:
            for d in node.defaults:
                if d is not None:
                    self._emit_expr(d)
                else:
                    self.bytecode.add(Op.PUSH_NONE)

        if is_lambda:
            return

        # Store the function
        if self.scope_depth == 0:
            idx = self.bytecode.add_name(func_name)
            self.bytecode.add(Op.DEFINE_GLOBAL, idx, node.line, node.column)
        else:
            idx = self._add_local(func_name)
            self.bytecode.add(Op.STORE_LOCAL, idx, node.line, node.column)

    # ============= Class =============

    def _emit_class(self, node: ClassNode):
        """Emit class declaration."""
        # Emit parent class if any
        if node.parent:
            idx = self.bytecode.add_name(node.parent)
            self.bytecode.add(Op.LOAD_GLOBAL, idx, node.line, node.column)
        else:
            self.bytecode.add(Op.PUSH_NONE)

        # Collect method bytecodes
        methods = {}
        for method in node.methods:
            saved = self.bytecode
            saved_locals = self.locals
            saved_free = self.free_vars
            saved_depth = self.scope_depth

            self.bytecode = Bytecode()
            self.scope_depth += 1
            self.locals = []
            self.free_vars = []

            # Add self as first param if not static
            if not method.is_static:
                self._add_local('self')
            for param in method.params:
                if param == 'self' and not method.is_static:
                    continue
                self._add_local(param)

            for stmt in method.body:
                self._emit_stmt(stmt)
            self.bytecode.add(Op.PUSH_NONE)
            self.bytecode.add(Op.RETURN)

            method_bc = self.bytecode
            method_bc.finalize()
            self.bytecode = saved
            self.locals = saved_locals
            self.free_vars = saved_free
            self.scope_depth = saved_depth

            total_params = len(method.params)
            methods[method.name] = (method_bc, method.is_static, total_params)

        idx = self.bytecode.add_const((node.name, methods))
        self.bytecode.add(Op.MAKE_CLASS, idx, node.line, node.column)

        # Store class
        name_idx = self.bytecode.add_name(node.name)
        self.bytecode.add(Op.DEFINE_GLOBAL, name_idx, node.line, node.column)

    # ============= Control Flow =============

    def _emit_if(self, node: IfNode):
        self._emit_expr(node.condition)
        jump_false_idx = len(self.bytecode.instructions)
        self.bytecode.add(Op.POP_JUMP_IF_FALSE, 0, node.line, node.column)

        for stmt in node.body:
            self._emit_stmt(stmt)

        else_jumps = []

        for i, (ec, eb) in enumerate(zip(node.elif_conditions, node.elif_bodies)):
            else_jumps.append(len(self.bytecode.instructions))
            self.bytecode.add(Op.JUMP, 0, node.line, node.column)

            # Patch previous jump to here
            self.bytecode.instructions[jump_false_idx].arg = len(self.bytecode.instructions)

            self._emit_expr(ec)
            jump_false_idx = len(self.bytecode.instructions)
            self.bytecode.add(Op.POP_JUMP_IF_FALSE, 0, node.line, node.column)

            for stmt in eb:
                self._emit_stmt(stmt)

        if node.else_body:
            else_jumps.append(len(self.bytecode.instructions))
            self.bytecode.add(Op.JUMP, 0, node.line, node.column)

        # Patch the last condition jump
        self.bytecode.instructions[jump_false_idx].arg = len(self.bytecode.instructions)

        for stmt in node.else_body:
            self._emit_stmt(stmt)

        # Patch all else/elif jumps
        for idx in else_jumps:
            self.bytecode.instructions[idx].arg = len(self.bytecode.instructions)

    def _emit_while(self, node: WhileNode):
        loop_start = len(self.bytecode.instructions)
        self._emit_expr(node.condition)
        exit_jump_idx = len(self.bytecode.instructions)
        self.bytecode.add(Op.POP_JUMP_IF_FALSE, 0, node.line, node.column)

        for stmt in node.body:
            self._emit_stmt(stmt)
            # Check for break/continue markers
            last = self.bytecode.instructions[-1]
            if last.op == Op.JUMP and isinstance(last.arg, tuple):
                if last.arg[0] == 'BREAK':
                    self.bytecode.instructions[-1] = Instruction(
                        Op.JUMP, len(self.bytecode.instructions) + 1,
                        last.line, last.column)
                    break
                elif last.arg[0] == 'CONTINUE':
                    self.bytecode.instructions[-1] = Instruction(
                        Op.JUMP, loop_start, last.line, last.column)

        self.bytecode.add(Op.JUMP, loop_start, node.line, node.column)
        self.bytecode.instructions[exit_jump_idx].arg = len(self.bytecode.instructions)

    def _emit_for(self, node: ForNode):
        """Emit for loop."""
        self._emit_expr(node.iterable)
        iter_var_idx = self._add_local('_iter')
        self.bytecode.add(Op.STORE_LOCAL, iter_var_idx, node.line, node.column)
        self.bytecode.add(Op.GET_ITER, line=node.line, column=node.column)

        loop_start = len(self.bytecode.instructions)

        var_name = node.variable
        body_jump_idx = len(self.bytecode.instructions)
        self.bytecode.add(Op.FOR_ITER, 0, node.line, node.column)

        # Store the loop variable
        self._ensure_local(var_name)
        var_idx = self._get_local_idx(var_name)
        self.bytecode.add(Op.STORE_LOCAL, var_idx, node.line, node.column)

        for stmt in node.body:
            self._emit_stmt(stmt)
            last = self.bytecode.instructions[-1]
            if last.op == Op.JUMP and isinstance(last.arg, tuple):
                if last.arg[0] == 'BREAK':
                    self.bytecode.instructions[-1] = Instruction(
                        Op.JUMP, len(self.bytecode.instructions) + 1,
                        last.line, last.column)
                    break
                elif last.arg[0] == 'CONTINUE':
                    self.bytecode.instructions[-1] = Instruction(
                        Op.JUMP, loop_start, last.line, last.column)

        self.bytecode.add(Op.JUMP, loop_start, node.line, node.column)
        self.bytecode.instructions[body_jump_idx].arg = len(self.bytecode.instructions)

        # Cleanup: remove iter and loop var from locals
        self._remove_locals(2)

    # ============= Print (fast path) =============

    def _emit_print(self, node: PrintNode):
        # Collect all expressions (main + args)
        exprs = [node.expression] + node.args
        for expr in exprs:
            self._emit_expr(expr)
        self.bytecode.add(Op.PRINT, len(exprs), node.line, node.column)

    # ============= Return =============

    def _emit_return(self, node: ReturnNode):
        if node.value and not isinstance(node.value, KosongNode):
            self._emit_expr(node.value)
            self.bytecode.add(Op.RETURN, line=node.line, column=node.column)
        else:
            self.bytecode.add(Op.PUSH_NONE, line=node.line, column=node.column)
            self.bytecode.add(Op.RETURN, line=node.line, column=node.column)

    # ============= Expression Emitter =============

    def _emit_expr(self, node: ASTNode):
        if isinstance(node, NumberNode):
            if node.value == 0:
                self.bytecode.add(Op.PUSH_INT_0, line=node.line, column=node.column)
            elif node.value == 1:
                self.bytecode.add(Op.PUSH_INT_1, line=node.line, column=node.column)
            else:
                idx = self.bytecode.add_const(node.value)
                self.bytecode.add(Op.PUSH_CONST, idx, node.line, node.column)

        elif isinstance(node, DecimalNode):
            idx = self.bytecode.add_const(node.value)
            self.bytecode.add(Op.PUSH_CONST, idx, node.line, node.column)

        elif isinstance(node, StringNode):
            idx = self.bytecode.add_const(node.value)
            self.bytecode.add(Op.PUSH_CONST, idx, node.line, node.column)

        elif isinstance(node, BooleanNode):
            if node.value:
                self.bytecode.add(Op.PUSH_TRUE, line=node.line, column=node.column)
            else:
                self.bytecode.add(Op.PUSH_FALSE, line=node.line, column=node.column)

        elif isinstance(node, KosongNode):
            self.bytecode.add(Op.PUSH_NONE, line=node.line, column=node.column)

        elif isinstance(node, (IdentifierNode, VariableNode)):
            name = node.name
            loc = self._resolve_name(name)
            if loc == 'local':
                idx = self._get_local_idx(name)
                self.bytecode.add(Op.LOAD_LOCAL, idx, node.line, node.column)
            elif loc == 'free':
                idx = self.bytecode.add_free_var(name)
                self.bytecode.add(Op.LOAD_DEREF, idx, node.line, node.column)
            else:
                idx = self.bytecode.add_name(name)
                self.bytecode.add(Op.LOAD_GLOBAL, idx, node.line, node.column)

        elif isinstance(node, BinaryOpNode):
            self._emit_binary_op(node)

        elif isinstance(node, UnaryOpNode):
            self._emit_expr(node.operand)
            if node.operator == '-':
                self.bytecode.add(Op.NEG, line=node.line, column=node.column)
            elif node.operator == 'bukan':
                self.bytecode.add(Op.NOT_OP, line=node.line, column=node.column)

        elif isinstance(node, CallNode):
            self._emit_call(node)

        elif isinstance(node, IfNode):
            # Ternary-like usage: if expr
            self._emit_if_expr(node)

        elif isinstance(node, ListNode):
            for elem in node.elements:
                self._emit_expr(elem)
            self.bytecode.add(Op.MAKE_LIST, len(node.elements), node.line, node.column)

        elif isinstance(node, TupleNode):
            for elem in node.elements:
                self._emit_expr(elem)
            self.bytecode.add(Op.MAKE_TUPLE, len(node.elements), node.line, node.column)

        elif isinstance(node, SetNode):
            for elem in node.elements:
                self._emit_expr(elem)
            self.bytecode.add(Op.MAKE_SET, len(node.elements), node.line, node.column)

        elif isinstance(node, ObjectNode):
            for k, v in node.entries.items():
                self.bytecode.add(Op.PUSH_CONST, self.bytecode.add_const(k))
                self._emit_expr(v)
            self.bytecode.add(Op.MAKE_DICT, len(node.entries), node.line, node.column)

        elif isinstance(node, ObjectAccessNode):
            self._emit_expr(node.object)
            prop_idx = self.bytecode.add_name(node.property)
            self.bytecode.add(Op.LOAD_ATTR, prop_idx, node.line, node.column)

        elif isinstance(node, IndexNode):
            self._emit_expr(node.target)
            if node.is_slice:
                self.bytecode.add(Op.PUSH_NONE)  # Placeholder
            else:
                self._emit_expr(node.index)
            self.bytecode.add(Op.INDEX_GET, line=node.line, column=node.column)

        elif isinstance(node, FStringNode):
            self._emit_fstring(node)

        elif isinstance(node, LambdaNode):
            self._emit_lambda(node)

        elif isinstance(node, NullCoalescingNode):
            self._emit_expr(node.left)
            self.bytecode.add(Op.DUP)
            self.bytecode.add(Op.PUSH_NONE)
            self.bytecode.add(Op.EQ)
            jump_idx = len(self.bytecode.instructions)
            self.bytecode.add(Op.POP_JUMP_IF_FALSE, 0)
            self.bytecode.add(Op.POP_TOP)  # pop the None
            self._emit_expr(node.right)
            self.bytecode.instructions[jump_idx].arg = len(self.bytecode.instructions)

        elif isinstance(node, TernaryNode):
            self._emit_expr(node.condition)
            jump_else = len(self.bytecode.instructions)
            self.bytecode.add(Op.POP_JUMP_IF_FALSE, 0)
            self._emit_expr(node.body)
            jump_end = len(self.bytecode.instructions)
            self.bytecode.add(Op.JUMP, 0)
            self.bytecode.instructions[jump_else].arg = len(self.bytecode.instructions)
            self._emit_expr(node.else_body)
            self.bytecode.instructions[jump_end].arg = len(self.bytecode.instructions)

        elif isinstance(node, StructInstanceNode):
            self._emit_expr(node.definition)
            for arg in node.args:
                self._emit_expr(arg)
            self.bytecode.add(Op.MAKE_INSTANCE, len(node.args), node.line, node.column)

        else:
            # Fallback: push None for unknown nodes
            self.bytecode.add(Op.PUSH_NONE, line=getattr(node, 'line', 0))

    def _emit_binary_op(self, node: BinaryOpNode):
        # Short-circuit for 'dan' / 'atau'
        if node.operator == 'dan':
            self._emit_expr(node.left)
            self.bytecode.add(Op.POP_JUMP_IF_FALSE, 0, node.line, node.column)
            self.bytecode.add(Op.POP_TOP)
            self._emit_expr(node.right)
            self.bytecode.instructions[-3].arg = len(self.bytecode.instructions)
            return
        if node.operator == 'atau':
            self._emit_expr(node.left)
            jump_right = len(self.bytecode.instructions)
            self.bytecode.add(Op.JUMP_IF_TRUE, 0, node.line, node.column)
            self.bytecode.add(Op.POP_TOP)
            self._emit_expr(node.right)
            self.bytecode.instructions[jump_right].arg = len(self.bytecode.instructions)
            return

        self._emit_expr(node.left)
        self._emit_expr(node.right)

        op_map = {
            '+': Op.ADD, '-': Op.SUB, '*': Op.MUL, '/': Op.DIV,
            '%': Op.MOD, '**': Op.POW,
            '==': Op.EQ, '!=': Op.NEQ, '>': Op.GT, '>=': Op.GTE,
            '<': Op.LT, '<=': Op.LTE, 'is': Op.IS_OP,
            'dan': Op.AND, 'atau': Op.OR,
        }
        op = op_map.get(node.operator)
        if op:
            self.bytecode.add(op, line=node.line, column=node.column)

    def _emit_call(self, node: CallNode):
        if isinstance(node.function, IdentifierNode):
            name = node.function.name
            # Check if builtin
            from brolang.interpreter.builtins import BUILTINS
            if name in BUILTINS:
                for arg in node.args:
                    self._emit_expr(arg)
                self.bytecode.add(Op.CALL_BUILTIN, (name, len(node.args)),
                               node.line, node.column)
                return

            for arg in node.args:
                self._emit_expr(arg)
            loc = self._resolve_name(name)
            if loc == 'local':
                idx = self._get_local_idx(name)
                self.bytecode.add(Op.LOAD_LOCAL, idx, node.line, node.column)
            elif loc == 'free':
                idx = self.bytecode.add_free_var(name)
                self.bytecode.add(Op.LOAD_DEREF, idx, node.line, node.column)
            else:
                idx = self.bytecode.add_name(name)
                self.bytecode.add(Op.LOAD_GLOBAL, idx, node.line, node.column)
            self.bytecode.add(Op.CALL, len(node.args), node.line, node.column)

        elif isinstance(node.function, ObjectAccessNode):
            self._emit_expr(node.function.object)
            prop_idx = self.bytecode.add_name(node.function.property)
            self.bytecode.add(Op.LOAD_METHOD, prop_idx, node.line, node.column)
            for arg in node.args:
                self._emit_expr(arg)
            self.bytecode.add(Op.CALL_METHOD, (prop_idx, len(node.args)),
                           node.line, node.column)
        else:
            # Generic call
            self._emit_expr(node.function)
            for arg in node.args:
                self._emit_expr(arg)
            self.bytecode.add(Op.CALL, len(node.args), node.line, node.column)

    # ============= Helpers =============

    def _emit_if_expr(self, node: IfNode):
        """Ternary: expression-style if."""
        self._emit_expr(node.condition)
        jump_else = len(self.bytecode.instructions)
        self.bytecode.add(Op.POP_JUMP_IF_FALSE, 0)
        for stmt in node.body:
            self._emit_stmt(stmt)
        jump_end = len(self.bytecode.instructions)
        self.bytecode.add(Op.JUMP, 0)
        self.bytecode.instructions[jump_else].arg = len(self.bytecode.instructions)
        for stmt in node.else_body:
            self._emit_stmt(stmt)
        self.bytecode.instructions[jump_end].arg = len(self.bytecode.instructions)

    def _emit_del(self, node: DelNode):
        if isinstance(node.target, IdentifierNode):
            loc = self._resolve_name(node.target.name)
            if loc == 'local':
                idx = self._get_local_idx(node.target.name)
                self.bytecode.add(Op.DEL_VAR, ('local', idx), node.line, node.column)
            else:
                idx = self.bytecode.add_name(node.target.name)
                self.bytecode.add(Op.DEL_VAR, ('global', idx), node.line, node.column)

    def _emit_assert(self, node: AssertNode):
        self._emit_expr(node.condition)
        if node.message:
            self._emit_expr(node.message)
        else:
            msg_idx = self.bytecode.add_const("Assertion gagal")
            self.bytecode.add(Op.PUSH_CONST, msg_idx)
        self.bytecode.add(Op.ASSERT, line=node.line, column=node.column)

    def _emit_raise(self, node: RaiseNode):
        if node.value:
            self._emit_expr(node.value)
        self.bytecode.add(Op.RAISE, line=node.line, column=node.column)

    def _emit_import(self, node):
        if isinstance(node, ImportNode):
            parts = '.'.join(node.parts)
            idx = self.bytecode.add_const(parts)
            self.bytecode.add(Op.IMPORT, (parts, None), node.line, node.column)
            name = node.parts[-1]
            name_idx = self.bytecode.add_name(name)
            self.bytecode.add(Op.DEFINE_GLOBAL, name_idx, node.line, node.column)
        elif isinstance(node, FromImportNode):
            parts = '.'.join(node.parts)
            for name in node.names:
                self.bytecode.add(Op.IMPORT, (parts, name), node.line, node.column)
                name_idx = self.bytecode.add_name(name)
                self.bytecode.add(Op.DEFINE_GLOBAL, name_idx, node.line, node.column)

    def _emit_enum(self, node: EnumNode):
        """Emit enum as dict."""
        entries = {}
        for i, name in enumerate(node.values):
            entries[name] = i
        idx = self.bytecode.add_const(entries)
        self.bytecode.add(Op.PUSH_CONST, idx, node.line, node.column)
        name_idx = self.bytecode.add_name(node.name)
        self.bytecode.add(Op.DEFINE_GLOBAL, name_idx, node.line, node.column)

    def _emit_struct(self, node: StructNode):
        """Emit struct as class-like construct."""
        # Simplified: treat struct as a class with automatic __init__
        methods = {}
        for method in node.methods:
            saved = self.bytecode
            saved_locals = self.locals
            saved_free = self.free_vars
            saved_depth = self.scope_depth

            self.bytecode = Bytecode()
            self.scope_depth += 1
            self.locals = []
            self.free_vars = []

            if not method.is_static:
                self._add_local('self')
            for param in method.params:
                if param == 'self' and not method.is_static:
                    continue
                self._add_local(param)

            for stmt in method.body:
                self._emit_stmt(stmt)
            self.bytecode.add(Op.PUSH_NONE)
            self.bytecode.add(Op.RETURN)

            method_bc = self.bytecode
            method_bc.finalize()
            self.bytecode = saved
            self.locals = saved_locals
            self.free_vars = saved_free
            self.scope_depth = saved_depth

            total_params = len(method.params)
            methods[method.name] = (method_bc, method.is_static, total_params)

        struct_data = (node.name, methods)
        idx = self.bytecode.add_const(struct_data)
        self.bytecode.add(Op.MAKE_CLASS, idx, node.line, node.column)
        name_idx = self.bytecode.add_name(node.name)
        self.bytecode.add(Op.DEFINE_GLOBAL, name_idx, node.line, node.column)

    def _emit_augmented_assignment(self, node: AugmentedAssignmentNode):
        name = node.target.name if isinstance(node.target, IdentifierNode) else ''
        self._emit_expr(node.target)
        self._emit_expr(node.value)
        op_map = {
            '+=': Op.AUG_ADD, '-=': Op.AUG_SUB,
            '*=': Op.AUG_MUL, '/=': Op.AUG_DIV,
        }
        op = op_map.get(node.operator)
        if op:
            self.bytecode.add(op, line=node.line, column=node.column)
        loc = self._resolve_name(name)
        if loc == 'local':
            idx = self._get_local_idx(name)
            self.bytecode.add(Op.STORE_LOCAL, idx, node.line, node.column)
        else:
            idx = self.bytecode.add_name(name)
            self.bytecode.add(Op.STORE_GLOBAL, idx, node.line, node.column)

    def _emit_try(self, node: TryNode):
        """Emit try/except."""
        push_idx = len(self.bytecode.instructions)
        self.bytecode.add(Op.TRY_PUSH, 0, node.line, node.column)

        for stmt in node.body:
            self._emit_stmt(stmt)

        jump_end = len(self.bytecode.instructions)
        self.bytecode.add(Op.JUMP, 0, node.line, node.column)

        self.bytecode.instructions[push_idx].arg = len(self.bytecode.instructions)
        self.bytecode.add(Op.TRY_POP)

        # Handle catch
        for handler in node.handlers:
            if handler.name:
                self._add_local(handler.name)
                var_idx = self._get_local_idx(handler.name)
                self.bytecode.add(Op.STORE_LOCAL, var_idx, node.line, node.column)

            for stmt in handler.body:
                self._emit_stmt(stmt)

        self.bytecode.instructions[jump_end].arg = len(self.bytecode.instructions)

    def _emit_fstring(self, node: FStringNode):
        """Emit f-string as string concatenation."""
        parts = []
        for ptype, pval in node.parts:
            if ptype == 'literal':
                idx = self.bytecode.add_const(pval)
                self.bytecode.add(Op.PUSH_CONST, idx, node.line, node.column)
                parts.append(('const', None))
            elif ptype == 'expr':
                self._emit_expr(pval)
                parts.append(('expr', None))

        # Concatenate all parts
        if len(parts) > 1:
            # Build string by converting all to string and joining
            self.bytecode.add(Op.FSTRING, len(parts), node.line, node.column)

    def _emit_lambda(self, node: LambdaNode):
        """Emit lambda as function."""
        saved = self.bytecode
        saved_locals = self.locals
        saved_free = self.free_vars
        saved_depth = self.scope_depth

        self.bytecode = Bytecode()
        self.scope_depth += 1
        self.locals = []
        self.free_vars = []

        for param in node.params:
            self._add_local(param)

        self._emit_expr(node.body)
        self.bytecode.add(Op.RETURN)

        func_bc = self.bytecode
        self.bytecode = saved
        self.locals = saved_locals
        self.free_vars = saved_free
        self.scope_depth = saved_depth

        const_idx = self.bytecode.add_const(func_bc)
        param_count = len(node.params)
        self.bytecode.add(Op.CLOSURE, (const_idx, param_count, False),
                         node.line, node.column)

    # ============= Scope Management =============

    def _add_local(self, name: str) -> int:
        self.locals.append((name, self.scope_depth))
        return len(self.locals) - 1

    def _get_local_idx(self, name: str) -> int:
        for i in range(len(self.locals) - 1, -1, -1):
            if self.locals[i][0] == name:
                return i
        return -1

    def _resolve_name(self, name: str) -> str:
        """Resolve where a name lives: 'local', 'free', or 'global'."""
        # Check locals (most recent first)
        for i in range(len(self.locals) - 1, -1, -1):
            if self.locals[i][0] == name:
                return 'local'
        # Check free vars
        if name in self.free_vars:
            return 'free'
        return 'global'

    def _ensure_local(self, name: str):
        """Ensure a local exists, create if needed."""
        if self._get_local_idx(name) == -1:
            self._add_local(name)

    def _remove_locals(self, count: int):
        """Remove last N locals."""
        for _ in range(count):
            if self.locals:
                self.locals.pop()


