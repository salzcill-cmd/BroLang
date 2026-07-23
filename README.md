<p align="center">
  <img src="https://img.shields.io/badge/version-5.0-blue?style=for-the-badge&logo=python&logoColor=white" alt="version"/>
  <img src="https://img.shields.io/badge/python-3.10+-green?style=for-the-badge&logo=python&logoColor=white" alt="python"/>
  <img src="https://img.shields.io/badge/license-MIT-orange?style=for-the-badge" alt="license"/>
  <img src="https://img.shields.io/badge/status-production%20ready-brightgreen?style=for-the-badge" alt="status"/>
</p>

<h1 align="center">BroLang v5.0</h1>

<p align="center">
  <b>Bahasa pemrograman buat yang males nulis syntax panjang</b><br>
  <sub>Sintaks Bahasa Indonesia, fitur lengkap, enak dipake</sub>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/223-Tests%20Passing-brightgreen?style=flat-square" alt="tests"/>
  <img src="https://img.shields.io/badge/110+-AST%20Nodes-blue?style=flat-square" alt="ast"/>
  <img src="https://img.shields.io/badge/130+Token%20Types-purple?style=flat-square" alt="tokens"/>
  <img src="https://img.shields.io/badge/25+-Stdlib%20Modules-orange?style=flat-square" alt="modules"/>
</p>

---

## Quick Start

### Cara 1: Install dengan script (recommended)
```bash
git clone https://github.com/salzcill-cmd/BroLang.git
cd BroLang
chmod +x install.sh
./install.sh
```

### Cara 2: Install manual
```bash
git clone https://github.com/salzcill-cmd/BroLang.git
cd BroLang
pip install -e .
```

### Cara 3: Install langsung dari GitHub
```bash
pip install git+https://github.com/salzcill-cmd/BroLang.git
```

### Cek apakah udah jalan
```bash
bro --version    # BroLang 5.0.0
echo 'tulis "Halo Dunia!"' > halo.bro
bro halo.bro
```

---

## Apa yang Baru di v5.0?

### Null Coalescing (`??`)
```
buat nama = kosong
tulis nama ?? "Anonim"   # Anonim
```
Kalo nilainya `kosong`, otomatis ganti ke default. Ga perlu nulis `jika` panjang-panjang.

### Higher-Order Functions
```
buat angka = [1, 2, 3, 4, 5]
tulis peta(angka, lalu(x) x * 2)     # [2, 4, 6, 8, 10]
tulis saring(angka, lalu(x) x > 3)   # [4, 5]
tulis kurangi(angka, lalu(a, b) a + b, 0)  # 15
```
`peta`, `saring`, `kurangi` — fungsi tinggi level kayak di Python tapi pake bahasa Indonesia.

### Result & Option Types
```
buat hasil = Benar(42)
buat error = Salah("ada yang salah")

buat nilai = Ada(100)
buat kosong = Kosong()
```
Buat handle error dengan rapi, mirip Rust tapi versi santai.

### Macros
```
makro Logger()
    tulis "[LOG] Program jalan!"
selesai

Logger()
```
Bikin macro gampang, tinggal `makro` terus isi badannya.

### Namespaces
```
ruang nama Matematika
    fungsi tambah(a, b)
        kembali a + b
    selesai
selesai

pakai Matematika
tulis Matematika.tambah(2, 3)   # 5
```
Organisasi kode biar ga berantakan.

### For-Each
```
buat buah = ["apel", "mangga", "jeruk"]
untuk setiap item dalam buah lakukan
    tulis item
selesai
```
Lebih pendek dari `untuk i dalam range(...)`.

### Interfaces
```
antarmuka DapatJalankan {
    fungsi jalankan()
}

kelas Robot(DapatJalankan)
    fungsi jalankan()
        tulis "Robot jalan!"
    selesai
selesai
```
Kalo ga implement method wajib, langsung error.

### Abstract Classes
```
abstrak kelas Hewan {
    fungsi suara()
}

buat hewan = Hewan()  # error! ga bisa langsung bikin instance
```
Harus diwarisi dulu sebelum bisa dipake.

### Access Modifiers
```
kelas Keamanan
    privat fungsi rahasia()
        tulis "jangan liat!"
    selesai

    fungsi buka()
        self.rahasia()  # bisa dari dalam kelas
    selesai
selesai

buat k = Keamanan()
k.buka()        # bisa
k.rahasia()     # error! privat
```
`privat` beneran diproteksi, `publik` bisa diakses dari mana aja, `terlindungi` cuma bisa dari kelas turunan.

### Chained Comparisons
```
buat x = 5
jika 0 < x < 10 maka
    tulis "dalam range"
selesai
```
Ga perlu pake `dan` lagi buat range checking.

### Generators
```
fungsi gen_sampai(n)
    buat i = 0
    selama i < n lakukan
        hasilkan i
        i = i + 1
    selesai
selesai

untuk angka dalam gen_sampai(5) lakukan
    tulis(angka)
selesai
```
`hasilkan` bikin fungsi jadi generator — value dikirim satu per satu.

### Iterator Protocol
```
kelas Rentang
    fungsi __init__(mulai, akhir)
        self.mulai = mulai
        self.akhir = akhir
    selesai

    fungsi __iter__()
        self._current = self.mulai
        kembali self
    selesai

    fungsi __next__()
        jika self._current >= self.akhir maka
            hentikan_iterasi()
        selesai
        buat val = self._current
        self._current = self._current + 1
        kembali val
    selesai
selesai
```
Bikin objek iterable sendiri pake `__iter__`/`__next__`, sama kayak Python.

### Properties (Getter/Setter)
```
kelas Suhu
    fungsi __init__(derajat)
        self._derajat = derajat
    selesai

    fungsi _derajat()
        kembali self._derajat
    selesai

    fungsi _derajat_set(nilai)
        self._derajat = nilai
    selesai
selesai

buat s = Suhu(36)
tulis(s.get("derajat"))     # 36
s.set("derajat", 37)
tulis(s.get("derajat"))     # 37
```
Convention: `_<nama>()` buat getter, `_<nama>_set(v)` buat setter.

### Static Methods
```
kelas Kalkulator
    statis fungsi tambah(a, b)
        kembali a + b
    selesai
selesai

tulis(Kalkulator.tambah(3, 4))  # 7
```
`statis` bikin method bisa dipanggil tanpa bikin instance.

### String Interpolation
```
buat nama = "Bro"
buat umur = 5

# Dollar variable
tulis("Halo $nama, umur $umur tahun!")

# Dollar expression
tulis("2 + 3 = ${2 + 3}")

# F-string
tulis(f"Halo {nama}, umur {umur} tahun!")
```
Dua cara: `$variable` buat simpel, `f"..."` buat expression.

### Type Checking
```
tulis(cek_tipe(42))          # int
tulis(cek_tipe(42, "angka")) # True
pastikan(42 == 42, "Harus sama!")  # assert
```

---

## Semua Fitur (v4.0 + v5.0)

### Basic
- `buat` variabel, `fungsi`, `kelas`, `muat` module
- Tipe data: angka, teks, boolean, list, tuple, set, objek, kosong
- Operator: aritmatika, perbandingan, logika, bitwise
- Percabangan: `jika...maka...lainnya...selesai`
- Perulangan: `untuk`, `selama`, `hentikan`, `lanjutkan`

### Functions
- Default parameters, lambda (`lalu`), closures
- List comprehension, keyword arguments, argument labels
- Variadic functions (`...`), recursion

### OOP
- Class, inheritensi, `super()`, dataclass
- Multiple inheritance, property

### Advanced
- `try...kecuali...selesai` error handling
- `lempar` exception, `final` block
- `global` / `nonlokal` scope
- `cocokkan` (match/case), dekorator
- Async/await, generators, context manager
- Enum, struct, ternary expression

### v5.0
- Null coalescing `??`
- Higher-order functions (`peta`, `saring`, `kurangi`)
- Result & Option types (`Benar`/`Salah`, `Ada`/`Kosong`)
- Macros (`makro`)
- Namespaces (`ruang nama` + `pakai`)
- Interfaces (`antarmuka`)
- Abstract classes (`abstrak kelas`)
- Access modifiers (`publik`, `privat`, `terlindungi`)
- For-each (`untuk setiap ... dalam ... lakukan`)
- Chained comparisons (`0 < x < 10`)
- Generators (`hasilkan`)
- Iterator protocol (`__iter__`/`__next__`/`hentikan_iterasi()`)
- Properties (`_<nama>()` getter, `_<nama>_set(v)` setter)
- Static methods (`statis fungsi`)
- String interpolation (`$variable` / `f"..."`)
- Type checking (`cek_tipe`/`pastikan`)
- Class inheritance syntax (`kelas Nama(Parent)`)

---

## Contoh Program

### Hello World
```
tulis "Halo Dunia!"
```

### Fungsi & Lambda
```
fungsi tambah(a, b)
    kembali a + b
selesai

buat kali2 = lalu(x) x * 2
tulis tambah(10, 5)     # 15
tulis kali2(10)         # 20
```

### Class
```
kelas Mahasiswa
    fungsi __init__(nama, nim)
        self.nama = nama
        self.nim = nim
    selesai

    fungsi info()
        tulis(self.nama + " - " + self.nim)
    selesai
selesai

buat mhs = Mahasiswa("Budi", "12345")
mhs.info()
```

### Higher-Order Functions
```
buat angka = [1, 2, 3, 4, 5]
buat genap = saring(angka, lalu(x) x % 2 == 0)
tulis genap    # [2, 4]

buat kali3 = peta(angka, lalu(x) x * 3)
tulis kali3    # [3, 6, 9, 12, 15]
```

### Result Handling
```
fungsi bagi(a, b)
    jika b == 0 maka
        kembali Salah("bagi dengan nol!")
    selesai
    kembali Benar(a / b)
selesai

buat hasil = bagi(10, 2)
tulis hasil    # 5.0
```

### Game Development
```
muat grafis

grafis.buat_layar(800, 600)

selama benar lakukan
    grafis.mulai_frame()
    grafis.isi_layar(0, 0, 0)
    grafis.gambar_kotak(400, 300, 50, 50, 0, 100, 255)
    grafis.selesai_frame()
selesai
```

---

## Standard Library (25+ modules)

| Module | Fungsi |
|--------|--------|
| `matematika` | Fungsi matematika |
| `teks` | Manipulasi string |
| `acak` | Random number |
| `waktu` | Waktu & sleep |
| `sistem` | OS interaction |
| `file` | File I/O |
| `jaringan` | HTTP client |
| `database` | SQLite wrapper |
| `json` | JSON parse/serialize |
| `game` | Game loop & scene |
| `grafis` | 2D graphics (SDL2) |
| `input` | Keyboard & mouse |
| `audio` | Sound effects |
| `vektor` | Vektor 2D/3D |
| `sprite` | Sprite system |
| `animasi` | Animation & tweens |
| `tilemap` | Tilemap support |
| `kamera` | Camera system |
| `fisika` | Physics engine |
| `tes` | Test framework |
| `profil` | Performance profiler |
| `debugger` | Step-through debugging |
| `pencocok` | Regex patterns |
| `antrian` | Queue & priority queue |
| `tumpukan` | Stack data structure |
| `serialisasi` | JSON, base64, CSV |
| `dasar` | Base encoding utilities |

---

## Dokumentasi

| Dokumentasi | Isinya |
|------------|--------|
| [Instalasi](docs/INSTALASI.md) | Cara install BroLang |
| [Quick Start](docs/QUICKSTART.md) | Tutorial singkat |
| [Dasar Bahasa](docs/DASAR.md) | Tipe data, variabel, operator |
| [Fungsi](docs/FUNGSI.md) | Fungsi, lambda, closures |
| [Class & OOP](docs/OOP.md) | OOP & inheritance |
| [Fitur v5.0](docs/FITUR.md) | Semua fitur lengkap |
| [Game Development](docs/GAME.md) | Bikin game pake BroLang |
| [Standard Library](docs/STDLIB.md) | 25+ module built-in |
| [CLI Tools](docs/CLI.md) | Compiler, formatter, profiler |
| [Arsitektur](docs/ARSITEKTUR.md) | Pipeline eksekusi |

---

## CLI Commands

```bash
bro run <file>         # Jalankan file .bro
bro build <file>       # Compile ke Python
bro repl               # REPL interaktif
bro test [file]        # Jalankan tes
bro profile <file>     # Profil eksekusi
bro lint <file>        # Analisis kode statis
bro fmt <file>         # Format kode
bro doc [topik]        # Dokumentasi
bro new-game <nama>    # Bikin proyek game baru
bro run-game <file>    # Jalankan game
```

---

## Arsitektur

```
Source Code (.bro)
    ↓
┌─────────┐
│  Lexer  │ ← Tokenisasi (130+ tokens)
└─────────┘
    ↓
┌──────────┐
│  Parser  │ ← Bikin AST (110+ nodes)
└──────────┘
    ↓
┌─────────────────────┐
│ SemanticAnalyzer    │ ← Cek tipe & scope
└─────────────────────┘
    ↓
┌────────────┐
│ Optimizer  │ ← Dead code elim, constant folding
└────────────┘
    ↓
┌─────────────┐
│ Interpreter │ ← Eksekusi langsung
└─────────────┘
    ↓
┌─────────┐
│ Output  │
└─────────┘
```

---

## Testing

```bash
# Jalankan semua test
python3 -m pytest tests/ -v

# Cuma test v5.0
python3 -m pytest tests/unit/test_v5_language.py -v
```

**189 test cases, semua passing!** (164 v4.0 + 25 v5.0)

---

## Kontribusi

1. Fork repo ini
2. Buat branch baru (`git checkout -b fitur-baru`)
3. Commit perubahan (`git commit -m "tambah fitur baru"`)
4. Push ke branch (`git push origin fitur-baru`)
5. Buka Pull Request

---

## License

MIT License — Bebas pake, dimodif, disebar.

---

## Credits

Dibuat dengan ❤️ oleh [salzcill-cmd](https://github.com/salzcill-cmd)

> **BroLang v5.0** — Bahasa pemrograman buat yang males nulis syntax panjang 🇮🇩

<p align="center">
  <img src="https://img.shields.io/badge/Made%20with-Python-yellow?style=for-the-badge&logo=python&logoColor=white" alt="python"/>
  <img src="https://img.shields.io/badge/Made%20with-❤️-red?style=for-the-badge" alt="love"/>
</p>
