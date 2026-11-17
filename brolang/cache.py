"""
Cache bytecode BroLang
======================

Menyimpan kode Python yang telah dikompilasi (code object) ke file cache
berbasis hash isi sumber, sehingga eksekusi berikutnya dapat melewati tahap
lexing, parsing, dan kompilasi jika sumber tidak berubah. Percepat startup
secara signifikan untuk file yang dijalankan berkali-kali.
"""

import hashlib
import marshal
import os
import sys
import time

CACHE_DIR = os.path.join(os.path.expanduser("~"), ".brolang", "cache")


def _cache_path(source: str, filename: str) -> str:
    """Hasilkan path cache file berdasarkan hash isi sumber + nama file."""
    key = f"{filename}\0{source}".encode("utf-8")
    digest = hashlib.sha256(key).hexdigest()[:16]
    safe_name = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in filename)
    return os.path.join(CACHE_DIR, f"{safe_name}_{digest}.brolangc")


def ensure_cache_dir() -> None:
    """Buat direktori cache jika belum ada."""
    os.makedirs(CACHE_DIR, exist_ok=True)


def load_cached(source: str, filename: str):
    """Muat code object dari cache jika cocok dengan isi sumber saat ini.

    Returns:
        code object atau None jika cache tidak ditemukan / tidak valid.
    """
    path = _cache_path(source, filename)
    if not os.path.exists(path):
        return None
    try:
        with open(path, "rb") as f:
            data = f.read()
        # Format: [4 byte magic version][marshaled code object]
        if len(data) < 4:
            return None
        version = int.from_bytes(data[:4], "little")
        if version != 1:
            return None
        code = marshal.loads(data[4:])
        return code
    except Exception:
        return None


def save_cached(source: str, filename: str, code) -> None:
    """Simpan code object ke cache."""
    ensure_cache_dir()
    path = _cache_path(source, filename)
    try:
        payload = marshal.dumps(code)
        data = (1).to_bytes(4, "little") + payload
        with open(path, "wb") as f:
            f.write(data)
    except Exception:
        pass  # Cache gagal ditulis tidak fatal


def clear_cache() -> int:
    """Hapus semua file cache. Kembalikan jumlah file yang dihapus."""
    if not os.path.isdir(CACHE_DIR):
        return 0
    removed = 0
    for name in os.listdir(CACHE_DIR):
        if name.endswith(".brolangc"):
            try:
                os.remove(os.path.join(CACHE_DIR, name))
                removed += 1
            except OSError:
                pass
    return removed
