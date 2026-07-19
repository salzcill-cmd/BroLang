"""
Built-in Functions untuk BroLang
=================================

Fungsi-fungsi bawaan yang tersedia tanpa perlu import.
"""

from typing import Any, List, Dict


def builtin_len(obj: Any) -> int:
    """len(obj) - Mengembalikan panjang objek."""
    if isinstance(obj, (list, str, dict, tuple, set)):
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


def builtin_boolean(val: Any) -> bool:
    """boolean(val) - Konversi ke boolean."""
    return bool(val)


def builtin_tipe(val: Any) -> str:
    """tipe(val) - Mengembalikan tipe data."""
    type_map = {
        int: "angka",
        float: "desimal",
        str: "teks",
        bool: "boolean",
        list: "list",
        dict: "objek",
        tuple: "tuple",
        set: "set",
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


# v4.0 New Builtins

def builtin_zip(*iterables) -> list:
    """zip(*iterables) - Menggabungkan iterable secara paralel."""
    return list(zip(*iterables))


def builtin_enumerate(iterable, start=0) -> list:
    """enumerate(iterable, start=0) - Menambahkan index."""
    return list(enumerate(iterable, start))


def builtin_urutkan(iterable, key=None, reverse=False) -> list:
    """urutkan(iterable, key, reverse) - Mengurutkan."""
    return sorted(iterable, key=key, reverse=reverse)


def builtin_terbalik(iterable) -> list:
    """terbalik(iterable) - Membalik urutan."""
    return list(reversed(iterable))


def builtin_ada(iterable) -> bool:
    """ada(iterable) - True jika ada elemen yang True."""
    return any(iterable)


def builtin_semua(iterable) -> bool:
    """semua(iterable) - True jika semua elemen True."""
    return all(iterable)


def builtin_isinstance(obj, types) -> bool:
    """isinstance(obj, tipe) - Cek tipe objek."""
    if isinstance(types, tuple):
        return isinstance(obj, types)
    return isinstance(obj, types)


def builtin_punya(obj, name) -> bool:
    """punya(obj, nama) - Cek apakah objek punya atribut/properti."""
    return hasattr(obj, name)


def builtin_ambil_atribut(obj, name) -> Any:
    """ambil_atribut(obj, nama) - Ambil atribut."""
    return getattr(obj, name)


def builtin_atur_atribut(obj, name, value) -> None:
    """atur_atribut(obj, nama, nilai) - Atur atribut."""
    setattr(obj, name, value)


def builtin_id(obj) -> int:
    """id(obj) - Mengembalikan unique identifier."""
    return id(obj)


def builtin_hash(obj) -> int:
    """hash(obj) - Mengembalikan hash value."""
    return hash(obj)


def builtin_eval(source: str) -> Any:
    """eval(source) - Mengevaluasi string sebagai ekspresi."""
    # Safety: only allow simple expressions
    import ast as python_ast
    try:
        tree = python_ast.parse(source, mode='eval')
        return eval(compile(tree, '<brolang>', 'eval'))
    except Exception:
        raise RuntimeError(f"Gagal mengevaluasi: {source}")


def builtin_exec(source: str) -> None:
    """exec(source) - Mengeksekusi string sebagai kode."""
    import ast as python_ast
    try:
        tree = python_ast.parse(source)
        exec(compile(tree, '<brolang>', 'exec'))
    except Exception as e:
        raise RuntimeError(f"Gagal mengeksekusi: {e}")


def builtin_abs(val) -> Any:
    """abs(val) - Nilai absolut."""
    return abs(val)


def builtin_round_val(val, digits=0) -> Any:
    """round(val, digits) - Pembulatan."""
    return round(val, digits)


def builtin_min_val(*args) -> Any:
    """min(iterable) atau min(a, b, ...) - Nilai minimum."""
    if len(args) == 1 and hasattr(args[0], '__iter__'):
        return min(args[0])
    return min(args)


def builtin_max_val(*args) -> Any:
    """max(iterable) atau max(a, b, ...) - Nilai maksimum."""
    if len(args) == 1 and hasattr(args[0], '__iter__'):
        return max(args[0])
    return max(args)


BUILTINS: Dict[str, Any] = {
    "len": builtin_len,
    "panjang": builtin_len,
    "angka": builtin_angka,
    "desimal": builtin_desimal,
    "teks": builtin_teks,
    "boolean": builtin_boolean,
    "tipe": builtin_tipe,
    "range": builtin_range,
    "jumlah": builtin_jumlah,
    "peta": builtin_peta,
    "saring": builtin_saring,
    # v4.0 builtins
    "zip": builtin_zip,
    "enumerate": builtin_enumerate,
    "min": builtin_min_val,
    "max": builtin_max_val,
    "urutkan": builtin_urutkan,
    "terbalik": builtin_terbalik,
    "ada": builtin_ada,
    "semua": builtin_semua,
    "isinstance": builtin_isinstance,
    "punya": builtin_punya,
    "ambil_atribut": builtin_ambil_atribut,
    "atur_atribut": builtin_atur_atribut,
    "id": builtin_id,
    "hash": builtin_hash,
    "eval": builtin_eval,
    "exec": builtin_exec,
    "abs": builtin_abs,
    "round": builtin_round_val,
}
