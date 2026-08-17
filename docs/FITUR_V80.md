# BroLang v8.0 — Fitur Bahasa Modern + Performa VM 🚀

Versi 8.0 menghadirkan fitur bahasa yang membuat BroLang setara dengan
bahasa pemrograman modern lain (JavaScript, Python, Kotlin, Swift) plus
peningkatan performa nyata pada bytecode VM.

## 1. Spread Objek `{...a, "b": 1}` 🧩

Sebarkan (spread) seluruh isi sebuah objek ke objek literal lain —
campur bebas dengan pasangan kunci-nilai, dalam urutan apa pun:

```bro
buat pengaturan = {"suara": 80, "bahasa": "id", "lvl": 3}
buat pemain = {...pengaturan, "nama": "Budi"}
tulis pemain
# {'suara': 80, 'bahasa': 'id', 'lvl': 3, 'nama': 'Budi'}
```

**Urutan sumber dipertahankan** — kunci dari item yang ditulis BELAKANG
menimpa kunci yang sama dari item sebelumnya (konsisten dengan
Python `{**a, "b": 1}` dan JS `{...a, b: 1}`):

```bro
buat a = {"x": 1, "y": 2}
buat b = {...a, "y": 99}      # y=99 menimpa y=2 dari a
tulis b                       # {'x': 1, 'y': 99}

buat c = {"x": 1, ...a}       # spread belakang menimpa x=1
tulis c                       # {'x': 1, 'y': 2}  → x tetap 1 (a.x = 1)
```

Contoh lain: gabungan beberapa objek, override konfigurasi, dsb:

```bro
buat gabung = {...a, ...b, "baru": 5}
```

Spread objek berjalan konsisten di **interpreter**, **transpiler**
(`bro run`), dan **bytecode VM** (`bro build`). Spread pada nilai yang
bukan objek (angka, teks, list) memunculkan error.

## 2. Null-Coalescing Assignment `x ??= v` 🧩

Isi variabel/atribut/index HANYA bila nilainya saat ini `kosong` (None).
Nilai kanan tidak dievaluasi bila tidak perlu (**short-circuit**):

```bro
buat nama = kosong
nama ??= "Anonim"
tulis nama                 # Anonim

buat skor = 100
skor ??= 0                 # tidak berubah — sudah terisi
tulis skor                 # 100

# Nilai falsy (0, "", False) BUKAN kosong — tetap dipertahankan
buat x = 0
x ??= 99
tulis x                    # 0
```

Bisa dipakai pada atribut objek dan index list/objek:

```bro
kelas Akun
    fungsi __init__(self)
        self.nama = kosong
    selesai
selesai

buat a = Akun()
a.nama ??= "Budi"          # atribut objek

buat cache = [kosong, kosong]
cache[0] ??= 42            # index list

buat opsi = {"mode": kosong}
opsi["mode"] ??= "cepat"   # index objek
```

Short-circuit dibuktikan: fungsi di sisi kanan tidak dipanggil bila nilai
sudah terisi.

```bro
buat hitung = [0]
fungsi f()
    hitung[0] = hitung[0] + 1
    kembali 5
selesai

buat x = 10
x ??= f()                  # f TIDAK dipanggil
tulis hitung[0]            # 0
```

Tidak ambigu dengan null-coalescing `??` (v5.0) — `??` menghasilkan nilai
default, `??=` menugaskan nilai default.

## 3. `kecuali (TipeA, TipeB)` — Multi-Tipe Exception 🧩

Satu klausa `kecuali` bisa menangkap beberapa tipe error sekaligus — cocok
bila SALAH SATU tipe cocok; selain itu exception dilempar ulang (re-raise):

```bro
coba
    buat hasil = 100 / angka_teks
kecuali (TypeError, ZeroDivisionError) sebagai e
    tulis "tertangkap: " + teks(e)
selesai
```

Berfungsi dengan tipe bawaan (`ZeroDivisionError`, `TypeError`,
`IndexError`, `KeyError`, `RuntimeError_`, `ValueError`, ...) dan
`kelas_error` kustom:

```bro
kelas_error ValidasiGagal extends Kesalahan
    fungsi __init__(pesan)
        self.pesan = pesan
    selesai
selesai

coba
    lempar ValidasiGagal("email kosong")
kecuali (ValidasiGagal, KeyError) sebagai e
    tulis "caught"
selesai
```

> **v8.0 fix**: `kelas_error` kustom kini berfungsi penuh di VM (sebelumnya
> deklarasi kelas error dibuang diam-diam dan `lempar` selalu membungkus ke
> `RuntimeError_`). VM mendaftarkan `Kesalahan` sebagai kelas dasar bawaan,
> `lempar <instance>` melampirkan `error_instance`/`error_class`, dan
> pencocokan `kecuali` menelusuri hierarki induk — `kecuali Induk` menangkap
> semua turunannya, variabel `e` mengikat instance error (`e.pesan` bisa
> dipakai) — konsisten di ketiga mesin.

Bisa digabung dengan klausa lain:

```bro
coba
    ...
kecuali (KeyError, IndexError) sebagai e
    tulis "akses gagal"
kecuali ZeroDivisionError sebagai e2
    tulis "bagi nol"
selesai
```

Konsisten di interpreter, transpiler, dan VM.

## 4. Performa Bytecode VM ⚡

v8.0 mengoptimalkan hot path VM (bytecode) — hasil benchmark:

| Benchmark | Sebelum (v7.2) | Sesudah (v8.0) | Peningkatan |
|-----------|----------------|----------------|-------------|
| Fibonacci (rekursif) | ~1260-1350 ms | ~1060-1140 ms | **~15% lebih cepat** |
| Loop + aritmatika    | ~1520-1870 ms | ~1440-1540 ms | **~10% lebih cepat** |

Optimasi yang dilakukan:

1. **Fast path `_execute`** — bila bytecode TIDAK punya handler exception
   (`has_handlers` dihitung saat kompilasi), wrapper try/except untuk
   exception routing dilewati — exception langsung menyebar ke pemanggil.
   Ini menghilangkan overhead try/except per pemanggilan fungsi (hot path
   rekursi seperti Fibonacci).
2. **Alokasi frame sesuai ukuran** — frame sekarang mengalokasikan slot
   lokal sebanyak yang benar-benar dipakai (`bytecode.local_count`,
   dihitung compiler sebagai jumlah puncak), bukan selalu 64 slot.
3. **Fast path `_call_function`** — pemanggilan fungsi VM biasa (tanpa
   keyword-argumen, tanpa default, tanpa rest param) melewati pemrosesan
   umum: parameter diikat langsung ke slot frame.
4. **`LOAD_GLOBAL` satu dict op** — variabel user dicari langsung di
   `globals_dict` (builtin juga terdaftar di sana), menghindari 2-3
   operasi dict per load. Invalidsai builtin cache per `STORE_GLOBAL`
   juga dihapus (redundan setelah perubahan ini).

Semua perilaku eksekusi IDENTIK — hanya kecepatan yang berubah. Seluruh
suite test (1200+) tetap hijau.

## File Terkait

- Contoh: `examples/fitur_v80.bro`
- Tes: `tests/unit/test_v80_language.py`
- Benchmark: `bro benchmark benchmarks/fibonacci.bro`
