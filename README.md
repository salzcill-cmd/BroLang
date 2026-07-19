<p align="center">
  <img src="https://img.shields.io/badge/version-4.0-blue?style=for-the-badge&logo=python&logoColor=white" alt="version"/>
  <img src="https://img.shields.io/badge/python-3.10+-green?style=for-the-badge&logo=python&logoColor=white" alt="python"/>
  <img src="https://img.shields.io/badge/license-MIT-orange?style=for-the-badge" alt="license"/>
  <img src="https://img.shields.io/badge/status-production%20ready-brightgreen?style=for-the-badge" alt="status"/>
</p>

<h1 align="center">BroLang v4.0</h1>

<p align="center">
  <b>Bahasa pemrograman profesional untuk game development 🇮🇩</b><br>
  <sub>Sintaks Bahasa Indonesia + fitur modern setara Python/TypeScript</sub>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/164-Tests%20Passing-brightgreen?style=flat-square" alt="tests"/>
  <img src="https://img.shields.io/badge/80+-AST%20Nodes-blue?style=flat-square" alt="ast"/>
  <img src="https://img.shields.io/badge/100+-Token%20Types-purple?style=flat-square" alt="tokens"/>
  <img src="https://img.shields.io/badge/25+-Stdlib%20Modules-orange?style=flat-square" alt="modules"/>
</p>

---

## Quick Start

```bash
# Clone & install
git clone https://github.com/salzcill-cmd/BroLang.git
cd BroLang
pip install -e .

# Jalankan program pertama
echo 'tulis "Halo Dunia!"' > halo.bro
bro halo.bro
```

---

## Fitur Baru v4.0

### Async/Await
```
asinkron fungsi ambil_data(url)
    buat data = tunggu http_get(url)
    kembali data
selesai
```

### Generators
```
fungsi counter(n)
    i = 0
    selagi i < n
        hasilkan i
        i = i + 1
selesai

buat gen = counter(5)
tulis gen   # 0, 1, 2, 3, 4
```

### Decorators
```
@dekoratorku
fungsi sapa()
    tulis "Halo!"
selesai
```

### Match/Case
```
cocokkan warna {
    "merah": tulis "Api"
    "biru": tulis "Air"
    _: tulis "Lainnya"
}
```

### Context Manager
```
dengan buka("data.txt") sebagai f
    buat isi = baca(f)
    tulis isi
selesai
```

### Typed Exceptions
```
coba
    buat x = 10 / 0
kecuali ZeroDivisionError sebagai err
    tulis "Error: " + str(err)
kecuali lainnya
    tulis "Error tak dikenal"
selesai
```

### Lambda & Comprehension
```
buat kuadrat = lalu(x) x * x
buat angka = [1, 2, 3, 4, 5]
buat genap = [x * 2 lalu x dalam angka jika x % 2 == 0]
tulis genap   # [4, 8]
```

### Enum & Struct
```
enum Warna { MERAH, BIRU, HIJAU }
struktur Posisi { x, y }
```

### String Methods
```
buat teks = "Hello World"
tulis teks.atas()        # HELLO WORLD
tulis teks.cocok("World") # True
tulis teks.ganti("World", "BroLang")  # Hello BroLang
tulis teks.potong(" ")   # ["Hello", "World"]
```

---

## Contoh Program

### Hello World
```
tulis "Halo Dunia!"
```

### Variabel & Operasi
```
buat nama = "Budi"
buat umur = 17
tulis "Nama: " + nama + ", Umur: " + teks(umur)
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

### Class & OOP
```
class Mahasiswa
    fungsi init(nama, nim)
        ini.nama = nama
        ini.nim = nim
    selesai

    fungsi info()
        tulis ini.nama + " - " + ini.nim
    selesai
selesai

buat mhs = Mahasiswa("Budi", "12345")
mhs.info()
```

### Game Development
```
impor grafis

grafis.buat_layar(800, 600)

selama benar
    grafis.mulai_frame()
    grafis.isi_layar(0, 0, 0)
    grafis.gambar_kotak(400, 300, 50, 50, 0, 100, 255)
    grafis.selesai_frame()
selesai
```

---

## Standard Library (25+ modules)

| Module | Deskripsi |
|--------|-----------|
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

| Dokumentasi | Keterangan |
|------------|-----------|
| [Quick Start](docs/QUICKSTART.md) | Tutorial singkat |
| [Dasar Bahasa](docs/DASAR.md) | Tipe data, variabel, operator |
| [Fungsi](docs/FUNGSI.md) | Fungsi, lambda, closures |
| [Class & OOP](docs/OOP.md) | OOP & inheritance |
| [Fitur v4.0](docs/FITUR.md) | Semua fitur lengkap |
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
bro new-game <nama>    # Buat proyek game
bro run-game <file>    # Jalankan game
```

---

## Arsitektur

```
Source Code (.bro)
    ↓
┌─────────┐
│  Lexer  │ ← Tokenisasi (100+ tokens)
└─────────┘
    ↓
┌──────────┐
│  Parser  │ ← Bikin AST (80+ nodes)
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

# Jalankan test spesifik
python3 -m pytest tests/unit/test_v4_language.py -v
```

**164 test cases, semua passing!**

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

> **BroLang v4.0** — Bahasa pemrograman profesional untuk generasi muda Indonesia 🇮🇩

<p align="center">
  <img src="https://img.shields.io/badge/Made%20with-Python-yellow?style=for-the-badge&logo=python&logoColor=white" alt="python"/>
  <img src="https://img.shields.io/badge/Made%20with-❤️-red?style=for-the-badge" alt="love"/>
</p>
