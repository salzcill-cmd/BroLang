"""
Recursive Descent Parser BroLang
=================================

Parser ini mengubah token-token dari Lexer menjadi AST.
Menggunakan teknik Recursive Descent Parsing yang:
- Stabil dan mudah di-debug
- Mudah dikembangkan
- Menghasilkan AST yang bersih
- Setiap method mewakili satu aturan grammar

Grammar BroLang (BNF-like):
    program         → statement*
    statement       → assignment | if_stmt | while_stmt | for_stmt
                    | function_def | class_def | import_stmt
                    | try_stmt | print_stmt | return_stmt
                    | expression | break | continue
    assignment      → "buat" IDENTIFIER "=" expression
    if_stmt         → "jika" expression "maka" block ("lainnya" block)? "selesai"
    while_stmt      → "selama" expression "lakukan" block "selesai"
    for_stmt        → "untuk" IDENTIFIER "dalam" expression "lakukan" block "selesai"
    function_def    → "fungsi" IDENTIFIER "(" params? ")" block "selesai"
    class_def       → "kelas" IDENTIFIER block "selesai"
    import_stmt     → "impor" IDENTIFIER ("." IDENTIFIER)*
    try_stmt        → "coba" block "tangkap" IDENTIFIER block "selesai"
    print_stmt      → "tulis" expression ("," expression)*
    return_stmt     → "kembali" expression?
    block           → NEWLINE INDENT statement+ DEDENT
                    | statement
    expression      → or_expr
    or_expr         → and_expr ("atau" and_expr)*
    and_expr        → not_expr ("dan" not_expr)*
    not_expr        → "bukan" not_expr | comparison
    comparison      → addition (("==" | "!=" | ">" | "<" | ">=" | "<=") addition)*
    addition        → term (("+" | "-") term)*
    term            → unary (("*" | "/" | "%") unary)*
    unary           → ("-" | "+") unary | power
    power           → primary ("**" power)?
    primary         → NUMBER | DECIMAL | STRING | BOOLEAN | KOSONG
                    | IDENTIFIER | "(" expression ")"
                    | "[" elements? "]"
                    | "{" entries? "}"
                    | list_access | object_access
                    | function_call
"""

from typing import List, Optional
from brolang.token_types import Token, TokenType
from brolang.ast.nodes import (
    ASTNode, ProgramNode, NumberNode, DecimalNode, StringNode,
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
    AsyncFunctionDefNode, AwaitNode,
    YieldNode, YieldFromNode, GeneratorFunctionNode,
    DecoratorNode, DecoratedFunctionNode, DecoratedClassNode,
    WalrusNode, WithNode, TypedExceptNode, MultiExceptNode,
    StarImportNode, ChainedCallNode, SwitchNode,
    # V5.0 Nodes
    TypeAnnotationNode, TypeAliasNode, UnionTypeNode, GenericTypeNode, FunctionTypeNode,
    InterfaceNode, MethodSignatureNode, ImplementsNode, AbstractClassNode, AbstractMethodNode,
    DestructuringPatternNode, GuardPatternNode,
    MapNode, FilterNode, ReduceNode,
    ResultNode, OptionNode,
    MacroDefNode, MacroCallNode,
    NamespaceNode, UseNode, AccessModifierNode,
    NullCoalescingNode, OptionalChainingNode,
    ForEachNode, ChainedComparisonNode,
    # V5.2 Nodes
    PipelineNode, DestructuringAssignmentNode,
    # V6.0 Nodes
    ObjectPatternNode, BindingPatternNode,
    KelasErrorNode,
    # V6.5 Nodes
    DoUntilNode, RangeForNode,
)
from brolang.exceptions import ParserError
from brolang.suggestions import saran_keyword


class Parser:
    """Recursive Descent Parser untuk BroLang.

    Attributes:
        tokens: Daftar token dari lexer
        pos: Posisi token saat ini
        current_token: Token saat ini
    """

    def __init__(self, tokens: List[Token], file_path: str = ""):
        self.tokens: List[Token] = tokens
        self.file_path: str = file_path
        self.pos: int = 0
        self.current_token: Token = self.tokens[0] if tokens else Token(TokenType.TOKEN_EOF)

    def _error(self, message: str, solution: str = "", example: str = "") -> ParserError:
        """Membuat ParserError dengan informasi token saat ini.

        Ramah pemula: kalau token yang bermasalah mirip keyword bahasa
        Inggris (print, if, def, ...), pesan diberi saran padanan BroLang.
        """
        saran = saran_keyword(self.current_token.value)
        if saran:
            message += saran
        return ParserError(
            message=message,
            line=self.current_token.line,
            column=self.current_token.column,
            solution=solution,
            example=example,
            file_path=self.file_path,
        )

    def _advance(self) -> Token:
        """Maju ke token berikutnya dan mengembalikannya."""
        token = self.current_token
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = Token(TokenType.TOKEN_EOF)
        return token

    def _peek(self, offset: int = 0) -> TokenType:
        """Melihat tipe token ke depan tanpa maju."""
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx].type
        return TokenType.TOKEN_EOF

    def _check(self, *types: TokenType) -> bool:
        """Memeriksa apakah token saat ini termasuk dalam types."""
        return self.current_token.type in types

    def _match(self, *types: TokenType) -> bool:
        """Memeriksa dan maju jika token saat ini termasuk dalam types."""
        if self._check(*types):
            self._advance()
            return True
        return False

    def _expect(self, expected_type: TokenType, message: str = "", solution: str = "", example: str = "") -> Token:
        """Mengharapkan token dengan tipe tertentu. Error jika tidak cocok."""
        if self.current_token.type != expected_type:
            if not message:
                message = f"Diharapkan {expected_type.name}, tapi mendapatkan {self.current_token.type.name}."
            if not solution:
                solution = f"Periksa sintaks di sekitar token '{self.current_token.value}'."
            raise self._error(message=message, solution=solution, example=example)
        return self._advance()

    def _expect_value(self, *values: str) -> Token:
        """Mengharapkan token dengan nilai tertentu."""
        if self.current_token.value not in values:
            raise self._error(
                message=f"Diharapkan salah satu dari {values}, tapi mendapatkan '{self.current_token.value}'.",
                solution=f"Gunakan kata kunci yang benar: {', '.join(values)}.",
            )
        return self._advance()

    def parse(self) -> ProgramNode:
        """Method utama: mem-parse seluruh program.

        Returns:
            ProgramNode: Root AST node
        """
        statements = []
        while self.current_token.type != TokenType.TOKEN_EOF:
            stmt = self._parse_statement()
            if stmt is not None:
                statements.append(stmt)
            # Skip newlines between statements
            while self._match(TokenType.TOKEN_NEWLINE):
                pass

        return ProgramNode(statements=statements)

    def _parse_statement(self) -> Optional[ASTNode]:
        """Mem-parse satu statement.

        Mendeteksi jenis statement berdasarkan token pertama.
        """
        # Skip newlines
        while self._match(TokenType.TOKEN_NEWLINE):
            pass

        if self._check(TokenType.TOKEN_EOF):
            return None

        token_type = self.current_token.type

        # Check for decorators before function/class
        if token_type == TokenType.TOKEN_AT:
            return self._parse_decorated()

        if token_type == TokenType.TOKEN_BUAT:
            return self._parse_assignment()
        elif token_type == TokenType.TOKEN_KONSTANTA:
            return self._parse_assignment(is_const=True)
        elif token_type == TokenType.TOKEN_TULIS:
            return self._parse_print()
        elif token_type == TokenType.TOKEN_JIKA:
            return self._parse_if()
        elif token_type == TokenType.TOKEN_SELAMA:
            return self._parse_while()
        elif token_type == TokenType.TOKEN_ULANGI:
            return self._parse_do_until()
        elif token_type == TokenType.TOKEN_UNTUK:
            # Check for 'untuk setiap' (for-each with index)
            if self._peek(1) == TokenType.TOKEN_IDENTIFIER and self.tokens[self.pos + 1].value == "setiap":
                return self._parse_for_each()
            return self._parse_for()
        elif token_type == TokenType.TOKEN_FUNGSI:
            return self._parse_function()
        elif token_type == TokenType.TOKEN_KELAS:
            return self._parse_class()
        elif token_type == TokenType.TOKEN_KELAS_ERROR:
            return self._parse_kelas_error()
        elif token_type == TokenType.TOKEN_ASYNKRON:
            return self._parse_async_function()
        elif token_type == TokenType.TOKEN_IMPOR:
            return self._parse_import()
        elif token_type == TokenType.TOKEN_DARI:
            return self._parse_from_import()
        elif token_type == TokenType.TOKEN_COBA:
            return self._parse_try_v4()
        elif token_type == TokenType.TOKEN_DENGAN:
            return self._parse_with()
        elif token_type == TokenType.TOKEN_COCOKKAN:
            return self._parse_match()
        elif token_type == TokenType.TOKEN_ENUM:
            return self._parse_enum()
        elif token_type == TokenType.TOKEN_STRUKTUR:
            return self._parse_struct()
        elif token_type == TokenType.TOKEN_KEMBALI:
            return self._parse_return()
        elif token_type == TokenType.TOKEN_HASILKAN:
            return self._parse_yield()
        elif token_type == TokenType.TOKEN_HASILKANDARI:
            return self._parse_yield_from()
        elif token_type == TokenType.TOKEN_LEMPAR:
            return self._parse_raise()
        elif token_type == TokenType.TOKEN_GLOBAL:
            return self._parse_global()
        elif token_type == TokenType.TOKEN_NONLOKAL:
            return self._parse_nonlocal()
        elif token_type == TokenType.TOKEN_BREAK:
            self._advance()
            return BreakNode(line=self.current_token.line, column=self.current_token.column)
        elif token_type == TokenType.TOKEN_CONTINUE:
            self._advance()
            return ContinueNode(line=self.current_token.line, column=self.current_token.column)
        elif token_type == TokenType.TOKEN_PASS:
            self._advance()
            return PassNode(line=self.current_token.line, column=self.current_token.column)
        elif token_type == TokenType.TOKEN_HAPUS:
            return self._parse_del()
        elif token_type == TokenType.TOKEN_PASTIKAN:
            return self._parse_assert()
        # v5.0 Keywords
        elif token_type == TokenType.TOKEN_TIPE:
            return self._parse_type_alias()
        elif token_type == TokenType.TOKEN_ANTARMUKA:
            return self._parse_interface()
        elif token_type == TokenType.TOKEN_IMPLEMENTASI:
            return self._parse_implements()
        elif token_type == TokenType.TOKEN_ABSTRAK:
            return self._parse_abstract_class()
        elif token_type == TokenType.TOKEN_MAKRO:
            return self._parse_macro_def()
        elif token_type == TokenType.TOKEN_RUANG:
            return self._parse_namespace()
        elif token_type == TokenType.TOKEN_PAKAI:
            return self._parse_use_statement()
        elif token_type in (TokenType.TOKEN_PUBLIK, TokenType.TOKEN_PRIVAT, TokenType.TOKEN_TERLINDUNGI):
            return self._parse_access_modifier()
        elif token_type == TokenType.TOKEN_STATIS:
            return self._parse_static_modifier()
        elif token_type == TokenType.TOKEN_PETA:
            return self._parse_map_call()
        elif token_type == TokenType.TOKEN_SARING:
            return self._parse_filter_call()
        elif token_type == TokenType.TOKEN_KURANGI:
            return self._parse_reduce_call()
        elif token_type == TokenType.TOKEN_BENAR_VAL or token_type == TokenType.TOKEN_SALAH_VAL:
            return self._parse_result()
        elif token_type == TokenType.TOKEN_SOME:
            return self._parse_option()
        elif token_type == TokenType.TOKEN_IDENTIFIER:
            # Could be reassignment, augmented assignment, method call, or expression
            # Peek ahead to see if it's assignment
            if self._peek(1) == TokenType.TOKEN_ASSIGN:
                return self._parse_reassignment()
            elif self._peek(1) in (
                TokenType.TOKEN_PLUS_ASSIGN, TokenType.TOKEN_MINUS_ASSIGN,
                TokenType.TOKEN_MULTIPLY_ASSIGN, TokenType.TOKEN_DIVIDE_ASSIGN,
                TokenType.TOKEN_MODULO_ASSIGN, TokenType.TOKEN_POWER_ASSIGN,
            ):
                return self._parse_augmented_assignment()
            elif self._peek(1) == TokenType.TOKEN_DOT:
                # Could be self.attr = value
                # Parse the full expression first
                saved_pos = self.pos
                expr = self._parse_expression()
                if self._check(TokenType.TOKEN_ASSIGN):
                    # It's an assignment to a dotted target
                    self._advance()  # =
                    value = self._parse_expression()
                    return AssignmentNode(target=expr, value=value, is_declaration=False,
                                          line=expr.line, column=expr.column)
                return expr
            else:
                expr = self._parse_expression()
                if self._check(TokenType.TOKEN_ASSIGN):
                    # Assignment ke index/ekspresi: d[1] = 99 (target IndexNode)
                    self._advance()  # =
                    value = self._parse_expression()
                    return AssignmentNode(target=expr, value=value, is_declaration=False,
                                          line=expr.line, column=expr.column)
                return expr
        else:
            return self._parse_expression()

    # ============= Assignment =============

    def _parse_assignment(self, is_const: bool = False) -> AssignmentNode:
        """buat identifier (. identifier)? = expression | konstanta identifier = expression (v6.5)"""
        token = self._advance()  # buat / konstanta

        # Destructuring assignment: buat [a, b] = list atau buat {x, y} = objek
        if self._check(TokenType.TOKEN_LBRACKET) or self._check(TokenType.TOKEN_LBRACE):
            if is_const:
                raise self._error(
                    message="'konstanta' tidak mendukung destructuring.",
                    solution="Deklarasikan satu konstanta per baris, mis. konstanta A = 1.",
                    example="konstanta A = 1\nkonstanta B = 2",
                )
            return self._parse_destructuring_assignment(
                token, is_array=self._check(TokenType.TOKEN_LBRACKET)
            )

        id_token = self._expect(
            TokenType.TOKEN_IDENTIFIER,
            message="Setelah 'buat', harus diikuti nama variabel.",
            solution="Tulis nama variabel setelah 'buat'.",
            example="buat nama = \"Budi\"",
        )
        target: ASTNode = IdentifierNode(name=id_token.value, line=id_token.line, column=id_token.column)

        # Handle dotted assignment: self.attr = value
        while self._match(TokenType.TOKEN_DOT):
            attr_token = self._expect(
                TokenType.TOKEN_IDENTIFIER,
                message="Setelah '.', harus ada nama atribut.",
            )
            target = ObjectAccessNode(
                object=target,
                property=attr_token.value,
                line=id_token.line,
                column=id_token.column,
            )

        # Type annotation v6.0: buat x: Angka = 5
        type_annotation = None
        if self._match(TokenType.TOKEN_COLON):
            type_annotation = self._parse_type_name()

        value = None
        if self._match(TokenType.TOKEN_ASSIGN):
            value = self._parse_expression()
        else:
            value = KosongNode(line=self.current_token.line, column=self.current_token.column)

        return AssignmentNode(
            target=target,
            value=value,
            is_declaration=True,
            type_annotation=type_annotation,
            is_const=is_const,
            line=token.line,
            column=token.column,
        )

    def _parse_destructuring_assignment(self, token: Token, is_array: bool) -> DestructuringAssignmentNode:
        """Destructuring assignment: buat [a, b] = list atau buat {x, y} = objek"""
        open_tok = self._advance()  # [ atau {
        targets = []

        if not self._check(TokenType.TOKEN_RBRACKET if is_array else TokenType.TOKEN_RBRACE):
            id_token = self._expect(
                TokenType.TOKEN_IDENTIFIER,
                message=f"Setelah '{'[' if is_array else '{'}', harus ada nama variabel.",
            )
            targets.append(id_token.value)
            while self._match(TokenType.TOKEN_COMMA):
                if self._check(TokenType.TOKEN_RBRACKET if is_array else TokenType.TOKEN_RBRACE):
                    break
                id_token = self._expect(TokenType.TOKEN_IDENTIFIER)
                targets.append(id_token.value)

        if is_array:
            self._expect(TokenType.TOKEN_RBRACKET, message="Destructuring list harus ditutup dengan ']'.")
        else:
            self._expect(TokenType.TOKEN_RBRACE, message="Destructuring objek harus ditutup dengan '}'.")

        self._expect(
            TokenType.TOKEN_ASSIGN,
            message="Destructuring harus diikuti '=' dan nilai.",
            solution="Gunakan: buat [a, b] = [1, 2]",
            example="buat [x, y] = [10, 20]",
        )
        value = self._parse_expression()

        return DestructuringAssignmentNode(
            targets=targets,
            is_array=is_array,
            value=value,
            line=token.line,
            column=token.column,
        )

    def _parse_reassignment(self) -> AssignmentNode:
        """Reassignment: identifier = expression"""
        id_token = self._advance()  # identifier
        target = IdentifierNode(name=id_token.value, line=id_token.line, column=id_token.column)
        self._expect(TokenType.TOKEN_ASSIGN,
                     message=f"Setelah variabel, harus ada '='.")
        value = self._parse_expression()
        return AssignmentNode(
            target=target,
            value=value,
            is_declaration=False,
            line=id_token.line,
            column=id_token.column,
        )

    def _parse_augmented_assignment(self) -> AugmentedAssignmentNode:
        """Augmented assignment: x += 1, x -= 2, x *= 3, dll."""
        id_token = self._advance()  # identifier
        target = IdentifierNode(name=id_token.value, line=id_token.line, column=id_token.column)

        op_token = self._advance()  # +=, -=, *=, /=, %=, **=
        op_map = {
            TokenType.TOKEN_PLUS_ASSIGN: "+=",
            TokenType.TOKEN_MINUS_ASSIGN: "-=",
            TokenType.TOKEN_MULTIPLY_ASSIGN: "*=",
            TokenType.TOKEN_DIVIDE_ASSIGN: "/=",
            TokenType.TOKEN_MODULO_ASSIGN: "%=",
            TokenType.TOKEN_POWER_ASSIGN: "**=",
        }
        operator = op_map[op_token.type]

        value = self._parse_expression()
        return AugmentedAssignmentNode(
            target=target,
            operator=operator,
            value=value,
            line=id_token.line,
            column=id_token.column,
        )

    def _parse_raise(self) -> RaiseNode:
        """lempar expression"""
        token = self._advance()  # lempar
        value = self._parse_expression()
        return RaiseNode(value=value, line=token.line, column=token.column)

    def _parse_global(self) -> GlobalNode:
        """global name (, name)*"""
        token = self._advance()  # global
        names = []
        name_token = self._expect(TokenType.TOKEN_IDENTIFIER,
                                  message="Setelah 'global', harus ada nama variabel.")
        names.append(name_token.value)
        while self._match(TokenType.TOKEN_COMMA):
            name_token = self._expect(TokenType.TOKEN_IDENTIFIER)
            names.append(name_token.value)
        return GlobalNode(names=names, line=token.line, column=token.column)

    def _parse_nonlocal(self) -> NonlocalNode:
        """nonlokal name (, name)*"""
        token = self._advance()  # nonlokal
        names = []
        name_token = self._expect(TokenType.TOKEN_IDENTIFIER,
                                  message="Setelah 'nonlokal', harus ada nama variabel.")
        names.append(name_token.value)
        while self._match(TokenType.TOKEN_COMMA):
            name_token = self._expect(TokenType.TOKEN_IDENTIFIER)
            names.append(name_token.value)
        return NonlocalNode(names=names, line=token.line, column=token.column)

    def _parse_del(self) -> DelNode:
        """hapus target"""
        token = self._advance()  # hapus
        target = self._parse_expression()
        return DelNode(target=target, line=token.line, column=token.column)

    def _parse_assert(self) -> AssertNode:
        """pastikan kondisi (, pesan)?"""
        token = self._advance()  # pastikan
        condition = self._parse_expression()
        message = None
        # If expression parser created a tuple from the comma, extract condition + message
        if isinstance(condition, TupleNode) and len(condition.elements) >= 2:
            message = condition.elements[-1]
            if len(condition.elements) == 2:
                condition = condition.elements[0]
            else:
                condition = TupleNode(
                    elements=condition.elements[:-1],
                    line=condition.line, column=condition.column,
                )
        elif self._match(TokenType.TOKEN_COMMA):
            message = self._parse_expression()
        return AssertNode(condition=condition, message=message, line=token.line, column=token.column)

    # ============= Print =============

    def _parse_print(self) -> PrintNode:
        """tulis expression ("," expression)*"""
        token = self._advance()  # tulis
        expr = self._parse_expression()
        args = [expr]

        while self._match(TokenType.TOKEN_COMMA):
            args.append(self._parse_expression())

        return PrintNode(
            expression=args[0],
            args=args[1:],
            line=token.line,
            column=token.column,
        )

    # ============= If Statement =============

    def _parse_if(self) -> IfNode:
        """jika expression maka block (lainnya block)? selesai"""
        token = self._advance()  # jika
        condition = self._parse_expression()

        # Pemula sering menulis `jika x = 5 maka` (satu '=') untuk membandingkan
        if self._check(TokenType.TOKEN_ASSIGN):
            raise self._error(
                message="Kelihatannya kamu memakai '=' untuk membandingkan di dalam kondisi.",
                solution="Untuk membandingkan gunakan '==' (dua tanda sama), bukan '='.",
                example="jika x == 5 maka\n    tulis \"lima\"\nselesai",
            )

        self._expect(
            TokenType.TOKEN_MAKA,
            message="Setelah kondisi 'jika', harus ada 'maka'.",
            solution="Tambahkan 'maka' setelah kondisi.",
            example="jika x > 0 maka\n    tulis \"positif\"\nselesai",
        )

        body = self._parse_block()

        elif_conditions = []
        elif_bodies = []
        else_body = []

        while self._check(TokenType.TOKEN_LAINNYA):
            self._advance()  # lainnya
            if self._check(TokenType.TOKEN_JIKA):
                # elif: lainnya jika
                self._advance()  # jika
                elif_condition = self._parse_expression()
                self._expect(
                    TokenType.TOKEN_MAKA,
                    message="Setelah 'lainnya jika', harus ada 'maka'.",
                )
                elif_body = self._parse_block()
                elif_conditions.append(elif_condition)
                elif_bodies.append(elif_body)
            else:
                else_body = self._parse_block()

        self._expect(
            TokenType.TOKEN_SELESAI,
            message="Blok 'jika' harus ditutup dengan 'selesai'.",
            solution="Tambahkan 'selesai' di akhir blok jika.",
            example="jika x > 0 maka\n    tulis \"positif\"\nselesai",
        )

        return IfNode(
            condition=condition,
            body=body,
            else_body=else_body,
            elif_conditions=elif_conditions,
            elif_bodies=elif_bodies,
            line=token.line,
            column=token.column,
        )

    # ============= While Loop =============

    def _parse_while(self) -> WhileNode:
        """selama expression lakukan block (lainnya block)? selesai"""
        token = self._advance()  # selama
        condition = self._parse_expression()

        # Pemula sering menulis `selama x = 5 lakukan` (satu '=') untuk membandingkan
        if self._check(TokenType.TOKEN_ASSIGN):
            raise self._error(
                message="Kelihatannya kamu memakai '=' untuk membandingkan di dalam kondisi.",
                solution="Untuk membandingkan gunakan '==' (dua tanda sama), bukan '='.",
                example="selama x == 5 lakukan\n    tulis x\nselesai",
            )

        self._expect(
            TokenType.TOKEN_LAKUKAN,
            message="Setelah kondisi 'selama', harus ada 'lakukan'.",
            solution="Tambahkan 'lakukan' setelah kondisi.",
            example="selama x < 10 lakukan\n    tulis x\n    x = x + 1\nselesai",
        )

        body = self._parse_block()

        # Check for else clause (lainnya) BEFORE selesai
        else_body = None
        if self._check(TokenType.TOKEN_LAINNYA):
            self._advance()  # consume 'lainnya'
            else_body = self._parse_block()

        self._expect(
            TokenType.TOKEN_SELESAI,
            message="Blok 'selama' harus ditutup dengan 'selesai'.",
            solution="Tambahkan 'selesai' di akhir blok selama.",
            example="selama x < 10 lakukan\n    tulis x\nselesai",
        )

        return WhileNode(condition=condition, body=body, else_body=else_body, line=token.line, column=token.column)

    # ============= V6.5: Do-Until Loop =============

    def _parse_do_until(self) -> DoUntilNode:
        """ulangi block sampai expression (v6.5)

        Body dijalankan minimal sekali, lalu kondisi dicek setelah body:
            ulangi
                tulis x
                x = x + 1
            sampai x >= 10
        """
        token = self._advance()  # ulangi

        body = self._parse_block()

        self._expect(
            TokenType.TOKEN_SAMPAI,
            message="Setelah blok 'ulangi', harus ada 'sampai' + kondisi.",
            solution="Tambahkan 'sampai' + kondisi untuk mengakhiri loop.",
            example="ulangi\n    tulis x\n    x = x + 1\nsampai x >= 10",
        )

        condition = self._parse_expression()

        return DoUntilNode(
            body=body,
            condition=condition,
            line=token.line,
            column=token.column,
        )

    # ============= For Loop =============

    def _parse_for(self) -> ForNode:
        """untuk identifier dalam expression lakukan block (lainnya block)? selesai

        v6.5: bentuk range numerik:
            untuk i dari 1 sampai 10 lakukan ... selesai
            untuk i dari 1 sampai 10 langkah 2 lakukan ... selesai
            untuk i dari 10 sampai 1 langkah -1 lakukan ... selesai
        """
        token = self._advance()  # untuk
        id_token = self._expect(
            TokenType.TOKEN_IDENTIFIER,
            message="Setelah 'untuk', harus ada nama variabel.",
            solution="Tulis nama variabel setelah 'untuk'.",
            example="untuk item dalam list lakukan\n    tulis item\nselesai",
        )
        variable = id_token.value

        # v6.5: 'untuk i dari A sampai B (langkah S)?' — range numerik
        if self._check(TokenType.TOKEN_DARI):
            return self._parse_range_for(token, variable)

        self._expect(
            TokenType.TOKEN_DALAM,
            message="Setelah variabel, harus ada 'dalam'.",
            solution="Tambahkan 'dalam' setelah nama variabel.",
            example="untuk item dalam list lakukan\n    tulis item\nselesai",
        )

        iterable = self._parse_expression()

        self._expect(
            TokenType.TOKEN_LAKUKAN,
            message="Setelah 'dalam', harus ada 'lakukan'.",
            solution="Tambahkan 'lakukan' setelah iterable.",
            example="untuk item dalam list lakukan\n    tulis item\nselesai",
        )

        body = self._parse_block()

        # Check for else clause (lainnya) BEFORE selesai
        else_body = None
        if self._check(TokenType.TOKEN_LAINNYA):
            self._advance()  # consume 'lainnya'
            else_body = self._parse_block()

        self._expect(
            TokenType.TOKEN_SELESAI,
            message="Blok 'untuk' harus ditutup dengan 'selesai'.",
            solution="Tambahkan 'selesai' di akhir blok untuk.",
        )

        return ForNode(
            variable=variable,
            iterable=iterable,
            body=body,
            else_body=else_body,
            line=token.line,
            column=token.column,
        )

    def _parse_range_for(self, token: Token, variable: str) -> RangeForNode:
        """untuk i dari start sampai end (langkah step)? lakukan block (lainnya block)? selesai (v6.5)"""
        self._advance()  # dari
        start = self._parse_expression()

        self._expect(
            TokenType.TOKEN_SAMPAI,
            message="Setelah 'dari', harus ada 'sampai'.",
            solution="Gunakan: untuk i dari 1 sampai 10 lakukan ... selesai",
            example="untuk i dari 1 sampai 10 lakukan\n    tulis i\nselesai",
        )

        end = self._parse_expression()

        # 'langkah' adalah soft keyword — hanya dikenali di sini supaya nama
        # variabel/kelas 'langkah' di program lama tetap valid.
        step = None
        if self._check(TokenType.TOKEN_IDENTIFIER) and self.current_token.value == "langkah":
            self._advance()
            step = self._parse_expression()

        self._expect(
            TokenType.TOKEN_LAKUKAN,
            message="Setelah batas range, harus ada 'lakukan'.",
            solution="Tambahkan 'lakukan' setelah batas range.",
            example="untuk i dari 1 sampai 10 lakukan\n    tulis i\nselesai",
        )

        body = self._parse_block()

        else_body = None
        if self._check(TokenType.TOKEN_LAINNYA):
            self._advance()  # consume 'lainnya'
            else_body = self._parse_block()

        self._expect(
            TokenType.TOKEN_SELESAI,
            message="Blok 'untuk' harus ditutup dengan 'selesai'.",
            solution="Tambahkan 'selesai' di akhir blok untuk.",
        )

        return RangeForNode(
            variable=variable,
            start=start,
            end=end,
            step=step,
            body=body,
            else_body=else_body,
            line=token.line,
            column=token.column,
        )

    # ============= Function =============

    def _parse_function(self) -> FunctionNode:
        """fungsi identifier(params) block selesai"""
        token = self._advance()  # fungsi
        # Nama fungsi bisa berupa keyword bahasa (mis. `fungsi cetak`, `fungsi tulis`)
        # Pengecualian: token yang jelas bukan nama (string, angka, kurung, dst.)
        _kata = (
            TokenType.TOKEN_IDENTIFIER, TokenType.TOKEN_CETAK,
            TokenType.TOKEN_TULIS, TokenType.TOKEN_INPUT,
            TokenType.TOKEN_BUAT, TokenType.TOKEN_TIPE,
            TokenType.TOKEN_KELAS, TokenType.TOKEN_FUNGSI,
        )
        if not self._check(*_kata):
            raise self._error(
                message="Setelah 'fungsi', harus ada nama fungsi.",
                solution="Tulis nama fungsi setelah 'fungsi'.",
                example='fungsi sapa(nama)\n    kembali "Halo " + nama\nselesai',
            )
        id_token = self._advance()
        name = id_token.value

        self._expect(
            TokenType.TOKEN_LPAREN,
            message="Setelah nama fungsi, harus ada '('.",
        )

        params, defaults, param_types = self._parse_parameter_list()

        self._expect(
            TokenType.TOKEN_RPAREN,
            message="Setelah parameter, harus ada ')'.",
        )

        # Return type v6.0: fungsi f() -> Angka
        return_type = None
        if self._check(TokenType.TOKEN_ARROW):
            self._advance()  # ->
            return_type = self._parse_type_name()

        body = self._parse_block()

        self._expect(
            TokenType.TOKEN_SELESAI,
            message="Fungsi harus ditutup dengan 'selesai'.",
            solution="Tambahkan 'selesai' di akhir fungsi.",
        )

        return FunctionNode(
            name=name,
            params=params,
            defaults=defaults,
            param_types=param_types,
            return_type=return_type,
            body=body,
            line=token.line,
            column=token.column,
        )

    def _parse_parameter_list(self) -> tuple:
        """Mem-parse daftar parameter dengan default values & tipe (v6.0).

        Returns:
            Tuple of (params, defaults, param_types)
        """
        params = []
        defaults = []
        param_types = []
        if self._check(TokenType.TOKEN_IDENTIFIER):
            token = self._advance()
            params.append(token.value)
            param_type = None
            if self._check(TokenType.TOKEN_COLON):
                self._advance()
                param_type = self._parse_type_name()
            param_types.append(param_type)
            default_val = None
            if self._match(TokenType.TOKEN_ASSIGN):
                default_val = self._parse_expression()
            defaults.append(default_val)

            while self._match(TokenType.TOKEN_COMMA):
                token = self._expect(
                    TokenType.TOKEN_IDENTIFIER,
                    message="Setelah koma, harus ada nama parameter.",
                )
                params.append(token.value)
                param_type = None
                if self._check(TokenType.TOKEN_COLON):
                    self._advance()
                    param_type = self._parse_type_name()
                param_types.append(param_type)
                default_val = None
                if self._match(TokenType.TOKEN_ASSIGN):
                    default_val = self._parse_expression()
                defaults.append(default_val)
        return params, defaults, param_types

    def _parse_type_name(self) -> str:
        """Parse nama tipe v6.0: Angka | Daftar<Angka> | Angka | Teks | alias.

        Mengembalikan string representasi tipe, mis. 'Daftar<Angka>' atau
        'Angka | Teks' (union).
        """
        parts = []
        tok = self._expect(
            TokenType.TOKEN_IDENTIFIER,
            message="Setelah ':' harus ada nama tipe.",
            solution="Gunakan tipe bawaan: Angka, Desimal, Teks, Boolean, Daftar, Objek",
            example="buat umur: Angka = 25",
        )
        parts.append(tok.value)

        # Generics: Daftar<Angka>
        if self._match(TokenType.TOKEN_LT):
            inner = self._parse_type_name()
            while self._match(TokenType.TOKEN_COMMA):
                inner += ", " + self._parse_type_name()
            self._expect(TokenType.TOKEN_GT,
                         message="Generik harus ditutup dengan '>'.",
                         example="Daftar<Angka>")
            parts.append(f"<{inner}>")

        # Union: Angka | Teks
        while self._match(TokenType.TOKEN_PIPE):
            parts.append("|")
            parts.append(self._parse_type_name())

        return "".join(parts)

    # ============= Class =============

    def _parse_class(self) -> ClassNode:
        """kelas identifier (: identifier)? block selesai"""
        token = self._advance()  # kelas
        id_token = self._expect(
            TokenType.TOKEN_IDENTIFIER,
            message="Setelah 'kelas', harus ada nama kelas.",
            solution="Tulis nama kelas setelah 'kelas'.",
            example="kelas Mobil\n    fungsi __init__(merk)\n        ...\n    selesai\nselesai",
        )
        name = id_token.value

        parent = None
        if self._match(TokenType.TOKEN_COLON):
            parent_token = self._expect(
                TokenType.TOKEN_IDENTIFIER,
                message="Setelah ':', harus ada nama kelas parent.",
            )
            parent = parent_token.value
        elif self._match(TokenType.TOKEN_LPAREN):
            parent_token = self._expect(
                TokenType.TOKEN_IDENTIFIER,
                message="Setelah '(', harus ada nama kelas parent.",
            )
            parent = parent_token.value
            self._expect(TokenType.TOKEN_RPAREN)

        body = self._parse_block()

        # Parse methods from body, handling statis modifier
        methods = []
        for stmt in body:
            if isinstance(stmt, FunctionNode):
                methods.append(
                    MethodNode(
                        name=stmt.name,
                        params=stmt.params,
                        body=stmt.body,
                        is_static=stmt.is_static,
                        line=stmt.line,
                        column=stmt.column,
                    )
                )

        self._expect(
            TokenType.TOKEN_SELESAI,
            message="Kelas harus ditutup dengan 'selesai'.",
            solution="Tambahkan 'selesai' di akhir kelas.",
        )

        return ClassNode(
            name=name,
            parent=parent,
            methods=methods,
            body=body,
            line=token.line,
            column=token.column,
        )

    def _parse_kelas_error(self) -> KelasErrorNode:
        """kelas_error Nama (extends Induk)? block selesai"""
        token = self._advance()  # kelas_error
        id_token = self._expect(
            TokenType.TOKEN_IDENTIFIER,
            message="Setelah 'kelas_error', harus ada nama kelas error.",
            solution="Tulis nama kelas error setelah 'kelas_error'.",
            example='kelas_error SaldoTidakCukup\n    ...\nselesai',
        )
        name = id_token.value

        parent = None
        # extends Induk (opsional; default Kesalahan)
        if self._check(TokenType.TOKEN_IDENTIFIER) and self.current_token.value in ("extends", "warisan"):
            self._advance()
            parent_token = self._expect(
                TokenType.TOKEN_IDENTIFIER,
                message="Setelah 'extends', harus ada nama kelas induk.",
            )
            parent = parent_token.value
        elif self._match(TokenType.TOKEN_COLON):
            parent_token = self._expect(
                TokenType.TOKEN_IDENTIFIER,
                message="Setelah ':', harus ada nama kelas induk.",
            )
            parent = parent_token.value

        body = self._parse_block()

        methods = []
        for stmt in body:
            if isinstance(stmt, FunctionNode):
                methods.append(
                    MethodNode(
                        name=stmt.name,
                        params=stmt.params,
                        body=stmt.body,
                        is_static=stmt.is_static,
                        line=stmt.line,
                        column=stmt.column,
                    )
                )

        self._expect(
            TokenType.TOKEN_SELESAI,
            message="Kelas error harus ditutup dengan 'selesai'.",
            solution="Tambahkan 'selesai' di akhir kelas error.",
        )

        return KelasErrorNode(
            name=name,
            parent=parent,
            methods=methods,
            body=body,
            line=token.line,
            column=token.column,
        )

    # ============= Import =============

    def _parse_import(self) -> ImportNode:
        """impor identifier (. identifier)*"""
        token = self._advance()  # impor
        parts = []
        # Accept identifier or keyword tokens as module names (e.g. 'impor input')
        if self.current_token and self.current_token.type in (
            TokenType.TOKEN_IDENTIFIER, TokenType.TOKEN_INPUT, TokenType.TOKEN_CETAK,
        ):
            id_token = self._advance()
            parts.append(id_token.value)
        else:
            raise self._error(
                message="Setelah 'impor', harus ada nama modul.",
                solution="Tulis nama modul setelah 'impor'.",
                example="impor matematika",
            )

        while self._match(TokenType.TOKEN_DOT):
            if self.current_token and self.current_token.type in (
                TokenType.TOKEN_IDENTIFIER, TokenType.TOKEN_INPUT, TokenType.TOKEN_CETAK,
            ):
                id_token = self._advance()
                parts.append(id_token.value)
            else:
                raise self._error(
                    message="Setelah '.', harus ada nama submodul.",
                )

        module = ".".join(parts)

        alias = None
        # 'sebagai' adalah keyword (TOKEN_SEBAGAI), bukan identifier
        if self._match(TokenType.TOKEN_SEBAGAI):
            alias_token = self._expect(
                TokenType.TOKEN_IDENTIFIER,
                message="Setelah 'sebagai', harus ada alias.",
            )
            alias = alias_token.value

        return ImportNode(module=module, alias=alias, line=token.line, column=token.column)

    def _parse_from_import(self) -> ASTNode:
        """dari module impor identifier (, identifier)* atau dari module impor *"""
        token = self._advance()  # dari
        module_parts = []
        id_token = self._expect(
            TokenType.TOKEN_IDENTIFIER,
            message="Setelah 'dari', harus ada nama modul.",
        )
        module_parts.append(id_token.value)

        while self._match(TokenType.TOKEN_DOT):
            id_token = self._expect(TokenType.TOKEN_IDENTIFIER)
            module_parts.append(id_token.value)

        module = ".".join(module_parts)

        self._expect(
            TokenType.TOKEN_IMPOR,
            message="Setelah 'dari module', harus ada 'impor'.",
            solution="Gunakan: dari module impor nama",
            example="dari matematika impor akar",
        )

        # Check for star import
        if self._check(TokenType.TOKEN_MULTIPLY):
            self._advance()  # *
            return StarImportNode(module=module, line=token.line, column=token.column)

        names = []
        id_token = self._expect(
            TokenType.TOKEN_IDENTIFIER,
            message="Setelah 'impor', harus ada nama yang diimpor.",
        )
        names.append(id_token.value)

        while self._match(TokenType.TOKEN_COMMA):
            id_token = self._expect(TokenType.TOKEN_IDENTIFIER)
            names.append(id_token.value)

        return FromImportNode(module=module, names=names, line=token.line, column=token.column)

    # ============= Try-Catch =============

    def _parse_try(self) -> TryNode:
        """coba block tangkap identifier block (akhirnya block)? selesai"""
        token = self._advance()  # coba
        body = self._parse_block()

        var_name = "error"
        self._expect(
            TokenType.TOKEN_TANGKAP,
            message="Setelah blok 'coba', harus ada 'tangkap'.",
            solution="Tambahkan 'tangkap error' untuk menangkap error.",
            example="coba\n    ...\ntangkap error\n    ...\nselesai",
        )

        if self._check(TokenType.TOKEN_IDENTIFIER):
            id_token = self._advance()
            var_name = id_token.value

        catch_body = self._parse_block()

        finally_body = None
        if self._check(TokenType.TOKEN_AKHIRNYA):
            self._advance()  # akhirnya
            finally_body = self._parse_block()

        self._expect(
            TokenType.TOKEN_SELESAI,
            message="Blok 'coba' harus ditutup dengan 'selesai'.",
        )

        return TryNode(body=body, catch_var=var_name, catch_body=catch_body,
                       finally_body=finally_body, line=token.line, column=token.column)

    # ============= V2: Match/Case =============

    def _parse_match(self) -> MatchNode:
        """cocokkan expression { pattern: body, ... }"""
        token = self._advance()  # cocokkan
        value = self._parse_expression()

        self._expect(
            TokenType.TOKEN_LBRACE,
            message="Setelah 'cocokkan', harus ada '{'.",
            solution="Tambahkan '{' setelah ekspresi.",
        )

        # Consume NEWLINE + INDENT if present
        self._match(TokenType.TOKEN_NEWLINE)
        self._match(TokenType.TOKEN_INDENT)

        cases = []
        guards = []
        default_case = None

        while not self._check(TokenType.TOKEN_RBRACE, TokenType.TOKEN_DEDENT, TokenType.TOKEN_EOF):
            # Skip commas and newlines between cases
            while self._match(TokenType.TOKEN_COMMA) or self._match(TokenType.TOKEN_NEWLINE):
                pass
            if self._check(TokenType.TOKEN_RBRACE, TokenType.TOKEN_DEDENT, TokenType.TOKEN_EOF):
                break

            # Parse pattern (v6.0: list/objek/binding/literal + guard)
            if self._check(TokenType.TOKEN_IDENTIFIER) and self.current_token.value == "_":
                self._advance()  # consume _
                pattern = WildcardNode(line=self.current_token.line, column=self.current_token.column)
                self._expect(TokenType.TOKEN_COLON, message="Setelah '_', harus ada ':'.")
                body = self._parse_match_case_body()
                default_case = body
            else:
                pattern = self._parse_pattern()
                guard = None
                if self._match(TokenType.TOKEN_JIKA):
                    guard = self._parse_expression()
                self._expect(TokenType.TOKEN_COLON, message="Setelah pattern, harus ada ':'.")
                body = self._parse_match_case_body()
                cases.append((pattern, body))
                guards.append(guard)

        # Consume DEDENT if present
        self._match(TokenType.TOKEN_DEDENT)
        self._expect(TokenType.TOKEN_RBRACE, message="Match harus ditutup dengan '}'.")

        return MatchNode(value=value, cases=cases, guards=guards,
                         default_case=default_case,
                         line=token.line, column=token.column)

    def _parse_pattern(self) -> ASTNode:
        """Parse pola match v6.0.

        - `[a, b, c]`        : pola list (destructure elemen)
        - `{nama, umur}`     : pola objek (destructure nilai)
        - `{"x": a, "y": b}` : pola objek dengan rename kunci
        - `nama` (identifier): binding — tangkap seluruh nilai
        - literal/ekspresi   : cocokkan nilai (perilaku lama)
        """
        if self._check(TokenType.TOKEN_LBRACKET):
            return self._parse_destructuring_pattern()
        if self._check(TokenType.TOKEN_LBRACE):
            return self._parse_object_pattern()
        if self._check(TokenType.TOKEN_IDENTIFIER):
            tok = self._advance()
            return BindingPatternNode(name=tok.value,
                                      line=tok.line, column=tok.column)
        return self._parse_expression()

    def _parse_object_pattern(self) -> ASTNode:
        """Parse pola objek: {nama, umur} atau {"x": a, "y": b}."""
        token = self._advance()  # {

        # Rename: {"kunci": variabel} atau literal: {"kunci": "nilai"}
        if self._check(TokenType.TOKEN_STRING) and self._peek(1) == TokenType.TOKEN_COLON:
            entries = {}
            key_token = self._advance()
            self._expect(TokenType.TOKEN_COLON)
            if self._check(TokenType.TOKEN_STRING):
                val_token = self._advance()
                entries[key_token.value] = ("lit", val_token.value)
            else:
                var_token = self._expect(TokenType.TOKEN_IDENTIFIER)
                entries[key_token.value] = ("var", var_token.value)
            while self._match(TokenType.TOKEN_COMMA):
                key_token = self._expect(TokenType.TOKEN_STRING)
                self._expect(TokenType.TOKEN_COLON)
                if self._check(TokenType.TOKEN_STRING):
                    val_token = self._advance()
                    entries[key_token.value] = ("lit", val_token.value)
                else:
                    var_token = self._expect(TokenType.TOKEN_IDENTIFIER)
                    entries[key_token.value] = ("var", var_token.value)
            self._expect(TokenType.TOKEN_RBRACE,
                         message="Pola objek harus ditutup dengan '}'.")
            return ObjectPatternNode(entries=entries,
                                     line=token.line, column=token.column)

        # Destructure: {nama, umur} — kunci = nama variabel
        variables = []
        var_token = self._expect(TokenType.TOKEN_IDENTIFIER,
                                 message="Setelah '{' pola objek, harus ada nama variabel.")
        variables.append(var_token.value)
        while self._match(TokenType.TOKEN_COMMA):
            if self._check(TokenType.TOKEN_RBRACE):
                break
            var_token = self._expect(TokenType.TOKEN_IDENTIFIER)
            variables.append(var_token.value)
        self._expect(TokenType.TOKEN_RBRACE,
                     message="Pola objek harus ditutup dengan '}'.")
        return DestructuringPatternNode(variables=variables, is_array=False,
                                        line=token.line, column=token.column)

    def _parse_match_case_body(self) -> List[ASTNode]:
        """Parse body of a match case (single statement or block)."""
        body = []
        # Skip newlines
        while self._match(TokenType.TOKEN_NEWLINE):
            pass

        # Single statement on same line or next
        if not self._check(TokenType.TOKEN_RBRACE, TokenType.TOKEN_DEDENT,
                          TokenType.TOKEN_COMMA, TokenType.TOKEN_NEWLINE, TokenType.TOKEN_EOF):
            stmt = self._parse_statement()
            if stmt:
                body.append(stmt)
        return body

    # ============= V2: Enum =============

    def _parse_enum(self) -> EnumNode:
        """enum Name { MEMBER1, MEMBER2, ... }"""
        token = self._advance()  # enum
        name_token = self._expect(
            TokenType.TOKEN_IDENTIFIER,
            message="Setelah 'enum', harus ada nama enum.",
        )
        self._expect(TokenType.TOKEN_LBRACE, message="Setelah nama enum, harus ada '{'.")

        self._match(TokenType.TOKEN_NEWLINE)
        self._match(TokenType.TOKEN_INDENT)

        members = []
        if not self._check(TokenType.TOKEN_RBRACE, TokenType.TOKEN_DEDENT):
            member_token = self._expect(
                TokenType.TOKEN_IDENTIFIER,
                message="Setelah '{', harus ada nama member enum.",
            )
            members.append(member_token.value)
            while self._match(TokenType.TOKEN_COMMA):
                member_token = self._expect(TokenType.TOKEN_IDENTIFIER)
                members.append(member_token.value)

        while self._match(TokenType.TOKEN_NEWLINE):
            pass
        self._match(TokenType.TOKEN_DEDENT)
        self._expect(TokenType.TOKEN_RBRACE, message="Enum harus ditutup dengan '}'.")

        return EnumNode(name=name_token.value, members=members,
                        line=token.line, column=token.column)

    # ============= V2: Struct =============

    def _parse_struct(self) -> StructNode:
        """struktur Name { field1, field2, ... }"""
        token = self._advance()  # struktur
        name_token = self._expect(
            TokenType.TOKEN_IDENTIFIER,
            message="Setelah 'struktur', harus ada nama struktur.",
        )
        self._expect(TokenType.TOKEN_LBRACE, message="Setelah nama struktur, harus ada '{'.")

        self._match(TokenType.TOKEN_NEWLINE)
        self._match(TokenType.TOKEN_INDENT)

        fields = []
        if not self._check(TokenType.TOKEN_RBRACE, TokenType.TOKEN_DEDENT):
            field_token = self._expect(
                TokenType.TOKEN_IDENTIFIER,
                message="Setelah '{', harus ada nama field.",
            )
            fields.append(field_token.value)
            while self._match(TokenType.TOKEN_COMMA):
                field_token = self._expect(TokenType.TOKEN_IDENTIFIER)
                fields.append(field_token.value)

        while self._match(TokenType.TOKEN_NEWLINE):
            pass
        self._match(TokenType.TOKEN_DEDENT)
        self._expect(TokenType.TOKEN_RBRACE, message="Struktur harus ditutup with '}'.")

        return StructNode(name=name_token.value, fields=fields,
                          line=token.line, column=token.column)

    # ============= V2: Lambda =============

    def _parse_lambda(self) -> LambdaNode:
        """lalu(params) expr"""
        token = self._advance()  # lalu
        self._expect(TokenType.TOKEN_LPAREN, message="Setelah 'lalu', harus ada '('.")
        params, _, _ = self._parse_parameter_list()
        self._expect(TokenType.TOKEN_RPAREN, message="Parameter lambda tidak ditutup.")

        # Single expression body (no block)
        body = self._parse_expression()

        return LambdaNode(params=params, body=body,
                          line=token.line, column=token.column)

    # ============= Return =============

    def _parse_return(self) -> ReturnNode:
        """kembali expression?"""
        token = self._advance()  # kembali

        value = KosongNode(line=token.line, column=token.column)
        if not self._check(TokenType.TOKEN_NEWLINE, TokenType.TOKEN_DEDENT, TokenType.TOKEN_EOF, TokenType.TOKEN_SELESAI):
            value = self._parse_expression()

        return ReturnNode(value=value, line=token.line, column=token.column)

    # ============= Block Parsing =============

    def _parse_block(self) -> List[ASTNode]:
        """Mem-parse blok statement.

        Blok bisa:
        - Single-line: setelah keyword di baris yang sama
        - Multi-line: NEWLINE INDENT ... DEDENT
        """
        statements = []

        # Single-line block
        if not self._check(TokenType.TOKEN_NEWLINE):
            stmt = self._parse_statement()
            if stmt is not None:
                statements.append(stmt)
            return statements

        # Multi-line block
        self._advance()  # newline
        self._expect(
            TokenType.TOKEN_INDENT,
            message="Blok harus memiliki indentasi.",
            solution="Tambahkan indentasi (spasi) setelah baris ini.",
        )

        while (not self._check(TokenType.TOKEN_DEDENT) and
               not self._check(TokenType.TOKEN_EOF)):
            while self._match(TokenType.TOKEN_NEWLINE):
                pass
            if self._check(TokenType.TOKEN_DEDENT, TokenType.TOKEN_EOF):
                break
            stmt = self._parse_statement()
            if stmt is not None:
                statements.append(stmt)

        if self._check(TokenType.TOKEN_DEDENT):
            self._advance()

        return statements

    # ============= Expression Parsing (Precedence Climbing) =============

    def _parse_expression(self) -> ASTNode:
        """Expression dengan precedence climbing."""
        return self._parse_pipeline_expr()

    def _parse_pipeline_expr(self) -> ASTNode:
        """Pipeline operator: nilai |> fungsi atau nilai |> lalu(x) x * 2"""
        left = self._parse_null_coalescing_expr()
        while self._check(TokenType.TOKEN_PIPE_GREATER):
            self._advance()  # |>
            right = self._parse_null_coalescing_expr()
            left = PipelineNode(left=left, right=right,
                                line=left.line, column=left.column)
        return left

    def _parse_null_coalescing_expr(self) -> ASTNode:
        """Null coalescing: expr ?? default"""
        left = self._parse_ternary()
        while self._check(TokenType.TOKEN_QUESTION):
            self._advance()  # ?? token (already a single token from lexer)
            right = self._parse_ternary()
            left = NullCoalescingNode(left=left, right=right,
                                      line=left.line, column=left.column)
        return left

    def _parse_ternary(self) -> ASTNode:
        """Ternary: expr jika kondisi lainnya expr"""
        left = self._parse_or()
        if self._check(TokenType.TOKEN_JIKA):
            if_token = self._advance()
            condition = self._parse_expression()
            self._expect(TokenType.TOKEN_LAINNYA,
                         message="Ternary membutuhkan 'lainnya'.",
                         solution="Gunakan: nilai_a jika kondisi lainnya nilai_b")
            false_val = self._parse_ternary()
            return TernaryNode(true_value=left, condition=condition, false_value=false_val,
                               line=if_token.line, column=if_token.column)
        return left

    def _parse_or(self) -> ASTNode:
        left = self._parse_and()
        while self._check(TokenType.TOKEN_ATAU):
            op_token = self._advance()
            right = self._parse_and()
            left = BinaryOpNode(left=left, operator="atau", right=right,
                                line=op_token.line, column=op_token.column)
        return left

    def _parse_and(self) -> ASTNode:
        left = self._parse_not()
        while self._check(TokenType.TOKEN_DAN):
            op_token = self._advance()
            right = self._parse_not()
            left = BinaryOpNode(left=left, operator="dan", right=right,
                                line=op_token.line, column=op_token.column)
        return left

    def _parse_not(self) -> ASTNode:
        if self._check(TokenType.TOKEN_BUKAN):
            op_token = self._advance()
            operand = self._parse_not()
            return UnaryOpNode(operator="bukan", operand=operand,
                               line=op_token.line, column=op_token.column)
        return self._parse_bitwise()

    def _parse_bitwise(self) -> ASTNode:
        """Bitwise operators: & | ^ << >>"""
        left = self._parse_comparison()
        while self._check(TokenType.TOKEN_AMPERSAND, TokenType.TOKEN_PIPE,
                         TokenType.TOKEN_CARET, TokenType.TOKEN_LSHIFT, TokenType.TOKEN_RSHIFT):
            op_token = self._advance()
            op_map = {
                TokenType.TOKEN_AMPERSAND: "&",
                TokenType.TOKEN_PIPE: "|",
                TokenType.TOKEN_CARET: "^",
                TokenType.TOKEN_LSHIFT: "<<",
                TokenType.TOKEN_RSHIFT: ">>",
            }
            right = self._parse_comparison()
            left = BinaryOpNode(left=left, operator=op_map[op_token.type], right=right,
                                line=op_token.line, column=op_token.column)
        return left

    def _parse_comparison(self) -> ASTNode:
        left = self._parse_addition()
        while self._check(
            TokenType.TOKEN_EQ, TokenType.TOKEN_NEQ,
            TokenType.TOKEN_GT, TokenType.TOKEN_LT,
            TokenType.TOKEN_GTE, TokenType.TOKEN_LTE,
            TokenType.TOKEN_IS, TokenType.TOKEN_DALAM,
        ):
            op_token = self._advance()
            # Handle "is bukan" (is not)
            if op_token.type == TokenType.TOKEN_IS and self._check(TokenType.TOKEN_BUKAN):
                self._advance()  # consume "bukan"
                right = self._parse_addition()
                left = BinaryOpNode(left=left, operator="is not", right=right,
                                    line=op_token.line, column=op_token.column)
            elif op_token.type == TokenType.TOKEN_IS:
                right = self._parse_addition()
                left = BinaryOpNode(left=left, operator="is", right=right,
                                    line=op_token.line, column=op_token.column)
            elif op_token.type == TokenType.TOKEN_DALAM:
                right = self._parse_addition()
                left = BinaryOpNode(left=left, operator="dalam", right=right,
                                    line=op_token.line, column=op_token.column)
            else:
                op_map = {
                    TokenType.TOKEN_EQ: "==",
                    TokenType.TOKEN_NEQ: "!=",
                    TokenType.TOKEN_GT: ">",
                    TokenType.TOKEN_LT: "<",
                    TokenType.TOKEN_GTE: ">=",
                    TokenType.TOKEN_LTE: "<=",
                }
                right = self._parse_addition()
                left = BinaryOpNode(left=left, operator=op_map[op_token.type], right=right,
                                    line=op_token.line, column=op_token.column)
        return left

    def _parse_addition(self) -> ASTNode:
        left = self._parse_term()
        while self._check(TokenType.TOKEN_PLUS, TokenType.TOKEN_MINUS):
            op_token = self._advance()
            op = "+" if op_token.type == TokenType.TOKEN_PLUS else "-"
            right = self._parse_term()
            left = BinaryOpNode(left=left, operator=op, right=right,
                                line=op_token.line, column=op_token.column)
        return left

    def _parse_term(self) -> ASTNode:
        left = self._parse_unary()
        while self._check(TokenType.TOKEN_MULTIPLY, TokenType.TOKEN_DIVIDE, TokenType.TOKEN_MODULO):
            op_token = self._advance()
            op_map = {
                TokenType.TOKEN_MULTIPLY: "*",
                TokenType.TOKEN_DIVIDE: "/",
                TokenType.TOKEN_MODULO: "%",
            }
            op = op_map[op_token.type]
            right = self._parse_unary()
            left = BinaryOpNode(left=left, operator=op, right=right,
                                line=op_token.line, column=op_token.column)
        return left

    def _parse_unary(self) -> ASTNode:
        if self._check(TokenType.TOKEN_MINUS):
            op_token = self._advance()
            operand = self._parse_unary()
            return UnaryOpNode(operator="-", operand=operand,
                               line=op_token.line, column=op_token.column)
        if self._check(TokenType.TOKEN_PLUS):
            op_token = self._advance()
            operand = self._parse_unary()
            return UnaryOpNode(operator="+", operand=operand,
                               line=op_token.line, column=op_token.column)
        if self._check(TokenType.TOKEN_TILDE):
            op_token = self._advance()
            operand = self._parse_unary()
            return UnaryOpNode(operator="~", operand=operand,
                               line=op_token.line, column=op_token.column)
        return self._parse_power()

    def _parse_power(self) -> ASTNode:
        left = self._parse_primary()
        if self._check(TokenType.TOKEN_POW):
            op_token = self._advance()
            right = self._parse_power()  # right-associative
            left = BinaryOpNode(left=left, operator="**", right=right,
                                line=op_token.line, column=op_token.column)
        return left

    def _parse_primary(self) -> ASTNode:
        """Mem-parse primary expression: literal, identifier, call, group, etc."""
        token = self.current_token

        # Literals
        if self._check(TokenType.TOKEN_NUMBER):
            token = self._advance()
            node = NumberNode(value=token.value, line=token.line, column=token.column)
        elif self._check(TokenType.TOKEN_DECIMAL):
            token = self._advance()
            node = DecimalNode(value=token.value, line=token.line, column=token.column)
        elif self._check(TokenType.TOKEN_STRING):
            token = self._advance()
            node = StringNode(value=token.value, line=token.line, column=token.column)
        elif self._check(TokenType.TOKEN_FSTRING):
            node = self._parse_fstring()
        elif self._check(TokenType.TOKEN_BOOLEAN):
            token = self._advance()
            node = BooleanNode(value=token.value, line=token.line, column=token.column)
        elif self._check(TokenType.TOKEN_KOSONG):
            token = self._advance()
            node = KosongNode(line=token.line, column=token.column)
        elif self._check(TokenType.TOKEN_LPAREN):
            self._advance()  # (
            # Check for empty tuple
            if self._check(TokenType.TOKEN_RPAREN):
                self._advance()
                node = TupleNode(elements=[], line=self.current_token.line, column=self.current_token.column)
            else:
                first_expr = self._parse_expression()
                # Check if it's a tuple (has comma)
                if self._check(TokenType.TOKEN_COMMA):
                    elements = [first_expr]
                    while self._match(TokenType.TOKEN_COMMA):
                        if self._check(TokenType.TOKEN_RPAREN):
                            break  # trailing comma
                        elements.append(self._parse_expression())
                    self._expect(TokenType.TOKEN_RPAREN)
                    node = TupleNode(elements=elements, line=self.current_token.line, column=self.current_token.column)
                else:
                    # Just a grouped expression
                    self._expect(TokenType.TOKEN_RPAREN,
                                 message="Tanda kurung tidak ditutup.",
                                 solution="Tambahkan ')' setelah ekspresi.",
                                 example="(1 + 2)")
                    node = first_expr
        elif self._check(TokenType.TOKEN_LBRACKET):
            node = self._parse_list_literal()
        elif self._check(TokenType.TOKEN_LBRACE):
            node = self._parse_object_literal()
        elif self._check(TokenType.TOKEN_LALU):
            node = self._parse_lambda()
        elif self._check(TokenType.TOKEN_IDENTIFIER):
            token = self._advance()
            node = self._parse_identifier_continuation(token)
        elif self._check(TokenType.TOKEN_BUAT):
            # Anonymous function call from assignment target
            raise self._error(
                message="Ekspresi tidak valid di sini.",
                solution="Periksa sintaks di sekitar sini.",
            )
        elif self._check(TokenType.TOKEN_INPUT):
            if self._peek(1) == TokenType.TOKEN_DOT:
                # 'input' dipakai sebagai nama modul (mis. 'impor input'),
                # bukan builtin input(). Akses atribut ditangani _parse_postfix.
                token = self._advance()
                node = IdentifierNode(name="input", line=token.line, column=token.column)
            else:
                node = self._parse_input()
        elif self._check(TokenType.TOKEN_CETAK):
            # 'cetak' adalah keyword reserved, tapi tetap bisa dipakai sebagai
            # nama fungsi/variabel (mis. `fungsi cetak(...)` lalu `cetak(...)`).
            token = self._advance()
            node = IdentifierNode(name=token.value, line=token.line, column=token.column)
        elif self._check(TokenType.TOKEN_TIPE):
            # 'tipe' sebagai fungsi: tipe(nilai). (Sebagai statement,
            # 'tipe Nama = ...' tetap jadi type alias di _parse_statement.)
            token = self._advance()
            node = IdentifierNode(name="tipe", line=token.line, column=token.column)
        # v5.0: HOF and Result/Option in expression context
        elif self._check(TokenType.TOKEN_PETA):
            node = self._parse_map_call()
        elif self._check(TokenType.TOKEN_SARING):
            node = self._parse_filter_call()
        elif self._check(TokenType.TOKEN_KURANGI):
            node = self._parse_reduce_call()
        elif self._check(TokenType.TOKEN_BENAR_VAL):
            node = self._parse_result()
        elif self._check(TokenType.TOKEN_SALAH_VAL):
            node = self._parse_result()
        elif self._check(TokenType.TOKEN_SOME):
            node = self._parse_option()
        else:
            raise self._error(
                message=f"Token tidak terduga: '{token.value}' ({token.type.name}).",
                solution="Periksa sintaks di sekitar token ini.",
            )

        # Handle chained calls and accesses
        node = self._parse_postfix(node)
        return node

    def _parse_identifier_continuation(self, token: Token) -> ASTNode:
        """Mem-parse identifier dan kelanjutannya (call, access, walrus)."""
        node = IdentifierNode(name=token.value, line=token.line, column=token.column)

        # Walrus operator: x := expr
        if self._check(TokenType.TOKEN_WALRUS):
            return self._parse_walrus(token.value)

        # Function call
        if self._check(TokenType.TOKEN_LPAREN):
            self._advance()  # (
            args, kwargs = self._parse_argument_list()
            self._expect(TokenType.TOKEN_RPAREN,
                         message="Argumen fungsi tidak ditutup.",
                         solution="Tambahkan ')' setelah argumen.")
            node = CallNode(function=node, args=args, kwargs=kwargs, line=token.line, column=token.column)

        return node

    def _parse_postfix(self, node: ASTNode) -> ASTNode:
        """Mem-parse postfix operations: calls, indexing, attribute access."""
        while True:
            if self._check(TokenType.TOKEN_LPAREN):
                # Function call on expression
                if isinstance(node, CallNode):
                    break
                self._advance()  # (
                args, kwargs = self._parse_argument_list()
                self._expect(TokenType.TOKEN_RPAREN)
                node = CallNode(function=node, args=args, kwargs=kwargs, line=node.line, column=node.column)
            elif self._check(TokenType.TOKEN_LBRACKET):
                # Indexing or slicing
                self._advance()  # [
                # Check for slice syntax
                if self._check(TokenType.TOKEN_COLON):
                    # [:stop] or [::step]
                    self._advance()  # :
                    slice_stop = None
                    slice_step = None
                    if not self._check(TokenType.TOKEN_COLON, TokenType.TOKEN_RBRACKET):
                        slice_stop = self._parse_expression()
                    if self._check(TokenType.TOKEN_COLON):
                        self._advance()  # :
                        if not self._check(TokenType.TOKEN_RBRACKET):
                            slice_step = self._parse_expression()
                    self._expect(TokenType.TOKEN_RBRACKET)
                    node = IndexNode(target=node, index=NumberNode(0),
                                     slice_start=None, slice_stop=slice_stop, slice_step=slice_step,
                                     is_slice=True, line=node.line, column=node.column)
                else:
                    first_expr = self._parse_expression()
                    if self._check(TokenType.TOKEN_COLON):
                        # [start:stop] or [start:stop:step]
                        self._advance()  # :
                        slice_stop = None
                        slice_step = None
                        if not self._check(TokenType.TOKEN_COLON, TokenType.TOKEN_RBRACKET):
                            slice_stop = self._parse_expression()
                        if self._check(TokenType.TOKEN_COLON):
                            self._advance()  # :
                            if not self._check(TokenType.TOKEN_RBRACKET):
                                slice_step = self._parse_expression()
                        self._expect(TokenType.TOKEN_RBRACKET)
                        node = IndexNode(target=node, index=NumberNode(0),
                                         slice_start=first_expr, slice_stop=slice_stop, slice_step=slice_step,
                                         is_slice=True, line=node.line, column=node.column)
                    else:
                        # Regular indexing
                        self._expect(TokenType.TOKEN_RBRACKET,
                                     message="Indexing tidak ditutup.",
                                     solution="Tambahkan ']' setelah indeks.",
                                     example="list[0]")
                        node = IndexNode(target=node, index=first_expr, line=node.line, column=node.column)
            elif self._check(TokenType.TOKEN_DOT):
                # Attribute/method access
                self._advance()  # .
                # Nama method bisa berupa keyword bahasa (mis. `csv.tulis`, `file.baca`)
                _method_tokens = (
                    TokenType.TOKEN_IDENTIFIER, TokenType.TOKEN_TULIS,
                    TokenType.TOKEN_BUAT, TokenType.TOKEN_MAKA,
                    TokenType.TOKEN_SELESAI, TokenType.TOKEN_DALAM,
                    TokenType.TOKEN_JIKA, TokenType.TOKEN_LAINNYA,
                    TokenType.TOKEN_FUNGSI, TokenType.TOKEN_KEMBALI,
                    TokenType.TOKEN_KELAS, TokenType.TOKEN_IMPOR,
                    TokenType.TOKEN_TIPE, TokenType.TOKEN_COBA,
                    TokenType.TOKEN_TANGKAP, TokenType.TOKEN_KECUALI,
                )
                if not self._check(*_method_tokens):
                    raise self._error(
                        message="Setelah '.', harus ada nama atribut atau method.",
                        solution="Periksa nama method setelah titik.",
                    )
                id_token = self._advance()
                attr_name = id_token.value

                if self._check(TokenType.TOKEN_LPAREN):
                    # Method call: obj.method()
                    self._advance()  # (
                    args, kwargs = self._parse_argument_list()
                    self._expect(TokenType.TOKEN_RPAREN)
                    # Build: ObjectAccessNode(obj, method) as the call target
                    access_node = ObjectAccessNode(
                        object=node,
                        property=attr_name,
                        line=id_token.line,
                        column=id_token.column,
                    )
                    node = CallNode(
                        function=access_node,
                        args=args,
                        kwargs=kwargs,
                        is_method=True,
                        object_name=attr_name,
                        line=id_token.line,
                        column=id_token.column,
                    )
                else:
                    # Attribute access: obj.attr
                    node = ObjectAccessNode(
                        object=node,
                        property=attr_name,
                        line=id_token.line,
                        column=id_token.column,
                    )
            else:
                break

        return node

    def _extract_obj_from_call(self, node: ASTNode) -> ASTNode:
        """Helper to extract object reference from chain."""
        if isinstance(node, CallNode):
            return node.function
        return node

    def _parse_argument_list(self) -> List[ASTNode]:
        """Mem-parse daftar argumen fungsi (termasuk keyword arguments)."""
        args = []
        kwargs = []
        if not self._check(TokenType.TOKEN_RPAREN):
            first = self._parse_expression()
            # Keyword argument: nama = nilai
            if self._check(TokenType.TOKEN_ASSIGN) and isinstance(first, IdentifierNode):
                self._advance()  # =
                value = self._parse_expression()
                kwargs.append((first.name, value))
            else:
                args.append(first)
            while self._match(TokenType.TOKEN_COMMA):
                expr = self._parse_expression()
                if self._check(TokenType.TOKEN_ASSIGN) and isinstance(expr, IdentifierNode):
                    self._advance()  # =
                    value = self._parse_expression()
                    kwargs.append((expr.name, value))
                else:
                    args.append(expr)
        return args, kwargs

    def _parse_list_literal(self) -> ASTNode:
        """[expression (, expression)*] atau [expr lalu var dalam iterable]"""
        token = self._advance()  # [
        elements = []
        if not self._check(TokenType.TOKEN_RBRACKET):
            first_expr = self._parse_expression()

            # Check if this is a comprehension: [expr lalu var dalam iterable]
            if self._check(TokenType.TOKEN_LALU):
                self._advance()  # lalu
                var_token = self._expect(
                    TokenType.TOKEN_IDENTIFIER,
                    message="Setelah 'lalu', harus ada nama variabel.",
                )
                self._expect(
                    TokenType.TOKEN_DALAM,
                    message="Setelah variabel, harus ada 'dalam'.",
                )
                # Iterable di-parse tanpa ternary di top-level, agar 'jika'
                # berikutnya = filter, bukan ternary (bug: "Ternary membutuhkan
                # 'lainnya'"). Ternary tetap bisa dipakai dalam kurung:
                # [x lalu x dalam (a jika b lainnya c)]
                iterable = self._parse_comprehension_iterable()

                # Optional filter: [expr lalu var dalam iterable jika kondisi]
                condition = None
                if self._check(TokenType.TOKEN_JIKA):
                    self._advance()  # jika
                    condition = self._parse_expression()

                self._expect(TokenType.TOKEN_RBRACKET,
                             message="List comprehension tidak ditutup.",
                             solution="Tambahkan ']' setelah iterable.")
                return ComprehensionNode(
                    expr=first_expr, variable=var_token.value,
                    iterable=iterable, condition=condition,
                    line=token.line, column=token.column,
                )

            elements.append(first_expr)
            while self._match(TokenType.TOKEN_COMMA):
                elements.append(self._parse_expression())
        self._expect(TokenType.TOKEN_RBRACKET,
                     message="List literal tidak ditutup.",
                     solution="Tambahkan ']' setelah elemen list.",
                     example="[1, 2, 3]")
        return ListNode(elements=elements, line=token.line, column=token.column)

    def _parse_comprehension_iterable(self) -> ASTNode:
        """Parse iterable list comprehension tanpa ternary di level teratas.

        Sama seperti _parse_expression tapi melewatkan level _parse_ternary,
        sehingga 'jika' setelah iterable jadi filter comprehension. Ternary di
        dalam kurung/argumen tetap didukung.
        """
        left = self._parse_or()
        while self._check(TokenType.TOKEN_QUESTION):
            self._advance()  # ??
            right = self._parse_or()
            left = NullCoalescingNode(left=left, right=right,
                                      line=left.line, column=left.column)
        while self._check(TokenType.TOKEN_PIPE_GREATER):
            self._advance()  # |>
            right = self._parse_comprehension_iterable()
            left = PipelineNode(left=left, right=right,
                                line=left.line, column=left.column)
        return left

    def _parse_object_literal(self):
        """{string: expression} for dict, or {expr, expr} for set"""
        token = self._advance()  # {
        
        # Check for empty dict/set
        if self._check(TokenType.TOKEN_RBRACE):
            self._advance()
            return ObjectNode(entries={}, line=token.line, column=token.column)
        
        # Peek at first element to determine if it's a dict or set
        # Dict: {"key": value} - string followed by colon
        # Set: {value, value} - any expression followed by comma or }
        if self._check(TokenType.TOKEN_STRING) and self._peek(1) == TokenType.TOKEN_COLON:
            # It's a dict
            entries = {}
            key_token = self._advance()  # string key
            self._expect(TokenType.TOKEN_COLON)
            value = self._parse_expression()
            entries[key_token.value] = value

            while self._match(TokenType.TOKEN_COMMA):
                if self._check(TokenType.TOKEN_RBRACE):
                    break  # trailing comma
                key_token = self._expect(TokenType.TOKEN_STRING)
                self._expect(TokenType.TOKEN_COLON)
                value = self._parse_expression()
                entries[key_token.value] = value

            self._expect(TokenType.TOKEN_RBRACE)
            return ObjectNode(entries=entries, line=token.line, column=token.column)
        else:
            # It's a set
            elements = []
            elements.append(self._parse_expression())
            while self._match(TokenType.TOKEN_COMMA):
                if self._check(TokenType.TOKEN_RBRACE):
                    break  # trailing comma
                elements.append(self._parse_expression())
            self._expect(TokenType.TOKEN_RBRACE)
            return SetNode(elements=elements, line=token.line, column=token.column)

    def _parse_fstring(self) -> FStringNode:
        """Parse f-string: f"...{expr}..." """
        token = self._advance()  # TOKEN_FSTRING
        parts = []
        for ptype, pval in token.value:
            if ptype == "literal":
                parts.append(("literal", pval))
            elif ptype == "expr":
                # Parse the expression string
                from brolang.lexer import Lexer
                inner_lexer = Lexer(pval, file_path=self.file_path)
                inner_tokens = inner_lexer.tokenize()
                inner_parser = Parser(inner_tokens, file_path=self.file_path)
                expr = inner_parser._parse_expression()
                parts.append(("expr", expr))
        return FStringNode(parts=parts, line=token.line, column=token.column)

    def _parse_input(self) -> InputNode:
        """input(prompt?)"""
        token = self._advance()  # input
        self._expect(TokenType.TOKEN_LPAREN,
                     message="Setelah 'input', harus ada '('.")
        prompt = None
        if not self._check(TokenType.TOKEN_RPAREN):
            prompt = self._parse_expression()
        self._expect(TokenType.TOKEN_RPAREN,
                     message="Input tidak ditutup.")
        return InputNode(prompt=prompt, line=token.line, column=token.column)

    # ============= V4: Decorator =============

    def _parse_decorated(self) -> ASTNode:
        """Parse decorated function or class: @decorator fungsi/kelas ..."""
        decorators = []
        while self._check(TokenType.TOKEN_AT):
            self._advance()  # @
            decorator_expr = self._parse_expression()
            decorators.append(decorator_expr)
            while self._match(TokenType.TOKEN_NEWLINE):
                pass

        # Now parse the function or class
        if self._check(TokenType.TOKEN_FUNGSI):
            func = self._parse_function()
            return DecoratedFunctionNode(
                name=func.name,
                params=func.params,
                defaults=func.defaults,
                body=func.body,
                decorators=decorators,
                line=func.line,
                column=func.column,
            )
        elif self._check(TokenType.TOKEN_KELAS):
            cls = self._parse_class()
            return DecoratedClassNode(
                name=cls.name,
                parent=cls.parent,
                methods=cls.methods,
                body=cls.body,
                decorators=decorators,
                line=cls.line,
                column=cls.column,
            )
        elif self._check(TokenType.TOKEN_ASYNKRON):
            func = self._parse_async_function()
            return DecoratedFunctionNode(
                name=func.name,
                params=func.params,
                defaults=func.defaults,
                body=func.body,
                decorators=decorators,
                line=func.line,
                column=func.column,
            )
        else:
            raise self._error(
                message="Setelah '@', harus ada 'fungsi' atau 'kelas'.",
                solution="Gunakan @sebelum fungsi atau kelas.",
                example="@dekorator\nfungsi nama() ... selesai",
            )

    # ============= V4: Async Function =============

    def _parse_async_function(self) -> AsyncFunctionDefNode:
        """asinkron fungsi identifier(params) block selesai"""
        token = self._advance()  # asinkron
        self._expect(TokenType.TOKEN_FUNGSI,
                     message="Setelah 'asinkron', harus ada 'fungsi'.")
        id_token = self._expect(
            TokenType.TOKEN_IDENTIFIER,
            message="Setelah 'fungsi', harus ada nama fungsi.",
        )
        name = id_token.value

        self._expect(TokenType.TOKEN_LPAREN)
        params, defaults, _ = self._parse_parameter_list()
        self._expect(TokenType.TOKEN_RPAREN)

        body = self._parse_block()
        self._expect(TokenType.TOKEN_SELESAI,
                     message="Fungsi asinkron harus ditutup dengan 'selesai'.")

        return AsyncFunctionDefNode(
            name=name, params=params, defaults=defaults, body=body,
            line=token.line, column=token.column,
        )

    # ============= V4: Yield =============

    def _parse_yield(self) -> YieldNode:
        """hasilkan expression?"""
        token = self._advance()  # hasilkan
        value = None
        if not self._check(TokenType.TOKEN_NEWLINE, TokenType.TOKEN_DEDENT,
                           TokenType.TOKEN_EOF, TokenType.TOKEN_SELESAI):
            value = self._parse_expression()
        return YieldNode(value=value, line=token.line, column=token.column)

    def _parse_yield_from(self) -> YieldFromNode:
        """hasilkandari expression"""
        token = self._advance()  # hasilkandari
        value = self._parse_expression()
        return YieldFromNode(value=value, line=token.line, column=token.column)

    # ============= V4: Walrus Operator =============

    def _parse_walrus(self, name: str) -> WalrusNode:
        """name := expression"""
        self._advance()  # :=
        value = self._parse_expression()
        return WalrusNode(name=name, value=value, line=self.current_token.line, column=self.current_token.column)

    # ============= V4: With Statement =============

    def _parse_with(self) -> WithNode:
        """dengan ekspresi sebagai nama ... selesai"""
        token = self._advance()  # dengan
        context_expr = self._parse_expression()

        as_name = None
        if self._check(TokenType.TOKEN_SEBAGAI):
            self._advance()  # sebagai
            id_token = self._expect(TokenType.TOKEN_IDENTIFIER,
                                    message="Setelah 'sebagai', harus ada nama variabel.")
            as_name = id_token.value

        body = self._parse_block()
        self._expect(TokenType.TOKEN_SELESAI,
                     message="Blok 'dengan' harus ditutup dengan 'selesai'.")

        return WithNode(context_expr=context_expr, as_name=as_name, body=body,
                        line=token.line, column=token.column)

    # ============= V4: Enhanced Try/Except =============

    def _parse_try_v4(self) -> MultiExceptNode:
        """coba block (kecuali type as var block)* (lainnya block)? (akhirnya block)? selesai"""
        token = self._advance()  # coba
        body = self._parse_block()

        except_clauses = []
        else_body = None
        finally_body = None

        # Parse multiple except clauses
        while self._check(TokenType.TOKEN_KECUALI, TokenType.TOKEN_TANGKAP):
            if self._check(TokenType.TOKEN_KECUALI):
                self._advance()  # kecuali
                exc_type = None
                var_name = "error"

                if self._check(TokenType.TOKEN_IDENTIFIER):
                    if self._peek(1) == TokenType.TOKEN_SEBAGAI:
                        # kecuali ExceptionType sebagai var_name
                        id_token = self._advance()
                        exc_type = id_token.value
                        self._advance()  # sebagai
                        var_token = self._expect(TokenType.TOKEN_IDENTIFIER)
                        var_name = var_token.value
                    elif self._peek(1) == TokenType.TOKEN_NEWLINE:
                        # kecuali var_name (bare except)
                        id_token = self._advance()
                        var_name = id_token.value
                    else:
                        # kecuali ExceptionType (no variable binding)
                        id_token = self._advance()
                        exc_type = id_token.value
                elif self._check(TokenType.TOKEN_LAINNYA):
                    # kecuali lainnya (catch-all bare except)
                    self._advance()
                    exc_type = "semua"
                    if self._match(TokenType.TOKEN_SEBAGAI):
                        var_token = self._expect(TokenType.TOKEN_IDENTIFIER,
                                                 message="Setelah 'sebagai', harus ada nama variabel error.")
                        var_name = var_token.value

                clause_body = self._parse_block()
                except_clauses.append(TypedExceptNode(
                    exception_type=exc_type, variable=var_name, body=clause_body,
                    line=token.line, column=token.column,
                ))
            elif self._check(TokenType.TOKEN_TANGKAP):
                # Legacy tangkap syntax
                self._advance()  # tangkap
                var_name = "error"
                if self._check(TokenType.TOKEN_IDENTIFIER):
                    id_token = self._advance()
                    var_name = id_token.value
                clause_body = self._parse_block()
                except_clauses.append(TypedExceptNode(
                    exception_type=None, variable=var_name, body=clause_body,
                    line=token.line, column=token.column,
                ))

        # Parse else clause
        if self._check(TokenType.TOKEN_LAINNYA):
            self._advance()  # lainnya
            else_body = self._parse_block()

        # Parse finally clause
        if self._check(TokenType.TOKEN_AKHIRNYA):
            self._advance()  # akhirnya
            finally_body = self._parse_block()

        self._expect(TokenType.TOKEN_SELESAI,
                     message="Blok 'coba' harus ditutup dengan 'selesai'.")

        return MultiExceptNode(
            body=body, except_clauses=except_clauses,
            else_body=else_body, finally_body=finally_body,
            line=token.line, column=token.column,
        )

    # ============= V4: Star Import =============

    def _parse_star_import(self) -> StarImportNode:
        """dari module impor *"""
        token = self._advance()  # dari
        module_parts = []
        id_token = self._expect(TokenType.TOKEN_IDENTIFIER,
                                message="Setelah 'dari', harus ada nama modul.")
        module_parts.append(id_token.value)

        while self._match(TokenType.TOKEN_DOT):
            id_token = self._expect(TokenType.TOKEN_IDENTIFIER)
            module_parts.append(id_token.value)

        module = ".".join(module_parts)

        self._expect(TokenType.TOKEN_IMPOR)
        self._expect(TokenType.TOKEN_MULTIPLY,
                     message="Setelah 'impor', gunakan '*' untuk star import.")

        return StarImportNode(module=module, line=token.line, column=token.column)

    # ============= V4: Generator Function =============

    def _parse_generator_function(self) -> GeneratorFunctionNode:
        """fungsi nama() ... hasilkan ... selesai"""
        token = self._advance()  # fungsi
        id_token = self._expect(TokenType.TOKEN_IDENTIFIER)
        name = id_token.value

        self._expect(TokenType.TOKEN_LPAREN)
        params, defaults, _ = self._parse_parameter_list()
        self._expect(TokenType.TOKEN_RPAREN)

        body = self._parse_block()
        self._expect(TokenType.TOKEN_SELESAI)

        return GeneratorFunctionNode(
            name=name, params=params, defaults=defaults, body=body,
            line=token.line, column=token.column,
        )

    # ============= V5.0: Type System =============

    def _parse_type_alias(self) -> TypeAliasNode:
        """tipe NamaTipe = definisi"""
        token = self._advance()  # tipe
        name_token = self._expect(
            TokenType.TOKEN_IDENTIFIER,
            message="Setelah 'tipe', harus ada nama tipe.",
        )
        self._expect(TokenType.TOKEN_ASSIGN,
                     message="Setelah nama tipe, harus ada '='.")
        definition = self._parse_expression()
        return TypeAliasNode(
            name=name_token.value,
            definition=definition,
            line=token.line,
            column=token.column,
        )

    def _parse_type_annotation(self) -> TypeAnnotationNode:
        """nama :: tipe atau nama :: tipe = default"""
        name_token = self._expect(TokenType.TOKEN_IDENTIFIER)
        
        # Expect :: (COLON COLON) for type annotation
        if self._check(TokenType.TOKEN_COLON):
            self._advance()  # first :
            if self._check(TokenType.TOKEN_COLON):
                self._advance()  # second :
            # If single :, it might be in a context where :: is not expected
            # For now, allow single : as well
        
        type_token = self._expect(TokenType.TOKEN_IDENTIFIER,
                                  message="Setelah ':' atau '::', harus ada nama tipe.")
        type_name = type_token.value
        
        # Check for optional marker ?
        is_optional = False
        if self._check(TokenType.TOKEN_MULTIPLY):
            self._advance()
            is_optional = True
        
        # Check for default value
        default_value = None
        if self._check(TokenType.TOKEN_ASSIGN):
            self._advance()
            default_value = self._parse_expression()
        
        return TypeAnnotationNode(
            name=name_token.value,
            type_name=type_name,
            is_optional=is_optional,
            default_value=default_value,
            line=name_token.line,
            column=name_token.column,
        )

    def _parse_typed_parameter_list(self) -> List[TypeAnnotationNode]:
        """Parse parameter list with type annotations"""
        params = []
        if self._check(TokenType.TOKEN_IDENTIFIER):
            params.append(self._parse_type_annotation())
            while self._match(TokenType.TOKEN_COMMA):
                params.append(self._parse_type_annotation())
        return params

    # ============= V5.0: Interfaces =============

    def _parse_interface(self) -> InterfaceNode:
        """antarmuka Nama { ... } atau antarmuka Nama extends I1, I2 { ... }"""
        token = self._advance()  # antarmuka
        name_token = self._expect(
            TokenType.TOKEN_IDENTIFIER,
            message="Setelah 'antarmuka', harus ada nama.",
        )
        
        # Check for parent interfaces (optional)
        parent_interfaces = []
        if self._check(TokenType.TOKEN_WARISAN):
            self._advance()  # warisan
            if_token = self._expect(TokenType.TOKEN_IDENTIFIER)
            parent_interfaces.append(if_token.value)
            while self._match(TokenType.TOKEN_COMMA):
                if_token = self._expect(TokenType.TOKEN_IDENTIFIER)
                parent_interfaces.append(if_token.value)
        
        self._expect(TokenType.TOKEN_LBRACE,
                     message="Setelah nama antarmuka, harus ada '{'.")
        
        # Consume optional NEWLINE + INDENT
        self._match(TokenType.TOKEN_NEWLINE)
        self._match(TokenType.TOKEN_INDENT)
        
        # Parse method signatures
        methods = []
        while not self._check(TokenType.TOKEN_RBRACE, TokenType.TOKEN_DEDENT, TokenType.TOKEN_EOF):
            while self._match(TokenType.TOKEN_NEWLINE):
                pass
            if self._check(TokenType.TOKEN_RBRACE, TokenType.TOKEN_DEDENT, TokenType.TOKEN_EOF):
                break
            method = self._parse_method_signature()
            methods.append(method)
        
        # Consume DEDENT if present
        self._match(TokenType.TOKEN_DEDENT)
        self._expect(TokenType.TOKEN_RBRACE,
                     message="Antarmuka harus ditutup dengan '}'.")
        
        return InterfaceNode(
            name=name_token.value,
            methods=methods,
            parent_interfaces=parent_interfaces,
            line=token.line,
            column=token.column,
        )

    def _parse_method_signature(self) -> MethodSignatureNode:
        """fungsi nama(param: tipe) -> tipe_return"""
        # Allow 'fungsi' keyword or just start with identifier
        if self._check(TokenType.TOKEN_FUNGSI):
            self._advance()  # fungsi
        name_token = self._expect(TokenType.TOKEN_IDENTIFIER)
        
        self._expect(TokenType.TOKEN_LPAREN)
        params = []
        if not self._check(TokenType.TOKEN_RPAREN):
            params.append(self._parse_type_annotation())
            while self._match(TokenType.TOKEN_COMMA):
                params.append(self._parse_type_annotation())
        self._expect(TokenType.TOKEN_RPAREN)
        
        return_type = None
        if self._check(TokenType.TOKEN_ARROW):
            self._advance()  # ->
            type_token = self._expect(TokenType.TOKEN_IDENTIFIER)
            return_type = type_token.value
        
        return MethodSignatureNode(
            name=name_token.value,
            params=params,
            return_type=return_type,
            line=name_token.line,
            column=name_token.column,
        )

    def _parse_implements(self) -> ImplementsNode:
        """implementasi NamaKelas: Interface1, Interface2"""
        token = self._advance()  # implementasi
        name_token = self._expect(TokenType.TOKEN_IDENTIFIER)
        self._expect(TokenType.TOKEN_COLON)
        
        interfaces = []
        if_token = self._expect(TokenType.TOKEN_IDENTIFIER)
        interfaces.append(if_token.value)
        while self._match(TokenType.TOKEN_COMMA):
            if_token = self._expect(TokenType.TOKEN_IDENTIFIER)
            interfaces.append(if_token.value)
        
        return ImplementsNode(
            class_name=name_token.value,
            interfaces=interfaces,
            line=token.line,
            column=token.column,
        )

    def _parse_abstract_class(self) -> AbstractClassNode:
        """abstrak kelas Nama { ... } atau abstrak kelas Nama warisan Parent { ... }"""
        token = self._advance()  # abstrak
        self._expect(TokenType.TOKEN_KELAS,
                     message="Setelah 'abstrak', harus ada 'kelas'.")
        
        name_token = self._expect(TokenType.TOKEN_IDENTIFIER)
        
        parent = None
        if self._check(TokenType.TOKEN_WARISAN):
            self._advance()  # warisan
            parent_token = self._expect(TokenType.TOKEN_IDENTIFIER)
            parent = parent_token.value
        
        body = []
        methods = []
        abstract_methods = []
        
        self._expect(TokenType.TOKEN_LBRACE,
                     message="Setelah nama kelas, harus ada '{'.")
        
        # Consume optional NEWLINE + INDENT
        self._match(TokenType.TOKEN_NEWLINE)
        self._match(TokenType.TOKEN_INDENT)
        
        while not self._check(TokenType.TOKEN_RBRACE, TokenType.TOKEN_DEDENT, TokenType.TOKEN_EOF):
            while self._match(TokenType.TOKEN_NEWLINE):
                pass
            if self._check(TokenType.TOKEN_RBRACE, TokenType.TOKEN_DEDENT, TokenType.TOKEN_EOF):
                break
            
            if self._check(TokenType.TOKEN_ABSTRAK):
                self._advance()  # abstrak
                self._expect(TokenType.TOKEN_FUNGSI)
                method_token = self._expect(TokenType.TOKEN_IDENTIFIER)
                abstract_methods.append(method_token.value)
                # Skip parameters and body
                self._expect(TokenType.TOKEN_LPAREN)
                while not self._check(TokenType.TOKEN_RPAREN):
                    self._advance()
                self._expect(TokenType.TOKEN_RPAREN)
                # Skip newline after abstract method
                while self._match(TokenType.TOKEN_NEWLINE):
                    pass
            elif self._check(TokenType.TOKEN_FUNGSI):
                # Peek ahead: is this a signature (no body) or a full method (has body)?
                # Save state and try method signature first
                saved_pos = self.pos
                saved_token = self.current_token
                try:
                    sig = self._parse_method_signature()
                    # Check if next meaningful token suggests a body (INDENT or LBRACE)
                    while self._match(TokenType.TOKEN_NEWLINE):
                        pass
                    if self._check(TokenType.TOKEN_INDENT, TokenType.TOKEN_LBRACE):
                        # Has body → restore and parse as full function
                        self.pos = saved_pos
                        self.current_token = saved_token
                        func = self._parse_function()
                        methods.append(func)
                        body.append(func)
                    else:
                        # No body → it's an abstract method signature
                        abstract_methods.append(sig.name)
                        # Consume any trailing newline
                        while self._match(TokenType.TOKEN_NEWLINE):
                            pass
                except Exception:
                    # Restore and try as function
                    self.pos = saved_pos
                    self.current_token = saved_token
                    func = self._parse_function()
                    methods.append(func)
                    body.append(func)
            else:
                # Skip unexpected tokens
                self._advance()
        
        # Consume DEDENT if present
        self._match(TokenType.TOKEN_DEDENT)
        self._expect(TokenType.TOKEN_RBRACE,
                     message="Kelas harus ditutup dengan '}'.")
        
        return AbstractClassNode(
            name=name_token.value,
            parent=parent,
            methods=methods,
            body=body,
            abstract_methods=abstract_methods,
            line=name_token.line,
            column=name_token.column,
        )

    # ============= V5.0: Enhanced Pattern Matching =============

    def _parse_destructuring_pattern(self) -> DestructuringPatternNode:
        """[a, b, c] atau {a, b, c}"""
        if self._check(TokenType.TOKEN_LBRACKET):
            self._advance()  # [
            variables = []
            var_token = self._expect(TokenType.TOKEN_IDENTIFIER)
            variables.append(var_token.value)
            while self._match(TokenType.TOKEN_COMMA):
                var_token = self._expect(TokenType.TOKEN_IDENTIFIER)
                variables.append(var_token.value)
            self._expect(TokenType.TOKEN_RBRACKET)
            return DestructuringPatternNode(variables=variables, is_array=True,
                                            line=self.current_token.line, column=self.current_token.column)
        elif self._check(TokenType.TOKEN_LBRACE):
            self._advance()  # {
            variables = []
            var_token = self._expect(TokenType.TOKEN_IDENTIFIER)
            variables.append(var_token.value)
            while self._match(TokenType.TOKEN_COMMA):
                var_token = self._expect(TokenType.TOKEN_IDENTIFIER)
                variables.append(var_token.value)
            self._expect(TokenType.TOKEN_RBRACE)
            return DestructuringPatternNode(variables=variables, is_array=False,
                                            line=self.current_token.line, column=self.current_token.column)
        else:
            raise self._error(
                message="Destructuring harus dimulai dengan '[' atau '{'.",
                example="[a, b, c] atau {nama, umur}",
            )

    # ============= V5.0: Higher-Order Functions =============

    def _parse_map_call(self) -> MapNode:
        """peta(iterable, fungsi) atau peta(fungsi) [untuk pipeline]"""
        token = self._advance()  # peta
        self._expect(TokenType.TOKEN_LPAREN)
        first = self._parse_expression()
        if self._match(TokenType.TOKEN_COMMA):
            function = self._parse_expression()
            self._expect(TokenType.TOKEN_RPAREN)
            return MapNode(iterable=first, function=function,
                           line=token.line, column=token.column)
        self._expect(TokenType.TOKEN_RPAREN)
        # Bentuk pipeline: iterable diisi oleh nilai kiri |>
        return MapNode(iterable=None, function=first,
                       line=token.line, column=token.column)

    def _parse_filter_call(self) -> FilterNode:
        """saring(iterable, kondisi) atau saring(kondisi) [untuk pipeline]"""
        token = self._advance()  # saring
        self._expect(TokenType.TOKEN_LPAREN)
        first = self._parse_expression()
        if self._match(TokenType.TOKEN_COMMA):
            condition = self._parse_expression()
            self._expect(TokenType.TOKEN_RPAREN)
            return FilterNode(iterable=first, condition=condition,
                              line=token.line, column=token.column)
        self._expect(TokenType.TOKEN_RPAREN)
        return FilterNode(iterable=None, condition=first,
                          line=token.line, column=token.column)

    def _parse_reduce_call(self) -> ReduceNode:
        """kurangi(iterable, fungsi, awal?) atau kurangi(fungsi, awal?) [untuk pipeline]"""
        token = self._advance()  # kurangi
        self._expect(TokenType.TOKEN_LPAREN)
        first = self._parse_expression()
        second = None
        initial = None
        if self._match(TokenType.TOKEN_COMMA):
            second = self._parse_expression()
            if self._match(TokenType.TOKEN_COMMA):
                initial = self._parse_expression()
        self._expect(TokenType.TOKEN_RPAREN)

        # Bentuk pipeline: argumen pertama adalah fungsi (lambda) atau hanya ada satu argumen
        is_pipeline = isinstance(first, LambdaNode) or second is None
        if is_pipeline:
            return ReduceNode(iterable=None, function=first, initial=second,
                              line=token.line, column=token.column)
        # Bentuk normal: kurangi(iterable, fungsi, awal?)
        return ReduceNode(iterable=first, function=second, initial=initial,
                          line=token.line, column=token.column)

    # ============= V5.0: Result/Option Types =============

    def _parse_result(self) -> ResultNode:
        """Benar(value) atau Salah(error)"""
        token = self.current_token
        if self._check(TokenType.TOKEN_BENAR_VAL):
            self._advance()  # Benar
            self._expect(TokenType.TOKEN_LPAREN)
            value = self._parse_expression()
            self._expect(TokenType.TOKEN_RPAREN)
            return ResultNode(is_success=True, value=value,
                              line=token.line, column=token.column)
        elif self._check(TokenType.TOKEN_SALAH_VAL):
            self._advance()  # Salah
            self._expect(TokenType.TOKEN_LPAREN)
            value = self._parse_expression()
            self._expect(TokenType.TOKEN_RPAREN)
            return ResultNode(is_success=False, value=value,
                              line=token.line, column=token.column)
        else:
            raise self._error(
                message="Result harus 'Benar(value)' atau 'Salah(error)'.",
                example="Benar(42) atau Salah(\"error\")",
            )

    def _parse_option(self) -> OptionNode:
        """Ada(value) atau Kosong()"""
        token = self.current_token
        if self._check(TokenType.TOKEN_SOME):
            self._advance()  # Ada
            self._expect(TokenType.TOKEN_LPAREN)
            value = self._parse_expression()
            self._expect(TokenType.TOKEN_RPAREN)
            return OptionNode(has_value=True, value=value,
                              line=token.line, column=token.column)
        elif self._check(TokenType.TOKEN_KOSONG_KW):
            self._advance()  # Kosong
            if self._check(TokenType.TOKEN_LPAREN):
                self._advance()  # (
                self._expect(TokenType.TOKEN_RPAREN)
            return OptionNode(has_value=False, value=None,
                              line=token.line, column=token.column)
        else:
            raise self._error(
                message="Option harus 'Ada(value)' atau 'Kosong()'.",
                example="Ada(42) atau Kosong()",
            )

    # ============= V5.0: Macros =============

    def _parse_macro_def(self) -> MacroDefNode:
        """makro Nama(param?) { body }"""
        token = self._advance()  # makro
        name_token = self._expect(TokenType.TOKEN_IDENTIFIER)
        
        params = []
        if self._check(TokenType.TOKEN_LPAREN):
            self._advance()  # (
            if not self._check(TokenType.TOKEN_RPAREN):
                var_token = self._expect(TokenType.TOKEN_IDENTIFIER)
                params.append(var_token.value)
                while self._match(TokenType.TOKEN_COMMA):
                    var_token = self._expect(TokenType.TOKEN_IDENTIFIER)
                    params.append(var_token.value)
            self._expect(TokenType.TOKEN_RPAREN)
        
        body = self._parse_block()
        self._expect(TokenType.TOKEN_SELESAI,
                     message="Macro harus ditutup dengan 'selesai'.")
        
        return MacroDefNode(
            name=name_token.value,
            params=params,
            body=body,
            line=token.line,
            column=token.column,
        )

    def _parse_macro_call(self) -> MacroCallNode:
        """Nama(args...)"""
        token = self._advance()  # macro name
        self._expect(TokenType.TOKEN_LPAREN)
        args = []
        if not self._check(TokenType.TOKEN_RPAREN):
            args.append(self._parse_expression())
            while self._match(TokenType.TOKEN_COMMA):
                args.append(self._parse_expression())
        self._expect(TokenType.TOKEN_RPAREN)
        return MacroCallNode(
            name=token.value,
            args=args,
            line=token.line,
            column=token.column,
        )

    # ============= V5.0: Module System =============

    def _parse_namespace(self) -> NamespaceNode:
        """ruang nama NamaModule { ... }"""
        token = self._advance()  # ruang
        self._expect(TokenType.TOKEN_IDENTIFIER,
                     message="Setelah 'ruang', harus ada 'nama'.")
        name_token = self._expect(TokenType.TOKEN_IDENTIFIER)
        
        body = self._parse_block()
        self._expect(TokenType.TOKEN_SELESAI,
                     message="Namespace harus ditutup dengan 'selesai'.")
        
        return NamespaceNode(
            name=name_token.value,
            body=body,
            line=token.line,
            column=token.column,
        )

    def _parse_use_statement(self) -> UseNode:
        """pakai NamaModule (sebagai alias)?"""
        token = self._advance()  # pakai
        module_parts = []
        name_token = self._expect(TokenType.TOKEN_IDENTIFIER)
        module_parts.append(name_token.value)
        
        while self._match(TokenType.TOKEN_DOT):
            name_token = self._expect(TokenType.TOKEN_IDENTIFIER)
            module_parts.append(name_token.value)
        
        module = ".".join(module_parts)
        
        alias = None
        if self._check(TokenType.TOKEN_SEBAGAI):
            self._advance()  # sebagai
            alias_token = self._expect(TokenType.TOKEN_IDENTIFIER)
            alias = alias_token.value
        
        return UseNode(
            module=module,
            alias=alias,
            line=token.line,
            column=token.column,
        )

    # ============= V5.0: Access Modifiers =============

    def _parse_access_modifier(self) -> AccessModifierNode:
        """publik/privat/terlindungi fungsi/kelas"""
        token = self.current_token
        modifier = "publik"
        
        if self._check(TokenType.TOKEN_PUBLIK):
            self._advance()
            modifier = "publik"
        elif self._check(TokenType.TOKEN_PRIVAT):
            self._advance()
            modifier = "privat"
        elif self._check(TokenType.TOKEN_TERLINDUNGI):
            self._advance()
            modifier = "terlindungi"
        
        # Parse the target (function, class, or variable)
        if self._check(TokenType.TOKEN_FUNGSI):
            target = self._parse_function()
        elif self._check(TokenType.TOKEN_KELAS):
            target = self._parse_class()
        else:
            target = self._parse_assignment()
        
        return AccessModifierNode(
            modifier=modifier,
            target=target,
            line=token.line,
            column=token.column,
        )

    def _parse_static_modifier(self) -> FunctionNode:
        """statis fungsi — method tanpa self"""
        token = self._advance()  # statis
        if self._check(TokenType.TOKEN_FUNGSI):
            func = self._parse_function()
            func.is_static = True
            return func
        raise self._error(
            message="Setelah 'statis', harus ada 'fungsi'.",
            solution="Tulis 'statis fungsi nama() ... selesai'",
        )

    # ============= V5.0: Null Coalescing =============

    def _parse_null_coalescing(self, left: ASTNode) -> NullCoalescingNode:
        """x ?? default_value"""
        token = self._advance()  # ??
        right = self._parse_expression()
        return NullCoalescingNode(left=left, right=right,
                                  line=left.line, column=left.column)

    # ============= V5.0: Optional Chaining =============

    def _parse_optional_chaining(self, obj: ASTNode) -> OptionalChainingNode:
        """obj?.attr"""
        token = self._advance()  # ?.
        attr_token = self._expect(TokenType.TOKEN_IDENTIFIER,
                                  message="Setelah '?.', harus ada nama atribut.")
        return OptionalChainingNode(
            object=obj,
            property=attr_token.value,
            line=obj.line,
            column=obj.column,
        )

    # ============= V5.0: For Each with Index =============

    def _parse_for_each(self) -> ForEachNode:
        """untuk setiap item dalam iterable lakukan ... selesai"""
        token = self._advance()  # untuk
        self._expect(TokenType.TOKEN_IDENTIFIER,
                     message="Setelah 'untuk', harus ada 'setiap'.")
        # This is handled by checking for 'setiap' keyword in the main statement parser
        var_token = self._expect(TokenType.TOKEN_IDENTIFIER)
        
        index_var = None
        if self._match(TokenType.TOKEN_COMMA):
            index_token = self._expect(TokenType.TOKEN_IDENTIFIER)
            index_var = index_token.value
        
        self._expect(TokenType.TOKEN_DALAM)
        iterable = self._parse_expression()
        
        self._expect(TokenType.TOKEN_LAKUKAN,
                     message="Setelah iterable, harus ada 'lakukan'.")
        
        body = self._parse_block()
        self._expect(TokenType.TOKEN_SELESAI)
        
        return ForEachNode(
            variable=var_token.value,
            index_variable=index_var,
            iterable=iterable,
            body=body,
            line=token.line,
            column=token.column,
        )

    # ============= V5.0: Chained Comparisons =============

    def _parse_chained_comparison(self, left: ASTNode) -> ChainedComparisonNode:
        """0 < x < 10"""
        operators = []
        comparators = []
        
        while self._check(TokenType.TOKEN_LT, TokenType.TOKEN_GT,
                          TokenType.TOKEN_LTE, TokenType.TOKEN_GTE):
            op_token = self._advance()
            op_map = {
                TokenType.TOKEN_LT: "<",
                TokenType.TOKEN_GT: ">",
                TokenType.TOKEN_LTE: "<=",
                TokenType.TOKEN_GTE: ">=",
            }
            operators.append(op_map[op_token.type])
            comparators.append(self._parse_addition())
        
        return ChainedComparisonNode(
            left=left,
            operators=operators,
            comparators=comparators,
            line=left.line,
            column=left.column,
        )
