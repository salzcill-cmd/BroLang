"""
Built-in Functions untuk BroLang
=================================

Fungsi-fungsi bawaan yang tersedia tanpa perlu import.
"""

from typing import Any, List, Dict


def builtin_len(obj: Any) -> int:
    """len(obj) - Mengembalikan panjang objek."""
    if isinstance(obj, (list, str, dict)):
        return len(obj)
    raise TypeError(f"Tipe {type(obj).__name__} tidak memiliki panjang.")


def builtin_angka(val: Any) -> int:
    """angka(val) - Konversi ke integer."""
    return int(val)


def builtin_desimal(val: Any) -> float:
    """desimal(val) - Konversi ke float."""
    return float(val)


def builtin_teks(val: Any) -> str:
    """teks(val) - Konversi ke string."""
    return str(val)


def builtin_tipe(val: Any) -> str:
    """tipe(val) - Mengembalikan tipe data."""
    type_map = {
        int: "angka",
        float: "desimal",
        str: "teks",
        bool: "boolean",
        list: "list",
        dict: "objek",
        type(None): "kosong",
    }
    return type_map.get(type(val), str(type(val).__name__))


def builtin_range(*args: int) -> range:
    """range(start, stop, step) - Membuat range angka."""
    return range(*args)


def builtin_jumlah(iterable: Any) -> Any:
    """jumlah(iterable) - Menjumlahkan elemen."""
    return sum(iterable)


def builtin_peta(func: Any, iterable: Any) -> List:
    """peta(func, iterable) - Map function over iterable."""
    return [func(x) for x in iterable]


def builtin_saring(func: Any, iterable: Any) -> List:
    """saring(func, iterable) - Filter iterable."""
    return [x for x in iterable if func(x)]


BUILTINS: Dict[str, Any] = {
    "len": builtin_len,
    "angka": builtin_angka,
    "desimal": builtin_desimal,
    "teks": builtin_teks,
    "tipe": builtin_tipe,
    "range": builtin_range,
    "jumlah": builtin_jumlah,
    "peta": builtin_peta,
    "saring": builtin_saring,
}
