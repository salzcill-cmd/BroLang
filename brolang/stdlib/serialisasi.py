"""
Modul Serialisasi untuk BroLang
================================

Menyediakan fungsi encoding/decoding data.

Contoh:
    impor serialisasi
    buat data = {"nama": "Budi", "umur": 25}
    buat json_str = serialisasi.ke_json(data)
    buat data_lagi = serialisasi.dari_json(json_str)
"""

import json
import base64
import pickle
from types import SimpleNamespace


def ke_json(data, indent=None):
    """Mengkonversi data ke JSON string."""
    return json.dumps(data, indent=indent, ensure_ascii=False)


def dari_json(string):
    """Mengkonversi JSON string ke data."""
    return json.loads(string)


def ke_json_file(data, filepath, indent=2):
    """Menyimpan data ke file JSON."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)


def dari_json_file(filepath):
    """Membaca data dari file JSON."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def ke_yaml_like(data):
    """Mengkonversi data ke format YAML-like (sederhana)."""
    lines = []
    _dict_to_yaml(data, lines, 0)
    return '\n'.join(lines)


def _dict_to_yaml(data, lines, indent):
    prefix = '  ' * indent
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                lines.append(f"{prefix}{key}:")
                _dict_to_yaml(value, lines, indent + 1)
            else:
                lines.append(f"{prefix}{key}: {value}")
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, (dict, list)):
                lines.append(f"{prefix}-")
                _dict_to_yaml(item, lines, indent + 1)
            else:
                lines.append(f"{prefix}- {item}")


def ke_base64(data):
    """Encode data ke base64."""
    if isinstance(data, str):
        data = data.encode('utf-8')
    return base64.b64encode(data).decode('utf-8')


def dari_base64(encoded):
    """Decode base64 ke data."""
    return base64.b64decode(encoded).decode('utf-8')


def ke_bytes(data):
    """Mengkonversi data ke bytes (pickle)."""
    return pickle.dumps(data)


def dari_bytes(data):
    """Mengkonversi bytes ke data (pickle)."""
    return pickle.loads(data)


def ke_url_encoded(data):
    """URL encode string."""
    from urllib.parse import quote
    if isinstance(data, dict):
        return '&'.join(f"{quote(str(k))}={quote(str(v))}" for k, v in data.items())
    return quote(str(data))


def dari_url_encoded(encoded):
    """URL decode string."""
    from urllib.parse import unquote, parse_qs
    if '&' in encoded:
        return parse_qs(encoded)
    return unquote(encoded)


def ke_csv(data, delimiter=','):
    """Mengkonversi list of dict ke CSV string."""
    if not data:
        return ""
    headers = list(data[0].keys())
    lines = [delimiter.join(headers)]
    for row in data:
        values = [str(row.get(h, '')) for h in headers]
        lines.append(delimiter.join(values))
    return '\n'.join(lines)


def dari_csv(string, delimiter=','):
    """Mengkonversi CSV string ke list of dict."""
    lines = string.strip().split('\n')
    if len(lines) < 2:
        return []
    headers = lines[0].split(delimiter)
    result = []
    for line in lines[1:]:
        values = line.split(delimiter)
        row = {}
        for i, header in enumerate(headers):
            row[header] = values[i] if i < len(values) else ''
        result.append(row)
    return result


module = SimpleNamespace(
    ke_json=ke_json,
    dari_json=dari_json,
    ke_json_file=ke_json_file,
    dari_json_file=dari_json_file,
    ke_yaml_like=ke_yaml_like,
    ke_base64=ke_base64,
    dari_base64=dari_base64,
    ke_bytes=ke_bytes,
    dari_bytes=dari_bytes,
    ke_url_encoded=ke_url_encoded,
    dari_url_encoded=dari_url_encoded,
    ke_csv=ke_csv,
    dari_csv=dari_csv,
)
