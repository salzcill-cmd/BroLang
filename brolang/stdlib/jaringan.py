"""
Modul Jaringan BroLang
======================

HTTP client untuk komunikasi jaringan.

Contoh:
    impor jaringan
    respon = jaringan.dapatkan("https://api.example.com")
"""

from types import SimpleNamespace
from typing import Optional, Dict, Any


def dapatkan(url: str, timeout: int = 30) -> Dict[str, Any]:
    """HTTP GET request."""
    try:
        import urllib.request
        import json

        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read().decode("utf-8")
            return {
                "status": resp.status,
                "data": json.loads(data) if data else None,
                "headers": dict(resp.headers),
            }
    except Exception as e:
        return {"status": 0, "error": str(e), "data": None}


def kirim(url: str, data: Any = None, method: str = "POST", timeout: int = 30) -> Dict[str, Any]:
    """HTTP request dengan data."""
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
            return {
                "status": resp.status,
                "data": json.loads(resp_data) if resp_data else None,
                "headers": dict(resp.headers),
            }
    except Exception as e:
        return {"status": 0, "error": str(e), "data": None}


module = SimpleNamespace(
    dapatkan=dapatkan,
    kirim=kirim,
)
