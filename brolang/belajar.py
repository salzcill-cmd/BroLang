"""
Mode Belajar BroLang (v6.1)
===========================

Tutorial interaktif di terminal untuk pemula & pelajar Indonesia.

Jalankan dengan:
    bro belajar

Struktur:
- 8 bab bertingkat: Halo Dunia → Variabel → Matematika → Percabangan →
  Perulangan → List → Fungsi → Proyek Mini
- Tiap bab: materi singkat + latihan soal
- Jawaban dicek otomatis dengan menjalankan kode di interpreter
- Nilai & umpan balik langsung, plus perintah bantuan:
    bantuan   : daftar perintah
    petunjuk  : bantuan untuk soal yang sedang dikerjakan
    jawaban   : lihat solusi (tanpa poin)
    lewati    : lanjut ke soal berikutnya
    keluar    : berhenti (nilai tetap dihitung)

Contoh pemakaian programatik (untuk test):
    from brolang.belajar import cek_jawaban, BAB
    status, detail = cek_jawaban('tulis "Halo Dunia!"', BAB[0]["soal"][0])
    # status: "benar" | "salah" | "error"
"""

import io
import contextlib
import threading
from typing import List, Dict, Any, Tuple

from brolang.lexer import Lexer
from brolang.parser import Parser
from brolang.interpreter import Interpreter
from brolang import __version__

# Batas waktu eksekusi jawaban siswa (detik) — mencegah perulangan tak
# berujung menggantung sesi belajar. Pemula justru sering menulis
# `selama true lakukan ... selesai` secara tidak sengaja.
_TIMEOUT_DETIK = 5.0


def _jalankan_dengan_batas_waktu(interp: Interpreter, ast, timeout: float) -> str:
    """Jalankan AST di interpreter dengan batas waktu (daemon thread).

    Interpreter di-serialisasi per cek jawaban (baru tiap panggilan dan
    hasilnya dibuang), jadi aman dijalankan di thread terpisah. Thread
    daemon mati otomatis saat proses selesai.

    Returns:
        None kalau selesai tanpa error, atau pesan error (str) kalau
        gagal / melewati batas waktu.
    """
    hasil: Dict[str, Exception] = {}

    def kerja() -> None:
        try:
            interp.interpret(ast)
        except Exception as e:
            hasil["error"] = e

    t = threading.Thread(target=kerja, daemon=True)
    t.start()
    # redirect_stdout di MAIN thread (bukan di worker): kalau timeout dan
    # worker masih terjebak di dalam interpret, blok `with` tetap keluar
    # sehingga sys.stdout langsung dipulihkan — output UI belajar setelah
    # jawaban yang menggantung tidak ikut tertelan.
    with contextlib.redirect_stdout(io.StringIO()):
        t.join(timeout)
    if t.is_alive():
        return ("Kode berjalan terlalu lama — kemungkinan ada perulangan tak "
                "berujung. Cek kondisi perulanganmu, lalu coba lagi.")
    if "error" in hasil:
        return str(hasil["error"])
    return None


# ============= Kurikulum =============

BAB: List[Dict[str, Any]] = [
    {
        "judul": "Halo Dunia",
        "ikon": "🖨️",
        "materi": """Program pertama! Kata kunci `tulis` mencetak sesuatu ke layar.

    tulis "Halo Dunia!"      # Halo Dunia!
    tulis 2 + 3              # 5
    tulis "A", "B"           # A B

Teks ditulis di dalam tanda kutip "..." — angka tidak perlu kutip.""",
        "soal": [
            {
                "teks": 'Cetak kalimat "Halo Dunia!" ke layar.',
                "cek": "tepat",
                "harapan": ["Halo Dunia!"],
                "petunjuk": "Gunakan `tulis` diikuti teks di dalam tanda kutip: tulis \"...\"",
                "solusi": 'tulis "Halo Dunia!"',
                "poin": 10,
            },
            {
                "teks": 'Cetak "Halo, saya Budi!" (ganti Budi dengan nama kamu sendiri).',
                "cek": "mengandung",
                "harapan": ["Halo, saya"],
                "petunjuk": 'Pola: tulis "Halo, saya ..." — nama di dalam tanda kutip.',
                "solusi": 'tulis "Halo, saya Budi!"',
                "poin": 10,
            },
        ],
    },
    {
        "judul": "Variabel",
        "ikon": "📦",
        "materi": """Variabel menyimpan nilai supaya bisa dipakai ulang. Pakai `buat`:

    buat nama = "Budi"       # variabel teks
    buat umur = 17           # variabel angka
    tulis nama               # Budi
    tulis umur               # 17

Isi variabel bisa digabung dengan tanda +.""",
        "soal": [
            {
                "teks": "Buat variabel `umur` berisi 17, lalu cetak isinya.",
                "cek": "tepat",
                "harapan": ["17"],
                "petunjuk": "buat umur = 17, lalu tulis umur",
                "solusi": "buat umur = 17\ntulis umur",
                "poin": 10,
            },
            {
                "teks": 'Buat variabel `nama` = "Ani" dan `kota` = "Jakarta", lalu cetak "Ani tinggal di Jakarta".',
                "cek": "mengandung",
                "harapan": ["tinggal di"],
                "petunjuk": 'Gabungkan dengan + : tulis nama + " tinggal di " + kota',
                "solusi": 'buat nama = "Ani"\nbuat kota = "Jakarta"\ntulis nama + " tinggal di " + kota',
                "poin": 10,
            },
        ],
    },
    {
        "judul": "Operasi Matematika",
        "ikon": "➕",
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
                "cek": "tepat",
                "harapan": ["20"],
                "petunjuk": "tulis 10 + 5 * 2  →  5 * 2 = 10, lalu 10 + 10 = 20",
                "solusi": "tulis 10 + 5 * 2",
                "poin": 10,
            },
            {
                "teks": "Cetak hasil dari (10 + 5) * 2 (kurung dulu!).",
                "cek": "tepat",
                "harapan": ["30"],
                "petunjuk": "Gunakan tanda kurung: tulis (10 + 5) * 2",
                "solusi": "tulis (10 + 5) * 2",
                "poin": 10,
            },
            {
                "teks": "Cetak sisa bagi 17 dibagi 5 (operator %).",
                "cek": "tepat",
                "harapan": ["2"],
                "petunjuk": "17 : 5 = 3 sisa 2. Pakai operator %",
                "solusi": "tulis 17 % 5",
                "poin": 10,
            },
        ],
    },
    {
        "judul": "Percabangan",
        "ikon": "🌿",
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
                "cek": "tepat",
                "harapan": ["besar"],
                "petunjuk": "jika 5 > 3 maka ... selesai (jangan lupa `selesai` di akhir blok)",
                "solusi": 'jika 5 > 3 maka\n    tulis "besar"\nselesai',
                "poin": 10,
            },
            {
                "teks": 'Buat variabel `nilai` = 80. Cetak "LULUS" jika nilai >= 75, selain itu cetak "TIDAK LULUS".',
                "cek": "tepat",
                "harapan": ["LULUS"],
                "petunjuk": "Gunakan jika ... maka ... lainnya ... selesai",
                "solusi": 'buat nilai = 80\njika nilai >= 75 maka\n    tulis "LULUS"\nlainnya\n    tulis "TIDAK LULUS"\nselesai',
                "poin": 10,
            },
        ],
    },
    {
        "judul": "Perulangan",
        "ikon": "🔁",
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
                "cek": "tepat",
                "harapan": ["0", "1", "2", "3", "4"],
                "petunjuk": "untuk i dalam range(5) lakukan ... selesai, lalu tulis i",
                "solusi": "untuk i dalam range(5) lakukan\n    tulis i\nselesai",
                "poin": 10,
            },
            {
                "teks": "Hitung mundur dari 5 ke 1 pakai `selama`.",
                "cek": "tepat",
                "harapan": ["5", "4", "3", "2", "1"],
                "petunjuk": "buat i = 5, lalu selama i > 0 lakukan: tulis i lalu i = i - 1",
                "solusi": "buat i = 5\nselama i > 0 lakukan\n    tulis i\n    i = i - 1\nselesai",
                "poin": 10,
            },
        ],
    },
    {
        "judul": "List",
        "ikon": "📋",
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
                "cek": "tepat",
                "harapan": ["mangga"],
                "petunjuk": "Indeks dimulai dari 0: buah[0] = apel, buah[1] = mangga",
                "solusi": 'buat buah = ["apel", "mangga"]\ntulis buah[1]',
                "poin": 10,
            },
            {
                "teks": 'Buat list ["apel", "mangga", "jeruk"], lalu cetak semua buah satu per satu.',
                "cek": "tepat",
                "harapan": ["apel", "mangga", "jeruk"],
                "petunjuk": "untuk item dalam buah lakukan ... tulis item ... selesai",
                "solusi": 'buat buah = ["apel", "mangga", "jeruk"]\nuntuk item dalam buah lakukan\n    tulis item\nselesai',
                "poin": 10,
            },
        ],
    },
    {
        "judul": "Fungsi",
        "ikon": "🧩",
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
                "cek": "tepat",
                "harapan": ["42"],
                "petunjuk": "fungsi kali2(x) ... kembali x * 2 ... selesai, lalu tulis kali2(21)",
                "solusi": "fungsi kali2(x)\n    kembali x * 2\nselesai\ntulis kali2(21)",
                "poin": 10,
            },
            {
                "teks": 'Buat fungsi sapa(nama) yang mengembalikan "Halo " + nama, lalu cetak sapa("Budi").',
                "cek": "tepat",
                "harapan": ["Halo Budi"],
                "petunjuk": 'fungsi sapa(nama) ... kembali "Halo " + nama ... selesai',
                "solusi": 'fungsi sapa(nama)\n    kembali "Halo " + nama\nselesai\ntulis sapa("Budi")',
                "poin": 10,
            },
        ],
    },
    {
        "judul": "Proyek Mini: Kalkulator",
        "ikon": "🎮",
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
                "cek": "tepat",
                "harapan": ["14", "6"],
                "petunjuk": "Salin pola dari materi, lengkapi dua percabangan (+, -), lalu panggil dua kali.",
                "solusi": 'fungsi hitung(a, b, op)\n    jika op == "+" maka\n        kembali a + b\n    selesai\n    jika op == "-" maka\n        kembali a - b\n    selesai\n    kembali 0\nselesai\ntulis hitung(10, 4, "+")\ntulis hitung(10, 4, "-")',
                "poin": 20,
            },
        ],
    },
]

TOTAL_POIN = sum(soal["poin"] for bab in BAB for soal in bab["soal"])


# ============= Pemeriksa Jawaban =============

def cek_jawaban(kode: str, soal: Dict[str, Any], timeout: float = _TIMEOUT_DETIK) -> Tuple[str, Any]:
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
    # Parse dulu supaya error sintaks terpisah dari error runtime
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

    # default: tepat (urutan baris harus sama persis)
    if keluaran == harapan:
        return ("benar", keluaran)
    harapan_teks = " | ".join(harapan)
    keluaran_teks = " | ".join(keluaran) if keluaran else "(tidak ada output)"
    return ("salah", f"Output kamu: {keluaran_teks} — yang diharapkan: {harapan_teks}")


# ============= Mode Interaktif =============

_PERINTAH = """Perintah yang bisa dipakai:
  petunjuk   : bantuan untuk soal ini
  jawaban    : lihat solusi (tanpa poin)
  lewati     : lanjut ke soal berikutnya (tanpa poin)
  bantuan    : tampilkan daftar perintah ini
  keluar     : berhenti belajar (nilai tetap dihitung)

Menjawab: ketik kode kamu, lalu tekan Enter di baris kosong untuk
mengirim jawaban. Perintah (petunjuk/jawaban/lewati/keluar) diproses
langsung tanpa perlu baris kosong."""

# Kata perintah — diproses langsung tanpa menunggu baris kosong
_PERINTAH_KATA = (
    "keluar", "exit", "quit", "q",
    "bantuan", "help", "?",
    "petunjuk", "hint", "bantu",
    "jawaban", "solusi", "answer",
    "lewati", "skip", "s",
)


def _baca_kode(prompt: str = "  1> ") -> str:
    """Baca kode multi-baris dari input sampai baris kosong.

    Perintah (keluar/jawaban/petunjuk/...) langsung dikembalikan tanpa
    perlu baris kosong, supaya interaksi terasa responsif.
    """
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
            return baris  # perintah diproses langsung di loop utama
        baris_list.append(baris)
        nomor += 1
    return "\n".join(baris_list)


def mulai_belajar() -> int:
    """Jalankan mode belajar interaktif. Mengembalikan exit code."""
    print()
    print("=" * 56)
    print("   🎓  BELAJAR BROLANG")
    print(f"       v{__version__} — belajar coding pakai Bahasa Indonesia")
    print("=" * 56)
    print()
    print(f"Ada {len(BAB)} bab, dari Halo Dunia sampai proyek mini.")
    print("Setiap jawaban benar bernilai poin. Ketik 'keluar' kapan saja.")
    print()
    print("Mari mulai! 🚀")
    print()

    total_nilai = 0
    bab_selesai = 0

    for idx, bab in enumerate(BAB, 1):
        print(f"\n{'─' * 56}")
        print(f"  BAB {idx}/{len(BAB)}  {bab['ikon']}  {bab['judul']}")
        print(f"{'─' * 56}")
        print()
        for baris in bab["materi"].splitlines():
            print(baris)
        print()

        for no, soal in enumerate(bab["soal"], 1):
            print(f"📝 Soal {no}/{len(bab['soal'])}  (+{soal['poin']} poin)")
            print(f"   {soal['teks']}")
            print()
            print("Ketik kode jawaban kamu (akhiri dengan baris kosong):")

            percobaan = 0
            jawaban_ditampilkan = False
            while True:
                kode = _baca_kode()
                if kode is None:
                    return _akhir(nilai=total_nilai, bab_selesai=bab_selesai)

                perintah = kode.strip().lower()
                if perintah in ("keluar", "exit", "quit", "q"):
                    return _akhir(nilai=total_nilai, bab_selesai=bab_selesai)
                if perintah in ("bantuan", "help", "?"):
                    print(_PERINTAH)
                    continue
                if perintah in ("petunjuk", "hint", "bantu"):
                    print(f"💡 Petunjuk: {soal['petunjuk']}")
                    continue
                if perintah in ("jawaban", "solusi", "answer"):
                    print(f"✅ Solusi:\n{soal['solusi']}")
                    jawaban_ditampilkan = True
                    print("(0 poin — lanjut ke soal berikutnya)\n")
                    break
                if perintah in ("lewati", "skip", "s"):
                    print("Soal dilewati (0 poin).\n")
                    break

                percobaan += 1
                try:
                    status, detail = cek_jawaban(kode, soal)
                except KeyboardInterrupt:
                    # Ctrl+C saat kode sedang dieksekusi (maks 5 detik)
                    print("\n(berhenti)")
                    return _akhir(nilai=total_nilai, bab_selesai=bab_selesai)
                if status == "benar":
                    total_nilai += soal["poin"]
                    print(f"🎉 Benar! +{soal['poin']} poin  (total: {total_nilai})\n")
                    break
                if status == "error":
                    print("❌ Kode kamu error:")
                    print(f"   {detail}")
                else:
                    print(f"❌ Belum tepat. {detail}")
                if percobaan >= 2 and not jawaban_ditampilkan:
                    print(f"💡 Petunjuk: {soal['petunjuk']}")
                print("Coba lagi, atau ketik 'petunjuk' / 'jawaban' / 'lewati'.")

        bab_selesai += 1

    return _akhir(nilai=total_nilai, bab_selesai=bab_selesai)


def _akhir(nilai: int, bab_selesai: int) -> int:
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
    print("Lanjut belajar? Coba: bro repl — ketik kode bebas di terminal.")
    print()
    return 0
