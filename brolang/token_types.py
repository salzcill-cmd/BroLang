"""
Token Types untuk BroLang
=========================

Mendefinisikan semua jenis token yang digunakan dalam bahasa BroLang.
Token mewakili unit terkecil dari kode sumber setelah proses lexing.
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import Any, Optional


class TokenType(Enum):
    """Semua jenis token yang dikenal oleh BroLang."""

    # Literals
    TOKEN_NUMBER = auto()
    TOKEN_DECIMAL = auto()
    TOKEN_STRING = auto()
    TOKEN_BOOLEAN = auto()
    TOKEN_KOSONG = auto()

    # Identifiers & Keywords
    TOKEN_IDENTIFIER = auto()

    # Keywords Bahasa Indonesia
    TOKEN_BUAT = auto()        # buat (var/let)
    TOKEN_TULIS = auto()       # tulis (print)
    TOKEN_JIKA = auto()        # jika (if)
    TOKEN_MAKA = auto()        # maka (then)
    TOKEN_LAINNYA = auto()     # lainnya (else)
    TOKEN_SELESAI = auto()     # selesai (end)
    TOKEN_UNTUK = auto()       # untuk (for)
    TOKEN_DALAM = auto()       # dalam (in)
    TOKEN_LAKUKAN = auto()     # lakukan (do)
    TOKEN_SELAMA = auto()      # selama (while)
    TOKEN_FUNGSI = auto()      # fungsi (function/def)
    TOKEN_KEMBALI = auto()     # kembali (return)
    TOKEN_KELAS = auto()       # kelas (class)
    TOKEN_IMPOR = auto()       # impor (import)
    TOKEN_DARI = auto()        # dari (from)
    TOKEN_COBA = auto()        # coba (try)
    TOKEN_TANGKAP = auto()     # tangkap (catch/except)
    TOKEN_DAN = auto()         # dan (and)
    TOKEN_ATAU = auto()        # atau (or)
    TOKEN_BUKAN = auto()       # bukan (not)
    TOKEN_BENAR = auto()       # benar (true)
    TOKEN_SALAH = auto()       # salah (false)
    TOKEN_KOSONG_KW = auto()   # kosong (null/none)

    # Operators
    TOKEN_PLUS = auto()        # +
    TOKEN_MINUS = auto()       # -
    TOKEN_MULTIPLY = auto()    # *
    TOKEN_DIVIDE = auto()      # /
    TOKEN_MODULO = auto()      # %
    TOKEN_POW = auto()         # **

    # Comparison
    TOKEN_EQ = auto()          # ==
    TOKEN_NEQ = auto()         # !=
    TOKEN_GT = auto()          # >
    TOKEN_LT = auto()          # <
    TOKEN_GTE = auto()         # >=
    TOKEN_LTE = auto()         # <=

    # Assignment
    TOKEN_ASSIGN = auto()      # =

    # Delimiters
    TOKEN_LPAREN = auto()      # (
    TOKEN_RPAREN = auto()      # )
    TOKEN_LBRACKET = auto()    # [
    TOKEN_RBRACKET = auto()    # ]
    TOKEN_LBRACE = auto()      # {
    TOKEN_RBRACE = auto()      # }
    TOKEN_COMMA = auto()       # ,
    TOKEN_DOT = auto()         # .
    TOKEN_COLON = auto()       # :
    TOKEN_ARROW = auto()       # ->
    TOKEN_PIPE = auto()        # |

    # Newline and Indentation
    TOKEN_NEWLINE = auto()
    TOKEN_INDENT = auto()
    TOKEN_DEDENT = auto()

    # Control Flow Keywords
    TOKEN_BREAK = auto()       # hentikan
    TOKEN_CONTINUE = auto()    # lanjutkan

    # Built-in Functions
    TOKEN_INPUT = auto()       # input

    # Special
    TOKEN_EOF = auto()


# Mapping dari keyword Bahasa Indonesia ke TokenType
KEYWORDS: dict[str, TokenType] = {
    "buat": TokenType.TOKEN_BUAT,
    "tulis": TokenType.TOKEN_TULIS,
    "jika": TokenType.TOKEN_JIKA,
    "hentikan": TokenType.TOKEN_BREAK,
    "lanjutkan": TokenType.TOKEN_CONTINUE,
    "maka": TokenType.TOKEN_MAKA,
    "lainnya": TokenType.TOKEN_LAINNYA,
    "selesai": TokenType.TOKEN_SELESAI,
    "untuk": TokenType.TOKEN_UNTUK,
    "dalam": TokenType.TOKEN_DALAM,
    "lakukan": TokenType.TOKEN_LAKUKAN,
    "selama": TokenType.TOKEN_SELAMA,
    "fungsi": TokenType.TOKEN_FUNGSI,
    "kembali": TokenType.TOKEN_KEMBALI,
    "kelas": TokenType.TOKEN_KELAS,
    "impor": TokenType.TOKEN_IMPOR,
    "dari": TokenType.TOKEN_DARI,
    "coba": TokenType.TOKEN_COBA,
    "tangkap": TokenType.TOKEN_TANGKAP,
    "dan": TokenType.TOKEN_DAN,
    "atau": TokenType.TOKEN_ATAU,
    "bukan": TokenType.TOKEN_BUKAN,
    "benar": TokenType.TOKEN_BENAR,
    "salah": TokenType.TOKEN_SALAH,
    "kosong": TokenType.TOKEN_KOSONG_KW,
    "input": TokenType.TOKEN_INPUT,
}


@dataclass
class Token:
    """Mewakili sebuah token dalam bahasa BroLang.

    Attributes:
        type: Jenis token
        value: Nilai token (misal: string literal, angka)
        line: Baris dalam kode sumber
        column: Kolom dalam kode sumber
    """

    type: TokenType
    value: Any = None
    line: int = 0
    column: int = 0

    def __repr__(self) -> str:
        return f"Token({self.type.name}, {self.value!r}, Ln {self.line}, Col {self.column})"


# Precedence untuk operator (semakin besar semakin tinggi)
PRECEDENCE: dict[TokenType, int] = {
    TokenType.TOKEN_ATAU: 1,
    TokenType.TOKEN_DAN: 2,
    TokenType.TOKEN_EQ: 3,
    TokenType.TOKEN_NEQ: 3,
    TokenType.TOKEN_GT: 4,
    TokenType.TOKEN_LT: 4,
    TokenType.TOKEN_GTE: 4,
    TokenType.TOKEN_LTE: 4,
    TokenType.TOKEN_PLUS: 5,
    TokenType.TOKEN_MINUS: 5,
    TokenType.TOKEN_MULTIPLY: 6,
    TokenType.TOKEN_DIVIDE: 6,
    TokenType.TOKEN_MODULO: 6,
    TokenType.TOKEN_POW: 7,
}
