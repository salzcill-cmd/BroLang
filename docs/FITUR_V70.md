# Fitur Baru — BroLang v7.0

BroLang v7.0 membawa **fitur bahasa modern**, **async/await sejati**, dan
perbaikan besar pada **VM bytecode**. Versi ini menandai lompatan ke
7.x dengan tiga pilar:

1. **Multiple assignment** — deklarasi & reassignment berpasangan, swap aman
2. **Switch expression** — `cocokkan` kini bisa menghasilkan nilai
3. **Error propagation `?`** — buka Result/Option tanpa boilerplate
4. **Async/Await sejati** — `asinkron fungsi` berjalan di background thread,
   `tunggu` memblokir sampai selesai, modul stdlib baru `event_loop`
5. **Perbaikan VM** — try/catch benar-benar bekerja, `coba/kecuali` ber-tipe,
   `Kosong()` (Option) bisa diparse

Daftar isi:
1. [Multiple Assignment](#1-multiple-assignment)
2. [Switch Expression](#2-switch-expression)
3. [Error Propagation `?`](#3-error-propagation-)
4. [Async/Await Sejati](#4-asyncawait-sejati)
5. [Modul `event_loop`](#5-modul-event_loop)
6. [Perbaikan VM](#6-perbaikan-vm)

---

## 1. Multiple Assignment

Deklarasi dan reassignment berpasangan dalam satu baris:

```bro
buat a, b = 1, 2        # deklarasi ganda → a=1, b=2
buat x, y, z = 1, 2, 3

a, b = b, a             # swap — nilai kanan dievaluasi DULU, jadi aman
```

Bisa dipakai di dalam fungsi:

```bro
fungsi tukar(p, q)
    p, q = q, p
    kembali p, q
selesai
```

Aturan:

- **Semua nilai kanan dievaluasi sebelum assignment** — swap `a, b = b, a`
  dan ekspresi yang memakai target (`a, b = b, a + b`) selalu aman.
- **Nilai kanan yang kurang** mengisi target tersisa dengan `kosong`.
- **`konstanta` menolak multiple assignment** — deklarasikan satu per baris.
- Konsisten di interpreter, transpiler, dan VM.

---

## 2. Switch Expression

Statement `cocokkan` (v2.0) kini bisa menjadi **ekspresi bernilai**:
setiap body case adalah satu ekspresi yang menjadi hasil switch.

```bro
buat status = cocokkan kode {
    1: "satu",
    2: "dua",
    _: "lainnya"          # default
}

# Tanpa default → kosong jika tidak ada yang cocok
buat x = cocokkan 5 { 1: "satu" }   # x = kosong
```

Mendukung pola yang sama dengan statement `cocokkan` — literal, binding
objek, dan wildcard:

```bro
buat data = { "x": 10, "y": 20 }
buat hasil = cocokkan data {
    { "x": a, "y": b }: a + b,      # binding → 30
    _: 0
}
```

Bisa jadi argumen fungsi atau nilai `kembali`:

```bro
fungsi label(k)
    kembali cocokkan k { 1: "satu", _: "lainnya" }
selesai
```

---

## 3. Error Propagation `?`

Operator `?` membuka (unwrap) nilai **Result** (`Benar`/`Salah`) dan
**Option** (`Ada`/`Kosong`) tanpa boilerplate:

```bro
fungsi cari(id)
    kembali Benar("ditemukan") jika id == 1
    kembali Salah("tidak ada")
selesai

buat hasil = cari(1)?     # Benar(v)  -> v
# Salah(e)?  -> lempar e (atau RuntimeError_ bila e bukan Exception)
# Ada(v)?    -> v
# Kosong()?  -> lempar error
```

Aturan:

- `Benar(v)?` → `v` | `Salah(e)?` → lempar `e`
- `Ada(v)?` → `v` | `Kosong()?` → lempar error
- Nilai biasa (bukan Result/Option) diteruskan apa adanya (no-op):
  `7?` → `7`
- Bisa dirantai pada pemanggilan fungsi: `cari(1)?`
- Konsisten di interpreter, transpiler, dan VM.

---

## 4. Async/Await Sejati

Sebelum v7.0, `asinkron fungsi` hanya alias untuk fungsi biasa (sinkron).
Kini pemanggilan fungsi asinkron mengembalikan objek **`Tugas`** yang
berjalan di **background thread (daemon)**, dan `tunggu` memblokir sampai
selesai:

```bro
asinkron fungsi muat(url)
    event_loop.tidur(0.1)              # IO simulasi — tidak memblokir task lain
    kembali "data dari " + url
selesai

buat a = muat("api/1")                 # tidak memblokir
buat b = muat("api/2")
buat hasil = tunggu a                  # blokir sampai a selesai
```

Cara kerja di balik layar:

- Body task di-serialisasi dengan lock (interpreter tidak thread-safe) dan
  berjalan di **sub-interpreter terpisah** — program utama tidak terganggu.
- `tunggu`/`tidur` di dalam body async melepas lock sambil menunggu agar
  task lain bisa maju — **task dalam task tidak deadlock**.

API objek `Tugas`:

| Method | Arti |
|--------|------|
| `selesai()` | True jika sudah selesai (tanpa memblokir) |
| `hasil(timeout=None)` | blokir sampai selesai, kembalikan hasil |
| `tunggu(timeout=None)` | alias `hasil()` |
| `batal()` | task sudah berjalan; selalu `salah` |

Error di dalam task dilempar saat `tunggu`/`hasil()`:

```bro
asinkron fungsi gagal()
    lempar "boom"
selesai

coba
    buat t = gagal()
    buat r = tunggu t        # melempar "boom"
tangkap e
    tulis "tertangkap"       # tercetak
selesai
```

---

## 5. Modul `event_loop`

Modul stdlib baru untuk bekerja dengan banyak tugas:

```bro
impor event_loop
```

| Fungsi | Arti |
|--------|------|
| `tidur(detik)` | Tidur kooperatif — di dalam async, task lain maju saat tidur |
| `tunggu_semua([...])` | Blokir sampai SEMUA tugas selesai → list hasil (urut) |
| `tunggu_apa_saja([...])` | Hasil tugas pertama yang selesai; sisanya tetap jalan |
| `jalankan(fn, ...)` | Jadwalkan fungsi biasa sebagai Tugas (delegasi ke `sejajar`) |
| `Tugas` | Kelas Tugas (sama dengan hasil `asinkron fungsi`) |

Contoh: tiga task tidur 0.15 detik yang tumpang tindih selesai dalam
< 0.45 detik:

```bro
asinkron fungsi kerja(n)
    event_loop.tidur(0.15)
    kembali n * 10
selesai

buat a = kerja(1)
buat b = kerja(2)
buat c = kerja(3)
tulis event_loop.tunggu_semua([a, b, c])   # [10, 20, 30] — cepat, overlap!
```

---

## 6. Perbaikan VM

Bug dan celah pre-existing yang diperbaiki di bytecode VM:

- **try/catch benar-benar bekerja** — sebelumnya `TRY_PUSH` hanya menaruh
  marker di stack tanpa pernah dipakai; exception menerobos keluar dan
  mematikan program. Kini `_execute` melakukan *exception routing*: stack
  dipotong sampai handler teratas, nilai exception didorong untuk di-bind
  `catch_var`, eksekusi lanjut dari handler (mendukung handler bertingkat).
- **`coba/tangkap` & `coba/kecuali` dikompilasi di VM** — sebelumnya
  `MultiExceptNode` di-skip diam-diam. Klausa ber-tipe dicocokkan lewat
  nama tipe + subkelas; tidak cocok → re-raise.
- **`Kosong()` (Option) bisa diparse** — keyword `Kosong` terdaftar di
  lexer (sebelumnya `Ada(v)` berfungsi tapi `Kosong()` jatuh ke
  "fungsi tidak ditemukan").
- **`a, b = 1, 2` & `?` didukung VM** — store terbalik agar swap aman, dan
  helper `_vm_propagate` (aman untuk nilai primitif seperti `7?`).
- **`impor` di VM diperbaiki** — `_emit_import` memakai `.module` (bukan
  `.parts` yang tidak pernah ada), jadi `impor event_loop` dll. berfungsi.
- **switch expression didukung VM** — `cocokkan x { pola: ekspresi }`
  bernilai lewat helper `_vm_switch_match` + binding pola.
- **`asinkron fungsi` didukung VM** — body dieksekusi sinkron, hasil
  dibungkus objek `Tugas` (`selesai`/`hasil`/`tunggu`/`batal`) agar API
  konsisten lintas mesin.
- **Perbaikan lain**: escape string di transpiler (`\n`/`\t`/`\r` kini
  ditulis ulang dengan benar), pemanggilan fungsi pada modul stdlib di VM
  (objek `SimpleNamespace`) tidak lagi mengoper `obj` berlebih.
- **Pola enum di `cocokkan` (bug lama)** — `Warna.MERAH` dulu gagal parse;
  kini diparse sebagai ekspresi member access, termasuk guard
  (`Warna.HIJAU jika c`), di interpreter, transpiler, dan VM.
- **Statement `cocokkan` didukung VM** — pola terstruktur (dict binding),
  literal/ekspresi, guard, dan default. `enum` & `struktur` di VM juga
  diperbaiki (`__init__` otomatis + `__repr__`).

---

## Verifikasi

```bro
bro run examples/fitur_v70.bro        # Interpreter
bro benchmark examples/fitur_v70.bro  # Ketiga mesin: interpreter, transpiler, VM
```

Catatan mesin:

- **Interpreter**: async/await sejati (background thread + lock kooperatif).
- **Transpiler**: `asinkron fungsi` dikompilasi ke tugas background thread
  (helper `_brolang_async_run`) — hasil, `selesai()`, `tunggu`, dan
  `event_loop` konsisten dengan interpreter.
- **VM bytecode**: body fungsi asinkron dieksekusi sinkron dan hasilnya
  dibungkus objek `Tugas` yang sudah selesai (`selesai() -> benar`),
  `tunggu` membuka hasilnya — API sama, perilaku sinkron (VM tidak punya
  event loop).

60 test baru (`tests/unit/test_v70_language.py`) — total **1075 test passing**.
