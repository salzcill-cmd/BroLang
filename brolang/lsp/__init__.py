"""
LSP (Language Server Protocol) untuk BroLang
=============================================

Language Server Protocol implementation for BroLang.
Memungkinkan editor seperti VS Code untuk memberikan:

- Auto completion
- Go to definition
- Hover documentation
- Error diagnostics
- Syntax highlighting

Kompatibel dengan VS Code, Neovim, Emacs, dan editor
lain yang mendukung LSP.

Penggunaan:
    bro-lsp
"""

from brolang.lsp.server import start_lsp, BroLangLSP
