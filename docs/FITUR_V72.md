# Fitur Baru — BroLang v7.2

BroLang v7.2 fokus pada **menutup celah konsistensi lintas mesin** (fitur
yang berfungsi di interpreter & transpiler tapi rusak/no-op di VM) plus
**dua fitur sintaks baru** dan **perluasan library**.

Daftar isi:
1. [Fitur Sintaks Baru](#1-fitur-sintaks-baru)
2. [Konsistensi VM — Fitur yang Kini Berfungsi di Ketiga Mesin](#2-konsistensi-vm)
3. [Perluasan Library](#3-perluasan-library)
4. [Verifikasi](#4-verifikasi)

---

## 1. Fitur Sintaks Baru

### Null-Safe Indexing `arr?[0]`

Mirror dari `objek?.atribut` tapi untuk **indeks** — target `kosong`
menghasilkan `kosong` tanpa error, dan indeks di luar jangkauan juga aman.
Sangat cocok dipasangkan dengan `??`:

```bro
buat data = kosong
tulis data?[0] ?? "default"        # "default" (tidak crash)

buat daftar = [10, 20, 30]
tulis daftar?[1]                   # 20
tulis daftar?[99] ?? "kosong"      # "kosong" (di luar jangkauan)

buat obj = {"nama": "Budi"}
tulis obj?["nama"] ?? "anonim"     # "Budi"
```

### Set Comprehension `{expr lalu var dalam iterable}`

Seperti list comprehension tapi hasilnya **set** (nilai unik):

```bro
buat s = {x * 2 lalu x dalam [1, 2, 2, 3]}
tulis s                             # {2, 4, 6}

buat genap = {x lalu x dalam [1, 2, 3, 4, 5, 6] jika x % 2 == 0}
tulis genap                         # {2, 4, 6}
```

### Dict Comprehension `{k: v lalu var dalam iterable}`

Sintaks dict comprehension kini benar-benar bisa diparse (sebelumnya node
AST-nya ada tapi parser tidak pernah menghasilkannya):

```bro
buat d = {x: x * 2 lalu x dalam [1, 2, 3]}
tulis d                             # {1: 2, 2: 4, 3: 6}
```

---

## 2. Konsistensi VM

Empat fitur berikut **sudah bekerja di interpreter & transpiler** sejak
lama, tapi **rusak / di-skip diam-diam di VM**. Kini berfungsi penuh di
ketiga mesin:

### Walrus `x := nilai`

```bro
buat hasil = (x := 10) + 5
tulis hasil      # 15
tulis x          # 10 — x ikut ter-set
```

### List Comprehension

```bro
buat r = [x * 2 lalu x dalam [1, 2, 3]]
tulis r                  # [2, 4, 6]
buat genap = [x lalu x dalam [1, 2, 3, 4, 5, 6] jika x % 2 == 0]
tulis genap              # [2, 4, 6]
```

### Generator `hasilkan` / `hasilkandari`

```bro
fungsi gen()
    hasilkan 1
    hasilkan 2
selesai
buat g = gen()
untuk setiap item dalam g lakukan
    tulis item           # 1, 2
selesai

fungsi seri()
    hasilkandari [3, 4]  # yield from
    hasilkan 5
selesai
```

### `dengan` (with statement)

Context manager `dengan ekspresi sebagai nama ... selesai` — memanggil
`__enter__`/`masuk` saat masuk dan `__exit__`/`keluar` saat keluar
(termasuk saat body melempar exception):

```bro
kelas Koneksi
    fungsi masuk(self)
        tulis "terhubung"
    selesai
    fungsi keluar(self)
        tulis "terputus"
    selesai
selesai

dengan Koneksi() sebagai k
    tulis "bekerja..."
selesai
# terhubung → bekerja... → terputus
```

> Perbaikan juga: `dengan` kini mengenali method `masuk`/`keluar` pada
> instance kelas BroLang di interpreter (sebelumnya `hasattr` gagal karena
> method BroLang tidak ter-expose sebagai atribut Python).

---

## 3. Perluasan Library

| Modul | Fungsi baru |
|-------|-------------|
| `waktu` | `waktu_iso()`, `timestamp()`, `milidetik()`, `zona_waktu()`, `dari_timestamp(ts)`, `hari_ini()`, `tambah_hari(tgl, n)`, `umur(tgl_lahir)`, `selisih_waktu(a, b)`, `detik_sejak(epoch)` |
| `file` | `baca_biner()`, `tulis_biner()`, `salin_biner()`, `ubah_nama()`, `ubah_waktu()`, `gabung_jalur()`, `absolute()`, `nama_dasar()`, `folder()`, `ekstensi()` |
| `dasar` | `unik()`, `terbalik()`, `urutkan()`, `kunci()`, `nilai()`, `item()` |
| `acak` | `pilih()`, `pilih_beberapa()`, `kocok()`, `unik()`, `kata()`, `huruf()`, `huruf_besar()`, `antara()`, `koin()`, `dadu()` |

Contoh:

```bro
impor waktu
tulis waktu.hari_ini()          # 2026-08-13
tulis waktu.timestamp()         # detik Unix
tulis waktu.tambah_hari("2026-01-01", 10)   # 2026-01-11

impor dasar
tulis dasar.unik([1, 2, 2, 3])  # [1, 2, 3]
tulis dasar.terbalik("abc")     # cba

impor acak
buat koin = acak.koin()         # "kepala" / "ekor"
buat lemparan = acak.dadu()     # 1..6
```

---

## 4. Verifikasi

- **1205 test passing** (32 test baru di `tests/unit/test_v72_language.py`)
- **Audit konsistensi lintas mesin** (`tools/audit_konsistensi.py`): 73 snippet
  fitur diuji di interpreter/transpiler/VM → **72 konsisten**. Bug yang
  diperbaiki: slicing string & list, method list/dict/str di VM & transpiler,
  closure di VM, unpack multiple return, index assignment dict, urutan
  kunci dict di VM.
- Semua fitur baru diuji konsisten di **interpreter, transpiler, dan VM**
- Contoh: `examples/fitur_v72.bro`
