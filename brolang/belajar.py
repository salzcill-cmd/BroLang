"""
Mode Belajar BroLang (v12.3 — Sistem Belajar Canggih & Adaptif)
================================================================

Tutorial interaktif di terminal untuk pemula & pelajar Indonesia.
Jalankan dengan:
    bro belajar          # jalur belajar terstruktur (bab demi bab)
    bro belajar --ulang  # mode ulangan (spaced repetition) konsep lemah
    bro belajar <konsep> # latihan mandiri satu konsep (contoh: variabel)

Fitur canggih v12.3:
- Penyimpanan progres ke ~/.brolang/belajar_progress.json (lanjutkan kapan saja)
- Pelacakan keahlian per-konsep (0 = baru ... 3 = ahli) bukan hanya per-bab
- Mode ulangan (spaced repetition): konsep yang belum mahir ditampilkan ulang
  dengan jeda yang semakin panjang (1 menit, 10 menit, 1 jam, 1 hari)
- Petunjuk adaptif bertingkat (level 0: samar → level 3: jelas) menyesuaikan
  dengan banyaknya percobaan salah
- Deteksi pola kesalahan umum dengan umpan balik spesifik (contoh: `print(`
  malah maksudnya `tulis(`, lupa `selesai`, pakai `=` untuk bandingkan)
- Umpan balik kualitas kode (lint ringan): variabel tidak terpakai, dll.
- Mode latihan mandiri: coba konsep bebas tanpa tekanan poin
- Buka kunci bab: tidak bisa lompat ke bab lanjutan sebelum bab sebelumnya
  selesai (mencegah kesenjangan pemahaman)

Struktur tiap bab:
  - materi singkat + contoh
  - soal dengan tag konsep & petunjuk bertingkat
  - jawaban dicek otomatis dengan interpreter (batas waktu 5 detik)

Contoh pemakaian programatik:
    from brolang.belajar import cek_jawaban, BAB
    status, detail = cek_jawaban('tulis "Halo Dunia!"', BAB[0]["soal"][0])
    # status: "benar" | "salah" | "error"
"""

import io
import json
import os
import random
import re
import threading
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from brolang.lexer import Lexer
from brolang.parser import Parser
from brolang.interpreter import Interpreter
from brolang import __version__

# ============= Konfigurasi =============

_TIME_OUT_DETIK = 5.0
_PROGRESS_FILE = os.path.join(
    os.path.expanduser("~"), ".brolang", "belajar_progress.json")
_LEVEL_NAMA = {0: "baru", 1: "belajar", 2: "mahir", 3: "ahli"}
_ICON_LEVEL = {0: "🆕", 1: "📚", 2: "⭐", 3: "👑"}

# Jeda spaced repetition (detik) menurut level keahlian — semakin mahir,
# jarak review semakin lama.
_REVIEW_JEDA_DETIK = {
    0: 60,        # 1 menit
    1: 600,       # 10 menit
    2: 3600,      # 1 jam
    3: 86400,     # 1 hari
}

# Batas waktu jeda antar review agar tidak menumpuk terlalu banyak.
_MAX_REVIEW_PER_SESI = 8


# ============= Pola Kesalahan Umum =============
# Setiap entri: (nama, regex, pesan_feedback, contoh_perbaikan, poin_dikurangi)
_POLA_KESALAHAN: List[Tuple[str, re.Pattern, str, str, int]] = [
    (
        "keyword_print",
        re.compile(r"\bprint\s*\("),
        "Kamu mengetik `print(` (Bahasa Inggris/Python). Di BroLang pakai `tulis(`.",
        "tulis(\"Halo\")",
        2,
    ),
    (
        "keyword_if",
        re.compile(r"\bif\s*\("),
        "Kamu mengetik `if (` (Bahasa Inggris). Di BroLang pakai `jika ... maka`.",
        "jika 5 > 3 maka",
        2,
    ),
    (
        "keyword_else",
        re.compile(r"\belse\b"),
        "Kamu mengetik `else` (Bahasa Inggris). Di BroLang pakai `lainnya`.",
        "lainnya",
        2,
    ),
    (
        "keyword_elif",
        re.compile(r"\belif\b"),
        "Kamu mengetik `elif` (Bahasa Inggris). Di BroLang pakai `lainnya jika`.",
        "lainnya jika",
        2,
    ),
    (
        "keyword_def",
        re.compile(r"\bdef\s+"),
        "Kamu mengetik `def` (Bahasa Inggris). Di BroLang pakai `fungsi`.",
        "fungsi sapa(nama)",
        2,
    ),
    (
        "keyword_for",
        re.compile(r"\bfor\s+"),
        "Kamu mengetik `for` (Bahasa Inggris). Di BroLang pakai `untuk ... dalam`.",
        "untuk i dalam range(5) lakukan",
        2,
    ),
    (
        "keyword_while",
        re.compile(r"\bwhile\s+"),
        "Kamu mengetik `while` (Bahasa Inggris). Di BroLang pakai `selama ... lakukan`.",
        "selama i > 0 lakukan",
        2,
    ),
    (
        "keyword_return",
        re.compile(r"\breturn\b"),
        "Kamu mengetik `return` (Bahasa Inggris). Di BroLang pakai `kembali`.",
        "kembali x * 2",
        2,
    ),
    (
        "keyword_end",
        re.compile(r"\bend\b"),
        "Kamu mengetik `end` (Bahasa Inggris). Di BroLang pakai `selesai`.",
        "selesai",
        2,
    ),
    (
        "keyword_range",
        re.compile(r"\brange\b"),
        "Kamu mengetik `range` (Bahasa Inggris). Di BroLang pakai `range` juga, "
        "tapi pola: `untuk i dalam range(5) lakukan`.",
        "untuk i dalam range(5) lakukan",
        1,
    ),
    (
        "assignment_semicolon",
        re.compile(r";\s*$"),
        "Jangan akhiri baris dengan titik koma `;` — BroLang tidak memerlukannya.",
        "tulis \"Halo\"",
        1,
    ),
    (
        "assign_vs_compare",
        re.compile(r"jika\s+\w+\s*=\s*\d"),
        "Di dalam `jika`, gunakan `==` untuk bandingkan, bukan `=` (yang itu untuk buat variabel).",
        "jika nilai == 80 maka",
        3,
    ),
    (
        "missing_selesai",
        re.compile(r"jika\b"),
        "Ingat: setiap blok `jika ... maka` harus ditutup dengan `selesai`.",
        "jika x > 5 maka\n    tulis \"besar\"\nselesai",
        2,
    ),
    (
        "missing_selesai_fungsi",
        re.compile(r"fungsi\b"),
        "Ingat: setiap blok `fungsi` harus ditutup dengan `selesai`.",
        "fungsi kali2(x)\n    kembali x * 2\nselesai",
        2,
    ),
]


def _deteksi_pola_kesalahan(kode: str) -> List[Tuple[str, str, str, int]]:
    """Cari pola kesalahan umum dalam kode siswa.
    Return list of (nama, pesan, contoh, poin_dikurangi).
    """
    ditemukan: List[Tuple[str, str, str, int]] = []
    for nama, regex, pesan, contoh, poin in _POLA_KESALAHAN:
        if regex.search(kode):
            ditemukan.append((nama, pesan, contoh, poin))
    return ditemukan


# ============= Manajemen Progres =============

def _baca_progres() -> Dict[str, Any]:
    """Baca progres belajar dari berkas JSON. Kembali dict kosong kalau belum ada."""
    if not os.path.exists(_PROGRESS_FILE):
        return {"versi": 1}
    try:
        with open(_PROGRESS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return {"versi": 1}
        return data
    except (json.JSONDecodeError, OSError):
        return {"versi": 1}


def _simpan_progres(progres: Dict[str, Any]) -> None:
    """Simpan progres belajar ke berkas JSON."""
    try:
        os.makedirs(os.path.dirname(_PROGRESS_FILE), exist_ok=True)
        with open(_PROGRESS_FILE, "w", encoding="utf-8") as f:
            json.dump(progres, f, indent=2, ensure_ascii=False)
    except OSError:
        pass  # gagal simpan tidak boleh menghentikan sesi belajar


def _konsep_progres(progres: Dict[str, Any], konsep_id: str) -> Dict[str, Any]:
    """Ambil atau buat entri progres untuk satu konsep."""
    konsep = progres.setdefault("konsep", {})
    entri = konsep.get(konsep_id)
    if entri is None:
        entri = {
            "level": 0,
            "attempts": 0,
            "benar": 0,
            "salah": 0,
            "next_review": None,
            "terakhir_diupai": None,
        }
        konsep[konsep_id] = entri
    return entri


def _perbarui_konsep(
    progres: Dict[str, Any],
    konsep_id: str,
    benar: bool,
) -> Tuple[int, str]:
    """Perbarui level keahlian konsep setelah satu percobaan.

    Return (level_baru, pesan_feedback).
    """
    entri = _konsep_progres(progres, konsep_id)
    entri["attempts"] += 1
    if benar:
        entri["benar"] += 1
    else:
        entri["salah"] += 1
    entri["terakhir_diupai"] = datetime.now().isoformat()

    # Hitung rasio keberhasilan (minimal 3 percobaan sebelum naik level)
    attempts = entri["attempts"]
    benar_count = entri["benar"]
    rasio = benar_count / attempts if attempts else 0.0

    level_lama = entri["level"]
    level_baru = level_lama
    if attempts >= 3 and rasio >= 0.8 and level_lama < 3:
        level_baru = min(3, level_lama + 1)
    elif attempts >= 5 and rasio < 0.4 and level_lama > 0:
        level_baru = max(0, level_lama - 1)

    entri["level"] = level_baru

    # Jadwalkan review berikutnya (spaced repetition)
    jeda = _REVIEW_JEDA_DETIK.get(level_baru, 60)
    entri["next_review"] = (datetime.now() + timedelta(seconds=jeda)).isoformat()

    progres["total_nilai"] = progres.get("total_nilai", 0)  # diisi pemanggil
    return level_baru, _LEVEL_NAMA[level_baru]


# ============= Kurikulum =============
# Setiap soal sekarang memiliki "konsep" (id konsep yang diuji) dan
# "petunjuk" yang adalah LIST bertingkat (level 0 samar, level 3 jelas).

BAB: List[Dict[str, Any]] = [
    {
        "judul": "Halo Dunia",
        "ikon": "🖨️",
        "konsep_utama": "tulis",
        "materi": """Program pertama! Kata kunci `tulis` mencetak sesuatu ke layar.

    tulis "Halo Dunia!"      # Halo Dunia!
    tulis 2 + 3              # 5
    tulis "A", "B"           # A B

Teks ditulis di dalam tanda kutip "..." — angka tidak perlu kutip.""",
        "soal": [
            {
                "teks": 'Cetak kalimat "Halo Dunia!" ke layar.',
                "konsep": "tulis",
                "cek": "tepat",
                "harapan": ["Halo Dunia!"],
                "petunjuk": [
                    "Gunakan kata kunci `tulis` diikuti teks dalam tanda kutip.",
                    "Pola: tulis \"...\"  (contoh: tulis \"Halo Dunia!\")",
                    "Jawaban lengkap: tulis \"Halo Dunia!\"",
                ],
                "solusi": 'tulis "Halo Dunia!"',
                "poin": 10,
            },
            {
                "teks": 'Cetak "Halo, saya Budi!" (ganti Budi dengan nama kamu).',
                "konsep": "tulis",
                "cek": "mengandung",
                "harapan": ["Halo, saya"],
                "petunjuk": [
                    "Pola: tulis \"Halo, saya ...\" — nama di dalam tanda kutip.",
                    'Contoh: tulis "Halo, saya Budi!"',
                ],
                "solusi": 'tulis "Halo, saya Budi!"',
                "poin": 10,
            },
        ],
    },
    {
        "judul": "Variabel",
        "ikon": "📦",
        "konsep_utama": "variabel",
        "materi": """Variabel menyimpan nilai supaya bisa dipakai ulang. Pakai `buat`:

    buat nama = "Budi"       # variabel teks
    buat umur = 17           # variabel angka
    tulis nama               # Budi
    tulis umur               # 17

Isi variabel bisa digabung dengan tanda +.""",
        "soal": [
            {
                "teks": "Buat variabel `umur` berisi 17, lalu cetak isinya.",
                "konsep": "variabel",
                "cek": "tepat",
                "harapan": ["17"],
                "petunjuk": [
                    "Pertama buat variabel: buat umur = 17",
                    "Kemudian cetak isinya: tulis umur",
                    "Gabungkan: buat umur = 17 \\n tulis umur",
                ],
                "solusi": "buat umur = 17\ntulis umur",
                "poin": 10,
            },
            {
                "teks": 'Buat variabel `nama` = "Ani" dan `kota` = "Jakarta", lalu cetak "Ani tinggal di Jakarta".',
                "konsep": "variabel",
                "cek": "mengandung",
                "harapan": ["tinggal di"],
                "petunjuk": [
                    "Buat dua variabel, lalu gabungkan dengan tanda +.",
                    'Pola: tulis nama + " tinggal di " + kota',
                ],
                "solusi": 'buat nama = "Ani"\nbuat kota = "Jakarta"\ntulis nama + " tinggal di " + kota',
                "poin": 10,
            },
        ],
    },
    {
        "judul": "Operasi Matematika",
        "ikon": "➕",
        "konsep_utama": "operator",
        "materi": """Operator matematika:
    + tambah      - kurang      * kali
    / bagi        % sisa bagi   ** pangkat

    tulis 10 + 5        # 15
    tulis 7 * 6         # 42
    tulis 17 % 5        # 2
    tulis 2 ** 3        # 8

Perkalian & pembagian dikerjakan lebih dulu (seperti matematika biasa).""",
        "soal": [
            {
                "teks": "Cetak hasil dari 10 + 5 * 2 (perkalian dulu!).",
                "konsep": "operator",
                "cek": "tepat",
                "harapan": ["20"],
                "petunjuk": [
                    "Perkalian dulu baru penjumlahan: 5 * 2 = 10, lalu 10 + 10 = 20.",
                    "Ketik: tulis 10 + 5 * 2",
                ],
                "solusi": "tulis 10 + 5 * 2",
                "poin": 10,
            },
            {
                "teks": "Cetak hasil dari (10 + 5) * 2 (kurung dulu!).",
                "konsep": "operator",
                "cek": "tepat",
                "harapan": ["30"],
                "petunjuk": [
                    "Kurung dulu: (10 + 5) = 15, lalu 15 * 2 = 30.",
                    "Ketik: tulis (10 + 5) * 2",
                ],
                "solusi": "tulis (10 + 5) * 2",
                "poin": 10,
            },
            {
                "teks": "Cetak sisa bagi 17 dibagi 5 (operator %).",
                "konsep": "operator",
                "cek": "tepat",
                "harapan": ["2"],
                "petunjuk": [
                    "17 : 5 = 3 sisa 2. Pakai operator %.",
                    "Ketik: tulis 17 % 5",
                ],
                "solusi": "tulis 17 % 5",
                "poin": 10,
            },
        ],
    },
    {
        "judul": "Percabangan",
        "ikon": "🌿",
        "konsep_utama": "percabangan",
        "materi": """`jika` menjalankan kode hanya kalau kondisinya benar:

    jika 5 > 3 maka
        tulis "besar"
    selesai            # cetak: besar

Perbandingan: == sama, != tidak sama, > lebih besar, < lebih kecil.

Percabangan dua arah dengan `lainnya`:

    jika nilai >= 75 maka
        tulis "LULUS"
    lainnya
        tulis "TIDAK LULUS"
    selesai

Catatan: untuk membandingkan pakai == (dua tanda sama), bukan =.""",
        "soal": [
            {
                "teks": 'Cetak "besar" jika 5 lebih besar dari 3.',
                "konsep": "percabangan",
                "cek": "tepat",
                "harapan": ["besar"],
                "petunjuk": [
                    "Pola: jika 5 > 3 maka ... selesai",
                    "Jangan lupa tutup blok dengan `selesai` di akhir.",
                ],
                "solusi": 'jika 5 > 3 maka\n    tulis "besar"\nselesai',
                "poin": 10,
            },
            {
                "teks": 'Buat variabel `nilai` = 80. Cetak "LULUS" jika nilai >= 75, selain itu cetak "TIDAK LULUS".',
                "konsep": "percabangan",
                "cek": "tepat",
                "harapan": ["LULUS"],
                "petunjuk": [
                    "Gunakan jika ... maka ... lainnya ... selesai",
                    "Bandingkan dengan >= (dua tanda sama lebih garis bawah).",
                ],
                "solusi": 'buat nilai = 80\njika nilai >= 75 maka\n    tulis "LULUS"\nlainnya\n    tulis "TIDAK LULUS"\nselesai',
                "poin": 10,
            },
        ],
    },
    {
        "judul": "Perulangan",
        "ikon": "🔁",
        "konsep_utama": "perulangan",
        "materi": """Perulangan `untuk` memproses tiap angka:

    untuk i dalam range(5) lakukan
        tulis i
    selesai       # mencetak 0 1 2 3 4 (tiap angka baris sendiri)

range(n) menghasilkan angka 0 sampai n-1.

`selama` mengulang selama kondisi masih benar:

    buat i = 3
    selama i > 0 lakukan
        tulis i
        i = i - 1
    selesai       # 3 2 1""",
        "soal": [
            {
                "teks": "Cetak angka 0 sampai 4 pakai `untuk` dan range(5).",
                "konsep": "perulangan",
                "cek": "tepat",
                "harapan": ["0", "1", "2", "3", "4"],
                "petunjuk": [
                    "Pola: untuk i dalam range(5) lakukan ... selesai",
                    "Di dalam blok: tulis i",
                ],
                "solusi": "untuk i dalam range(5) lakukan\n    tulis i\nselesai",
                "poin": 10,
            },
            {
                "teks": "Hitung mundur dari 5 ke 1 pakai `selama`.",
                "konsep": "perulangan",
                "cek": "tepat",
                "harapan": ["5", "4", "3", "2", "1"],
                "petunjuk": [
                    "buat i = 5, lalu selama i > 0 lakukan: tulis i lalu i = i - 1",
                    "Jangan lupa `selesai` di akhir blok.",
                ],
                "solusi": "buat i = 5\nselama i > 0 lakukan\n    tulis i\n    i = i - 1\nselesai",
                "poin": 10,
            },
        ],
    },
    {
        "judul": "List",
        "ikon": "📋",
        "konsep_utama": "list",
        "materi": """List menyimpan banyak nilai sekaligus. Indeks dimulai dari 0:

    buat buah = ["apel", "mangga", "jeruk"]
    tulis buah[0]             # apel
    tulis buah[1]             # mangga

    buah.tambah("pisang")     # tambah ke belakang
    tulis buah.panjang()      # 4

Untuk memproses tiap isi list, pakai `untuk ... dalam ...`.""",
        "soal": [
            {
                "teks": 'Buat list ["apel", "mangga"], lalu cetak isi pada index ke-1.',
                "konsep": "list",
                "cek": "tepat",
                "harapan": ["mangga"],
                "petunjuk": [
                    "Indeks dimulai dari 0: buah[0] = apel, buah[1] = mangga",
                    'Pola: buat buah = ["apel", "mangga"] \\n tulis buah[1]',
                ],
                "solusi": 'buat buah = ["apel", "mangga"]\ntulis buah[1]',
                "poin": 10,
            },
            {
                "teks": 'Buat list ["apel", "mangga", "jeruk"], lalu cetak semua buah satu per satu.',
                "konsep": "list",
                "cek": "tepat",
                "harapan": ["apel", "mangga", "jeruk"],
                "petunjuk": [
                    "Gunakan untuk item dalam buah lakukan ... selesai",
                    "Di dalam blok: tulis item",
                ],
                "solusi": 'buat buah = ["apel", "mangga", "jeruk"]\nuntuk item dalam buah lakukan\n    tulis item\nselesai',
                "poin": 10,
            },
        ],
    },
    {
        "judul": "Fungsi",
        "ikon": "🧩",
        "konsep_utama": "fungsi",
        "materi": """Fungsi mengelompokkan kode yang dipakai berulang-ulang:

    fungsi kali2(x)
        kembali x * 2
    selesai

    tulis kali2(21)      # 42

`kembali` mengirim hasil keluar dari fungsi. Fungsi dipanggil dengan
nama + tanda kurung.""",
        "soal": [
            {
                "teks": "Buat fungsi kali2(x) yang mengembalikan x * 2, lalu cetak kali2(21).",
                "konsep": "fungsi",
                "cek": "tepat",
                "harapan": ["42"],
                "petunjuk": [
                    "Pola: fungsi kali2(x) \\n    kembali x * 2 \\n selesai",
                    "Lalu panggil: tulis kali2(21)",
                ],
                "solusi": "fungsi kali2(x)\n    kembali x * 2\nselesai\ntulis kali2(21)",
                "poin": 10,
            },
            {
                "teks": 'Buat fungsi sapa(nama) yang mengembalikan "Halo " + nama, lalu cetak sapa("Budi").',
                "konsep": "fungsi",
                "cek": "tepat",
                "harapan": ["Halo Budi"],
                "petunjuk": [
                    'Pola: fungsi sapa(nama) \\n    kembali "Halo " + nama \\n selesai',
                    "Lalu: tulis sapa(\"Budi\")",
                ],
                "solusi": 'fungsi sapa(nama)\n    kembali "Halo " + nama\nselesai\ntulis sapa("Budi")',
                "poin": 10,
            },
        ],
    },
    {
        "judul": "Proyek Mini: Kalkulator",
        "ikon": "🎮",
        "konsep_utama": "kalkulator",
        "materi": """Semua yang sudah dipelajari digabung: fungsi + percabangan + operator.

    fungsi hitung(a, b, op)
        jika op == "+" maka
            kembali a + b
        selesai
        jika op == "-" maka
            kembali a - b
        selesai
        kembali 0
    selesai

    tulis hitung(10, 4, "+")     # 14
    tulis hitung(10, 4, "-")     # 6

Perhatikan: fungsi bisa punya banyak `kembali`, dan `jika` bisa berada
di dalam fungsi.""",
        "soal": [
            {
                "teks": 'Buat fungsi hitung(a, b, op) untuk "+" dan "-", lalu cetak hitung(10, 4, "+") dan hitung(10, 4, "-").',
                "konsep": "kalkulator",
                "cek": "tepat",
                "harapan": ["14", "6"],
                "petunjuk": [
                    "Salin pola dari materi, lengkapi dua percabangan (+ dan -).",
                    "Akhir fungsi: kembali 0",
                    "Panggil dua kali: tulis hitung(10, 4, \"+\") dan tulis hitung(10, 4, \"-\")",
                ],
                "solusi": 'fungsi hitung(a, b, op)\n    jika op == "+" maka\n        kembali a + b\n    selesai\n    jika op == "-" maka\n        kembali a - b\n    selesai\n    kembali 0\nselesai\ntulis hitung(10, 4, "+")\ntulis hitung(10, 4, "-")',
                "poin": 20,
            },
        ],
    },
]

TOTAL_POIN = sum(soal["poin"] for bab in BAB for soal in bab["soal"])

# Urutan bab untuk pembukaan kunci (harus lulus berurutan)
_URUTAN_BAB = [bab["judul"] for bab in BAB]


# ============= Pemeriksa Jawaban =============

def cek_jawaban(kode: str, soal: Dict[str, Any], timeout: float = _TIME_OUT_DETIK) -> Tuple[str, Any]:
    """Jalankan kode jawaban dan bandingkan dengan harapan soal.

    Args:
        kode: Kode jawaban siswa.
        soal: Dict soal (kunci: cek, harapan, dst).
        timeout: Batas waktu eksekusi dalam detik (default 5.0).

    Returns:
        Tuple (status, detail):
        - ("benar", keluaran)   : jawaban tepat
        - ("salah", pesan)      : jalan tapi output tidak sesuai
        - ("error", pesan)      : error sintaks / runtime / timeout
    """
    try:
        ast = Parser(Lexer(kode).tokenize()).parse()
    except Exception as e:
        return ("error", str(e))

    interp = Interpreter()
    pesan = _jalankan_dengan_batas_waktu(interp, ast, timeout)
    if pesan is not None:
        return ("error", pesan)

    keluaran = [baris.strip() for baris in interp.output]
    tipe = soal.get("cek", "tepat")
    harapan = soal.get("harapan", [])

    if tipe == "mengandung":
        belum_ada = [h for h in harapan if not any(h in o for o in keluaran)]
        if not belum_ada:
            return ("benar", keluaran)
        return ("salah", f"Output kamu belum memuat '{belum_ada[0]}'.")

    if keluaran == harapan:
        return ("benar", keluaran)
    harapan_teks = " | ".join(harapan)
    keluaran_teks = " | ".join(keluaran) if keluaran else "(tidak ada output)"
    return ("salah", f"Output kamu: {keluaran_teks} — yang diharapkan: {harapan_teks}")


def _jalankan_dengan_batas_waktu(interp: Interpreter, ast, timeout: float) -> Optional[str]:
    """Jalankan AST di interpreter dengan batas waktu (daemon thread).

    Returns:
        None kalau selesai tanpa error, atau pesan error (str).
    """
    hasil: Dict[str, Exception] = {}

    def kerja() -> None:
        try:
            interp.interpret(ast)
        except Exception as e:
            hasil["error"] = e

    t = threading.Thread(target=kerja, daemon=True)
    t.start()
    with io.StringIO() as buf:
        import contextlib
        with contextlib.redirect_stdout(buf):
            t.join(timeout)
    if t.is_alive():
        return ("Kode berjalan terlalu lama — kemungkinan ada perulangan tak "
                "berujung. Cek kondisi perulanganmu, lalu coba lagi.")
    if "error" in hasil:
        return str(hasil["error"])
    return None


def _feedback_kualitas_kode(kode: str) -> List[str]:
    """Berikan umpan balik kualitas kode ringan (lint) pada jawaban siswa.

    Deteksi pola anti-pola sederhana tanpa perlu import linter penuh
    (agar cepat dan tidak menambahkan dependensi).
    """
    masukan: List[str] = []
    baris = kode.splitlines()
    for i, bar in enumerate(baris, 1):
        s = bar.strip()
        if not s or s.startswith("#"):
            continue
        if s.endswith(";"):
            masukan.append(f"Baris {i}: hapus titik koma `;` di akhir — tidak diperlukan BroLang.")
        # Deteksi variabel yang dibuat tapi mungkin tidak dipakai (heuristik ringan)
        m = re.match(r"buat\s+(\w+)\s*=", s)
        if m:
            nama_var = m.group(1)
            # Cari apakah nama variabel muncul lagi di baris lain
            digunakan = any(
                nama_var in b for j, b in enumerate(baris) if j != i - 1
            )
            if not digunakan:
                masukan.append(
                    f"Baris {i}: variabel `{nama_var}` dibuat tapi belum dipakai — "
                    "boleh dihapus atau dipakai di output."
                )
    return masukan


# ============= Mode Interaktif =============

_PERINTAH = """Perintah yang bisa dipakai:
  petunjuk   : bantuan untuk soal ini (bertingkat: samar → jelas)
  jawaban    : lihat solusi (tanpa poin)
  lewati     : lanjut ke soal berikutnya (tanpa poin)
  bantuan    : tampilkan daftar perintah ini
  progres    : lihat keahlian kamu per konsep
  keluar     : berhenti belajar (nilai & progres tetap dihitung)

Menjawab: ketik kode kamu, lalu tekan Enter di baris kosong untuk mengirim.
Perintah diproses langsung tanpa perlu baris kosong."""

_PERINTAH_KATA = (
    "keluar", "exit", "quit", "q",
    "bantuan", "help", "?",
    "petunjuk", "hint", "bantu",
    "jawaban", "solusi", "answer",
    "lewati", "skip", "s",
    "progres", "progress",
)


def _baca_kode(prompt: str = "  1> ") -> Optional[str]:
    """Baca kode multi-baris sampai baris kosong. Perintah langsung dikembalikan."""
    baris_list: List[str] = []
    nomor = 1
    while True:
        try:
            baris = input(prompt if nomor == 1 else f"  {nomor}> ")
        except (KeyboardInterrupt, EOFError):
            return None
        if baris.strip() == "":
            break
        if baris.strip().lower() in _PERINTAH_KATA:
            return baris
        baris_list.append(baris)
        nomor += 1
    return "\n".join(baris_list)


def _petunjuk_tingkat(soal: Dict[str, Any], level: int) -> str:
    """Ambil petunjuk pada tingkat tertentu (0 = samar, 3 = jelas)."""
    daftar = soal.get("petunjuk", [])
    if not daftar:
        return "Coba pola umum untuk topik ini, atau ketik 'jawaban'."
    idx = min(level, len(daftar) - 1)
    return daftar[idx]


def _tampilkan_progres(progres: Dict[str, Any]) -> None:
    """Tampilkan keahlian per konsep."""
    konsep = progres.get("konsep", {})
    if not konsep:
        print("Belum ada progres konsep. Mulai dengan menyelesaikan soal pertama.")
        return
    print()
    print("  📊  PROGRES KEMAHUAN KAMU")
    print("  " + "-" * 52)
    print(f"  {'Konsep':<16} {'Level':<8} {'Percobaan':<10} {'Benar':<7} {'Next Review'}")
    print("  " + "-" * 52)
    now = datetime.now()
    for nama_k, entri in sorted(konsep.items()):
        level = entri.get("level", 0)
        attempts = entri.get("attempts", 0)
        benar = entri.get("benar", 0)
        nr = entri.get("next_review")
        if nr:
            try:
                t_review = datetime.fromisoformat(nr)
                sisa = (t_review - now).total_seconds()
                if sisa <= 0:
                    review_tampil = "sekarang"
                elif sisa < 3600:
                    review_tampil = f"{int(sisa//60)} menit lagi"
                elif sisa < 86400:
                    review_tampil = f"{int(sisa//3600)} jam lagi"
                else:
                    review_tampil = f"{int(sisa//86400)} hari lagi"
            except ValueError:
                review_tampil = "?"
        else:
            review_tampil = "belum"
        print(
            f"  {_ICON_LEVEL.get(level,'?')} {nama_k:<14} "
            f"{_LEVEL_NAMA.get(level,'?'):<8} {attempts:<10} {benar:<7} {review_tampil}"
        )
    print("  " + "-" * 52)
    print(f"  Total poin : {progres.get('total_nilai', 0)}/{TOTAL_POIN}")
    print()


def _mode_latihan_mandiri(progres: Dict[str, Any], konsep_id: Optional[str]) -> int:
    """Mode latihan mandiri: coba konsep bebas tanpa tekanan poin."""
    print()
    print("=" * 56)
    print("   🏋️  LATIHAN MANDIRI")
    print("=" * 56)
    if konsep_id:
        print(f"Konsep: {konsep_id}")
        print("Ketik kode bebas. Ketik 'selesai' untuk kembali ke menu utama.")
    else:
        print("Ketik kode BroLang bebas. Ketik 'selesai' untuk kembali.")
    print()
    while True:
        try:
            baris = input("latihan> ")
        except (KeyboardInterrupt, EOFError):
            print()
            return 0
        if baris.strip().lower() in ("selesai", "keluar", "exit", "q"):
            return 0
        if not baris.strip():
            continue
        try:
            ast = Parser(Lexer(baris).tokenize()).parse()
        except Exception as e:
            print(f"  ❌ Error sintaks: {e}")
            continue
        interp = Interpreter()
        pesan = _jalankan_dengan_batas_waktu(interp, ast, 3.0)
        if pesan is not None:
            print(f"  ❌ Error: {pesan}")
            continue
        if interp.output:
            for o in interp.output:
                print(f"  => {o}")
        # Umpan balik kualitas kode ringan
        masukan = _feedback_kualitas_kode(baris)
        for m in masukan:
            print(f"  💡 {m}")
    return 0


def _mode_ulangan(progres: Dict[str, Any]) -> int:
    """Mode ulangan (spaced repetition): konsep yang sudah waktunya direview."""
    print()
    print("=" * 56)
    print("   🔄  MODE ULANGAN (Spaced Repetition)")
    print("=" * 56)
    now = datetime.now()
    konsep = progres.get("konsep", {})
    Kandidat = []
    for nama_k, entri in konsep.items():
        nr = entri.get("next_review")
        if not nr:
            continue
        try:
            t_review = datetime.fromisoformat(nr)
        except ValueError:
            continue
        if t_review <= now:
            Kandidat.append((nama_k, entri))
    if not Kandidat:
        print("Tidak ada konsep yang perlu diulang saat ini. 🎉")
        print("Kembali nanti, atau coba latihan mandiri.")
        return 0
    # Batasi jumlah review per sesi agar tidak melelahkan
    Kandidat = Kandidat[:_MAX_REVIEW_PER_SESI]
    print(f"Konsep yang waktunya direview: {len(Kandidat)}")
    for nama_k, entri in Kandidat:
        level = entri.get("level", 0)
        print(f"\n  {_ICON_LEVEL.get(level,'?')} {nama_k} (level {_LEVEL_NAMA.get(level,'?')})")
    print("\nKetik nama konsep untuk latihan, atau 'selesai' untuk kembali.")
    while True:
        try:
            pilih = input("pilih konsep> ").strip()
        except (KeyboardInterrupt, EOFError):
            print()
            return 0
        if pilih.lower() in ("selesai", "keluar", "exit", "q"):
            return 0
        if pilih not in [k for k, _ in Kandidat]:
            print("  Pilih salah satu konsep yang tercantum di atas.")
            continue
        # Latihan mandiri pada konsep yang dipilih
        _mode_latihan_mandiri(progres, pilih)
        # Setelah latihan, pertimbangkan untuk naik level jika masih wajib review
        nr = _konsep_progres(progres, pilih).get("next_review")
        if nr:
            try:
                if datetime.fromisoformat(nr) <= now:
                    print(f"\n  {pilih} masih perlu review. Latihan lagi? (y/n)")
            except ValueError:
                pass
        _simpan_progres(progres)
    return 0


def _buka_kunci_bab(index_bab: int, progres: Dict[str, Any]) -> bool:
    """Cek apakah bab pada index_bab boleh dibuka (bab sebelumnya selesai)."""
    if index_bab == 0:
        return True
    bab_selesai = progres.get("bab_selesai", 0)
    return bab_selesai >= index_bab


def mulai_belajar(mode: str = "normal", konsep: Optional[str] = None) -> int:
    """Jalankan mode belajar interaktif.

    Args:
        mode: "normal" (jalur terstruktur), "ulang" (spaced repetition),
              "latihan" (latihan mandiri).
        konsep: id konsep untuk mode latihan (opsional).

    Returns:
        Exit code.
    """
    progres = _baca_progres()

    if mode == "ulang":
        return _mode_ulangan(progres)
    if mode == "latihan":
        return _mode_latihan_mandiri(progres, konsep)

    # --- Mode normal: jalur terstruktur ---
    print()
    print("=" * 56)
    print("   🎓  BELAJAR BROLANG")
    print(f"       v{__version__} — belajar coding pakai Bahasa Indonesia")
    print("=" * 56)
    print()
    print(f"Ada {len(BAB)} bab, dari Halo Dunia sampai proyek mini.")
    print("Setiap jawaban benar bernilai poin. Progres disimpan otomatis.")
    print("Ketik 'keluar' kapan saja untuk berhenti (progres tetap tersimpan).")
    print()
    print("Mari mulai! 🚀")
    print()

    total_nilai = progres.get("total_nilai", 0)
    bab_selesai = progres.get("bab_selesai", 0)

    for idx, bab in enumerate(BAB, 1):
        if not _buka_kunci_bab(idx - 1, progres):
            print(f"\n🔒 BAB {idx} {bab['ikon']} {bab['judul']} masih dikunci.")
            print("   Selesaikan bab terlebih dahulu untuk membuka kunci ini.")
            break

        print(f"\n{'─' * 56}")
        print(f"  BAB {idx}/{len(BAB)}  {bab['ikon']}  {bab['judul']}")
        print(f"{'─' * 56}")
        print()
        for baris in bab["materi"].splitlines():
            print(baris)
        print()

        for no, soal in enumerate(bab["soal"], 1):
            konsep_id = soal.get("konsep", bab.get("konsep_utama", "umum"))
            print(f"📝 Soal {no}/{len(bab['soal'])}  (+{soal['poin']} poin)")
            print(f"   Konsep: {konsep_id}  [{_ICON_LEVEL.get(_konsep_progres(progres, konsep_id).get('level', 0), '?')}]")
            print(f"   {soal['teks']}")
            print()
            print("Ketik kode jawaban kamu (akhiri dengan baris kosong):")

            percobaan = 0
            jawaban_ditampilkan = False
            hint_level = 0
            while True:
                kode = _baca_kode()
                if kode is None:
                    _simpan_progres(progres)
                    return _akhir(nilai=total_nilai, bab_selesai=bab_selesai, progres=progres)

                perintah = kode.strip().lower()
                if perintah in ("keluar", "exit", "quit", "q"):
                    _simpan_progres(progres)
                    return _akhir(nilai=total_nilai, bab_selesai=bab_selesai, progres=progres)
                if perintah in ("bantuan", "help", "?"):
                    print(_PERINTAH)
                    continue
                if perintah in ("petunjuk", "hint", "bantu"):
                    hint_level = min(hint_level + 1, 3)
                    print(f"💡 Petunjuk (level {hint_level}): {_petunjuk_tingkat(soal, hint_level)}")
                    continue
                if perintah in ("jawaban", "solusi", "answer"):
                    print(f"✅ Solusi:\n{soal['solusi']}")
                    jawaban_ditampilkan = True
                    print("(0 poin — lanjut ke soal berikutnya)\n")
                    break
                if perintah in ("lewati", "skip", "s"):
                    print("Soal dilewati (0 poin).\n")
                    break
                if perintah in ("progres", "progress"):
                    _tampilkan_progres(progres)
                    continue

                percobaan += 1
                try:
                    status, detail = cek_jawaban(kode, soal)
                except KeyboardInterrupt:
                    print("\n(berhenti)")
                    _simpan_progres(progres)
                    return _akhir(nilai=total_nilai, bab_selesai=bab_selesai, progres=progres)

                # Deteksi pola kesalahan umum + umpan balik kualitas
                pola = _deteksi_pola_kesalahan(kode)
                masukan_kualitas = _feedback_kualitas_kode(kode)

                if status == "benar":
                    total_nilai += soal["poin"]
                    level_baru, nama_level = _perbarui_konsep(progres, konsep_id, benar=True)
                    print(f"🎉 Benar! +{soal['poin']} poin  (total: {total_nilai})")
                    print(f"   Konsep {konsep_id} sekarang level {nama_level} {_ICON_LEVEL.get(level_baru,'')}\n")
                    break
                if status == "error":
                    print("❌ Kode kamu error:")
                    print(f"   {detail}")
                else:
                    print(f"❌ Belum tepat. {detail}")

                # Umpan balik pola kesalahan
                for _nama, pesan, contoh, _poin in pola[:2]:
                    print(f"   🔍 {pesan}  (contoh: {contoh})")
                for m in masukan_kualitas[:2]:
                    print(f"   💡 {m}")

                # Naikkan level petunjuk setelah 2 percobaan salah
                if percobaan >= 2 and hint_level < 3 and not jawaban_ditampilkan:
                    hint_level += 1
                    print(f"💡 Petunjuk (level {hint_level}): {_petunjuk_tingkat(soal, hint_level)}")
                print("Coba lagi, atau ketik 'petunjuk' / 'jawaban' / 'lewati'.")

            bab_selesai += 1
            progres["bab_selesai"] = bab_selesai
            _simpan_progres(progres)

    _simpan_progres(progres)
    return _akhir(nilai=total_nilai, bab_selesai=bab_selesai, progres=progres)


def _akhir(nilai: int, bab_selesai: int, progres: Dict[str, Any]) -> int:
    """Tampilkan ringkasan nilai akhir."""
    persen = round(nilai / TOTAL_POIN * 100) if TOTAL_POIN else 0
    print()
    print("=" * 56)
    print("   🏁  HASIL BELAJAR")
    print("=" * 56)
    print(f"   Bab selesai : {bab_selesai}/{len(BAB)}")
    print(f"   Nilai       : {nilai}/{TOTAL_POIN}  ({persen}%)")
    print()
    if persen >= 90:
        pesan = "Luar biasa! Kamu siap bikin game pertama kamu 🚀"
    elif persen >= 70:
        pesan = "Hebat! Sedikit lagi sempurna 💪"
    elif persen >= 50:
        pesan = "Bagus! Terus berlatih biar makin jago 📚"
    else:
        pesan = "Jangan menyerah — coba lagi pelan-pelan, pasti bisa 🌱"
    print(f"   {pesan}")
    print("=" * 56)
    print()
    print("Lanjut belajar? Coba:")
    print("  bro belajar --ulang   # ulangi konsep yang perlu diperkuat")
    print("  bro repl              # latihan bebas di terminal")
    print()
    return 0


if __name__ == "__main__":
    import sys
    mode = "normal"
    konsep = None
    args = sys.argv[1:]
    if "--ulang" in args or "-u" in args:
        mode = "ulang"
    elif "--latihan" in args or "-l" in args:
        mode = "latihan"
        # ambil argumen setelah --latihan sebagai konsep
        for i, a in enumerate(args):
            if a in ("--latihan", "-l") and i + 1 < len(args):
                konsep = args[i + 1]
    sys.exit(mulai_belajar(mode=mode, konsep=konsep))
