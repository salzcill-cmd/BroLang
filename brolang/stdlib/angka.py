"""
Modul Angka BroLang
===================

Matematika lanjut: konstanta & fungsi matematika tambahan.

Modul ini adalah versi lengkap dari `matematika` — dengan konstanta
`pi` dan `e` langsung sebagai nilai (bukan fungsi), plus fungsi cepat
`sqr`, `abs`, `min`, `max`, dan lainnya.

Contoh:
    impor angka

    tulis angka.pi           # 3.141592653589793
    tulis angka.e            # 2.718281828459045
    tulis angka.sqr(16)      # 4.0
    tulis angka.abs(-5)      # 5
    tulis angka.min(3, 7)    # 3
    tulis angka.max(3, 7)    # 7
"""

import math
import random
from builtins import abs as _builtin_abs
from builtins import max as _builtin_max
from builtins import min as _builtin_min
from types import SimpleNamespace

# --- Konstanta ---

pi = math.pi
e = math.e

# --- Fungsi cepat ---


def sqr(x: float) -> float:
    """Akar kuadrat (alias akar)."""
    return math.sqrt(x)


def abs(x: float) -> float:
    """Nilai absolut."""
    return _builtin_abs(x)


def min(*nilai) -> float:
    """Nilai minimum dari 2+ angka, atau dari satu list/objek."""
    if len(nilai) == 1:
        return _builtin_min(nilai[0])
    return _builtin_min(nilai)


def max(*nilai) -> float:
    """Nilai maksimum dari 2+ angka, atau dari satu list/objek."""
    if len(nilai) == 1:
        return _builtin_max(nilai[0])
    return _builtin_max(nilai)


def akar(x: float) -> float:
    """Akar kuadrat (alias sqr)."""
    return math.sqrt(x)


def pangkat(x: float, y: float) -> float:
    """x pangkat y."""
    return math.pow(x, y)


def lantai(x: float) -> int:
    """Floor — pembulatan ke bawah."""
    return math.floor(x)


def langit(x: float) -> int:
    """Ceil — pembulatan ke atas."""
    return math.ceil(x)


def bulat(x: float, n: int = 0) -> float:
    """Pembulatan ke n digit desimal."""
    return round(x, n)


def log(x: float, base: float = math.e) -> float:
    """Logaritma dengan basis tertentu."""
    return math.log(x, base)


def sin(x: float) -> float:
    """Sinus (radian)."""
    return math.sin(x)


def cos(x: float) -> float:
    """Cosinus (radian)."""
    return math.cos(x)


def tan(x: float) -> float:
    """Tangen (radian)."""
    return math.tan(x)


def faktorial(n: int) -> int:
    """Faktorial dari n."""
    return math.factorial(int(n))


def acak_antara(a: float, b: float) -> float:
    """Angka acak antara a dan b."""
    return random.uniform(a, b)


module = SimpleNamespace(
    pi=pi,
    e=e,
    sqr=sqr,
    abs=abs,
    min=min,
    max=max,
    akar=akar,
    pangkat=pangkat,
    lantai=lantai,
    langit=langit,
    bulat=bulat,
    log=log,
    sin=sin,
    cos=cos,
    tan=tan,
    faktorial=faktorial,
    acak_antara=acak_antara,
)
