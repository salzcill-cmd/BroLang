"""
Modul Web BroLang
=================

HTTP client sederhana: GET, POST, PUT, DELETE, dan request bebas.

Mengembalikan objek respon dengan atribut:
- teks   : isi body sebagai teks
- status : kode status HTTP (200, 404, ...)
- json   : isi body yang di-parse sebagai JSON (atau kosong bila bukan JSON)
- header : objek berisi header respon
- sukses : True bila status 2xx

Contoh:
    impor web

    buat respon = web.get("https://api.example.com/data")
    tulis respon.status
    tulis respon.teks

    buat hasil = web.post("https://api.example.com/login",
                          json={"nama": "Budi", "kata": "rahasia"})
    jika hasil.sukses maka
        tulis hasil.json
    selesai
"""

import json as _json
import urllib.error
import urllib.parse
import urllib.request
from types import SimpleNamespace


def _build_respon(
    metode: str, url: str, data=None, header=None, timeout: float = 30.0, json_body=None
):
    """Kirim HTTP request dan bangun objek respon BroLang."""
    try:
        req_header = dict(header or {})
        body = None
        if json_body is not None:
            body = _json.dumps(json_body).encode("utf-8")
            req_header.setdefault("Content-Type", "application/json")
        elif data is not None:
            if isinstance(data, dict):
                body = urllib.parse.urlencode(data).encode("utf-8")
                req_header.setdefault("Content-Type", "application/x-www-form-urlencoded")
            else:
                body = str(data).encode("utf-8")

        req = urllib.request.Request(url, data=body, headers=req_header, method=metode)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            teks = raw.decode("utf-8", errors="replace")
            try:
                parsed_json = _json.loads(teks)
            except ValueError:
                parsed_json = None
            return SimpleNamespace(
                teks=teks,
                status=resp.status,
                json=parsed_json,
                header=dict(resp.headers),
                sukses=200 <= resp.status < 300,
                error=None,
            )
    except urllib.error.HTTPError as e:
        # Server merespons dengan error (404, 500, ...) — tetap baca body
        try:
            teks = e.read().decode("utf-8", errors="replace")
        except (OSError, ValueError):
            teks = ""
        try:
            parsed_json = _json.loads(teks) if teks else None
        except ValueError:
            parsed_json = None
        return SimpleNamespace(
            teks=teks,
            status=e.code,
            json=parsed_json,
            header=dict(e.headers),
            sukses=False,
            error=str(e),
        )
    except (OSError, ValueError) as e:
        # Error jaringan (koneksi ditolak, timeout, DNS) atau URL tak valid
        return SimpleNamespace(
            teks="",
            status=0,
            json=None,
            header={},
            sukses=False,
            error=str(e),
        )


def get(url: str, header=None, timeout: float = 30.0) -> SimpleNamespace:
    """HTTP GET request.

    Contoh:
        buat respon = web.get("https://api.example.com/data")
        tulis respon.teks
    """
    return _build_respon("GET", url, header=header, timeout=timeout)


def post(url: str, data=None, json=None, header=None, timeout: float = 30.0) -> SimpleNamespace:
    """HTTP POST request.

    Args:
        data: dict/form yang di-encode urlencoded, atau teks mentah.
        json: dict yang dikirim sebagai JSON (lebih umum untuk API).
              Bila `json` diisi, `data` diabaikan (json menang).

    Contoh:
        buat respon = web.post("https://api.example.com/login",
                               json={"nama": "Budi"})
    """
    return _build_respon("POST", url, data=data, header=header, timeout=timeout, json_body=json)


def put(url: str, data=None, json=None, header=None, timeout: float = 30.0) -> SimpleNamespace:
    """HTTP PUT request (update resource)."""
    return _build_respon("PUT", url, data=data, header=header, timeout=timeout, json_body=json)


def hapus_http(url: str, header=None, timeout: float = 30.0) -> SimpleNamespace:
    """HTTP DELETE request.

    Nama 'hapus' tidak dipakai karena tabrakan keyword BroLang.
    """
    return _build_respon("DELETE", url, header=header, timeout=timeout)


def kirim(
    metode: str, url: str, data=None, json=None, header=None, timeout: float = 30.0
) -> SimpleNamespace:
    """HTTP request bebas dengan metode apa pun (GET/POST/PUT/DELETE/PATCH)."""
    return _build_respon(
        metode.upper(), url, data=data, header=header, timeout=timeout, json_body=json
    )


module = SimpleNamespace(
    get=get,
    post=post,
    put=put,
    hapus_http=hapus_http,
    kirim=kirim,
)
