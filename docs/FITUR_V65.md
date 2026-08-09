# Fitur Bahasa Baru — BroLang v6.5

BroLang v6.5 fokus pada **fitur bahasa** yang membuat kode lebih aman,
lebih ringkas, dan lebih ramah pemula. Semua fitur berjalan konsisten di
**interpreter**, **transpiler** (`bro run`), dan **compiler** (`bro build`).

Daftar isi:
1. [Konstanta — variabel immutable](#1-konstanta--variabel-immutable)
2. [ulangi ... sampai — do-until loop](#2-ulangi--sampai--do-until-loop)
3. [untuk i dari A sampai B — range for loop](#3-untuk-i-dari-a-sampai-b--range-for-loop)

---

## 1. Konstanta — variabel immutable

Deklarasikan nilai yang **tidak bisa diubah** setelah ditetapkan:

```bro
konstanta PI = 3.14
konstanta NAMA = "BroLang"
konstanta MAKS_PERCUBAAN: Angka = 3   # bisa pakai anotasi tipe (v6.0)
```

Setelah dideklarasikan, semua bentuk penulisan ulang akan ditolak:

```bro
PI = 3.15    # ✗ error: Konstanta 'PI' tidak bisa diubah
PI += 1      # ✗ error (augmented assignment juga ditolak)
```

**Penegakan dua lapis** (konsisten dengan type system v6.0):

| Lapisan | Kapan | Hasil |
|---------|-------|-------|
| SemanticAnalyzer | `bro run` / `bro build` | error statis sebelum eksekusi |
| Interpreter | REPL / `Interpreter().interpret()` | error runtime |

Gunakan `konstanta` untuk nilai tetap seperti rumus, konfigurasi, atau
nilai yang harus konsisten sepanjang program. Untuk nilai yang berubah,
tetap pakai `buat`:

```bro
buat skor = 0          # boleh diubah
skor += 10             # ok
```

---

## 2. ulangi ... sampai — do-until loop

Loop yang **menjalankan body minimal satu kali**, lalu memeriksa kondisi
di akhir. Berhenti saat kondisi bernilai `benar`:

```bro
buat tebakan = 0
ulangi
    tebakan = tebakan + 1
    tulis "Percobaan ke-" + teks(tebakan)
sampai tebakan >= 3
```

Beda dengan `selama` (while): di `selama`, kondisi dicek **sebelum**
body — kalau sudah salah dari awal, body tidak pernah jalan. Di
`ulangi ... sampai`, body **pasti jalan sekali**:

```bro
# Selama: body tidak pernah jalan
buat x = 5
selama x < 3 lakukan
    tulis x            # tidak pernah tercetak
selesai

# Ulangi: body jalan minimal sekali
buat y = 5
ulangi
    tulis y            # tercetak: 5
sampai y < 3
```

Kontrol loop biasa tetap berlaku:

```bro
buat i = 0
ulangi
    i = i + 1
    jika i == 2 maka
        hentikan       # 'hentikan' (break)
    selesai
    lanjutkan          # 'lanjutkan' (continue) juga didukung
sampai i >= 10
```

Bisa bersarang dengan loop lain:

```bro
buat i = 0
ulangi
    i = i + 1
    untuk j dari 1 sampai 2 lakukan
        tulis i * j
    selesai
sampai i >= 2
```

---

## 3. untuk i dari A sampai B — range for loop

Iterasi angka dari `A` sampai `B` — **inklusif** (nilai akhir ikut):

```bro
untuk i dari 1 sampai 5 lakukan
    tulis i
selesai
# Output: 1 2 3 4 5
```

### Langkah otomatis

- `A <= B` → naik otomatis (langkah 1)
- `A > B` → turun otomatis (langkah -1)

```bro
untuk i dari 3 sampai 1 lakukan
    tulis i
selesai
# Output: 3 2 1
```

### Langkah eksplisit (`langkah`)

```bro
untuk i dari 0 sampai 20 langkah 5 lakukan
    tulis i
selesai
# Output: 0 5 10 15 20

untuk i dari 10 sampai 2 langkah -2 lakukan
    tulis i
selesai
# Output: 10 8 6 4 2
```

### Else clause

Seperti `untuk`/`selama`, blok `lainnya` dieksekusi saat loop selesai
normal (tanpa `hentikan`):

```bro
untuk i dari 1 sampai 3 lakukan
    tulis i
lainnya
    tulis "loop selesai normal"
selesai
```

### Ekspresi sebagai batas

Batas boleh berupa ekspresi apa pun (variabel, aritmatika, hasil fungsi):

```bro
buat n = 5
untuk i dari n sampai n + 3 lakukan
    tulis i
selesai
# Output: 5 6 7 8
```

### Catatan implementasi

- `sampai` inklusif: rentang dikonversi ke `range(start, end + (1 if step > 0 else -1), step)`.
- `langkah` adalah **soft keyword** — hanya dikenali dalam konteks
  `untuk i dari A sampai B langkah S`. Program lama yang memakai
  `langkah` sebagai nama variabel/kelas tetap berjalan.
- Ekspresi start/end/step dievaluasi **sekali** (konsisten interpreter ↔ transpiler).
- `langkah 0` → error ramah ("Langkah range tidak boleh nol").

---

## Ringkasan sintaks

```bro
# 1. Konstanta
konstanta NAMA = nilai
konstanta NAMA: Tipe = nilai

# 2. do-until
ulangi
    ...
sampai kondisi

# 3. Range for
untuk VAR dari AWAL sampai AKHIR lakukan
    ...
selesai

untuk VAR dari AWAL sampai AKHIR langkah LANGKAH lakukan
    ...
selesai
```

Contoh lengkap: [`examples/fitur_bahasa.bro`](../examples/fitur_bahasa.bro)
