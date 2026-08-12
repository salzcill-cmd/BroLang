"""
Optimizer BroLang
=================

Optimizer melakukan optimasi pada AST sebelum eksekusi atau kompilasi.
Optimasi yang diimplementasikan:

1. Constant Folding:
   2 + 3 → 5
   "a" + "b" → "ab"
   bukan benar → salah

2. Dead Code Elimination:
   Hapus kode yang tidak akan pernah dieksekusi.

3. Simplifikasi Expression:
   -(-x) → x
   x + 0 → x
   x * 1 → x
   x * 0 → 0

Pipeline:
    AST → Semantic Analyzer → [Optimizer] → Optimized AST → Interpreter
"""

from typing import Optional, Any, List
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
    ListNode, IndexNode, ObjectNode, ObjectAccessNode,
    PrintNode, InputNode,
    LambdaNode, ComprehensionNode, FStringNode,
    EnumNode, StructNode, StructInstanceNode,
    MatchNode, WildcardNode,
    AugmentedAssignmentNode, TernaryNode, RaiseNode,
    GlobalNode, NonlocalNode,
    PassNode, DelNode, AssertNode,
    TupleNode, SetNode, DictComprehensionNode,
    SpreadNode,
)


class Optimizer(ASTVisitor):
    """Optimizer untuk AST BroLang.

    Melakukan berbagai optimasi pada AST untuk meningkatkan
    performa eksekusi dan menghasilkan kode yang lebih efisien.
    """

    def __init__(self, optimization_level: int = 1):
        self.optimization_level = optimization_level
        self.optimized_count = 0

    def optimize(self, node: ASTNode) -> ASTNode:
        """Menjalankan optimasi pada AST.

        Args:
            node: Root AST node

        Returns:
            ASTNode: Optimized AST
        """
        return self.visit(node)

    def visit(self, node: ASTNode) -> Any:
        """Visit node dengan optimasi."""
        method_name = f"visit_{node.__class__.__name__}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node: ASTNode) -> ASTNode:
        """Default: kunjungi children."""
        return node

    # ============= Constant Folding =============

    def visit_BinaryOpNode(self, node: BinaryOpNode) -> ASTNode:
        """Optimasi operasi biner dengan constant folding."""
        left = self.visit(node.left)
        right = self.visit(node.right)

        # Coba constant folding jika kedua operand adalah literal
        if isinstance(left, (NumberNode, DecimalNode, StringNode, BooleanNode)) and \
           isinstance(right, (NumberNode, DecimalNode, StringNode, BooleanNode)):
            folded = self._try_fold(node.operator, left, right)
            if folded is not None:
                self.optimized_count += 1
                return folded

        # Simplifikasi aljabar
        simplified = self._try_simplify(node.operator, left, right)
        if simplified is not None:
            self.optimized_count += 1
            return simplified

        return BinaryOpNode(left=left, operator=node.operator, right=right,
                            line=node.line, column=node.column)

    def _try_fold(self, operator: str, left: ASTNode, right: ASTNode) -> Optional[ASTNode]:
        """Mencoba melakukan constant folding."""
        try:
            if operator == "+":
                if isinstance(left, NumberNode) and isinstance(right, NumberNode):
                    return NumberNode(value=left.value + right.value, line=left.line, column=left.column)
                if isinstance(left, DecimalNode) and isinstance(right, DecimalNode):
                    return DecimalNode(value=left.value + right.value, line=left.line, column=left.column)
                if isinstance(left, (NumberNode, DecimalNode)) and isinstance(right, (NumberNode, DecimalNode)):
                    return DecimalNode(value=float(left.value) + float(right.value))
                if isinstance(left, StringNode) and isinstance(right, StringNode):
                    return StringNode(value=left.value + right.value, line=left.line, column=left.column)
                if isinstance(left, StringNode):
                    return StringNode(value=left.value + str(right.value), line=left.line, column=left.column)

            elif operator == "-":
                if isinstance(left, NumberNode) and isinstance(right, NumberNode):
                    return NumberNode(value=left.value - right.value, line=left.line, column=left.column)
                if isinstance(left, DecimalNode) and isinstance(right, DecimalNode):
                    return DecimalNode(value=left.value - right.value, line=left.line, column=left.column)
                if isinstance(left, (NumberNode, DecimalNode)) and isinstance(right, (NumberNode, DecimalNode)):
                    return DecimalNode(value=float(left.value) - float(right.value))

            elif operator == "*":
                if isinstance(left, NumberNode) and isinstance(right, NumberNode):
                    return NumberNode(value=left.value * right.value, line=left.line, column=left.column)
                if isinstance(left, DecimalNode) and isinstance(right, DecimalNode):
                    return DecimalNode(value=left.value * right.value, line=left.line, column=left.column)
                if isinstance(left, (NumberNode, DecimalNode)) and isinstance(right, (NumberNode, DecimalNode)):
                    return DecimalNode(value=float(left.value) * float(right.value))

            elif operator == "/":
                if isinstance(left, NumberNode) and isinstance(right, NumberNode):
                    if right.value != 0:
                        return DecimalNode(value=left.value / right.value, line=left.line, column=left.column)
                if isinstance(left, DecimalNode) and isinstance(right, DecimalNode):
                    if right.value != 0:
                        return DecimalNode(value=left.value / right.value, line=left.line, column=left.column)

            elif operator == "//":  # v6.8: floor division
                if isinstance(left, NumberNode) and isinstance(right, NumberNode):
                    if right.value != 0:
                        return NumberNode(value=left.value // right.value, line=left.line, column=left.column)
                if isinstance(left, DecimalNode) and isinstance(right, DecimalNode):
                    if right.value != 0:
                        return DecimalNode(value=left.value // right.value, line=left.line, column=left.column)

            elif operator == "%":
                if isinstance(left, NumberNode) and isinstance(right, NumberNode):
                    if right.value != 0:
                        return NumberNode(value=left.value % right.value, line=left.line, column=left.column)

            elif operator == "**":
                if isinstance(left, NumberNode) and isinstance(right, NumberNode):
                    return NumberNode(value=left.value ** right.value, line=left.line, column=left.column)

            elif operator == "==":
                if isinstance(left, (NumberNode, DecimalNode, StringNode, BooleanNode)) and \
                   isinstance(right, (NumberNode, DecimalNode, StringNode, BooleanNode)):
                    return BooleanNode(value=left.value == right.value, line=left.line, column=left.column)

            elif operator == "!=":
                if isinstance(left, (NumberNode, DecimalNode, StringNode, BooleanNode)) and \
                   isinstance(right, (NumberNode, DecimalNode, StringNode, BooleanNode)):
                    return BooleanNode(value=left.value != right.value, line=left.line, column=left.column)

            elif operator == ">":
                if isinstance(left, (NumberNode, DecimalNode)) and isinstance(right, (NumberNode, DecimalNode)):
                    return BooleanNode(value=left.value > right.value)

            elif operator == "<":
                if isinstance(left, (NumberNode, DecimalNode)) and isinstance(right, (NumberNode, DecimalNode)):
                    return BooleanNode(value=left.value < right.value)

            elif operator == ">=":
                if isinstance(left, (NumberNode, DecimalNode)) and isinstance(right, (NumberNode, DecimalNode)):
                    return BooleanNode(value=left.value >= right.value)

            elif operator == "<=":
                if isinstance(left, (NumberNode, DecimalNode)) and isinstance(right, (NumberNode, DecimalNode)):
                    return BooleanNode(value=left.value <= right.value)

            elif operator == "dan":
                if isinstance(left, BooleanNode) and isinstance(right, BooleanNode):
                    return BooleanNode(value=left.value and right.value)

            elif operator == "atau":
                if isinstance(left, BooleanNode) and isinstance(right, BooleanNode):
                    return BooleanNode(value=left.value or right.value)

        except (TypeError, ZeroDivisionError):
            pass

        return None

    def _try_simplify(self, operator: str, left: ASTNode, right: ASTNode) -> Optional[ASTNode]:
        """Mencoba simplifikasi aljabar."""
        # x + 0 → x
        if operator == "+" and isinstance(right, (NumberNode, DecimalNode)) and right.value == 0:
            return left
        # 0 + x → x
        if operator == "+" and isinstance(left, (NumberNode, DecimalNode)) and left.value == 0:
            return right
        # x * 1 → x
        if operator == "*" and isinstance(right, (NumberNode, DecimalNode)) and right.value == 1:
            return left
        # 1 * x → x
        if operator == "*" and isinstance(left, (NumberNode, DecimalNode)) and left.value == 1:
            return right
        # x * 0 → 0
        if operator == "*" and isinstance(right, (NumberNode, DecimalNode)) and right.value == 0:
            return NumberNode(value=0)
        # 0 * x → 0
        if operator == "*" and isinstance(left, (NumberNode, DecimalNode)) and left.value == 0:
            return NumberNode(value=0)
        # x - 0 → x
        if operator == "-" and isinstance(right, (NumberNode, DecimalNode)) and right.value == 0:
            return left
        # x / 1 → x
        if operator == "/" and isinstance(right, (NumberNode, DecimalNode)) and right.value == 1:
            return left
        # x // 1 → x (v6.8)
        if operator == "//" and isinstance(right, (NumberNode, DecimalNode)) and right.value == 1:
            return left

        return None

    def visit_UnaryOpNode(self, node: UnaryOpNode) -> ASTNode:
        """Optimasi operasi unary."""
        operand = self.visit(node.operand)

        # -(-x) → x
        if node.operator == "-" and isinstance(operand, UnaryOpNode) and operand.operator == "-":
            self.optimized_count += 1
            return operand.operand

        # -0 → 0
        if node.operator == "-" and isinstance(operand, NumberNode) and operand.value == 0:
            return operand

        # bukan bukan x → x
        if node.operator == "bukan" and isinstance(operand, UnaryOpNode) and operand.operator == "bukan":
            self.optimized_count += 1
            return operand.operand

        # Constant fold: -5, bukan(true)
        if isinstance(operand, (NumberNode, DecimalNode, BooleanNode)):
            if node.operator == "-":
                if isinstance(operand, NumberNode):
                    return NumberNode(value=-operand.value)
                if isinstance(operand, DecimalNode):
                    return DecimalNode(value=-operand.value)
            if node.operator == "bukan" and isinstance(operand, BooleanNode):
                return BooleanNode(value=not operand.value)

        return UnaryOpNode(operator=node.operator, operand=operand,
                           line=node.line, column=node.column)

    def visit_IfNode(self, node: IfNode) -> ASTNode:
        """Optimasi if statement."""
        condition = self.visit(node.condition)
        body = [self.visit(stmt) for stmt in node.body]

        elif_conditions = [self.visit(ec) for ec in node.elif_conditions]
        elif_bodies = [[self.visit(stmt) for stmt in eb] for eb in node.elif_bodies]
        else_body = [self.visit(stmt) for stmt in node.else_body]

        # If condition is constant
        if isinstance(condition, BooleanNode):
            self.optimized_count += 1
            if condition.value:
                # Always execute body
                result = []
                for stmt in body:
                    result.append(stmt)
                # Create a block node or just return the first statement
                if len(result) == 1:
                    return result[0]
                return ProgramNode(statements=result)
            else:
                # Check elif/else
                for i, ec in enumerate(elif_conditions):
                    if isinstance(ec, BooleanNode) and ec.value:
                        result = []
                        for stmt in elif_bodies[i]:
                            result.append(stmt)
                        if len(result) == 1:
                            return result[0]
                        return ProgramNode(statements=result)
                # Execute else
                result = []
                for stmt in else_body:
                    result.append(stmt)
                if len(result) == 1:
                    return result[0]
                return ProgramNode(statements=result)

        return IfNode(
            condition=condition, body=body,
            else_body=else_body,
            elif_conditions=elif_conditions,
            elif_bodies=elif_bodies,
            line=node.line, column=node.column,
        )

    def visit_WhileNode(self, node: WhileNode) -> ASTNode:
        """Optimasi while loop."""
        condition = self.visit(node.condition)
        body = [self.visit(stmt) for stmt in node.body]

        # while false → dead code
        if isinstance(condition, BooleanNode) and not condition.value:
            self.optimized_count += 1
            return ProgramNode(statements=[])

        # Optimize else body too
        else_body = None
        if node.else_body:
            else_body = [self.visit(stmt) for stmt in node.else_body]

        return WhileNode(condition=condition, body=body, else_body=else_body,
                         line=node.line, column=node.column)

    def visit_ForNode(self, node: ForNode) -> ASTNode:
        """Optimasi for loop."""
        iterable = self.visit(node.iterable)
        body = [self.visit(stmt) for stmt in node.body]

        # Optimize else body too
        else_body = None
        if node.else_body:
            else_body = [self.visit(stmt) for stmt in node.else_body]

        return ForNode(variable=node.variable, iterable=iterable,
                       body=body, else_body=else_body,
                       line=node.line, column=node.column)

    def visit_DoUntilNode(self, node: DoUntilNode) -> ASTNode:
        """Optimasi do-until loop (v6.5)."""
        body = [self.visit(stmt) for stmt in node.body]
        condition = self.visit(node.condition)
        return DoUntilNode(body=body, condition=condition,
                           line=node.line, column=node.column)

    def visit_RangeForNode(self, node: RangeForNode) -> ASTNode:
        """Optimasi range for loop (v6.5)."""
        start = self.visit(node.start)
        end = self.visit(node.end)
        step = self.visit(node.step) if node.step else None
        body = [self.visit(stmt) for stmt in node.body]
        else_body = None
        if node.else_body:
            else_body = [self.visit(stmt) for stmt in node.else_body]
        return RangeForNode(variable=node.variable, start=start, end=end,
                            step=step, body=body, else_body=else_body,
                            line=node.line, column=node.column)

    def visit_ProgramNode(self, node: ProgramNode) -> ProgramNode:
        """Optimasi program."""
        statements = []
        for stmt in node.statements:
            optimized = self.visit(stmt)
            if isinstance(optimized, ProgramNode):
                statements.extend(optimized.statements)
            elif optimized is not None:
                statements.append(optimized)
        return ProgramNode(statements=statements, name=node.name)

    def visit_AssignmentNode(self, node: AssignmentNode) -> AssignmentNode:
        value = self.visit(node.value) if node.value else None
        return AssignmentNode(target=node.target, value=value if value else node.value,
                              is_declaration=node.is_declaration,
                              type_annotation=node.type_annotation,
                              is_const=node.is_const,
                              line=node.line, column=node.column)

    def visit_FunctionNode(self, node: FunctionNode) -> FunctionNode:
        body = [self.visit(stmt) for stmt in node.body]
        return FunctionNode(
            name=node.name, params=node.params, defaults=node.defaults,
            body=body, is_static=node.is_static,
            param_types=node.param_types, return_type=node.return_type,
            rest_param=node.rest_param,
            line=node.line, column=node.column,
        )

    def visit_ReturnNode(self, node: ReturnNode) -> ReturnNode:
        value = self.visit(node.value) if node.value else None
        guard = None
        if getattr(node, "guard", None) is not None:
            guard = self.visit(node.guard)
        return ReturnNode(value=value if value else node.value, guard=guard,
                          line=node.line, column=node.column)

    def visit_PrintNode(self, node: PrintNode) -> PrintNode:
        expr = self.visit(node.expression)
        args = [self.visit(arg) for arg in node.args]
        return PrintNode(expression=expr, args=args, line=node.line, column=node.column)

    def visit_ListNode(self, node: ListNode) -> ListNode:
        elements = [self.visit(elem) for elem in node.elements]
        return ListNode(elements=elements, line=node.line, column=node.column)

    def visit_TupleNode(self, node: TupleNode) -> TupleNode:
        elements = [self.visit(elem) for elem in node.elements]
        return TupleNode(elements=elements, line=node.line, column=node.column)

    def visit_SetNode(self, node: SetNode) -> SetNode:
        elements = [self.visit(elem) for elem in node.elements]
        return SetNode(elements=elements, line=node.line, column=node.column)

    def visit_ObjectNode(self, node: ObjectNode) -> ObjectNode:
        entries = {k: self.visit(v) for k, v in node.entries.items()}
        return ObjectNode(entries=entries, line=node.line, column=node.column)

    def visit_PassNode(self, node: PassNode) -> PassNode:
        return node

    def visit_DelNode(self, node: DelNode) -> DelNode:
        return DelNode(target=node.target, line=node.line, column=node.column)

    def visit_AssertNode(self, node: AssertNode) -> AssertNode:
        condition = self.visit(node.condition)
        message = self.visit(node.message) if node.message else None
        return AssertNode(condition=condition, message=message,
                          line=node.line, column=node.column)

    def visit_IndexNode(self, node: IndexNode) -> IndexNode:
        target = self.visit(node.target)
        index = self.visit(node.index)
        slice_start = self.visit(node.slice_start) if node.slice_start else None
        slice_stop = self.visit(node.slice_stop) if node.slice_stop else None
        slice_step = self.visit(node.slice_step) if node.slice_step else None
        return IndexNode(target=target, index=index,
                         slice_start=slice_start, slice_stop=slice_stop, slice_step=slice_step,
                         is_slice=node.is_slice, line=node.line, column=node.column)

    def visit_DictComprehensionNode(self, node: DictComprehensionNode) -> DictComprehensionNode:
        key_expr = self.visit(node.key_expr)
        value_expr = self.visit(node.value_expr)
        iterable = self.visit(node.iterable)
        condition = self.visit(node.condition) if node.condition else None
        return DictComprehensionNode(key_expr=key_expr, value_expr=value_expr,
                                     key_var=node.key_var, value_var=node.value_var,
                                     iterable=iterable, condition=condition,
                                     line=node.line, column=node.column)

    def visit_StringNode(self, node: StringNode) -> StringNode:
        return node

    def visit_NumberNode(self, node: NumberNode) -> NumberNode:
        return node

    def visit_DecimalNode(self, node: DecimalNode) -> DecimalNode:
        return node

    def visit_BooleanNode(self, node: BooleanNode) -> BooleanNode:
        return node

    def visit_KosongNode(self, node: KosongNode) -> KosongNode:
        return node

    def visit_IdentifierNode(self, node: IdentifierNode) -> IdentifierNode:
        return node

    def visit_CallNode(self, node: CallNode) -> CallNode:
        func = self.visit(node.function)
        args = [self.visit(arg) for arg in node.args]
        kwargs = [(name, self.visit(val)) for name, val in node.kwargs]
        return CallNode(function=func, args=args, kwargs=kwargs,
                        is_method=node.is_method,
                        object_name=node.object_name, line=node.line, column=node.column)

    def visit_SpreadNode(self, node: SpreadNode) -> SpreadNode:
        """Optimasi spread operator (v6.7)."""
        value = self.visit(node.value)
        return SpreadNode(value=value, line=node.line, column=node.column)
