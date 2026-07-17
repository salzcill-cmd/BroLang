"""
AST (Abstract Syntax Tree) untuk BroLang
=========================================

AST adalah representasi tree dari struktur kode sumber.
Setiap node dalam tree mewakili konstruksi bahasa.

Pipeline:
    Tokens → [Parser] → AST → Semantic Analyzer → Optimizer → Interpreter

Contoh:
    from brolang.ast.nodes import (
        ProgramNode, NumberNode, BinaryOpNode, AssignmentNode
    )

    ast = ProgramNode([
        AssignmentNode("nama", StringNode("Budi"))
    ])
"""

from brolang.ast.nodes import (
    # Base
    ASTNode,
    # Literals
    NumberNode,
    DecimalNode,
    StringNode,
    BooleanNode,
    KosongNode,
    # Variables
    IdentifierNode,
    AssignmentNode,
    VariableNode,
    # Operations
    BinaryOpNode,
    UnaryOpNode,
    # Control Flow
    IfNode,
    WhileNode,
    ForNode,
    BreakNode,
    ContinueNode,
    # Functions
    FunctionNode,
    ReturnNode,
    CallNode,
    # Classes
    ClassNode,
    AttributeNode,
    MethodNode,
    # Modules
    ImportNode,
    FromImportNode,
    # Error Handling
    TryNode,
    CatchNode,
    # Data Structures
    ListNode,
    IndexNode,
    ObjectNode,
    ObjectAccessNode,
    # I/O
    PrintNode,
    InputNode,
    # Program
    ProgramNode,
    # Visitor
    ASTVisitor,
    # V2
    LambdaNode,
    ComprehensionNode,
    FStringNode,
    EnumNode,
    StructNode,
    StructInstanceNode,
    MatchNode,
    WildcardNode,
    # V3
    AugmentedAssignmentNode,
    TernaryNode,
    RaiseNode,
    GlobalNode,
    NonlocalNode,
    # V3.1
    PassNode,
    DelNode,
    AssertNode,
    TupleNode,
    SetNode,
    DictComprehensionNode,
)
