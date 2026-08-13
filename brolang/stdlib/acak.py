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
import string
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


# ============= v7.1: generator =============


def boolean() -> bool:
    """Nilai benar/salah acak."""
    return random.random() < 0.5


def huruf() -> str:
    """Satu huruf kecil acak (a-z)."""
    return random.choice(string.ascii_lowercase)


def huruf_besar() -> str:
    """Satu huruf kapital acak (A-Z)."""
    return random.choice(string.ascii_uppercase)


def kata(panjang: int = 5) -> str:
    """Kata acak dari huruf kecil, panjang default 5."""
    return "".join(random.choice(string.ascii_lowercase) for _ in range(max(1, panjang)))


def antara(min_val: int = 0, max_val: int = 100) -> int:
    """Integer acak antara min dan max (alias bulat)."""
    return random.randint(min_val, max_val)


def kocok(items: List[Any]) -> List[Any]:
    """Acak urutan list (shuffle) dan kembalikan salinannya (v7.2)."""
    salinan = list(items)
    random.shuffle(salinan)
    return salinan


def unik(items: List[Any], jumlah: int = 1) -> List[Any]:
    """Ambil N item unik tanpa pengulangan (v7.2)."""
    return random.sample(list(items), min(int(jumlah), len(items)))


def koin() -> str:
    """Lempar koin: 'kepala' atau 'ekor' (v7.2)."""
    return "kepala" if random.random() < 0.5 else "ekor"


def dadu(sisi: int = 6) -> int:
    """Lempar dadu dengan jumlah sisi tertentu (v7.2)."""
    return random.randint(1, int(sisi))


module = SimpleNamespace(
    angka=angka,
    bulat=bulat,
    pilih=pilih,
    pilih_beberapa=pilih_beberapa,
    acak_list=acak_list,
    seed=seed,
    # v7.1
    boolean=boolean,
    huruf=huruf,
    huruf_besar=huruf_besar,
    kata=kata,
    antara=antara,
    # v7.2
    kocok=kocok,
    unik=unik,
    koin=koin,
    dadu=dadu,
)
