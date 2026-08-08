"""
Modul Web Server BroLang
========================

Framework web untuk membuat API backend / server HTTP di BroLang.
Berbasis stdlib Python (http.server) — tanpa dependency eksternal.

Fitur:
- Routing metode + jalur (GET/POST/PUT/DELETE/PATCH/OPTIONS)
- Parameter jalur dinamis: `/pengguna/{id}`
- Query string otomatis di-parse: `/cari?q=budi`
- Body JSON otomatis di-parse untuk POST/PUT
- Response: teks, JSON, HTML, status, file statis
- CORS sederhana (opsional)

Contoh:
    impor web_server

    fungsi halaman_utama(req)
        kembali req.kirim_json({"pesan": "Halo Dunia!"})
    selesai

    fungsi detail_pengguna(req)
        buat id = req.parameter["id"]
        kembali req.kirim_json({"id": id, "nama": "Budi"})
    selesai

    buat app = web_server.Buat()
    app.rute("GET", "/", halaman_utama)
    app.rute("GET", "/pengguna/{id}", detail_pengguna)
    app.jalankan(8000)          # server jalan di http://127.0.0.1:8000
"""

import json as _json
import os
import urllib.parse as _urlparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from types import SimpleNamespace


class _Handler(BaseHTTPRequestHandler):
    """Handler HTTP internal yang meneruskan request ke aplikasi BroLang."""

    app = None

    def log_message(self, *args):
        pass  # Redam log default agar output bersih

    # ----- Utility -----

    def _kirim(self, status: int, body: bytes, tipe: str, header=None):
        self.send_response(status)
        self.send_header("Content-Type", tipe)
        self.send_header("Content-Length", str(len(body)))
        for k, v in (header or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    # ----- Request handling -----

    def _proses(self, metode: str):
        app = self.app
        jalur = _urlparse.urlparse(self.path).path
        query = _urlparse.parse_qs(_urlparse.urlparse(self.path).query)
        # Query value pertama untuk tiap key (lebih natural: q=budi -> "budi")
        query_flat = {k: v[0] if len(v) == 1 else v for k, v in query.items()}

        # Baca body
        body = b""
        try:
            panjang = int(self.headers.get("Content-Length", 0) or 0)
            if panjang > 0:
                body = self.rfile.read(panjang)
        except (ValueError, OSError):
            body = b""

        # Parse JSON body kalau ada
        json_body = None
        if body:
            try:
                json_body = _json.loads(body.decode("utf-8"))
            except (ValueError, UnicodeDecodeError):
                json_body = None

        # Cari route yang cocok
        for rute in app.routes:
            if rute.metode != metode:
                continue
            params = app._cocok_jalur(rute.jalur, jalur)
            if params is None:
                continue

            req = SimpleNamespace(
                metode=metode,
                jalur=jalur,
                jalur_lengkap=self.path,
                query=query_flat,
                header=dict(self.headers),
                body=body.decode("utf-8", errors="replace") if body else "",
                json=json_body,
                parameter=params,
                # Helper response
                kirim_teks=lambda t, s=200: self._kirim(
                    s, str(t).encode("utf-8"), "text/plain; charset=utf-8"
                ),
                kirim_json=lambda d, s=200: self._kirim(
                    s,
                    _json.dumps(d, ensure_ascii=False).encode("utf-8"),
                    "application/json; charset=utf-8",
                ),
                kirim_html=lambda h, s=200: self._kirim(
                    s, str(h).encode("utf-8"), "text/html; charset=utf-8"
                ),
                kirim_status=lambda s=204: self._kirim(s, b"", "text/plain; charset=utf-8"),
                kirim_file=lambda p, s=200: app._kirim_file(self, p, s),
            )

            try:
                hasil = rute.handler(req)
                # Handler boleh mengembalikan dict -> auto-JSON (helper modern)
                if isinstance(hasil, dict):
                    req.kirim_json(hasil)
                    return
                if isinstance(hasil, str):
                    req.kirim_teks(hasil)
                    return
                # SimpleNamespace hasil dari helper: sudah terkirim
            except (RuntimeError, ValueError, TypeError, OSError) as e:
                app._handler_error(self, e)
            return

        # Route tidak ditemukan
        body_err = _json.dumps(
            {"error": "Tidak ditemukan", "jalur": jalur}, ensure_ascii=False
        ).encode("utf-8")
        self._kirim(404, body_err, "application/json; charset=utf-8")

    def do_GET(self):
        self._proses("GET")

    def do_POST(self):
        self._proses("POST")

    def do_PUT(self):
        self._proses("PUT")

    def do_DELETE(self):
        self._proses("DELETE")

    def do_PATCH(self):
        self._proses("PATCH")

    def do_OPTIONS(self):
        app = self.app
        if app.cors:
            self.send_response(204)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header(
                "Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, PATCH, OPTIONS"
            )
            self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
            self.send_header("Content-Length", "0")
            self.end_headers()
        else:
            self.send_response(405)
            self.end_headers()


class _Rute:
    """Satu rute terdaftar."""

    __slots__ = ("handler", "jalur", "metode")

    def __init__(self, metode, jalur, handler):
        self.metode = metode.upper()
        self.jalur = jalur.rstrip("/") or "/"
        self.handler = handler


class WebServer:
    """Server web BroLang.

    Contoh:
        buat app = web_server.Buat()
        app.rute("GET", "/", handler)
        app.jalankan(8000)
    """

    def __init__(self):
        self.routes = []
        self.cors = False
        self.serving_dir = None  # batasi kirim_file ke folder ini (opsional)
        self._server = None

    def rute(self, metode: str, jalur: str, handler) -> "_Rute":
        """Daftarkan handler untuk metode + jalur.

        Args:
            metode: GET/POST/PUT/DELETE/PATCH
            jalur: path seperti "/" atau "/pengguna/{id}"
            handler: fungsi BroLang yang menerima objek `req`
        """
        r = _Rute(metode, jalur, handler)
        self.routes.append(r)
        return r

    def get(self, jalur: str, handler) -> "_Rute":
        """Shorthand untuk rute GET."""
        return self.rute("GET", jalur, handler)

    def post(self, jalur: str, handler) -> "_Rute":
        """Shorthand untuk rute POST."""
        return self.rute("POST", jalur, handler)

    def put(self, jalur: str, handler) -> "_Rute":
        """Shorthand untuk rute PUT."""
        return self.rute("PUT", jalur, handler)

    def hapus(self, jalur: str, handler) -> "_Rute":
        """Shorthand untuk rute DELETE."""
        return self.rute("DELETE", jalur, handler)

    def atur_cors(self, aktif: bool = True) -> "WebServer":
        """Aktifkan CORS (berguna untuk frontend terpisah)."""
        self.cors = aktif
        return self

    def _cocok_jalur(self, pola: str, jalur: str):
        """Cocokkan jalur request dengan pola rute.

        Pola `/pengguna/{id}` cocok dengan `/pengguna/5`
        dan menghasilkan {"id": "5"}. Return None bila tidak cocok.
        """
        pola = pola.rstrip("/") or "/"
        jalur = jalur.rstrip("/") or "/"
        pp = pola.split("/")
        jp = jalur.split("/")
        if len(pp) != len(jp):
            return None
        params = {}
        for a, b in zip(pp, jp):
            if a.startswith("{") and a.endswith("}"):
                params[a[1:-1]] = b
            elif a != b:
                return None
        return params

    def _kirim_file(self, handler, path: str, status: int = 200):
        """Kirim file statis. `path` relatif ke folder saat ini.

        Keamanan: path dengan `..` ditolak (anti path traversal), dan bila
        `serving_dir` diset, path dipaksa berada di dalam folder tersebut.
        """
        # Anti path traversal: tolak `..` agar tidak bisa keluar dari root
        if ".." in path.split("/") or ".." in path.split(os.sep):
            handler._kirim(403, b"Akses ditolak", "text/plain; charset=utf-8")
            return
        if self.serving_dir:
            path = os.path.join(self.serving_dir, path.lstrip("/"))
        if not os.path.isfile(path):
            handler._kirim(404, b"File tidak ditemukan", "text/plain; charset=utf-8")
            return
        try:
            with open(path, "rb") as f:
                data = f.read()
        except OSError:
            handler._kirim(500, b"Gagal membaca file", "text/plain; charset=utf-8")
            return
        tipe = "application/octet-stream"
        if path.endswith((".html", ".htm")):
            tipe = "text/html; charset=utf-8"
        elif path.endswith(".css"):
            tipe = "text/css; charset=utf-8"
        elif path.endswith(".js"):
            tipe = "application/javascript; charset=utf-8"
        elif path.endswith(".json"):
            tipe = "application/json; charset=utf-8"
        elif path.endswith((".png", ".jpg", ".jpeg", ".gif", ".svg")):
            tipe = "image/" + path.rsplit(".", 1)[-1].lower()
        handler._kirim(status, data, tipe)
        return

    def _handler_error(self, handler, e):
        """Kirim response error 500 dengan pesan (tanpa expose stack)."""
        body = _json.dumps({"error": str(e)}, ensure_ascii=False).encode("utf-8")
        handler._kirim(500, body, "application/json; charset=utf-8")

    def jalankan(self, port: int = 8000, host: str = "127.0.0.1"):
        """Jalankan server (blocking). Ctrl+C untuk berhenti.

        Args:
            port: Port HTTP (default 8000)
            host: Bind address (default 127.0.0.1; 0.0.0.0 untuk publik)
        """
        _Handler.app = self
        self._server = ThreadingHTTPServer((host, port), _Handler)
        print(f"Server BroLang berjalan di http://{host}:{port}")
        try:
            self._server.serve_forever()
        except KeyboardInterrupt:
            print("\nServer dihentikan.")
        finally:
            self._server.server_close()

    def jalankan_async(self, port: int = 8000, host: str = "127.0.0.1"):
        """Jalankan server di thread terpisah (non-blocking).

        Berguna untuk test: server jalan di background sementara
        program utama mengirim request ke server tersebut.
        """
        import threading

        _Handler.app = self
        self._server = ThreadingHTTPServer((host, port), _Handler)
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()
        return self

    def berhenti(self):
        """Hentikan server (untuk jalankan_async)."""
        if self._server:
            self._server.shutdown()
            self._server.server_close()
            self._server = None


def Buat() -> WebServer:
    """Buat instance WebServer baru (pola pabrik BroLang)."""
    return WebServer()


module = SimpleNamespace(
    WebServer=WebServer,
    Buat=Buat,
)
