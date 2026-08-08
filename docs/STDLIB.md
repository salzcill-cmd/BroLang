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

tulis sistem.versi()        # 6.2.0 (Versi BroLang)
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

## Module List

| Module | Fungsi |
|--------|--------|
| `angka` | Matematika lanjut — pi, e (nilai), sqr, abs, min, max |
| `vektor` | Vektor 2D/3D |
| `audio` | Sound effects |
| `grafis` | Graphics rendering |
| `game` | Game utilities |
| `web` | HTTP requests |
| `sistem_operasi` | OS operations |
| `sistem` | System info |
| `debug` | Debugging tools |
| `random` | Angka random |
| `waktu` | Waktu & sleep |
| `crypto` | Encryption |
| `database` | SQLite wrapper — buka, query, eksekusi_sql, tabel |
| `regex` | Regular expressions |
| `json` | JSON parsing |
| `csv` | CSV parsing |
| `math` | Math functions |
| `visualisasi` | Chart & grafik data (ASCII, SVG, HTML) |
| `statistics` | Statistical analysis |
| `collections` | Data structures |
