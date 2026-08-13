"""
Modul Jaringan BroLang
======================

HTTP client & info jaringan.

Contoh:
    impor jaringan
    respon = jaringan.dapatkan("https://api.example.com")
    teks = jaringan.muat("https://example.com")
"""

import socket
from types import SimpleNamespace
from typing import Optional, Dict, Any


def dapatkan(url: str, timeout: int = 30) -> Dict[str, Any]:
    """HTTP GET request (data di-parse sebagai JSON bila memungkinkan)."""
    try:
        import urllib.request
        import json

        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read().decode("utf-8")
            try:
                parsed = json.loads(data) if data else None
            except ValueError:
                parsed = data
            return {
                "status": resp.status,
                "data": parsed,
                "headers": dict(resp.headers),
            }
    except Exception as e:
        return {"status": 0, "error": str(e), "data": None}


def kirim(url: str, data: Any = None, method: str = "POST", timeout: int = 30) -> Dict[str, Any]:
    """HTTP request dengan data JSON."""
    try:
        import urllib.request
        import json

        body = json.dumps(data).encode("utf-8") if data else None
        req = urllib.request.Request(
            url, data=body, method=method,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            resp_data = resp.read().decode("utf-8")
            try:
                parsed = json.loads(resp_data) if resp_data else None
            except ValueError:
                parsed = resp_data
            return {
                "status": resp.status,
                "data": parsed,
                "headers": dict(resp.headers),
            }
    except Exception as e:
        return {"status": 0, "error": str(e), "data": None}


# ============= v7.1 =============


def muat(url: str, timeout: int = 30) -> str:
    """Ambil isi halaman sebagai teks polos (HTTP GET)."""
    try:
        import urllib.request
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8")
    except Exception as e:
        return f"Error: {e}"


def kirim_json(url: str, data: Any, timeout: int = 30) -> Dict[str, Any]:
    """HTTP POST data JSON, kembalikan data hasil (alias kirim)."""
    return kirim(url, data, method="POST", timeout=timeout)


def status(url: str, timeout: int = 10) -> int:
    """Kode status HTTP saja (0 bila gagal)."""
    return dapatkan(url, timeout=timeout).get("status", 0)


def ip_local() -> str:
    """Alamat IP lokal mesin."""
    try:
        return socket.gethostbyname(socket.gethostname())
    except Exception:
        return "127.0.0.1"


def hostname() -> str:
    """Nama host mesin."""
    return socket.gethostname()


module = SimpleNamespace(
    dapatkan=dapatkan,
    kirim=kirim,
    # v7.1
    muat=muat,
    kirim_json=kirim_json,
    status=status,
    ip_local=ip_local,
    hostname=hostname,
)
