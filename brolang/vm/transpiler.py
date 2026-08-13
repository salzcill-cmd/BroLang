"""
Transpiler BroLang → Python
============================
Mengubah AST BroLang menjadi kode Python yang bisa dijalankan langsung
dengan CPython — memberikan performa native Python.

Transpiler hanya menangani fitur-fitur yang punya padanan Python langsung.
Fitur BroLang-specific (hasilkan, hentikan_iterasi, ??, ?. ) ditangani
dengan runtime helpers.
"""

from brolang.ast.nodes import *
from typing import List, Optional


# BroLang builtins yang perlu di-override agar identik
RUNTIME_HELPERS = '''
import sys as _sys

def _brolang_tulis(*args, **kwargs):
    print(*args, **kwargs)

def _brolang_cek_tipe(x, tipe=None):
    result = type(x).__name__
    if tipe is not None:
        return result == tipe
    return result

def _brolang_panjang(x):
    return len(x)

def _brolang_hentikan_iterasi():
    raise StopIteration

def _brolang_rentang(*args):
    return range(*args)

def _brolang_jenis(x):
    return type(x).__name__

def _brolang_tipe(x):
    _m = {int: 'angka', float: 'desimal', str: 'teks', bool: 'boolean',
          list: 'list', dict: 'objek', tuple: 'tuple', set: 'set', type(None): 'kosong'}
    return _m.get(type(x), type(x).__name__)

def _brolang_stdlib_get(name):
    from brolang.stdlib import get_stdlib_module as _g
    return _g(name)

_brolang_nomatch = object()  # sentinel pola objek (v6.0)

# V7.0: error propagation '?' — buka Result/Option (dict interpreter ATAU
# tuple transpiler) dan lempar error untuk kasus Salah/Kosong.
def _brolang_propagate(v):
    if isinstance(v, dict) and v.get("type") == "Result":
        if v.get("is_success"):
            return v.get("value")
        err = v.get("value")
        if isinstance(err, BaseException):
            raise err
        raise RuntimeError(str(err) if err is not None else "Error tanpa pesan")
    if isinstance(v, dict) and v.get("type") == "Option":
        if v.get("has_value"):
            return v.get("value")
        raise RuntimeError("Nilai kosong (Kosong()) — tidak bisa di-unwrap dengan '?'.")
    if isinstance(v, tuple) and len(v) == 2:
        if v[0] == "ok":
            return v[1]
        if v[0] == "some":
            return v[1]
        if v[0] == "err":
            err = v[1]
            if isinstance(err, BaseException):
                raise err
            raise RuntimeError(str(err) if err is not None else "Error tanpa pesan")
        if v[0] == "none":
            raise RuntimeError("Nilai kosong — tidak bisa di-unwrap dengan '?'.")
    return v

# V7.0: async sejati — body fungsi asinkron dijalankan di background
# thread (daemon) dan dibungkus objek _AsyncTugas (kelas yang SAMA dengan
# interpreter, agar `selesai()`/`hasil()`/`tunggu()` konsisten lintas mesin).
def _brolang_async_run(fn, *args):
    import concurrent.futures as _cf
    import threading as _th
    from brolang.interpreter.interpreter import _AsyncTugas as _T

    _future = _cf.Future()

    def _brolang_worker():
        try:
            _future.set_result(fn(*args))
        except Exception as _e:
            _future.set_exception(_e)

    _th.Thread(target=_brolang_worker, daemon=True).start()
    return _T(_future)


def _brolang_await(v):
    # tunggu: blokir sampai Tugas selesai; nilai non-Tugas apa adanya.
    if hasattr(v, 'tunggu') and callable(v.tunggu):
        return v.tunggu()
    return v


# V7.2: `dengan` statement — dukung method BroLang `masuk`/`keluar` DAN
# protocol Python `__enter__`/`__exit__` (konsisten dengan interpreter/VM).
def _brolang_with_enter(ctx):
    if hasattr(ctx, 'masuk') and callable(ctx.masuk):
        r = ctx.masuk()
        return r if r is not None else ctx
    if hasattr(ctx, '__enter__'):
        r = ctx.__enter__()
        return r if r is not None else ctx
    return ctx


def _brolang_with_exit(ctx):
    if hasattr(ctx, 'keluar') and callable(ctx.keluar):
        return ctx.keluar()
    if hasattr(ctx, '__exit__'):
        return ctx.__exit__(None, None, None)
    return None


def _brolang_with(ctx):
    class _Ctx:
        def __enter__(self):
            return _brolang_with_enter(ctx)

        def __exit__(self, et, ev, tb):
            return _brolang_with_exit(ctx)

    return _Ctx()


_tulis = _brolang_tulis

# V6.0: kelas dasar error kustom
class Kesalahan(Exception):
    def __init__(self, pesan=''):
        self.pesan = str(pesan)
        super().__init__(str(pesan))
'''


class Transpiler:
    """Transpile AST BroLang → Python source code."""

    # Operator overloading (v5.5): method BroLang `_tambah_` dst ditranspile
    # menjadi dunder Python `__add__` dst, sehingga hasilnya konsisten dengan
    # interpreter dan berjalan di CPython secara native.
    _OVERLOAD_METHOD_MAP = {
        '_tambah_': '__add__', '_kurang_': '__sub__', '_kali_': '__mul__',
        '_bagi_': '__truediv__', '_modulo_': '__mod__', '_pangkat_': '__pow__',
        '_negasi_': '__neg__', '_positif_': '__pos__',
        '_sama_': '__eq__', '_tidak_sama_': '__ne__',
        '_kurang_dari_': '__lt__', '_lebih_dari_': '__gt__',
        '_kurang_sama_': '__le__', '_lebih_sama_': '__ge__',
        '_teks_': '__str__', '_panjang_': '__len__',
        '_index_': '__getitem__', '_index_set_': '__setitem__',
        '_panggil_': '__call__', '_dalam_': '__contains__',
        '_iter_': '__iter__', '_iter_next_': '__next__',
    }

    def __init__(self):
        self._indent = 0
        self._lines: List[str] = []
        self._in_class = False
        self._modules: set = set()  # nama identifier yang merupakan modul (impor)
        self._tmp_counter = 0  # v6.5: nama temp unik untuk range-for

    def transpile(self, node: ASTNode) -> str:
        """Transpile AST root → Python source code string."""
        self._lines = []
        self._indent = 0
        self._modules = set()
        self._emit_stmt(node)
        return RUNTIME_HELPERS + '\n' + '\n'.join(self._lines) + '\n'

    # ==================== Indentation ====================

    def _line(self, code: str):
        self._lines.append('    ' * self._indent + code)

    def _blank(self):
        self._lines.append('')

    # ==================== Statements ====================

    def _emit_stmt(self, node: ASTNode):
        if isinstance(node, ProgramNode):
            for stmt in node.statements:
                self._emit_stmt(stmt)
        elif isinstance(node, AssignmentNode):
            self._emit_assignment(node)
        elif isinstance(node, MultiAssignNode):
            # Multiple assignment (v7.0): a, b = 1, 2 / a, b = b, a
            # (Python mengevaluasi sisi kanan dulu — swap aman.)
            targets = ', '.join(node.targets)
            values = ', '.join(self._emit_expr(v) for v in node.values)
            self._line(f'{targets} = {values}')
        elif isinstance(node, FunctionNode):
            self._emit_function(node)
        elif isinstance(node, ClassNode):
            self._emit_class(node)
        elif isinstance(node, KelasErrorNode):
            self._emit_kelas_error(node)
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
        elif isinstance(node, ReturnNode):
            self._emit_return(node)
        elif isinstance(node, PrintNode):
            self._emit_print(node)
        elif isinstance(node, BreakNode):
            guard = getattr(node, "guard", None)
            if guard is not None:
                # hentikan jika x (v6.8)
                self._line(f'if {self._emit_expr(guard)}: break')
            else:
                self._line('break')
        elif isinstance(node, ContinueNode):
            guard = getattr(node, "guard", None)
            if guard is not None:
                # lanjutkan jika x (v6.8)
                self._line(f'if {self._emit_expr(guard)}: continue')
            else:
                self._line('continue')
        elif isinstance(node, PassNode):
            self._line('pass')
        elif isinstance(node, RaiseNode):
            self._emit_raise(node)
        elif isinstance(node, AssertNode):
            self._emit_assert(node)
        elif isinstance(node, DelNode):
            self._emit_del(node)
        elif isinstance(node, ImportNode):
            self._emit_import(node)
        elif isinstance(node, FromImportNode):
            self._emit_from_import(node)
        elif isinstance(node, TryNode):
            self._emit_try(node)
        elif isinstance(node, MultiExceptNode):
            self._emit_multi_except(node)
        elif isinstance(node, YieldNode):
            self._emit_yield(node)
        elif isinstance(node, YieldFromNode):
            self._emit_yield_from(node)
        elif isinstance(node, GeneratorFunctionNode):
            self._emit_generator_function(node)
        elif isinstance(node, AugmentedAssignmentNode):
            self._emit_augmented_assignment(node)
        elif isinstance(node, MatchNode):
            self._emit_match(node)
        elif isinstance(node, SwitchNode):
            self._emit_match(node)
        elif isinstance(node, EnumNode):
            self._emit_enum(node)
        elif isinstance(node, StructNode):
            self._emit_struct(node)
        elif isinstance(node, StructInstanceNode):
            self._emit_struct_instance_stmt(node)
        elif isinstance(node, GlobalNode):
            self._line(f'global {", ".join(node.names)}')
        elif isinstance(node, NonlocalNode):
            self._line(f'nonlocal {", ".join(node.names)}')
        elif isinstance(node, DecoratedFunctionNode):
            self._emit_decorated_function(node)
        elif isinstance(node, DecoratedClassNode):
            self._emit_decorated_class(node)
        elif isinstance(node, AsyncFunctionDefNode):
            self._emit_async_function(node)
        elif isinstance(node, WithNode):
            self._emit_with(node)
        elif isinstance(node, DestructuringAssignmentNode):
            self._emit_destructuring_assignment(node)
        elif isinstance(node, NamespaceNode):
            self._emit_namespace(node)
        elif isinstance(node, MacroDefNode):
            params = ', '.join(node.params) if node.params else ''
            self._line(f'def {node.name}({params}):')
            self._indent += 1
            if not node.body:
                self._line('pass')
            else:
                for stmt in node.body:
                    self._emit_stmt(stmt)
            self._indent -= 1
            self._blank()
        elif isinstance(node, MacroCallNode):
            self._emit_macro_call(node)
        elif isinstance(node, AccessModifierNode):
            if self._in_class and isinstance(node.target, FunctionNode):
                self._emit_method(node.target)
            else:
                self._emit_stmt(node.target)
        elif isinstance(node, AbstractClassNode):
            self._emit_abstract_class(node)
        else:
            # Expression statement
            code = self._emit_expr(node)
            if code:
                self._line(code)

    def _emit_assignment(self, node: AssignmentNode):
        target = self._emit_expr(node.target)
        value = self._emit_expr(node.value)
        self._line(f'{target} = {value}')

    def _emit_function(self, node: FunctionNode, is_async=False):
        prefix = 'async ' if is_async else ''
        params = self._emit_params_with_defaults(node)
        self._line(f'{prefix}def {node.name}({params}):')
        self._indent += 1
        rest_param = getattr(node, 'rest_param', None)
        if rest_param:
            # Konsisten dengan interpreter (list, bukan tuple dari *args)
            self._line(f'{rest_param} = list({rest_param})')
        if not node.body:
            self._line('pass')
        else:
            for stmt in node.body:
                self._emit_stmt(stmt)
        self._indent -= 1
        self._blank()

    def _emit_generator_function(self, node: GeneratorFunctionNode):
        params = self._emit_params_with_defaults(node)
        self._line(f'def {node.name}({params}):')
        self._indent += 1
        rest_param = getattr(node, 'rest_param', None)
        if rest_param:
            self._line(f'{rest_param} = list({rest_param})')
        if not node.body:
            self._line('pass')
        else:
            for stmt in node.body:
                self._emit_stmt(stmt)
        self._indent -= 1
        self._blank()

    def _emit_class(self, node: ClassNode):
        parent = f'({node.parent})' if node.parent else ''
        self._line(f'class {node.name}{parent}:')
        self._indent += 1
        self._in_class = True
        if not node.methods and not node.body:
            self._line('pass')
        else:
            for method in node.methods:
                self._emit_method(method)
            for stmt in node.body:
                if isinstance(stmt, AccessModifierNode):
                    self._emit_stmt(stmt)
                elif not isinstance(stmt, FunctionNode):
                    self._emit_stmt(stmt)
            # Python menonaktifkan hashing saat __eq__ didefinisikan; pulihkan
            # agar kelas dengan `_sama_` tetap bisa masuk set/dict.
            py_names = [self._OVERLOAD_METHOD_MAP.get(m.name, m.name)
                        for m in node.methods]
            if '__eq__' in py_names and '__hash__' not in py_names:
                self._line('__hash__ = object.__hash__')
            # Reflected dunder (konsisten dengan interpreter yang mendukung
            # refleksi): `b + a` juga memanggil `a._tambah_` kalau b tidak punya.
            reflected = {
                '__add__': '__radd__', '__sub__': '__rsub__',
                '__mul__': '__rmul__', '__truediv__': '__rtruediv__',
                '__mod__': '__rmod__', '__pow__': '__rpow__',
            }
            for dunder, rdunder in reflected.items():
                if dunder in py_names and rdunder not in py_names:
                    self._line(f'{rdunder} = {dunder}')
        self._in_class = False
        self._indent -= 1
        self._blank()

    def _emit_kelas_error(self, node: KelasErrorNode):
        """kelas_error Nama extends Induk ... selesai -> class Nama(Induk): ..."""
        parent = node.parent or 'Kesalahan'
        self._line(f'class {node.name}({parent}):')
        self._indent += 1
        self._in_class = True
        if not node.methods and not node.body:
            self._line('pass')
        else:
            for method in node.methods:
                self._emit_method(method)
            for stmt in node.body:
                if isinstance(stmt, AccessModifierNode):
                    self._emit_stmt(stmt)
                elif not isinstance(stmt, FunctionNode):
                    self._emit_stmt(stmt)
        self._in_class = False
        self._indent -= 1
        self._blank()

    def _emit_method(self, node):
        if node.is_static:
            self._line('@staticmethod')
            params = ', '.join(node.params)
        else:
            if node.params and node.params[0] == 'self':
                params = ', '.join(node.params)
            else:
                params = ', '.join(['self'] + node.params) if node.params else 'self'
        rest_param = getattr(node, 'rest_param', None)
        if rest_param:
            # Guard params kosong (mis. static method hanya punya rest)
            params = f'*{rest_param}' if not params else f'{params}, *{rest_param}'
        # Operator overloading: _tambah_ -> __add__, dst.
        py_name = self._OVERLOAD_METHOD_MAP.get(node.name, node.name)
        self._line(f'def {py_name}({params}):')
        self._indent += 1
        if rest_param:
            # Konsisten dengan interpreter (list, bukan tuple dari *args)
            self._line(f'{rest_param} = list({rest_param})')
        if not node.body:
            self._line('pass')
        else:
            for stmt in node.body:
                self._emit_stmt(stmt)
        self._indent -= 1
        self._blank()

    def _emit_if(self, node: IfNode):
        cond = self._emit_expr(node.condition)
        self._line(f'if {cond}:')
        self._indent += 1
        if not node.body:
            self._line('pass')
        else:
            for stmt in node.body:
                self._emit_stmt(stmt)
        self._indent -= 1

        for ec, eb in zip(node.elif_conditions, node.elif_bodies):
            cond = self._emit_expr(ec)
            self._line(f'elif {cond}:')
            self._indent += 1
            if not eb:
                self._line('pass')
            else:
                for stmt in eb:
                    self._emit_stmt(stmt)
            self._indent -= 1

        if node.else_body:
            self._line('else:')
            self._indent += 1
            for stmt in node.else_body:
                self._emit_stmt(stmt)
            self._indent -= 1

    def _emit_while(self, node: WhileNode):
        cond = self._emit_expr(node.condition)
        self._line(f'while {cond}:')
        self._indent += 1
        if not node.body:
            self._line('pass')
        else:
            for stmt in node.body:
                self._emit_stmt(stmt)
        self._indent -= 1
        if node.else_body:
            self._line('else:')
            self._indent += 1
            for stmt in node.else_body:
                self._emit_stmt(stmt)
            self._indent -= 1

    def _emit_do_until(self, node: DoUntilNode):
        """ulangi ... sampai kondisi -> while True: body; if kond: break (v6.5)"""
        self._line('while True:')
        self._indent += 1
        if not node.body:
            self._line('pass')
        else:
            for stmt in node.body:
                self._emit_stmt(stmt)
        cond = self._emit_expr(node.condition)
        self._line(f'if {cond}:')
        self._indent += 1
        self._line('break')
        self._indent -= 1
        self._indent -= 1

    def _emit_range_for(self, node: RangeForNode):
        """untuk i dari A sampai B langkah S -> range inklusif Python (v6.5)

        `sampai` inklusif: nilai akhir ikut termasuk. Langkah default
        otomatis 1 (start <= end) atau -1 (start > end). Ekspresi start/end/
        step dievaluasi sekali lewat temp agar konsisten dengan interpreter.
        """
        self._tmp_counter += 1
        n = self._tmp_counter
        s, e, k = f'_bro_range_s{n}', f'_bro_range_e{n}', f'_bro_range_k{n}'
        start = self._emit_expr(node.start)
        end = self._emit_expr(node.end)
        if node.step is not None:
            self._line(f'{s} = {start}')
            self._line(f'{e} = {end}')
            self._line(f'{k} = {self._emit_expr(node.step)}')
            self._line(f'if {k} == 0: raise ValueError("Langkah range tidak boleh nol")')
            self._line(f'for {node.variable} in range({s}, {e} + (1 if {k} > 0 else -1), {k}):')
        else:
            self._line(f'{s} = {start}')
            self._line(f'{e} = {end}')
            self._line(f'{k} = 1 if {s} <= {e} else -1')
            self._line(f'for {node.variable} in range({s}, {e} + (1 if {k} > 0 else -1), {k}):')
        self._indent += 1
        if not node.body:
            self._line('pass')
        else:
            for stmt in node.body:
                self._emit_stmt(stmt)
        self._indent -= 1
        if node.else_body:
            self._line('else:')
            self._indent += 1
            for stmt in node.else_body:
                self._emit_stmt(stmt)
            self._indent -= 1

    def _emit_for(self, node: ForNode):
        iterable = self._emit_expr(node.iterable)
        self._line(f'for {node.variable} in {iterable}:')
        self._indent += 1
        if not node.body:
            self._line('pass')
        else:
            for stmt in node.body:
                self._emit_stmt(stmt)
        self._indent -= 1
        if node.else_body:
            self._line('else:')
            self._indent += 1
            for stmt in node.else_body:
                self._emit_stmt(stmt)
            self._indent -= 1

    def _emit_for_each(self, node: ForEachNode):
        iterable = self._emit_expr(node.iterable)
        if node.index_variable:
            self._line(f'for {node.index_variable}, {node.variable} in enumerate({iterable}):')
        else:
            self._line(f'for {node.variable} in {iterable}:')
        self._indent += 1
        if not node.body:
            self._line('pass')
        else:
            for stmt in node.body:
                self._emit_stmt(stmt)
        self._indent -= 1

    def _emit_return(self, node: ReturnNode):
        val = self._emit_expr(node.value)
        guard = getattr(node, "guard", None)
        if guard is not None:
            # kembali x jika c (v6.8) -> if c: return x
            g = self._emit_expr(guard)
            if val:
                self._line(f'if {g}: return {val}')
            else:
                self._line(f'if {g}: return')
            return
        if val:
            self._line(f'return {val}')
        else:
            self._line('return')

    def _emit_print(self, node: PrintNode):
        parts = [self._emit_expr(node.expression)]
        for arg in node.args:
            parts.append(self._emit_expr(arg))
        self._line(f'print({", ".join(parts)})')

    def _emit_raise(self, node: RaiseNode):
        val = self._emit_expr(node.value)
        # v6.0: error kustom (instance kelas_error) langsung di-raise;
        # nilai primitif dibungkus RuntimeError agar tidak TypeError.
        self._line(f'_brolang_err = {val}')
        self._line('raise _brolang_err if isinstance(_brolang_err, BaseException) else RuntimeError(_brolang_err)')

    def _emit_assert(self, node: AssertNode):
        cond = self._emit_expr(node.condition)
        if node.message:
            msg = self._emit_expr(node.message)
            self._line(f'assert {cond}, {msg}')
        else:
            self._line(f'assert {cond}')

    def _emit_del(self, node: DelNode):
        target = self._emit_expr(node.target)
        self._line(f'del {target}')

    def _emit_import(self, node: ImportNode):
        # Module stdlib BroLang bukan package Python top-level. Coba modul
        # stdlib BroLang DULU (agar `impor json`/`impor csv` tidak tertimpa
        # modul Python dengan nama sama — fix v7.1), lalu fallback ke import
        # Python biasa bila tidak ada di stdlib BroLang.
        bind = node.alias or node.module.split('.')[0]
        self._modules.add(bind)
        self._line('try:')
        self._indent += 1
        self._line(f'{bind} = _brolang_stdlib_get({node.module!r})')
        self._indent -= 1
        self._line('except ImportError:')
        self._indent += 1
        if node.alias:
            self._line(f'import {node.module} as {node.alias}')
        else:
            self._line(f'import {node.module}')
        self._indent -= 1

    def _emit_from_import(self, node: FromImportNode):
        names = ', '.join(node.names)
        self._line(f'from {node.module} import {names}')

    def _emit_try(self, node: TryNode):
        self._line('try:')
        self._indent += 1
        for stmt in node.body:
            self._emit_stmt(stmt)
        self._indent -= 1
        self._line(f'except Exception as {node.catch_var}:')
        self._indent += 1
        for stmt in node.catch_body:
            self._emit_stmt(stmt)
        self._indent -= 1
        if node.finally_body:
            self._line('finally:')
            self._indent += 1
            for stmt in node.finally_body:
                self._emit_stmt(stmt)
            self._indent -= 1

    def _emit_multi_except(self, node: MultiExceptNode):
        self._line('try:')
        self._indent += 1
        for stmt in node.body:
            self._emit_stmt(stmt)
        self._indent -= 1
        for clause in node.except_clauses:
            exc_type = clause.exception_type or 'Exception'
            self._line(f'except {exc_type} as {clause.variable}:')
            self._indent += 1
            for stmt in clause.body:
                self._emit_stmt(stmt)
            self._indent -= 1
        if node.else_body:
            self._line('else:')
            self._indent += 1
            for stmt in node.else_body:
                self._emit_stmt(stmt)
            self._indent -= 1
        if node.finally_body:
            self._line('finally:')
            self._indent += 1
            for stmt in node.finally_body:
                self._emit_stmt(stmt)
            self._indent -= 1

    def _emit_yield(self, node: YieldNode):
        if node.value:
            val = self._emit_expr(node.value)
            self._line(f'yield {val}')
        else:
            self._line('yield')

    def _emit_yield_from(self, node: YieldFromNode):
        val = self._emit_expr(node.value)
        self._line(f'yield from {val}')

    def _emit_augmented_assignment(self, node: AugmentedAssignmentNode):
        target = self._emit_expr(node.target)
        value = self._emit_expr(node.value)
        self._line(f'{target} {node.operator} {value}')

    def _emit_match(self, node):
        # V6.0: dukung pola modern (list/objek/binding + guard).
        val = self._emit_expr(node.value)
        guards = getattr(node, 'guards', None) or [None] * len(node.cases)
        first = True
        for idx, (pattern, body) in enumerate(node.cases):
            if isinstance(pattern, WildcardNode):
                self._line('else:')
            else:
                kw = 'if' if first else 'elif'
                cond = self._emit_pattern_condition(pattern, val)
                guard = guards[idx] if idx < len(guards) else None
                if guard is not None:
                    g = self._emit_expr(guard)
                    cond = f'{cond} and ({g})'
                self._line(f'{kw} {cond}:')
                first = False
            self._indent += 1
            if not body:
                self._line('pass')
            else:
                for stmt in body:
                    self._emit_stmt(stmt)
            self._indent -= 1
        if node.default_case:
            self._line('else:')
            self._indent += 1
            for stmt in node.default_case:
                self._emit_stmt(stmt)
            self._indent -= 1

    def _emit_pattern_condition(self, pattern, val: str) -> str:
        """Buat kondisi Python untuk pola match (v6.0).

        - DestructuringPatternNode [a, b]  : type check + panjang + binding
        - ObjectPatternNode {"x": a}       : dict + kunci + binding
        - BindingPatternNode nama          : selalu cocok, bind nilai
        - lainnya                          : perbandingan nilai (perilaku lama)
        """
        bindings = getattr(self, '_match_bindings', None)
        if isinstance(pattern, DestructuringPatternNode):
            if pattern.is_array:
                conds = [
                    f'isinstance({val}, (list, tuple))',
                    f'len({val}) == {len(pattern.variables)}',
                ]
                for i, var in enumerate(pattern.variables):
                    # Kurung luar penting: tanpa kurung, precedence Python
                    # (`and` > `or`) membuat `or True` men-short-circuit
                    # binding berikutnya di dalam satu kondisi gabungan.
                    conds.append(f'(({var} := {val}[{i}]) is not None or True)')
                return ' and '.join(conds)
            conds = [f'isinstance({val}, dict)']
            for var in pattern.variables:
                conds.append(f'(({var} := {val}.get({var!r}, _brolang_nomatch)) != _brolang_nomatch)')
            return ' and '.join(conds)
        if isinstance(pattern, ObjectPatternNode):
            conds = [f'isinstance({val}, dict)']
            for key, entry in pattern.entries.items():
                if isinstance(entry, tuple) and entry[0] == 'lit':
                    conds.append(f'{val}.get({key!r}) == {entry[1]!r}')
                elif isinstance(entry, tuple) and entry[0] == 'var':
                    conds.append(f'(({entry[1]} := {val}.get({key!r})) is not None or True)')
                else:
                    conds.append(f'(({entry} := {val}.get({key!r})) is not None or True)')
            return ' and '.join(conds)
        if isinstance(pattern, BindingPatternNode):
            return f'(({pattern.name} := {val}) is not None) or True'
        pat = self._emit_expr(pattern)
        return f'{val} == {pat}'

    def _emit_enum(self, node: EnumNode):
        self._line(f'class {node.name}:')
        self._indent += 1
        if not node.members:
            self._line('pass')
        else:
            for m in node.members:
                self._line(f'{m} = "{m}"')
        self._indent -= 1
        self._blank()

    def _emit_struct(self, node: StructNode):
        fields = ', '.join(node.fields)
        self._line(f'from dataclasses import dataclass')
        self._line(f'@dataclass')
        self._line(f'class {node.name}:')
        self._indent += 1
        for f in node.fields:
            self._line(f'{f}: object = None')
        if not node.fields:
            self._line('pass')
        self._indent -= 1
        self._blank()

    def _emit_struct_instance_stmt(self, node: StructInstanceNode):
        args = ', '.join(self._emit_expr(a) for a in node.args)
        self._line(f'{node.struct_name}({args})')

    def _emit_decorated_function(self, node: DecoratedFunctionNode):
        for dec in node.decorators:
            d = self._emit_expr(dec)
            self._line(f'@{d}')
        params = ', '.join(node.params)
        rest_param = getattr(node, 'rest_param', None)
        if rest_param:
            params = f'*{rest_param}' if not params else f'{params}, *{rest_param}'
        self._line(f'def {node.name}({params}):')
        self._indent += 1
        if rest_param:
            # Konsisten dengan interpreter (list, bukan tuple dari *args)
            self._line(f'{rest_param} = list({rest_param})')
        if not node.body:
            self._line('pass')
        else:
            for stmt in node.body:
                self._emit_stmt(stmt)
        self._indent -= 1
        self._blank()

    def _emit_decorated_class(self, node: DecoratedClassNode):
        for dec in node.decorators:
            d = self._emit_expr(dec)
            self._line(f'@{d}')
        parent = f'({node.parent})' if node.parent else ''
        self._line(f'class {node.name}{parent}:')
        self._indent += 1
        if not node.body:
            self._line('pass')
        else:
            for stmt in node.body:
                self._emit_stmt(stmt)
        self._indent -= 1
        self._blank()

    def _emit_async_function(self, node: AsyncFunctionDefNode):
        """Async function (v7.0: async sejati, konsisten dengan interpreter).

        Body ditulis sebagai nested function `_brolang_async_body`, lalu
        pemanggilan membungkusnya menjadi Tugas background thread via
        `_brolang_async_run` — pemanggil tidak diblokir, dan `tunggu`
        memblokir sampai selesai (lihat helper runtime).
        """
        params = self._emit_params_with_defaults(node)
        call_args = ', '.join(node.params)
        rest_param = getattr(node, 'rest_param', None)
        if rest_param:
            call_args = f'{call_args}, *{rest_param}' if call_args else f'*{rest_param}'
        self._line(f'def {node.name}({params}):')
        self._indent += 1
        self._line(f'def _brolang_async_body({params}):')
        self._indent += 1
        if rest_param:
            self._line(f'{rest_param} = list({rest_param})')
        if not node.body:
            self._line('pass')
        else:
            for stmt in node.body:
                self._emit_stmt(stmt)
        self._indent -= 1
        self._line(f'return _brolang_async_run(_brolang_async_body, {call_args})')
        self._indent -= 1
        self._blank()

    def _emit_params_with_defaults(self, node) -> str:
        """Buat daftar parameter dengan default value: 'a, b=0, c="x"'.
        v6.7: rest parameter '...sisa' -> '*sisa'."""
        params = []
        defaults = getattr(node, 'defaults', None) or []
        for i, name in enumerate(node.params):
            if i < len(defaults) and defaults[i] is not None:
                default_expr = self._emit_expr(defaults[i])
                params.append(f'{name}={default_expr}')
            else:
                params.append(name)
        rest_param = getattr(node, 'rest_param', None)
        if rest_param:
            params.append(f'*{rest_param}')
        return ', '.join(params)

    def _emit_destructuring_assignment(self, node: DestructuringAssignmentNode):
        targets = ', '.join(node.targets)
        value = self._emit_expr(node.value)
        if node.is_array:
            self._line(f'{targets} = {value}')
        else:
            # Objek: bongkar per kunci (pakai .get agar konsisten dengan
            # interpreter yang memberi None untuk kunci yang tidak ada)
            parts = ', '.join(f'{value}.get({t!r}, None)' for t in node.targets)
            self._line(f'{targets} = {parts}')

    def _emit_with(self, node: WithNode):
        # v7.2: pakai helper _brolang_with supaya `masuk`/`keluar` (method
        # BroLang) dan `__enter__`/`__exit__` (protocol Python) sama-sama
        # berfungsi — konsisten dengan interpreter & VM.
        ctx = self._emit_expr(node.context_expr)
        if node.as_name:
            self._line(f'with _brolang_with({ctx}) as {node.as_name}:')
        else:
            self._line(f'with _brolang_with({ctx}):')
        self._indent += 1
        if not node.body:
            self._line('pass')
        else:
            for stmt in node.body:
                self._emit_stmt(stmt)
        self._indent -= 1

    def _emit_namespace(self, node: NamespaceNode):
        self._line(f'class {node.name}:')
        self._indent += 1
        if not node.body:
            self._line('pass')
        else:
            for stmt in node.body:
                self._emit_stmt(stmt)
        self._indent -= 1
        self._blank()

    def _emit_macro_call(self, node: MacroCallNode):
        args = ', '.join(self._emit_expr(a) for a in node.args)
        self._line(f'{node.name}({args})')

    def _emit_abstract_class(self, node: AbstractClassNode):
        parent = f'({node.parent})' if node.parent else ''
        self._line(f'from abc import ABC, abstractmethod')
        self._line(f'class {node.name}(ABC){parent}:')
        self._indent += 1
        if node.methods:
            for method in node.methods:
                self._emit_method(method)
        elif node.abstract_methods:
            for name in node.abstract_methods:
                self._line('@abstractmethod')
                self._line(f'def {name}(self):')
                self._indent += 1
                self._line('pass')
                self._indent -= 1
                self._blank()
        elif not node.body:
            self._line('pass')
        else:
            for stmt in node.body:
                self._emit_stmt(stmt)
        self._indent -= 1
        self._blank()

    # ==================== Expressions ====================

    def _emit_expr(self, node: ASTNode) -> str:
        if node is None:
            return ''
        if isinstance(node, NumberNode):
            return str(node.value)
        elif isinstance(node, DecimalNode):
            return str(node.value)
        elif isinstance(node, StringNode):
            return f'"{self._escape_string(node.value)}"'
        elif isinstance(node, BooleanNode):
            return 'True' if node.value else 'False'
        elif isinstance(node, KosongNode):
            return 'None'
        elif isinstance(node, IdentifierNode):
            return node.name
        elif isinstance(node, VariableNode):
            return node.name
        elif isinstance(node, BinaryOpNode):
            return self._emit_binary_op(node)
        elif isinstance(node, UnaryOpNode):
            return self._emit_unary_op(node)
        elif isinstance(node, CallNode):
            return self._emit_call(node)
        elif isinstance(node, AttributeNode):
            obj = self._emit_expr(node.object)
            return f'{obj}.{node.attribute}'
        elif isinstance(node, ObjectAccessNode):
            obj = self._emit_expr(node.object)
            return f'{obj}.{node.property}'
        elif isinstance(node, IndexNode):
            return self._emit_index(node)
        elif isinstance(node, ListNode):
            elems = ', '.join(self._emit_list_element(e) for e in node.elements)
            return f'[{elems}]'
        elif isinstance(node, TupleNode):
            elems = ', '.join(self._emit_list_element(e) for e in node.elements)
            if len(node.elements) == 1:
                return f'({elems},)'
            return f'({elems})'
        elif isinstance(node, SetNode):
            elems = ', '.join(self._emit_expr(e) for e in node.elements)
            return f'{{{elems}}}'
        elif isinstance(node, ObjectNode):
            pairs = []
            for k, v in node.entries.items():
                val = self._emit_expr(v)
                pairs.append(f'"{k}": {val}')
            return '{' + ', '.join(pairs) + '}'
        elif isinstance(node, LambdaNode):
            params = ', '.join(node.params)
            rest_param = getattr(node, 'rest_param', None)
            if rest_param:
                # Rest di lambda: bind ulang via walrus agar konsisten dengan
                # interpreter yang memberi list (bukan tuple). Tuple trick
                # `(..., body)[-1]` dipakai agar body falsy (0/""/kosong)
                # tetap menjadi hasil.
                params = f'*{rest_param}' if not node.params else f'{params}, *{rest_param}'
                body = self._emit_expr(node.body)
                return f'(lambda {params}: ({rest_param} := list({rest_param}), {body})[-1])'
            body = self._emit_expr(node.body)
            return f'lambda {params}: {body}'
        elif isinstance(node, ComprehensionNode):
            cond = f' if {self._emit_expr(node.condition)}' if node.condition else ''
            iterable = self._emit_expr(node.iterable)
            expr = self._emit_expr(node.expr)
            return f'[{expr} for {node.variable} in {iterable}{cond}]'
        elif isinstance(node, SetComprehensionNode):
            # v7.2: set comprehension {expr lalu var dalam iterable}
            cond = f' if {self._emit_expr(node.condition)}' if node.condition else ''
            iterable = self._emit_expr(node.iterable)
            expr = self._emit_expr(node.expr)
            return f'{{{expr} for {node.variable} in {iterable}{cond}}}'
        elif isinstance(node, FStringNode):
            return self._emit_fstring(node)
        elif isinstance(node, SpreadNode):
            # Spread di luar konteks list/call (jarang) — perlakuan fallback
            return f'*{self._emit_expr(node.value)}'
        elif isinstance(node, PipelineNode):
            left = self._emit_expr(node.left)
            right = node.right
            if isinstance(right, MapNode):
                func = self._emit_expr(right.function)
                return f'list(map({func}, {left}))'
            if isinstance(right, FilterNode):
                cond = self._emit_expr(right.condition)
                if isinstance(right.condition, LambdaNode):
                    return f'list(filter({cond}, {left}))'
                return f'list(filter(lambda x: {cond}, {left}))'
            if isinstance(right, ReduceNode):
                func = self._emit_expr(right.function)
                if right.initial:
                    return f'__import__("functools").reduce({func}, {left}, {self._emit_expr(right.initial)})'
                return f'__import__("functools").reduce({func}, {left})'
            if isinstance(right, CallNode):
                args = ', '.join([left] + [self._emit_expr(a) for a in right.args])
                func = self._emit_expr(right.function)
                return f'{func}({args})'
            if isinstance(right, LambdaNode):
                body = self._emit_expr(right.body)
                params = ', '.join(right.params)
                return f'(lambda {params}: {body})({left})'
            func = self._emit_expr(right)
            return f'{func}({left})'
        elif isinstance(node, NullCoalescingNode):
            left = self._emit_expr(node.left)
            right = self._emit_expr(node.right)
            return f'({left} if {left} is not None else {right})'
        elif isinstance(node, OptionalChainingNode):
            obj = self._emit_expr(node.object)
            return f'getattr({obj}, "{node.property}", None)'
        elif isinstance(node, TernaryNode):
            true_val = self._emit_expr(node.true_value)
            cond = self._emit_expr(node.condition)
            false_val = self._emit_expr(node.false_value)
            return f'({true_val} if {cond} else {false_val})'
        elif isinstance(node, DictComprehensionNode):
            k = self._emit_expr(node.key_expr)
            v = self._emit_expr(node.value_expr)
            iterable = self._emit_expr(node.iterable)
            cond = f' if {self._emit_expr(node.condition)}' if node.condition else ''
            return f'{{{k}: {v} for {node.key_var} in {iterable}{cond}}}'
        elif isinstance(node, WalrusNode):
            val = self._emit_expr(node.value)
            return f'({node.name} := {val})'
        elif isinstance(node, MapNode):
            iterable = self._emit_expr(node.iterable)
            func = self._emit_expr(node.function)
            return f'list(map({func}, {iterable}))'
        elif isinstance(node, FilterNode):
            iterable = self._emit_expr(node.iterable)
            cond = self._emit_expr(node.condition)
            if isinstance(node.condition, LambdaNode):
                return f'list(filter({cond}, {iterable}))'
            return f'list(filter(lambda x: {cond}, {iterable}))'
        elif isinstance(node, ReduceNode):
            iterable = self._emit_expr(node.iterable)
            func = self._emit_expr(node.function)
            initial = self._emit_expr(node.initial) if node.initial else ''
            if initial:
                return f'__import__("functools").reduce({func}, {iterable}, {initial})'
            return f'__import__("functools").reduce({func}, {iterable})'
        elif isinstance(node, ChainedComparisonNode):
            parts = [self._emit_expr(node.left)]
            for op, comp in zip(node.operators, node.comparators):
                parts.append(op)
                parts.append(self._emit_expr(comp))
            return ' '.join(parts)
        elif isinstance(node, AwaitNode):
            val = self._emit_expr(node.value)
            # v7.0: tunggu memblokir sampai Tugas selesai (nilai non-Tugas
            # dikembalikan apa adanya) — lihat helper runtime `_brolang_await`.
            return f'_brolang_await({val})'
        elif isinstance(node, InputNode):
            if node.prompt:
                prompt = self._emit_expr(node.prompt)
                return f'input({prompt})'
            return 'input()'
        elif isinstance(node, StructInstanceNode):
            args = ', '.join(self._emit_expr(a) for a in node.args)
            return f'{node.struct_name}({args})'
        elif isinstance(node, MatchResultNode):
            return f'_match_result({self._emit_expr(node.value)})'
        elif isinstance(node, ResultNode):
            val = self._emit_expr(node.value)
            if node.is_success:
                return f'("ok", {val})'
            return f'("err", {val})'
        elif isinstance(node, OptionNode):
            if node.has_value and node.value:
                return f'("some", {self._emit_expr(node.value)})'
            return '("none", None)'
        elif isinstance(node, ErrorPropagationNode):
            # Error propagation (v7.0): ekspresi? — helper membuka
            # Result/Option dan melempar error untuk Salah/Kosong.
            return f'_brolang_propagate({self._emit_expr(node.value)})'
        elif isinstance(node, NullSafeIndexNode):
            # Null-safe indexing (v7.2): arr?[0] — kosong bila target kosong
            # atau indeks di luar jangkauan. Untuk dict, cek kunci dengan in.
            target = self._emit_expr(node.target)
            index = self._emit_expr(node.index)
            return (f'(None if {target} is None else '
                    f'({target}[{index}] '
                    f'if {index} in {target} or '
                    f'(type({index}) is int and 0 <= {index} < len({target})) '
                    f'else None))')
        elif isinstance(node, SwitchExprNode):
            # Switch expression (v7.0): cocokkan x { pola: ekspresi } — bernilai.
            # Emit IIFE: (lambda _sv: hasil if kondisi else ...)(x)
            val = self._emit_expr(node.value)
            parts = []
            for pattern, body in node.cases:
                body_expr = self._emit_expr(body[0]) if body else 'None'
                if isinstance(pattern, WildcardNode):
                    parts.append(body_expr)
                else:
                    cond = self._emit_pattern_condition(pattern, '_sv')
                    parts.append(f'({body_expr}) if ({cond}) else')
            if node.default_case is not None:
                parts.append(self._emit_expr(node.default_case))
            else:
                parts.append('None')
            return '(lambda _sv: ' + ' '.join(parts) + f')({val})'
        else:
            return f'# unsupported: {type(node).__name__}'

    def _emit_binary_op(self, node: BinaryOpNode) -> str:
        left = self._emit_expr(node.left)
        right = self._emit_expr(node.right)

        # BroLang operator → Python operator mapping
        op_map = {
            '+': '+', '-': '-', '*': '*', '/': '/', '%': '%', '**': '**',
            '==': '==', '!=': '!=', '>': '>', '>=': '>=', '<': '<', '<=': '<=',
            'dan': 'and', 'atau': 'or',
            'adalah': 'is', 'bukan': 'is not',
            'dalam': 'in', 'tidak_dalam': 'not in',
            '??': 'if ... else',  # handled separately
        }

        op = node.operator
        if op == '??':
            return f'({left} if {left} is not None else {right})'
        elif op in ('dan', 'atau'):
            py_op = op_map[op]
            return f'({left} {py_op} {right})'
        elif op in op_map:
            return f'({left} {op_map[op]} {right})'
        else:
            return f'({left} {op} {right})'

    def _emit_unary_op(self, node: UnaryOpNode) -> str:
        operand = self._emit_expr(node.operand)
        op_map = {'-': '-', 'bukan': 'not ', 'tidak': 'not '}
        op = op_map.get(node.operator, node.operator)
        return f'({op}{operand})'

    def _emit_list_element(self, node) -> str:
        """Emit satu elemen list — spread `...a` -> `*a` (v6.7)."""
        if isinstance(node, SpreadNode):
            return f'*{self._emit_expr(node.value)}'
        return self._emit_expr(node)

    def _emit_call(self, node: CallNode) -> str:
        func = self._emit_expr(node.function)
        arg_parts = [self._emit_call_arg(a) for a in node.args]
        arg_parts.extend(f'{name}={self._emit_expr(val)}' for name, val in node.kwargs)
        args = ', '.join(arg_parts)

        # Map BroLang builtins to Python equivalents
        builtin_map = {
            'tulis': 'print',
            'panjang': 'len',
            'angka': 'int',
            'teks': 'str',
            'desimal': 'float',
            'benar': 'bool',
            'rentang': 'range',
            'jenis': 'type',
            'tipe': '_brolang_tipe',
            'cek_tipe': '_brolang_cek_tipe',
            'hentikan_iterasi': '_brolang_hentikan_iterasi',
            'masukkan': 'input',
            'gabungkan': '"".join',
            'bagi': 'str.split',
            'ganti': 'str.replace',
            'tampilkan': 'print',
        }

        if isinstance(node.function, IdentifierNode):
            name = node.function.name
            if name in builtin_map:
                py_name = builtin_map[name]
                # Handle special cases
                if name == 'gabungkan' and node.args:
                    sep = self._emit_expr(node.args[0])
                    items = self._emit_expr(node.args[1]) if len(node.args) > 1 else '""'
                    return f'{sep}.join({items})'
                return f'{py_name}({args})'

        # Handle method calls on objects with BroLang name mapping
        if isinstance(node.function, ObjectAccessNode):
            obj = self._emit_expr(node.function.object)
            method_name = node.function.property
            method_map = {
                # list
                'tambah': 'append',
                'sisipkan': 'insert',
                'urutkan': 'sort',
                'balik': 'reverse',
                'balikkan': 'reverse',
                'hapus': 'remove',
                'pop': 'pop',
                'indeks': 'index',
                'hitung': 'count',
                'perpanjang': 'extend',
                'jumlah': '__len__',
                'salin': 'copy',
                'kosongkan': 'clear',
                # dict
                'kunci': 'keys',
                'nilai': 'values',
                'item': 'items',
                'dapat': 'get',
                'ambil': 'get',
                'punya': '__contains__',
                'perbarui': 'update',
                'hapus_kunci': 'pop',
                # string
                'panjang': '__len__',
                'potong': 'split',
                'atas': 'upper',
                'bawah': 'lower',
            }
            # Jangan map kalau objeknya modul hasil impor (mis. teks.potong)
            # — atribut modul adalah fungsi utuh, bukan method string/list.
            is_module_attr = (isinstance(node.function.object, IdentifierNode)
                              and node.function.object.name in self._modules)
            if method_name in method_map and not is_module_attr:
                py_method = method_map[method_name]
                # v7.1: panggil method BroLang asli bila ada (mis. method
                # stdlib seperti GrupSprite.kosongkan) — fallback ke method
                # Python builtin (mis. list.clear). Konsisten dengan
                # interpreter yang mencoba getattr(obj, nama) lebih dulu.
                # v7.2: urutkan/balik/balikkan interpreter MENGEMBALIKAN
                # list (bukan None seperti sort()/reverse() Python) —
                # tambahkan `or _o` supaya hasilnya konsisten.
                if method_name in ('urutkan', 'balik', 'balikkan'):
                    return (f'(lambda _o: _o.{method_name}() '
                            f'if hasattr(_o, {method_name!r}) else '
                            f'(_o.{py_method}() or _o))({obj})')
                # v7.2: kunci/nilai/item interpreter mengembalikan LIST
                # (bukan view dict_keys/dict_values) — bungkus list() agar
                # konsisten (mis. d.kunci() -> ['a', 'b']).
                if method_name in ('kunci', 'nilai', 'item'):
                    return (f'(lambda _o: _o.{method_name}() '
                            f'if hasattr(_o, {method_name!r}) else '
                            f'list(_o.{py_method}()))({obj})')
                return (f'(lambda _o: _o.{method_name}({args}) '
                        f'if hasattr(_o, {method_name!r}) else '
                        f'_o.{py_method}({args}))({obj})')

        return f'{func}({args})'

    def _emit_call_arg(self, node) -> str:
        """Emit satu argumen call — spread `...a` -> `*a` (v6.7)."""
        if isinstance(node, SpreadNode):
            return f'*{self._emit_expr(node.value)}'
        return self._emit_expr(node)

    def _emit_index(self, node: IndexNode) -> str:
        target = self._emit_expr(node.target)
        if node.is_slice:
            # Slicing asli: target[start:stop:step] — bukan string berisi ':.'
            start = self._emit_expr(node.slice_start) if node.slice_start else ''
            stop = self._emit_expr(node.slice_stop) if node.slice_stop else ''
            step = self._emit_expr(node.slice_step) if node.slice_step else ''
            return f'{target}[{start}:{stop}:{step}]'
        idx = self._emit_expr(node.index)
        return f'{target}[{idx}]'

    @staticmethod
    def _escape_string(value: str) -> str:
        """Escape string untuk output Python (v7.0 fix).

        Lexer sudah menerjemahkan escape (`\n`, `\t`, ...) menjadi karakter
        asli, jadi saat ditulis ulang sebagai literal Python perlu di-escape
        lagi — sebelumnya `tulis "a\nb"` menghasilkan newline literal di
        tengah string Python (SyntaxError).
        """
        return (
            value.replace('\\', '\\\\')
            .replace('"', '\\"')
            .replace('\n', '\\n')
            .replace('\r', '\\r')
            .replace('\t', '\\t')
            .replace('\0', '\\0')
        )

    def _emit_fstring(self, node: FStringNode) -> str:
        parts = []
        for ptype, pval in node.parts:
            if ptype == 'literal':
                parts.append(self._escape_string(pval))
            elif ptype == 'expr':
                code = self._emit_expr(pval)
                parts.append(f'{{{code}}}')
            elif ptype == 'dollar_var':
                parts.append(f'{{{pval}}}')
        return 'f"' + ''.join(parts) + '"'
