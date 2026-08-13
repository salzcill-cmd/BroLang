"""
Modul Matematika BroLang
========================

Fungsi matematika dasar dan lanjutan.

Contoh:
    impor matematika
    matematika.akar(25)
    matematika.sin(3.14)
    matematika.rata_rata([1, 2, 3, 4, 5])   # 3.0
    matematika.fpb(12, 18)                  # 6
"""

import math
import statistics
from types import SimpleNamespace
from typing import List


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


def log2(x: float) -> float:
    """Logaritma basis 2."""
    return math.log2(x)


def log10(x: float) -> float:
    """Logaritma basis 10."""
    return math.log10(x)


def pi() -> float:
    """Nilai pi (3.14159...)."""
    return math.pi


def e() -> float:
    """Nilai e (2.71828...)."""
    return math.e


def max_(a: float, b: float) -> float:
    """Nilai maksimum dua bilangan."""
    return max(a, b)


def min_(a: float, b: float) -> float:
    """Nilai minimum dua bilangan."""
    return min(a, b)


def maksimal(*nilai) -> float:
    """Nilai terbesar dari banyak argumen: maksimal(3, 9, 5) -> 9."""
    return max(nilai)


def minimal(*nilai) -> float:
    """Nilai terkecil dari banyak argumen: minimal(3, 9, 5) -> 3."""
    return min(nilai)


def faktorial(n: int) -> int:
    """Faktorial dari n."""
    return math.factorial(n)


# ============= v7.1: Statistik =============


def rata_rata(data: List[float]) -> float:
    """Rata-rata (mean) dari list angka."""
    return statistics.mean(data)


def median(data: List[float]) -> float:
    """Median dari list angka."""
    return statistics.median(data)


def modus(data: List[float]):
    """Modus — nilai yang paling sering muncul."""
    return statistics.mode(data)


def varians(data: List[float]) -> float:
    """Varians populasi dari list angka."""
    return statistics.pvariance(data)


def standar_deviasi(data: List[float]) -> float:
    """Standar deviasi populasi dari list angka."""
    return statistics.pstdev(data)


# ============= v7.1: Teori Bilangan =============


def fpb(a: int, b: int) -> int:
    """Faktor persekutuan terbesar (GCD)."""
    return math.gcd(a, b)


def kpk(a: int, b: int) -> int:
    """Kelipatan persekutuan terkecil (LCM)."""
    return abs(a * b) // math.gcd(a, b) if a and b else 0


def prima(n: int) -> bool:
    """Cek apakah n bilangan prima."""
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


def bilangan_prima(n: int) -> List[int]:
    """Daftar semua bilangan prima <= n (sieve of Eratosthenes)."""
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
    if n < 0:
        raise ValueError("n tidak boleh negatif.")
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


# ============= v7.1: Utilitas =============


def clamp(x: float, bawah: float, atas: float) -> float:
    """Kunci nilai x ke rentang [bawah, atas]."""
    return max(bawah, min(atas, x))


def hipotenusa(a: float, b: float) -> float:
    """Sisi miring segitiga siku-siku (teorema Pythagoras)."""
    return math.hypot(a, b)


def derajat_ke_radian(x: float) -> float:
    """Konversi derajat ke radian."""
    return math.radians(x)


def radian_ke_derajat(x: float) -> float:
    """Konversi radian ke derajat."""
    return math.degrees(x)


def kombinasi(n: int, r: int) -> int:
    """Kombinasi C(n, r) — cara memilih r dari n tanpa urutan."""
    return math.comb(n, r)


def permutasi(n: int, r: int) -> int:
    """Permutasi P(n, r) — cara memilih r dari n dengan urutan."""
    return math.perm(n, r)


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
    log2=log2,
    log10=log10,
    pi=pi,
    e=e,
    max=max_,
    min=min_,
    maksimal=maksimal,
    minimal=minimal,
    faktorial=faktorial,
    # v7.1: statistik
    rata_rata=rata_rata,
    median=median,
    modus=modus,
    varians=varians,
    standar_deviasi=standar_deviasi,
    # v7.1: teori bilangan
    fpb=fpb,
    kpk=kpk,
    prima=prima,
    bilangan_prima=bilangan_prima,
    fibonacci=fibonacci,
    # v7.1: utilitas
    clamp=clamp,
    hipotenusa=hipotenusa,
    derajat_ke_radian=derajat_ke_radian,
    radian_ke_derajat=radian_ke_derajat,
    kombinasi=kombinasi,
    permutasi=permutasi,
)
