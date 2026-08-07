# Fitur BroLang v6.0

> **v6.0 bawa BroLang ke level "bahasa produksi":** type system lengkap, pattern matching modern, custom error class, error CLI profesional, 6 modul stdlib baru, dan package registry online. Semua fitur bekerja konsisten di interpreter **dan** transpiler, serta diverifikasi otomatis oleh analyzer.

## Daftar Isi

- [1. Type System Lengkap](#1-type-system-lengkap)
- [2. Pattern Matching Modern](#2-pattern-matching-modern)
- [3. Error Handling Profesional](#3-error-handling-profesional)
- [4. Ekosistem Stdlib Baru](#4-ekosistem-stdlib-baru)
- [5. Package Registry Online](#5-package-registry-online)
- [6. Error CLI Profesional](#6-error-cli-profesional)

---

## 1. Type System Lengkap

Anotasi tipe di variabel, parameter, dan return value — **diverifikasi otomatis**. Mismatch tipe ditolak di **dua lapis**: analyzer statis (sebelum program jalan, jadi `bro run` langsung menolak) dan interpreter (saat runtime).

### Anotasi Variabel

```bro
buat umur: Angka = 25
buat nama: Teks = "Budi"
buat aktif: Boolean = benar
buat tinggi: Desimal = 170.5
buat daftar: Daftar<Angka> = [1, 2, 3]
```

```bro
buat umur: Angka = "salah"
# Error: Tipe tidak cocok untuk 'umur': diharapkan Angka, tapi mendapat teks.
```

### Anotasi Parameter & Return

```bro
fungsi kali2(a: Angka) -> Angka
    kembali a * 2
selesai

tulis kali2(21)    # 42
```

```bro
fungsi sapa(nama: Teks) -> Teks
    kembali "Halo " + nama
selesai

sapa(42)
# Error: Parameter 'nama' diharapkan Teks, tapi mendapat angka.
```

### Tipe Bawaan

| Anotasi | Tipe runtime | Keterangan |
|---------|--------------|------------|
| `Angka` | angka / desimal | integer & float |
| `Desimal` | desimal | float |
| `Teks` / `String` | teks | string |
| `Boolean` | boolean | `benar` / `salah` |
| `Daftar` / `List` / `Array` | list | list |
| `Objek` / `Dict` / `Map` | objek | dictionary |
| `Tupel` / `Tuple` | tuple | tuple |
| `Set` | set | set |
| `Kosong` / `Null` | kosong | null |
| `ApaSaja` / `Any` | apapun | wildcard |

### Union Type

Satu parameter bisa menerima beberapa tipe:

```bro
fungsi cetak(nilai: Angka | Teks)
    tulis nilai
selesai

cetak(5)        # 5
cetak("lima")   # lima
```

### Generik

```bro
buat angka2: Daftar<Angka> = [1, 2, 3]
tulis angka2[0] + angka2[2]    # 4
```

Elemen yang tidak cocok dengan tipe dalam `<>` ditolak saat runtime.

### Type Alias

```bro
tipe ID = Angka
tipe Nama = Teks

buat kode: ID = 12345
buat nama: Nama = "Budi"
```

### Kelas sebagai Tipe

Kelas user bisa dipakai sebagai anotasi parameter (termasuk turunannya):

```bro
kelas Mobil
    fungsi __init__(merk)
        self.merk = merk
    selesai
selesai

fungsi info(m: Mobil) -> Teks
    kembali m.merk
selesai

buat mobil = Mobil("Toyota")
tulis info(mobil)    # Toyota
```

### Catatan

- Anotasi bersifat *validasi* (bukan deklarasi kaku) — nilai default parameter juga dicek cocok dengan anotasinya.
- `kembali kosong` / `kembali` (tanpa nilai) diizinkan pada fungsi ber-tipe apa pun — pola "tidak ditemukan → return null" tetap valid.
- Transpiler menghasilkan Python setara; konsistensi output interpreter vs transpiler dijamin test suite.

---

## 2. Pattern Matching Modern

`cocokkan` kini punya pola destructuring — membongkar list/objek langsung di polanya, plus binding dan guard.

### Pola List

```bro
buat data = [1, 2]
cocokkan data {
    [a, b]: tulis a + b     # 3 — bind elemen ke variabel
    _: tulis "lain"
}
```

### Pola Objek

```bro
buat orang = {"nama": "Ani", "umur": 20}
cocokkan orang {
    {"nama": n, "umur": u}: tulis "Nama: " + n + ", Umur: " + teks(u)
    _: tulis "siapa?"
}
```

Pola objek bisa mencocokkan literal kunci:

```bro
cocokkan orang {
    {"nama": "Ani"}: tulis "hai Ani"
    {"nama": "Budi"}: tulis "hai Budi"
    _: tulis "siapa?"
}
```

### Binding

Identifier sebagai pola = tangkap seluruh nilai:

```bro
buat angka = 42
cocokkan angka {
    n: tulis "nilai: " + teks(n)     # nilai: 42
}
```

### Guard

Tambahkan kondisi `jika` setelah pola:

```bro
buat skor = 15
cocokkan skor {
    x jika x > 10: tulis "tinggi"     # tinggi
    _: tulis "rendah"
}
```

### Perilaku Lama Tetap Jalan

```bro
buat nilai = 5
cocokkan nilai {
    1: tulis "satu"
    5: tulis "lima"
    _: tulis "lain"
}
```

### ⚠️ Breaking Change (dari v5.x)

Pola **identifier** di `cocokkan` kini menjadi **binding** — selalu cocok dan menangkap nilai (`n: ...`), bukan dibandingkan sebagai nilai (`nilai == n`) seperti di v5.x. Program lama yang memakai identifier sebagai pola perbandingan harus diganti dengan literal/ekspresi.

---

## 3. Error Handling Profesional

### Custom Error Class (`kelas_error`)

Definisikan error dengan field sendiri:

```bro
kelas_error SaldoTidakCukup extends Kesalahan
    fungsi __init__(pesan, saldo)
        self.pesan = pesan
        self.saldo = saldo
    selesai
selesai

coba
    lempar SaldoTidakCukup("Saldo tidak cukup", 5000)
kecuali SaldoTidakCukup sebagai e
    tulis "Tertangkap: " + e.pesan + ", saldo=" + teks(e.saldo)
selesai
```

Output: `Tertangkap: Saldo tidak cukup, saldo=5000`

### Hierarki Error

`kecuali Induk sebagai e` menangkap semua turunannya:

```bro
kelas_error ErrorValidasi extends Kesalahan
    fungsi __init__(pesan)
        self.pesan = pesan
    selesai
selesai

kelas_error ErrorNama extends ErrorValidasi
    fungsi __init__(pesan)
        self.pesan = pesan
    selesai
selesai

coba
    lempar ErrorNama("Nama kosong")
kecuali ErrorValidasi sebagai e
    tulis "Validasi: " + e.pesan     # Validasi: Nama kosong
selesai

coba
    lempar ErrorNama("Nama kosong")
kecuali Kesalahan sebagai e
    tulis "Base: " + e.pesan         # Base: Nama kosong
selesai
```

### Fallback `kecuali lainnya`

```bro
coba
    lempar ErrorX("boom")
kecuali ErrorLain sebagai e
    tulis "salah tipe"
kecuali lainnya sebagai e
    tulis "default: " + e.pesan      # default: boom
selesai
```

### `Kesalahan` — Kelas Dasar Bawaan

- Tersedia langsung (tanpa import) sebagai kelas dasar semua error kustom.
- `lempar Kesalahan("pesan")` juga valid.
- Error kustom yang tidak tertangkap akan mempropagasi seperti exception biasa.
- Konsisten di interpreter **dan** transpiler (`kelas_error` → `class Nama(Kesalahan)` di Python).

---

## 4. Ekosistem Stdlib Baru

Enam modul baru siap pakai — tinggal `impor`.

### `tanggal` — Tanggal & Waktu

```bro
impor tanggal

tulis tanggal.hari_ini()                   # 2026-08-07
tulis tanggal.sekarang()                   # 2026-08-07 14:30:00
tulis tanggal.parse("07/08/2026")          # 2026-08-07
tulis tanggal.parse("7 Agustus 2026")      # 2026-08-07
tulis tanggal.selisih_hari("2026-08-07", "2026-08-01")   # 6
tulis tanggal.tambah_hari("2026-08-07", 3)               # 2026-08-10
tulis tanggal.format("2026-08-07", "%d %B %Y")          # 07 August 2026 (strftime)

# Nama hari/bulan Indonesia: pakai komponen()
buat kom = tanggal.komponen("2026-08-07")
tulis kom["nama_bulan"]                    # Agustus
tulis kom["hari_dalam_minggu"]             # Jumat

tulis tanggal.umur("2000-01-15")           # umur dalam tahun
tulis tanggal.hari_besar("kemerdekaan")    # 2026-08-17
```

| Fungsi | Keterangan |
|--------|------------|
| `hari_ini()` | Tanggal hari ini (YYYY-MM-DD) |
| `sekarang()` | Tanggal & waktu sekarang |
| `parse(teks)` | Parse berbagai format → ISO (`07/08/2026`, `2026-08-07`, `7 Agustus 2026`) |
| `format(iso, pola)` | Format tanggal ISO ke pola strftime |
| `komponen(iso)` | Objek: `tahun`, `bulan`, `hari`, `nama_bulan`, `hari_dalam_minggu` |
| `tambah_hari(iso, n)` | Tambah/kurang n hari |
| `selisih_hari(a, b)` | Selisih hari (a − b) |
| `umur(tanggal_lahir)` | Umur dalam tahun |
| `hari_besar(nama)` | Hari besar nasional: `tahun_baru`, `kemerdekaan`, `kartini`, `pahlawan`, `pendidikan`, dst. |

### `catat` — Logging Profesional

```bro
impor catat

catat.info("Aplikasi dimulai")        # [2026-08-07 14:30:00] [INFO] Aplikasi dimulai
catat.peringatan("Memori menipis")
catat.error("Koneksi gagal")

catat.atur_level("debug")             # tampilkan level >= debug
catat.atur_file("app.log")            # log juga ke file
catat.bersihkan()                     # hapus file log
```

| Fungsi | Keterangan |
|--------|------------|
| `atur_level(level)` | `debug` / `info` / `peringatan` / `error` / `kritis` |
| `atur_file(path)` | Arahkan log juga ke file (`kosong` untuk matikan) |
| `debug(pesan)` / `info(pesan)` | Log level rendah |
| `peringatan(pesan)` / `error(pesan)` / `kritis(pesan)` | Log level tinggi |
| `bersihkan()` | Hapus file log |

### `lingkungan` — Environment Variables

```bro
impor lingkungan

lingkungan.set("NAMA_APP", "myapp")
tulis lingkungan.get("NAMA_APP", "default")   # myapp
tulis lingkungan.ada("NAMA_APP")              # True
lingkungan.hapus("NAMA_APP")

tulis lingkungan.sistem()         # Linux / Darwin / Windows
tulis lingkungan.prosesor()       # x86_64
tulis lingkungan.hostname()       # nama host
tulis lingkungan.cwd()            # direktori kerja
tulis lingkungan.jalur_home()     # /home/user
```

### `proses` — Jalankan Subprocess

```bro
impor proses

buat hasil = proses.jalankan("echo halo dari proses")
tulis hasil.keluaran    # halo dari proses
tulis hasil.kode        # 0
tulis hasil.sukses      # True

tulis proses.kode_keluar("ls /tidak/ada")   # 2
tulis proses.keluaran("echo hi")            # hi
buat r = proses.jalankan_di("pwd", "/tmp")  # jalankan di folder tertentu
```

Objek hasil: `keluaran` (stdout), `error` (stderr), `kode` (exit code), `sukses` (bool).

### `csv` — Baca/Tulis CSV

```bro
impor csv

buat data = [{"nama": "Budi", "umur": 20}, {"nama": "Ani", "umur": 25}]
csv.tulis("data.csv", data)          # header otomatis dari kunci pertama

buat dibaca = csv.baca("data.csv")   # list objek
tulis dibaca[0]["nama"]              # Budi
tulis dibaca[1]["umur"]              # 25

buat mentah = csv.baca_list("data.csv")   # list of list (tanpa header)
csv.tulis_baris("data.csv", ["Citra", 30])  # append satu baris
tulis csv.kolom("data.csv", "nama")         # ["Budi", "Ani", "Citra"]
```

| Fungsi | Keterangan |
|--------|------------|
| `baca(path, delimiter?)` | Baca CSV → list objek (baris pertama = header) |
| `baca_list(path, delimiter?)` | Baca CSV → list of list |
| `tulis(path, data, kolom?)` | Tulis list objek/list → file (kembalikan jumlah baris) |
| `tulis_baris(path, baris, delimiter?)` | Append satu baris |
| `kolom(path, nama, delimiter?)` | Ambil satu kolom → list nilai |

### `sejajar` — Threading (v5.5, lanjutan)

```bro
impor sejajar

fungsi hitung(x)
    kembali x * 2
selesai

buat t = sejajar.jalankan(hitung, 21)    # background thread
buat hasil = t.hasil()                    # 42 (blokir sampai selesai)

tulis sejajar.peta_sejajar(hitung, [1, 2, 3, 4])   # [2, 4, 6, 8]
```

---

## 5. Package Registry Online

Registry paket HTTP — publish & install paket antar mesin lewat jaringan.

### Jalankan Server Registry

Dari terminal (blocking):

```bash
bro pkg server 8000
# Registry BroLang berjalan di http://127.0.0.1:8000
```

Atau dari kode BroLang (blocking atau background thread):

```bro
impor registri
registri.jalankan(8000)                        # blocking, Ctrl+C untuk berhenti

buat srv = registri.jalankan_async(8000)       # background thread
# ... lakukan hal lain ...
srv.berhenti()                                  # hentikan server
```

### Publish & Install

Di folder proyek paket (harus ada `brolang.json`):

```bash
bro pkg init
bro pkg publish --registry http://127.0.0.1:8000
```

Di mesin/proyek lain:

```bash
bro pkg install nama-paket --registry http://host:8000
bro pkg search kata-kunci          # hasil lokal + remote digabung
```

Lalu pakai di kode:

```bro
impor nama-paket
tulis nama-paket.fungsi_utama()
```

### HTTP API

| Endpoint | Fungsi |
|----------|--------|
| `GET /api/paket` | Daftar semua paket (JSON) |
| `GET /api/paket/<nama>` | Info satu paket |
| `POST /api/publish` | Publish paket (manifest + file) |
| `GET /api/download/<nama>` | Unduh paket (tar.gz) |

### API Modul `registri`

| Fungsi | Keterangan |
|--------|------------|
| `jalankan(port?, host?, folder?)` | Jalankan server (blocking) |
| `jalankan_async(port?, host?, folder?)` | Jalankan server di background thread → objek `berhenti()` |
| `atur_folder(path)` | Set folder penyimpanan paket |
| `buat_tar(manifest, files)` | Buat tarball dari `{path: konten}` |

Folder default: `~/.brolang/registry-server` (bisa di-override dengan env `BROLANG_REGISTRY_DIR`).

---

## 6. Error CLI Profesional

`bro run` kini menampilkan error ala compiler modern:

```text
==================================================
[Error BroLang]
==================================================
File      : app.bro
Baris     : 4 (kolom 1)
Sumber    : buat umur: Angka = "salah"
              ^
Pesan     : Tipe tidak cocok untuk 'umur': diharapkan Angka, tapi mendapat teks.
Solusi    : Ubah nilai menjadi Angka atau ubah anotasi tipe.
==================================================
```

Yang ditampilkan: lokasi (file/baris/kolom), baris sumber dengan penanda `^`, pesan + solusi (+ contoh bila ada), dan stack trace panggilan fungsi.

---

## Ringkasan

| Fitur | Sintaks | Konsisten Interpreter + Transpiler |
|-------|---------|:---:|
| Anotasi tipe | `buat x: Angka = 5`, `fungsi f(a: Angka) -> Teks` | ✅ |
| Union & generik | `Angka \| Teks`, `Daftar<Angka>` | ✅ |
| Pola list/objek | `[a, b]:`, `{"nama": n}:` | ✅ |
| Binding & guard | `n:`, `x jika x > 10:` | ✅ |
| Custom error | `kelas_error Nama extends Kesalahan` | ✅ |
| Modul baru | `tanggal`, `catat`, `lingkungan`, `proses`, `csv`, `registri` | ✅ |
| Registry online | `registri.jalankan(port)` + `bro pkg --registry` | ✅ |
