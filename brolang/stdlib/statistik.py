"""
Modul Statistik untuk BroLang
==============================

Fungsi-fungsi statistik dasar: rerata, median, modus, varians, simpangan baku.

Contoh:
    impor statistik
    buat data = [10, 20, 30, 40, 50]
    tulis statistik.rerata(data)          # 30
    tulis statistik.median(data)          # 30
    tulis statistik.modus([1, 1, 2, 3])   # 1
    tulis statistik.varians(data)         # 200
    tulis statistik.simpangan_baku(data)  # 14.142...
    tulis statistik.kuartil(data, 1)      # 20
    tulis statistik.persentil(data, 50)   # 30
    tulis statistik.korelasi([1,2,3], [2,4,6])  # 1.0
"""

import math
from collections import Counter


def rerata(data):
    """Rerata (mean) dari list angka."""
    if not data:
        return 0
    return sum(data) / len(data)


def median(data):
    """Median (nilai tengah) dari list angka."""
    if not data:
        return 0
    s = sorted(data)
    n = len(s)
    mid = n // 2
    if n % 2 == 0:
        return (s[mid - 1] + s[mid]) / 2
    return s[mid]


def modus(data):
    """Modus (nilai yang paling sering muncul). Mengembalikan list karena bisa lebih dari satu."""
    if not data:
        return []
    counter = Counter(data)
    max_count = max(counter.values())
    modes = [val for val, count in counter.items() if count == max_count]
    if len(modes) == len(data):
        return []  # semua nilai unik, tidak ada modus
    return sorted(modes)


def modus_satu(data):
    """Modus tunggal — mengembalikan satu nilai saja (yang pertama ditemukan)."""
    modes = modus(data)
    return modes[0] if modes else None


def variance(data, population=True):
    """Varians dari list angka.
    
    population=True → varian populasi (bagi N)
    population=False → varian sampel (bagi N-1)
    """
    if len(data) < 2:
        return 0
    avg = rerata(data)
    sq_diff = [(x - avg) ** 2 for x in data]
    n = len(data) if population else len(data) - 1
    return sum(sq_diff) / n


def simpangan_baku(data, population=True):
    """Simpangan baku (standard deviation)."""
    return math.sqrt(variance(data, population))


def kuartil(data, q):
    """Kuartil data (q=1, 2, atau 3).
    
    q=1 → Q1 (25th percentile)
    q=2 → Q2 = median
    q=3 → Q3 (75th percentile)
    """
    if not data:
        return 0
    s = sorted(data)
    n = len(s)
    pos = q * (n - 1) / 4
    low = int(pos)
    frac = pos - low
    if low + 1 < n:
        return s[low] + frac * (s[low + 1] - s[low])
    return s[low]


def persentil(data, p):
    """Persentil dari data (0-100)."""
    if not data:
        return 0
    s = sorted(data)
    n = len(s)
    pos = p * (n - 1) / 100
    low = int(pos)
    frac = pos - low
    if low + 1 < n:
        return s[low] + frac * (s[low + 1] - s[low])
    return s[low]


def korelasi(x_data, y_data):
    """Korelasi Pearson antara dua list angka (-1 sampai 1)."""
    if len(x_data) != len(y_data) or len(x_data) < 2:
        return 0
    n = len(x_data)
    avg_x = rerata(x_data)
    avg_y = rerata(y_data)
    
    cov = sum((x - avg_x) * (y - avg_y) for x, y in zip(x_data, y_data))
    std_x = math.sqrt(sum((x - avg_x) ** 2 for x in x_data))
    std_y = math.sqrt(sum((y - avg_y) ** 2 for y in y_data))
    
    if std_x == 0 or std_y == 0:
        return 0
    return cov / (std_x * std_y)


def rank(data, value):
    """Rank/peringkat sebuah nilai dalam data (dari terkecil, dimulai 1)."""
    s = sorted(data)
    for i, v in enumerate(s):
        if v == value:
            return i + 1
    return 0


def ringkasan(data):
    """Ringkasan statistik lengkap: min, max, rerata, median, std_dev, jumlah."""
    if not data:
        return {"min": 0, "max": 0, "rerata": 0, "median": 0, "std_dev": 0, "jumlah": 0}
    return {
        "min": min(data),
        "max": max(data),
        "rerata": rerata(data),
        "median": median(data),
        "modus": modus(data),
        "varians": variance(data),
        "simpangan_baku": simpangan_baku(data),
        "jumlah": len(data),
    }
