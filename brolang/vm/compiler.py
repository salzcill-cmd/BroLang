"""
Bytecode Compiler untuk BroLang
================================

Mengkonversi AST BroLang menjadi bytecode yang bisa dijalankan oleh VM.
"""

from brolang.ast.nodes import (
    AssertNode,
    AssignmentNode,
    ASTNode,
    AugmentedAssignmentNode,
    BinaryOpNode,
    BooleanNode,
    BreakNode,
    CallNode,
    ClassNode,
    ComprehensionNode,
    ContinueNode,
    DecimalNode,
    DelNode,
    DestructuringAssignmentNode,
    DictComprehensionNode,
    DoUntilNode,
    EnumNode,
    ForEachNode,
    ForNode,
    FromImportNode,
    RangeForNode,
    FStringNode,
    FunctionNode,
    GlobalNode,
    IdentifierNode,
    IfNode,
    ImportNode,
    IndexNode,
    InputNode,
    KosongNode,
    LambdaNode,
    ListNode,
    MatchNode,
    NonlocalNode,
    NullCoalescingNode,
    NumberNode,
    ObjectAccessNode,
    ObjectNode,
    OptionalChainingNode,
    PassNode,
    PipelineNode,
    PrintNode,
    ProgramNode,
    RaiseNode,
    ReturnNode,
    SetNode,
    StringNode,
    StructInstanceNode,
    StructNode,
    TernaryNode,
    TryNode,
    TupleNode,
    UnaryOpNode,
    VariableNode,
    WhileNode,
    WildcardNode,
    SpreadNode,
    MapNode, FilterNode, ReduceNode,
)
from brolang.vm.opcodes import Bytecode, Instruction, Op

# ============= Peephole Optimizer =============

# Operasi biner yang aman untuk constant folding (menghasilkan nilai deterministik,
# tidak punya efek samping, dan tidak bergantung pada state runtime).
_FOLDABLE_BINARY = {
    Op.ADD,
    Op.SUB,
    Op.MUL,
    Op.DIV,
    Op.MOD,
    Op.POW,
    Op.EQ,
    Op.NEQ,
    Op.GT,
    Op.GTE,
    Op.LT,
    Op.LTE,
}

_JUMP_OPS = {
    Op.JUMP,
    Op.JUMP_IF_FALSE,
    Op.JUMP_IF_TRUE,
    Op.POP_JUMP_IF_FALSE,
    Op.FOR_ITER,
    Op.TRY_PUSH,
}


def _coba_fold(a, b, op):
    """Coba hitung hasil fold konstanta (a OP b).

    Returns:
        (True, hasil) bila berhasil, (False, None) bila tidak aman/foldable.
    """
    if op in (Op.EQ, Op.NEQ, Op.GT, Op.GTE, Op.LT, Op.LTE):
        try:
            if op == Op.EQ:
                return (True, a == b)
            if op == Op.NEQ:
                return (True, a != b)
            if op == Op.GT:
                return (True, a > b)
            if op == Op.GTE:
                return (True, a >= b)
            if op == Op.LT:
                return (True, a < b)
            if op == Op.LTE:
                return (True, a <= b)
        except Exception:
            return (False, None)
    # Aritmatika: hanya untuk angka; string concat khusus ADD
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        if op == Op.ADD and isinstance(a, str) and isinstance(b, str):
            return (True, a + b)
        return (False, None)
    try:
        if op == Op.ADD:
            r = a + b
        elif op == Op.SUB:
            r = a - b
        elif op == Op.MUL:
            r = a * b
        elif op == Op.DIV:
            r = a / b
        elif op == Op.MOD:
            r = a % b
        elif op == Op.POW:
            # Guard eksponen besar: folding eager `2 ** 1000000` bisa
            # menghabiskan CPU/memori saat kompilasi — biarkan runtime
            # bila eksponen di luar batas aman.
            if isinstance(b, (int, float)) and abs(b) > 64:
                return (False, None)
            r = a**b
        else:
            return (False, None)
    except Exception:
        return (False, None)
    return (True, r)


def apply_peephole(bytecode: Bytecode) -> None:
    """Peephole optimization untuk bytecode.

    1. Constant folding: `PUSH_CONST a; PUSH_CONST b; ADD` -> `PUSH_CONST (a+b)`
       (juga NEG/NOT pada konstanta).
    2. Hapus instruksi NOP.
    3. Remap semua target jump karena index instruksi berubah.

    Amannya: hanya melipat konstanta murni (tidak mengeksekusi kode user),
    dan target jump yang hilang dipertahankan via mapping.get(arg, arg).
    """
    instrs = bytecode.instructions
    if not instrs:
        return

    mapping = {}  # index lama -> index baru
    kept = []
    i = 0
    n = len(instrs)

    while i < n:
        ins = instrs[i]

        # Pola: PUSH_CONST a; PUSH_CONST b; OP -> PUSH_CONST (a OP b)
        if (
            i + 2 < n
            and ins.op == Op.PUSH_CONST
            and instrs[i + 1].op == Op.PUSH_CONST
            and instrs[i + 2].op in _FOLDABLE_BINARY
        ):
            a = bytecode.constants[ins.arg]
            b = bytecode.constants[instrs[i + 1].arg]
            ok, result = _coba_fold(a, b, instrs[i + 2].op)
            if ok:
                new_ins = Instruction(
                    Op.PUSH_CONST, bytecode.add_const(result), line=ins.line, column=ins.column
                )
                mapping[i] = len(kept)
                kept.append(new_ins)
                i += 3
                continue

        # Pola: PUSH_CONST x; NEG -> PUSH_CONST (-x)
        if i + 1 < n and ins.op == Op.PUSH_CONST and instrs[i + 1].op == Op.NEG:
            v = bytecode.constants[ins.arg]
            if isinstance(v, (int, float)):
                new_ins = Instruction(
                    Op.PUSH_CONST, bytecode.add_const(-v), line=ins.line, column=ins.column
                )
                mapping[i] = len(kept)
                kept.append(new_ins)
                i += 2
                continue

        # Pola: PUSH_TRUE/PUSH_FALSE; NOT_OP -> PUSH_FALSE/PUSH_TRUE
        if i + 1 < n and ins.op in (Op.PUSH_TRUE, Op.PUSH_FALSE) and instrs[i + 1].op == Op.NOT_OP:
            new_ins = Instruction(
                Op.PUSH_FALSE if ins.op == Op.PUSH_TRUE else Op.PUSH_TRUE,
                line=ins.line,
                column=ins.column,
            )
            mapping[i] = len(kept)
            kept.append(new_ins)
            i += 2
            continue

        if ins.op == Op.NOP:
            i += 1
            continue

        mapping[i] = len(kept)
        kept.append(ins)
        i += 1

    # Remap target jump
    for ins in kept:
        if ins.op in _JUMP_OPS and isinstance(ins.arg, int):
            ins.arg = mapping.get(ins.arg, ins.arg)

    bytecode.instructions = kept


class Compiler:
    """Kompilasi AST ke bytecode."""

    def __init__(self):
        self.bytecode = Bytecode()
        self.scope_depth = 0
        self.locals = []  # [(name, scope_depth), ...]
        self.free_vars = []  # Closure variable names
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
        apply_peephole(self.bytecode)
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
        elif isinstance(node, DoUntilNode):
            self._emit_do_until(node)
        elif isinstance(node, ForNode):
            self._emit_for(node)
        elif isinstance(node, RangeForNode):
            self._emit_range_for(node)
        elif isinstance(node, ForEachNode):
            self._emit_for_each(node)
        elif isinstance(node, PrintNode):
            self._emit_print(node)
        elif isinstance(node, BreakNode):
            if getattr(node, "guard", None) is not None:
                # hentikan jika x -> if x: hentikan (guard clause v6.8)
                self._emit_if(IfNode(
                    condition=node.guard,
                    body=[BreakNode(line=node.line, column=node.column)],
                    else_body=[], elif_conditions=[], elif_bodies=[],
                    line=node.line, column=node.column,
                ))
            else:
                self.bytecode.add(Op.JUMP, ("BREAK",), node.line, node.column)
        elif isinstance(node, ContinueNode):
            if getattr(node, "guard", None) is not None:
                # lanjutkan jika x -> if x: lanjutkan (guard clause v6.8)
                self._emit_if(IfNode(
                    condition=node.guard,
                    body=[ContinueNode(line=node.line, column=node.column)],
                    else_body=[], elif_conditions=[], elif_bodies=[],
                    line=node.line, column=node.column,
                ))
            else:
                self.bytecode.add(Op.JUMP, ("CONTINUE",), node.line, node.column)
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
        elif isinstance(node, DestructuringAssignmentNode):
            self._emit_destructuring(node)
        else:
            # Expression statement — evaluate and pop
            self._emit_expr(node)
            self.bytecode.add(Op.POP_TOP, line=getattr(node, "line", 0))

    # ============= Assignment =============

    def _emit_assignment(self, node: AssignmentNode):
        """`buat x = v` / `x = v` / `obj.atribut = v` / `lst[i] = v`.

        Catatan: untuk target atribut/index, value di-eval **sekali** lalu
        dibuang dari stack setelah store — sebelumnya value di-emit dua kali
        (di sini + di _get_assign_name) dan sisa STORE_ATTR menumpuk di
        stack, merusak FOR_ITER/loop di sekitar assignment (regresi v6.7).
        """
        if isinstance(node.target, ObjectAccessNode):
            self._emit_expr(node.target.object)
            self._emit_expr(node.value)
            prop = self.bytecode.add_name(node.target.property)
            self.bytecode.add(Op.STORE_ATTR, prop, node.line, node.column)
            # STORE_ATTR mengembalikan val — buang agar stack bersih
            self.bytecode.add(Op.POP_TOP, line=node.line, column=node.column)
            return
        if isinstance(node.target, IndexNode):
            self._emit_expr(node.target.target)
            self._emit_expr(node.target.index)
            self._emit_expr(node.value)
            self.bytecode.add(Op.INDEX_SET, line=node.line, column=node.column)
            self.bytecode.add(Op.POP_TOP, line=node.line, column=node.column)
            return

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
            if loc == "local":
                idx = self._get_local_idx(name)
                self.bytecode.add(Op.STORE_LOCAL, idx, node.line, node.column)
            elif loc == "free":
                idx = self.bytecode.add_free_var(name)
                self.bytecode.add(Op.STORE_DEREF, idx, node.line, node.column)
            else:
                idx = self.bytecode.add_name(name)
                self.bytecode.add(Op.STORE_GLOBAL, idx, node.line, node.column)

    def _get_assign_name(self, node: AssignmentNode) -> str:
        if isinstance(node.target, IdentifierNode):
            return node.target.name
        return ""

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

        # Parameters become locals (rest param disimpan di slot terakhir
        # setelah param biasa — indeksnya harus sama dengan rest_pos).
        for param in node.params:
            self._add_local(param)
        if node.rest_param:
            self._add_local(node.rest_param)

        # Compile body
        for stmt in node.body:
            self._emit_stmt(stmt)
        self.bytecode.add(Op.PUSH_NONE)
        self.bytecode.add(Op.RETURN)

        # Capture free vars from enclosing scope
        captured_free = list(self.free_vars)

        func_bytecode = self.bytecode
        apply_peephole(func_bytecode)
        func_bytecode.finalize()

        # Restore state
        self.bytecode = saved
        self.locals = saved_locals
        self.free_vars = saved_free
        self.scope_depth = saved_depth

        # Emit closure in parent scope
        const_idx = self.bytecode.add_const(func_bytecode)
        param_count = len(node.params) + (1 if node.rest_param else 0)
        rest_pos = len(node.params) if node.rest_param else -1
        has_defaults = len(node.defaults) > 0 and any(d is not None for d in node.defaults)

        # Create closure instruction
        self.bytecode.add(
            Op.CLOSURE, (const_idx, param_count, has_defaults, rest_pos),
            node.line, node.column,
        )

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

    def _compile_methods(self, method_list) -> dict:
        """Kompilasi daftar method menjadi dict {nama: (bc, is_static, params)}.

        Setiap body method di-peephole optimize sebelum di-finalize.
        """
        methods = {}
        for method in method_list:
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
                self._add_local("self")
            for param in method.params:
                if param == "self" and not method.is_static:
                    continue
                self._add_local(param)
            rest_name = getattr(method, "rest_param", None)
            if rest_name:
                self._add_local(rest_name)

            # Snapshot total_params & rest_pos SEGERA setelah parameter
            # ditambahkan — body method bisa mendeklarasikan local (`buat x`)
            # yang menambah len(self.locals) dan mengubah hasil _get_local_idx
            # (index paling baru), sehingga snapshot sebelum compile body
            # memastikan nilai ini selalu = slot parameter yang sebenarnya.
            total_params = len(self.locals)
            rest_pos = self._get_local_idx(rest_name) if rest_name else -1

            for stmt in method.body:
                self._emit_stmt(stmt)
            self.bytecode.add(Op.PUSH_NONE)
            self.bytecode.add(Op.RETURN)

            method_bc = self.bytecode
            apply_peephole(method_bc)
            method_bc.finalize()

            self.bytecode = saved
            self.locals = saved_locals
            self.free_vars = saved_free
            self.scope_depth = saved_depth

            methods[method.name] = (method_bc, method.is_static, total_params, rest_pos)
        return methods

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
        methods = self._compile_methods(node.methods)

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

        break_idxs = []
        for stmt in node.body:
            self._emit_stmt(stmt)
            # Check for break/continue markers (v6.8: break bisa ber-guard,
            # jadi body tetap dikompilasi sampai selesai; marker di-patch di akhir)
            last = self.bytecode.instructions[-1]
            if last.op == Op.JUMP and isinstance(last.arg, tuple):
                if last.arg[0] == "BREAK":
                    break_idxs.append(len(self.bytecode.instructions) - 1)
                elif last.arg[0] == "CONTINUE":
                    self.bytecode.instructions[-1] = Instruction(
                        Op.JUMP, loop_start, last.line, last.column
                    )

        self.bytecode.add(Op.JUMP, loop_start, node.line, node.column)
        loop_end = len(self.bytecode.instructions)
        self.bytecode.instructions[exit_jump_idx].arg = loop_end
        for idx in break_idxs:
            brk = self.bytecode.instructions[idx]
            self.bytecode.instructions[idx] = Instruction(
                Op.JUMP, loop_end, brk.line, brk.column
            )

    def _emit_do_until(self, node: DoUntilNode):
        """ulangi ... sampai kondisi -> body dulu, cek kondisi di akhir (v6.5).

        Body dijalankan minimal sekali. Loop berhenti saat kondisi TRUE
        (POP_JUMP_IF_FALSE kembali ke awal = ulangi selama kondisi FALSE).
        BREAK dilompatkan ke akhir loop (melewati pengecekan kondisi)
        supaya tidak berisiko infinite loop saat kondisi masih FALSE.
        LANJUTKAN dilompatkan ke pengecekan kondisi (bawah body) — karena
        kondisi do-until dicek SETELAH body, continue tidak boleh balik ke
        awal body (loop_start) seperti di while.
        """
        loop_start = len(self.bytecode.instructions)
        break_idxs = []
        continue_idxs = []

        for stmt in node.body:
            self._emit_stmt(stmt)
            # Check for break/continue markers
            last = self.bytecode.instructions[-1]
            if last.op == Op.JUMP and isinstance(last.arg, tuple):
                if last.arg[0] == "BREAK":
                    break_idxs.append(len(self.bytecode.instructions) - 1)
                elif last.arg[0] == "CONTINUE":
                    continue_idxs.append(len(self.bytecode.instructions) - 1)

        # LANJUTKAN -> cek kondisi (posisi sebelum evaluasi kondisi)
        cond_start = len(self.bytecode.instructions)
        for idx in continue_idxs:
            cont = self.bytecode.instructions[idx]
            self.bytecode.instructions[idx] = Instruction(
                Op.JUMP, cond_start, cont.line, cont.column
            )

        self._emit_expr(node.condition)
        self.bytecode.add(Op.POP_JUMP_IF_FALSE, loop_start, node.line, node.column)

        # Patch semua break jump ke akhir loop (lewat kondisi + pengecekan)
        if break_idxs:
            loop_end = len(self.bytecode.instructions)
            for idx in break_idxs:
                brk = self.bytecode.instructions[idx]
                self.bytecode.instructions[idx] = Instruction(
                    Op.JUMP, loop_end, brk.line, brk.column
                )

    def _emit_for(self, node: ForNode):
        """Emit for loop."""
        self._emit_expr(node.iterable)
        self.bytecode.add(Op.GET_ITER, line=node.line, column=node.column)

        loop_start = len(self.bytecode.instructions)

        var_name = node.variable
        body_jump_idx = len(self.bytecode.instructions)
        self.bytecode.add(Op.FOR_ITER, 0, node.line, node.column)

        # Store the loop variable
        self._ensure_local(var_name)
        var_idx = self._get_local_idx(var_name)
        self.bytecode.add(Op.STORE_LOCAL, var_idx, node.line, node.column)

        break_idxs = []
        for stmt in node.body:
            self._emit_stmt(stmt)
            last = self.bytecode.instructions[-1]
            if last.op == Op.JUMP and isinstance(last.arg, tuple):
                if last.arg[0] == "BREAK":
                    break_idxs.append(len(self.bytecode.instructions) - 1)
                elif last.arg[0] == "CONTINUE":
                    self.bytecode.instructions[-1] = Instruction(
                        Op.JUMP, loop_start, last.line, last.column
                    )

        self.bytecode.add(Op.JUMP, loop_start, node.line, node.column)
        loop_end = len(self.bytecode.instructions)
        self.bytecode.instructions[body_jump_idx].arg = loop_end
        for idx in break_idxs:
            brk = self.bytecode.instructions[idx]
            self.bytecode.instructions[idx] = Instruction(
                Op.JUMP, loop_end, brk.line, brk.column
            )

        # Cleanup: remove loop var from locals
        self._remove_locals(1)

    def _emit_range_for(self, node: RangeForNode):
        """untuk i dari A sampai B (langkah S)? lakukan ... selesai (v6.7)

        Dikompilasi sebagai iterasi over Python range yang dibuat runtime:
            range(start, end + (1 if step > 0 else -1), step)
        sehingga inklusif dan konsisten dengan interpreter & transpiler.
        """
        # Evaluasi start & end sekali
        self._emit_expr(node.start)
        self._ensure_local("_range_s")
        s_idx = self._get_local_idx("_range_s")
        self.bytecode.add(Op.STORE_LOCAL, s_idx, node.line, node.column)
        self._emit_expr(node.end)
        self._ensure_local("_range_e")
        e_idx = self._get_local_idx("_range_e")
        self.bytecode.add(Op.STORE_LOCAL, e_idx, node.line, node.column)

        # step: evaluasi atau default 1/-1
        # Default: step = 1 jika start <= end, else -1
        #   stack: [kondisi] -> POP_JUMP_IF_FALSE -> pilih 1 atau -1
        if node.step is not None:
            self._emit_expr(node.step)
        else:
            self.bytecode.add(Op.LOAD_LOCAL, s_idx, node.line, node.column)
            self.bytecode.add(Op.LOAD_LOCAL, e_idx, node.line, node.column)
            self.bytecode.add(Op.LTE, line=node.line, column=node.column)
            jump_step_else = len(self.bytecode.instructions)
            self.bytecode.add(Op.POP_JUMP_IF_FALSE, 0)
            self.bytecode.add(Op.PUSH_INT_1)
            jump_step_end = len(self.bytecode.instructions)
            self.bytecode.add(Op.JUMP, 0)
            self.bytecode.instructions[jump_step_else].arg = len(self.bytecode.instructions)
            self.bytecode.add(Op.PUSH_CONST, self.bytecode.add_const(-1))
            self.bytecode.instructions[jump_step_end].arg = len(self.bytecode.instructions)
            # stack: [step]

        # Guard step == 0: konsisten dengan interpreter & transpiler yang
        # memberi error ramah "Langkah range tidak boleh nol".
        self._ensure_local("_range_k")
        k_idx = self._get_local_idx("_range_k")
        self.bytecode.add(Op.STORE_LOCAL, k_idx, node.line, node.column)
        self.bytecode.add(Op.LOAD_LOCAL, k_idx, node.line, node.column)
        self.bytecode.add(Op.PUSH_INT_0, line=node.line, column=node.column)
        self.bytecode.add(Op.EQ, line=node.line, column=node.column)
        jump_step_ok = len(self.bytecode.instructions)
        self.bytecode.add(Op.POP_JUMP_IF_FALSE, 0)
        msg_idx = self.bytecode.add_const("Langkah range tidak boleh nol")
        self.bytecode.add(Op.PUSH_CONST, msg_idx, node.line, node.column)
        self.bytecode.add(Op.RAISE, line=node.line, column=node.column)
        self.bytecode.instructions[jump_step_ok].arg = len(self.bytecode.instructions)

        # end_inkl = end + (1 if k > 0 else -1)
        self.bytecode.add(Op.LOAD_LOCAL, e_idx, node.line, node.column)
        self.bytecode.add(Op.LOAD_LOCAL, k_idx, node.line, node.column)
        self.bytecode.add(Op.PUSH_INT_0)
        self.bytecode.add(Op.GT, line=node.line, column=node.column)
        jump_adj_else = len(self.bytecode.instructions)
        self.bytecode.add(Op.POP_JUMP_IF_FALSE, 0)
        self.bytecode.add(Op.PUSH_INT_1)
        jump_adj_end = len(self.bytecode.instructions)
        self.bytecode.add(Op.JUMP, 0)
        self.bytecode.instructions[jump_adj_else].arg = len(self.bytecode.instructions)
        self.bytecode.add(Op.PUSH_CONST, self.bytecode.add_const(-1))
        self.bytecode.instructions[jump_adj_end].arg = len(self.bytecode.instructions)
        self.bytecode.add(Op.ADD)  # end + adj
        self._ensure_local("_range_ei")
        ei_idx = self._get_local_idx("_range_ei")
        self.bytecode.add(Op.STORE_LOCAL, ei_idx, node.line, node.column)

        # Buat iterable range(start, end_inkl, step)
        self.bytecode.add(Op.LOAD_LOCAL, s_idx, node.line, node.column)
        self.bytecode.add(Op.LOAD_LOCAL, ei_idx, node.line, node.column)
        self.bytecode.add(Op.LOAD_LOCAL, k_idx, node.line, node.column)
        self.bytecode.add(Op.CALL_BUILTIN, ("range", 3), node.line, node.column)
        self.bytecode.add(Op.GET_ITER, line=node.line, column=node.column)

        loop_start = len(self.bytecode.instructions)
        body_jump_idx = len(self.bytecode.instructions)
        self.bytecode.add(Op.FOR_ITER, 0, node.line, node.column)

        # Simpan loop variable
        self._ensure_local(node.variable)
        var_idx = self._get_local_idx(node.variable)
        self.bytecode.add(Op.STORE_LOCAL, var_idx, node.line, node.column)

        break_idxs = []
        for stmt in node.body:
            self._emit_stmt(stmt)
            last = self.bytecode.instructions[-1]
            if last.op == Op.JUMP and isinstance(last.arg, tuple):
                if last.arg[0] == "BREAK":
                    break_idxs.append(len(self.bytecode.instructions) - 1)
                elif last.arg[0] == "CONTINUE":
                    self.bytecode.instructions[-1] = Instruction(
                        Op.JUMP, loop_start, last.line, last.column
                    )

        self.bytecode.add(Op.JUMP, loop_start, node.line, node.column)
        loop_end = len(self.bytecode.instructions)
        self.bytecode.instructions[body_jump_idx].arg = loop_end
        for idx in break_idxs:
            brk = self.bytecode.instructions[idx]
            self.bytecode.instructions[idx] = Instruction(
                Op.JUMP, loop_end, brk.line, brk.column
            )

        # Cleanup: hapus variabel loop + temp range
        self._remove_locals(5)

    def _emit_for_each(self, node: ForEachNode):
        """untuk setiap (item, indeks)? dalam iterable lakukan ... selesai (v6.7)

        Iterasi langsung atas iterator (GET_ITER + FOR_ITER). Bila
        index_variable dipakai, counter indeks dikelola manual via local
        `_each_i` (mulai 0, +1 tiap iterasi) — konsisten dengan
        interpreter `enumerate` dan tanpa alokasi list ekstra.
        """
        # Evaluasi iterable & buat iterator
        self._emit_expr(node.iterable)
        self.bytecode.add(Op.GET_ITER, line=node.line, column=node.column)

        # Catat jumlah locals sebelum loop — cleanup hanya menghapus yang
        # benar-benar ditambahkan di sini (aman bila nama variabel loop
        # sudah ada sebagai local/param dari luar).
        locals_before = len(self.locals)

        # Counter indeks (hanya bila index_variable dipakai)
        i_idx = -1
        if node.index_variable:
            self._ensure_local("_each_i")
            i_idx = self._get_local_idx("_each_i")
            self.bytecode.add(Op.PUSH_INT_0, line=node.line, column=node.column)
            self.bytecode.add(Op.STORE_LOCAL, i_idx, node.line, node.column)

        loop_start = len(self.bytecode.instructions)
        body_jump_idx = len(self.bytecode.instructions)
        self.bytecode.add(Op.FOR_ITER, 0, node.line, node.column)

        # Simpan item
        self._ensure_local(node.variable)
        var_idx = self._get_local_idx(node.variable)
        self.bytecode.add(Op.STORE_LOCAL, var_idx, node.line, node.column)

        if node.index_variable:
            # indeks = _each_i, lalu _each_i += 1
            self._ensure_local(node.index_variable)
            ix_idx = self._get_local_idx(node.index_variable)
            self.bytecode.add(Op.LOAD_LOCAL, i_idx, node.line, node.column)
            self.bytecode.add(Op.STORE_LOCAL, ix_idx, node.line, node.column)
            self.bytecode.add(Op.LOAD_LOCAL, i_idx, node.line, node.column)
            self.bytecode.add(Op.PUSH_INT_1, line=node.line, column=node.column)
            self.bytecode.add(Op.ADD, line=node.line, column=node.column)
            self.bytecode.add(Op.STORE_LOCAL, i_idx, node.line, node.column)

        break_idxs = []
        for stmt in node.body:
            self._emit_stmt(stmt)
            last = self.bytecode.instructions[-1]
            if last.op == Op.JUMP and isinstance(last.arg, tuple):
                if last.arg[0] == "BREAK":
                    break_idxs.append(len(self.bytecode.instructions) - 1)
                elif last.arg[0] == "CONTINUE":
                    self.bytecode.instructions[-1] = Instruction(
                        Op.JUMP, loop_start, last.line, last.column
                    )

        self.bytecode.add(Op.JUMP, loop_start, node.line, node.column)
        loop_end = len(self.bytecode.instructions)
        self.bytecode.instructions[body_jump_idx].arg = loop_end
        for idx in break_idxs:
            brk = self.bytecode.instructions[idx]
            self.bytecode.instructions[idx] = Instruction(
                Op.JUMP, loop_end, brk.line, brk.column
            )

        # Cleanup: hapus hanya local yang ditambahkan oleh loop ini
        self._remove_locals(len(self.locals) - locals_before)

    def _emit_destructuring(self, node: DestructuringAssignmentNode):
        """buat [a, b] = list / buat {x, y} = objek / buat (a, b) = tuple (v6.7)

        Nilai di-evaluasi sekali dan disimpan di stack (DUP per target),
        sehingga tidak perlu local temp yang mengganggu scope tracking.
        """
        self._emit_expr(node.value)

        if node.is_array:
            for i, name in enumerate(node.targets):
                self.bytecode.add(Op.DUP, line=node.line, column=node.column)
                idx_const = self.bytecode.add_const(i)
                self.bytecode.add(Op.PUSH_CONST, idx_const, node.line, node.column)
                self.bytecode.add(Op.INDEX_GET, line=node.line, column=node.column)
                self._store_destructure_target(name, node)
        else:
            for name in node.targets:
                self.bytecode.add(Op.DUP, line=node.line, column=node.column)
                key_const = self.bytecode.add_const(name)
                self.bytecode.add(Op.PUSH_CONST, key_const, node.line, node.column)
                self.bytecode.add(Op.DICT_GET, line=node.line, column=node.column)
                self._store_destructure_target(name, node)

        # Buang nilai asli dari stack
        self.bytecode.add(Op.POP_TOP, line=node.line, column=node.column)

    def _store_destructure_target(self, name: str, node):
        """Simpan hasil destructuring ke variabel (global di top-level,
        local di dalam fungsi) — konsisten dengan _emit_assignment."""
        if self.scope_depth == 0:
            idx = self.bytecode.add_name(name)
            self.bytecode.add(Op.DEFINE_GLOBAL, idx, node.line, node.column)
        else:
            self._ensure_local(name)
            self.bytecode.add(Op.STORE_LOCAL, self._get_local_idx(name), node.line, node.column)

    def _emit_pipeline(self, node: PipelineNode):
        """nilai |> f(args) => f(nilai, args...) (v6.7)"""
        right = node.right

        # Higher-order functions: iterable dari nilai kiri
        if isinstance(right, MapNode):
            self._emit_expr(node.left)
            self._emit_expr(right.function)
            self.bytecode.add(Op.CALL_BUILTIN, ("peta", 2), node.line, node.column)
            return
        if isinstance(right, FilterNode):
            self._emit_expr(node.left)
            self._emit_expr(right.condition)
            self.bytecode.add(Op.CALL_BUILTIN, ("saring", 2), node.line, node.column)
            return
        if isinstance(right, ReduceNode):
            self._emit_expr(node.left)
            self._emit_expr(right.function)
            self.bytecode.add(Op.CALL_BUILTIN, ("kurangi", 2), node.line, node.column)
            return

        if isinstance(right, CallNode):
            # f(nilai, args...)
            self._emit_expr(node.left)
            self._emit_call_with_first_arg(right)
            return

        # f(nilai)
        self._emit_expr(node.left)
        self._emit_expr(right)
        self.bytecode.add(Op.CALL, 1, node.line, node.column)

    def _emit_call_with_first_arg(self, node: CallNode):
        """Emit pemanggilan dengan nilai kiri pipeline sebagai argumen pertama.

        Stack saat dipanggil: [nilai_kiri]
        Menghasilkan: fungsi, nilai_kiri, args... -> CALL (1 + len(args))
        """
        from brolang.interpreter.builtins import BUILTINS

        has_kwargs = bool(node.kwargs)
        n_args = len(node.args) + 1 + (1 if has_kwargs else 0)

        if isinstance(node.function, IdentifierNode):
            name = node.function.name
            if name in BUILTINS and not has_kwargs:
                # Stack saat ini: [nilai_kiri]. Builtin butuh nilai_kiri + args.
                for arg in node.args:
                    self._emit_expr(arg)
                self.bytecode.add(
                    Op.CALL_BUILTIN, (name, len(node.args) + 1), node.line, node.column
                )
                return
            loc = self._resolve_name(name)
            if loc == "local":
                idx = self._get_local_idx(name)
                self.bytecode.add(Op.LOAD_LOCAL, idx, node.line, node.column)
            elif loc == "free":
                idx = self.bytecode.add_free_var(name)
                self.bytecode.add(Op.LOAD_DEREF, idx, node.line, node.column)
            else:
                idx = self.bytecode.add_name(name)
                self.bytecode.add(Op.LOAD_GLOBAL, idx, node.line, node.column)
            for arg in node.args:
                self._emit_expr(arg)
            self.bytecode.add(Op.CALL, n_args, node.line, node.column)
        else:
            self._emit_expr(node.function)
            for arg in node.args:
                self._emit_expr(arg)
            self.bytecode.add(Op.CALL, n_args, node.line, node.column)

    # ============= Print (fast path) =============

    def _emit_print(self, node: PrintNode):
        # Collect all expressions (main + args)
        exprs = [node.expression] + node.args
        for expr in exprs:
            self._emit_expr(expr)
        self.bytecode.add(Op.PRINT, len(exprs), node.line, node.column)

    # ============= Return =============

    def _emit_return(self, node: ReturnNode):
        guard = getattr(node, "guard", None)
        if guard is not None:
            # kembali x jika c -> guard DULU (value hanya dievaluasi saat guard
            # benar, konsisten dengan interpreter & transpiler).
            self._emit_expr(guard)
            skip_idx = len(self.bytecode.instructions)
            self.bytecode.add(Op.POP_JUMP_IF_FALSE, 0, node.line, node.column)
            if node.value and not isinstance(node.value, KosongNode):
                self._emit_expr(node.value)
            else:
                self.bytecode.add(Op.PUSH_NONE, line=node.line, column=node.column)
            self.bytecode.add(Op.RETURN, line=node.line, column=node.column)
            self.bytecode.instructions[skip_idx].arg = len(self.bytecode.instructions)
            return
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
            if loc == "local":
                idx = self._get_local_idx(name)
                self.bytecode.add(Op.LOAD_LOCAL, idx, node.line, node.column)
            elif loc == "free":
                idx = self.bytecode.add_free_var(name)
                self.bytecode.add(Op.LOAD_DEREF, idx, node.line, node.column)
            else:
                idx = self.bytecode.add_name(name)
                self.bytecode.add(Op.LOAD_GLOBAL, idx, node.line, node.column)

        elif isinstance(node, BinaryOpNode):
            self._emit_binary_op(node)

        elif isinstance(node, UnaryOpNode):
            self._emit_expr(node.operand)
            if node.operator == "-":
                self.bytecode.add(Op.NEG, line=node.line, column=node.column)
            elif node.operator == "bukan":
                self.bytecode.add(Op.NOT_OP, line=node.line, column=node.column)

        elif isinstance(node, CallNode):
            self._emit_call(node)

        elif isinstance(node, IfNode):
            # Ternary-like usage: if expr
            self._emit_if_expr(node)

        elif isinstance(node, ListNode):
            self._emit_list_with_spread(node)

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
            self._emit_expr(node.true_value)
            jump_end = len(self.bytecode.instructions)
            self.bytecode.add(Op.JUMP, 0)
            self.bytecode.instructions[jump_else].arg = len(self.bytecode.instructions)
            self._emit_expr(node.false_value)
            self.bytecode.instructions[jump_end].arg = len(self.bytecode.instructions)

        elif isinstance(node, StructInstanceNode):
            self._emit_expr(node.definition)
            for arg in node.args:
                self._emit_expr(arg)
            self.bytecode.add(Op.MAKE_INSTANCE, len(node.args), node.line, node.column)

        elif isinstance(node, PipelineNode):
            self._emit_pipeline(node)

        elif isinstance(node, SpreadNode):
            self._emit_expr(node.value)
            self.bytecode.add(Op.MAKE_LIST, 1, node.line, node.column)

        else:
            # Fallback: push None for unknown nodes
            self.bytecode.add(Op.PUSH_NONE, line=getattr(node, "line", 0))

    def _emit_binary_op(self, node: BinaryOpNode):
        # Short-circuit for 'dan' / 'atau'
        if node.operator == "dan":
            self._emit_expr(node.left)
            self.bytecode.add(Op.POP_JUMP_IF_FALSE, 0, node.line, node.column)
            self.bytecode.add(Op.POP_TOP)
            self._emit_expr(node.right)
            self.bytecode.instructions[-3].arg = len(self.bytecode.instructions)
            return
        if node.operator == "atau":
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
            "+": Op.ADD,
            "-": Op.SUB,
            "*": Op.MUL,
            "/": Op.DIV,
            "//": Op.FLOOR_DIV,
            "%": Op.MOD,
            "**": Op.POW,
            "==": Op.EQ,
            "!=": Op.NEQ,
            ">": Op.GT,
            ">=": Op.GTE,
            "<": Op.LT,
            "<=": Op.LTE,
            "is": Op.IS_OP,
            "dan": Op.AND,
            "atau": Op.OR,
        }
        op = op_map.get(node.operator)
        if op:
            self.bytecode.add(op, line=node.line, column=node.column)

    def _emit_call(self, node: CallNode):
        # Keyword arguments dikonversi jadi positional dict-passing:
        # fungsi(a, b=1) => fungsi(a, {'b': 1})
        # Untuk VM sederhana, kwargs dipasangkan sebagai dict arg terakhir.
        has_kwargs = bool(node.kwargs)
        has_spread = any(isinstance(a, SpreadNode) for a in node.args)

        def _emit_args():
            for arg in node.args:
                self._emit_expr(arg)
            if has_kwargs:
                for _, val in node.kwargs:
                    self._emit_expr(val)

        if isinstance(node.function, IdentifierNode):
            name = node.function.name
            # Check if builtin
            from brolang.interpreter.builtins import BUILTINS

            if name in BUILTINS and not has_kwargs and not has_spread:
                for arg in node.args:
                    self._emit_expr(arg)
                self.bytecode.add(Op.CALL_BUILTIN, (name, len(node.args)), node.line, node.column)
                return

            # Spread call: bangun list argumen lalu panggil via CALL_SPREAD
            if has_spread:
                self._emit_spread_args(node, has_kwargs)
                loc = self._resolve_name(name)
                if loc == "local":
                    idx = self._get_local_idx(name)
                    self.bytecode.add(Op.LOAD_LOCAL, idx, node.line, node.column)
                elif loc == "free":
                    idx = self.bytecode.add_free_var(name)
                    self.bytecode.add(Op.LOAD_DEREF, idx, node.line, node.column)
                else:
                    idx = self.bytecode.add_name(name)
                    self.bytecode.add(Op.LOAD_GLOBAL, idx, node.line, node.column)
                self.bytecode.add(Op.CALL_SPREAD, line=node.line, column=node.column)
                return

            _emit_args()
            loc = self._resolve_name(name)
            if loc == "local":
                idx = self._get_local_idx(name)
                self.bytecode.add(Op.LOAD_LOCAL, idx, node.line, node.column)
            elif loc == "free":
                idx = self.bytecode.add_free_var(name)
                self.bytecode.add(Op.LOAD_DEREF, idx, node.line, node.column)
            else:
                idx = self.bytecode.add_name(name)
                self.bytecode.add(Op.LOAD_GLOBAL, idx, node.line, node.column)
            self.bytecode.add(
                Op.CALL, len(node.args) + (1 if has_kwargs else 0), node.line, node.column
            )

        elif isinstance(node.function, ObjectAccessNode):
            if has_spread:
                # Method + spread: LOAD_ATTR memberi method terikat, lalu
                # CALL_SPREAD memanggilnya dengan argumen yang di-unpack.
                self._emit_spread_args(node, has_kwargs)
                self._emit_expr(node.function.object)
                prop_idx = self.bytecode.add_name(node.function.property)
                self.bytecode.add(Op.LOAD_ATTR, prop_idx, node.line, node.column)
                # Stack: [arg_list, method_bound]
                self.bytecode.add(Op.CALL_SPREAD, line=node.line, column=node.column)
                return
            self._emit_expr(node.function.object)
            prop_idx = self.bytecode.add_name(node.function.property)
            self.bytecode.add(Op.LOAD_METHOD, prop_idx, node.line, node.column)
            _emit_args()
            self.bytecode.add(
                Op.CALL_METHOD,
                (prop_idx, len(node.args) + (1 if has_kwargs else 0)),
                node.line,
                node.column,
            )
        else:
            # Generic call
            if has_spread:
                self._emit_spread_args(node, has_kwargs)
                self._emit_expr(node.function)
                self.bytecode.add(Op.CALL_SPREAD, line=node.line, column=node.column)
                return
            self._emit_expr(node.function)
            _emit_args()
            self.bytecode.add(
                Op.CALL, len(node.args) + (1 if has_kwargs else 0), node.line, node.column
            )

    def _emit_spread_args(self, node: CallNode, has_kwargs: bool):
        """Emit argumen dengan spread sebagai list di stack.

        Untuk setiap argumen push pasangan (is_spread, value):
            is_spread = benar  -> BUILD_LIST_SPREAD extend
            is_spread = salah  -> append
        Lalu BUILD_LIST_SPREAD membuat list argumen final.
        """
        for arg in node.args:
            if isinstance(arg, SpreadNode):
                self.bytecode.add(Op.PUSH_TRUE, line=arg.line, column=arg.column)
                self._emit_expr(arg.value)
            else:
                self.bytecode.add(Op.PUSH_FALSE, line=getattr(arg, "line", 0))
                self._emit_expr(arg)
        if has_kwargs:
            self.bytecode.add(Op.PUSH_FALSE)
            self._emit_expr(ObjectNode(entries={n: v for n, v in node.kwargs}))
        self.bytecode.add(
            Op.BUILD_LIST_SPREAD, len(node.args) + (1 if has_kwargs else 0),
            node.line, node.column,
        )

    def _emit_list_with_spread(self, node: ListNode):
        """Emit list literal — dukung spread elemen `[...a, 1]` (v6.7)."""
        has_spread = any(isinstance(e, SpreadNode) for e in node.elements)
        if not has_spread:
            for elem in node.elements:
                self._emit_expr(elem)
            self.bytecode.add(Op.MAKE_LIST, len(node.elements), node.line, node.column)
            return
        for elem in node.elements:
            if isinstance(elem, SpreadNode):
                self.bytecode.add(Op.PUSH_TRUE, line=elem.line, column=elem.column)
                self._emit_expr(elem.value)
            else:
                self.bytecode.add(Op.PUSH_FALSE, line=getattr(elem, "line", 0))
                self._emit_expr(elem)
        self.bytecode.add(
            Op.BUILD_LIST_SPREAD, len(node.elements), node.line, node.column
        )

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
            if loc == "local":
                idx = self._get_local_idx(node.target.name)
                self.bytecode.add(Op.DEL_VAR, ("local", idx), node.line, node.column)
            else:
                idx = self.bytecode.add_name(node.target.name)
                self.bytecode.add(Op.DEL_VAR, ("global", idx), node.line, node.column)

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
            parts = ".".join(node.parts)
            idx = self.bytecode.add_const(parts)
            self.bytecode.add(Op.IMPORT, (parts, None), node.line, node.column)
            name = node.parts[-1]
            name_idx = self.bytecode.add_name(name)
            self.bytecode.add(Op.DEFINE_GLOBAL, name_idx, node.line, node.column)
        elif isinstance(node, FromImportNode):
            parts = ".".join(node.parts)
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
        methods = self._compile_methods(node.methods)

        struct_data = (node.name, methods)
        idx = self.bytecode.add_const(struct_data)
        self.bytecode.add(Op.MAKE_CLASS, idx, node.line, node.column)
        name_idx = self.bytecode.add_name(node.name)
        self.bytecode.add(Op.DEFINE_GLOBAL, name_idx, node.line, node.column)

    def _emit_augmented_assignment(self, node: AugmentedAssignmentNode):
        """Augmented assignment: x += 1, self.x += 1, data[i] //= 2 (v6.8)."""
        target = node.target
        op_map = {
            "+=": Op.AUG_ADD,
            "-=": Op.AUG_SUB,
            "*=": Op.AUG_MUL,
            "/=": Op.AUG_DIV,
            "//=": Op.AUG_FLOOR_DIV,
            "%=": Op.AUG_MOD,
            "**=": Op.AUG_POW,
        }
        op = op_map[node.operator]

        if isinstance(target, IdentifierNode):
            name = target.name
            self._emit_expr(target)  # muat nilai saat ini
            self._emit_expr(node.value)
            self.bytecode.add(op, line=node.line, column=node.column)
            loc = self._resolve_name(name)
            if loc == "local":
                idx = self._get_local_idx(name)
                self.bytecode.add(Op.STORE_LOCAL, idx, node.line, node.column)
            else:
                idx = self.bytecode.add_name(name)
                self.bytecode.add(Op.STORE_GLOBAL, idx, node.line, node.column)
            return

        if isinstance(target, ObjectAccessNode):
            # self.x += 1 → [obj] DUP LOAD_ATTR [value] AUG STORE_ATTR POP_TOP
            self._emit_expr(target.object)
            self.bytecode.add(Op.DUP, line=node.line, column=node.column)
            prop_idx = self.bytecode.add_name(target.property)
            self.bytecode.add(Op.LOAD_ATTR, prop_idx, node.line, node.column)
            self._emit_expr(node.value)
            self.bytecode.add(op, line=node.line, column=node.column)
            self.bytecode.add(Op.STORE_ATTR, prop_idx, node.line, node.column)
            self.bytecode.add(Op.POP_TOP, line=node.line, column=node.column)
            return

        if isinstance(target, IndexNode):
            # data[i] += 1 → target di-evaluasi sekali (DUP); index disimpan
            # di local temp supaya bisa dipakai INDEX_GET lalu INDEX_SET (v6.8).
            self._ensure_local("_aug_idx")
            tmp_idx = self._get_local_idx("_aug_idx")
            self._emit_expr(target.target)
            self.bytecode.add(Op.DUP, line=node.line, column=node.column)
            self._emit_expr(target.index)
            self.bytecode.add(Op.STORE_LOCAL, tmp_idx, node.line, node.column)
            self.bytecode.add(Op.LOAD_LOCAL, tmp_idx, node.line, node.column)
            self.bytecode.add(Op.INDEX_GET, line=node.line, column=node.column)
            self._emit_expr(node.value)
            self.bytecode.add(op, line=node.line, column=node.column)
            self.bytecode.add(Op.LOAD_LOCAL, tmp_idx, node.line, node.column)
            self.bytecode.add(Op.SWAP, line=node.line, column=node.column)  # [data, i, hasil]
            self.bytecode.add(Op.INDEX_SET, line=node.line, column=node.column)
            self.bytecode.add(Op.POP_TOP, line=node.line, column=node.column)
            return

        raise NotImplementedError("Augmented assignment untuk target ini belum didukung.")

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
            if ptype == "literal":
                idx = self.bytecode.add_const(pval)
                self.bytecode.add(Op.PUSH_CONST, idx, node.line, node.column)
                parts.append(("const", None))
            elif ptype == "expr":
                self._emit_expr(pval)
                parts.append(("expr", None))

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
        if node.rest_param:
            self._add_local(node.rest_param)

        self._emit_expr(node.body)
        self.bytecode.add(Op.RETURN)

        func_bc = self.bytecode
        apply_peephole(func_bc)
        func_bc.finalize()
        self.bytecode = saved
        self.locals = saved_locals
        self.free_vars = saved_free
        self.scope_depth = saved_depth

        const_idx = self.bytecode.add_const(func_bc)
        param_count = len(node.params) + (1 if node.rest_param else 0)
        rest_pos = len(node.params) if node.rest_param else -1
        self.bytecode.add(
            Op.CLOSURE, (const_idx, param_count, False, rest_pos), node.line, node.column
        )

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
                return "local"
        # Check free vars
        if name in self.free_vars:
            return "free"
        return "global"

    def _ensure_local(self, name: str):
        """Ensure a local exists, create if needed."""
        if self._get_local_idx(name) == -1:
            self._add_local(name)

    def _remove_locals(self, count: int):
        """Remove last N locals."""
        for _ in range(count):
            if self.locals:
                self.locals.pop()
