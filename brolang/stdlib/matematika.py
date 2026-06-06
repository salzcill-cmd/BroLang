"""
Modul Matematika BroLang
========================

Fungsi matematika dasar dan lanjutan.

Contoh:
    impor matematika
    matematika.akar(25)
    matematika.sin(3.14)
"""

import math
from types import SimpleNamespace


def akar(x: float) -> float:
    """Akar kuadrat."""
    return math.sqrt(x)


def sin(x: float) -> float:
    """Sinus (radian)."""
    return math.sin(x)


def cos(x: float) -> float:
    """Cosinus (radian)."""
    return math.cos(x)


def tan(x: float) -> float:
    """Tangen (radian)."""
    return math.tan(x)


def pangkat(x: float, y: float) -> float:
    """x pangkat y."""
    return math.pow(x, y)


def absolut(x: float) -> float:
    """Nilai absolut."""
    return abs(x)


def bulat(x: float, n: int = 0) -> float:
    """Pembulatan ke n digit desimal."""
    return round(x, n)


def lantai(x: float) -> int:
    """Floor (pembulatan ke bawah)."""
    return math.floor(x)


def langit(x: float) -> int:
    """Ceil (pembulatan ke atas)."""
    return math.ceil(x)


def log(x: float, base: float = math.e) -> float:
    """Logaritma dengan basis tertentu."""
    return math.log(x, base)


def pi() -> float:
    """Nilai pi (3.14159...)."""
    return math.pi


def e() -> float:
    """Nilai e (2.71828...)."""
    return math.e


def max_(a: float, b: float) -> float:
    """Nilai maksimum."""
    return max(a, b)


def min_(a: float, b: float) -> float:
    """Nilai minimum."""
    return min(a, b)


def faktorial(n: int) -> int:
    """Faktorial dari n."""
    return math.factorial(n)


module = SimpleNamespace(
    akar=akar,
    sin=sin,
    cos=cos,
    tan=tan,
    pangkat=pangkat,
    absolut=absolut,
    bulat=bulat,
    lantai=lantai,
    langit=langit,
    log=log,
    pi=pi,
    e=e,
    max=max_,
    min=min_,
    faktorial=faktorial,
)
