"""
Modul Fungsi - Utility Fungsi untuk BroLang
=============================================

Fungsi-fungsi utility untuk higher-order programming.

Contoh:
    impor fungsi

    fungsi.parsial(f, 1)           -> fungsi baru dengan argumen tetap
    fungsi.cache(f)                -> memoize fungsi (LRU cache)
    fungsi.total_urutan(Kelas)     -> tambah operator comparison ke kelas
    fungsi.reduce(f, [1,2,3])      -> reduce/accumulate
"""

from types import SimpleNamespace
from functools import reduce, partial, lru_cache, wraps, total_ordering, cache


def _parsial(func, *args, **kwargs):
    """Buat fungsi baru dengan beberapa argumen tetap."""
    return partial(func, *args, **kwargs)


def _cache(func, maxsize=128):
    """Memoize fungsi dengan LRU cache."""
    return lru_cache(maxsize=maxsize)(func)


def _total_urutan(cls):
    """Tambahkan operator comparison otomatis ke kelas.

    Cukup definisikan __eq__ dan __lt__, sisanya di-generate otomatis.
    """
    return total_ordering(cls)


def _reduce(func, iterable, initial=None):
    """Reduce iterable menggunakan func."""
    if initial is not None:
        return reduce(func, iterable, initial)
    return reduce(func, iterable)


def _compose(*funcs):
    """Komposisi fungsi: compose(f, g)(x) = f(g(x))."""
    def composed(x):
        result = x
        for f in reversed(funcs):
            result = f(result)
        return result
    return composed


def _memoize(func):
    """Memoize fungsi sederhana (tanpa batas cache)."""
    cache_dict = {}
    @wraps(func)
    def wrapper(*args):
        if args not in cache_dict:
            cache_dict[args] = func(*args)
        return cache_dict[args]
    wrapper.cache = cache_dict
    return wrapper


def _clamp(value, min_val, max_val):
    """Batasi nilai antara min dan max."""
    return max(min_val, min(max_val, value))


def _invoke(obj, method_name, *args, **kwargs):
    """Panggil method pada objek berdasarkan nama string."""
    method = getattr(obj, method_name)
    return method(*args, **kwargs)


module = SimpleNamespace(
    parsial=_parsial,
    cache=_cache,
    total_urutan=_total_urutan,
    reduce=_reduce,
    compose=_compose,
    memoize=_memoize,
    clamp=_clamp,
    invoke=_invoke,
    wraps=wraps,
)
