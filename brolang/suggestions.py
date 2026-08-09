"""
Saran Ramah Pemula (v6.1)
=========================

Membantu pelajar Indonesia yang baru belajar coding — sering kali mereka
mengetik keyword bahasa Inggris (dari Python/JavaScript) di BroLang.

Modul ini menyediakan pemetaan keyword Inggris → BroLang supaya pesan error
bisa memberi saran: "mungkin maksudmu 'tulis'?".

Dipakai oleh lexer, parser, analyzer, dan interpreter.
"""

# Keyword bahasa Inggris yang umum dipakai pemula → padanan BroLang
BAHASA_INGGRIS: dict = {
    # Output
    "print": "tulis",
    # Variabel
    "let": "buat",
    "var": "buat",
    "const": "konstanta",
    "val": "buat",
    # Percabangan
    "if": "jika",
    "else": "lainnya",
    "elif": "lainnya jika",
    "then": "maka",
    "end": "selesai",
    # Perulangan
    "for": "untuk",
    "while": "selama",
    "do": "ulangi",
    "do-while": "ulangi ... sampai",
    "until": "sampai",
    "in": "dalam",
    "range": "dari ... sampai",
    "break": "hentikan",
    "continue": "lanjutkan",
    # Fungsi
    "def": "fungsi",
    "function": "fungsi",
    "fn": "fungsi",
    "return": "kembali",
    "lambda": "lalu",
    # Kelas & modul
    "class": "kelas",
    "import": "impor",
    "from": "dari",
    "as": "sebagai",
    # Error handling
    "try": "coba",
    "except": "kecuali",
    "finally": "akhirnya",
    "raise": "lempar",
    # Boolean & null
    "true": "benar",
    "false": "salah",
    "True": "benar",
    "False": "salah",
    "null": "kosong",
    "None": "kosong",
    "nil": "kosong",
    # Logika
    "and": "dan",
    "or": "atau",
    "not": "bukan",
    # Lainnya
    "match": "cocokkan",
    "struct": "struktur",
    "yield": "hasilkan",
    "pass": "pass",
    "delete": "hapus",
    "assert": "pastikan",
}


def saran_keyword(kata: str) -> str:
    """Saran padanan BroLang untuk kata yang mirip keyword Inggris.

    Args:
        kata: Kata yang ditulis user (nilai token, mis. 'print').

    Returns:
        String saran siap-tempel (mis. " Mungkin maksudmu 'tulis'?"),
        atau string kosong bila tidak ada padanan.
    """
    if not kata or not isinstance(kata, str):
        return ""
    padanan = BAHASA_INGGRIS.get(kata)
    if padanan is None:
        return ""
    if kata == padanan:
        return ""
    return f" Mungkin maksudmu '{padanan}'?"


def cek_kesalahan_umum(teks: str) -> str:
    """Saran untuk kesalahan sintaks yang sering dilakukan pemula.

    Args:
        teks: Cuplikan kode di sekitar error.

    Returns:
        Saran ramah, atau string kosong.
    """
    if not teks:
        return ""
    if ";" in teks:
        return " BroLang tidak memakai titik koma ';' di akhir baris — hapus saja."
    return ""
