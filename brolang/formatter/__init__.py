"""
Formatter BroLang (brofmt)
==========================

Formatter otomatis untuk kode BroLang.
Memastikan kode mengikuti standar formatting yang konsisten.

Penggunaan:
    bro fmt file.bro
    bro fmt file.bro --check

Fitur:
- Indentasi konsisten
- Spasi di sekitar operator
- Baris kosong antar fungsi/kelas
- Penempatan kurung yang rapi
"""

from brolang.formatter.formatter import format_code, format_file, check_format
