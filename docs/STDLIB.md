# Standard Library

> **BroLang punya module built-in yang keren-keren.** Tinggal pake aja.

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
| `statistics` | Statistical analysis |
| `collections` | Data structures |
