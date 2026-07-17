# 🔥 Fitur BroLang v3.1

> **BroLang v3.1 itu fiturnya lengkap banget.** Mulai dari dasar sampe advanced, semua ada.

## 📋 Tabel Fitur

### Bahasa Dasar

| Fitur | Keterangan | Status |
|-------|-----------|--------|
| `buat` | Variabel declaration | ✅ |
| `fungsi` | Fungsi dengan parameter | ✅ |
| `kelas` | OOP (inheritance, polymorphism) | ✅ |
| `muat` | Import module | ✅ |
| `tulis` | Print output | ✅ |
| `kembali` | Return value | ✅ |
| `pass` | No-op placeholder | ✅ |
| `hapus` | Hapus variabel/index | ✅ |
| `pastikan` | Runtime assertion | ✅ |

### Tipe Data

| Tipe | Keterangan | Status |
|------|-----------|--------|
| Angka | Integer & float | ✅ |
| Teks | String (1 baris / multi-line) | ✅ |
| Boolean | `benar` / `salah` | ✅ |
| List | Mutable, ordered collection | ✅ |
| Tuple | Immutable, ordered collection | ✅ |
| Set | Unordered, unique collection | ✅ |
| Objek (Dict) | Key-value pairs | ✅ |
| Kosong | Null value | ✅ |
| Lambda | Anonymous function | ✅ |

### Operator

| Operator | Fungsi | Status |
|----------|--------|--------|
| `+ - * / % **` | Aritmatika | ✅ |
| `== != > < >= <=` | Perbandingan | ✅ |
| `is` / `is bukan` | Identity comparison | ✅ |
| `dalam` / `bukan dalam` | Membership test | ✅ |
| `dan` / `atau` / `bukan` | Logika | ✅ |
| `& \| ^ ~ << >>` | Bitwise | ✅ |
| `+= -= *= /= %= **=` | Augmented assignment | ✅ |

### Control Flow

| Fitur | Keterangan | Status |
|-------|-----------|--------|
| `jika...maka...lainnya...selesai` | If/else | ✅ |
| `selama...lakukan...selesai` | While loop | ✅ |
| `untuk...lakukan...selesai` | For loop | ✅ |
| `hentikan` | Break | ✅ |
| `lanjutkan` | Continue | ✅ |
| `untuk...lakukan...lainnya...selesai` | For-else | ✅ |
| `selama...lakukan...lainnya...selesai` | While-else | ✅ |

### Advanced Features

| Fitur | Keterangan | Status |
|-------|-----------|--------|
| `lalu(x) ...` | Lambda expression | ✅ |
| `[x untuk x dalam list]` | List comprehension | ✅ |
| `"a" jika kondisi lainnya "b"` | Ternary expression | ✅ |
| `1 < x < 10` | Chained comparison | ✅ |
| Closures | Lambda/fungsi nangkep scope luar | ✅ |
| `class` / `@dataclass` | OOP | ✅ |
| `super()` | Inheritensi | ✅ |
| `try...kecuali...selesai` | Error handling | ✅ |
| `lempar "error"` | Raise exception | ✅ |
| `final` | Finally block | ✅ |
| `global x` / `nonlokal x` | Scope control | ✅ |
| Tuple `(1, 2, 3)` | Immutable list | ✅ |
| Set `{1, 2, 3}` | Unique collection | ✅ |
| Slicing `list[1:3]` | Potong list/string | ✅ |
| `is` / `is bukan` | Identity comparison | ✅ |
| `dalam` / `bukan dalam` | Membership test | ✅ |

### String Features

| Fitur | Contoh | Status |
|-------|--------|--------|
| Escape sequences | `\n \t \\` | ✅ |
| String methods | `.atas()`, `.bawah()`, `.ganti()` | ✅ |
| String concatenation | `"Halo" + " Dunia"` | ✅ |
| String slicing | `"Hello"[0:5]` | ✅ |

### List Methods

| Method | Fungsi | Status |
|--------|--------|--------|
| `.tambah(x)` | Append | ✅ |
| `.sisipkan(i, x)` | Insert at index | ✅ |
| `.hapus(x)` | Remove first occurrence | ✅ |
| `.pop()` | Remove & return last | ✅ |
| `.urutkan()` | Sort | ✅ |
| `.balik()` | Reverse | ✅ |
| `.indeks(x)` | Find index | ✅ |
| `.jumlah()` | Sum all elements | ✅ |
| `.rata_rata()` | Average | ✅ |
| `.min()` | Minimum | ✅ |
| `.max()` | Maximum | ✅ |
| `.salin()` | Copy | ✅ |
| `.kosongkan()` | Clear all | ✅ |
| `.ada(x)` | Check membership | ✅ |
| `.panjang()` | Length | ✅ |
| `.isi(x)` | Fill with value | ✅ |
| `.gabung(s)` | Join to string | ✅ |
| `.potong()` | Slice | ✅ |
| `.set(i, x)` | Set at index | ✅ |
| `.ambil(i)` | Get at index | ✅ |
| `.perbarui(i, x)` | Update at index | ✅ |

### Dict Methods

| Method | Fungsi | Status |
|--------|--------|--------|
| `.kunci()` | All keys | ✅ |
| `.nilai()` | All values | ✅ |
| `.item()` | All items | ✅ |
| `.punya(k)` | Key exists | ✅ |
| `.ambil(k, default)` | Get with default | ✅ |
| `.set(k, v)` | Set key-value | ✅ |
| `.hapus(k)` | Delete key | ✅ |
| `.kosongkan()` | Clear all | ✅ |
| `.panjang()` | Length | ✅ |
| `.gabung(other)` | Merge dicts | ✅ |
| `.salin()` | Copy | ✅ |

### Game Dev Features

| Feature | Keterangan | Status |
|---------|-----------|--------|
| `grafis` | 2D graphics (SDL2) | ✅ |
| `game` | Game utilities | ✅ |
| `audio` | Sound effects | ✅ |
| `input` | Keyboard/mouse handling | ✅ |
| `vektor` | 2D/3D vector math | ✅ |

---

## 📖 Contoh Lengkap

### Program Pertama

```
tulis "Halo Dunia!"
```

### Variabel & Operasi

```
buat nama = "Budi"
buat umur = 17
tulis "Nama: " + nama + ", Umur: " + teks(umur)
```

### Fungsi

```
fungsi tambah(a, b)
    kembali a + b
selesai

tulis tambah(10, 5)
```

### Lambda

```
buat kali2 = lalu(x) x * 2
tulis kali2(10)    # 20
```

### Class

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
```

### Game

```
muat grafis
muat game

grafis.buat_layar(800, 600)
grafis.set_judul("Game Saya")

buat x = 400
buat y = 300

selama benar lakukan
    grafis.mulai_frame()
    grafis.isi_layar(0, 0, 0)

    jika game.input_ditekan("d") maka
        x = x + 5
    selesai

    grafis.gambar_kotak(x, y, 50, 50, 0, 100, 255)
    grafis.selesai_frame()
selesai
```
