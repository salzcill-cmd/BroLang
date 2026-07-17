# ⚡ Quick Start

> **Baru pertama kali pake BroLang?** Mulai dari sini ya bos.

## 🎯 Hello World

Buat file `halo.bro`:

```
tulis "Halo Dunia!"
```

Terus jalankan:

```bash
bro halo.bro
```

Output:

```
Halo Dunia!
```

Gampang kan? 😎

## 📝 Variabel

```
buat nama = "Budi"
buat umur = 17

tulis "Nama: " + nama
tulis "Umur: " + teks(umur)
```

## 🔢 Operasi Matematika

```
tulis 10 + 5      # 15
tulis 10 - 5      # 5
tulis 10 * 5      # 50
tulis 10 / 3      # 3.333...
tulis 10 % 3      # 1
tulis 10 ** 2     # 100
```

## 📋 List

```
buat angka = [1, 2, 3, 4, 5]
tulis angka[0]    # 1
tulis angka[-1]   # 5
tulis jumlah(angka)  # 5
```

## 🔄 Perulangan

```
untuk i dalam range(5) lakukan
    tulis i
selesai
```

## ❓ Percabangan

```
buat nilai = 85

jika nilai >= 90 maka
    tulis "Grade A"
lainnya jika nilai >= 80 maka
    tulis "Grade B"
lainnya
    tulis "Grade C"
selesai
```

## 🔧 Fungsi

```
fungsi sapa(nama)
    kembali "Halo, " + nama + "!"
selesai

tulis sapa("Budi")  # Halo, Budi!
```

## 🚀 Next Step

Mau tau lebih lanjut? Baca:

- [Dasar Bahasa](DASAR.md) - Tipe data, variabel, operator
- [Fitur Lengkap](FITUR.md) - Semua fitur BroLang
- [Game Development](GAME.md) - Bikin game pake BroLang
