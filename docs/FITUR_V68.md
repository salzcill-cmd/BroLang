# Fitur Baru — BroLang v6.8

BroLang v6.8 menghadirkan **fitur bahasa** (guard clause, floor division,
augmented assignment pada atribut & index), **perbaikan bytecode VM**
(`%=`/`**=` yang tadinya diam-diam rusak, loop dengan guard break), dan
**fitur game dev** (generator BGM prosedural tanpa file eksternal).

Daftar isi:
1. [Guard clause `kembali x jika c`](#1-guard-clause-kembali-x-jika-c)
2. [Floor division `//`](#2-floor-division-)
3. [Augmented assignment pada atribut & index](#3-augmented-assignment-pada-atribut--index)
4. [Perbaikan VM](#4-perbaikan-vm)
5. [Game dev: BGM prosedural](#5-game-dev-bgm-prosedural)

---

## 1. Guard clause `kembali x jika c`

Statement `kembali`, `hentikan`, dan `lanjutkan` kini bisa diberi
kondisi — statement hanya dijalankan **saat kondisi benar**. Ini
membuat early return / early exit jauh lebih ringkas:

```bro
fungsi cek(x)
    kembali "negatif" jika x < 0
    kembali "nol" jika x == 0
    kembali "positif"
selesai

tulis cek(-5), cek(0), cek(7)    # negatif nol positif
```

Guard tanpa nilai juga didukung (`kembali jika x`), dan bekerja di
dalam loop:

```bro
fungsi cari(daftar, target)
    untuk setiap nilai dalam daftar lakukan
        kembali nilai jika nilai == target
    selesai
    kembali -1
selesai

# hentikan / lanjutkan bersyarat
untuk i dari 1 sampai 10 lakukan
    lanjutkan jika i % 2 == 0     # skip angka genap
    hentikan jika i > 5           # berhenti lebih awal
    tulis i                       # 1 3 5
selesai
```

### Tidak ambigu dengan ternary

`kembali a jika b lainnya c` tetap **ternary** (butuh `lainnya`),
sedangkan `kembali a jika b` adalah **guard clause** — parser
membedakannya otomatis:

```bro
fungsi f(x)
    kembali x jika x > 0 lainnya 0   # ternary
selesai
```

---

## 2. Floor division `//`

Pembagian yang membulatkan hasil ke bawah (floor), konsisten dengan
semantik Python:

```bro
tulis 17 // 5      # 3      (17 / 5 = 3.4 → dibulatkan ke bawah)
tulis -17 // 5     # -4     (bukan -3! floor selalu ke bawah)
tulis 17.5 // 5    # 3.0
tulis 2 + 17 // 5 * 2   # 8   (presedensi sama dengan * dan /)
```

Operator augmented `//=`:

```bro
buat skor = 10
skor //= 3
tulis skor          # 3
```

Bekerja di **interpreter**, **transpiler**, **VM bytecode**, dan
compiler `bro build`. Optimizer juga melakukan constant folding:
`20 // 3` langsung menjadi `6`.

---

## 3. Augmented assignment pada atribut & index

Sebelum v6.8, `self.x += 1` ditolak interpreter ("target harus berupa
variabel") dan menimbun stack di VM. Kini augmented assignment
berfungsi penuh untuk **variabel, atribut objek, dan index list** di
ketiga mesin:

```bro
kelas Akun
    fungsi __init__(self)
        self.total = 0
    selesai
    fungsi naik(self, n)
        self.total += n        # atribut objek
        kembali self.total
    selesai
selesai

buat ak = Akun()
tulis ak.naik(5)               # 5

buat data = [1, 2, 3]
data[1] += 10                  # index list
tulis data                     # [1, 12, 3]

buat skor = [0, 0, 0]
untuk i dari 0 sampai 2 lakukan
    skor[i] += 10              # augmented di dalam loop
selesai
tulis skor                     # [10, 10, 10]
```

Semua operator didukung: `+=`, `-=`, `*=`, `/=`, `//=`, `%=`, `**=`.

---

## 4. Perbaikan VM

### `%=` dan `**=` kini benar di bytecode VM

Compiler VM tidak memiliki opcode untuk `%=` dan `**=`, sehingga
`x %= 3` dieksekusi sebagai `x = 3` (nilai kanan disalin, operasi
dilewati). Kedua opcode baru (`AUG_MOD`, `AUG_POW`) ditambahkan:

```bro
buat x = 7
x %= 3
tulis x              # 1 (sebelumnya: 3!)
```

### Loop tidak lagi memotong body setelah `hentikan`

Compiler loop VM berhenti mengkompilasi body setelah menemukan
`hentikan` — akibatnya statement setelah `hentikan jika x` tidak pernah
jalan saat kondisi salah. Kelima loop (while/do-until/for/range-for/
for-each) kini mengumpulkan semua marker break dan mem-patch-nya di
akhir loop:

```bro
buat hasil = []
untuk i dari 1 sampai 4 lakukan
    hentikan jika i > 10        # selalu salah — body harus tetap jalan
    hasil = hasil + [i]
selesai
tulis hasil          # [1, 2, 3, 4]
```

---

## 5. Game dev: BGM prosedural

Modul `audio` kini bisa membuat **musik latar** langsung dari pola nada
— tanpa file eksternal:

```bro
impor audio

# Pola memakai nama not: "C4", "A#3", "Bb2" (oktaf 0-8)
buat bgm = audio.buat_bgm(["C4", "E4", "G4", 0, "A4", "G4", "E4", 0])
audio.simpan_wav(bgm, "bgm.wav")

# Atau putar langsung sebagai musik loop (butuh pygame)
audio.mainkan_bgm(audio.pola_arcade, 120)
audio.hentikan_bgm()
```

Pola fleksibel — setiap elemen bisa berupa:

| Bentuk | Contoh | Arti |
|--------|--------|------|
| Nama not | `"C4"`, `"A#3"`, `"Bb2"` | Nada dengan oktaf |
| Frekuensi | `440.0` | Nada langsung dalam Hz |
| Tuple | `("C4", 2)` | Nada dengan durasi 2 ketuk |
| Jeda | `0` | Diam selama 1 ketuk |

Pola siap pakai: `pola_arcade`, `pola_epik`, `pola_tenang`. Helper
`frekuensi_nada("C4")` mengonversi nama not → Hz untuk pola kustom.

---

## Ringkasan sintaks

```bro
# 1. Guard clause
kembali x jika kondisi
hentikan jika kondisi
lanjutkan jika kondisi

# 2. Floor division
buat a = 17 // 5      # 3
buat b = -17 // 5     # -4
x //= 3

# 3. Augmented pada atribut & index
self.total += n
data[i] += 10

# 4. BGM prosedural
buat bgm = audio.buat_bgm(audio.pola_arcade)
audio.mainkan_bgm(audio.pola_epik)
audio.hentikan_bgm()
```
