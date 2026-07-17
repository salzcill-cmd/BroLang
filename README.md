<div align="center">

# 🇮🇩 BroLang v3.0

### **Bahasa Pemrograman Indonesia yang Serius (Tapi Fun)**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-133%20Passed-brightgreen?style=for-the-badge)](#)
[![Version](https://img.shields.io/badge/Version-3.0-blue?style=for-the-badge)](#)

```
tulis "Halo Dunia!"    ← ini Bahasa BroLang, bukan Python ya bos
```

**BroLang itu bahasa pemrograman yang sintaksnya pake Bahasa Indonesia.**
**Jadi kalo kamu ngoding, rasanya kayak lagi ngetik chat WA tapi isinya program.**

<br>

[![Made with Love](https://img.shields.io/badge/Made_with_%E2%9D%A4_by_a_9th_grader-orange?style=for-the-badge)](#)

</div>

---

## 📋 Daftar Isi

| # | Topik | Link |
|---|-------|------|
| 🚀 | Instalasi | [→ Klik disini](#-instalasi) |
| ⚡ | Quick Start | [→ Klik disini](#-quick-start) |
| 📦 | Fitur v3.0 (Baru!) | [→ Klik disini](#-fitur-v30---yang-baru) |
| 🧱 | Dasar Bahasa | [→ Klik disini](#-dasar-bahasa) |
| 🔧 | Fungsi & Default Params | [→ Klik disini](#-fungsi) |
| 🎯 | Advanced Features | [→ Klik disini](#-advanced-features) |
| 🎮 | Game Development | [→ Klik disini](#-game-development) |
| 📚 | Standard Library | [→ Klik disini](#-standard-library) |
| 🛠️ | CLI Tools | [→ Klik disini](#-cli-tools) |
| 🏗️ | Arsitektur | [→ Klik disini](#-arsitektur) |

---

## 🚀 Instalasi

> **Syarat:** Python 3.10 ke atas. Kalo versi kamu di bawah itu, upgrade dulu ya bos.

```bash
# 1. Clone repo-nya
git clone https://github.com/salzcill-cmd/BroLang.git
cd BroLang

# 2. Install (editable mode, biar kalo update ga perlu install ulang)
pip install -e .

# 3. Cek apakah udah ke-install
bro --help
```

Kalo muncul info kayak gini, berarti udah sukses ✅

---

## ⚡ Quick Start

### Jalankan File

```bash
# Cara 1: langsung
bro contoh.bro

# Cara 2: pake perintah run
bro run contoh.bro
```

### Bikin File BroLang Pertama

Buat file `halo.bro`, terus isi kayak gini:

```
buat nama = "Bro"
tulis "Halo, " + nama + "! Selamat datang di BroLang!"
```

Terus jalankan:

```bash
bro halo.bro
```

Output:

```
Halo, Bro! Selamat datang di BroLang!
```

Gampang kan? 😎

---

## 📦 Fitur v3.0 — Yang Baru!

> **Versi 3.0 ini banyak banget fitur barunya.** Kayak HP upgrade dari Nokia ke Android gitu.

### ✅ Augmented Assignment

```
buat x = 5
x += 3       # x jadi 8
x -= 2       # x jadi 6
x *= 4       # x jadi 24
x /= 6       # x jadi 4.0
x %= 3       # x jadi 1.0
x **= 2      # x jadi 1.0
```

**Ga perlu nulis `x = x + 3` lagi, tinggal `x += 3` langsung jadi.** Singkat kan?

---

### 🔀 Ternary Expression

```
buat umur = 17
buat status = "Dewasa" jika umur >= 18 lainnya "Anak-anak"
tulis status  # Output: Anak-anak
```

**Satu baris langsung dapet hasilnya.** Ga perlu pake `jika...lainnya` yang panjang.

---

### 🌐 Global & Nonlocal

```
buat x = 10

fungsi ubah_x()
  global x          # akses variabel global
  x = 99
selesai

ubah_x()
tulis x             # Output: 99
```

**`global` = akses variabel dari luar fungsi.** Berguna banget kalo lagi bikin game.

---

### 🎯 Default Parameter Value

```
fungsi sapa(nama = "Dunia")
  tulis "Halo, " + nama + "!"
selesai

sapa()              # Output: Halo, Dunia!
sapa("Budi")        # Output: Halo, Budi!
```

**Parameter bisa pake nilai default.** Kalo ga dikasih, pake default-nya.

---

### 💥 Raise Statement (Lempar Error)

```
coba
  lempar "ada error nih!"
tangkap e
  tulis "Error: " + e
selesai

# Output: Error: ada error nih!
```

**`lempar`** itu kayak `raise` di Python. Buat nge-throw error sendiri.

---

### 🏁 Finally Block

```
coba
  tulis "buka file"
tangkap e
  tulis "error: " + e
akhirnya
  tulis "tutup file"        # ini JALAN terus, mau error atau ga
selesai
```

**`akhirnya`** itu kayak `finally` di Python. Pasti dijalankan, error atau ga.

---

### 📋 List Methods

```
buat angka = [3, 1, 2]
angka.tambah(4)           # [3, 1, 2, 4]
angka.urutkan()           # [1, 2, 3, 4]
angka.balik()             # [4, 3, 2, 1]
angka.hapus(4)            # [3, 2, 1]
angka.sisipkan(1, 99)     # [3, 99, 2, 1]
tulis angka.jumlah()      # 106 (3+99+2+1)
```

**Ga perlu pake `teks.gabung` atau cara ribet.** Tinggal `daftar.method()`.

---

### 📖 Dict Methods

```
buat orang = {"nama": "Budi", "umur": 17}
tulis orang.kunci()       # ["nama", "umur"]
tulis orang.nilai()       # ["Budi", 17]
tulis orang.item()        # [["nama","Budi"], ["umur",17]]
tulis orang.punya("nama")  # benar
```

**Dictionary makin gampang di-manage.**

---

### 🔢 Bitwise Operators

```
tulis 6 & 3       # 2 (AND)
tulis 6 | 3       # 7 (OR)
tulis 6 ^ 3       # 5 (XOR)
tulis 1 << 3      # 8 (LEFT SHIFT)
tulis 8 >> 1      # 4 (RIGHT SHIFT)
tulis ~0          # -1 (NOT)
```

**Berguna buat low-level programming atau kompetisi algorithm.**

---

## 🧱 Dasar Bahasa

### Tipe Data

| Tipe | Nama BroLang | Contoh |
|------|-------------|--------|
| Integer | `angka` | `42` |
| Float | `desimal` | `3.14` |
| String | `teks` | `"halo"` |
| Boolean | `boolean` | `benar`, `salah` |
| List | `list` | `[1, 2, 3]` |
| Dictionary | `objek` | `{"nama": "Budi"}` |
| Null | `kosong` | `kosong` |

```
tulis tipe(42)         # angka
tulis tipe("halo")     # teks
tulis tipe(benar)      # boolean
tulis tipe([1,2,3])    # list
tulis tipe(kosong)     # kosong
```

---

### Variabel

```
buat nama = "Budi"
buat umur = 17
buat tinggi = 170.5
buat siswa = benar
buat nilai = kosong

# Reassign (ga perlu "buat" lagi)
umur = 18

# Multi variable
buat a = 1, b = 2, c = 3
```

> **Catatan:** `buat` cuma dipake waktu pertama kali声明 variabel. Kalo mau ganti nilainya, tinggal tulis nama variabelnya aja.

---

### Operator

**Aritmatika:**

| Operator | Fungsi | Contoh |
|----------|--------|--------|
| `+` | Penjumlahan | `10 + 3 = 13` |
| `-` | Pengurangan | `10 - 3 = 7` |
| `*` | Perkalian | `10 * 3 = 30` |
| `/` | Pembagian | `10 / 3 = 3.333` |
| `%` | Modulo (sisa bagi) | `10 % 3 = 1` |
| `**` | Pangkat | `10 ** 3 = 1000` |

**Perbandingan:**

| Operator | Fungsi |
|----------|--------|
| `==` | Sama dengan |
| `!=` | Tidak sama dengan |
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

---

### Percabangan (If/Else)

```
buat nilai = 85

jika nilai >= 90 maka
    tulis "Grade A — Mantap!"
lainnya jika nilai >= 80 maka
    tulis "Grade B — Lumayan!"
lainnya jika nilai >= 70 maka
    tulis "Grade C — Masih oke"
lainnya
    tulis "Grade D — Belajar lagi ya"
selesai
```

---

### Perulangan

**For Loop:**

```
# Pake range
untuk i dalam range(5) lakukan
    tulis i
selesai
# Output: 0 1 2 3 4

# Pake list langsung
untuk buah dalam ["apel", "pisang", "jeruk"] lakukan
    tulis "Buah favorit: " + buah
selesai
```

**While Loop:**

```
buat i = 0
selama i < 5 lakukan
    tulis i
    i = i + 1
selesai
```

**Loop Control:**

```
# break — berhenti di tengah
untuk i dalam range(10) lakukan
    jika i == 5 maka
        hentikan
    selesai
    tulis i
selesai

# continue — skip satu iterasi
untuk i dalam range(5) lakukan
    jika i == 2 maka
        lanjutkan
    selesai
    tulis i
selesai
```

---

### String

```
buat s1 = "Hello"
buat s2 = 'World'
buat s3 = """Multi-line
string di BroLang"""

# Concatenation
buat s = "Halo " + "Dunia"

# Escape sequences
tulis "Baris 1\nBaris 2"
tulis "Tab\tselanjutnya"
```

---

### List

```
buat angka = [1, 2, 3, 4, 5]
tulis angka[0]          # 1
tulis angka[-1]         # 5
tulis jumlah(angka)     # 5 (panjang list)

# Nested list
buat matriks = [[1, 2], [3, 4]]
tulis matriks[0][1]     # 2
```

---

### Dictionary (Objek)

```
buat orang = {
    "nama": "Budi",
    "umur": 17,
    "jurusan": "Informatika"
}

tulis orang["nama"]              # Budi
orang["pekerjaan"] = "Programmer"  # Tambah field baru
```

---

## 🔧 Fungsi

```
fungsi sapa(nama)
    kembali "Halo " + nama + "!"
selesai

tulis sapa("Budi")  # Halo Budi!
```

### Default Parameter

```
fungsi tambah(a, b = 10)
    kembali a + b
selesai

tulis tambah(5)      # 15 (pake default b=10)
tulis tambah(5, 3)   # 8  (b=3)
```

### Recursive

```
fungsi faktorial(n)
    jika n <= 1 maka
        kembali 1
    lainnya
        kembali n * faktorial(n - 1)
    selesai
selesai

tulis faktorial(5)   # 120
```

### Lambda

```
buat tambah_dua = lalu(x) x + 2
tulis tambah_dua(5)  # 7

buat kali = lalu(a, b) a * b
tulis kali(3, 4)     # 12
```

---

## 🎯 Advanced Features

### List Comprehension

```
buat angka = [1, 2, 3, 4, 5]
buat genap = [x * 2 lalu x dalam angka]
tulis genap  # [2, 4, 6, 8, 10]

# Dengan filter
buat besar = [x lalu x dalam angka jika x > 3]
tulis besar  # [4, 5]
```

### F-String (Interpolasi String)

```
buat nama = "Budi"
buat umur = 17
tulis f"Halo {nama}, umur kamu {umur} tahun"
# Output: Halo Budi, umur kamu 17 tahun
```

### Enum

```
enum Warna {
    MERAH,
    BIRU,
    HIJAU
}

buat warna = Warna.MERAH
```

### Struct

```
struktur Pemain {
    nama,
    hp,
    skor
}

buat hero = Pemain("Budi", 100, 0)
tulis hero.nama  # Budi
tulis hero.hp    # 100
```

### Pattern Matching

```
buat x = 2

cocokkan x {
    1: tulis "satu"
    2: tulis "dua"
    3: tulis "tiga"
    _: tulis "lainnya"
}
```

### Error Handling

```
coba
    buat hasil = 10 / 0
tangkap error
    tulis "Error: " + error
selesai
```

---

## 🎮 Game Development

> **BroLang bisa bikin game pake Pygame!** Serius, bukan main-main.

### Persiapan

```bash
pip install pygame-ce
```

### Quick Start

```bash
# Bikin project game baru
bro new-game nama_game

# Jalankan game
bro run-game main.bro
```

### Modul Game

#### 🎨 `grafis` — Rendering 2D

```
impor grafis

grafis.mulai_jendela(800, 600, "Gameku")
grafis.bersihkan("hitam")

# Gambar bentuk
grafis.segi_panjang(100, 100, 50, 50, "biru")
grafis.lingkaran(400, 300, 30, "merah")
grafis.garis(0, 0, 800, 600, "putih", 2)

# Teks
grafis.tulis_teks("Skor: 100", 10, 10, "kuning", 32)

# Gambar/Sprite
buat img = grafis.muat_gambar("assets/player.png")
grafis.gambar_gambar(img, 100, 200)

# Deteksi tabrakan
grafis.tabrakan_segi_panjang(x1, y1, w1, h1, x2, y2, w2, h2)

grafis.perbarui()
```

#### 🎵 `audio` — Sound & Musik

```
impor audio

audio.muat_musik("assets/bgm.mp3")
audio.mainkan_musik()
audio.atur_volume_musik(0.5)

buat sfx = audio.muat_suara("assets/tembak.wav")
audio.mainkan_suara(sfx)
```

#### ⌨️ `input` — Keyboard & Mouse

```
impor input

# Keyboard
jika input.tombol_ditekan("LEFT") maka
    #Gerak ke kiri
selesai

# Mouse
buat posisi = input.tikus_posisi()
jika input.tikus_tombol_ditekan(0) maka
    # Klik kiri
selesai
```

#### 🕐 `game` — Game Loop

```
impor game

game.buat_jendela(800, 600, "Gameku")
game.atur_fps(60)

game.tambah_scene("menu", update_menu, gambar_menu)
game.ganti_scene("menu")
game.mulai()
```

### Contoh Game

Cek folder `games/` untuk contoh game yang udah jadi:

| Game | Deskripsi |
|------|-----------|
| `space_defender.bro` | Game shoot 'em up — tembak-tembakan di luar angkasa |

```bash
bro run games/space_defender.bro
```

---

## 📚 Standard Library

### `matematika` — Matematika

```
impor matematika

matematika.akar(25)          # 5.0
matematika.sin(3.14/2)       # 0.999...
matematika.absolut(-5)       # 5
matematika.faktorial(5)      # 120
matematika.pi()              # 3.14159...
matematika.max(10, 20)       # 20
matematika.min(10, 20)       # 10
```

### `teks` — String Manipulation

```
impor teks

teks.upper("hello")              # HELLO
teks.lower("HELLO")              # hello
teks.kapital("hello world")      # Hello world
teks.potong("a,b,c", ",")        # ["a", "b", "c"]
teks.ganti("hello", "l", "x")    # hexxo
teks.cari("hello", "el")         # 1
teks.strip("  hi  ")             # hi
```

### `waktu` — Waktu

```
impor waktu

waktu.sekarang()             # "2026-06-06T12:00:00"
waktu.tidur(1)               # Tunggu 1 detik
waktu.tanggal()              # "2026-06-06"
waktu.jam()                  # "12:00:00"
```

### `file` — File Operations

```
impor file

file.baca("data.txt")
file.tulis("output.txt", "konten")
file.tambah("log.txt", "baris baru")
file.ada("data.txt")
file.hapus("sampah.txt")
```

### `json` — JSON

```
impor json

json.parsing('{"nama": "Budi"}')
json.string({"nama": "Budi"})
json.baca("data.json")
json.tulis("data.json", {"key": "val"})
```

### `jaringan` — HTTP Request

```
impor jaringan

hasil = jaringan.dapatkan("https://api.example.com")
tulis hasil.status
tulis hasil.data
```

### `acak` — Random

```
impor acak

acak.bulat(1, 100)                        # 42
acak.pilih(["merah", "biru", "hijau"])    # "biru"
acak.acak_list([1,2,3,4,5])              # [3, 1, 5, 2, 4]
```

---

## 🛠️ CLI Tools

```bash
bro                         # Info singkat
bro contoh.bro              # Jalankan file
bro run contoh.bro          # Jalankan file (explicit)
bro build contoh.bro        # Kompilasi ke Python
bro build contoh.bro -o out.py  # Simpan hasil kompilasi
bro repl                    # REPL interaktif
bro fmt contoh.bro          # Format kode
bro fmt contoh.bro --check  # Cek format (jangan diubah)
bro lint contoh.bro         # Analisis statis / cek error
bro new-game nama_game      # Bikin project game baru
bro run-game main.bro       # Jalankan game
bro version                 # Cek versi
bro --help                  # Bantuan
```

### Format Kode

```bash
bro fmt contoh.bro          # Auto-format
bro fmt contoh.bro --check  # Cek doang
```

### Linter

```bash
bro lint contoh.bro
```

| Aturan | Severity | Deskripsi |
|--------|----------|-----------|
| `line-length` | warning | Maks 100 karakter per baris |
| `trailing-whitespace` | info | Ga boleh ada spasi di akhir baris |
| `indentation` | warning | Spasi 4, bukan tab |
| `naming-convention` | info | Minimal 2 karakter |

---

## 🏗️ Arsitektur

```
┌─────────────┐    ┌───────────┐    ┌──────────┐    ┌───────────┐    ┌───────────┐
│ Source Code  │───▶│   Lexer   │───▶│  Parser  │───▶│ Semantic  │───▶│ Interpreter│
│   (.bro)     │    │           │    │          │    │ Analyzer  │    │           │
└─────────────┘    └───────────┘    └──────────┘    └───────────┘    └───────────┘
                                                                        
                                                  ┌───────────┐    
                                                  │ Optimizer │──── (optional)    
                                                  └───────────┘    
```

| Tahap | Fungsi |
|-------|--------|
| **Lexer** | Pecah source code jadi token. Support Unicode, indent/dedent, komentar |
| **Parser** | Ubah token stream jadi AST (Abstract Syntax Tree) |
| **Semantic Analyzer** | Validasi semantik: cek variabel, tipe, scope |
| **Optimizer** | Constant folding, algebraic simplification, dead code elimination |
| **Interpreter** | Eksekusi AST pake visitor pattern |

### Compiler Pipeline

```
Source Code → Lexer → Parser → AST → Compiler → Python AST → Python Bytecode
```

Kompilasi ke Python murni, bisa dijalankan tanpa BroLang.

---

## 🧪 Testing

```bash
# Jalankan semua test
python -m pytest tests/ -x -q

# Dengan verbose
python -m pytest tests/ -v

# Coverage
python -m pytest tests/ --cov=brolang --cov-report=term
```

**133 tests — semua passed.** Ga ada yang fail. ✅

---

## 📂 Contoh Program

Lihat folder `examples/` untuk contoh-contoh program:

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
| `v2_demo.bro` | Demo fitur v2 |

---

## 🤝 Kontribusi

```
1. Fork repository ini
2. Buat branch baru: git checkout -b fitur-baru
3. Commit perubahan: git commit -m "tambah fitur X"
4. Push ke branch: git push origin fitur-baru
5. Buka Pull Request
```

---

## 📄 Lisensi

MIT License — bebas dipake, dimodif, disebar.

---

<div align="center">

**Dibuat dengan ❤️ oleh anak kelas 9 SMP yang kebanyakan ngoding**

*"Bahasa Indonesia itu keren, makanya saya bikin bahasa pemrogramannya pake Indonesia juga."*

<br>

![Visitor Count](https://komarev.com/ghpvc/?username=salzcill-cmd&color=blue&style=for-the-badge)

</div>
