# ⚙️ Fungsi

> **Fungsi di BroLang itu flexible banget.** Bisa default params, lambda, closures, sampe keyword arguments.

## 📝 Fungsi Biasa

```
fungsi sapa(nama)
    tulis "Halo, " + nama + "!"
selesai

sapa("Budi")    # Halo, Budi!
```

## 🔙 Return Value

```
fungsi tambah(a, b)
    kembali a + b
selesai

buat hasil = tambah(10, 5)
tulis hasil    # 15
```

## 🎯 Default Parameters

```
fungsi sapa(nama, sapaan = "Halo")
    tulis sapaan + ", " + nama + "!"
selesai

sapa("Budi")                  # Halo, Budi!
sapa("Budi", "Selamat pagi")  # Selamat pagi, Budi!
```

**Ga wajib isi semua parameter.** Kalo ga diisi, pake nilai default-nya.

## ⚡ Lambda (Anonymous Function)

```
buat kali = lalu(x) x * 2
tulis kali(5)    # 10

buat tambah = lalu(a, b) a + b
tulis tambah(3, 4)    # 7

# Lambda pake di higher-order function
buat angka = [1, 2, 3, 4, 5]
buat kuadrat = angka.filter(lalu(x) x > 2)
tulis kuadrat    # [3, 4, 5]
```

**Satu baris, langsung jadi.** Ga perlu definisi fungsi yang panjang.

## 🏗️ Closures

> **Fungsi bisa "nangkep" variabel dari scope luar.** Ini namanya closure.

```
fungsi pembuat_pengali(n)
    kembali lalu(x) x * n
selesai

buat kali2 = pembuat_pengali(2)
buat kali5 = pembuat_pengali(5)

tulis kali2(10)    # 20
tulis kali5(10)    # 50
```

**`n` tetap "hidup"** meskipun `pembuat_pengali()` udah selesai dijalankan. Ini powerful banget buat bikin factory functions.

## 🔀 Higher-Order Functions

```
# Fungsi bisa dikirim sebagai parameter
fungsi jalankan(fungsi, nilai)
    kembali fungsi(nilai)
selesai

buat kuadrat = lalu(x) x ** 2
tulis jalankan(kuadrat, 5)    # 25
```

## 📋 List Comprehension

```
# Filter
buat genap = [x untuk x dalam range(10) jika x % 2 == 0]
tulis genap    # [0, 2, 4, 6, 8]

# Transform
buat kuadrat = [x ** 2 untuk x dalam range(5)]
tulis kuadrat    # [0, 1, 4, 9, 16]

# Dua kondisi
buat hasil = [x untuk x dalam range(20) jika x > 5 jika x % 2 == 0]
tulis hasil    # [6, 8, 10, 12, 14, 16, 18]
```

## 🏷️ Keyword Arguments

```
fungsi profil(nama, umur, kota)
    tulis "Nama: " + nama
    tulis "Umur: " + teks(umur)
    tulis "Kota: " + kota
selesai

profil(kota = "Bandung", nama = "Andi", umur = 17)
```

**Ga perlu urut.** Tinggal sebut namanya aja.

## 🏷️ Argument Labels

```
fungsi sapaorang(nama luar nama, usia luar umur)
    tulis "Halo " + nama + ", umur kamu " + teks(usia)
selesai

sapaorang(nama luar "Budi", usia luar 17)
```

**Parameter internal vs external.** Biar lebih readable.

## 🔄 Recursion

```
fungsi faktorial(n)
    jika n <= 1 maka
        kembali 1
    selesai
    kembali n * faktorial(n - 1)
selesai

tulis faktorial(5)    # 120
```

## 🧩 Variadic Functions (Kumpulin Semua Argumen)

```
fungsi jumlah_semua(...)
    buat total = 0
    untuk angka dalam args lakukan
        total = total + angka
    selesai
    kembali total
selesai

tulis jumlah_semua(1, 2, 3, 4, 5)    # 15
```

---

## 📖 Recap

| Fitur | Contoh |
|-------|--------|
| Fungsi biasa | `fungsi nama() ... selesai` |
| Return | `kembali nilai` |
| Default params | `fungsi f(a, b = 10)` |
| Lambda | `lalu(x) x * 2` |
| Closures | Fungsi nangkep variabel luar |
| List comprehension | `[x untuk x dalam list]` |
| Keyword args | `f(nama = "Budi")` |
| Argument labels | `f(nama luar "B")` |
| Variadic | `fungsi f(...)` |
| Recursion | Fungsi panggil diri sendiri |
