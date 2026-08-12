# Fitur Baru — BroLang v6.9

BroLang v6.9 memperluas **guard clause** (v6.8) ke *semua* statement
sederhana. Sebelumnya hanya `kembali`, `hentikan`, dan `lanjutkan` yang
bisa diberi kondisi `jika c`; kini `tulis`, assignment, `lempar`, `hapus`,
pemanggilan fungsi, dan `hasilkan` juga bisa — statement hanya dijalankan
**saat kondisi benar**.

```bro
tulis x jika x > 0          # hanya mencetak saat x > 0
skor += 10 jika menang       # hanya menambah skor saat menang
lempar "error" jika kosong   # hanya melempar saat kosong
```

Daftar isi:
1. [Statement yang didukung](#1-statement-yang-didukung)
2. [Tidak ambigu dengan ternary](#2-tidak-ambigu-dengan-ternary)
3. [Nilai tidak dievaluasi saat guard salah](#3-nilai-tidak-dievaluasi-saat-guard-salah)
4. [Konsisten di semua mesin](#4-konsisten-di-semua-mesin)

---

## 1. Statement yang didukung

Guard clause bekerja pada statement sederhana berikut:

| Statement | Contoh | Arti |
|-----------|--------|------|
| `tulis` | `tulis x jika x > 5` | cetak hanya saat kondisi benar |
| `buat` | `buat x = hitung() jika c` | deklarasi hanya saat kondisi benar |
| Reassignment | `x = 99 jika c` | ubah nilai hanya saat kondisi benar |
| Augmented | `x += 5 jika c` | `x += 5` hanya saat kondisi benar |
| Atribut objek | `self.total += n jika n > 0` | update atribut bersyarat |
| Index list | `data[i] += 10 jika c` | update index bersyarat |
| Destructuring | `buat [a, b] = pasangan() jika c` | unpack bersyarat |
| `lempar` | `lempar e jika c` | lempar error bersyarat |
| `hapus` | `hapus cache jika basi` | hapus bersyarat |
| Panggilan fungsi | `log(pesan) jika debug` | panggil bersyarat |
| `hasilkan` | `hasilkan v jika v > 0` | yield bersyarat (generator) |

Contoh lengkap:

```bro
# Log bersyarat — hilangkan boilerplate if
log("request masuk") jika mode_debug

# Update atribut ber-guard di dalam method
kelas Akun
    fungsi __init__(self)
        self.bonus = 0
    selesai
    fungsi beri_bonus(self, n)
        self.bonus += n jika n > 0     # abaikan nilai negatif
        kembali self.bonus
    selesai
selesai

# Index list bersyarat
buat data = [1, 2, 3]
data[1] += 10 jika benar

# Lempar error bersyarat
lempar "stok habis" jika stok <= 0

# Yield bersyarat di generator
fungsi gen()
    hasilkan 1
    hasilkan 2 jika benar
selesai
```

Guard juga bekerja di dalam loop, blok `jika`, dan single-line block:

```bro
untuk i dari 1 sampai 5 lakukan
    tulis i jika i % 2 == 1       # 1 3 5
selesai

jika x > 0 maka tulis "positif" jika x > 10 selesai
```

---

## 2. Tidak ambigu dengan ternary

Sama seperti v6.8, `a jika b lainnya c` tetap **ternary** (butuh
`lainnya`), sedangkan `a jika b` di akhir statement adalah **guard**.
Parser membedakannya otomatis:

```bro
buat a = 5 jika benar lainnya 99    # ternary → a = 5
buat b = 5 jika salah lainnya 99    # ternary → b = 99

tulis x jika x > 5                  # guard → tulis hanya saat x > 5
tulis x jika x > 5 lainnya -1       # ternary → tulis (x > 5 ? x : -1)
```

Ternari di dalam tanda kurung/panggilan fungsi juga tetap berfungsi:

```bro
tulis f(1 jika benar lainnya 2)     # f(1)
```

---

## 3. Nilai tidak dievaluasi saat guard salah

Saat kondisi guard salah, nilai statement **tidak dievaluasi sama sekali**
— side-effect tidak terjadi. Konsisten di interpreter, transpiler, dan VM:

```bro
buat dipanggil = 0
fungsi hitung(x)
    dipanggil = dipanggil + 1
    kembali x
selesai

tulis hitung(5) jika salah      # hitung tidak pernah dipanggil
tulis dipanggil                  # 0
```

---

## 4. Konsisten di semua mesin

Guard statement direpresentasikan sebagai statement `jika` biasa
(`jika c maka <statement> selesai`) di level AST, sehingga **interpreter**,
**transpiler** (`bro run`), **VM bytecode** (`bro build`), dan optimizer
langsung mendukungnya tanpa perubahan khusus. Verifikasi:

```bro
# Interpreter  : bro contoh.bro
# Transpiler   : bro benchmark contoh.bro
# VM bytecode  : bro benchmark --vm contoh.bro
```

> Catatan: konsisten dengan blok `jika` biasa, deklarasi `buat x = ...`
> yang di-guard bersifat block-scoped — variabel baru tidak terlihat
> setelah statement guard. Gunakan reassignment (`x = ...`) bila ingin
> mengubah variabel yang sudah ada dari luar blok.

---

## Ringkasan sintaks

```bro
# Statement apa pun + jika kondisi
tulis x jika kondisi
buat y = hitung() jika kondisi
x = 99 jika kondisi
x += 5 jika kondisi
self.total += n jika n > 0
data[i] += 10 jika kondisi
lempar "error" jika kondisi
hapus cache jika basi
log(pesan) jika debug
hasilkan v jika kondisi

# Ternary tidak berubah
buat a = 1 jika benar lainnya 2
```
