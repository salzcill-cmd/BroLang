"""
Modul HTTP - HTTP Client untuk BroLang
=======================================

Modul untuk melakukan HTTP requests.

Contoh:
    impor http

    # GET request
    resp = http.get("https://api.example.com/data")
    tulis resp.teks
    tulis resp.kode

    # POST request
    resp = http.post("https://api.example.com/data", {"nama": "Budi"})
    tulis resp.json()

    # Dengan headers
    resp = http.get("https://api.example.com/data", {
        "Authorization": "Bearer token123"
    })
"""

from types import SimpleNamespace
import urllib.request as _urllib_request
import json as _json


class _Response:
    """Response object dari HTTP request."""

    __slots__ = ("teks", "kode", "headers", "_data")

    def __init__(self, data, kode, headers):
        self._data = data
        self.teks = data.decode("utf-8") if isinstance(data, bytes) else str(data)
        self.kode = kode
        self.headers = dict(headers) if headers else {}

    def json(self):
        """Parse response sebagai JSON."""
        return _json.loads(self.teks)

    def __repr__(self):
        return f"<Response {self.kode}>"


def _get(url, headers=None, timeout=30):
    """HTTP GET request."""
    req = _urllib_request.Request(url, method="GET")
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)
    try:
        with _urllib_request.urlopen(req, timeout=timeout) as resp:
            return _Response(resp.read(), resp.status, resp.headers)
    except Exception as e:
        return _Response(str(e).encode(), 0, {})


def _post(url, data=None, headers=None, timeout=30):
    """HTTP POST request."""
    body = None
    if data is not None:
        if isinstance(data, dict):
            body = _json.dumps(data).encode("utf-8")
            if headers is None:
                headers = {}
            headers["Content-Type"] = "application/json"
        elif isinstance(data, str):
            body = data.encode("utf-8")
        elif isinstance(data, bytes):
            body = data

    req = _urllib_request.Request(url, data=body, method="POST")
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)
    try:
        with _urllib_request.urlopen(req, timeout=timeout) as resp:
            return _Response(resp.read(), resp.status, resp.headers)
    except Exception as e:
        return _Response(str(e).encode(), 0, {})


def _put(url, data=None, headers=None, timeout=30):
    """HTTP PUT request."""
    body = None
    if data is not None:
        if isinstance(data, dict):
            body = _json.dumps(data).encode("utf-8")
            if headers is None:
                headers = {}
            headers["Content-Type"] = "application/json"
        elif isinstance(data, str):
            body = data.encode("utf-8")
    req = _urllib_request.Request(url, data=body, method="PUT")
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)
    try:
        with _urllib_request.urlopen(req, timeout=timeout) as resp:
            return _Response(resp.read(), resp.status, resp.headers)
    except Exception as e:
        return _Response(str(e).encode(), 0, {})


def _delete(url, headers=None, timeout=30):
    """HTTP DELETE request."""
    req = _urllib_request.Request(url, method="DELETE")
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)
    try:
        with _urllib_request.urlopen(req, timeout=timeout) as resp:
            return _Response(resp.read(), resp.status, resp.headers)
    except Exception as e:
        return _Response(str(e).encode(), 0, {})


module = SimpleNamespace(
    get=_get,
    post=_post,
    put=_put,
    delete=_delete,
    Response=_Response,
)
