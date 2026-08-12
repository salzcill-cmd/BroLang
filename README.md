<p align="center">
  <img src="https://img.shields.io/badge/version-6.9-blue?style=for-the-badge&logo=python&logoColor=white" alt="version"/>
  <img src="https://img.shields.io/badge/python-3.10+-green?style=for-the-badge&logo=python&logoColor=white" alt="python"/>
  <img src="https://img.shields.io/badge/license-MIT-orange?style=for-the-badge" alt="license"/>
  <img src="https://img.shields.io/badge/status-production%20ready-brightgreen?style=for-the-badge" alt="status"/>
</p>

<h1 align="center">BroLang v6.9</h1>

<p align="center">
  <b>Bahasa pemrograman buat yang males nulis syntax panjang</b><br>
  <sub>Sintaks Bahasa Indonesia, fitur lengkap, enak dipake</sub>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/1005-Tests%20Passing-brightgreen?style=flat-square" alt="tests"/>
  <img src="https://img.shields.io/badge/115+-AST%20Nodes-blue?style=flat-square" alt="ast"/>
  <img src="https://img.shields.io/badge/135+Token%20Types-purple?style=flat-square" alt="tokens"/>
  <img src="https://img.shields.io/badge/43+-Stdlib%20Modules-orange?style=flat-square" alt="modules"/>
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
bro --version    # BroLang 6.9.0
echo 'tulis "Halo Dunia!"' > halo.bro
bro halo.bro
```

---

## Apa yang Baru di v6.9?

### Guard Clause untuk Semua Statement 🧩

Guard clause (v6.8) diperluas ke **semua statement sederhana** — statement hanya dijalankan saat kondisi benar:

```bro
fungsi cek(x)
    tulis x jika x > 0           # print bersyarat
    kembali x * 2 jika x > 0     # early return (v6.8)
selesai

buat skor = 0
skor = 100 jika benar           # reassignment bersyarat
skor += 10 jika menang          # augmented bersyarat

kelas Akun
    fungsi beri_bonus(self, n)
        self.bonus += n jika n > 0   # atribut objek ber-guard
        kembali self.bonus
    selesai
selesai

buat data = [1, 2, 3]
data[1] += 10 jika benar        # index list ber-guard

lempar "stok habis" jika stok <= 0   # raise bersyarat
log(pesan) jika mode_debug           # panggilan fungsi bersyarat
hapus cache jika basi                # delete bersyarat
```

Statement yang didukung: `tulis`, `buat` (deklarasi + destructuring),
reassignment, augmented assignment, atribut objek, index list, `lempar`,
`hapus`, pemanggilan fungsi, dan `hasilkan` (yield). Tidak ambigu dengan
ternary — `a jika b lainnya c` tetap ternary:

```bro
buat a = 5 jika benar lainnya 99   # ternary → a = 5
buat b = 5 jika salah lainnya 99   # ternary → b = 99
```

Detail: `docs/FITUR_V69.md`.

---

## Apa yang Baru di v6.8?

### Fitur Bahasa Baru 🧩

**Guard clause** — `kembali`, `hentikan`, dan `lanjutkan` bisa diberi kondisi:

```bro
fungsi cek(x)
    kembali "negatif" jika x < 0
    kembali "nol" jika x == 0
    kembali "positif"
selesai

tulis cek(-5), cek(0), cek(7)   # negatif nol positif

untuk i dari 1 sampai 10 lakukan
    lanjutkan jika i % 2 == 0   # skip genap
    hentikan jika i > 5         # break bersyarat
    tulis i                     # 1 3 5
selesai
```
Tidak ambigu dengan ternary: `kembali a jika b lainnya c` tetap ternary.

**Floor division `//`** — pembagian dibulatkan ke bawah:

```bro
tulis 17 // 5      # 3
buat x = 10
x //= 3
tulis x            # 3
```

**Augmented assignment pada atribut & index:**

```bro
kelas Akun
    fungsi __init__(self)
        self.total = 0
    selesai
    fungsi naik(self, n)
        self.total += n        # atribut objek
        kembali self.total
    selesai
selesai

buat data = [1, 2, 3]
data[1] += 10                  # index list → [1, 12, 3]
```

### Game Dev 🎮
**`audio` BGM prosedural** — musik latar tanpa file eksternal:

```bro
impor audio

buat bgm = audio.buat_bgm(audio.pola_arcade)   # pola siap pakai
audio.mainkan_bgm(audio.pola_epik, 120)        # putar loop (butuh pygame)
audio.hentikan_bgm()
```
Pola bisa pakai nama not (`"C4"`, `"A#3"`), frekuensi, tuple `(nada, ketukan)`, atau jeda `0`.

### Perbaikan VM ⚙️
`x %= y` dan `x **= y` yang tadinya diam-diam menjadi `x = y` di VM kini benar; loop dengan guard `hentikan jika` tidak lagi memotong body.

Detail: `docs/FITUR_V68.md`.

---

## Apa yang Baru di v6.7?

### Fitur Bahasa Modern 🧩

**Rest parameter `...nama`** — fungsi menampung semua sisa argumen:

```bro
fungsi jumlahkan(...angka)
    buat total = 0
    untuk setiap n dalam angka lakukan
        total = total + n
    selesai
    kembali total
selesai

tulis jumlahkan(1, 2, 3, 4, 5)   # 15
```

**Spread call `f(...args)`** — bongkar list jadi argumen:

```bro
fungsi kali3(a, b, c)
    kembali a * b * c
selesai

buat nilai = [2, 3, 4]
tulis kali3(...nilai)            # 24
```

**Spread list `[...a, 1]`** — gabungkan list di literal:

```bro
buat gabung = [...dasar, 3, 4]   # [1, 2, 3, 4]
```

**Multiple return `kembali a, b`** — beberapa nilai sekaligus:

```bro
fungsi bagi_dan_sisa(a, b)
    kembali a / b, a % b
selesai

buat [hasil, sisa] = bagi_dan_sisa(17, 5)   # 3.4 2
```

### Bytecode VM kini lengkap ⚙️
Range-for, destructuring, pipeline, dan for-each (`untuk setiap`) yang
sebelumnya `NotImplementedError` / diam-diam dilewati di VM bytecode kini
berfungsi penuh — konsisten dengan interpreter & transpiler.

### Game Dev 🎮
- **`efek.Guncangan`** — screen shake trauma-based (memudar alami, testable tanpa pygame)
- **`audio` synth** — `nada()` / `laser()` / `ledakan()` / `blip()` buat WAV procedural tanpa file eksternal

Detail: `docs/FITUR_V67.md`.

---

## Apa yang Baru di v6.6?

### Upgrade Library Game Komprehensif 🎮
**2 modul baru** + **8 modul ditingkatkan** — buat bikin game 2D makin gampang:

**Modul baru `jalur`** — pathfinding A* + navigasi waypoint:
```bro
impor jalur

buat rute = jalur.cari_jalur(denah, (1, 1), (10, 5))   # A* di tilemap
jika rute maka
    tulis jalur.panjang_jalur(rute)
selesai

buat penjaga = jalur.Patroli([(100, 100), (500, 100)], kecepatan=120,
                             mode="bolak-balik")        # patroli waypoint
penjaga.update(dt)
```

**Modul baru `efek`** — efek layar instan:
```bro
impor efek

buat kilat = efek.buat_flash("putih", durasi=0.15)      # flash layar
buat dmg = efek.TeksMelayang("-25", x, y, warna="merah")  # damage number
buat vin = efek.Vignette(kekuatan=0.4)                   # vignette
```

**Fisika AABB + raycast:** collider persegi (`set_persegi`), tabrakan campuran,
`dunia.raycast(x1, y1, x2, y2)`, `dunia.cari_bodi_di_area(...)`.

**Partikel:** gradien warna seumur hidup (`warna_awal`/`warna_akhir`),
tekstur partikel, emiter siap pakai `buat_trail` / `buat_asap` / `buat_bintang`.

**Tilemap:** tile animasi (`atur_animasi` + `peta.update(dt)`), layer objek
(`tambah_objek`, `cari_objek`), `cek_lantai` untuk platformer.

**Kamera:** parallax layers (`screen_parallax`), deadzone follow
(`set_target(pemain, deadzone=(120, 80))`), `set_lerp`.

**Game loop:** fixed timestep fisika (`game.atur_fisika(fungsi, 1/120)`),
screenshot (`tangkap_layar`), resize jendela.

**Grafis:** gradien vertikal/horizontal, `glow_lingkaran`, perataan teks
(`tengah`/`kanan`), `gambar_gambar_alpha`.

**UI:** `Tooltip`, `Tombol` bergambar, `DaftarSkor` (high score persisten),
navigasi fokus keyboard.

**Sprite:** `ikuti_patroli`, `rotasi_ke_titik`, `tampilkan`/`sembunyikan`.

Bonus: sintaks `buat (x, y) = fungsi()` yang selama ini ada di dokumentasi
kini benar-benar berfungsi.

```bash
bro examples/game_v66.bro     # showcase lengkap semua fitur v6.6
```

Detail: `docs/GAME_V66.md`.

---

## Apa yang Baru di v6.5?

### Fitur Bahasa Baru 🧩

**`konstanta`** — variabel immutable, nilai tidak bisa diubah setelah deklarasi:

```bro
konstanta PI = 3.14
konstanta NAMA = "BroLang"

PI = 3.15   # error: Konstanta 'PI' tidak bisa diubah
```

**`ulangi ... sampai`** — do-until loop, body jalan minimal satu kali:

```bro
buat tebakan = 0
ulangi
    tebakan = tebakan + 1
    tulis "Percobaan ke-" + teks(tebakan)
sampai tebakan >= 3
```

**`untuk i dari A sampai B`** — range for loop (inklusif, bisa `langkah`):

```bro
untuk i dari 1 sampai 10 lakukan
    tulis i
selesai

untuk i dari 10 sampai 2 langkah -2 lakukan
    tulis i
selesai
```

Semua fitur berjalan konsisten di interpreter, transpiler (`bro run`),
dan compiler (`bro build`). Detail: `docs/FITUR_V65.md`.

---

## Apa yang Baru di v6.3?

### Performance Boost ⚡
Tiga lapis optimasi bikin BroLang makin kencang:

- **Peephole optimizer** di bytecode VM — constant folding (`2 + 3 * 4` jadi satu konstanta), removal NOP, remap jump otomatis
- **Method cache** — pemanggilan method di inheritance chain di-cache (invalidasi otomatis saat monkey-patch)
- **Fast path interpreter** — operator biner pada angka/teks tidak lagi mengecek operator overloading

```bash
bro benchmark benchmarks/fibonacci.bro --repeat 3
# Transpiler 11x-151x lebih cepat dari VM per kasus
```

Benchmark publik ada di folder `benchmarks/` + docs `docs/PERFORMANCE.md`.

### Tooling Proyek Modern 🛠️

```bash
bro init myapp          # scaffolding proyek lengkap
cd myapp
bro run                 # jalankan entry point dari brolang.json (tanpa argumen)
bro test                # jalankan test
```

Struktur yang dibuat: `brolang.json`, `src/main.bro`, `tests/`, `docs/`, `.gitignore`.

### Web Framework 🌐
Bikin API backend langsung dari BroLang — tanpa dependency eksternal:

```bro
impor web_server

fungsi halaman(req)
    kembali req.kirim_json({"pesan": "Halo Dunia!"})
selesai

buat app = web_server.Buat()
app.get("/", halaman)
app.get("/pengguna/{id}", detail)   # parameter dinamis
app.jalankan(8000)                   # http://127.0.0.1:8000
```

Routing GET/POST/PUT/DELETE, query string, body JSON, static files, CORS.
Contoh lengkap: `examples/web_api.bro`.

---

## Apa yang Baru di v6.4?

### Keamanan, Arsip & Terminal UX 🔐
Tiga modul stdlib baru — semuanya murni stdlib Python, tanpa dependency eksternal:

**`kripto`** — Keamanan & kriptografi:
```bro
impor kripto

tulis kripto.sha256("halo dunia")       # 64 karakter hex
tulis kripto.base64_encode("BroLang")   # QnJvTGFuZw==

buat hash = kripto.hash_password("rahasia123")   # PBKDF2 + salt acak
tulis kripto.cek_password("rahasia123", hash)    # True
buat api_key = kripto.token(32)                  # token crypto-grade
```

**`arsip`** — ZIP & kompresi:
```bro
impor arsip

arsip.buat_zip("backup.zip", ["a.txt", "b.txt"])
tulis arsip.daftar_zip("backup.zip")
arsip.ekstrak_zip("backup.zip", "restore/")
buat padat = arsip.kompres("teks panjang ...")   # lebih pendek (zlib)
```

**`terminal`** — UX terminal untuk program CLI:
```bro
impor terminal

tulis terminal.hijau("sukses")
terminal.sukses("Deploy berhasil")
tulis terminal.bilah_progress(7, 10)             # [███████░░░] 70%
buat nama = terminal.tanya("Nama kamu? ", "anonim")
```

### Tooling: `bro test` lebih pintar 🧪
- `bro test --nama <filter>` — hanya jalankan file tes yang namanya mengandung filter
- `bro test --detail` — tampilkan status ✓/✗ + durasi tiap file
- Ringkasan total dengan waktu eksekusi

### Perintah baru `bro upgrade` 🔄
`bro upgrade` — update BroLang ke versi terbaru langsung dari GitHub
(git pull + install ulang otomatis).

Contoh lengkap: `examples/kripto.bro`, `examples/arsip.bro`, `examples/terminal.bro`.

---

## Apa yang Baru di v6.2?

### Scene Lifecycle + Transisi 🎬
Scene sekarang punya siklus hidup penuh: `on_masuk` / `on_keluar`, transisi **fade** antar scene, dan tumpukan scene untuk **overlay menu pause**.

```bro
impor game

# Lifecycle: setup saat scene aktif, cleanup saat diganti
game.tambah_scene("main", update_main, gambar_main,
                   on_masuk=muat_level, on_keluar=simpan_skor)

# Transisi fade antar scene
game.ganti_scene("main", transisi="fade", durasi=1.0, warna="hitam")

# Overlay menu pause di atas gameplay (scene bawah tetap digambar)
game.dorong_scene("pause", transisi="fade")
game.pop_scene(transisi="fade")
```

### UI Komponen Baru 🖱️
Empat komponen UI baru siap pakai: **KotakTeks** (input teks), **Slider**, **KotakCentang** (checkbox), dan **DaftarPilih** (dropdown).

```bro
impor ui

buat nama = ui.KotakTeks(200, 150, 250, 40, placeholder="Nama pemain")
buat volume = ui.Slider(200, 300, 250, nilai=50, min=0, maks=100)
buat musik = ui.KotakCentang(200, 400, label="Aktifkan musik", dicentang=True)
buat level = ui.DaftarPilih(200, 500, 200, opsi=["Mudah", "Sedang", "Sulit"])

nama.update(mx, my, klik)          # fokus via klik
nama.tambah_karakter("A")          # terima karakter dari input keyboard
volume.update(mx, my, ditekan)     # drag
musik.update(mx, my, klik)         # toggle
level.update(mx, my, klik)         # buka/pilih opsi
```

Semua komponen logika-nya jalan **tanpa pygame** (hanya render yang butuh pygame) — gampang di-test.

### 5 Modul Stdlib Baru 🧩
Modul yang selama ini hanya dijanjikan di dokumentasi kini **benar-benar ada**: `angka`, `sistem`, `sistem_operasi`, `web`, dan `database`.

```bro
impor angka
impor sistem
impor web
impor database

tulis angka.pi                  # 3.141592653589793 (konstanta langsung)
tulis angka.sqr(16)             # 4.0
tulis sistem.platform()         # linux / windows / darwin

buat respon = web.get("https://api.example.com/data")
tulis respon.status             # 200
tulis respon.json               # body ter-parse sebagai objek

buat db = database.buka("data.db")
db.eksekusi_sql("CREATE TABLE IF NOT EXISTS t (id INTEGER, nama TEXT)")
db.eksekusi_sql("INSERT INTO t (id, nama) VALUES (?, ?)", 1, "Budi")
tulis db.query("SELECT * FROM t")[0]["nama"]    # Budi
```

Plus `sistem_operasi` untuk operasi file/folder & jalur (`list_dir`, `buat_folder`, `pindah`, `gabung_jalur`, dll).

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

## Apa yang Baru di v6.0?

### Type System Lengkap 🏷️
Anotasi tipe di variabel, parameter, dan return value — diverifikasi otomatis (ditolak kalau salah).

```bro
buat umur: Angka = 25          # anotasi variabel
buat nama: Teks = "Budi"

fungsi kali2(a: Angka) -> Angka   # anotasi parameter & return
    kembali a * 2
selesai

tulis kali2(21)                # 42

# Union, generik, dan alias
buat nilai: Angka | Teks = "lima"     # union type
buat angka2: Daftar<Angka> = [1, 2, 3]  # generic

tipe ID = Angka                        # type alias
buat kode: ID = 12345
```

```bro
buat umur: Angka = "salah"   # Error: Tipe tidak cocok untuk 'umur'
```
Mismatch tipe ditolak di **dua lapis**: analyzer statis (sebelum jalan) dan interpreter (saat runtime). Kelas user juga bisa dipakai sebagai tipe parameter (`fungsi info(m: Mobil)`).

### Pattern Matching Modern 🎯
`cocokkan` kini bisa membongkar list/objek langsung di polanya.

```bro
buat data = [1, 2]
cocokkan data {
    [a, b]: tulis a + b              # pola list → bind elemen → 3
    _: tulis "lain"
}

buat orang = {"nama": "Ani", "umur": 20}
cocokkan orang {
    {"nama": n, "umur": u}: tulis "Nama: " + n + ", Umur: " + teks(u)
    _: tulis "siapa?"
}

buat skor = 15
cocokkan skor {
    x jika x > 10: tulis "tinggi"     # guard condition
    _: tulis "rendah"
}
```
Pola: list `[a, b]`, objek `{"nama": n}`, binding `n:`, literal, wildcard `_`, plus guard `jika`. Bekerja sama di interpreter **dan** transpiler.

### Error Handling Profesional 🚨
Custom error class — `kelas_error` dengan field sendiri + hierarki + fallback.

```bro
kelas_error SaldoTidakCukup extends Kesalahan
    fungsi __init__(pesan, saldo)
        self.pesan = pesan
        self.saldo = saldo
    selesai
selesai

coba
    lempar SaldoTidakCukup("Saldo tidak cukup", 5000)
kecuali SaldoTidakCukup sebagai e
    tulis "Tertangkap: " + e.pesan + ", saldo=" + teks(e.saldo)
selesai
```

Hierarki error didukung: `kecuali Induk sebagai e` menangkap semua turunannya, dan `kecuali lainnya sebagai e` jadi fallback. Konsisten di interpreter & transpiler. Error CLI juga makin profesional — `bro run` menampilkan baris/kolom, baris sumber dengan penanda `^`, solusi, dan stack trace.

### Ekosistem Stdlib + Package Registry 🌐
Enam modul baru siap pakai:

```bro
impor tanggal
impor catat
impor lingkungan
impor proses
impor csv
impor registri

tulis tanggal.selisih_hari("2026-08-07", "2026-08-01")   # 6

buat hasil = proses.jalankan("echo halo")
tulis hasil.keluaran                                  # halo

impor csv
buat data = [{"nama": "Budi", "umur": 20}]
csv.tulis("data.csv", data)
tulis csv.baca("data.csv")[0]["nama"]                 # Budi
```

**Package Registry Online**: `registri.jalankan_async(port)` menjalankan registry HTTP lokal — `bro pkg publish` / `bro pkg install` / `cari_remote` sekarang bisa lewat jaringan.

---

## Apa yang Baru di v5.5?

### Operator Overloading 🧮
Kelas BroLang sekarang bisa mendefinisikan perilaku operator sendiri — nggak perlu fungsi bantu manual.

```bro
kelas Titik
    fungsi __init__(x, y)
        self.x = x
        self.y = y
    selesai
    fungsi _tambah_(lain)
        kembali Titik(self.x + lain.x, self.y + lain.y)
    selesai
    fungsi _sama_(lain)
        kembali self.x == lain.x dan self.y == lain.y
    selesai
    fungsi _teks_()
        kembali "(" + teks(self.x) + ", " + teks(self.y) + ")"
    selesai
selesai

buat a = Titik(1, 2)
buat b = Titik(3, 4)
tulis a + b              # (4, 6)
tulis a == Titik(1, 2)   # True
```
Method yang bisa di-overload: `_tambah_` (+), `_kurang_` (-), `_kali_` (*), `_bagi_` (/), `_modulo_` (%), `_pangkat_` (**), `_sama_` (==), `_tidak_sama_` (!=), `_kurang_dari_` (<), `_lebih_dari_` (>), `_kurang_sama_` (<=), `_lebih_sama_` (>=), `_negasi_` (-), `_positif_` (+), `_dalam_` (dalam), `_teks_` (print/konversi), `_panjang_` (panjang()), `_index_`/`_index_set_` (`[]`). Bekerja konsisten di interpreter **dan** transpiler.

### Threading (`sejajar`) 🧵
Jalankan fungsi di background thread supaya game loop / program utama tetap responsif.

```bro
impor sejajar

fungsi hitung(x)
    kembali x * 2
selesai

buat t = sejajar.jalankan(hitung, 21)      # background thread
buat hasil = t.hasil()                      # 42 (blokir sampai selesai)

tulis sejajar.peta_sejajar(hitung, [1, 2, 3, 4])   # [2, 4, 6, 8]
```
API: `jalankan`, `tunggu`, `tunggu_semua`, `peta_sejajar`, `atur_thread`/`jumlah_thread`, objek `Tugas` (`selesai()`/`hasil()`/`batal()`). Fungsi BroLang otomatis di-serialisasi biar aman; callable Python murni jalan paralel penuh.

### LSP & Tooling ⚡
Language server makin pintar: auto-completion mencakup **keyword + semua builtin + simbol di dokumen + member modul** (setelah titik), **go-to-definition** lompat ke baris deklarasi, dan **hover** menampilkan info tipe simbol. Cocok dipasang di VS Code / editor yang mendukung LSP.

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

## Semua Fitur (v4.0 + v5.0 + v5.2 + v5.3 + v5.4 + v5.5 + v6.0)

### v6.0
- Type system lengkap: `buat x: Angka = 5`, `fungsi f(a: Angka) -> Teks`, union `Angka | Teks`, generik `Daftar<Angka>`, alias tipe
- Pattern matching modern: pola list `[a, b]`, pola objek `{"nama": n}`, binding, guard `x jika x > 10`
- Error handling profesional: `kelas_error` custom error class + hierarki + `kecuali lainnya`
- Modul baru: `tanggal`, `catat`, `lingkungan`, `proses`, `csv`, `registri` (package registry online)
- CLI error display profesional: baris/kolom, penanda `^`, solusi, stack trace
- Analyzer: dukungan kelas_error & pattern binding + cek tipe statis (mismatch ditolak di `bro run`)

### v5.5
- Operator overloading: `_tambah_`, `_kurang_`, `_sama_`, `_teks_`, `_panjang_`, `_index_`, dll.
- Modul `sejajar`: threading/parallel — `jalankan`, `tunggu`, `peta_sejajar`, objek `Tugas`
- LSP: completion pintar, go-to-definition, hover

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

## Standard Library (43+ modules)

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

---

## Dokumentasi

| Dokumentasi | Isinya |
|------------|--------|
| [Instalasi](docs/INSTALASI.md) | Cara install BroLang |
| [Quick Start](docs/QUICKSTART.md) | Tutorial singkat |
| [Dasar Bahasa](docs/DASAR.md) | Tipe data, variabel, operator |
| [Fungsi](docs/FUNGSI.md) | Fungsi, lambda, closures |
| [Class & OOP](docs/OOP.md) | OOP & inheritance |
| [Fitur v6.9](docs/FITUR_V69.md) | Guard clause untuk semua statement (tulis, assignment, lempar, dst) |
| [Fitur v6.8](docs/FITUR_V68.md) | Guard clause, floor division //, augmented pada atribut/index, BGM prosedural |
| [Fitur v6.7](docs/FITUR_V67.md) | Rest/spread parameter, multiple return, VM lengkap, screen shake, synth audio |
| [Game Dev v6.6](docs/GAME_V66.md) | Pathfinding A*, efek layar, fisika AABB, parallax, fixed timestep, UI baru |
| [Fitur v6.5](docs/FITUR_V65.md) | Konstanta, do-until loop, range for loop |
| [Fitur v6.0](docs/FITUR_V60.md) | Type system, pattern matching modern, kelas_error, stdlib baru, package registry online |
| [Fitur v5.0](docs/FITUR.md) | Semua fitur lengkap |
| [Game Development](docs/GAME.md) | Bikin game pake BroLang |
| [Standard Library](docs/STDLIB.md) | 43+ module built-in |
| [CLI Tools](docs/CLI.md) | Compiler, formatter, profiler |
| [Arsitektur](docs/ARSITEKTUR.md) | Pipeline eksekusi |

---

## CLI Commands

```bash
bro run <file>         # Jalankan file .bro (tanpa argumen: dari brolang.json)
bro init <nama>        # Bikin proyek baru (src/, tests/, docs/, brolang.json)
bro build <file>       # Compile ke Python
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
bro pkg <cmd>          # Package manager (init/install/publish/dll)
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

**1005 test cases, semua passing!** (termasuk 8 test baru perbaikan `hasilkandari` yield-from; 43 test v6.9: guard clause statement umum; 55 test v6.8: guard clause, floor division, augmented pada atribut/index, BGM prosedural; 59 test v6.7: rest/spread parameter, multiple return, VM lengkap; 65 test v6.6 game dev: pathfinding A*, efek layar, fisika AABB + raycast, partikel gradien, tilemap animasi, parallax, fixed timestep, Tooltip/DaftarSkor; 43 test v6.2 game dev; 61 test library game v5.4; output-consistency; visualisasi; ramah pemula; dan modul stdlib v6.0/v6.4)

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

> **BroLang v6.9** — Bahasa pemrograman buat yang males nulis syntax panjang 🇮🇩

<p align="center">
  <img src="https://img.shields.io/badge/Made%20with-Python-yellow?style=for-the-badge&logo=python&logoColor=white" alt="python"/>
  <img src="https://img.shields.io/badge/Made%20with-❤️-red?style=for-the-badge" alt="love"/>
</p>
