"""
CLI (Command Line Interface) untuk BroLang
===========================================

Antarmuka baris perintah untuk BroLang.

Perintah:
    bro run     <file>     : Menjalankan file BroLang
    bro build   <file>     : Mengompilasi file BroLang ke Python
    bro repl               : Memulai REPL interaktif
    bro fmt     <file>     : Memformat kode BroLang
    bro lint    <file>     : Menganalisis kode statis
    bro version            : Menampilkan versi

Penggunaan:
    bro run app.bro
    bro repl
    bro build app.bro -o output.py
"""

from brolang.cli.main import main
