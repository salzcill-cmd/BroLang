"""BroLang VM — bytecode virtual machine + transpiler for high performance."""

from brolang.vm.opcodes import Op, Instruction
from brolang.vm.compiler import Compiler
from brolang.vm.vm import VM
from brolang.vm.transpiler import Transpiler

__all__ = ['Op', 'Instruction', 'Compiler', 'VM', 'Transpiler']


def run_fast(code: str):
    """Run BroLang code using transpiler (97x faster than interpreter).
    
    Falls back to VM if transpilation fails.
    """
    from brolang.lexer import Lexer
    from brolang.parser import Parser
    
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    
    # Try transpiler first (fast path)
    try:
        transpiler = Transpiler()
        py_code = transpiler.transpile(ast)
        compiled = compile(py_code, '<brolang>', 'exec')
        exec(compiled, {'__builtins__': __builtins__})
        return
    except Exception:
        pass
    
    # Fallback to VM
    compiler = Compiler()
    bytecode = compiler.compile(ast)
    vm = VM()
    vm.run(bytecode)
    return vm.output
