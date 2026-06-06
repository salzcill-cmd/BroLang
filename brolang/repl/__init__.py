"""
REPL (Read-Eval-Print Loop) untuk BroLang
===========================================

REPL interaktif untuk eksperimen dan pembelajaran.

Fitur:
- Syntax highlighting
- History (riwayat perintah)
- Auto-completion
- Multi-line mode
- Error reporting yang jelas

Contoh:
    from brolang.repl import start_repl
    start_repl()
"""

from brolang.repl.repl import start_repl, BroLangREPL
