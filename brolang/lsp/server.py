"""
LSP Server Implementation untuk BroLang
=========================================

Implementasi Language Server Protocol yang memungkinkan
editor untuk memberikan fitur bahasa secara real-time.

Fitur:
- Diagnostics (error checking)
- Auto completion
- Hover information
- Go to definition
"""

import sys
import json
from typing import Any, Dict, List, Optional
from brolang.lexer import Lexer
from brolang.token_types import TokenType, KEYWORDS
from brolang.exceptions import BroLangError


class BroLangLSP:
    """Language Server Protocol implementation untuk BroLang.

    Menggunakan stdin/stdout untuk komunikasi dengan editor.
    """

    def __init__(self):
        self.documents: Dict[str, str] = {}
        self.running = True

    def start(self) -> None:
        """Memulai LSP server."""
        while self.running:
            try:
                message = self._read_message()
                if message is None:
                    break
                self._handle_message(message)
            except (EOFError, ConnectionError):
                break
            except Exception as e:
                self._send_error(e)

    def _read_message(self) -> Optional[Dict[str, Any]]:
        """Membaca message dari stdin (LSP protocol)."""
        try:
            content_length = 0
            line = sys.stdin.readline()
            if not line:
                return None

            if line.startswith("Content-Length: "):
                content_length = int(line.strip().split(": ")[1])
                sys.stdin.readline()  # Read empty line
                content = sys.stdin.read(content_length)
                return json.loads(content)

            return None
        except Exception:
            return None

    def _send_message(self, message: Dict[str, Any]) -> None:
        """Mengirim message ke stdout (LSP protocol)."""
        content = json.dumps(message, ensure_ascii=False)
        response = f"Content-Length: {len(content)}\r\n\r\n{content}"
        sys.stdout.write(response)
        sys.stdout.flush()

    def _send_error(self, error: Exception) -> None:
        """Mengirim error response."""
        self._send_message({
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,
                "message": str(error),
            },
        })

    def _handle_message(self, message: Dict[str, Any]) -> None:
        """Menangani berbagai tipe LSP message."""
        method = message.get("method", "")
        msg_id = message.get("id")
        params = message.get("params", {})

        handlers = {
            "initialize": self._handle_initialize,
            "textDocument/didOpen": self._handle_did_open,
            "textDocument/didChange": self._handle_did_change,
            "textDocument/completion": self._handle_completion,
            "textDocument/hover": self._handle_hover,
            "textDocument/definition": self._handle_definition,
            "textDocument/diagnostic": self._handle_diagnostic,
            "shutdown": self._handle_shutdown,
        }

        handler = handlers.get(method)
        if handler:
            result = handler(params)
            if msg_id:
                self._send_message({
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": result,
                })
        elif msg_id:
            self._send_message({
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": None,
            })

    def _handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Menangani initialize request."""
        return {
            "capabilities": {
                "textDocumentSync": {
                    "openClose": True,
                    "change": 1,  # Full document sync
                },
                "completionProvider": {
                    "triggerCharacters": [".", "("],
                },
                "hoverProvider": True,
                "definitionProvider": True,
                "diagnosticProvider": {
                    "interFileDependencies": False,
                    "workspaceDiagnostics": False,
                },
            },
            "serverInfo": {
                "name": "BroLang LSP",
                "version": "1.0.0",
            },
        }

    def _handle_did_open(self, params: Dict[str, Any]) -> None:
        """Menangani dokumen yang dibuka."""
        uri = params["textDocument"]["uri"]
        text = params["textDocument"]["text"]
        self.documents[uri] = text
        self._publish_diagnostics(uri)

    def _handle_did_change(self, params: Dict[str, Any]) -> None:
        """Menangani perubahan dokumen."""
        uri = params["textDocument"]["uri"]
        content_changes = params.get("contentChanges", [])
        if content_changes:
            self.documents[uri] = content_changes[-1].get("text", "")
            self._publish_diagnostics(uri)

    def _publish_diagnostics(self, uri: str) -> None:
        """Menerbitkan diagnostics untuk dokumen."""
        text = self.documents.get(uri, "")
        diagnostics = self._get_diagnostics(text)

        self._send_message({
            "jsonrpc": "2.0",
            "method": "textDocument/publishDiagnostics",
            "params": {
                "uri": uri,
                "diagnostics": diagnostics,
            },
        })

    def _get_diagnostics(self, text: str) -> List[Dict[str, Any]]:
        """Mendapatkan daftar diagnostic error."""
        diagnostics = []

        try:
            lexer = Lexer(text)
            tokens = lexer.tokenize()
        except BroLangError as e:
            diagnostics.append({
                "range": {
                    "start": {"line": max(0, e.detail.line - 1), "character": max(0, e.detail.column - 1)},
                    "end": {"line": max(0, e.detail.line - 1), "character": max(0, e.detail.column)},
                },
                "severity": 1,  # Error
                "message": e.detail.message,
                "source": "brolang",
            })

        return diagnostics

    # ============ Symbol table (dari dokumen) ============

    _DECL_KEYWORDS = {
        "buat": "Variable",
        "konstanta": "Variable",  # v6.5
        "fungsi": "Function",
        "kelas": "Class",
        "konstanta": "Constant",
        "struktur": "Struct",
        "enum": "Enum",
        "ruang": "Namespace",
        "impor": "Module",
        "muat": "Module",
    }

    _STDLIB_NAMES = [
        "matematika", "teks", "waktu", "file", "json", "jaringan", "acak",
        "vektor", "grafis", "audio", "input", "game", "pencocok", "antrian",
        "tumpukan", "serialisasi", "dasar", "sprite", "animasi", "tilemap",
        "kamera", "partikel", "ui", "fisika", "debugger", "profil", "tes",
        "visualisasi", "sejajar",
    ]

    def _build_symbols(self, text: str) -> Dict[str, Dict[str, Any]]:
        """Kumpulkan simbol (variabel/fungsi/kelas/modul) + posisi definisinya."""
        symbols: Dict[str, Dict[str, Any]] = {}
        try:
            tokens = Lexer(text).tokenize()
        except Exception:
            return symbols
        for i, tok in enumerate(tokens):
            if tok.value in self._DECL_KEYWORDS and i + 1 < len(tokens):
                nxt = tokens[i + 1]
                # Hanya identifier asli (bukan string literal / operator / keyword)
                if nxt.type == TokenType.TOKEN_IDENTIFIER:
                    symbols[nxt.value] = {
                        "kind": self._DECL_KEYWORDS[tok.value],
                        "line": max(0, (nxt.line or 1) - 1),
                        "character": max(0, (nxt.column or 1) - 1),
                    }
        return symbols

    def _kind_for(self, kind: str) -> int:
        """Nama kind -> LSP CompletionItemKind."""
        return {
            "Variable": 6, "Function": 3, "Class": 7, "Constant": 21,
            "Struct": 22, "Enum": 13, "Namespace": 9, "Module": 9,
        }.get(kind, 6)

    def _builtin_names(self) -> List[str]:
        try:
            from brolang.interpreter.builtins import BUILTINS
            return sorted(BUILTINS.keys())
        except Exception:
            return []

    def _handle_completion(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Menangani auto-completion (keyword, builtin, simbol, member modul)."""
        uri = params["textDocument"]["uri"]
        position = params.get("position", {})
        text = self.documents.get(uri, "")
        lines = text.split("\n")
        line = lines[position.get("line", 0)] if position.get("line", 0) < len(lines) else ""
        char = position.get("character", 0)
        prefix = line[:char]

        # Member completion: sesuatu.member
        if "." in prefix:
            obj_name = prefix.rsplit(".", 1)[0].strip().split()[-1] or ""
            member_prefix = prefix.rsplit(".", 1)[1]
            return {"isIncomplete": False,
                    "items": self._member_completions(obj_name, member_prefix)}

        token = self._get_word_at(line, char) or ""
        items = []
        seen = set()

        def _add(label, kind, detail):
            if label in seen or (token and not label.startswith(token)):
                return
            seen.add(label)
            items.append({
                "label": label, "kind": kind,
                "detail": detail, "insertText": label,
            })

        for kw in sorted(KEYWORDS.keys()):
            _add(kw, 14, "Keyword BroLang")
        for name in self._builtin_names():
            _add(name, 3, "Builtin BroLang")
        for mod in self._STDLIB_NAMES:
            _add(mod, 9, "Modul stdlib BroLang")
        for name, info in self._build_symbols(text).items():
            _add(name, self._kind_for(info["kind"]), f"{info['kind']} (dokumen ini)")

        return {"isIncomplete": False, "items": items}

    def _member_completions(self, obj_name: str, member_prefix: str) -> List[Dict[str, Any]]:
        """Completion untuk member objek/modul (setelah tanda titik)."""
        items = []
        members = set()

        # Modul stdlib: tampilkan fungsi asli dari modulnya
        if obj_name in self._STDLIB_NAMES:
            try:
                from brolang.stdlib import get_stdlib_module
                mod = get_stdlib_module(obj_name)
                members.update(n for n in dir(mod) if not n.startswith("_"))
            except Exception:
                pass
        else:
            # Member umum untuk objek game/UI
            members.update({
                "gambar", "update", "set_teks", "set_nilai", "tambah", "kurang",
                "set_posisi", "get", "set", "aktif", "terlihat", "x", "y",
            })

        for name in sorted(members):
            if member_prefix and not name.startswith(member_prefix):
                continue
            items.append({
                "label": name,
                "kind": 4,  # Method/Property
                "detail": f"Member dari {obj_name}",
                "insertText": name,
            })
        return items

    def _handle_hover(self, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Menangani hover request (keyword/simbol/builtin)."""
        uri = params["textDocument"]["uri"]
        position = params["position"]
        text = self.documents.get(uri, "")
        lines = text.split("\n")
        line = lines[position["line"]] if position["line"] < len(lines) else ""
        word = self._get_word_at(line, position["character"])
        if not word:
            return None

        if word in KEYWORDS:
            return {"contents": {"kind": "markdown",
                                 "value": f"**{word}** — Keyword BroLang"}}

        symbols = self._build_symbols(text)
        if word in symbols:
            info = symbols[word]
            return {"contents": {"kind": "markdown",
                                 "value": f"**{word}** — {info['kind']} BroLang "
                                          f"(deklarasi baris {info['line'] + 1})"}}

        if word in self._STDLIB_NAMES:
            return {"contents": {"kind": "markdown",
                                 "value": f"**{word}** — Modul stdlib BroLang"}}

        if word in self._builtin_names():
            return {"contents": {"kind": "markdown",
                                 "value": f"**{word}** — Builtin BroLang"}}

        return {"contents": {"kind": "markdown",
                             "value": f"**{word}** — Identifier"}}

    def _handle_definition(self, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Menangani go-to-definition (pindah ke deklarasi simbol)."""
        uri = params["textDocument"]["uri"]
        position = params["position"]
        text = self.documents.get(uri, "")
        lines = text.split("\n")
        line = lines[position["line"]] if position["line"] < len(lines) else ""
        word = self._get_word_at(line, position["character"])
        if not word:
            return None

        symbols = self._build_symbols(text)
        if word in symbols:
            info = symbols[word]
            start = {"line": info["line"], "character": info["character"]}
            return {"uri": uri, "range": {
                "start": start,
                "end": {"line": info["line"],
                        "character": info["character"] + len(word)},
            }}
        return None

    def _handle_diagnostic(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Menangani diagnostic request."""
        uri = params["textDocument"]["uri"]
        text = self.documents.get(uri, "")
        diagnostics = self._get_diagnostics(text)
        return {"items": diagnostics}

    def _handle_shutdown(self, params: Dict[str, Any]) -> None:
        """Menangani shutdown."""
        self.running = False

    def _get_word_at(self, line: str, character: int) -> Optional[str]:
        """Mendapatkan kata pada posisi tertentu."""
        if character >= len(line):
            return None

        start = character
        while start > 0 and (line[start - 1].isalnum() or line[start - 1] == "_"):
            start -= 1

        end = character
        while end < len(line) and (line[end].isalnum() or line[end] == "_"):
            end += 1

        if start < end:
            return line[start:end]
        return None


def start_lsp() -> None:
    """Memulai LSP server."""
    server = BroLangLSP()
    server.start()


if __name__ == "__main__":
    start_lsp()
