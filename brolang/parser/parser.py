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
)
from brolang.exceptions import ParserError


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
        """Membuat ParserError dengan informasi token saat ini."""
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

        if token_type == TokenType.TOKEN_BUAT:
            return self._parse_assignment()
        elif token_type == TokenType.TOKEN_TULIS:
            return self._parse_print()
        elif token_type == TokenType.TOKEN_JIKA:
            return self._parse_if()
        elif token_type == TokenType.TOKEN_SELAMA:
            return self._parse_while()
        elif token_type == TokenType.TOKEN_UNTUK:
            return self._parse_for()
        elif token_type == TokenType.TOKEN_FUNGSI:
            return self._parse_function()
        elif token_type == TokenType.TOKEN_KELAS:
            return self._parse_class()
        elif token_type == TokenType.TOKEN_IMPOR:
            return self._parse_import()
        elif token_type == TokenType.TOKEN_DARI:
            return self._parse_from_import()
        elif token_type == TokenType.TOKEN_COBA:
            return self._parse_try()
        elif token_type == TokenType.TOKEN_COCOKKAN:
            return self._parse_match()
        elif token_type == TokenType.TOKEN_ENUM:
            return self._parse_enum()
        elif token_type == TokenType.TOKEN_STRUKTUR:
            return self._parse_struct()
        elif token_type == TokenType.TOKEN_KEMBALI:
            return self._parse_return()
        elif token_type == TokenType.TOKEN_BREAK:
            self._advance()
            return BreakNode(line=self.current_token.line, column=self.current_token.column)
        elif token_type == TokenType.TOKEN_CONTINUE:
            self._advance()
            return ContinueNode(line=self.current_token.line, column=self.current_token.column)
        elif token_type == TokenType.TOKEN_IDENTIFIER:
            # Could be reassignment, method call, or expression
            # Peek ahead to see if it's assignment
            if self._peek(1) == TokenType.TOKEN_ASSIGN:
                return self._parse_reassignment()
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
                return self._parse_expression()
        else:
            return self._parse_expression()

    # ============= Assignment =============

    def _parse_assignment(self) -> AssignmentNode:
        """buat identifier (. identifier)? = expression"""
        token = self._advance()  # buat
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

        value = None
        if self._match(TokenType.TOKEN_ASSIGN):
            value = self._parse_expression()
        else:
            value = KosongNode(line=self.current_token.line, column=self.current_token.column)

        return AssignmentNode(
            target=target,
            value=value,
            is_declaration=True,
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
        """selama expression lakukan block selesai"""
        token = self._advance()  # selama
        condition = self._parse_expression()

        self._expect(
            TokenType.TOKEN_LAKUKAN,
            message="Setelah kondisi 'selama', harus ada 'lakukan'.",
            solution="Tambahkan 'lakukan' setelah kondisi.",
            example="selama x < 10 lakukan\n    tulis x\n    x = x + 1\nselesai",
        )

        body = self._parse_block()

        self._expect(
            TokenType.TOKEN_SELESAI,
            message="Blok 'selama' harus ditutup dengan 'selesai'.",
            solution="Tambahkan 'selesai' di akhir blok selama.",
            example="selama x < 10 lakukan\n    tulis x\nselesai",
        )

        return WhileNode(condition=condition, body=body, line=token.line, column=token.column)

    # ============= For Loop =============

    def _parse_for(self) -> ForNode:
        """untuk identifier dalam expression lakukan block selesai"""
        token = self._advance()  # untuk
        id_token = self._expect(
            TokenType.TOKEN_IDENTIFIER,
            message="Setelah 'untuk', harus ada nama variabel.",
            solution="Tulis nama variabel setelah 'untuk'.",
            example="untuk item dalam list lakukan\n    tulis item\nselesai",
        )
        variable = id_token.value

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

        self._expect(
            TokenType.TOKEN_SELESAI,
            message="Blok 'untuk' harus ditutup dengan 'selesai'.",
            solution="Tambahkan 'selesai' di akhir blok untuk.",
        )

        return ForNode(
            variable=variable,
            iterable=iterable,
            body=body,
            line=token.line,
            column=token.column,
        )

    # ============= Function =============

    def _parse_function(self) -> FunctionNode:
        """fungsi identifier(params) block selesai"""
        token = self._advance()  # fungsi
        id_token = self._expect(
            TokenType.TOKEN_IDENTIFIER,
            message="Setelah 'fungsi', harus ada nama fungsi.",
            solution="Tulis nama fungsi setelah 'fungsi'.",
            example='fungsi sapa(nama)\n    kembali "Halo " + nama\nselesai',
        )
        name = id_token.value

        self._expect(
            TokenType.TOKEN_LPAREN,
            message="Setelah nama fungsi, harus ada '('.",
        )

        params = self._parse_parameter_list()

        self._expect(
            TokenType.TOKEN_RPAREN,
            message="Setelah parameter, harus ada ')'.",
        )

        body = self._parse_block()

        self._expect(
            TokenType.TOKEN_SELESAI,
            message="Fungsi harus ditutup dengan 'selesai'.",
            solution="Tambahkan 'selesai' di akhir fungsi.",
        )

        return FunctionNode(
            name=name,
            params=params,
            body=body,
            line=token.line,
            column=token.column,
        )

    def _parse_parameter_list(self) -> List[str]:
        """Mem-parse daftar parameter."""
        params = []
        if self._check(TokenType.TOKEN_IDENTIFIER):
            token = self._advance()
            params.append(token.value)
            while self._match(TokenType.TOKEN_COMMA):
                token = self._expect(
                    TokenType.TOKEN_IDENTIFIER,
                    message="Setelah koma, harus ada nama parameter.",
                )
                params.append(token.value)
        return params

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

        body = self._parse_block()

        # Parse methods from body
        methods = []
        for stmt in body:
            if isinstance(stmt, FunctionNode):
                methods.append(
                    MethodNode(
                        name=stmt.name,
                        params=stmt.params,
                        body=stmt.body,
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

    # ============= Import =============

    def _parse_import(self) -> ImportNode:
        """impor identifier (. identifier)*"""
        token = self._advance()  # impor
        parts = []
        id_token = self._expect(
            TokenType.TOKEN_IDENTIFIER,
            message="Setelah 'impor', harus ada nama modul.",
            solution="Tulis nama modul setelah 'impor'.",
            example="impor matematika",
        )
        parts.append(id_token.value)

        while self._match(TokenType.TOKEN_DOT):
            id_token = self._expect(
                TokenType.TOKEN_IDENTIFIER,
                message="Setelah '.', harus ada nama submodul.",
            )
            parts.append(id_token.value)

        module = ".".join(parts)

        alias = None
        if self._check(TokenType.TOKEN_IDENTIFIER) and self.current_token.value == "sebagai":
            self._advance()
            alias_token = self._expect(
                TokenType.TOKEN_IDENTIFIER,
                message="Setelah 'sebagai', harus ada alias.",
            )
            alias = alias_token.value

        return ImportNode(module=module, alias=alias, line=token.line, column=token.column)

    def _parse_from_import(self) -> FromImportNode:
        """dari module impor identifier (, identifier)*"""
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
        """coba block tangkap identifier block selesai"""
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

        self._expect(
            TokenType.TOKEN_SELESAI,
            message="Blok 'coba' harus ditutup dengan 'selesai'.",
        )

        return TryNode(body=body, catch_var=var_name, catch_body=catch_body, line=token.line, column=token.column)

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
        default_case = None

        while not self._check(TokenType.TOKEN_RBRACE, TokenType.TOKEN_DEDENT, TokenType.TOKEN_EOF):
            # Skip commas and newlines between cases
            while self._match(TokenType.TOKEN_COMMA) or self._match(TokenType.TOKEN_NEWLINE):
                pass
            if self._check(TokenType.TOKEN_RBRACE, TokenType.TOKEN_DEDENT, TokenType.TOKEN_EOF):
                break

            # Parse pattern
            if self._check(TokenType.TOKEN_IDENTIFIER) and self.current_token.value == "_":
                self._advance()  # consume _
                pattern = WildcardNode(line=self.current_token.line, column=self.current_token.column)
                self._expect(TokenType.TOKEN_COLON, message="Setelah '_', harus ada ':'.")
                body = self._parse_match_case_body()
                default_case = body
            else:
                pattern = self._parse_expression()
                self._expect(TokenType.TOKEN_COLON, message="Setelah pattern, harus ada ':'.")
                body = self._parse_match_case_body()
                cases.append((pattern, body))

        # Consume DEDENT if present
        self._match(TokenType.TOKEN_DEDENT)
        self._expect(TokenType.TOKEN_RBRACE, message="Match harus ditutup dengan '}'.")

        return MatchNode(value=value, cases=cases, default_case=default_case,
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

        members = []
        if not self._check(TokenType.TOKEN_RBRACE):
            member_token = self._expect(
                TokenType.TOKEN_IDENTIFIER,
                message="Setelah '{', harus ada nama member enum.",
            )
            members.append(member_token.value)
            while self._match(TokenType.TOKEN_COMMA):
                member_token = self._expect(TokenType.TOKEN_IDENTIFIER)
                members.append(member_token.value)

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

        fields = []
        if not self._check(TokenType.TOKEN_RBRACE):
            field_token = self._expect(
                TokenType.TOKEN_IDENTIFIER,
                message="Setelah '{', harus ada nama field.",
            )
            fields.append(field_token.value)
            while self._match(TokenType.TOKEN_COMMA):
                field_token = self._expect(TokenType.TOKEN_IDENTIFIER)
                fields.append(field_token.value)

        self._expect(TokenType.TOKEN_RBRACE, message="Struktur harus ditutup dengan '}'.")

        return StructNode(name=name_token.value, fields=fields,
                          line=token.line, column=token.column)

    # ============= V2: Lambda =============

    def _parse_lambda(self) -> LambdaNode:
        """lalu(params) expr"""
        token = self._advance()  # lalu
        self._expect(TokenType.TOKEN_LPAREN, message="Setelah 'lalu', harus ada '('.")
        params = self._parse_parameter_list()
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
        return self._parse_or()

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
        return self._parse_comparison()

    def _parse_comparison(self) -> ASTNode:
        left = self._parse_addition()
        while self._check(
            TokenType.TOKEN_EQ, TokenType.TOKEN_NEQ,
            TokenType.TOKEN_GT, TokenType.TOKEN_LT,
            TokenType.TOKEN_GTE, TokenType.TOKEN_LTE,
        ):
            op_token = self._advance()
            right = self._parse_addition()
            op_map = {
                TokenType.TOKEN_EQ: "==",
                TokenType.TOKEN_NEQ: "!=",
                TokenType.TOKEN_GT: ">",
                TokenType.TOKEN_LT: "<",
                TokenType.TOKEN_GTE: ">=",
                TokenType.TOKEN_LTE: "<=",
            }
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
            node = self._parse_expression()
            self._expect(TokenType.TOKEN_RPAREN,
                         message="Tanda kurung tidak ditutup.",
                         solution="Tambahkan ')' setelah ekspresi.",
                         example="(1 + 2)")
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
            node = self._parse_input()
        else:
            raise self._error(
                message=f"Token tidak terduga: '{token.value}' ({token.type.name}).",
                solution="Periksa sintaks di sekitar token ini.",
            )

        # Handle chained calls and accesses
        node = self._parse_postfix(node)
        return node

    def _parse_identifier_continuation(self, token: Token) -> ASTNode:
        """Mem-parse identifier dan kelanjutannya (call, access)."""
        node = IdentifierNode(name=token.value, line=token.line, column=token.column)

        # Function call
        if self._check(TokenType.TOKEN_LPAREN):
            self._advance()  # (
            args = self._parse_argument_list()
            self._expect(TokenType.TOKEN_RPAREN,
                         message="Argumen fungsi tidak ditutup.",
                         solution="Tambahkan ')' setelah argumen.")
            node = CallNode(function=node, args=args, line=token.line, column=token.column)

        return node

    def _parse_postfix(self, node: ASTNode) -> ASTNode:
        """Mem-parse postfix operations: calls, indexing, attribute access."""
        while True:
            if self._check(TokenType.TOKEN_LPAREN):
                # Function call on expression
                if isinstance(node, CallNode):
                    break
                self._advance()  # (
                args = self._parse_argument_list()
                self._expect(TokenType.TOKEN_RPAREN)
                node = CallNode(function=node, args=args, line=node.line, column=node.column)
            elif self._check(TokenType.TOKEN_LBRACKET):
                # Indexing
                self._advance()  # [
                index = self._parse_expression()
                self._expect(TokenType.TOKEN_RBRACKET,
                             message="Indexing tidak ditutup.",
                             solution="Tambahkan ']' setelah indeks.",
                             example="list[0]")
                node = IndexNode(target=node, index=index, line=node.line, column=node.column)
            elif self._check(TokenType.TOKEN_DOT):
                # Attribute/method access
                self._advance()  # .
                id_token = self._expect(
                    TokenType.TOKEN_IDENTIFIER,
                    message="Setelah '.', harus ada nama atribut atau method.",
                )
                attr_name = id_token.value

                if self._check(TokenType.TOKEN_LPAREN):
                    # Method call: obj.method()
                    self._advance()  # (
                    args = self._parse_argument_list()
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
        """Mem-parse daftar argumen fungsi."""
        args = []
        if not self._check(TokenType.TOKEN_RPAREN):
            args.append(self._parse_expression())
            while self._match(TokenType.TOKEN_COMMA):
                args.append(self._parse_expression())
        return args

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
                iterable = self._parse_expression()

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

    def _parse_object_literal(self) -> ObjectNode:
        """{string: expression (, string: expression)*}"""
        token = self._advance()  # {
        entries = {}
        if not self._check(TokenType.TOKEN_RBRACE):
            key_token = self._expect(
                TokenType.TOKEN_STRING,
                message="Kunci objek harus berupa string.",
                solution="Gunakan string sebagai kunci.",
                example='{"nama": "Budi"}',
            )
            self._expect(TokenType.TOKEN_COLON,
                         message="Setelah kunci, harus ada ':'.",
                         example='{"nama": "Budi"}')
            value = self._parse_expression()
            entries[key_token.value] = value

            while self._match(TokenType.TOKEN_COMMA):
                key_token = self._expect(TokenType.TOKEN_STRING)
                self._expect(TokenType.TOKEN_COLON)
                value = self._parse_expression()
                entries[key_token.value] = value

        self._expect(TokenType.TOKEN_RBRACE,
                     message="Objek literal tidak ditutup.",
                     solution="Tambahkan '}' setelah entry objek.",
                     example='{"nama": "Budi"}')
        return ObjectNode(entries=entries, line=token.line, column=token.column)

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
