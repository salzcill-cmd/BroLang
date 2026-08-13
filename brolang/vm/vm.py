"""
Bytecode Virtual Machine untuk BroLang
=======================================

Stack-based VM yang mengeksekusi bytecode yang dikompilasi oleh Compiler.
"""

from typing import Any, List, Dict, Optional, Callable
from brolang.vm.opcodes import Op, Bytecode, Instruction
from brolang.exceptions import RuntimeError_, NameError_, TypeError_
from brolang.interpreter.builtins import BUILTINS
from brolang.ast.nodes import (
    DestructuringPatternNode, ObjectPatternNode, BindingPatternNode, WildcardNode,
)


class _Missing:
    """Sentinel untuk cache lookup yang miss."""

    __slots__ = ()

    def __bool__(self):
        return False


_MISSING = _Missing()


def _vm_jenis(exc, nama: str) -> bool:
    """Helper `kecuali Tipe` (v7.0): apakah exception cocok dengan nama tipe.

    - Tipe Python langsung (RuntimeError_, TypeError_, NameError_, ...).
    - Kelas error kustom BroLang (subclass RuntimeError_ / Kesalahan).
    """
    t = type(exc)
    if t.__name__ == nama:
        return True
    return any(c.__name__ == nama for c in t.__mro__)


def _vm_switch_match(value, pattern):
    """Cocokkan nilai dengan pola switch expression (v7.0) di VM.

    Kembalikan dict binding bila cocok (bisa kosong), atau False bila tidak
    cocok — semantik identik dengan `_match_pattern` interpreter.
    """
    if isinstance(pattern, DestructuringPatternNode):
        if pattern.is_array:
            if not isinstance(value, (list, tuple)) or len(value) != len(pattern.variables):
                return False
            return {var: item for var, item in zip(pattern.variables, value)}
        if not isinstance(value, dict):
            return False
        bindings = {}
        for var in pattern.variables:
            if var not in value:
                return False
            bindings[var] = value[var]
        return bindings
    if isinstance(pattern, ObjectPatternNode):
        if not isinstance(value, dict):
            return False
        bindings = {}
        for key, entry in pattern.entries.items():
            if key not in value:
                return False
            if isinstance(entry, tuple) and entry[0] == "var":
                bindings[entry[1]] = value[key]
            elif isinstance(entry, tuple) and entry[0] == "lit":
                if value[key] != entry[1]:
                    return False
            else:
                bindings[entry] = value[key]
        return bindings if bindings else True  # {} falsy → pakai True
    if isinstance(pattern, BindingPatternNode):
        return {pattern.name: value}
    if isinstance(pattern, WildcardNode):
        return True  # cocok tanpa binding ({ } falsy — jangan dipakai)
    # Pola literal/ekspresi (perilaku lama): nilai pola sudah dievaluasi
    # compiler (`Warna.MERAH` -> anggota enum, angka, teks, ...)
    return value == pattern


def _vm_propagate(v):
    """Helper error propagation '?' (v7.0) di VM.

    Identik dengan interpreter (`visit_ErrorPropagationNode`):
        Benar(v)? -> v | Salah(e)? -> lempar e
        Ada(v)?   -> v | Kosong()? -> lempar error
    Nilai non-Result/Option (angka, teks, list, ...) dikembalikan apa
    adanya (no-op) — aman untuk primitif seperti `7?`.
    """
    if isinstance(v, dict) and v.get("type") == "Result":
        if v.get("is_success"):
            return v.get("value")
        err = v.get("value")
        if isinstance(err, Exception):
            raise err
        raise RuntimeError_(
            message=str(err) if err is not None else "Error tanpa pesan"
        )
    if isinstance(v, dict) and v.get("type") == "Option":
        if v.get("has_value"):
            return v.get("value")
        raise RuntimeError_(
            message="Nilai kosong (Kosong()) — tidak bisa di-unwrap dengan '?'."
        )
    return v


def _vm_tunggu(v):
    """Helper `tunggu` di VM (v7.0): blokir sampai Tugas selesai.

    Tugas VM sudah selesai (body dieksekusi sinkron) → langsung kembalikan
    hasilnya. Nilai non-Tugas dikembalikan apa adanya (no-op), konsisten
    dengan interpreter & transpiler.
    """
    if hasattr(v, 'tunggu') and callable(v.tunggu):
        return v.tunggu()
    return v


class _VmTugas:
    """Tugas asinkron di VM (v7.0).

    VM tidak punya event loop — body fungsi asinkron dieksekusi sinkron,
    hasilnya langsung dibungkus Tugas yang sudah selesai. API konsisten
    dengan interpreter (`selesai`, `hasil`, `tunggu`, `batal`) sehingga
    program yang memakai `asinkron fungsi` + `tunggu` bisa dijalankan
    di semua mesin.
    """

    __slots__ = ("_value",)

    def __init__(self, value):
        self._value = value

    def selesai(self) -> bool:
        return True

    def hasil(self, timeout=None):
        return self._value

    def tunggu(self, timeout=None):
        return self._value

    def batal(self) -> bool:
        return False


class _VmKwargs(dict):
    """Marker: dict keyword-argumen (v7.1).

    Compiler membungkus kwargs sebagai dict `{nama: nilai}` lalu menandai
    dengan helper `_vm_kwargs` agar VM tahu itu keyword-argumen — bukan
    dict posisional biasa. `_call_function` membedakan keduanya:
        f(a, b=1)   -> f(a, **_VmKwargs({'b': 1}))
        f(a, {'b': 1}) -> f(a, {'b': 1})  (dict posisional apa adanya)
    """


def _vm_kwargs(d):
    """Helper `_vm_kwargs` di VM (v7.1): tandai dict sebagai kwargs."""
    return _VmKwargs(d)


def _vm_comp_append(lst, value):
    """Helper list comprehension di VM (v7.2): append & kembalikan list."""
    lst.append(value)
    return lst


def _vm_dict_set(d, key, value):
    """Helper dict comprehension di VM (v7.2): set item & kembalikan dict."""
    d[key] = value
    return d


def _vm_set_add(s, value):
    """Helper set comprehension di VM (v7.2): tambah & kembalikan set."""
    s.add(value)
    return s


def _vm_with_enter(context):
    """Helper `dengan` di VM (v7.2): panggil __enter__/masuk bila ada.

    Mirror interpreter: bila context punya `__enter__`/`masuk`, hasilnya
    jadi nilai yang di-bind ke variabel; selain itu context sendiri.
    (Untuk VMInstance, VM mendaftarkan wrapper `_vm_with_enter_vm` yang
    memakai `_call_method` — lihat VM.__init__.)
    """
    if hasattr(context, "__enter__"):
        return context.__enter__()
    if hasattr(context, "masuk"):
        return context.masuk()
    return context


def _vm_with_exit(context):
    """Helper `dengan` di VM (v7.2): panggil __exit__/keluar bila ada."""
    if hasattr(context, "__exit__"):
        context.__exit__(None, None, None)
    elif hasattr(context, "keluar"):
        context.keluar()
    return None


def _vm_make_slice(start, stop, step):
    """Bangun objek slice untuk INDEX_GET (v7.2 fix slicing di VM).

    Nilai None (bagian yang tidak ditulis: `a[1:]`, `a[:3]`, `a[::2]`)
    diteruskan sebagai None supaya Python slice bekerja seperti interpreter.
    """
    return slice(start, stop, step)


_LIST_METHOD_MAP = {
    "tambah": "append",
    "sisipkan": "insert",
    "hapus": "remove",
    "perpanjang": "extend",
    "urutkan": "sort",
    "balik": "reverse",
    "balikkan": "reverse",
    "indeks": "index",
    "hitung": "count",
    "jumlah": "__len__",
    "salin": "copy",
    "kosongkan": "clear",
}

_DICT_METHOD_MAP = {
    "kunci": "keys",
    "nilai": "values",
    "item": "items",
    "dapat": "get",
    "ambil": "get",
    "hapus_kunci": "pop",
    "jumlah": "__len__",
    "punya": "__contains__",
    "perbarui": "update",
    "kosongkan": "clear",
    "salin": "copy",
}

_STR_METHOD_MAP = {
    "atas": "upper",
    "bawah": "lower",
    "kapital": "capitalize",
    "judul": "title",
    "potong": "split",
    "ganti": "replace",
    "cari": "find",
    "mulai": "startswith",
    "berakhir": "endswith",
    "strip": "strip",
    "panjang": "__len__",
}


# Metode yang interpreter KEMBALIKAN hasilnya (bukan None). Python
# sort()/reverse() mengembalikan None — bungkus supaya konsisten.
_RETURN_SELF_METHODS = {"urutkan", "balik", "balikkan"}


def _vm_brolang_method(obj, name):
    """Terjemahkan method BroLang -> method Python untuk list/dict/str
    (v7.2 fix konsistensi VM). Mirip _get_list_methods interpreter.

    Mengembalikan callable atau None bila tidak ada mapping.
    """
    if isinstance(obj, list) and name in _LIST_METHOD_MAP:
        py = _LIST_METHOD_MAP[name]
        fn = getattr(obj, py)
        if name in _RETURN_SELF_METHODS:
            return lambda *a: (fn(*a), obj)[1]
        return fn
    if isinstance(obj, dict) and name in _DICT_METHOD_MAP:
        py = _DICT_METHOD_MAP[name]
        if py == "keys":
            return lambda: list(obj.keys())
        if py == "values":
            return lambda: list(obj.values())
        if py == "items":
            return lambda: list(obj.items())
        if py == "__contains__":
            return lambda k: k in obj
        return getattr(obj, py)
    if isinstance(obj, str) and name in _STR_METHOD_MAP:
        return getattr(obj, _STR_METHOD_MAP[name])
    return None


def _vm_null_safe_index(target, index):
    """Helper null-safe indexing di VM (v7.2): arr?[0]

    Target kosong (None) -> None tanpa error; di luar jangkauan -> None;
    selain itu indexing biasa. Konsisten dengan interpreter.
    """
    if target is None:
        return None
    try:
        return target[index]
    except (TypeError, IndexError, KeyError):
        return None


class Frame:
    """Execution frame — represents one function call."""

    __slots__ = ("bytecode", "ip", "stack", "locals", "parent", "globals", "closure", "yields")

    def __init__(self, bytecode: Bytecode, parent=None, globals_=None, closure=None):
        self.bytecode = bytecode
        self.ip = 0
        self.stack = []
        self.locals = [None] * 64  # Pre-allocate for speed
        self.parent = parent
        self.globals = globals_ or (parent.globals if parent else {})
        self.closure = closure
        # v7.2: buffer nilai `hasilkan` untuk fungsi generator.
        self.yields = []


class VM:
    """Stack-based bytecode virtual machine."""

    __slots__ = ("frames", "globals", "output", "_frame", "_builtin_cache", "_method_cache")

    def __init__(self):
        self.globals: Dict[str, Any] = {}
        self.output: List[str] = []
        self._frame = None
        self._builtin_cache: Dict[str, Any] = {}
        # Cache hasil pencarian method (id(klass), name) -> VMFunction | None.
        # Menghindari rekursi parent-chain berulang untuk pemanggilan method
        # pada inheritance yang dalam (hot path: _get_attribute / _call_method).
        self._method_cache: Dict[Any, Any] = {}

        # Register builtins
        for name, func in BUILTINS.items():
            self.globals[name] = func
            self._builtin_cache[name] = func
        # Helper untuk klausa `kecuali Tipe` (v7.0): cocokkan nama tipe
        # exception (termasuk subkelas RuntimeError_ kustom).
        self.globals["_vm_jenis"] = _vm_jenis
        # Helper `tunggu` (v7.0): buka Tugas -> hasil (no-op untuk nilai biasa).
        self.globals["_vm_tunggu"] = _vm_tunggu
        # Helper error propagation '?' (v7.0): buka Result/Option dict.
        self.globals["_vm_propagate"] = _vm_propagate
        # Helper switch expression (v7.0): cocokkan pola -> dict binding.
        self.globals["_vm_switch_match"] = _vm_switch_match
        # Helper kwargs (v7.1): tandai dict sebagai keyword-argumen.
        self.globals["_vm_kwargs"] = _vm_kwargs
        # Helper comprehension (v7.2): kumpulkan hasil list/dict/set.
        self.globals["_vm_comp_append"] = _vm_comp_append
        self.globals["_vm_dict_set"] = _vm_dict_set
        self.globals["_vm_set_add"] = _vm_set_add
        # Helper `dengan` (v7.2): enter/exit context manager. Untuk
        # VMInstance, method BroLang (masuk/keluar) dipanggil lewat
        # `_call_method` yang punya akses VM.
        def _with_enter_vm(context):
            if hasattr(context, "__enter__"):
                return context.__enter__()
            if isinstance(context, VMInstance) and context.klass.methods.get("masuk"):
                return self._call_method(context, "masuk", [])
            if hasattr(context, "masuk"):
                return context.masuk()
            return context

        def _with_exit_vm(context):
            if hasattr(context, "__exit__"):
                context.__exit__(None, None, None)
            elif isinstance(context, VMInstance) and context.klass.methods.get("keluar"):
                self._call_method(context, "keluar", [])
            elif hasattr(context, "keluar"):
                context.keluar()
            return None

        self.globals["_vm_with_enter"] = _with_enter_vm
        self.globals["_vm_with_exit"] = _with_exit_vm
        # Helper null-safe indexing (v7.2): arr?[0].
        self.globals["_vm_null_safe_index"] = _vm_null_safe_index
        # Helper slicing (v7.2 fix): a[start:stop:step].
        self.globals["_vm_make_slice"] = _vm_make_slice

    def run(self, bytecode: Bytecode) -> Any:
        """Execute compiled bytecode."""
        frame = Frame(bytecode, globals_=self.globals)
        self._frame = frame
        result = self._execute(frame)
        self.globals = frame.globals
        return result

    def _execute(self, frame: Frame) -> Any:
        """Eksekusi dengan exception routing (v7.0 fix try/catch VM).

        Sebelumnya `TRY_PUSH` hanya menaruh marker ("handler", target) di
        stack tanpa pernah dipakai — exception menerobos keluar dan program
        mati. Kini exception dicari handler teratas di stack: stack dipotong
        sampai marker, nilai exception didorong (untuk di-bind catch_var),
        lalu eksekusi dilanjutkan dari target handler.
        """
        while True:
            try:
                return self._run_loop(frame)
            except Exception as e:
                stack = frame.stack
                found = False
                for i in range(len(stack) - 1, -1, -1):
                    entry = stack[i]
                    if isinstance(entry, tuple) and len(entry) == 2 and entry[0] == "handler":
                        target = entry[1]
                        del stack[i:]
                        stack.append(e)
                        frame.ip = target
                        found = True
                        break
                if not found:
                    raise
                # Lanjutkan eksekusi dari handler (loop lagi)

    def _run_loop(self, frame: Frame) -> Any:
        """Main execution loop — the hot path.

        Uses pre-flattened instruction arrays from Bytecode.finalize() for minimal overhead.
        """
        stack = frame.stack
        bc = frame.bytecode
        constants = bc.constants
        names = bc.names
        globals_dict = frame.globals
        ip = frame.ip

        # Use pre-flattened arrays
        ops = bc.ops
        args_arr = bc.args_flat
        lines_arr = bc.lines_flat
        cols_arr = bc.cols_flat
        n = len(ops)

        _locals = frame.locals
        _append = stack.append
        _pop = stack.pop
        _Op = Op

        while ip < n:
            op = ops[ip]
            arg = args_arr[ip]
            ip += 1

            if op == _Op.PUSH_CONST:
                _append(constants[arg])

            elif op == _Op.PUSH_INT_0:
                _append(0)

            elif op == _Op.PUSH_INT_1:
                _append(1)

            elif op == _Op.PUSH_TRUE:
                _append(True)

            elif op == _Op.PUSH_FALSE:
                _append(False)

            elif op == _Op.PUSH_NONE:
                _append(None)

            elif op == _Op.LOAD_LOCAL:
                val = _locals[arg]
                if val is None:
                    raise RuntimeError_(
                        message=f"Variabel lokal belum diinisialisasi (slot {arg}).",
                        line=lines_arr[ip - 1],
                        column=cols_arr[ip - 1],
                    )
                _append(val)

            elif op == _Op.STORE_LOCAL:
                _locals[arg] = _pop()

            elif op == _Op.LOAD_GLOBAL:
                name = names[arg]
                # Fast path: builtin cache (avoid dict lookup)
                cached = self._builtin_cache.get(name, _MISSING)
                if cached is not _MISSING:
                    _append(cached)
                elif name in globals_dict:
                    _append(globals_dict[name])
                else:
                    raise RuntimeError_(
                        message=f"Variabel '{name}' belum didefinisikan.",
                        line=lines_arr[ip - 1],
                        column=cols_arr[ip - 1],
                        solution=f"Deklarasikan '{name}' dengan 'buat {name} = ...'.",
                    )

            elif op == _Op.STORE_GLOBAL:
                globals_dict[names[arg]] = _pop()
                # Invalidate builtin cache jika nama ditimpa oleh user
                self._builtin_cache.pop(names[arg], None)

            elif op == _Op.DEFINE_GLOBAL:
                globals_dict[names[arg]] = _pop()
                # Invalidate builtin cache jika nama ditimpa oleh user
                self._builtin_cache.pop(names[arg], None)

            elif op == _Op.LOAD_DEREF:
                _append(frame.closure[arg] if frame.closure else None)

            elif op == _Op.STORE_DEREF:
                if frame.closure:
                    frame.closure[arg] = stack[-1]

            elif op == _Op.ADD:
                right = _pop()
                _append(_pop() + right)

            elif op == _Op.SUB:
                right = _pop()
                _append(_pop() - right)

            elif op == _Op.MUL:
                right = _pop()
                _append(_pop() * right)

            elif op == _Op.DIV:
                right = _pop()
                _append(_pop() / right)

            elif op == _Op.FLOOR_DIV:  # v6.8: //
                right = _pop()
                _append(_pop() // right)

            elif op == _Op.MOD:
                right = _pop()
                _append(_pop() % right)

            elif op == _Op.POW:
                right = _pop()
                _append(_pop() ** right)

            elif op == _Op.NEG:
                _append(-_pop())

            elif op == _Op.EQ:
                right = _pop()
                _append(_pop() == right)

            elif op == _Op.NEQ:
                right = _pop()
                _append(_pop() != right)

            elif op == _Op.GT:
                right = _pop()
                _append(_pop() > right)

            elif op == _Op.GTE:
                right = _pop()
                _append(_pop() >= right)

            elif op == _Op.LT:
                right = _pop()
                _append(_pop() < right)

            elif op == _Op.LTE:
                right = _pop()
                _append(_pop() <= right)

            elif op == _Op.IS_OP:
                right = _pop()
                _append(_pop() is right)

            elif op == _Op.AND:
                right = _pop()
                _append(_pop() and right)

            elif op == _Op.OR:
                right = _pop()
                _append(_pop() or right)

            elif op == _Op.NOT_OP:
                _append(not _pop())

            elif op == _Op.JUMP:
                ip = arg

            elif op == _Op.POP_JUMP_IF_FALSE:
                if not _pop():
                    ip = arg

            elif op == _Op.JUMP_IF_FALSE:
                if not stack[-1]:
                    ip = arg

            elif op == _Op.JUMP_IF_TRUE:
                if stack[-1]:
                    ip = arg

            elif op == _Op.POP_TOP:
                _pop()

            elif op == _Op.DUP:
                _append(stack[-1])

            elif op == _Op.SWAP:
                stack[-1], stack[-2] = stack[-2], stack[-1]

            elif op == _Op.CLOSURE:
                func_bc_idx, param_count, has_defaults, rest_pos = arg[:4]
                is_async = arg[4] if len(arg) > 4 else False
                param_names = arg[5] if len(arg) > 5 else None  # v7.1
                is_generator = arg[6] if len(arg) > 6 else False  # v7.2
                func_bc = constants[func_bc_idx]
                closure = VMFunction(
                    func_bc, param_count, has_defaults, _locals[: len(_locals)],
                    rest_pos, is_async, param_names, is_generator=is_generator,
                )
                _append(closure)

            elif op == _Op.MAKE_FUNCTION:
                # Gabungkan closure + daftar default parameter (v7.1):
                # Stack: [..., closure, d0, d1, ...] dengan arg = jumlah default.
                defaults = [_pop() for _ in range(arg)][::-1]
                closure = _pop()
                closure.defaults = defaults
                _append(closure)

            elif op == _Op.CALL:
                func = _pop()
                args_list = [_pop() for _ in range(arg)][::-1]
                if isinstance(func, VMClass):
                    instance = VMInstance(func)
                    init_method = self._find_method_on_class(func, "__init__")
                    if init_method:
                        self._call_function(init_method, [instance] + args_list, None)
                    _append(instance)
                else:
                    result = self._call_function(func, args_list, None)
                    # v7.0: fungsi asinkron → hasil dibungkus Tugas (sudah
                    # selesai; VM mengeksekusi body sinkron).
                    if isinstance(func, VMFunction) and func.is_async:
                        result = _VmTugas(result)
                    _append(result)

            elif op == _Op.CALL_BUILTIN:
                func_name, arg_count = arg
                args_list = [_pop() for _ in range(arg_count)][::-1]
                func = self._builtin_cache.get(func_name) or globals_dict[func_name]
                result = self._call_builtin(func, args_list, func_name, None)
                _append(result)

            elif op == _Op.RETURN:
                return _pop()

            elif op == _Op.MAKE_CLASS:
                data = constants[arg]
                name, methods_data = data
                parent = _pop()
                vm_class = VMClass(name, parent, methods_data)
                _append(vm_class)

            elif op == _Op.MAKE_INSTANCE:
                klass = _pop()
                args_list = [_pop() for _ in range(arg)][::-1]
                instance = VMInstance(klass)
                if "__init__" in klass.methods:
                    self._call_method(instance, "__init__", args_list)
                _append(instance)

            elif op == _Op.LOAD_ATTR:
                obj = _pop()
                val = self._get_attribute(obj, names[arg], None)
                _append(val)

            elif op == _Op.STORE_ATTR:
                val = _pop()
                obj = _pop()
                self._set_attribute(obj, names[arg], val, None)
                _append(val)

            elif op == _Op.LOAD_METHOD:
                obj = _pop()
                _append(obj)
                _append(self._get_attribute(obj, names[arg], None))

            elif op == _Op.CALL_METHOD:
                method_name_idx, arg_count = arg
                args_list = [_pop() for _ in range(arg_count)][::-1]
                method = _pop()
                obj = _pop()
                # v7.1: keyword-argumen (marker _VmKwargs) dipisahkan dulu.
                kwargs = None
                if args_list and isinstance(args_list[-1], _VmKwargs):
                    kwargs = dict(args_list[-1])
                    args_list = args_list[:-1]
                if isinstance(method, VMFunction):
                    result = self._call_function(method, [obj] + args_list, None, kwargs=kwargs)
                elif callable(method):
                    # Fungsi Python polos (mis. atribut modul stdlib seperti
                    # event_loop.tidur) tidak terikat objek → jangan oper `obj`;
                    # bound method Python sudah membawa self sendiri.
                    if kwargs:
                        result = method(*args_list, **kwargs)
                    else:
                        result = method(*args_list)
                else:
                    result = method
                _append(result)

            elif op == _Op.GET_ITER:
                stack[-1] = iter(stack[-1])

            elif op == _Op.FOR_ITER:
                try:
                    _append(next(stack[-1]))
                except StopIteration:
                    ip = arg
                    _pop()

            elif op == _Op.YIELD:
                # v7.2: hasilkan nilai — append ke buffer generator frame.
                frame.yields.append(_pop())

            elif op == _Op.YIELD_FROM:
                # v7.2: hasilkan semua nilai dari iterable.
                iterable = _pop()
                try:
                    frame.yields.extend(list(iterable))
                except TypeError:
                    raise RuntimeError_(
                        message=f"Objek '{iterable}' tidak bisa di-iterasi untuk hasilkandari."
                    )

            elif op == _Op.MAKE_LIST:
                _append([_pop() for _ in range(arg)][::-1])

            elif op == _Op.BUILD_LIST_SPREAD:
                # arg = jumlah pasangan (is_spread, value) di stack.
                # Stack: [..., is_spread, value] per pasangan (teratas = terakhir).
                # Kumpulkan lalu balik supaya urutan elemen benar.
                pairs = []
                for _ in range(arg):
                    value = _pop()
                    is_spread = _pop()
                    pairs.append((is_spread, value))
                pairs.reverse()
                result = []
                for is_spread, value in pairs:
                    if is_spread:
                        result.extend(value)
                    else:
                        result.append(value)
                _append(result)

            elif op == _Op.CALL_SPREAD:
                # Stack: [..., arg_list, func]
                func = _pop()
                args_list = _pop()
                if isinstance(func, VMClass):
                    instance = VMInstance(func)
                    init_method = self._find_method_on_class(func, "__init__")
                    if init_method:
                        self._call_function(init_method, [instance] + args_list, None)
                    _append(instance)
                else:
                    result = self._call_function(func, args_list, None)
                    _append(result)

            elif op == _Op.MAKE_TUPLE:
                _append(tuple([_pop() for _ in range(arg)][::-1]))

            elif op == _Op.MAKE_SET:
                _append(set([_pop() for _ in range(arg)][::-1]))

            elif op == _Op.MAKE_DICT:
                # Kompiler mendorong (kunci, nilai) berurutan; pop membalik
                # urutan, jadi kumpulkan dulu lalu isi dict dari belakang
                # agar urutan kunci dipertahankan (v7.2 fix).
                items = [_pop() for _ in range(arg * 2)][::-1]
                pairs = {}
                for i in range(0, len(items), 2):
                    pairs[items[i]] = items[i + 1]
                _append(pairs)

            elif op == _Op.INDEX_GET:
                index = _pop()
                _append(_pop()[index])

            elif op == _Op.DICT_GET:
                # dict.get(key) dengan default None — dipakai destructuring
                # objek `buat {x, y} = objek` agar kunci yang tidak ada
                # menghasilkan None (konsisten dengan interpreter).
                key = _pop()
                _append(_pop().get(key))

            elif op == _Op.INDEX_SET:
                val = _pop()
                index = _pop()
                target = _pop()
                target[index] = val
                _append(val)

            elif op == _Op.DEL_VAR:
                kind, idx = arg
                if kind == "local":
                    _locals[idx] = None
                else:
                    del globals_dict[names[idx]]

            elif op == _Op.PRINT:
                args_list = [_pop() for _ in range(arg)][::-1]
                self.output.append(" ".join(str(a) for a in args_list))

            elif op == _Op.ASSERT:
                msg = _pop()
                if not _pop():
                    raise RuntimeError_(
                        message=f"Pastikan: {msg}", line=lines_arr[ip - 1], column=cols_arr[ip - 1]
                    )

            elif op == _Op.RAISE:
                val = _pop() if stack else "Error"
                raise RuntimeError_(
                    message=str(val), line=lines_arr[ip - 1], column=cols_arr[ip - 1]
                )

            elif op == _Op.TRY_PUSH:
                _append(("handler", arg))

            elif op == _Op.TRY_POP:
                if stack and isinstance(stack[-1], tuple):
                    _pop()

            elif op == _Op.IMPORT:
                module_path, attr_name = arg
                try:
                    mod = self._do_import(module_path)
                    if attr_name:
                        _append(getattr(mod, attr_name, None))
                    else:
                        _append(mod)
                except Exception:
                    _append(None)

            elif op == _Op.FSTRING:
                parts = [_pop() for _ in range(arg)][::-1]
                _append("".join(str(p) for p in parts))

            elif op == _Op.AUG_ADD:
                right = _pop()
                _append(_pop() + right)

            elif op == _Op.AUG_SUB:
                right = _pop()
                _append(_pop() - right)

            elif op == _Op.AUG_MUL:
                right = _pop()
                _append(_pop() * right)

            elif op == _Op.AUG_DIV:
                right = _pop()
                _append(_pop() / right)

            elif op == _Op.AUG_FLOOR_DIV:  # v6.8: x //= y
                right = _pop()
                _append(_pop() // right)

            elif op == _Op.AUG_MOD:
                right = _pop()
                _append(_pop() % right)

            elif op == _Op.AUG_POW:
                right = _pop()
                _append(_pop() ** right)

            elif op == _Op.NOP:
                pass

            elif op == _Op.HALT:
                break

        frame.ip = ip
        return stack[-1] if stack else None

    # ============= Function Calls =============

    def _call_function(self, func, args, instr=None, kwargs=None):
        """Call a VM function."""
        # v7.1: pisahkan keyword-argumen (marker _VmKwargs) dari argumen
        # posisional — konsisten dengan interpreter (`f(a, b=1)`).
        if kwargs is None and args and isinstance(args[-1], _VmKwargs):
            kwargs = dict(args[-1])
            args = args[:-1]

        if callable(func) and not isinstance(func, VMFunction):
            try:
                if kwargs:
                    return func(*args, **kwargs)
                return func(*args)
            except Exception as e:
                if isinstance(e, (RuntimeError_, TypeError_, NameError_)):
                    raise
                raise RuntimeError_(message=str(e))

        if not isinstance(func, VMFunction):
            raise RuntimeError_(
                message=f"'{func}' bukan fungsi yang bisa dipanggil.",
                line=getattr(instr, "line", 0) if instr else 0,
                column=getattr(instr, "column", 0) if instr else 0,
            )

        # VMFunction: ikat keyword-argumen berdasarkan nama parameter
        # (v7.1) — konsisten dengan interpreter `_bind_params`.
        if kwargs:
            names = func.get_param_names()
            args = list(args)
            for key, val in kwargs.items():
                if key not in names:
                    raise RuntimeError_(
                        message=f"Keyword argument '{key}' tidak dikenal.",
                        line=getattr(instr, "line", 0) if instr else 0,
                        column=getattr(instr, "column", 0) if instr else 0,
                    )
                idx = names.index(key)
                while len(args) <= idx:
                    args.append(None)
                args[idx] = val

        # Create new frame (v7.2: generator memakai buffer yield frame)
        new_frame = Frame(
            func.bytecode, parent=self._frame, globals_=self._frame.globals, closure=func.closure
        )
        if func.is_generator:
            new_frame.yields = []

        # Bind parameters by index (params occupy slots 0..param_count-1).
        # v7.1: argumen yang tidak diberikan diisi nilai default bila ada
        # (konsisten dengan interpreter `_bind_params`).
        args = list(args)
        defaults = func.defaults
        for i in range(func.param_count):
            if i < len(args):
                new_frame.locals[i] = args[i]
            elif defaults and i < len(defaults) and defaults[i] is not None:
                new_frame.locals[i] = defaults[i]
            else:
                new_frame.locals[i] = None

        # v6.7: rest parameter — semua argumen yang tidak terikat ke param
        # biasa (indeks >= jumlah param regular) dikumpulkan menjadi list.
        if func.rest_pos >= 0:
            new_frame.locals[func.rest_pos] = list(args[func.rest_pos:])

        # Execute
        old_frame = self._frame
        self._frame = new_frame
        try:
            result = self._execute(new_frame)
        finally:
            self._frame = old_frame

        # v7.2: generator — hasil pemanggilan adalah daftar nilai `hasilkan`
        # (konsisten dengan interpreter yang mengumpulkan semua yield).
        if func.is_generator:
            return new_frame.yields

        return result

    def _call_method(self, obj, method_name, args):
        """Call a method on an object."""
        if isinstance(obj, VMInstance):
            method = self._find_method_on_class(obj.klass, method_name)
            if method:
                return self._call_function(method, [obj] + args)
        raise RuntimeError_(message=f"Method '{method_name}' tidak ditemukan.")

    def _find_method_on_class(self, klass, method_name):
        """Find a method on a class, walking up the parent chain.

        Hasil di-cache per (kelas, nama) sehingga pencarian berulang pada
        inheritance yang dalam tidak mengulang traversal parent-chain.
        Key memakai objek kelas (bukan id()) agar tidak tabrakan bila
        kelas lama di-GC dan id-nya dipakai ulang.
        """
        key = (klass, method_name)
        cached = self._method_cache.get(key, _MISSING)
        if cached is not _MISSING:
            return cached
        method = self._find_method_on_class_uncached(klass, method_name)
        self._method_cache[key] = method
        return method

    def _find_method_on_class_uncached(self, klass, method_name):
        """Pencarian method tanpa cache (traversal parent chain)."""
        if method_name in klass.methods:
            return klass.methods[method_name]
        if klass.parent:
            return self._find_method_on_class_uncached(klass.parent, method_name)
        return None

    def _call_builtin(self, func, args, name, instr=None):
        """Call a builtin function."""
        try:
            return func(*args)
        except Exception as e:
            if isinstance(e, (RuntimeError_, TypeError_, NameError_)):
                raise
            raise RuntimeError_(
                message=f"Error di builtin '{name}': {e}",
                line=getattr(instr, "line", 0) if instr else 0,
                column=getattr(instr, "column", 0) if instr else 0,
            )

    # ============= Attribute Access =============

    def _get_attribute(self, obj, name, instr=None):
        """Get attribute from an object."""
        if isinstance(obj, VMInstance):
            # Check instance dict first
            if name in obj.dict:
                return obj.dict[name]
            # Check class methods
            if name in obj.klass.methods:
                method = obj.klass.methods[name]
                if isinstance(method, VMFunction):
                    return method
                if isinstance(method, tuple):
                    # (bytecode, is_static, param_count, rest_pos, param_names)
                    bc, is_static = method[0], method[1]
                    param_count = method[2] if len(method) > 2 else 0
                    rest_pos = method[3] if len(method) > 3 else -1
                    pnames = method[4] if len(method) > 4 else None
                    func = VMFunction(bc, param_count, False, [], rest_pos, False, pnames)
                    if not is_static:
                        return lambda *a: self._call_function(func, [obj] + list(a))
                    return lambda *a: self._call_function(func, list(a))
                return method
            # Check parent class
            if obj.klass.parent:
                return self._get_attribute(obj.klass.parent, name, instr)
            # Built-in get/set
            if name == "get":
                return lambda n: (
                    self._get_attribute(obj, n, instr) if n in obj.dict else obj.dict.get(n)
                )
            if name == "set":

                def _set(n, v):
                    obj.dict[n] = v

                return _set
            raise RuntimeError_(
                message=f"'{obj.klass.name}' tidak memiliki atribut '{name}'.",
                line=getattr(instr, "line", 0) if instr else 0,
                column=getattr(instr, "column", 0) if instr else 0,
            )

        if isinstance(obj, VMClass):
            if name in obj.methods:
                return obj.methods[name]
            if obj.parent:
                return self._get_attribute(obj.parent, name, instr)
            raise RuntimeError_(
                message=f"Kelas '{obj.name}' tidak memiliki method '{name}'.",
                line=getattr(instr, "line", 0) if instr else 0,
            )

        # Dict: kunci diakses via atribut (`Warna.MERAH` untuk enum) —
        # konsisten dengan interpreter visit_ObjectAccessNode.
        if isinstance(obj, dict) and name in obj:
            return obj[name]

        # Python objects — coba atribut asli dulu, lalu method BroLang
        # (list/dict/str) agar konsisten dengan interpreter & transpiler.
        if hasattr(obj, name):
            return getattr(obj, name)
        mapped = _vm_brolang_method(obj, name)
        if mapped is not None:
            return mapped

        raise RuntimeError_(
            message=f"Tidak bisa mengakses '{name}' pada tipe {type(obj).__name__}.",
            line=getattr(instr, "line", 0) if instr else 0,
            column=getattr(instr, "column", 0) if instr else 0,
        )

    def _set_attribute(self, obj, name, val, instr=None):
        """Set attribute on an object."""
        if isinstance(obj, VMInstance):
            obj.dict[name] = val
            return
        if isinstance(obj, VMClass):
            obj.methods[name] = val
            # Monkey-patch: invalidate seluruh cache — method bisa saja
            # terselesaikan lewat parent, sehingga subclass yang sudah
            # meng-cache hasil lama ikut terpengaruh. Cache kecil dan
            # jarang di-patch, jadi clear penuh lebih aman.
            self._method_cache.clear()
            return
        raise RuntimeError_(
            message=f"Tidak bisa mengatur atribut '{name}' pada {type(obj).__name__}."
        )

    def _get_params(self, bytecode):
        """Get parameter names from bytecode (heuristic)."""
        # Count STORE_LOCAL instructions at start
        count = 0
        for instr in bytecode.instructions[:10]:
            if instr.op == Op.STORE_LOCAL and instr.arg == count:
                count += 1
            elif instr.op not in (Op.STORE_LOCAL, Op.NOP):
                break
        return [""] * count

    def _do_import(self, module_path):
        """Import a module."""
        import importlib

        parts = module_path.split(".")
        # Try stdlib first
        try:
            mod = importlib.import_module(f"brolang.stdlib.{parts[0]}")
            return mod
        except ImportError:
            pass
        # Try Python stdlib
        try:
            return importlib.import_module(module_path)
        except ImportError:
            pass
        return None


class VMFunction:
    """Bytecode function object."""

    __slots__ = ("bytecode", "param_count", "has_defaults", "closure", "rest_pos",
                 "is_async", "param_names", "defaults", "is_generator")

    def __init__(self, bytecode, param_count, has_defaults, closure, rest_pos=-1, is_async=False,
                 param_names=None, is_generator=False):
        self.bytecode = bytecode
        self.param_count = param_count
        self.has_defaults = has_defaults
        self.closure = closure
        self.rest_pos = rest_pos  # v6.7: indeks slot rest parameter (-1 = tidak ada)
        self.is_async = is_async  # v7.0: hasil pemanggilan dibungkus Tugas
        # v7.1: nama parameter asli (dari CLOSURE) untuk mengikat keyword
        # argumen. None untuk fungsi lama/kode bytecode tanpa info nama.
        self.param_names = tuple(param_names) if param_names else None
        # v7.1: nilai default parameter (set MAKE_FUNCTION) — panjangnya
        # harus sama dengan param_count; None berarti tanpa default.
        self.defaults = None
        # v7.2: fungsi generator — hasil pemanggilan = list nilai `hasilkan`.
        self.is_generator = is_generator

    def get_param_names(self):
        """Nama parameter asli bila tersedia; fallback ke p0..pN."""
        if self.param_names:
            return list(self.param_names)
        names = []
        for instr in self.bytecode.instructions[: self.param_count + 5]:
            if instr.op == Op.STORE_LOCAL:
                names.append(f"p{instr.arg}")
            if len(names) >= self.param_count:
                break
        return names

    def __repr__(self):
        return f"<VMFunction {self.bytecode}>"


class VMClass:
    """Bytecode class object."""

    __slots__ = ("name", "parent", "methods", "access_map")

    def __init__(self, name, parent, methods_data):
        self.name = name
        self.parent = parent
        self.methods = {}
        self.access_map = {}

        for method_name, method_data in methods_data.items():
            bc, is_static = method_data[0], method_data[1]
            param_count = method_data[2] if len(method_data) > 2 else 0
            rest_pos = method_data[3] if len(method_data) > 3 else -1
            pnames = method_data[4] if len(method_data) > 4 else None
            self.methods[method_name] = VMFunction(bc, param_count, False, [], rest_pos, False, pnames)

    def __repr__(self):
        return f"<VMClass {self.name}>"


class VMInstance:
    """Instance of a VM class."""

    __slots__ = ("klass", "dict")

    def __init__(self, klass):
        self.klass = klass
        self.dict = {}

    def __repr__(self):
        # Struct (kelas yang punya __repr__): tampilkan field sebagai
        # `Titik(x=10, y=20)` — konsisten dengan interpreter & transpiler.
        if "__repr__" in self.klass.methods and self.dict:
            fields = ", ".join(k + "=" + str(v) for k, v in self.dict.items())
            return self.klass.name + "(" + fields + ")"
        return "<" + self.klass.name + " instance>"
