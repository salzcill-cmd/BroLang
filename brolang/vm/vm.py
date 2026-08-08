"""
Bytecode Virtual Machine untuk BroLang
=======================================

Stack-based VM yang mengeksekusi bytecode yang dikompilasi oleh Compiler.
"""

from typing import Any, List, Dict, Optional, Callable
from brolang.vm.opcodes import Op, Bytecode, Instruction
from brolang.exceptions import RuntimeError_, NameError_, TypeError_
from brolang.interpreter.builtins import BUILTINS


class _Missing:
    """Sentinel untuk cache lookup yang miss."""

    __slots__ = ()

    def __bool__(self):
        return False


_MISSING = _Missing()


class Frame:
    """Execution frame — represents one function call."""

    __slots__ = ("bytecode", "ip", "stack", "locals", "parent", "globals", "closure")

    def __init__(self, bytecode: Bytecode, parent=None, globals_=None, closure=None):
        self.bytecode = bytecode
        self.ip = 0
        self.stack = []
        self.locals = [None] * 64  # Pre-allocate for speed
        self.parent = parent
        self.globals = globals_ or (parent.globals if parent else {})
        self.closure = closure


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

    def run(self, bytecode: Bytecode) -> Any:
        """Execute compiled bytecode."""
        frame = Frame(bytecode, globals_=self.globals)
        self._frame = frame
        result = self._execute(frame)
        self.globals = frame.globals
        return result

    def _execute(self, frame: Frame) -> Any:
        """Main execution loop — the hot path.

        Uses pre-flattened instruction arrays from Bytecode.finalize() for minimal overhead.
        """
        stack = frame.stack
        bc = frame.bytecode
        constants = bc.constants
        names = bc.names
        globals_dict = frame.globals
        ip = 0

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
                func_bc_idx, param_count, has_defaults = arg
                func_bc = constants[func_bc_idx]
                closure = VMFunction(func_bc, param_count, has_defaults, _locals[: len(_locals)])
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
                if isinstance(method, VMFunction):
                    result = self._call_function(method, [obj] + args_list, None)
                elif callable(method):
                    result = method(obj, *args_list)
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

            elif op == _Op.MAKE_LIST:
                _append([_pop() for _ in range(arg)][::-1])

            elif op == _Op.MAKE_TUPLE:
                _append(tuple([_pop() for _ in range(arg)][::-1]))

            elif op == _Op.MAKE_SET:
                _append(set([_pop() for _ in range(arg)][::-1]))

            elif op == _Op.MAKE_DICT:
                pairs = {}
                for _ in range(arg):
                    val = _pop()
                    pairs[_pop()] = val
                _append(pairs)

            elif op == _Op.INDEX_GET:
                index = _pop()
                _append(_pop()[index])

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

            elif op == _Op.NOP:
                pass

            elif op == _Op.HALT:
                break

        return stack[-1] if stack else None

    # ============= Function Calls =============

    def _call_function(self, func, args, instr=None):
        """Call a VM function."""
        if callable(func) and not isinstance(func, VMFunction):
            try:
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

        # Create new frame
        new_frame = Frame(
            func.bytecode, parent=self._frame, globals_=self._frame.globals, closure=func.closure
        )

        # Bind parameters by index (params occupy slots 0..param_count-1)
        for i in range(func.param_count):
            if i < len(args):
                new_frame.locals[i] = args[i]

        # Execute
        old_frame = self._frame
        self._frame = new_frame
        try:
            result = self._execute(new_frame)
        finally:
            self._frame = old_frame

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
                if isinstance(method, tuple):
                    # (bytecode, is_static)
                    bc, is_static = method
                    func = VMFunction(bc, len(self._get_params(bc)), False, [])
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

        # Python objects
        if hasattr(obj, name):
            return getattr(obj, name)

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

    __slots__ = ("bytecode", "param_count", "has_defaults", "closure")

    def __init__(self, bytecode, param_count, has_defaults, closure):
        self.bytecode = bytecode
        self.param_count = param_count
        self.has_defaults = has_defaults
        self.closure = closure

    def param_names(self):
        """Extract param names from bytecode."""
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
            self.methods[method_name] = VMFunction(bc, param_count, False, [])

    def __repr__(self):
        return f"<VMClass {self.name}>"


class VMInstance:
    """Instance of a VM class."""

    __slots__ = ("klass", "dict")

    def __init__(self, klass):
        self.klass = klass
        self.dict = {}

    def __repr__(self):
        return f"<{self.klass.name} instance>"
