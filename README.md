<p align="center">
  <img src="https://img.shields.io/badge/version-3.1-blue?style=for-the-badge&logo=python&logoColor=white" alt="version"/>
  <img src="https://img.shields.io/badge/python-3.10+-green?style=for-the-badge&logo=python&logoColor=white" alt="python"/>
  <img src="https://img.shields.io/badge/license-MIT-orange?style=for-the-badge" alt="license"/>
  <img src="https://img.shields.io/badge/status-stable-brightgreen?style=for-the-badge" alt="status"/>
</p>

<h1 align="center">BroLang</h1>

<p align="center">
  <b>Bahasa pemrograman kekinian pake bahasa Indonesia 🇮🇩</b><br>
  <sub>Cocok buat belajar coding secara fun & gampang!</sub>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/133-Tests%20Passing-brightgreen?style=flat-square" alt="tests"/>
  <img src="https://img.shields.io/badge/60+-AST%20Nodes-blue?style=flat-square" alt="ast"/>
  <img src="https://img.shields.io/badge/80+-Token%20Types-purple?style=flat-square" alt="tokens"/>
  <img src="https://img.shields.io/badge/20+-Modules-orange?style=flat-square" alt="modules"/>
</p>

---

## ⚡ Quick Start

```bash
# 1. Clone repo-nya
git clone https://github.com/salzcill-cmd/BroLang.git
cd BroLang

# 2. Install
pip install -e .

# 3. Jalankan program pertama kamu
echo 'tulis "Halo Dunia!"' > halo.bro
bro halo.bro
```

Output:
```
Halo Dunia!
```

---

## 📖 Contoh Program

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

### List & Comprehension
```
buat angka = [1, 2, 3, 4, 5]
buat genap = [x untuk x dalam angka jika x % 2 == 0]
tulis genap    # [2, 4]

# Slicing
tulis angka[1:4]    # [2, 3, 4]
tulis angka[::2]    # [1, 3, 5]
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

## 📚 Dokumentasi

> **Pilih topik yang mau kamu pelajari.**

### 🚀 Mulai Dari Sini
| Dokumentasi | Keterangan |
|------------|-----------|
| [Instalasi](docs/INSTALASI.md) | Cara install & setup BroLang |
| [Quick Start](docs/QUICKSTART.md) | Tutorial singkat buat pemula |

### 🧱 Belajar Bahasa
| Dokumentasi | Keterangan |
|------------|-----------|
| [Dasar Bahasa](docs/DASAR.md) | Tipe data, variabel, operator, control flow |
| [Fungsi](docs/FUNGSI.md) | Fungsi, lambda, closures, comprehension |
| [Class & OOP](docs/OOP.md) | OOP, inheritensi, dataclass |

### 🔥 Fitur Lengkap
| Dokumentasi | Keterangan |
|------------|-----------|
| [Fitur BroLang](docs/FITUR.md) | Semua fitur v3.1 (lengkap!) |

### 🎮 Development
| Dokumentasi | Keterangan |
|------------|-----------|
| [Game Development](docs/GAME.md) | Bikin game pake BroLang |
| [Standard Library](docs/STDLIB.md) | 20+ module built-in |
| [CLI Tools](docs/CLI.md) | Compiler, formatter, debug mode |

### 🏛️ Arsitektur
| Dokumentasi | Keterangan |
|------------|-----------|
| [Arsitektur](docs/ARSITEKTUR.md) | Pipeline eksekusi, struktur project |

---

## 🧩 Fitur Utama

### Bahasa Dasar
- **Variabel** — `buat x = 10`
- **Fungsi** — `fungsi nama() ... selesai`
- **Lambda** — `lalu(x) x * 2`
- **Class** — `class Nama ... selesai`
- **Control Flow** — `jika...maka`, `selama...lakukan`, `untuk...lakukan`

### Tipe Data
- **Primitif** — Angka, Teks, Boolean, Kosong
- **Collection** — List, Tuple, Set, Objek (Dict)

### Operator
- **Aritmatika** — `+ - * / % **`
- **Perbandingan** — `== != > < >= <= is dalam`
- **Logika** — `dan atau bukan`
- **Bitwise** — `& | ^ ~ << >>`

### Advanced Features
- **Closures** — Lambda/fungsi nangkep variabel luar
- **Ternary** — `"a" jika kondisi lainnya "b"`
- **Chained Comparison** — `1 < x < 10`
- **List Comprehension** — `[x untuk x dalam list]`
- **For-Else / While-Else** — Else di loop
- **Slicing** — `list[1:3]`, `list[::2]`

### Error Handling
- **Try/Catch** — `try...kecuali...selesai`
- **Raise** — `lempar "error"`
- **Finally** — `final`

### OOP
- **Inheritensi** — `class Anak(OrangTua)`
- **Dataclass** — `@dataclass class X`
- **Super** — `super.init(args)`

### Game Dev
- **Grafis** — 2D graphics (SDL2)
- **Audio** — Sound effects
- **Input** — Keyboard/mouse
- **Game Utilities** — Collision, input handling

---

## 🏗️ Arsitektur

```
Source Code (.bro)
    ↓
┌─────────┐
│  Lexer  │ ← Tokenisasi (80+ tokens)
└─────────┘
    ↓
┌──────────┐
│  Parser  │ ← Bikin AST (60+ nodes)
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

## 🧪 Testing

```bash
# Jalankan semua test
python -m pytest tests/ -v

# Jalankan test spesifik
python -m pytest tests/test_core_language.py -v
```

**133 test cases, semua passing!**

---

## 🤝 Kontribusi

Mau kontribusi ke BroLang? Gampang banget:

1. Fork repo ini
2. Buat branch baru (`git checkout -b fitur-baru`)
3. Commit perubahan (`git commit -m "tambah fitur baru"`)
4. Push ke branch (`git push origin fitur-baru`)
5. Buka Pull Request

**Pastikan semua test masih passing sebelum submit PR!**

---

## 📝 License

MIT License — Bebas pake, dimodif, disebar.

---

## 🙏 Credits

Dibuat dengan ❤️ oleh [salzcill-cmd](https://github.com/salzcill-cmd)

> **BroLang** — Bahasa pemrograman buat generasi muda Indonesia 🇮🇩

<p align="center">
  <img src="https://img.shields.io/badge/Made%20with-Python-yellow?style=for-the-badge&logo=python&logoColor=white" alt="python"/>
  <img src="https://img.shields.io/badge/Made%20with-❤️-red?style=for-the-badge" alt="love"/>
</p>
