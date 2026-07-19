'''
Implementasi Lexer BroLang
===========================

Lexer ini mengubah kode sumber BroLang menjadi token-token.
Mendukung:
- Unicode dan UTF-8 penuh
- Keyword Bahasa Indonesia
- Komentar baris tunggal (#) dan multi-baris (#| ... |#)
- String single-line dan multi-line
- Indentation tracking (seperti Python)
- Posisi error yang presisi

Design:
    Lexer bekerja secara sekuensial, membaca karakter per karakter
    dan menghasilkan token. Menggunakan pendekatan maximal munch
    untuk memastikan token terpanjang dikenali terlebih dahulu.
'''

from typing import List, Optional
from brolang.token_types import Token, TokenType, KEYWORDS
from brolang.exceptions import LexerError


class Lexer:
    '''Lexer untuk bahasa BroLang.

    Attributes:
        source: Kode sumber yang akan di-lex
        tokens: Daftar token yang dihasilkan
        pos: Posisi karakter saat ini
        line: Baris saat ini
        column: Kolom saat ini
        indent_stack: Stack untuk tracking indentasi
    '''

    def __init__(self, source: str, file_path: str = ''):
        self.source: str = source
        self.file_path: str = file_path
        self.tokens: List[Token] = []
        self.pos: int = 0
        self.line: int = 1
        self.column: int = 1
        self.indent_stack: List[int] = [0]
        self._at_line_start: bool = True
        self._pending_indents: List[Token] = []

    def _current(self) -> Optional[str]:
        '''Mengembalikan karakter saat ini, atau None jika EOF.'''
        if self.pos >= len(self.source):
            return None
        return self.source[self.pos]

    def _peek(self, offset: int = 1) -> Optional[str]:
        '''Melihat karakter ke depan tanpa maju.'''
        idx = self.pos + offset
        if idx >= len(self.source):
            return None
        return self.source[idx]

    def _advance(self) -> str:
        '''Maju satu karakter dan mengembalikannya.'''
        char = self.source[self.pos]
        self.pos += 1
        if char == '\n':
            self.line += 1
            self.column = 1
            self._at_line_start = True
        else:
            self.column += 1
        return char

    def _error(self, message: str, solution: str = '', example: str = '') -> LexerError:
        '''Membuat LexerError dengan informasi lokasi.'''
        return LexerError(
            message=message,
            line=self.line,
            column=self.column,
            solution=solution,
            example=example,
            file_path=self.file_path,
            source_line=self._get_source_line(),
        )

    def _get_source_line(self) -> str:
        '''Mendapatkan baris sumber saat ini untuk ditampilkan.'''
        lines = self.source.split('\n')
        if 1 <= self.line <= len(lines):
            return lines[self.line - 1]
        return ''

    def _skip_whitespace(self) -> None:
        '''Melewati spasi dan tab (bukan newline).'''
        while self._current() is not None and self._current() in ' \t\r':
            self._advance()

    def _skip_comment(self) -> None:
        '''Melewati komentar.'''
        if self._current() == '#':
            # Komentar baris tunggal: # sampai akhir baris
            while self._current() is not None and self._current() != '\n':
                self._advance()
        elif self._current() == '|' and self._peek() == '#':
            # Komentar multi-baris: |# ... #|
            self._advance()  # |
            self._advance()  # #
            while self._current() is not None:
                if self._current() == '#' and self._peek() == '|':
                    self._advance()  # #
                    self._advance()  # |
                    return
                self._advance()
            raise self._error(
                message='Komentar multi-baris tidak ditutup.',
                solution='Tambahkan #| pada akhir komentar.',
                example='#| ini adalah komentar #|',
            )

    def _handle_indent(self) -> None:
        '''Menangani indentasi dan menghasilkan token INDENT/DEDENT.'''
        self._at_line_start = False
        indent = 0

        # Count leading whitespace
        while self._current() is not None and self._current() in ' \t':
            if self._current() == ' ':
                indent += 1
            elif self._current() == '\t':
                indent += 4
            self._advance()

        # Skip blank lines (only whitespace) and comments
        while self._current() is not None and self._current() in ('#', '\n'):
            if self._current() == '#':
                self._skip_comment()
            if self._current() == '\n':
                self._advance()
                indent = 0
                self._at_line_start = True
                while self._current() is not None and self._current() in ' \t':
                    if self._current() == ' ':
                        indent += 1
                    elif self._current() == '\t':
                        indent += 4
                    self._advance()
                self._at_line_start = False

        # If we reached EOF or a newline, nothing more to do
        if self._current() is None:
            return

        current_indent = self.indent_stack[-1]

        if indent > current_indent:
            self.indent_stack.append(indent)
            self.tokens.append(Token(TokenType.TOKEN_INDENT, None, self.line, self.column))
        elif indent < current_indent:
            while indent < self.indent_stack[-1]:
                self.indent_stack.pop()
                self.tokens.append(Token(TokenType.TOKEN_DEDENT, None, self.line, self.column))
            if indent != self.indent_stack[-1]:
                raise self._error(
                    message='Indentasi tidak konsisten.',
                    solution='Periksa jumlah spasi/tab agar konsisten.',
                    example='jika x > 0 maka\n    tulis "positif"\nselesai',
                )

    def _at_chainable_newline(self) -> bool:
        '''Periksa apakah kita di awal baris baru.'''
        return self._at_line_start

    def _read_string(self, quote: str) -> str:
        '''Membaca string literal.

        Mendukung:
        - String baris tunggal: "teks" atau 'teks'
        - String multi-baris: """teks""" atau \\'\\'\\'teks\\'\\'\\'

        Args:
            quote: Karakter kutip yang digunakan (" atau \\')

        Returns:
            string literal
        '''
        result = []
        # Cek apakah ini multi-line string
        if self._peek() == quote and self._peek(2) == quote:
            self._advance()  # kutip ke-2
            self._advance()  # kutip ke-3

            while self._current() is not None:
                if self._current() == '\\' and self._peek() is not None:
                    result.append(self._read_escape())
                elif self._current() == quote and self._peek() == quote and self._peek(2) == quote:
                    self._advance()  # kutip ke-2
                    self._advance()  # kutip ke-3
                    break
                elif self._current() == '\n':
                    result.append(self._advance())
                else:
                    result.append(self._advance())
            else:
                raise self._error(
                    message=f'String multi-baris tidak ditutup.',
                    solution=f'Tambahkan {quote*3} pada akhir string.',
                    example=f'{quote*3}teks{quote*3}',
                )
        else:
            while self._current() is not None:
                if self._current() == '\\' and self._peek() is not None:
                    result.append(self._read_escape())
                elif self._current() == quote:
                    self._advance()  # consume closing quote
                    break
                elif self._current() == '\n':
                    raise self._error(
                        message='String tidak boleh mengandung baris baru tanpa kutip multi-baris.',
                        solution=f'Gunakan {quote*3} untuk string multi-baris.',
                        example=f'{quote*3}teks panjang{quote*3}',
                    )
                else:
                    result.append(self._advance())
            else:
                raise self._error(
                    message=f'String tidak ditutup.',
                    solution=f'Tambahkan {quote} pada akhir teks.',
                    example=f'{quote}Halo{quote}',
                )

        return ''.join(result)

    def _read_escape(self) -> str:
        '''Membaca escape character.'''
        self._advance()  # backslash
        if self._current() is None:
            raise self._error(
                message='Escape sequence tidak lengkap.',
                solution='Tambahkan karakter setelah backslash.',
                example='tulis "Halo\\nDunia"',
            )
        char = self._advance()
        escape_map = {
            'n': '\n',
            't': '\t',
            'r': '\r',
            '"': '"',
            "'": "'",
            '\\': '\\',
            '0': '\0',
        }
        return escape_map.get(char, char)

    def _read_fstring(self, quote: str) -> Token:
        '''Membaca f-string: f"...{expr}..."
        
        F-strings mendukung interpolasi variabel dan ekspresi.
        Hasilnya adalah token TOKEN_FSTRING dengan value berisi
        list of (type, value) tuples:
        - ("literal", "teks")
        - ("expr", ASTNode)
        '''
        start_line = self.line
        start_col = self.column - 2  # -2 for 'f' and quote
        parts = []
        current_literal = []

        while self._current() is not None:
            if self._current() == '\\' and self._peek() is not None:
                current_literal.append(self._read_escape())
            elif self._current() == '{' and self._peek() != '{':
                # Save literal so far
                if current_literal:
                    parts.append(("literal", ''.join(current_literal)))
                    current_literal = []
                # Read expression inside {}
                self._advance()  # consume {
                expr_chars = []
                depth = 1
                while self._current() is not None and depth > 0:
                    if self._current() == '{':
                        depth += 1
                    elif self._current() == '}':
                        depth -= 1
                        if depth == 0:
                            break
                    if self._current() == '\n':
                        raise self._error(
                            message='Ekspresi dalam f-string tidak boleh multi-baris.',
                            solution='Gunakan variabel atau ekspresi sederhana dalam {}.',
                        )
                    expr_chars.append(self._advance())
                if depth != 0:
                    raise self._error(
                        message='Kurung kurawal f-string tidak ditutup.',
                        solution='Tambahkan } setelah ekspresi.',
                    )
                self._advance()  # consume }
                expr_str = ''.join(expr_chars).strip()
                parts.append(("expr", expr_str))
            elif self._current() == quote:
                self._advance()  # consume closing quote
                break
            elif self._current() == '\n':
                raise self._error(
                    message='F-string tidak boleh multi-baris tanpa kutip tiga.',
                    solution='Gunakan """...""" untuk f-string multi-baris.',
                )
            else:
                current_literal.append(self._advance())

        if current_literal:
            parts.append(("literal", ''.join(current_literal)))

        return Token(TokenType.TOKEN_FSTRING, parts, start_line, start_col)

    def _read_number(self) -> Token:
        '''Membaca number literal (angka dan desimal).'''
        result = []
        is_decimal = False
        start_line, start_col = self.line, self.column

        while self._current() is not None and (self._current().isdigit() or self._current() == '_'):
            if self._current() == '_':
                self._advance()
                continue
            result.append(self._advance())

        if self._current() == '.' and self._peek() is not None and self._peek().isdigit():
            is_decimal = True
            result.append(self._advance())
            while self._current() is not None and (self._current().isdigit() or self._current() == '_'):
                if self._current() == '_':
                    self._advance()
                    continue
                result.append(self._advance())

        value_str = ''.join(result)
        if is_decimal:
            return Token(
                TokenType.TOKEN_DECIMAL,
                float(value_str),
                start_line,
                start_col,
            )
        return Token(
            TokenType.TOKEN_NUMBER,
            int(value_str),
            start_line,
            start_col,
        )

    def _read_identifier(self) -> Token:
        '''Membaca identifier atau keyword.'''
        result = []
        start_line, start_col = self.line, self.column

        while self._current() is not None and (
            self._current().isalnum() or self._current() == '_'
        ):
            result.append(self._advance())

        word = ''.join(result)

        if word in KEYWORDS:
            token_type = KEYWORDS[word]
            if token_type in (TokenType.TOKEN_BENAR, TokenType.TOKEN_SALAH):
                value = word == 'benar'
                return Token(TokenType.TOKEN_BOOLEAN, value, start_line, start_col)
            if token_type == TokenType.TOKEN_KOSONG_KW:
                return Token(TokenType.TOKEN_KOSONG, None, start_line, start_col)
            return Token(token_type, word, start_line, start_col)

        return Token(TokenType.TOKEN_IDENTIFIER, word, start_line, start_col)

    def _read_operator(self) -> Token:
        '''Membaca operator dan delimiter.'''
        char = self._advance()
        start_line, start_col = self.line, self.column

        if char == '+' and self._current() == '=':
            self._advance()
            return Token(TokenType.TOKEN_PLUS_ASSIGN, '+=', start_line, start_col)
        if char == '-' and self._current() == '>':
            self._advance()
            return Token(TokenType.TOKEN_ARROW, '->', start_line, start_col)
        if char == '-' and self._current() == '=':
            self._advance()
            return Token(TokenType.TOKEN_MINUS_ASSIGN, '-=', start_line, start_col)
        if char == '*' and self._current() == '*':
            self._advance()
            if self._current() == '=':
                self._advance()
                return Token(TokenType.TOKEN_POWER_ASSIGN, '**=', start_line, start_col)
            return Token(TokenType.TOKEN_POW, '**', start_line, start_col)
        if char == '*' and self._current() == '=':
            self._advance()
            return Token(TokenType.TOKEN_MULTIPLY_ASSIGN, '*=', start_line, start_col)
        if char == '/' and self._current() == '=':
            self._advance()
            return Token(TokenType.TOKEN_DIVIDE_ASSIGN, '/=', start_line, start_col)
        if char == '%' and self._current() == '=':
            self._advance()
            return Token(TokenType.TOKEN_MODULO_ASSIGN, '%=', start_line, start_col)
        if char == '!' and self._current() == '=':
            self._advance()
            return Token(TokenType.TOKEN_NEQ, '!=', start_line, start_col)
        if char == '=' and self._current() == '>':
            self._advance()
            return Token(TokenType.TOKEN_ARROW_FAT, '=>', start_line, start_col)
        if char == '=' and self._current() == '=':
            self._advance()
            return Token(TokenType.TOKEN_EQ, '==', start_line, start_col)
        if char == '>' and self._current() == '=':
            self._advance()
            return Token(TokenType.TOKEN_GTE, '>=', start_line, start_col)
        if char == '<' and self._current() == '=':
            self._advance()
            return Token(TokenType.TOKEN_LTE, '<=', start_line, start_col)
        if char == '<' and self._current() == '<':
            self._advance()
            return Token(TokenType.TOKEN_LSHIFT, '<<', start_line, start_col)
        if char == '>' and self._current() == '>':
            self._advance()
            return Token(TokenType.TOKEN_RSHIFT, '>>', start_line, start_col)
        if char == '|' and self._current() == '|':
            self._advance()
            return Token(TokenType.TOKEN_ATAU, '||', start_line, start_col)
        if char == ':' and self._current() == '=':
            self._advance()
            return Token(TokenType.TOKEN_WALRUS, ':=', start_line, start_col)
        if char == '@':
            return Token(TokenType.TOKEN_AT, '@', start_line, start_col)

        operator_map = {
            '+': TokenType.TOKEN_PLUS,
            '-': TokenType.TOKEN_MINUS,
            '*': TokenType.TOKEN_MULTIPLY,
            '/': TokenType.TOKEN_DIVIDE,
            '%': TokenType.TOKEN_MODULO,
            '=': TokenType.TOKEN_ASSIGN,
            '>': TokenType.TOKEN_GT,
            '<': TokenType.TOKEN_LT,
            '(': TokenType.TOKEN_LPAREN,
            ')': TokenType.TOKEN_RPAREN,
            '[': TokenType.TOKEN_LBRACKET,
            ']': TokenType.TOKEN_RBRACKET,
            '{': TokenType.TOKEN_LBRACE,
            '}': TokenType.TOKEN_RBRACE,
            ',': TokenType.TOKEN_COMMA,
            '.': TokenType.TOKEN_DOT,
            ':': TokenType.TOKEN_COLON,
            '|': TokenType.TOKEN_PIPE,
            '&': TokenType.TOKEN_AMPERSAND,
            '^': TokenType.TOKEN_CARET,
            '~': TokenType.TOKEN_TILDE,
        }

        token_type = operator_map.get(char)
        if token_type is None:
            raise self._error(
                message=f'Karakter \'{char}\' tidak dikenal.',
                solution=f'Hapus karakter \'{char}\' atau ganti dengan yang benar.',
            )

        return Token(token_type, char, start_line, start_col)

    def tokenize(self) -> List[Token]:
        '''Proses utama lexing.

        Mengubah kode sumber menjadi daftar token.

        Returns:
            List[Token]: Daftar token yang dihasilkan
        '''
        self.tokens = []

        while self._current() is not None:
            char = self._current()

            # Handle indent at line start before anything else
            if self._at_line_start:
                self._handle_indent()
                if self._current() is None:
                    break
                # After handling indent, re-read char
                char = self._current()
                if char is None:
                    break

            if char in ' \t\r':
                self._skip_whitespace()
                continue

            if char == '\n':
                self._advance()
                self.tokens.append(Token(TokenType.TOKEN_NEWLINE, '\n', self.line - 1, self.column))
                self._at_line_start = True
                continue

            if char == '#' or (char == '|' and self._peek() == '#'):
                self._skip_comment()
                continue

            if char == 'f' and self._peek() in ('"', "'"):
                # f-string: f"..." or f'...'
                self._advance()  # consume 'f'
                quote = self._advance()
                self.tokens.append(self._read_fstring(quote))
                continue

            if char in ('"', "'"):
                quote = self._advance()
                string_value = self._read_string(quote)
                self.tokens.append(Token(TokenType.TOKEN_STRING, string_value, self.line, self.column))
                continue

            if char.isdigit():
                self.tokens.append(self._read_number())
                continue

            if char.isalpha() or char == '_':
                self.tokens.append(self._read_identifier())
                continue

            self.tokens.append(self._read_operator())

        # Handle DEDENT di akhir
        while len(self.indent_stack) > 1:
            self.indent_stack.pop()
            self.tokens.append(Token(TokenType.TOKEN_DEDENT, None, self.line, self.column))

        self.tokens.append(Token(TokenType.TOKEN_EOF, None, self.line, self.column))
        return self.tokens
