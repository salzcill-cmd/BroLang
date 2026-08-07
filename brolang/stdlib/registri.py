"""
Modul Registri BroLang (v6.0)
=============================

Server package registry online untuk BroLang. Membuat registry paket
yang bisa diakses oleh `bro pkg install` dari mesin lain.

API:
    GET  /api/paket            -> daftar semua paket (JSON)
    GET  /api/paket/<nama>     -> info satu paket
    POST /api/publish          -> publish paket (multipart: manifest.json + paket.tar.gz)
    GET  /api/download/<nama>  -> unduh paket (tar.gz)

Contoh:
    impor registri
    registri.jalankan(8000, folder_registry="~/brolang-registry")

    # Dari terminal lain:
    bro pkg install nama-paket --registry http://host:8000
"""

import io
import os
import json
import tarfile
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from types import SimpleNamespace

_DEFAULT_DIR = os.path.expanduser("~/.brolang/registry-server")

_REGISTRY_DIR = os.environ.get("BROLANG_REGISTRY_DIR", _DEFAULT_DIR)


def atur_folder(path: str) -> None:
    """Atur folder tempat registry menyimpan paket."""
    global _REGISTRY_DIR
    _REGISTRY_DIR = path
    os.makedirs(path, exist_ok=True)


def _file_registry() -> str:
    return os.path.join(_REGISTRY_DIR, "registry.json")


def _load() -> dict:
    if os.path.exists(_file_registry()):
        try:
            with open(_file_registry(), "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            pass
    return {}


def _save(data: dict) -> None:
    os.makedirs(_REGISTRY_DIR, exist_ok=True)
    with open(_file_registry(), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def buat_tar(manifest: dict, files: dict) -> bytes:
    """Buat tarball dari {relative_path: konten_teks}."""
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        data = json.dumps(manifest, indent=2).encode("utf-8")
        info = tarfile.TarInfo("brolang.json")
        info.size = len(data)
        tar.addfile(info, io.BytesIO(data))
        for rel, konten in files.items():
            data = konten.encode("utf-8")
            info = tarfile.TarInfo(rel)
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))
    return buf.getvalue()


def _class_handler(registri_dir: str):
    class _Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):  # senyap
            pass

        def _kirim_json(self, data: dict, status: int = 200):
            body = json.dumps(data).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            path = self.path
            if path == "/" or path == "/api/paket":
                self._kirim_json({"paket": _load()})
                return
            if path.startswith("/api/paket/"):
                nama = path.rsplit("/", 1)[-1]
                reg = _load()
                if nama in reg:
                    self._kirim_json({"paket": reg[nama]})
                else:
                    self._kirim_json({"error": f"Paket '{nama}' tidak ditemukan."}, 404)
                return
            if path.startswith("/api/download/"):
                nama = path.rsplit("/", 1)[-1]
                reg = _load()
                if nama not in reg:
                    self._kirim_json({"error": f"Paket '{nama}' tidak ditemukan."}, 404)
                    return
                tar_path = os.path.join(registri_dir, f"{nama}.tar.gz")
                if not os.path.exists(tar_path):
                    self._kirim_json({"error": f"Arsip paket '{nama}' hilang."}, 404)
                    return
                with open(tar_path, "rb") as f:
                    body = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "application/gzip")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            self._kirim_json({"error": "Endpoint tidak dikenal."}, 404)

        def do_POST(self):
            if self.path != "/api/publish":
                self._kirim_json({"error": "Endpoint tidak dikenal."}, 404)
                return
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length)
            try:
                payload = json.loads(raw.decode("utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                self._kirim_json({"error": "Body harus JSON."}, 400)
                return
            manifest = payload.get("manifest")
            files = payload.get("files", {})
            if not manifest or not isinstance(manifest, dict):
                self._kirim_json({"error": "Manifest tidak valid."}, 400)
                return
            nama = manifest.get("nama")
            if not nama:
                self._kirim_json({"error": "Manifest harus punya 'nama'."}, 400)
                return
            versi = manifest.get("versi", "1.0.0")

            # Simpan tar.gz
            os.makedirs(registri_dir, exist_ok=True)
            tar_path = os.path.join(registri_dir, f"{nama}.tar.gz")
            with open(tar_path, "wb") as f:
                f.write(buat_tar(manifest, files))

            reg = _load()
            reg[nama] = {
                "nama": nama,
                "versi": versi,
                "deskripsi": manifest.get("deskripsi", ""),
                "dependencies": manifest.get("dependencies", []),
                "source": "registry",
                "main": manifest.get("main", "__init__.bro"),
            }
            _save(reg)
            self._kirim_json({"sukses": True, "nama": nama, "versi": versi})

    return _Handler


def jalankan(port: int = 8000, host: str = "127.0.0.1", folder: str = "") -> None:
    """Jalankan server registry (blocking). Ctrl+C untuk berhenti.

    Contoh:
        registri.jalankan(8000)
    """
    global _REGISTRY_DIR
    if folder:
        _REGISTRY_DIR = folder
    os.makedirs(_REGISTRY_DIR, exist_ok=True)
    server = HTTPServer((host, port), _class_handler(_REGISTRY_DIR))
    print(f"Registry BroLang berjalan di http://{host}:{port}")
    print(f"Folder paket   : {_REGISTRY_DIR}")
    print()
    print("Paket yang tersedia:")
    for nama, info in _load().items():
        print(f"  {nama} ({info.get('versi', '?')}) - {info.get('deskripsi', '')}")
    print()
    print("Install dari mesin lain:")
    print(f"  bro pkg install <nama> --registry http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nRegistry dihentikan.")
    finally:
        server.server_close()


def jalankan_async(port: int = 8000, host: str = "127.0.0.1", folder: str = "") -> SimpleNamespace:
    """Jalankan server registry di thread latar. Kembalikan objek berhenti()."""
    global _REGISTRY_DIR
    if folder:
        _REGISTRY_DIR = folder
    os.makedirs(_REGISTRY_DIR, exist_ok=True)
    server = HTTPServer((host, port), _class_handler(_REGISTRY_DIR))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return SimpleNamespace(
        port=port,
        host=host,
        server=server,
        berhenti=server.shutdown,
    )


module = SimpleNamespace(
    atur_folder=atur_folder,
    jalankan=jalankan,
    jalankan_async=jalankan_async,
    buat_tar=buat_tar,
)
