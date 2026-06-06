# BroLang

**Bahasa Pemrograman Edukatif Profesional**

BroLang adalah bahasa pemrograman dengan sintaks Bahasa Indonesia yang dirancang untuk memudahkan pembelajaran pemrograman bagi pemula berbahasa Indonesia. Dibangun dengan Python, BroLang memiliki fitur lengkap bahasa pemrograman modern.

```
tulis "Halo Dunia!"
```

---

## Daftar Isi

- [Instalasi](#instalasi)
- [Penggunaan Cepat](#penggunaan-cepat)
- [Dasar Bahasa](#dasar-bahasa)
  - [Tipe Data](#tipe-data)
  - [Variabel](#variabel)
  - [Operator](#operator)
  - [Percabangan](#percabangan)
  - [Perulangan](#perulangan)
  - [String](#string)
  - [List](#list)
  - [Objek](#objek)
- [Fungsi](#fungsi)
- [Kelas & OOP](#kelas--oop)
- [Error Handling](#error-handling)
- [Modul & Import](#modul--import)
- [Fungsi Bawaan](#fungsi-bawaan)
- [Standard Library](#standard-library)
  - [matematika](#matematika)
  - [teks](#teks)
  - [waktu](#waktu)
  - [file](#file)
  - [json](#json)
  - [jaringan](#jaringan)
  - [acak](#acak)
- [CLI](#cli)
- [REPL](#repl)
- [Format Kode](#format-kode)
- [Linter](#linter)
- [Kompilasi](#kompilasi)
- [Package Manager](#package-manager)
- [LSP](#lsp)
- [Arsitektur](#arsitektur)
- [Contoh Lengkap](#contoh-lengkap)

---

## Instalasi

```bash
# Clone repo
git clone https://github.com/brolang/brolang.git
cd brolang

# Install
pip install -e .

# Cek instalasi
bro --help
```

## Penggunaan Cepat

```bash
# Jalankan file
bro contoh.bro

# Atau dengan perintah run
bro run contoh.bro

# REPL interaktif
bro repl

# Format kode
bro fmt contoh.bro

# Lint kode
bro lint contoh.bro

# Kompilasi ke Python
bro build contoh.bro -o output.py
```

---

## Dasar Bahasa

### Tipe Data

| Tipe | Nama BroLang | Contoh |
|------|--------------|--------|
| Integer | `angka` | `42` |
| Float | `desimal` | `3.14` |
| String | `teks` | `"halo"` |
| Boolean | `boolean` | `benar`, `salah` |
| List | `list` | `[1, 2, 3]` |
| Objek | `objek` | `{"nama": "Budi"}` |
| Null | `kosong` | `kosong` |

Cek tipe dengan fungsi `tipe()`:

```python
tulis tipe(42)         # angka
tulis tipe(3.14)       # desimal
tulis tipe("halo")     # teks
tulis tipe(benar)      # boolean
tulis tipe([1,2,3])    # list
tulis tipe(kosong)     # kosong
```

### Variabel

```python
buat nama = "Budi"
buat umur = 17
buat tinggi = 170.5
buat siswa = benar
buat nilai = kosong

# Reassign (tanpa buat)
umur = 18

# Multi variable
buat a = 1, b = 2, c = 3
```

### Operator

**Aritmatika:**

| Operator | Fungsi |
|----------|--------|
| `+` | Penjumlahan |
| `-` | Pengurangan |
| `*` | Perkalian |
| `/` | Pembagian |
| `%` | Modulo (sisa bagi) |
| `**` | Pangkat |

```python
tulis 10 + 3    # 13
tulis 10 - 3    # 7
tulis 10 * 3    # 30
tulis 10 / 3    # 3.333...
tulis 10 % 3    # 1
tulis 10 ** 3   # 1000
```

**Perbandingan:**

| Operator | Fungsi |
|----------|--------|
| `==` | Sama dengan |
| `!=` | Tidak sama |
| `>` | Lebih besar |
| `<` | Lebih kecil |
| `>=` | Lebih besar atau sama |
| `<=` | Lebih kecil atau sama |

**Logika:**

| Operator | Fungsi |
|----------|--------|
| `dan` | AND |
| `atau` | OR |
| `bukan` | NOT |

```python
jika umur >= 17 dan memiliki_sim maka
    tulis "Boleh menyetir"
selesai
```

### Percabangan

```python
jika nilai >= 90 maka
    tulis "Grade A"
lainnya jika nilai >= 80 maka
    tulis "Grade B"
lainnya jika nilai >= 70 maka
    tulis "Grade C"
lainnya
    tulis "Grade D"
selesai
```

### Perulangan

**For loop:**

```python
# Range
untuk i dalam range(5) lakukan
    tulis i
selesai

# List
untuk buah dalam ["apel", "pisang", "jeruk"] lakukan
    tulis "Buah:", buah
selesai
```

**While loop:**

```python
buat i = 0
selama i < 5 lakukan
    tulis i
    i = i + 1
selesai
```

**Loop control:**

```python
# break
untuk i dalam range(10) lakukan
    jika i == 5 maka
        hentikan
    selesai
    tulis i
selesai

# continue
untuk i dalam range(5) lakukan
    jika i == 2 maka
        lanjutkan
    selesai
    tulis i
selesai
```

### String

```python
buat s1 = "Hello"
buat s2 = 'World'
buat s3 = """Multi-line
string"""

# Concatenation
buat s = "Halo " + "Dunia"

# Escape sequences
tulis "Baris pertama\nBaris kedua"
tulis "Tab\tberikutnya"
tulis "Tanda kutip \" di dalam string"

# String methods (via stdlib teks)
impor teks
tulis teks.upper("hello")     # HELLO
tulis teks.kapital("halo")    # Halo
tulis teks.potong("a,b,c", ",")  # ["a", "b", "c"]
```

### List

```python
buat angka = [1, 2, 3, 4, 5]
tulis angka[0]          # 1
tulis angka[-1]         # 5
tulis len(angka)        # 5

# Nested list
buat matriks = [[1, 2], [3, 4]]
tulis matriks[0][1]     # 2

# List operation
buat list2 = angka + [6, 7]
```

### Objek

```python
buat orang = {"nama": "Budi", "umur": 17}
tulis orang["nama"]
orang["pekerjaan"] = "Programmer"
```

---

## Fungsi

```python
fungsi sapa(nama)
    kembali "Halo " + nama + "!"
selesai

tulis sapa("Budi")  # Halo Budi!

# Multiple params
fungsi tambah(a, b)
    kembali a + b
selesai

# Default return (kembali None)
fungsi cetak_pesan(pesan)
    tulis pesan
selesai

# Recursive
fungsi faktorial(n)
    jika n <= 1 maka
        kembali 1
    lainnya
        kembali n * faktorial(n - 1)
    selesai
selesai
```

---

## Kelas & OOP

```python
kelas Mahasiswa

    fungsi __init__(self, nama, jurusan)
        buat self.nama = nama
        buat self.jurusan = jurusan
        buat self.nilai = []
    selesai

    fungsi tambah_nilai(self, n)
        self.nilai = self.nilai + [n]
    selesai

    fungsi info(self)
        kembali self.nama + " - " + self.jurusan
    selesai

selesai

buat mhs = Mahasiswa("Ani", "Informatika")
mhs.tambah_nilai(85)
tulis mhs.info()
```

**Class dengan pewarisan:**

```python
kelas Karyawan
    fungsi __init__(self, nama, gaji)
        buat self.nama = nama
        buat self.gaji = gaji
    selesai
    fungsi info(self)
        kembali self.nama + ": Rp" + self.gaji
    selesai
selesai

kelas Manager(Karyawan)
    fungsi __init__(self, nama, gaji, tim)
        buat self.nama = nama  # atau panggil parent __init__
        buat self.gaji = gaji
        buat self.tim = tim
    selesai
selesai
```

---

## Error Handling

```python
coba
    buat hasil = 10 / 0
    tulis hasil
tangkap error
    tulis "Terjadi error:", error
selesai
```

Error yang bisa ditangkap:

- `Pesan: Tidak bisa membagi dengan nol.` — pembagian dengan nol
- `Pesan: Variabel 'x' tidak ditemukan.` — variabel tidak terdefinisi
- `Pesan: Tipe ... tidak bisa di-index.` — indexing salah
- `Pesan: Indeks ... di luar batas.` — indeks melebihi panjang list

---

## Modul & Import

```python
# Import seluruh modul
impor matematika
tulis matematika.akar(25)

# Import spesifik
dari teks impor upper, lower
tulis upper("halo")

# Import dengan alias
impor acak sebagai rnd
tulis rnd.bulat(1, 10)
```

---

## Fungsi Bawaan

Fungsi-fungsi ini tersedia secara global tanpa perlu import:

| Fungsi | Deskripsi | Contoh |
|--------|-----------|--------|
| `len(x)` | Panjang string/list/objek | `len("halo")` |
| `angka(x)` | Konversi ke integer | `angka("42")` |
| `desimal(x)` | Konversi ke float | `desimal("3.14")` |
| `teks(x)` | Konversi ke string | `teks(42)` |
| `tipe(x)` | Nama tipe data | `tipe(42)` |
| `range(start, stop, step)` | Membuat range | `range(5)` |
| `jumlah(iterable)` | Sum elemen | `jumlah([1,2,3])` |
| `peta(func, iterable)` | Map function | `peta(angka, ["1","2"])` |
| `saring(func, iterable)` | Filter list | `saring(f, [1,2,3])` |
| `input(prompt)` | Input dari user | `input("Nama: ")` |

---

## Standard Library

### matematika

```python
impor matematika

matematika.akar(25)          # 5.0
matematika.sin(3.14/2)       # 0.999...
matematika.cos(0)            # 1.0
matematika.tan(0)            # 0.0
matematika.pangkat(2, 3)     # 8.0
matematika.absolut(-5)       # 5
matematika.bulat(3.141, 2)   # 3.14
matematika.lantai(3.7)       # 3
matematika.langit(3.2)       # 4
matematika.log(100, 10)      # 2.0
matematika.pi()              # 3.141592653589793
matematika.e()               # 2.718281828459045
matematika.max(10, 20)       # 20
matematika.min(10, 20)       # 10
matematika.faktorial(5)      # 120
```

### teks

```python
impor teks

teks.upper("hello")              # HELLO
teks.lower("HELLO")              # hello
teks.kapital("hello world")      # Hello world
teks.judul("hello world")        # Hello World
teks.potong("a,b,c", ",")        # ["a", "b", "c"]
teks.gabung(["a", "b", "c"])     # abc
teks.ganti("hello", "l", "x")    # hexxo
teks.panjang("hello")            # 5
teks.strip("  hi  ")             # hi
teks.cari("hello", "el")         # 1
teks.mulai("hello", "he")        # benar
teks.berakhir("hello", "lo")     # benar
teks.potong_kiri("  hi  ")       # "hi  "
teks.potong_kanan("  hi  ")      # "  hi"
```

### waktu

```python
impor waktu

waktu.sekarang()             # "2026-06-06T12:00:00"
waktu.tidur(1)               # Tunggu 1 detik
waktu.waktu()                # 1778654400.0 (UNIX timestamp)
waktu.tanggal()              # "2026-06-06"
waktu.jam()                  # "12:00:00"
waktu.format_waktu("%Y-%m")  # "2026-06"
```

### file

```python
impor file

file.baca("data.txt")                    # Baca file teks
file.tulis("output.txt", "konten")        # Tulis file
file.tambah("log.txt", "baris baru")      # Append
file.baca_baris("data.txt")               # Generator baris
file.ada("data.txt")                      # True/False
file.hapus("sampah.txt")                  # Hapus file
file.ukuran("data.txt")                   # Ukuran bytes
file.daftar("/tmp")                       # List directory
file.buat_folder("folder_baru")           # Buat folder
```

### json

```python
impor json

json.parsing('{"nama": "Budi"}')          # {"nama": "Budi"}
json.string({"nama": "Budi"})             # '{\n  "nama": "Budi"\n}'
json.baca("data.json")                    # Baca file JSON
json.tulis("data.json", {"key": "val"})   # Tulis file JSON
```

### jaringan

```python
impor jaringan

# HTTP GET
hasil = jaringan.dapatkan("https://api.example.com")
tulis hasil.status
tulis hasil.data

# HTTP POST
hasil = jaringan.kirim("https://api.example.com",
    data='{"nama": "Budi"}', method="POST")
```

### acak

```python
impor acak

acak.angka(0, 1)                          # 0.731...
acak.bulat(1, 100)                        # 42
acak.pilih(["merah", "biru", "hijau"])    # "biru"
acak.pilih_beberapa([1,2,3,4,5], 3)       # [2, 5, 1]
acak.acak_list([1,2,3,4,5])              # [3, 1, 5, 2, 4]
acak.seed(42)                             # Set seed
```

---

## CLI

```bash
bro                     # Tampilkan info
bro file.bro            # Jalankan file (langsung)
bro run file.bro        # Jalankan file
bro build file.bro      # Kompilasi ke Python
bro build file.bro -o output.py  # Simpan hasil kompilasi
bro repl                # REPL interaktif
bro fmt file.bro        # Format kode
bro fmt file.bro --check  # Cek format saja
bro lint file.bro       # Analisis statis
bro version             # Info versi
bro --help              # Bantuan
```

---

## REPL

```bash
bro repl
```

Fitur REPL:
- History perintah (navigasi dengan panah atas/bawah)
- Multi-line input (enter dua kali untuk eksekusi)
- Error reporting dengan pesan jelas
- Auto-completion (via LSP)

---

## Format Kode

```bash
bro fmt file.bro        # Format file
bro fmt file.bro --check  # Cek tanpa mengubah
```

Aturan format:
- Indentasi 4 spasi
- Baris baru setelah `maka`, `lakukan`, `selesai`, `lainnya`, `tangkap`
- Dedent otomatis pada `selesai`, `lainnya`, `tangkap`
- Mempertahankan komentar dan baris kosong

---

## Linter

```bash
bro lint file.bro
```

Aturan lint:

| Aturan | Severity | Deskripsi |
|--------|----------|-----------|
| `line-length` | warning | Maksimal 100 karakter per baris |
| `trailing-whitespace` | info | Tidak boleh ada spasi di akhir baris |
| `indentation` | warning | Gunakan spasi (bukan tab), 4 spasi per level |
| `naming-convention` | info | Minimal 2 karakter, deskriptif |

---

## Kompilasi

Kompilasi kode BroLang ke Python:

```bash
bro build program.bro -o output.py
python output.py        # Jalankan hasil kompilasi
```

Hasil kompilasi adalah kode Python murni yang bisa dijalankan langsung.

---

## Package Manager

```bash
bropm install paket       # Install package
bropm remove paket        # Hapus package
bropm update              # Update semua
bropm update paket        # Update spesifik
bropm list                # Lihat package terinstall
bropm search kata_kunci   # Cari package
```

Packages disimpan di `~/.brolang/packages/`.

---

## LSP

BroLang memiliki Language Server Protocol (LSP) server yang kompatibel dengan VS Code, Neovim, dan editor lainnya.

```bash
bro-lsp  # Jalankan LSP server
```

Fitur:
- **Diagnostics**: error dan warning real-time
- **Auto-completion**: saran kode kontekstual
- **Hover information**: info tipe dan dokumentasi

Integrasi VS Code — tambahkan ke `settings.json`:

```json
{
    "lsp.enabled": true,
    "lsp.serverCommand": ["bro-lsp"]
}
```

---

## Arsitektur

BroLang menggunakan pipeline eksekusi 5 tahap:

```
Source Code → Lexer → Tokens → Parser → AST → Analyzer → AST → Optimizer → AST → Interpreter → Output
```

| Tahap | Deskripsi |
|-------|-----------|
| **Lexer** | Memecah source code menjadi token. Mendukung Unicode/UTF-8, indent/dedent (gaya Python), komentar single-line (`#`) dan multi-line (`#| \|#`), string single/double/multi-line, konversi keyword Indonesia ke token |
| **Parser** | Recursive descent parser. Mengubah token stream menjadi AST (Abstract Syntax Tree). Menangani semua grammar BroLang dengan precedence climbing untuk operator |
| **Semantic Analyzer** | Validasi semantik. Symbol table dengan scoping, deteksi variabel tak terdefinisi, deklarasi duplikat, type checking, validasi fungsi |
| **Optimizer** | Optimasi AST. Constant folding (`2+3` → `5`), algebraic simplification (`x+0` → `x`, `x*1` → `x`), dead code elimination (konstanta if/while) |
| **Interpreter** | Visitor pattern interpreter. Environment-based scoping, function call dengan argument passing, class instantiation dengan method dispatch, try-catch error handling |

**Compiler**: Alternatif pipeline — mengubah AST BroLang ke Python AST, lalu dikompilasi ke Python bytecode via `compile()`.

---

## Contoh Lengkap

Lihat `examples/brolang_comprehensive.bro` untuk demo semua fitur:

```bash
bro examples/brolang_comprehensive.bro
```

Contoh lain di `examples/`:

| File | Deskripsi |
|------|-----------|
| `hello.bro` | Hello World |
| `variabel.bro` | Variabel dan tipe data |
| `kondisi.bro` | If/elif/else |
| `loop.bro` | For dan while |
| `fungsi.bro` | Fungsi |
| `kelas.bro` | Kelas dan OOP |
| `error_handling.bro` | Try-catch |
| `stdlib.bro` | Standard library |
| `brolang_comprehensive.bro` | Semua fitur |

---

## Pengembangan

```bash
# Setup dev environment
pip install -e ".[dev]"

# Run tests
PYTHONPATH=/home/izza/Projects/BroLang pytest tests/

# Run tests with coverage
PYTHONPATH=/home/izza/Projects/BroLang pytest tests/ --cov=brolang --cov-report=term

# Test specific file
PYTHONPATH=/home/izza/Projects/BroLang pytest tests/unit/test_lexer.py -v
```

**Persyaratan:** Python ≥ 3.10

---

## Lisensi

MIT License — lihat file LICENSE untuk detail.

---

## Kontribusi

Kontribusi selalu diterima! Silakan buka issue atau pull request di repository.
