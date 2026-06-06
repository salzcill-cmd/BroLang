"""
Modul Acak BroLang
==================

Random number generation.

Contoh:
    impor acak
    angka = acak.angka(1, 100)
    item = acak.pilih([1, 2, 3])
"""

import random
from types import SimpleNamespace
from typing import List, Any


def angka(min_val: float = 0, max_val: float = 1) -> float:
    """Angka acak antara min dan max."""
    return random.uniform(min_val, max_val)


def bulat(min_val: int = 0, max_val: int = 100) -> int:
    """Integer acak antara min dan max."""
    return random.randint(min_val, max_val)


def pilih(items: List[Any]) -> Any:
    """Pilih item acak dari list."""
    return random.choice(items)


def pilih_beberapa(items: List[Any], jumlah: int = 1) -> List[Any]:
    """Pilih beberapa item acak dari list."""
    return random.sample(items, min(jumlah, len(items)))


def acak_list(items: List[Any]) -> List[Any]:
    """Acak urutan list."""
    result = items.copy()
    random.shuffle(result)
    return result


def seed(nilai: int) -> None:
    """Set seed untuk reproducibilitas."""
    random.seed(nilai)


module = SimpleNamespace(
    angka=angka,
    bulat=bulat,
    pilih=pilih,
    pilih_beberapa=pilih_beberapa,
    acak_list=acak_list,
    seed=seed,
)
