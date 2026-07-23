# Dasar Bahasa BroLang

> **Belajar dari nol?** Mulai dari sini ya bos.

## Tipe Data

| Tipe | Nama BroLang | Contoh |
|------|-------------|--------|
| Integer | `angka` | `42` |
| Float | `desimal` | `3.14` |
| String | `teks` | `"halo"` |
| Boolean | `boolean` | `benar`, `salah` |
| List | `list` | `[1, 2, 3]` |
| Tuple | `tuple` | `(1, 2, 3)` |
| Set | `set` | `{1, 2, 3}` |
| Dictionary | `objek` | `{"nama": "Budi"}` |
| Null | `kosong` | `kosong` |

```
tulis tipe(42)         # angka
tulis tipe("halo")     # teks
tulis tipe(benar)      # boolean
tulis tipe([1,2,3])    # list
tulis tipe((1,2,3))    # tuple
tulis tipe({1,2,3})    # set
tulis tipe(kosong)     # kosong
```

---

## Variabel

```
buat nama = "Budi"
buat umur = 17
buat tinggi = 170.5
buat siswa = benar
buat nilai = kosong

# Reassign (ga perlu "buat" lagi)
umur = 18

# Multi variable
buat a = 1, b = 2, c = 3
```

> **Catatan:** `buat` cuma dipake waktu pertama kali deklarasi variabel. Kalo mau ganti nilainya, tinggal tulis nama variabelnya aja.

---

## Operator

### Aritmatika

| Operator | Fungsi | Contoh |
|----------|--------|--------|
| `+` | Penjumlahan | `10 + 3 = 13` |
| `-` | Pengurangan | `10 - 3 = 7` |
| `*` | Perkalian | `10 * 3 = 30` |
| `/` | Pembagian | `10 / 3 = 3.333` |
| `%` | Modulo (sisa bagi) | `10 % 3 = 1` |
| `**` | Pangkat | `10 ** 3 = 1000` |

### Perbandingan

| Operator | Fungsi |
|----------|--------|
| `==` | Sama dengan |
| `!=` | Tidak sama dengan |
| `>` | Lebih besar |
| `<` | Lebih kecil |
| `>=` | Lebih besar atau sama |
| `<=` | Lebih kecil atau sama |
| `is` | Identitas (sama objek) |
| `is bukan` | Bukan identitas |

### Keanggotaan

| Operator | Fungsi |
|----------|--------|
| `dalam` | Ada di dalam list/string |
| `bukan dalam` | Tidak ada di dalam |

```
buat angka = [1, 2, 3]
tulis 3 dalam angka      # benar
tulis 6 dalam angka      # salah
tulis bukan 6 dalam angka  # benar
```

### Logika

| Operator | Fungsi |
|----------|--------|
| `dan` | AND |
| `atau` | OR |
| `bukan` | NOT |

```
jika umur >= 17 dan memiliki_sim maka
    tulis "Boleh menyetir"
selesai
```

### Bitwise

| Operator | Fungsi |
|----------|--------|
| `&` | AND |
| `|` | OR |
| `^` | XOR |
| `~` | NOT |
| `<<` | Left Shift |
| `>>` | Right Shift |

```
tulis 6 & 3    # 2
tulis 6 | 3    # 7
tulis 6 ^ 3    # 5
tulis 1 << 3   # 8
tulis 8 >> 1   # 4
```

### Augmented Assignment

```
buat x = 5
x += 3    # x = 8
x -= 2    # x = 6
x *= 4    # x = 24
x /= 6    # x = 4.0
x %= 3    # x = 1.0
x **= 2   # x = 1.0
```

### Null Coalescing (v5.0)

```
buat nama = kosong
tulis nama ?? "Anonim"    # Anonim

buat umur = 17
tulis umur ?? 0            # 17
```

Kalo nilainya `kosong`, otomatis pake nilai sebelah kanan. Ga perlu nulis `jika` panjang-panjang.

---

## Percabangan (If/Else)

```
buat nilai = 85

jika nilai >= 90 maka
    tulis "Grade A — Mantap!"
lainnya jika nilai >= 80 maka
    tulis "Grade B — Lumayan!"
lainnya jika nilai >= 70 maka
    tulis "Grade C — Masih oke"
lainnya
    tulis "Grade D — Belajar lagi ya"
selesai
```

---

## Perulangan

### For Loop

```
# Pake range
untuk i dalam range(5) lakukan
    tulis i
selesai
# Output: 0 1 2 3 4

# Pake list langsung
untuk buah dalam ["apel", "pisang", "jeruk"] lakukan
    tulis "Buah favorit: " + buah
selesai
```

### For-Each (v5.0)

```
buat buah = ["apel", "mangga", "jeruk"]
untuk setiap item dalam buah lakukan
    tulis item
selesai
# Output: apel, mangga, jeruk
```

Lebih pendek dari for loop biasa.

### While Loop

```
buat i = 0
selama i < 5 lakukan
    tulis i
    i = i + 1
selesai
```

### Loop Control

```
# break — berhenti di tengah
untuk i dalam range(10) lakukan
    jika i == 5 maka
        hentikan
    selesai
    tulis i
selesai

# continue — skip satu iterasi
untuk i dalam range(5) lakukan
    jika i == 2 maka
        lanjutkan
    selesai
    tulis i
selesai
```

### For-Else / While-Else

```
# Else dijalankan kalo loop ga break
untuk i dalam range(5) lakukan
    tulis i
lainnya
    tulis "Loop selesai tanpa break!"
selesai
```

---

## String

```
buat s1 = "Hello"
buat s2 = 'World'
buat s3 = """Multi-line
string di BroLang"""

# Concatenation
buat s = "Halo " + "Dunia"

# Escape sequences
tulis "Baris 1\nBaris 2"
tulis "Tab\tselanjutnya"

# Slicing
buat kata = "Hello World"
tulis kata[0:5]    # Hello
tulis kata[6:]     # World
```

---

## List

```
buat angka = [1, 2, 3, 4, 5]
tulis angka[0]          # 1
tulis angka[-1]         # 5
tulis jumlah(angka)     # 5 (panjang list)

# Nested list
buat matriks = [[1, 2], [3, 4]]
tulis matriks[0][1]     # 2

# Slicing
tulis angka[1:4]        # [2, 3, 4]
tulis angka[:3]         # [1, 2, 3]
tulis angka[::2]        # [1, 3, 5]
```

### List Methods

```
buat angka = [3, 1, 2]
angka.tambah(4)           # [3, 1, 2, 4]
angka.urutkan()           # [1, 2, 3, 4]
angka.balik()             # [4, 3, 2, 1]
angka.hapus(4)            # [3, 2, 1]
angka.sisipkan(1, 99)     # [3, 99, 2, 1]
tulis angka.jumlah()      # 105
```

---

## Dictionary (Objek)

```
buat orang = {
    "nama": "Budi",
    "umur": 17,
    "jurusan": "Informatika"
}

tulis orang["nama"]              # Budi
orang["pekerjaan"] = "Programmer"  # Tambah field baru
```

### Dict Methods

```
buat kamus = {"a": 1, "b": 2}
tulis kamus.kunci()       # ["a", "b"]
tulis kamus.nilai()       # [1, 2]
tulis kamus.punya("a")    # benar
```

---

## Tuple

```
buat t = (1, 2, 3)
tulis t              # (1, 2, 3)
tulis t[0]           # 1
tulis t[2]           # 3

# Tuple ga bisa diubah (immutable)
# t[0] = 99  ← ERROR!
```

---

## Set

```
buat s = {1, 2, 3, 2, 1}
tulis s              # {1, 2, 3} (duplikat dihapus)

# Operasi set
buat a = {1, 2, 3}
buat b = {2, 3, 4}
```

---

## Ternary Expression

```
buat umur = 17
buat status = "Dewasa" jika umur >= 18 lainnya "Anak-anak"
tulis status  # Output: Anak-anak
```

**Satu baris langsung dapet hasilnya.** Ga perlu pake `jika...lainnya` yang panjang.

---

## Chained Comparison (v5.0)

```
buat x = 5
tulis 1 < x < 10      # benar
tulis 1 < x < 3       # salah
tulis 1 <= x <= 5     # benar
```

**Ga perlu pake `dan` lagi.** Langsung chain aja.
