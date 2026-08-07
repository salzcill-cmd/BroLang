<p align="center">
  <img src="https://img.shields.io/badge/version-5.4-blue?style=for-the-badge&logo=python&logoColor=white" alt="version"/>
  <img src="https://img.shields.io/badge/python-3.10+-green?style=for-the-badge&logo=python&logoColor=white" alt="python"/>
  <img src="https://img.shields.io/badge/license-MIT-orange?style=for-the-badge" alt="license"/>
  <img src="https://img.shields.io/badge/status-production%20ready-brightgreen?style=for-the-badge" alt="status"/>
</p>

<h1 align="center">BroLang v5.4</h1>

<p align="center">
  <b>Bahasa pemrograman buat yang males nulis syntax panjang</b><br>
  <sub>Sintaks Bahasa Indonesia, fitur lengkap, enak dipake</sub>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/473-Tests%20Passing-brightgreen?style=flat-square" alt="tests"/>
  <img src="https://img.shields.io/badge/110+-AST%20Nodes-blue?style=flat-square" alt="ast"/>
  <img src="https://img.shields.io/badge/130+Token%20Types-purple?style=flat-square" alt="tokens"/>
  <img src="https://img.shields.io/badge/28+-Stdlib%20Modules-orange?style=flat-square" alt="modules"/>
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
bro --version    # BroLang 5.4.0
echo 'tulis "Halo Dunia!"' > halo.bro
bro halo.bro
```

---

## Apa yang Baru di v5.4?

### Full Upgrade Library Game 🎮
Semua modul game di-*full update* — 14 modul game lengkap buat bikin game 2D ala Python Arcade/Pygame:

| Modul | Fitur baru |
|-------|-----------|
| `sprite` | **Diperbaiki total** (sebelumnya SyntaxError, ga bisa di-import!) — gambar, sprite sheet, animasi frame, rotasi, flip, alpha, z-order, collider kotak/lingkaran, GrupSprite |
| `partikel` 🆕 | Particle system: ledakan, hujan, semburan, emisi otomatis, gravitasi partikel |
| `ui` 🆕 | Tombol (hover+klik+callback), Label, Panel, Bar (health/progress bar) |
| `game` | Pause/resume, dt-clamp anti-lag, FPS display, background color, reset state |
| `input` | **Fix konflik event dengan game loop**, scroll wheel, mouse just-pressed, gamepad/joystick |
| `grafis` | Rounded rect, teks multi-baris, poligon bebas, ellipse, offscreen surface |
| `animasi` | **Fix easing elastic/bounce crash** + 26 jenis easing + callback on_selesai |
| `fisika` | Radius per-bodi (bukan hardcode 16), gravitasi configurable, ground detection |
| `tilemap` | **Fix solid_map** setelah bulk-load, `dari_file`, rendering warna fallback |
| `kamera` | Reset, pan, rotasi, batas world otomatis, `buat_layar_penuh` |
| `vektor` | Sudut derajat, `dari_polar`, proyeksi, refleksi, midpoint |
| `waktu` | Timer, Stopwatch, FPS counter, delta otomatis |

```
impor game
impor sprite
impor ui
impor partikel

buat pemain = sprite.Sprite(kosong, 100, 300, lebar=34, tinggi=40)
pemain.warna = "langit"
buat tombol = ui.Tombol("MULAI", 300, 330, 200, 60)
buat hp = ui.Bar(100, 100, 10, 42, 220, 18)
buat efek = partikel.buat_emiter(0, 0)
```

Coba game showcase lengkapnya:
```bash
bro examples/game_arena.bro
```
Platformer arena dengan tilemap solid, musuh patroli, tembakan, ledakan partikel, health bar, tombol menu, kamera shake, dan pause — semua pakai API baru.

### Interpreter: Atribut Objek Stdlib
Objek stdlib (Sprite, Vec2, ui, dll) sekarang bisa **diset atributnya** (`pemain.warna = "merah"`, `pemain.vel_x = 100`) — konsisten dengan transpiler yang sudah mendukungnya sebelumnya.

---

## Apa yang Baru di v5.3?

### Visualisasi Data (`visualisasi`)
```
impor visualisasi

buat penjualan = {"Senin": 12, "Selasa": 45, "Rabu": 23, "Kamis": 67, "Jumat": 34}

# Chart ASCII langsung di terminal
# Senin  │ ███████ 12
# Selasa │ ███████████████████████████ 45
# ...
tulis visualisasi.batang(penjualan, judul="Penjualan Mingguan", satuan="unit")

# Chart SVG + laporan HTML untuk dibuka di browser
buat svg = visualisasi.batang_svg(penjualan, judul="Penjualan Mingguan")
visualisasi.simpan_svg("penjualan.svg", svg)
visualisasi.simpan_html("laporan.html", [svg], judul="Laporan Penjualan")
```
Modul `visualisasi` menyediakan 5 jenis chart (bar, garis, pie/donut, scatter, histogram) dalam tiga format: **ASCII** buat tampil langsung di terminal, **SVG/HTML** buat laporan profesional, dan **GUI jendela native** buat tampilan ala game.

### GUI Chart (Pygame) 🎮
```
# pip install pygame-ce  (sekali saja)
impor visualisasi

buat chart1 = {"jenis": "batang", "data": [12, 45, 23], "judul": "Penjualan"}
buat chart2 = {"jenis": "kue", "data": {"A": 30, "B": 40}, "judul": "Pasar"}
visualisasi.tampilkan_jendela([chart1, chart2], judul="Dashboard")
```
Chart tampil di jendela gelap ala game: animasi masuk, hover tooltip, navigasi keyboard (panah ganti chart, `1-9` lompat, `F` fullscreen, `S` screenshot, `ESC` tutup). Data bisa berupa list nilai, list pasangan `[label, nilai]`, atau objek `{label: nilai}`.

---

## Apa yang Baru di v5.2?

### Keyword Arguments
```
fungsi sapa(nama, umur=0)
    kembali "Halo " + nama + " umur " + teks(umur)
selesai

tulis sapa(nama="Budi")              # Halo Budi umur 0
tulis sapa(nama="Ani", umur=25)     # Halo Ani umur 25
tulis sapa("Citra", umur=30)        # Halo Citra umur 30
```
Argumen bernama bikin pemanggilan fungsi lebih jelas & ga perlu inget urutan parameter. Bisa dipakai di fungsi, method, lambda, dan constructor kelas.

### Pipeline Operator (`|>`)
```
fungsi kali2(x)
    kembali x * 2
selesai

buat hasil = 21 |> kali2            # 42 — nilai dikirim ke fungsi berikutnya
buat genap = [1, 2, 3, 4] |> saring(lalu(x) x % 2 == 0)  # [2, 4]
buat plus1 = [1, 2, 3] |> peta(lalu(x) x + 1)           # [2, 3, 4]
```
Komposisi fungsi ala Elixir/F# — baca dari kiri ke kanan, ga perlu nested call.

### Destructuring Assignment
```
buat [a, b, c] = [1, 2, 3]
tulis a, b, c     # 1 2 3

buat {x, y} = {"x": 10, "y": 20}
tulis x, y        # 10 20
```
Unpacking list & objek langsung ke variabel, kayak Python/JS.

### Package Manager (BroPM)
```bash
bro pkg init                    # Bikin project + manifest brolang.json
bro pkg install <nama|git-url>  # Install package
bro pkg publish                 # Publish ke registry lokal
bro pkg search <kata>           # Cari package
```
```
impor paket-ku
tulis paket-ku.fungsi_utama()
```
Package manager beneran jalan: manifest `brolang.json`, install dari folder lokal / git URL / registry, dan package yang terinstall bisa langsung di-`impor` dari kode BroLang.

### Benchmark Command
```bash
bro benchmark <file>   # bandingkan Interpreter vs Transpiler vs Bytecode VM
bro bench <file>
```
Ukur performa ketiga mesin eksekusi BroLang dalam satu command.

### VM Optimasi
Bytecode VM sekarang punya builtin cache (fast path `LOAD_GLOBAL`/`CALL_BUILTIN`) plus perbaikan stack discipline `STORE_LOCAL`/`STORE_GLOBAL` yang bikin for-loop & assignment berjalan benar dan lebih cepat.

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

## Semua Fitur (v4.0 + v5.0 + v5.2 + v5.3 + v5.4)

### v5.4
- **Full upgrade library game** (14 modul): sprite ditulis ulang, `partikel` 🆕, `ui` 🆕, input event fix, tilemap fix, fisika radius configurable, kamera rotasi, 26 easing animasi, Timer/Stopwatch/FPS
- `examples/game_arena.bro`: showcase platformer (sprite + fisika + partikel + UI + tilemap + kamera)
- Interpreter: atribut objek stdlib bisa diset (`pemain.warna = "merah"`)

### v5.3
- Modul `visualisasi`: chart ASCII + SVG + HTML (bar, garis, pie, scatter, histogram)
- Export laporan: `simpan_svg`, `simpan_html`, `simpan_txt`
- **GUI chart (Pygame)**: `tampilkan_jendela` / `tampilkan_batang` / dll. + `simpan_png`
  - Jendela native ala game: animasi, tooltip, keyboard nav, fullscreen, screenshot

### v5.2
- Keyword arguments: `sapa(nama="Budi", umur=25)`
- Pipeline operator: `nilai |> fungsi`
- Destructuring assignment: `buat [a, b] = list` / `buat {x, y} = objek`
- Package manager: `bro pkg init/install/remove/list/search/publish/info`
- Package import: `impor <paket>` untuk package terinstall
- Benchmark CLI: `bro benchmark <file>`

### v5.0

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
impor game
impor grafis
impor input

game.buat_jendela(800, 600, "Game Pertamaku")
game.set_latar_warna("biru_gelap")

fungsi update(dt)
    jika input.tombol_baru_ditekan("SPACE") maka
        tulis "Lompat!"
    selesai
selesai

fungsi gambar(screen)
    grafis.segi_panjang(400, 300, 50, 50, "merah")
selesai

game.tambah_scene("utama", update, gambar)
game.ganti_scene("utama")
game.mulai()
```

Full API game (sprite, partikel, ui, fisika, tilemap, kamera, dll): baca [docs/GAME.md](docs/GAME.md). Contoh lengkap: `bro examples/game_arena.bro`.

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
| `partikel` | Particle system (ledakan, hujan, semburan) |
| `ui` | UI components (Tombol, Label, Panel, Bar) |
| `tes` | Test framework |
| `profil` | Performance profiler |
| `debugger` | Step-through debugging |
| `pencocok` | Regex patterns |
| `antrian` | Queue & priority queue |
| `tumpukan` | Stack data structure |
| `serialisasi` | JSON, base64, CSV |
| `dasar` | Base encoding utilities |
| `visualisasi` | Chart & grafik data (ASCII, SVG, HTML, GUI Pygame) |

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
bro benchmark <file>   # Benchmark interpreter vs transpiler vs VM
bro pkg <cmd>          # Package manager (init/install/publish/dll)
```

### Game Arena (showcase library game)

```bash
pip install pygame-ce                  # sekali saja, untuk semua modul game
bro examples/game_arena.bro            # platformer: sprite + fisika + partikel + UI + tilemap + kamera
```

### GUI Chart

```bash
pip install pygame-ce              # sekali saja, untuk jendela GUI chart
bro examples/visualisasi.bro       # tur lengkap: ASCII + HTML + buka jendela GUI
bro examples/visualisasi_gui.bro   # khusus jendela chart ala game
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

**473 test cases, semua passing!** (termasuk 61 test library game v5.4, output-consistency tests, suite v5.x, dan test visualisasi: ASCII, SVG, GUI)

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

> **BroLang v5.4** — Bahasa pemrograman buat yang males nulis syntax panjang 🇮🇩

<p align="center">
  <img src="https://img.shields.io/badge/Made%20with-Python-yellow?style=for-the-badge&logo=python&logoColor=white" alt="python"/>
  <img src="https://img.shields.io/badge/Made%20with-❤️-red?style=for-the-badge" alt="love"/>
</p>
