"""
Modul Itertools - Iterator Combinator untuk BroLang
====================================================

Fungsi-fungsi untuk manipulasi iterator.

Contoh:
    impor itertools

    itertools.chain([1,2], [3,4])        -> [1, 2, 3, 4]
    itertools.product([1,2], [3,4])      -> [(1,3), (1,4), (2,3), (2,4)]
    itertools.kombinasi([1,2,3], 2)      -> [(1,2), (1,3), (2,3)]
    itertools.permutasi([1,2,3], 2)      -> [(1,2), (1,3), (2,1), (2,3), (3,1), (3,2)]
    itertools.accumulate([1,2,3,4])      -> [1, 3, 6, 10]
"""

from types import SimpleNamespace
from itertools import chain, product, combinations, permutations, accumulate, islice, takewhile, dropwhile, starmap, groupby, repeat, cycle, zip_longest


def _chain(*iterables):
    """Gabungkan beberapa iterable menjadi satu."""
    result = []
    for it in iterables:
        result.extend(list(it))
    return result


def _product(*iterables, repeat=1):
    """Cartesian product dari iterable."""
    from itertools import product as _prod
    return list(_prod(*iterables, repeat=repeat))


def _kombinasi(iterable, r):
    """Kombinasi r elemen dari iterable."""
    return list(combinations(iterable, r))


def _permutasi(iterable, r=None):
    """Permutasi r elemen dari iterable."""
    return list(permutations(iterable, r or len(iterable)))


def _accumulate(iterable, func=None):
    """Akumulasi (cumulative sum/func)."""
    if func is None:
        return list(accumulate(iterable))
    return list(accumulate(iterable, func))


def _take_while(iterable, pred):
    """Ambil elemen selama predikat benar."""
    return list(takewhile(pred, iterable))


def _drop_while(iterable, pred):
    """Buang elemen selama predikat benar, lalu ambil sisa."""
    return list(dropwhile(pred, iterable))


def _chunk(iterable, size):
    """Bagi iterable menjadi chunk berukuran size."""
    result = []
    chunk = []
    for item in iterable:
        chunk.append(item)
        if len(chunk) == size:
            result.append(chunk)
            chunk = []
    if chunk:
        result.append(chunk)
    return result


def _flatten(iterable):
    """Flatten nested list satu level."""
    result = []
    for item in iterable:
        if isinstance(item, (list, tuple)):
            result.extend(item)
        else:
            result.append(item)
    return result


def _group_by(iterable, key_func=None):
    """Kelompokkan elemen berdasarkan key function."""
    from collections import defaultdict
    groups = defaultdict(list)
    for item in iterable:
        key = key_func(item) if key_func else item
        groups[key].append(item)
    return dict(groups)


def _interleave(*iterables):
    """Interleave beberapa iterable."""
    result = []
    iterators = [iter(it) for it in iterables]
    while iterators:
        next_iterators = []
        for it in iterators:
            try:
                result.append(next(it))
                next_iterators.append(it)
            except StopIteration:
                pass
        iterators = next_iterators
    return result


def _repeat_value(value, n=None):
    """Ulangi nilai n kali (atau tak terbatas jika n=None)."""
    if n is None:
        return [value] * 10  # default limit
    return [value] * n


module = SimpleNamespace(
    chain=_chain,
    product=_product,
    kombinasi=_kombinasi,
    permutasi=_permutasi,
    accumulate=_accumulate,
    take_while=_take_while,
    drop_while=_drop_while,
    chunk=_chunk,
    flatten=_flatten,
    group_by=_group_by,
    interleave=_interleave,
    repeat=_repeat_value,
)
