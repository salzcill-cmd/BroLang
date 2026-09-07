"""
Modul Koleksi - Struktur Data Lanjutan untuk BroLang
=====================================================

Struktur data khusus yang sering digunakan.

Contoh:
    impor koleksi

    koleksi.Counter("hello")              -> {'h': 1, 'e': 1, 'l': 2, 'o': 1}
    koleksi.defaultdict(list)             -> dict dengan default []
    koleksi.namedtuple("Point", "x y")    -> tipe baru dengan atribut
    koleksi.deque([1,2,3])                -> double-ended queue
    koleksi.ChainMap(d1, d2)              -> gabungan dict
"""

from types import SimpleNamespace
import collections


def _Counter(iterable=None):
    """Hitung frekuensi elemen."""
    counter = collections.Counter()
    if iterable:
        for item in iterable:
            counter[item] += 1
    return dict(counter)


def _defaultdict(default_factory=None):
    """Dict dengan default value otomatis."""
    return collections.defaultdict(default_factory)


def _namedtuple(name, fields):
    """Buat tipe tuple bernama."""
    if isinstance(fields, str):
        fields = fields.split()
    return collections.namedtuple(name, fields)


def _deque(iterable=None, maxlen=None):
    """Double-ended queue."""
    d = collections.deque(iterable or [], maxlen=maxlen)
    return d


def _ChainMap(*maps):
    """Gabungan beberapa dict."""
    return dict(collections.ChainMap(*maps))


def _OrderedDict(pairs=None):
    """Dict yang mempertahankan urutan insertion."""
    if pairs:
        return dict(pairs)
    return {}


def _top_n(items, n, key=None):
    """Ambil n elemen terbesar/terkecil."""
    if key:
        return sorted(items, key=key, reverse=True)[:n]
    return sorted(items, reverse=True)[:n]


def _flatten_dict(d, parent_key='', sep='.'):
    """Flatten nested dict: {'a': {'b': 1}} -> {'a.b': 1}."""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(_flatten_dict(v, new_key, sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def _unflatten_dict(d, sep='.'):
    """Unflatten dict: {'a.b': 1} -> {'a': {'b': 1}}."""
    result = {}
    for key, value in d.items():
        parts = key.split(sep)
        current = result
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        current[parts[-1]] = value
    return result


module = SimpleNamespace(
    Counter=_Counter,
    defaultdict=_defaultdict,
    namedtuple=_namedtuple,
    deque=_deque,
    ChainMap=_ChainMap,
    OrderedDict=_OrderedDict,
    top_n=_top_n,
    flatten_dict=_flatten_dict,
    unflatten_dict=_unflatten_dict,
)
