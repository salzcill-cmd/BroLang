"""
Modul CSV BroLang (v6.0)
========================

Membaca & menulis file CSV dengan mudah — termasuk header otomatis
dan konversi ke objek.

Contoh:
    impor csv

    buat data = csv.baca("data.csv")       # list objek: [{"nama": ..., ...}]
    csv.tulis("keluar.csv", data)          # tulis list objek
"""

import csv as _csv
import os
from types import SimpleNamespace


def baca(path: str, delimiter: str = ",") -> list:
    """Baca file CSV menjadi list objek (baris pertama = header)."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"File CSV tidak ditemukan: {path}")
    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = _csv.DictReader(f, delimiter=delimiter)
        rows = []
        for row in reader:
            rows.append(dict(row))
        return rows


def baca_list(path: str, delimiter: str = ",") -> list:
    """Baca file CSV sebagai list of list (tanpa interpretasi header)."""
    with open(path, "r", encoding="utf-8", newline="") as f:
        return list(_csv.reader(f, delimiter=delimiter))


def tulis(path: str, data: list, kolom: list = None) -> int:
    """Tulis list objek ke file CSV. Kembalikan jumlah baris.

    Contoh:
        csv.tulis("out.csv", [
            {"nama": "Budi", "umur": 20},
            {"nama": "Ani", "umur": 25},
        ])
    """
    if not data:
        raise ValueError("Data kosong — tidak bisa menulis CSV tanpa baris.")
    first = data[0]
    if isinstance(first, dict):
        kolom = kolom or list(first.keys())
        with open(path, "w", encoding="utf-8", newline="") as f:
            writer = _csv.DictWriter(f, fieldnames=kolom)
            writer.writeheader()
            for row in data:
                writer.writerow(row)
    else:
        with open(path, "w", encoding="utf-8", newline="") as f:
            writer = _csv.writer(f)
            for row in data:
                writer.writerow(row)
    return len(data)


def tulis_baris(path: str, baris: list, delimiter: str = ",") -> None:
    """Tulis satu baris ke file CSV (append)."""
    with open(path, "a", encoding="utf-8", newline="") as f:
        writer = _csv.writer(f, delimiter=delimiter)
        writer.writerow(baris)


def kolom(path: str, nama_kolom: str, delimiter: str = ",") -> list:
    """Ambil satu kolom dari CSV (list nilai)."""
    rows = baca(path, delimiter)
    if not rows:
        return []
    return [r.get(nama_kolom) for r in rows if nama_kolom in r]


module = SimpleNamespace(
    baca=baca,
    baca_list=baca_list,
    tulis=tulis,
    tulis_baris=tulis_baris,
    kolom=kolom,
)
