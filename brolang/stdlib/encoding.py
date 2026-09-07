"""
Modul Encoding - Enkripsi & Encoding untuk BroLang
===================================================

Modul untuk berbagai jenis encoding/decoding.

Contoh:
    impor encoding

    # Base64
    encoding.base64_encode("Hello BroLang")
    encoding.base64_decode("SGVsbG8gQnJvTGFuZw==")

    # URL encoding
    encoding.url_encode("hello world")
    encoding.url_decode("hello%20world")

    # Hex encoding
    encoding.hex_encode("Hello")
    encoding.hex_decode("48656c6c6f")

    # Binary representation
    encoding.binary_encode(42)
    encoding.binary_decode("101010")
"""

from types import SimpleNamespace
import base64 as _base64
import urllib.parse as _urllib_parse


def _base64_encode(teks):
    """Encode teks ke base64."""
    if isinstance(teks, str):
        teks = teks.encode("utf-8")
    return _base64.b64encode(teks).decode("utf-8")


def _base64_decode(teks):
    """Decode base64 ke teks."""
    return _base64.b64decode(teks).decode("utf-8")


def _url_encode(teks):
    """URL-encode teks."""
    return _urllib_parse.quote(str(teks))


def _url_decode(teks):
    """URL-decode teks."""
    return _urllib_parse.unquote(teks)


def _hex_encode(teks):
    """Encode teks ke hexadecimal."""
    if isinstance(teks, str):
        teks = teks.encode("utf-8")
    return teks.hex()


def _hex_decode(teks):
    """Decode hexadecimal ke teks."""
    return bytes.fromhex(teks).decode("utf-8")


def _binary_encode(angka):
    """Convert angka ke representasi binary string."""
    return bin(int(angka))[2:]


def _binary_decode(teks):
    """Convert binary string ke angka."""
    return int(teks, 2)


module = SimpleNamespace(
    base64_encode=_base64_encode,
    base64_decode=_base64_decode,
    url_encode=_url_encode,
    url_decode=_url_decode,
    hex_encode=_hex_encode,
    hex_decode=_hex_decode,
    binary_encode=_binary_encode,
    binary_decode=_binary_decode,
)
