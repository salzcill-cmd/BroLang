<p align="center">
  <img src="https://img.shields.io/pypi/v/brolang?style=for-the-badge&logo=pypi&logoColor=white" alt="PyPI"/>
  <img src="https://img.shields.io/badge/python-3.10+-green?style=for-the-badge&logo=python&logoColor=white" alt="python"/>
  <img src="https://img.shields.io/badge/license-MIT-orange?style=for-the-badge" alt="license"/>
  <img src="https://img.shields.io/badge/status-production%20ready-brightgreen?style=for-the-badge" alt="status"/>
</p>

<h1 align="center">BroLang v12.3</h1>

<p align="center">
  <b>Bahasa pemrograman buat yang males nulis syntax panjang</b><br>
  <sub>Sintaks Bahasa Indonesia, fitur lengkap, enak dipake</sub>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/1406-Tests%20Passing-brightgreen?style=flat-square" alt="tests"/>
  <img src="https://img.shields.io/badge/115+-AST%20Nodes-blue?style=flat-square" alt="ast"/>
  <img src="https://img.shields.io/badge/135+Token%20Types-purple?style=flat-square" alt="tokens"/>
  <img src="https://img.shields.io/badge/65+-Stdlib%20Modules-orange?style=flat-square" alt="modules"/>
</p>

---

## Quick Start

### Cara 1: Install dari PyPI (paling gampang)
```bash
pip install brolang
```

### Cara 2: Install dari source
```bash
git clone https://github.com/salzcill-cmd/BroLang.git
cd BroLang
pip install -e .
```

### Cara 3: Install dengan script
```bash
git clone https://github.com/salzcill-cmd/BroLang.git
cd BroLang
chmod +x install.sh
./install.sh
```

### Cek apakah udah jalan
```bash
bro --version    # BroLang 12.3.0
echo 'tulis "Halo Dunia!"' > halo.bro
bro halo.bro
```

---

## Apa yang Baru di v12.3? 🚀

### Sistem Belajar Adaptif (`bro belajar`) 🎓
Mode belajar interaktif yang telah ditingkatkan sepenuhnya:
- **Progres tersimpan otomatis** ke `~/.brolang/belajar_progress.json` — lanjutkan kapan saja tanpa kehilangan poin.
- **Keahlian per-konsep** (level 0 = baru → 3 = ahli) dengan rasio keberhasilan, bukan hanya per-bab.
- **`bro belajar --ulang`**: spaced repetition — konsep yang belum mahir ditampilkan ulang dengan jeda semakin panjang (1 menit → 10 menit → 1 jam → 1 hari).
- **Petunjuk adaptif bertingkat** (level 0 samar → level 3 jelas) menyesuaikan dengan banyaknya percobaan salah.
- **Deteksi pola kesalahan umum** dengan umpan balik spesifik (contoh: `print(` → `tulis(`, lupa `selesai`, pakai `=` untuk bandingkan).
- **Umpan balik kualitas kode ringan** (variabel tidak terpakai, titik koma berlebih).
- **Mode latihan mandiri** (`bro belajar --latihan <konsep>`): coba konsep bebas tanpa tekanan poin.

Contoh:
```bash
bro belajar           # jalur terstruktur (8 bab)
bro belajar --ulang   # ulangi konsep yang perlu diperkuat
bro belajar --latihan variabel  # latihan mandiri konsep bebas
```

---

## Apa yang Baru di v12.2? 🚀

### Algebraic Data Types (ADT) 🧬
Deklarasikan enum dengan varian yang membawa payload, mirip Rust enum / Haskell data type:
```bro
enum Opsi {
    Sukses(teks),
    Gagal
}

fungsi unwrap(o)
    cocokkan o {
        Sukses(x): tulis "sukses: " + x
        Gagal(): tulis "gagal"
    }
selesai

unwrap(Sukses("halo"))  # sukses: halo
unwrap(Gagal())         # gagal
```
- `Varian(arg1, arg2)` membangun nilai varian.
- `cocokkan v { Varian(x, y): ... }` mencocokkan pola varian dan me-bind payload ke variabel.
- Analyzer validasi jumlah binding vs field varian, deteksi varian tak dikenal, dan cek kejelasan (exhaustiveness): jika semua varian dari satu enum tercover oleh pola varian (atau ada wildcard/default), tidak ada peringatan.
- Nilai varian direpresentasikan sebagai objek dengan `__eq__` dan `__repr__`, sehingga bisa dibandingkan dan dicetak.

---

## Apa yang Baru di v12.1? 🚀

### Kepemilikan Memori (`miliki`) / Move Semantics (Rust-like) 🧠
Fitur yang dijanjikan sejak v10.0 kini truly diimplementasikan:
```bro
miliki x = 5        # variabel kepemilikan tunggal
buat y = x          # memindahkan milik dari x ke y (move)
tulis x             # ERROR: x sudah dipindahkan (use-after-move)
tulis y             # 5
```
- `buat y = x` memindahkan milik dari `x` ke `y`; `x` tidak bisa digunakan lagi (use-after-move = error di analyzer compile-time DAN interpreter runtime).
- Variabel miliki bisa ditetapkan ulang (nilai lama di-drop); variabel biasa (`buat`) pakai semantik salin.
- Mencegah data race & use-after-free style bug tanpa garbage collector.

### Design by Contract 📋
Precondition, postcondition, dan class invariant (menandingi Eiffel/Dafny):
```bro
fungsi bagi(a, b)
    syarat_awal b != 0
    syarat_akhiri hasil != 0 atau a == 0
    kembali a / b
selesai

kelas Rekening
    fungsi __init__(awal)
        buat self.saldo = awal
    selesai
    invariansi self.saldo >= 0
    fungsi ambil(jumlah)
        syarat_awal jumlah > 0
        syarat_awal jumlah <= self.saldo
        self.saldo = self.saldo - jumlah
    selesai
selesai
```
- `syarat_awal` dicek sebelum body fungsi dieksekusi.
- `syarat_akhiri` dicek setelah return; variabel `hasil` merujuk nilai kembalian.
- `invariansi` dicek setelah setiap statement di dalam method kelas.
- Dicek oleh analyzer (kompilasi) DAN interpreter (runtime).

---

## Apa yang Baru di v12.0? 🚀

### Sistem Tipe — Type Inference & Konsistensi Reassignment 🏷️
- `buat x = 5` menyimpulkan tipe `Angka` otomatis dari nilai awal (type inference).
- Reassignment `x = ...` dengan tipe konkret berbeda dari tipe awal ditolak pada waktu kompilasi (analyzer), kecuali tipe tak dikenal (diserahke ke runtime) atau campuran numerik `Angka`↔`Desimal` (diizinkan).
- Menyelesaikan kisaran antara sistem tipe v6.0 (anotasi) dan penegakan konsisten, sehingga BroLang bersaing dengan TypeScript/Kotlin/Swift dalam keamanan tipe statis sambil tetap gradual (tidak ada false-positive).

---

## Apa yang Baru di v11.0? 🚀

### Library Game Lengkap 🎮
14 modul game ditulis ulang/ditingkatkan:
- **`game`** — fixed-timestep loop, scene stack/overlay, transisi (fade/slide/wipe/zoom), pause/resume, profil statistik, headless mode, screenshot, resize
- **`grafis`** — blend modes, offscreen render targets, gradien, perataan teks, clip/viewport, glow, draw-call counter
- **`input`** — action mapping (`atur_peta_aksi`), gamepad rumble, swipe gesture, focus events
- **`fisika`** — SpatialHash broadphase, collider radius configurable, AABB + raycast, gravitasi
- **`sprite`** — Atlas, Batcher (draw-call batching), gambar 9-slice (9-slice scaling)
- **`partikel`** — emitter, gravitasi point/angin/tarik/tolak, jejak (trail), warna gradien per-partikel, pooling
- **`ui`** — tema, stack vertikal/horizontal, kotak gulir, navigasi fokus
- **`kamera`** — zoom transisi cinematic, panning halus, deadzone, rotasi, screen shake, parallax
- **`audio`** — mixer volume master/SFX/musik, spatial audio (attenuasi jarak), crossfade musik, synth prosedural, BGM generator
- **`animasi`** — 26 easing, tween, sequence, keyframe animasi
- **`tilemap`** — layer objek, platform satu arah, platform bergerak, animasi tile, JSON (Tiled-like) impor/ekspor
- **`efek`** — flash, vignette, teks melayang, pulsa, guncangan, cromatic aberration, scanline, bloom
- **`vektor`** — Vec2/Vec3, lerp, proyeksi, refleksi, rotasi, polar

Semua modul game ditulis ulang/ditingkatkan agar BroLang menjadi salah satu bahasa paling lengkap untuk pengembangan game 2D.

---

## Apa yang Baru di v10.0? 🚀

### Compiler Native (AOT) ⚡
- **`bro build --native`** — kompilasi ahead-of-time ke executable Python mandiri (shebang `#!/usr/bin/env python3` + `chmod +x`), siap langsung dijalankan tanpa `bro run` dan tanpa memasang BroLang di target machine (hanya butuh Python 3).

### Konkurensi Berbasis Aktor 🧵
- **Modul `aktor`** — model actor (passing pesan): setiap aktor punya state terisolasi, berkomunikasi lewat `aktor.kirim` / `aktor.tanya`, tidak ada state bersama, **tidak ada race condition**, tidak perlu lock manual. Cocok untuk game loop, server, dan tugas bersamaan.

Semua fitur v10.0 tersedia di interpreter, transpiler, dan VM.

---

## Apa yang Baru di v9.0? 🚀

### Performa & Optimasi ⚡
- **String interning** & **small int cache** (-5 sampai 255) — hemat memori dan perbandingan lebih cepat
- VM: opcode/dispatch lebih efisien + jalur cepat panggilan & akses atribut (`FAST_CALL`, `LOAD_ATTR_FAST`, dll.)

### Fitur Bahasa Baru 🧩
- **`program_utama`** — entry point guard (kayak `if __name__ == "__main__"`), bloknya cuma jalan saat file dieksekusi langsung
- **`mengulang`** — shorthand map+filter satu baris: `mengulang data lalu ekspresi` (opsional pakai `jika` untuk filter)

### Stdlib Baru 📦
- **`regex`** — pencocokan pola lanjutan
- **`http`** — HTTP client (`get`, `post`, `put`, `delete`)
- **`encoding`** — base64/url/hex/binary encode-decode

### Tooling 🛠️
- **`bro info`** — tampilkan info versi/proyek, dependensi, dan jumlah file `.bro`

---

## Apa yang Baru di v8.2? ✨

### `properti` Decorator — Getter/Clean Setter
Sintaks bersih untuk getter/setter di kelas, mirip Python `@property`.

### 4 Modul Stdlib Baru 🧩
**`statistik`** — rerata, median, modus, simpangan baku, korelasi, ringkasan.  
**`zaman`** — Timer & stopwatch.  
**`penampilan`** — Pretty print & format data (angka, tabel, pohon, progress bar, JSON).  
**`warna`** — Warna terminal ANSI, gradient, kotak, rainbow.

---

## Belajar BroLang 🎓 (untuk pemula)

**Mau belajar coding dari nol, pakai Bahasa Indonesia?** Jalankan:

```bash
bro belajar
```

Tutorial interaktif di terminal — 8 bab bertingkat:
1. 🖨️ Halo Dunia
2. 📦 Variabel
3. ➕ Operasi Matematika
4. 🌿 Percabangan
5. 🔁 Perulangan
6. 📋 List
7. 🧩 Fungsi
8. 🎮 Proyek Mini: Kalkulator

Setiap bab ada materi singkat + latihan soal yang **dicek otomatis** (dijalankan langsung, lalu dibandingkan output-nya). Ada nilai akhir, petunjuk saat kesulitan, dan solusi kalau mentok. Tanpa install apa-apa, langsung dari terminal.

**Ramah pemula di semua sisi:**
- Pesan error memberi saran keyword: `print` → *"mungkin maksudmu 'tulis'?"*, `null` → *"mungkin maksudmu 'kosong'?"*
- Hint kesalahan umum: `jika x = 5 maka` → *"pakai '==' untuk membandingkan"*, titik koma `;` → *"tidak perlu dipakai"*
- REPL makin pintar: blok `jika`/`fungsi` multi-baris berfungsi, hasil ekspresi muncul (`2 + 3` → `=> 5`), perintah `bantuan`/`tips`/`contoh`

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

## Standard Library (65+ modules)

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
| `sejajar` | Threading & parallel (jalankan background task, peta_sejajar) |
| `aktor` | Actor model — state terisolasi, passing pesan, tanpa race condition (v10.0) |
| `ffi` | Foreign Function Interface — panggil fungsi C via ctypes (v11.0) |
| `tanggal` | Tanggal Indonesia: parse, format, selisih hari, komponen |
| `catat` | Logging ber-level (info/error/warning) ke terminal & file |
| `lingkungan` | Environment variables (get/set/ada/hapus) |
| `proses` | Jalankan subprocess (keluaran, kode exit) |
| `csv` | Baca/tulis CSV → list objek |
| `registri` | Package registry online: server HTTP + publish/install |
| `angka` | Matematika lanjut: pi/e (nilai), sqr, abs, min, max, faktorial |
| `sistem` | Info sistem: versi, platform, prosesor, hostname, cwd |
| `sistem_operasi` | Operasi OS: list_dir, buat/hapus/pindah file & folder, jalur |
| `web` | HTTP client: get/post/put/delete → objek respon (teks, status, json) |
| `database` | SQLite: buka, query, eksekusi_sql, tabel, kolom |
| `kripto` | Keamanan: md5/sha1/sha256/sha512, base64, password PBKDF2+salt, token (v6.4) |
| `arsip` | Arsip: buat/tambah/ekstrak/daftar ZIP, kompresi teks (v6.4) |
| `terminal` | UX CLI: warna ANSI, gaya teks, progress bar, prompt, pesan status (v6.4) |
| `jalur` | Pathfinding A* + navigasi: cari_jalur, IkutiJalur, Patroli waypoint (v6.6) |
| `efek` | Efek layar: Flash, Vignette, TeksMelayang, Pulsa (v6.6) + Guncangan screen shake (v6.7) |
| `belajar` | Sistem belajar adaptif: progres tersimpan, keahlian per-konsep, spaced repetition, petunjuk adaptif (v12.3) |

---

## Dokumentasi

| Dokumentasi | Isinya |
|------------|--------|
| [Instalasi](docs/INSTALASI.md) | Cara install BroLang |
| [Quick Start](docs/QUICKSTART.md) | Tutorial singkat |
| [Dasar Bahasa](docs/DASAR.md) | Tipe data, variabel, operator |
| [Fungsi](docs/FUNGSI.md) | Fungsi, lambda, closures |
| [Class & OOP](docs/OOP.md) | OOP & inheritance |
| [Fitur v8.1](docs/GAME_V81.md) | Game dev: object pooling, simpan/muat, dialog, AI (FSM+steering), platform satu arah & bergerak, quest/achievement |
| [Fitur v8.0](docs/FITUR_V80.md) | Spread objek {...a}, null-coalescing assignment ??=, kecuali multi-tipe (A, B), performa VM |
| [Fitur v6.9](docs/FITUR_V69.md) | Guard clause untuk semua statement (tulis, assignment, lempar, dst) |
| [Fitur v6.8](docs/FITUR_V68.md) | Guard clause, floor division //, augmented pada atribut/index, BGM prosedural |
| [Fitur v6.7](docs/FITUR_V67.md) | Rest/spread parameter, multiple return, VM lengkap, screen shake, synth audio |
| [Game Dev v6.6](docs/GAME_V66.md) | Pathfinding A*, efek layar, fisika AABB, parallax, fixed timestep, UI baru |
| [Fitur v6.5](docs/FITUR_V65.md) | Konstanta, do-until loop, range for loop |
| [Fitur v6.0](docs/FITUR_V60.md) | Type system, pattern matching modern, kelas_error, stdlib baru, package registry online |
| [Fitur v5.0](docs/FITUR.md) | Semua fitur lengkap |
| [Game Development](docs/GAME.md) | Bikin game pake BroLang |
| [Standard Library](docs/STDLIB.md) | 65+ module built-in |
| [CLI Tools](docs/CLI.md) | Compiler, formatter, profiler |
| [Arsitektur](docs/ARSITEKTUR.md) | Pipeline eksekusi |

---

## CLI Commands

```bash
bro run <file>         # Jalankan file .bro (tanpa argumen: dari brolang.json)
bro init <nama>        # Bikin proyek baru (src/, tests/, docs/, brolang.json)
bro build <file>       # Compile ke Python (--native untuk executable mandiri)
bro repl               # REPL interaktif
bro test [file]        # Jalankan tes (--nama <filter>, --detail)
bro profile <file>     # Profil eksekusi
bro lint <file>        # Analisis kode statis
bro fmt <file>         # Format kode
bro doc [topik]        # Dokumentasi (kripto, arsip, terminal, web, ...)
bro new-game <nama>    # Bikin proyek game baru
bro run-game <file>    # Jalankan game
bro benchmark <file>   # Benchmark interpreter vs transpiler vs VM
bro upgrade            # Update BroLang ke versi terbaru dari GitHub (v6.4)
bro belajar            # Belajar coding interaktif untuk pemula 🎓
bro belajar --ulang    # Mode ulangan (spaced repetition) konsep lemah
bro belajar --latihan <konsep>  # Latihan mandiri konsep bebas
bro pkg <cmd>          # Package manager (init/install/publish/dll)
bro pack <file> <out>  # Bundel .bro + runtime ke folder distribusi (v11.0)
```

### Game (showcase library game)

```bash
pip install pygame-ce                  # sekali saja, untuk semua modul game
bro examples/game_v66.bro              # showcase v6.6: pathfinding A*, efek, AABB, parallax, tooltip
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
│  Lexer  │ ← Tokenisasi (135+ tokens)
└─────────┘
    ↓
┌──────────┐
│  Parser  │ ← Bikin AST (115+ nodes)
└──────────┘
    ↓
┌─────────────────────┐
│ SemanticAnalyzer    │ ← Cek tipe, scope, kontrak, kepemilikan
└─────────────────────┘
    ↓
┌─────────────┐
│ Optimizer   │ ← Dead code elim, constant folding
└─────────────┘
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

**1406 test cases, semua passing!** (termasuk demo contoh v9.0; 58 test v8.2: properti decorator, statistik, zaman, penampilan, warna; 48 test v8.1: object pooling, simpan/muat, dialog, AI FSM+steering, platform satu arah & bergerak, quest/achievement; 32 test v8.0: spread objek, ??=, kecuali multi-tipe + error kustom di VM, konsistensi VM; 32 test v7.2; 10 test yield di dalam `coba`/`tangkap` di generator; 8 test perbaikan `hasilkandari` yield-from; 43 test v6.9: guard clause statement umum; 55 test v6.8: guard clause, floor division, augmented pada atribut/index, BGM prosedural; 59 test v6.7: rest/spread parameter, multiple return, VM lengkap; 65 test v6.6 game dev: pathfinding A*, efek layar, fisika AABB + raycast, partikel gradien, tilemap animasi, parallax, fixed timestep, Tooltip/DaftarSkor; 43 test v6.2 game dev; 61 test library game v5.4; output-consistency; visualisasi; ramah pemula; dan modul stdlib v6.0/v6.4; 23 test belajar v12.3)

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

> **BroLang v12.3** — Bahasa pemrograman buat yang males nulis syntax panjang 🇮🇩

<p align="center">
  <img src="https://img.shields.io/badge/Made%20with-Python-yellow?style=for-the-badge&logo=python&logoColor=white" alt="python"/>
  <img src="https://img.shields.io/badge/Made%20with-❤️-red?style=for-the-badge" alt="love"/>
</p>
```
