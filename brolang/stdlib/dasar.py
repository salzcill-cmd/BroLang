"""
Modul Dasar (Base Encoding) untuk BroLang
==========================================

Menyediakan fungsi encoding/decoding berbagai format.

Contoh:
    impor dasar
    buat encoded = dasar.ke_base64("Halo Dunia")
    buat decoded = dasar.dari_base64(encoded)
    tulis(decoded)
"""

import base64
import binascii
from types import SimpleNamespace


def ke_base64(data):
    """Encode ke base64."""
    if isinstance(data, str):
        data = data.encode('utf-8')
    return base64.b64encode(data).decode('utf-8')


def dari_base64(encoded):
    """Decode dari base64."""
    return base64.b64decode(encoded).decode('utf-8')


def ke_base32(data):
    """Encode ke base32."""
    if isinstance(data, str):
        data = data.encode('utf-8')
    return base64.b32encode(data).decode('utf-8')


def dari_base32(encoded):
    """Decode dari base32."""
    return base64.b32decode(encoded).decode('utf-8')


def ke_hex(data):
    """Encode ke hexadecimal."""
    if isinstance(data, str):
        data = data.encode('utf-8')
    return data.hex()


def dari_hex(encoded):
    """Decode dari hexadecimal."""
    return bytes.fromhex(encoded).decode('utf-8')


def ke_bin(data):
    """Encode ke binary string."""
    if isinstance(data, str):
        data = data.encode('utf-8')
    return ' '.join(format(byte, '08b') for byte in data)


def dari_bin(encoded):
    """Decode dari binary string."""
    binary_list = encoded.split()
    data = bytes(int(b, 2) for b in binary_list)
    return data.decode('utf-8')


def ke_url(data):
    """URL encode."""
    from urllib.parse import quote
    if isinstance(data, dict):
        return '&'.join(f"{quote(str(k))}={quote(str(v))}" for k, v in data.items())
    return quote(str(data))


def dari_url(encoded):
    """URL decode."""
    from urllib.parse import unquote, parse_qs
    if '&' in encoded and '=' in encoded:
        return parse_qs(encoded)
    return unquote(encoded)


def ke_html(data):
    """HTML entity encode."""
    import html
    return html.escape(str(data))


def dari_html(encoded):
    """HTML entity decode."""
    import html
    return html.unescape(encoded)


module = SimpleNamespace(
    ke_base64=ke_base64,
    dari_base64=dari_base64,
    ke_base32=ke_base32,
    dari_base32=dari_base32,
    ke_hex=ke_hex,
    dari_hex=dari_hex,
    ke_bin=ke_bin,
    dari_bin=dari_bin,
    ke_url=ke_url,
    dari_url=dari_url,
    ke_html=ke_html,
    dari_html=dari_html,
)
