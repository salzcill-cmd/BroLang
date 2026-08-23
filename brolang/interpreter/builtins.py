"""
Built-in Functions untuk BroLang
=================================

Fungsi-fungsi bawaan yang tersedia tanpa perlu import.
"""

from typing import Any, List, Dict


def builtin_len(obj: Any) -> int:
    """len(obj) - Mengembalikan panjang objek."""
    if isinstance(obj, (list, str, dict, tuple, set, bytes)):
        return len(obj)
    # Objek kelas BroLang dengan overload `_panjang_` (v5.5)
    getter = getattr(obj, "get", None)
    if callable(getter):
        try:
            method = getter("_panjang_")
            if callable(method) and not isinstance(method, type(obj)):
                return int(method(obj))
        except Exception:
            pass
    raise TypeError(f"Tipe {type(obj).__name__} tidak memiliki panjang.")


def builtin_angka(val: Any) -> int:
    """angka(val) - Konversi ke integer."""
    return int(val)


def builtin_desimal(val: Any) -> float:
    """desimal(val) - Konversi ke float."""
    return float(val)


def builtin_teks(val: Any) -> str:
    """teks(val) - Konversi ke string (hormati overload `_teks_`)."""
    getter = getattr(val, "get", None)
    if callable(getter):
        try:
            method = getter("_teks_")
            if callable(method) and not isinstance(method, type(val)):
                return str(method(val))
        except Exception:
            pass
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


# v5.0 Type checking

_TYPE_MAP = {
    "angka": (int, float),
    "desimal": float,
    "bilangan": int,
    "teks": str,
    "boolean": bool,
    "daftar": list,
    "objek": dict,
    "tipe": type,
    "kosong": type(None),
}


def builtin_cektipe(value, tipe_name=None):
    """cek_tipe(val, tipe?) - Cek tipe nilai."""
    if tipe_name is None:
        return type(value).__name__
    expected = _TYPE_MAP.get(tipe_name, tipe_name)
    if isinstance(expected, str):
        try:
            return isinstance(value, eval(expected))
        except Exception:
            return False
    return isinstance(value, expected)


def builtin_pastikan(value, tipe_name, pesan=None):
    """pastikan(val, tipe, pesan?) - Validasi tipe, lempar error jika salah."""
    if not builtin_cektipe(value, tipe_name):
        msg = pesan or f"Diharapkan tipe '{tipe_name}', tapi mendapatkan '{type(value).__name__}'."
        from brolang.exceptions import RuntimeError_
        raise RuntimeError_(message=msg)


def builtin_hentikan_iterasi():
    """hentikan_iterasi() - Memberhentikan iterasi dari __next__."""
    raise StopIteration("Iterasi berhenti")


# v8.2: properti decorator — clean getter/setter syntax
class _Property:
    """Objek properti yang mengikat getter & setter ke nama atribut.

    Digunakan oleh `properti` decorator:
        @properti
        fungsi nama(self)
            kembali self._nama
        selesai

    Atau dengan getter + setter:
        @properti
        fungsi nama(self)
            kembali self._nama
        selesai
        @nama.setter
        fungsi nama_set(self, v)
            self._nama = v
        selesai
    """

    def __init__(self, fget=None, fset=None, name=None):
        self.fget = fget
        self.fset = fset
        self.name = name  # diisi saat dekorasi

    def getter(self, func):
        """Dekorasi getter baru: @nama.getter"""
        self.fget = func
        return self

    def setter(self, func):
        """Dekorasi setter baru: @nama.setter"""
        self.fset = func
        return self


def builtin_properti(func_or_fget=None):
    """properti(fget) atau @properti — dekorator properti untuk kelas.

    v8.2: Sintaks bersih untuk getter/setter:

        kelas Suhu
            fungsi __init__(self, derajat)
                self._derajat = derajat
            selesai

            @properti
            fungsi derajat(self)
                kembali self._derajat
            selesai

            @derajat.setter
            fungsi set_derajat(self, v)
                self._derajat = v
            selesai
        selesai

        buat s = Suhu(36)
        tulis s.derajat       # 36 (getter)
        s.derajat = 37        # setter
        tulis s.derajat       # 37

    Bisa dipakai tanpa setter (read-only) atau dengan setter.
    """
    if func_or_fget is not None and callable(func_or_fget):
        # @properti tanpa argumen — fget = func_or_fget
        prop = _Property(fget=func_or_fget)
        prop.name = func_or_fget.__name__
        return prop

    # properti(fget) — mode fungsi biasa
    def decorator(fget):
        prop = _Property(fget=fget)
        prop.name = fget.__name__
        return prop
    return decorator


# v8.2: _Property juga harus di-expose untuk setter decorator
def builtin_properti_setter(prop):
    """Helper internal: buat setter decorator dari properti object.

    Dipanggil dari interpreter saat melihat `@nama.setter` pada method
    dalam kelas. Mengembalikan fungsi decorator yang menerima setter
    function dan mengembalikan properti object yang sudah di-update.
    """
    def decorator(func):
        if isinstance(prop, _Property):
            prop.fset = func
            return prop
        return prop
    return decorator


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
    # v5.0 Type checking
    "cek_tipe": builtin_cektipe,
    "pastikan": builtin_pastikan,
    # Iterator
    "hentikan_iterasi": builtin_hentikan_iterasi,
    # v8.2: properti decorator
    "properti": builtin_properti,
    "_Property": _Property,
}
