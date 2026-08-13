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
from typing import List

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


# ============= v7.1: teori bilangan =============


def genap(n: int) -> bool:
    """Cek apakah bilangan genap."""
    return int(n) % 2 == 0


def ganjil(n: int) -> bool:
    """Cek apakah bilangan ganjil."""
    return int(n) % 2 == 1


def fpb(a: int, b: int) -> int:
    """Faktor persekutuan terbesar (GCD)."""
    return math.gcd(int(a), int(b))


def kpk(a: int, b: int) -> int:
    """Kelipatan persekutuan terkecil (LCM)."""
    a, b = int(a), int(b)
    return abs(a * b) // math.gcd(a, b) if a and b else 0


def prima(n: int) -> bool:
    """Cek apakah n bilangan prima."""
    n = int(n)
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(math.isqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True


def angka_prima(n: int) -> List[int]:
    """Daftar semua bilangan prima <= n."""
    n = int(n)
    if n < 2:
        return []
    saringan = [True] * (n + 1)
    saringan[0] = saringan[1] = False
    for i in range(2, int(math.isqrt(n)) + 1):
        if saringan[i]:
            for j in range(i * i, n + 1, i):
                saringan[j] = False
    return [i for i, is_prima in enumerate(saringan) if is_prima]


def fibonacci(n: int) -> int:
    """Bilangan Fibonacci ke-n (fibonacci(0)=0, fibonacci(1)=1)."""
    n = int(n)
    if n < 0:
        raise ValueError("n tidak boleh negatif.")
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def digit(n: int) -> List[int]:
    """Daftar digit penyusun bilangan: digit(1234) -> [1, 2, 3, 4]."""
    return [int(d) for d in str(abs(int(n)))]


def jumlah_digit(n: int) -> int:
    """Jumlah semua digit: jumlah_digit(1234) -> 10."""
    return sum(digit(n))


def terbalik(n: int) -> int:
    """Bilangan dengan digit dibalik: terbalik(1234) -> 4321."""
    tanda = -1 if int(n) < 0 else 1
    return tanda * int(str(abs(int(n)))[::-1])


# ============= v7.1: konversi basis =============


def ke_biner(n: int) -> str:
    """Konversi bilangan ke biner (tanpa prefix): ke_biner(10) -> "1010"."""
    return bin(int(n))[2:]


def dari_biner(s: str) -> int:
    """Konversi string biner ke bilangan: dari_biner("1010") -> 10."""
    return int(s, 2)


def ke_oktal(n: int) -> str:
    """Konversi bilangan ke oktal (tanpa prefix): ke_oktal(8) -> "10"."""
    return oct(int(n))[2:]


def dari_oktal(s: str) -> int:
    """Konversi string oktal ke bilangan: dari_oktal("10") -> 8."""
    return int(s, 8)


def ke_heksa(n: int) -> str:
    """Konversi bilangan ke heksadesimal (tanpa prefix): ke_heksa(255) -> "ff"."""
    return hex(int(n))[2:]


def dari_heksa(s: str) -> int:
    """Konversi string heksadesimal ke bilangan: dari_heksa("ff") -> 255."""
    return int(s, 16)


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
    # v7.1: teori bilangan
    genap=genap,
    ganjil=ganjil,
    fpb=fpb,
    kpk=kpk,
    prima=prima,
    angka_prima=angka_prima,
    fibonacci=fibonacci,
    digit=digit,
    jumlah_digit=jumlah_digit,
    terbalik=terbalik,
    # v7.1: konversi basis
    ke_biner=ke_biner,
    dari_biner=dari_biner,
    ke_oktal=ke_oktal,
    dari_oktal=dari_oktal,
    ke_heksa=ke_heksa,
    dari_heksa=dari_heksa,
)
