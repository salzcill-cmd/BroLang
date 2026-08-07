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

## `sistem` — Info System

```
muat sistem

tulis sistem.versi()        # Versi BroLang
tulis sistem.platform()     # linux / windows / darwin
```

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

```
muat web

buat respon = web.get("https://api.example.com/data")
tulis respon.teks
```

## `sistem_operasi` — OS Operations

```
muat sistem_operasi

buat daftar = sistem_operasi.list_dir(".")
untuk file dalam daftar lakukan
    tulis file
selesai
```

---

## Module List

| Module | Fungsi |
|--------|--------|
| `angka` | Matematika lanjut (pi, e, sqr, abs) |
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
| `database` | Database operations |
| `regex` | Regular expressions |
| `json` | JSON parsing |
| `csv` | CSV parsing |
| `math` | Math functions |
| `visualisasi` | Chart & grafik data (ASCII, SVG, HTML) |
| `statistics` | Statistical analysis |
| `collections` | Data structures |
