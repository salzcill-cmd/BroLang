"""
Bytecode Opcodes untuk BroLang VM
==================================

Stack-based bytecode instruction set.
Setiap instruksi: opcode + arg (opsional).
"""

from enum import IntEnum, auto
from dataclasses import dataclass
from typing import Any


class Op(IntEnum):
    """Bytecode opcodes."""
    # Constants
    PUSH_CONST = auto()     # Push constant from pool
    PUSH_TRUE = auto()      # Push True
    PUSH_FALSE = auto()     # Push False
    PUSH_NONE = auto()      # Push None (kosong)
    PUSH_INT_0 = auto()     # Push 0 (fast path)
    PUSH_INT_1 = auto()     # Push 1 (fast path)

    # Variables
    LOAD_LOCAL = auto()     # Load local variable (fast path)
    STORE_LOCAL = auto()    # Store local variable (fast path)
    LOAD_GLOBAL = auto()    # Load global variable
    STORE_GLOBAL = auto()   # Store global variable
    LOAD_DEREF = auto()     # Load closure variable
    STORE_DEREF = auto()    # Store closure variable
    DEFINE_GLOBAL = auto()  # Define new global variable

    # Arithmetic
    ADD = auto()
    SUB = auto()
    MUL = auto()
    DIV = auto()
    FLOOR_DIV = auto()  # v6.8: //
    MOD = auto()
    POW = auto()
    NEG = auto()

    # Comparison
    EQ = auto()
    NEQ = auto()
    GT = auto()
    GTE = auto()
    LT = auto()
    LTE = auto()
    IS_OP = auto()

    # Logic
    AND = auto()
    OR = auto()
    NOT_OP = auto()

    # Control flow
    JUMP = auto()           # Unconditional jump
    JUMP_IF_FALSE = auto()  # Jump if top is false
    JUMP_IF_TRUE = auto()   # Jump if top is true
    POP_JUMP_IF_FALSE = auto()  # Pop and jump if false

    # Stack
    POP_TOP = auto()
    DUP = auto()
    SWAP = auto()

    # Functions
    MAKE_FUNCTION = auto()  # Create function object
    CALL = auto()           # Call function with N args
    RETURN = auto()         # Return from function
    RETURN_CONST = auto()   # Return constant (fast path)
    CLOSURE = auto()        # Create closure

    # Classes
    MAKE_CLASS = auto()     # Create class
    MAKE_INSTANCE = auto()  # Create instance
    LOAD_ATTR = auto()      # Load attribute
    STORE_ATTR = auto()     # Store attribute
    LOAD_METHOD = auto()    # Load method for call
    CALL_METHOD = auto()    # Call method with N args

    # Iteration
    GET_ITER = auto()       # Get iterator
    FOR_ITER = auto()       # Iterator next (JUMP_IF_FALSE on StopIteration)
    LOAD_FAST_ITER = auto() # Fast iterator next

    # Builtins
    CALL_BUILTIN = auto()   # Call builtin function

    # I/O
    PRINT = auto()          # Print (fast path for tulis)

    # Misc
    NOP = auto()
    HALT = auto()           # Stop execution

    # Complex operations (delegate to helper)
    IMPORT = auto()         # Import module
    MAKE_LIST = auto()      # Create list from N elements
    MAKE_TUPLE = auto()     # Create tuple from N elements
    MAKE_SET = auto()       # Create set from N elements
    MAKE_DICT = auto()      # Create dict from N key-value pairs
    INDEX_GET = auto()      # Get index: obj[key]
    INDEX_SET = auto()      # Set index: obj[key] = value
    DICT_GET = auto()       # dict.get(key) dengan default None (v6.7 destructuring objek)
    BUILD_LIST_SPREAD = auto()  # Buat list dari pasangan (is_spread, value) (v6.7)
    CALL_SPREAD = auto()    # Panggil fungsi dengan list argumen (v6.7)
    SLICE = auto()          # Slice operation
    ASSERT = auto()         # Assert statement
    DEL_VAR = auto()        # Delete variable
    RAISE = auto()          # Raise exception
    TRY_PUSH = auto()       # Push exception handler
    TRY_POP = auto()        # Pop exception handler
    FOR_ITER_EX = auto()    # Extended for_iter (for BroLangInstance)

    # String interpolation
    FSTRING = auto()        # Format string

    # Lambda
    MAKE_LAMBDA = auto()    # Create lambda

    # Augmented assignment
    AUG_ADD = auto()        # x += y
    AUG_SUB = auto()        # x -= y
    AUG_MUL = auto()        # x *= y
    AUG_DIV = auto()        # x /= y
    AUG_FLOOR_DIV = auto()  # v6.8: x //= y
    AUG_MOD = auto()        # x %= y
    AUG_POW = auto()        # x **= y
    YIELD = auto()          # v7.2: hasilkan nilai (append ke buffer generator)
    YIELD_FROM = auto()     # v7.2: hasilkan semua nilai dari iterable
    GENERATOR_MAKE = auto() # v7.2: tandai fungsi sebagai generator


@dataclass(slots=True)
class Instruction:
    """A single bytecode instruction."""
    op: Op
    arg: Any = None
    line: int = 0
    column: int = 0

    def __repr__(self):
        if self.arg is not None:
            return f"({self.op.name}, {self.arg})"
        return f"({self.op.name})"


class Bytecode:
    """Compiled bytecode chunk."""

    def __init__(self):
        self.instructions: list[Instruction] = []
        self.constants: list = []
        self.names: list[str] = []       # Global variable names
        self.var_names: list[str] = []    # Local variable names
        self.free_vars: list[str] = []    # Closure variable names

    def add(self, op: Op, arg=None, line=0, column=0):
        self.instructions.append(Instruction(op=op, arg=arg, line=line, column=column))

    def add_const(self, value) -> int:
        """Add constant and return its index."""
        # Deduplicate small ints
        if isinstance(value, int) and -5 <= value <= 255:
            for i, c in enumerate(self.constants):
                if c is value:
                    return i
        self.constants.append(value)
        return len(self.constants) - 1

    def add_name(self, name) -> int:
        """Add name and return its index."""
        if name in self.names:
            return self.names.index(name)
        self.names.append(name)
        return len(self.names) - 1

    def add_var_name(self, name) -> int:
        """Add local variable name."""
        if name in self.var_names:
            return self.var_names.index(name)
        self.var_names.append(name)
        return len(self.var_names) - 1

    def add_free_var(self, name) -> int:
        """Add free (closure) variable."""
        if name in self.free_vars:
            return self.free_vars.index(name)
        self.free_vars.append(name)
        return len(self.free_vars) - 1

    def finalize(self):
        """Pre-flatten instructions into parallel arrays for fast VM execution."""
        n = len(self.instructions)
        self.ops = [None] * n
        self.args_flat = [None] * n
        self.lines_flat = [0] * n
        self.cols_flat = [0] * n
        for i in range(n):
            ri = self.instructions[i]
            self.ops[i] = ri.op
            self.args_flat[i] = ri.arg
            self.lines_flat[i] = ri.line
            self.cols_flat[i] = ri.column

    def __len__(self):
        return len(self.instructions)
