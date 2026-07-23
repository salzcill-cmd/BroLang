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
    TOKEN_FSTRING = auto()     # f-string interpolation (v2)
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
    TOKEN_PLUS_ASSIGN = auto()    # +=
    TOKEN_MINUS_ASSIGN = auto()   # -=
    TOKEN_MULTIPLY_ASSIGN = auto() # *=
    TOKEN_DIVIDE_ASSIGN = auto()  # /=
    TOKEN_MODULO_ASSIGN = auto()  # %=
    TOKEN_POWER_ASSIGN = auto()   # **=

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
    TOKEN_AMPERSAND = auto()   # &
    TOKEN_CARET = auto()       # ^
    TOKEN_TILDE = auto()       # ~
    TOKEN_LSHIFT = auto()      # <<
    TOKEN_RSHIFT = auto()      # >>
    TOKEN_WALRUS = auto()      # := (walrus operator)
    TOKEN_AT = auto()          # @ (decorator)
    TOKEN_QUESTION = auto()    # ? (null coalescing, optional chaining)
    TOKEN_QUESTION_DOT = auto() # ?. (optional chaining)

    # Newline and Indentation
    TOKEN_NEWLINE = auto()
    TOKEN_INDENT = auto()
    TOKEN_DEDENT = auto()

    # Control Flow Keywords
    TOKEN_BREAK = auto()       # hentikan
    TOKEN_CONTINUE = auto()    # lanjutkan

    # Built-in Functions
    TOKEN_INPUT = auto()       # input

    # Lambda & Comprehension (v2)
    TOKEN_LALU = auto()        # lalu (lambda/comprehension)
    TOKEN_ARROW_FAT = auto()   # =>

    # Pattern Matching (v2)
    TOKEN_COCOKKAN = auto()    # cocokkan (match)
    TOKEN_PATERN = auto()      # _ (wildcard in match)

    # Data Types (v2)
    TOKEN_ENUM = auto()        # enum
    TOKEN_STRUKTUR = auto()    # struktur (struct)
    TOKEN_CETAK = auto()       # cetak (screenshot/print to file - reserved)
    TOKEN_LEMPAR = auto()      # lempar (raise)
    TOKEN_AKHIRNYA = auto()    # akhirnya (finally)
    TOKEN_GLOBAL = auto()      # global
    TOKEN_NONLOKAL = auto()    # nonlokal (nonlocal)

    # v3.1 Keywords
    TOKEN_IS = auto()          # is (identity comparison)
    TOKEN_PASS = auto()        # pass (no-op)
    TOKEN_HAPUS = auto()       # hapus (del)
    TOKEN_PASTIKAN = auto()    # pastikan (assert)
    TOKEN_DENGAN = auto()      # dengan (with)

    # v4.0 Keywords — Async/Await
    TOKEN_ASYNKRON = auto()    # asinkron (async)
    TOKEN_TUNGGU = auto()      # tunggu (await)

    # v4.0 Keywords — Generators
    TOKEN_HASILKAN = auto()    # hasilkan (yield)
    TOKEN_HASILKANDARI = auto() # hasilkandari (yield from)

    # v4.0 Keywords — Decorators
    TOKEN_DEKORATOR = auto()   # @ (decorator symbol)
    TOKEN_DEKORATORKU = auto() # dekorator (decorator keyword)

    # v4.0 Keywords — Context Manager
    TOKEN_SEBAGAI = auto()     # sebagai (as)

    # v4.0 Keywords — Multiple Except
    TOKEN_KECUALI = auto()     # kecuali (except with type)

    # v4.0 Keywords — Star Import
    TOKEN_BINTANG = auto()     # * (star/wildcard import)

    # v4.0 Keywords — Match improvements
    TOKEN_PATERN_LIST = auto() # [pattern, pattern] in match
    TOKEN_PATERN_OBJEK = auto() # {key: pattern} in match

    # v4.0 Keywords — Assertions
    TOKEN_HARUSNYA = auto()    # harusnya (should/be)

    # v5.0 Keywords — Type System
    TOKEN_TIPE = auto()        # tipe (type)
    TOKEN_ANOTASI = auto()     # : (type annotation colon)
    TOKEN_UNION = auto()       # | (union type)
    TOKEN_GENERIC = auto()     # <T> (generic)

    # v5.0 Keywords — Interfaces/Traits
    TOKEN_ANTARMUKA = auto()   # antarmuka (interface)
    TOKEN_IMPLEMENTASI = auto() # implementasi (implements)
    TOKEN_SUPER = auto()       # super (superclass)

    # v5.0 Keywords — Pattern Matching Enhancement
    TOKEN_PATERN_DESTRUCT = auto() # [a, b] destructuring
    TOKEN_GUARD = auto()       # jika (guard in match)

    # v5.0 Keywords — Higher-Order Functions
    TOKEN_PETA = auto()        # peta (map)
    TOKEN_SARING = auto()      # saring (filter)
    TOKEN_KURANGI = auto()     # kurangi (reduce)

    # v5.0 Keywords — Result/Option Types
    TOKEN_BENAR_VAL = auto()   # Benar(value) - Result success
    TOKEN_SALAH_VAL = auto()   # Salah(error) - Result failure
    TOKEN_SOME = auto()        # Ada(value) - Option present
    TOKEN_NONE_VAL = auto()    # Kosong() - Option absent

    # v5.0 Keywords — Macros
    TOKEN_MAKRO = auto()       # makro (macro)
    TOKENEKSEKUSI = auto()     # eksekusi (execute)

    # v5.0 Keywords — Enhanced Async
    TOKEN_EVENT_LOOP = auto()  # event_loop
    TOKEN_TASK = auto()        # tugas (task)
    TOKEN_JANJI = auto()       # janji (promise)

    # v5.0 Keywords — Module System
    TOKEN_RUANG = auto()       # ruang (namespace)
    TOKEN_PAKAI = auto()       # pakai (use)

    # v5.0 Keywords — Access Modifiers
    TOKEN_PUBLIK = auto()      # publik (public)
    TOKEN_PRIVAT = auto()      # privat (private)
    TOKEN_TERLINDUNGI = auto() # terlindungi (protected)

    # v5.0 Keywords — Abstract Classes
    TOKEN_ABSTRAK = auto()     # abstrak (abstract)
    TOKEN_KONKRET = auto()     # konkret (concrete)

    # v5.0 Keywords — Enums with Values
    TOKEN_ENUMBERHASIL = auto() # enumberhasil (enum with values)

    # v5.0 Keywords — Exception Hierarchy
    TOKEN_WARISAN = auto()     # warisan (inherit)

    # v5.0 Keywords — Static/Class Methods
    TOKEN_STATIS = auto()      # statis (static method)
    TOKEN_KELASMETHOD = auto() # kelas_method (class method)

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
    # v2 keywords
    "lalu": TokenType.TOKEN_LALU,
    "cocokkan": TokenType.TOKEN_COCOKKAN,
    "enum": TokenType.TOKEN_ENUM,
    "struktur": TokenType.TOKEN_STRUKTUR,
    "cetak": TokenType.TOKEN_CETAK,
    "lempar": TokenType.TOKEN_LEMPAR,
    "akhirnya": TokenType.TOKEN_AKHIRNYA,
    "global": TokenType.TOKEN_GLOBAL,
    "nonlokal": TokenType.TOKEN_NONLOKAL,
    # v3.1 keywords
    "is": TokenType.TOKEN_IS,
    "pass": TokenType.TOKEN_PASS,
    "hapus": TokenType.TOKEN_HAPUS,
    "pastikan": TokenType.TOKEN_PASTIKAN,
    "dengan": TokenType.TOKEN_DENGAN,
    # v4.0 keywords
    "asinkron": TokenType.TOKEN_ASYNKRON,
    "tunggu": TokenType.TOKEN_TUNGGU,
    "hasilkan": TokenType.TOKEN_HASILKAN,
    "hasilkandari": TokenType.TOKEN_HASILKANDARI,
    "dekorator": TokenType.TOKEN_DEKORATORKU,
    "sebagai": TokenType.TOKEN_SEBAGAI,
    "kecuali": TokenType.TOKEN_KECUALI,
    "harusnya": TokenType.TOKEN_HARUSNYA,
    # v5.0 keywords — Type System
    "tipe": TokenType.TOKEN_TIPE,
    "antarmuka": TokenType.TOKEN_ANTARMUKA,
    "implementasi": TokenType.TOKEN_IMPLEMENTASI,
    "super": TokenType.TOKEN_SUPER,
    # v5.0 keywords — Higher-Order Functions
    "peta": TokenType.TOKEN_PETA,
    "saring": TokenType.TOKEN_SARING,
    "kurangi": TokenType.TOKEN_KURANGI,
    # v5.0 keywords — Result/Option
    "Benar": TokenType.TOKEN_BENAR_VAL,
    "Salah": TokenType.TOKEN_SALAH_VAL,
    "Ada": TokenType.TOKEN_SOME,
    # v5.0 keywords — Macros
    "makro": TokenType.TOKEN_MAKRO,
    "eksekusi": TokenType.TOKENEKSEKUSI,
    # v5.0 keywords — Module System
    "ruang": TokenType.TOKEN_RUANG,
    "pakai": TokenType.TOKEN_PAKAI,
    # v5.0 keywords — Access Modifiers
    "publik": TokenType.TOKEN_PUBLIK,
    "privat": TokenType.TOKEN_PRIVAT,
    "terlindungi": TokenType.TOKEN_TERLINDUNGI,
    # v5.0 keywords — Abstract Classes
    "abstrak": TokenType.TOKEN_ABSTRAK,
    "konkret": TokenType.TOKEN_KONKRET,
    # v5.0 keywords — Async
    "tugas": TokenType.TOKEN_TASK,
    "janji": TokenType.TOKEN_JANJI,
    # v5.0 keywords — Inheritance
    "warisan": TokenType.TOKEN_WARISAN,
    # v5.0 keywords — Static/Class Methods
    "statis": TokenType.TOKEN_STATIS,
    "kelas_method": TokenType.TOKEN_KELASMETHOD,
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
