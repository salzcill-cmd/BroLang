# Standard Library

> **BroLang punya module built-in yang keren-keren.** Tinggal pake aja.

## `visualisasi` — Visualisasi Data

Chart/grafik untuk memvisualisasikan data, baik ASCII (langsung di terminal) maupun SVG/HTML (laporan untuk browser).

```
impor visualisasi

buat data = {"Senin": 12, "Selasa": 45, "Rabu": 23, "Kamis": 67, "Jumat": 34}

# Chart ASCII di terminal
tulis visualisasi.batang(data, judul="Penjualan Mingguan", satuan="unit")
tulis visualisasi.garis([3, 7, 2, 9, 5], judul="Tren")
tulis visualisasi.kue([30, 40, 25, 5], label=["A", "B", "C", "D"], judul="Pasar")
tulis visualisasi.sebar([1, 2, 3, 4], [2, 4, 1, 5], judul="Sebaran")
tulis visualisasi.histogram([1, 1, 2, 2, 2, 3, 3, 4], jumlah_bin=4, judul="Distribusi")

# Export SVG & HTML
buat svg = visualisasi.batang_svg(data, judul="Penjualan Mingguan")
visualisasi.simpan_svg("penjualan.svg", svg)
visualisasi.simpan_html("laporan.html", [svg], judul="Laporan Bulanan")
```

**Fungsi:**

| Fungsi | Keterangan |
|--------|------------|
| `batang(data, label?, judul?, lebar?, satuan?, berwarna?)` | Bar chart horizontal (ASCII) |
| `garis(data, label?, judul?, tinggi?, lebar?)` | Line chart (ASCII) |
| `kue(data, label?, judul?, radius?, satuan?, desimal?)` | Pie/donut chart (ASCII) |
| `sebar(x_data, y_data, judul?, tinggi?, lebar?)` | Scatter plot (ASCII) |
| `histogram(data, jumlah_bin?, judul?, tinggi?)` | Histogram (ASCII) |
| `batang_svg(data, label?, judul?, warna?, lebar?, tinggi?)` | Bar chart (SVG) |
| `garis_svg(data, x?, label?, judul?, warna?)` | Line chart (SVG), dukung multi-seri |
| `kue_svg(data, label?, judul?, warna?)` | Pie/donut chart (SVG) |
| `sebar_svg(x_data, y_data, judul?, label_x?, label_y?, warna?)` | Scatter plot (SVG) |
| `histogram_svg(data, jumlah_bin?, judul?, warna?)` | Histogram (SVG) |
| `simpan_svg(nama_file, svg)` | Simpan SVG ke file |
| `simpan_html(nama_file, svg_list, judul?)` | Simpan 1+ chart ke halaman HTML |
| `simpan_txt(nama_file, teks)` | Simpan chart ASCII ke file |

**GUI (butuh `pip install pygame-ce`):**

```
impor visualisasi

buat chart1 = {"jenis": "batang", "data": [12, 45, 23], "judul": "Penjualan"}
buat chart2 = {"jenis": "kue", "data": {"A": 30, "B": 40}, "judul": "Pasar"}
visualisasi.tampilkan_jendela([chart1, chart2], judul="Dashboard")

visualisasi.tampilkan_batang([12, 45, 23], judul="Penjualan")     # satu chart langsung
visualisasi.simpan_png("chart.png", chart1)                        # render ke PNG
```

| Fungsi | Keterangan |
|--------|------------|
| `tampilkan_jendela(charts, judul?, lebar?, tinggi?, layar_penuh?)` | Jendela pygame berisi 1+ chart (blokir sampai ditutup) |
| `tampilkan_batang(data, label?, judul?, warna?)` | Buka jendela chart batang |
| `tampilkan_garis(data, x?, label?, judul?, warna?)` | Buka jendela chart garis |
| `tampilkan_kue(data, label?, judul?, warna?)` | Buka jendela chart pie/donat |
| `tampilkan_sebar(x_data, y_data, judul?, warna?)` | Buka jendela scatter plot |
| `tampilkan_histogram(data, jumlah_bin?, judul?, warna?)` | Buka jendela histogram |
| `simpan_png(nama_file, spec, lebar?, tinggi?)` | Render chart ke PNG tanpa buka jendela |

Spec chart: `{"jenis": "batang|garis|kue|sebar|histogram", "data": ..., "label": ..., "judul": ..., "warna": ...}`.

**Kontrol jendela:** panah kiri/kanan = ganti chart, `1-9` = lompat, `F` = fullscreen, `S` = screenshot, `H` = bantuan, `ESC`/`Q` = tutup.

**Format data:** list nilai (`[12, 45]`), list pasangan (`[["Senin", 12]]`), atau objek (`{"Senin": 12}`).

---

## `angka` — Matematika Lanjut

```
muat angka

tulis angka.pi           # 3.14159...
tulis angka.e            # 2.71828...
tulis angka.sqr(16)      # 4.0
tulis angka.abs(-5)      # 5
tulis angka.min(3, 7)    # 3
tulis angka.max(3, 7)    # 7
```

## `vektor` — Vektor Matematika

```
muat vektor

buat a = vektor.buat(1, 2)
buat b = vektor.buat(3, 4)

tulis vektor.tambah(a, b)      # (4, 6)
tulis vektor.kali_skalar(a, 3) # (3, 6)
tulis vektor.panjang(a)        # 2.236...
```

## `audio` — Sound Effects

```
muat audio

audio.muat("efek_lompat", "assets/lompat.mp3")
audio.mainkan("efek_lompat")
```

## `angka` — Matematika Lanjut

Konstanta & fungsi matematika cepat. `pi` dan `e` langsung sebagai nilai
(tanpa kurung).

```
impor angka

tulis angka.pi           # 3.141592653589793
tulis angka.e            # 2.718281828459045
tulis angka.sqr(16)      # 4.0
tulis angka.abs(-5)      # 5
tulis angka.min(3, 7)    # 3
tulis angka.max(3, 7)    # 7
```

| Fungsi | Keterangan |
|--------|------------|
| `pi`, `e` | Konstanta matematika (nilai) |
| `sqr(x)` / `akar(x)` | Akar kuadrat |
| `abs(x)` | Nilai absolut |
| `min(...)` / `max(...)` | Minimum/maksimum (2+ angka atau satu list) |
| `pangkat(x, y)` | x pangkat y |
| `lantai(x)` / `langit(x)` | Floor / ceil |
| `bulat(x, n?)` | Pembulatan ke n digit |
| `log(x, base?)` | Logaritma |
| `sin(x)` / `cos(x)` / `tan(x)` | Trigonometri (radian) |
| `faktorial(n)` | Faktorial |
| `acak_antara(a, b)` | Angka acak antara a dan b |

---

## `sistem` — Info System

Informasi sistem operasi & lingkungan.

```
impor sistem

tulis sistem.versi()        # 6.6.0 (Versi BroLang)
tulis sistem.platform()     # linux / windows / darwin
tulis sistem.nama()         # Linux
tulis sistem.prosesor()     # x86_64
tulis sistem.python()       # 3.12.3
```

| Fungsi | Keterangan |
|--------|------------|
| `versi()` | Versi BroLang yang berjalan |
| `platform()` | OS huruf kecil: linux/windows/darwin |
| `nama()` / `versi_os()` | Nama & versi detail OS |
| `prosesor()` | Arsitektur prosesor |
| `python()` | Versi Python |
| `hostname()` | Nama host mesin |
| `cwd()` / `home()` | Direktori kerja & folder home |
| `lingkungan()` | Nilai `BROLANG_ENV` (default development) |

## `game` — Game Utilities

```
muat game

# Tabrakan antara dua kotak
buat ada_tabrakan = game.cek_tabrakan(
    x1, y1, w1, h1,
    x2, y2, w2, h2
)

# Input tombol
jika game.input_ditekan("space") maka
    lompat()
selesai
```

## `web` — HTTP Requests

HTTP client sederhana. Setiap request mengembalikan objek respon dengan
atribut: `teks` (body), `status` (kode HTTP), `json` (body ter-parse atau
`kosong`), `header` (objek header), `sukses` (True untuk status 2xx),
dan `error` (pesan error atau `kosong`).

```
impor web

buat respon = web.get("https://api.example.com/data")
tulis respon.status       # 200
tulis respon.teks         # body mentah
tulis respon.json         # body sebagai objek (bila JSON)

buat hasil = web.post("https://api.example.com/login",
                      json={"nama": "Budi", "kata": "rahasia"})
jika hasil.sukses maka
    tulis hasil.json
selesai
```

| Fungsi | Keterangan |
|--------|------------|
| `get(url, header?, timeout?)` | HTTP GET |
| `post(url, data?, json?, header?, timeout?)` | HTTP POST (form atau JSON) |
| `put(url, data?, json?, header?, timeout?)` | HTTP PUT |
| `hapus_http(url, header?, timeout?)` | HTTP DELETE |
| `kirim(metode, url, data?, json?, header?, timeout?)` | Request bebas |

## `sistem_operasi` — OS Operations

Operasi file/folder & manipulasi jalur.

```
impor sistem_operasi

buat daftar = sistem_operasi.list_dir(".")
untuk file dalam daftar lakukan
    tulis file
selesai
```

| Fungsi | Keterangan |
|--------|------------|
| `list_dir(path?)` | Daftar nama file & folder (urut abjad) |
| `daftar_file(path?)` / `daftar_folder(path?)` | Hanya file / hanya folder |
| `ada(path)` / `adalah_file(path)` / `adalah_folder(path)` | Cek keberadaan |
| `buat_folder(path)` | Buat folder (termasuk induk) |
| `hapus_file(path)` / `hapus_folder(path)` | Hapus file / folder |
| `pindah(sumber, tujuan)` / `salin(sumber, tujuan)` | Pindah / salin |
| `ukuran(path)` | Ukuran file (byte) |
| `cwd()` / `ganti_cwd(path)` | Direktori kerja |
| `nama_dasar(path)` / `folder_induk(path)` | Basename / dirname |
| `ekstensi(path)` / `nama_tanpa_ekstensi(path)` | Ekstensi & nama tanpa ekstensi |
| `gabung_jalur(...)` | Gabung bagian jalur (sesuai OS) |
| `jalur_absolut(path)` / `jalur_nyata(path)` | Jalur lengkap / kanonik |
| `ubah_ekstensi(path, ekstensi)` | Ganti ekstensi file |

---

## `database` — Database (SQLite)

Wrapper SQLite untuk penyimpanan data lokal. Bisa buka file `.db` atau
langsung di memori (`:memory:`).

```
impor database

buat db = database.buka("data.db")   # atau database.buka() / buka_memori()
db.eksekusi_sql("CREATE TABLE IF NOT EXISTS pengguna (id INTEGER, nama TEXT)")
db.eksekusi_sql("INSERT INTO pengguna (id, nama) VALUES (?, ?)", 1, "Budi")

buat semua = db.query("SELECT * FROM pengguna")
untuk row dalam semua lakukan
    tulis row["nama"]
selesai

tulis db.jumlah_baris("pengguna")    # 1
db.tutup()
```

| Fungsi | Keterangan |
|--------|------------|
| `buka(path?)` / `buka_memori()` | Buka database file / di memori |
| `eksekusi_sql(sql, *params)` | Jalankan INSERT/UPDATE/DELETE/DDL (pakai `?` placeholder) |
| `query(sql, *params)` | SELECT → list objek `{kolom: nilai}` |
| `query_satu(sql, *params)` | Baris pertama atau `kosong` |
| `query_nilai(sql, *params)` | Nilai kolom pertama baris pertama |
| `eksekusi_banyak(sql, daftar)` | Insert banyak baris sekaligus |
| `tabel()` | Daftar nama tabel |
| `kolom(nama_tabel)` | Daftar nama kolom tabel |
| `jumlah_baris(nama_tabel)` | Jumlah baris di tabel |
| `tutup()` / `tersambung()` | Tutup koneksi / cek status |

---

## `web_server` — Web Framework (v6.3)

Framework web untuk membuat API backend / server HTTP — berbasis stdlib Python
(`http.server`), tanpa dependency eksternal. Berpasangan dengan modul `web`
(HTTP client) untuk testing.

```
impor web_server

fungsi halaman(req)
    kembali req.kirim_json({"pesan": "Halo Dunia!", "sukses": benar})
selesai

fungsi detail(req)
    kembali req.kirim_json({"id": req.parameter["id"], "nama": "Budi"})
selesai

buat app = web_server.Buat()
app.rute("GET", "/", halaman)
app.rute("GET", "/pengguna/{id}", detail)
app.jalankan(8000)          # blocking; Ctrl+C berhenti
```

| Fungsi | Keterangan |
|--------|------------|
| `Buat()` | Buat instance server baru |
| `app.rute(metode, jalur, handler)` | Daftarkan route (GET/POST/PUT/DELETE/PATCH) |
| `app.get/post/put/hapus(jalur, handler)` | Shorthand routing |
| `app.jalankan(port, host?)` | Jalankan server (blocking) |
| `app.jalankan_async(port)` | Jalankan di thread (non-blocking, untuk test) |
| `app.berhenti()` | Hentikan server async |
| `app.atur_cors(benar)` | Aktifkan CORS untuk semua route |

Objek `req` (dikirim ke handler) berisi:
- `metode`, `jalur`, `jalur_lengkap` — info request
- `query` — dict query string (`/cari?kota=x` → `{"kota": "x"}`)
- `header` — dict header HTTP
- `body` — body mentah sebagai teks
- `json` — body JSON yang sudah di-parse (atau `kosong`)
- `parameter` — nilai route dinamis (`/pengguna/{id}` → `{"id": "5"}`)

Helper response di `req`:
- `req.kirim_teks(teks, status?)` / `req.kirim_json(data, status?)`
- `req.kirim_html(html, status?)` / `req.kirim_status(status?)`
- `req.kirim_file(jalur)` — static file dengan MIME type otomatis

Handler juga bisa `kembali` dict (auto-JSON) atau string (auto-teks).
Contoh lengkap: `examples/web_api.bro`.

---

## `kripto` — Keamanan & Kriptografi (v6.4)

Hashing, Base64, hashing password dengan salt acak, dan token acak aman
(crypto-grade) — berbasis `hashlib`, `base64`, dan `secrets` (tanpa dependency
eksternal).

```
impor kripto

tulis kripto.sha256("halo")            # 64 karakter hex
buat hash = kripto.hash_password("rahasia123")
tulis kripto.cek_password("rahasia123", hash)   # True
buat api_key = kripto.token(32)
```

| Fungsi | Keterangan |
|--------|------------|
| `md5(teks)` / `sha1(teks)` | Hash hex 32 / 40 karakter |
| `sha256(teks)` / `sha512(teks)` | Hash hex 64 / 128 karakter |
| `base64_encode(teks)` | Encode teks → Base64 |
| `base64_decode(teks)` | Decode Base64 → teks asli |
| `hash_password(kata_sandi)` | PBKDF2-SHA256 + salt acak (`algo$salt$hash`) |
| `cek_password(kata_sandi, hash)` | Verifikasi password (constant-time) |
| `token(panjang=32)` | Token hex acak aman (session / API key) |
| `bilangan_acak(batas=100)` | Bilangan acak crypto-grade (0..batas-1) |

Contoh lengkap: `examples/kripto.bro`.

---

## `arsip` — ZIP & Kompresi (v6.4)

Membuat/membaca arsip ZIP dan kompresi teks — berbasis `zipfile` dan `zlib`
(tanpa dependency eksternal).

```
impor arsip

arsip.buat_zip("backup.zip", ["a.txt", "b.txt"])
tulis arsip.daftar_zip("backup.zip")
arsip.ekstrak_zip("backup.zip", "restore/")

buat padat = arsip.kompres("teks panjang ...")   # lebih pendek (Base64+zlib)
tulis arsip.dekompres(padat)
```

| Fungsi | Keterangan |
|--------|------------|
| `buat_zip(nama, daftar_file)` | Buat arsip ZIP baru → `benar`/`salah` |
| `tambah_ke_zip(nama, daftar_file)` | Tambah file ke arsip yang sudah ada |
| `ekstrak_zip(nama, tujuan=".")` | Ekstrak semua isi → list nama file |
| `daftar_zip(nama)` | List nama file di dalam arsip |
| `kompres(teks)` | Kompres teks → string Base64 (zlib level 9) |
| `dekompres(data)` | Kembalikan teks asli dari hasil `kompres` |

Contoh lengkap: `examples/arsip.bro`.

---

## `terminal` — UX Terminal (v6.4)

Warna ANSI, gaya teks, progress bar, prompt interaktif, dan pesan status
untuk program CLI — murni stdlib Python.

```
impor terminal

tulis terminal.hijau("sukses")
terminal.sukses("Deploy berhasil")
tulis terminal.bilah_progress(7, 10)    # [███████░░░] 70%
buat nama = terminal.tanya("Nama kamu? ", "anonim")
```

| Fungsi | Keterangan |
|--------|------------|
| `merah/hijau/kuning/biru/magenta/cyan/putih/abu(teks)` | Warna teks ANSI |
| `warna(teks, nama)` | Warna dengan nama dinamis |
| `tebal/miring/garis_bawah/terbalik(teks)` | Gaya teks |
| `bersihkan()` | Escape sequence pembersih layar |
| `bilah_progress(sekarang, total, lebar=30)` | String progress bar `[███░░] 60%` |
| `cetak_progress(sekarang, total, lebar=30)` | Cetak progress inline (\r) |
| `tanya(pesan, default="")` | Prompt input interaktif |
| `tanya_ya(pesan)` | Prompt ya/tidak → `benar`/`salah` |
| `sukses/info/peringatan/gagal(pesan)` | Pesan status berwarna + ikon |
| `banner(teks, lebar=50)` | Banner dekoratif |

Contoh lengkap: `examples/terminal.bro`.

---

## `jalur` — Pathfinding & Gerakan (v6.6)

Pathfinding A* di grid tile, pengikut jalur otomatis, dan patroli waypoint
untuk AI musuh / NPC.

```
impor jalur

# A* pathfinding: 1 = dinding, 0 = bisa dilalui
buat peta = [[0,0,0],[1,1,0],[0,0,0]]
buat rute = jalur.cari_jalur(peta, (0,0), (2,2))  # list (x,y) atau kosong

# NPC mengikuti jalur
buat pengikut = jalur.IkutiJalur(rute, kecepatan=150)
pengikut.update(dt)          # panggil tiap frame
buat (x, y) = pengikut.posisi()

# Patroli bolak-balik antar waypoint
buat penjaga = jalur.Patroli([(100,0),(300,0)], kecepatan=120, mode="bolak-balik")
penjaga.update(dt)
```

| Fungsi | Keterangan |
|--------|------------|
| `cari_jalur(peta, mulai, tujuan)` | A* pathfinding → list (x,y) atau `kosong` |
| `jalur_ke_pixel(jalur, ukuran_tile)` | Konversi koordinat tile → pixel (tengah tile) |
| `IkutiJalur(titik, kecepatan, loop?)` | Gerakkan objek sepanjang polyline |
| `Patroli(waypoint, kecepatan, mode?)` | Patroli waypoint (`loop`/`bolak-balik`/`sekali`) |

**IkutiJalur**: `update(dt)`, `posisi()`, `selesai` (bool), `loop=benar` untuk
mengulang terus-menerus.

**Patroli**: mode `"loop"` (kembali ke awal), `"bolak-balik"` (pantul), atau
`"sekali"` (berhenti). Ada `indeks_sekarang()`, `arah()` (vektor unit), dan
`selesai`.

---

## `efek` — Efek Layar & Partikel Teks (v6.6)

Efek visual siap pakai: flash layar, vignette, teks melayang (damage number),
dan efek denyut (pulse).

```
impor efek

# Flash putih saat player kena
buat flash = efek.Flash(warna="putih", durasi=0.3)
flash.picu()
# ...di loop update:
flash.update(dt)
flash.gambar()              # overlay layar penuh dengan alpha menurun

# Damage number melayang naik lalu pudar
buat teks = efek.TeksMelayang("25", 100, 100, warna="kuning")
teks.update(dt)
teks.gambar()
```

| Fungsi | Keterangan |
|--------|------------|
| `Flash(warna?, durasi?, layar?)` | Overlay layar penuh yang memudar |
| `Vignette(warna?, intensitas?)` | Pinggiran layar gelap (statis) |
| `TeksMelayang(teks, x, y, warna?, kecepatan?)` | Teks naik lalu memudar |
| `Pulsa(min?, maks?, kecepatan?)` | Nilai denyut sinus 0..1 untuk efek berdenyut |

Semua efek punya `update(dt)` & `gambar()` (butuh pygame aktif). `Pulsa`
murni kalkulasi: `p.nilai()` mengembalikan 0..1.

---

## Module List

| Module | Fungsi |
|--------|--------|
| `angka` | Matematika lanjut — pi, e (nilai), sqr, abs, min, max |
| `vektor` | Vektor 2D/3D |
| `audio` | Sound effects |
| `grafis` | Graphics rendering |
| `game` | Game utilities |
| `jalur` | Pathfinding A* & gerakan AI — cari_jalur, IkutiJalur, Patroli (v6.6) |
| `efek` | Efek layar — Flash, Vignette, TeksMelayang, Pulsa (v6.6) |
| `web` | HTTP requests (client) |
| `sistem_operasi` | OS operations |
| `sistem` | System info |
| `debug` | Debugging tools |
| `random` | Angka random |
| `waktu` | Waktu & sleep |
| `crypto` | Encryption |
| `database` | SQLite wrapper — buka, query, eksekusi_sql, tabel |
| `web_server` | Web framework — routing, JSON, static files (v6.3) |
| `kripto` | Keamanan — hash md5/sha1/sha256/sha512, base64, password PBKDF2, token (v6.4) |
| `arsip` | ZIP — buat/tambah/ekstrak/daftar, kompresi teks zlib+base64 (v6.4) |
| `terminal` | UX CLI — warna ANSI, gaya teks, progress bar, prompt, pesan status (v6.4) |
| `regex` | Regular expressions |
| `json` | JSON parsing |
| `csv` | CSV parsing |
| `math` | Math functions |
| `visualisasi` | Chart & grafik data (ASCII, SVG, HTML) |
| `statistics` | Statistical analysis |
| `collections` | Data structures |
