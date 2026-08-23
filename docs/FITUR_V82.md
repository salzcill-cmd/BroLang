# Fitur Baru v8.2 ✨

BroLang v8.2 menambah **1 fitur bahasa** dan **4 modul stdlib** baru:

1. **`properti` decorator** — syntax bersih untuk getter/setter di kelas
2. **`statistik`** — fungsi statistik dasar
3. **`zaman`** — timer & stopwatch
4. **`penampilan`** — pretty print & format data
5. **`warna`** — warna terminal ANSI & konversi

---

## 1. `properti` Decorator — Getter/Clean Setter

Sintaks bersih untuk property getter/setter di kelas, mirip Python `@property`.

### Getter saja (read-only)

```bro
kelas Lingkaran
    fungsi __init__(self, jari)
        self._jari = jari
    selesai

    @properti
    fungsi luas(self)
        kembali 3.14 * self._jari * self._jari
    selesai
selesai

buat l = Lingkaran(5)
tulis l.luas    # 78.5
```

### Getter + Setter

```bro
kelas Suhu
    fungsi __init__(self, derajat)
        self._derajat = derajat
    selesai

    @properti
    fungsi derajat(self)
        kembali self._derajat
    selesai

    @derajat.setter
    fungsi set_derajat(self, v)
        self._derajat = v
    selesai
selesai

buat s = Suhu(36)
tulis s.derajat       # 36 (getter)
s.derajat = 37        # setter
tulis s.derajat       # 37
```

### Property dengan validasi

```bro
kelas Akun
    fungsi __init__(self, saldo)
        self._saldo = saldo
    selesai

    @properti
    fungsi saldo(self)
        kembali self._saldo
    selesai

    @saldo.setter
    fungsi set_saldo(self, v)
        jika v >= 0 maka
            self._saldo = v
        selesai
    selesai
selesai

buat a = Akun(1000)
a.saldo = 500       # OK
tulis a.saldo        # 500
a.saldo = -100       # ditolak (tidak ada perubahan)
```

### Catatan Implementasi
- **Interpreter**: `@properti` decorator sepenuhnya didukung dengan property lookup
- **Transpiler & VM**: Fallback ke konvensi `_<nama>()` getter / `_<nama>_set(v)` setter

---

## 2. Modul `statistik`

Fungsi statistik dasar — rerata, median, modus, varians, simpangan baku, korelasi.

```bro
impor statistik

buat data = [10, 20, 30, 40, 50]

tulis statistik.rerata(data)              # 30.0
tulis statistik.median(data)              # 30
tulis statistik.modus([1, 1, 2, 3])       # [1]
tulis statistik.modus_satu([1, 1, 2, 3])  # 1
tulis statistik.varians(data)             # 200.0
tulis statistik.simpangan_baku(data)      # 14.142...
tulis statistik.kuartil(data, 1)          # Q1 (25th percentile)
tulis statistik.kuartil(data, 3)          # Q3 (75th percentile)
tulis statistik.persentil(data, 90)       # 90th percentile
tulis statistik.rank([10, 20, 30], 20)    # 2

# Korelasi Pearson antara dua data
buat x = [1, 2, 3, 4, 5]
buat y = [2, 4, 6, 8, 10]
tulis statistik.korelasi(x, y)           # 1.0 (korelasi sempurna)

# Ringkasan lengkap
tulis statistik.ringkasan(data)
# {"min": 10, "max": 50, "rerata": 30.0, "median": 30, ...}
```

### Fungsi

| Fungsi | Keterangan |
|--------|------------|
| `rerata(data)` | Rerata (mean) |
| `median(data)` | Median (nilai tengah) |
| `modus(data)` | Modus (nilai paling sering, bisa lebih dari satu) |
| `modus_satu(data)` | Modus tunggal |
| `varians(data, pop=True)` | Varians (populasi/sampel) |
| `simpangan_baku(data, pop=True)` | Simpangan baku |
| `kuartil(data, q)` | Kuartil (1, 2, atau 3) |
| `persentil(data, p)` | Persentil (0-100) |
| `korelasi(x, y)` | Korelasi Pearson (-1 sampai 1) |
| `rank(data, val)` | Peringkat sebuah nilai |
| `ringkasan(data)` | Ringkasan statistik lengkap (dict) |

---

## 3. Modul `zaman`

Timer, stopwatch, dan utilitas waktu.

```bro
impor zaman

# Stopwatch — ukur waktu eksekusi
buat sw = zaman.Stopwatch()
sw.mulai()
# ... kode yang mau diukur ...
sw.berhenti()
tulis sw.detik            # 1.234 (detik)
tulis sw.mili_detik       # 1234.0 (mili detik)
tulis sw.lap_times        # Daftar waktu lap

# Timer countdown
buat timer = zaman.Timer(5.0)
timer.mulai()
tulis timer.sisa()        # ~5.0 (menurun)
tulis timer.habis         # False
tulis timer.persentase    # Persentase waktu berlalu

# Waktu berlalu
buat t0 = zaman.sekarang()
# ... kode ...
tulis zaman.berlalu(t0)   # 0.050 (detik)

# Format waktu
tulis zaman.uman(3725)    # "1j 2m 5d"
tulis zaman.detik_milidetik(1.234)  # "1d 234md"
```

### Class

| Class | Keterangan |
|-------|------------|
| `Stopwatch()` | Stopwatch: `mulai()`, `berhenti()`, `lap()`, `reset()` |
| `Timer(durasi)` | Countdown: `mulai()`, `sisa()`, `habis`, `persentase` |

### Fungsi

| Fungsi | Keterangan |
|--------|------------|
| `sekarang()` | Waktu saat ini (presisi tinggi) |
| `sekarang_unix()` | Waktu Unix |
| `berlalu(t0)` | Detik sejak t0 |
| `tidur(detik)` | Sleep |
| `uman(detik)` | Format manusiawi: "1j 2m 5d" |
| `detik_milidetik(detik)` | Format: "1d 234md" |

---

## 4. Modul `penampilan`

Pretty print & format data.

```bro
impor penampilan

# Format angka
tulis penampilan.angka(1234567)          # "1,234,567"
tulis penampilan.angka_desimal(3.14)     # "3.14"
tulis penampilan.persen(0.75)            # "75.0%"

# Daftar
tulis penampilan.daftar(["apel", "mangga"], style="bullet")  # • apel / • mangga
tulis penampilan.bernomic(["a", "b"])    # 1. a / 2. b

# Tabel
buat data = [{"nama": "Budi", "umur": 25}]
tulis penampilan.tabel(data)
# nama | umur
# -----|-----
# Budi | 25

# Pohon
buat obj = {"akar": {"anak1": {}, "anak2": {"cucu": {}}}}
tulis penampilan.pohon(obj)
# akar
# ├── anak1
# └── anak2
#     └── cucu

# Key-value pairs
tulis penampilan.kvp({"nama": "Budi", "umur": 25})

# JSON terformat
tulis penampilan.json_indented({"nama": "Budi"})

# Progress bar
tulis penampilan.horizontal(0.7)
# [██████████████░░░░░░░░░░░░░░░░░░░░░░░░░░] 70%
```

### Fungsi

| Fungsi | Keterangan |
|--------|------------|
| `tabel(data, columns?, padding?)` | Format list objek sebagai tabel ASCII |
| `daftar(items, style?)` | Daftar terformat (bullet/number/letter/roman) |
| `pohon(data, indent?)` | Tree view recursive |
| `angka(n, separator?)` | Angka dengan separator ribuan |
| `angka_desimal(n, desimals?)` | Angka desimal terformat |
| `persen(n, desimals?)` | Format persentase |
| `kvp(data)` | Key-value pairs |
| `json_indented(data, indent?)` | JSON terformat |
| `horizontal(data, lebar?)` | Progress bar ASCII |
| `bernomic(items, start?)` | Daftar bernomor |

---

## 5. Modul `warna`

Warna terminal ANSI, gradient, kotak, konversi warna.

```bro
impor warna

# Teks berwarna
tulis warna.merah("Error!")
tulis warna.hijau("Sukses!")
tulis warna.kuning("Peringatan")
tulis warna.biru("Info")

# Kustom
tulis warna.ansi("Halo", huruf="putih", latar="biru", tebal=benar)

# Gradient & Rainbow
tulis warna.gradient("Halo!", (255, 0, 0), (0, 0, 255))
tulis warna.rainbow("BroLang!")

# Kotak & dekorasi
tulis warna.kotak("Penting", warna="merah")
tulis warna.garis(40)
tulis warna.judul("Chapter 1")

# Konversi warna
tulis warna.rgb_to_hex(255, 128, 0)     # "#ff8000"
tulis warna.hex_to_rgb("#ff8000")        # (255, 128, 0)
```

### Fungsi Warna

| Fungsi | Keterangan |
|--------|------------|
| `merah(teks)` | Teks merah |
| `hijau(teks)` | Teks hijau |
| `biru(teks)` | Teks biru |
| `kuning(teks)` | Teks kuning |
| `ansi(teks, huruf?, latar?, tebal?, miring?)` | Custom ANSI styling |
| `tebal(teks)` | Bold |
| `miring(teks)` | Italic |
| `garis_bawah(teks)` | Underline |
| `dim(teks)` | Dimmed |
| `gradient(teks, awal, akhir)` | Gradient per karakter |
| `rainbow(teks)` | Rainbow per karakter |

### Konversi & Dekorasi

| Fungsi | Keterangan |
|--------|------------|
| `rgb_to_hex(r, g, b)` | RGB → hex string |
| `hex_to_rgb(hex)` | Hex → tuple RGB |
| `kotak(teks, warna?, style?)` | Bungkus teks dalam kotak |
| `garis(lebar?, char?)` | Garis horizontal |
| `judul(teks, level?)` | Judul terdekorasi |
