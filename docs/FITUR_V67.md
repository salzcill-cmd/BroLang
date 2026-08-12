# Fitur Baru — BroLang v6.7

BroLang v6.7 menghadirkan **fitur bahasa modern** (spread/rest parameter,
multiple return), **melengkapi bytecode VM** (range-for, destructuring,
pipeline, for-each kini berfungsi penuh), dan **dua fitur game dev**
(screen shake + synth audio procedural).

Daftar isi:
1. [Rest parameter `...nama`](#1-rest-parameter-nama)
2. [Spread call `f(...args)`](#2-spread-call-fargs)
3. [Spread list `[...a, 1]`](#3-spread-list-a-1)
4. [Multiple return `kembali a, b`](#4-multiple-return-kembali-a-b)
5. [Bytecode VM kini lengkap](#5-bytecode-vm-kini-lengkap)
6. [Game dev: Guncangan & synth audio](#6-game-dev-guncangan--synth-audio)

---

## 1. Rest parameter `...nama`

Fungsi bisa menampung **semua sisa argumen** ke dalam satu list:

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

Rest parameter boleh digabung dengan parameter biasa — harus diletakkan
di posisi **terakhir**:

```bro
fungsi sapa(nama, ...sisanya)
    tulis "Halo " + nama + ", tambahan: " + teks(sisanya)
selesai

sapa("Budi")                    # Halo Budi, tambahan: []
sapa("Ani", 1, 2)               # Halo Ani, tambahan: [1, 2]
```

Bekerja di semua bentuk fungsi: `fungsi`, lambda `lalu(...)`, method
kelas, `asinkron fungsi`, dan generator.

---

## 2. Spread call `f(...args)`

Membongkar list saat memanggil fungsi — setiap elemen menjadi satu
argumen:

```bro
fungsi kali3(a, b, c)
    kembali a * b * c
selesai

buat nilai = [2, 3, 4]
tulis kali3(...nilai)            # 24
```

Bisa dikombinasikan dengan argumen biasa, keyword arguments, dan method:

```bro
tulis kali3(...[1, 2], 3)        # 1 * 2 * 3 = 6
buat g = Gabung()
g.tampil(...nilai)               # method juga didukung
```

---

## 3. Spread list `[...a, 1]`

Menggabungkan list di dalam literal list:

```bro
buat dasar = [1, 2]
buat gabung = [...dasar, 3, 4]
tulis gabung                     # [1, 2, 3, 4]
```

Spread bisa muncul di mana saja di dalam literal:

```bro
buat a = [1, 2]
buat b = [5, 6]
buat semua = [...a, 3, 4, ...b]  # [1, 2, 3, 4, 5, 6]
```

---

## 4. Multiple return `kembali a, b`

Fungsi bisa mengembalikan beberapa nilai sekaligus, dan hasilnya
langsung dibongkar dengan destructuring:

```bro
fungsi bagi_dan_sisa(a, b)
    kembali a / b, a % b
selesai

buat [hasil, sisa] = bagi_dan_sisa(17, 5)
tulis hasil, sisa                # 3.4 2
```

Tanpa destructuring, hasilnya berupa tuple:

```bro
buat r = bagi_dan_sisa(17, 5)
tulis r                          # (3.4, 2)
```

---

## 5. Bytecode VM kini lengkap

Sejak v5.2 beberapa fitur bahasa **belum didukung** oleh compiler
bytecode (`bro build` / `bro benchmark --vm`) — kini semuanya berfungsi
penuh dan konsisten dengan interpreter & transpiler:

| Fitur | Sebelum v6.7 | Sesudah v6.7 |
|-------|--------------|--------------|
| `untuk i dari A sampai B langkah S` | `NotImplementedError` | ✅ inklusif, step otomatis, guard step 0 |
| `buat [a, b] = list` / `buat {x, y} = objek` | `NotImplementedError` | ✅ opcode `DICT_GET` (kunci hilang → `kosong`) |
| `nilai \|> fungsi` | `NotImplementedError` | ✅ termasuk `peta`/`saring`/`kurangi` |
| `untuk setiap item dalam iterable` | diam-diam dilewati | ✅ counter indeks manual |
| rest parameter | tidak didukung | ✅ `rest_pos` di `CLOSURE`/`VMFunction`/method |

Bonus perbaikan: `untuk setiap` kini juga dikenali **SemanticAnalyzer**
(`visit_ForEachNode`), sehingga `bro run` tidak lagi error untuk program
yang memakai for-each.

---

## 6. Game dev: Guncangan & synth audio

### `efek.Guncangan` — screen shake

Screen shake berbasis *trauma*: getaran kuat saat baru dipicu, lalu
membaik secara eksponensial — natural dan tidak membuat mual:

```bro
impor efek

buat guncang = efek.Guncangan(kekuatan_maks=16, redaman=1.2)

fungsi update(dt)
    jika kena_tembakan maka
        guncang.guncang(0.8)      # 0..1 — seberapa keras
    selesai
    guncang.update(dt)
selesai

fungsi gambar(screen)
    buat [ox, oy] = guncang.offset()   # offset pixel untuk kamera/gambar
    grafis.segi_panjang(ox + 100, oy + 100, 50, 50, "merah")
selesai
```

API: `guncang(kekuatan)` (0..1), `offset()` → `(x, y)` random terarah,
`update(dt)` (memulihkan trauma), `set_redaman(nilai)`, dan
`kekuatan_sekarang()`. Logika berjalan **tanpa pygame** — mudah di-test.

### `audio` — synth procedural

Buat efek suara langsung dari kode — **tanpa file eksternal** (murni
stdlib Python, menghasilkan bytes WAV):

```bro
impor audio

# Nada sinus dengan fade in/out
buat nada = audio.nada(440, 0.2)          # A4, 0.2 detik

# Efek siap pakai
buat pew = audio.laser()                  # sweep frekuensi turun
buat led = audio.ledakan()                # noise + low-pass
buat bip = audio.blip()                   # square pendek
```

Setiap fungsi mengembalikan bytes WAV (`RIFF`/`WAVE`) yang valid —
simpan ke file lalu mainkan dengan modul game/audio biasa:

```bro
buat f = file.buka("laser.wav", "wb")
f.tulis(audio.laser())
f.tutup()
```

---

## Ringkasan sintaks

```bro
# 1. Rest parameter
fungsi nama(param_biasa, ...sisa)

# 2. Spread call
f(...list)

# 3. Spread list
buat list = [...a, 1, 2]

# 4. Multiple return
fungsi nama()
    kembali a, b
selesai
buat [x, y] = nama()

# 5. Screen shake
buat g = efek.Guncangan(16)
g.guncang(0.8)
buat [ox, oy] = g.offset()

# 6. Synth audio
buat wav = audio.laser()
```
