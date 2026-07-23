# Quick Start

> **Baru pertama kali pake BroLang?** Mulai dari sini ya bos.

## Hello World

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

Gampang kan?

## Variabel

```
buat nama = "Budi"
buat umur = 17

tulis "Nama: " + nama
tulis "Umur: " + teks(umur)
```

## Operasi Matematika

```
tulis 10 + 5      # 15
tulis 10 - 5      # 5
tulis 10 * 5      # 50
tulis 10 / 3      # 3.333...
tulis 10 % 3      # 1
tulis 10 ** 2     # 100
```

## List

```
buat angka = [1, 2, 3, 4, 5]
tulis angka[0]    # 1
tulis angka[-1]   # 5
tulis jumlah(angka)  # 5
```

## Perulangan

```
untuk i dalam range(5) lakukan
    tulis i
selesai
```

## Percabangan

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

## Fungsi

```
fungsi sapa(nama)
    kembali "Halo, " + nama + "!"
selesai

tulis sapa("Budi")  # Halo, Budi!
```

## Null Coalescing (v5.0)

Kalo nilainya kosong, otomatis pake default:

```
buat nama = kosong
tulis nama ?? "Anonim"    # Anonim
```

## Higher-Order Functions (v5.0)

`peta` buat ubah tiap elemen, `saring` buat ambil yang cocok:

```
buat angka = [1, 2, 3, 4, 5]
tulis peta(angka, lalu(x) x * 2)    # [2, 4, 6, 8, 10]
tulis saring(angka, lalu(x) x > 3)  # [4, 5]
```

## Result Type (v5.0)

Handle error dengan rapi:

```
fungsi bagi(a, b)
    jika b == 0 maka
        kembali Salah("bagi dengan nol!")
    selesai
    kembali Benar(a / b)
selesai

tulis bagi(10, 2)    # 5.0
tulis bagi(10, 0)    # bagi dengan nol!
```

## Next Step

Mau tau lebih lanjut? Baca:

- [Dasar Bahasa](DASAR.md) — Tipe data, variabel, operator
- [Fitur Lengkap](FITUR.md) — Semua fitur BroLang
- [Fungsi](FUNGSI.md) — Fungsi, lambda, closures
- [Game Development](GAME.md) — Bikin game pake BroLang
