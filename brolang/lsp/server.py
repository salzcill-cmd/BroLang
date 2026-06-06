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

    def _handle_completion(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Menangani auto-completion."""
        # Complete keywords and built-in functions
        completions = []

        for keyword in sorted(KEYWORDS.keys()):
            completions.append({
                "label": keyword,
                "kind": 14,  # Keyword
                "detail": "Keyword BroLang",
                "insertText": keyword,
            })

        builtins = [
            ("input", "Function", "input(prompt) -> str"),
            ("len", "Function", "len(obj) -> int"),
            ("angka", "Function", "angka(val) -> int"),
            ("desimal", "Function", "desimal(val) -> float"),
            ("teks", "Function", "teks(val) -> str"),
            ("range", "Function", "range(start, stop, step)"),
        ]

        for name, kind, detail in builtins:
            completions.append({
                "label": name,
                "kind": 3,  # Function
                "detail": detail,
                "insertText": name,
            })

        return {"isIncomplete": False, "items": completions}

    def _handle_hover(self, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Menangani hover request."""
        uri = params["textDocument"]["uri"]
        position = params["position"]
        text = self.documents.get(uri, "")
        lines = text.split("\n")

        if position["line"] < len(lines):
            line = lines[position["line"]]
            word = self._get_word_at(line, position["character"])
            if word:
                if word in KEYWORDS:
                    return {"contents": f"**{word}** - Keyword BroLang"}
                return {"contents": f"**{word}** - Identifier"}

        return None

    def _handle_definition(self, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Menangani go-to-definition."""
        # Basic implementation - would need symbol table for proper support
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
