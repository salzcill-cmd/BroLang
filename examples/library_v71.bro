# Contoh Perluasan Library BroLang v7.1
# ======================================
# Demo fungsi baru di modul stdlib yang diperluas.
#
# Jalankan:  bro examples/library_v71.bro

# ============ matematika ============
tulis "=== matematika ==="
impor matematika
buat nilai = [7, 3, 9, 3, 5]
tulis "rata_rata :", matematika.rata_rata(nilai)
tulis "median    :", matematika.median(nilai)
tulis "modus     :", matematika.modus(nilai)
tulis "fpb(12,18) :", matematika.fpb(12, 18)
tulis "kpk(4,6)   :", matematika.kpk(4, 6)
tulis "prima(17)  :", matematika.prima(17)
tulis "fibonacci  :", matematika.fibonacci(10)
tulis "clamp      :", matematika.clamp(50, 0, 10)
tulis "kombinasi  :", matematika.kombinasi(5, 2)

# ============ teks ============
tulis "\n=== teks ==="
impor teks
tulis "balik      :", teks.balik("abc")
tulis "hitung_kata:", teks.hitung_kata("Halo dunia, apa kabar")
tulis "regex_ganti:", teks.regex_ganti("a1 b2", "\\d", "#")
tulis "regex_cari :", teks.regex_cari("Halo 123", "\\d+")

# ============ tanggal ============
tulis "\n=== tanggal ==="
impor tanggal
tulis "nama_hari  :", tanggal.nama_hari("2026-08-07")
tulis "kabisat    :", tanggal.kabisat(2024)
tulis "akhir_bulan:", tanggal.akhir_bulan("2024-02-10")
tulis "tambah_bulan:", tanggal.tambah_bulan("2026-01-31", 1)

# ============ angka ============
tulis "\n=== angka ==="
impor angka
tulis "fpb(12,18)  :", angka.fpb(12, 18)
tulis "ke_biner(10):", angka.ke_biner(10)
tulis "dari_heksa  :", angka.dari_heksa("ff")
tulis "digit(1234) :", angka.digit(1234)
tulis "terbalik    :", angka.terbalik(1234)

# ============ dasar ============
tulis "\n=== dasar ==="
impor dasar
tulis "ke_angka    :", dasar.ke_angka("42")
tulis "ke_boolean  :", dasar.ke_boolean("benar")
tulis "jenis([1,2]) :", dasar.jenis([1, 2])
tulis "adalah_kosong(''):", dasar.adalah_kosong("")

# ============ acak ============
tulis "\n=== acak ==="
impor acak
acak.seed(7)
tulis "boolean     :", acak.boolean()
tulis "huruf       :", acak.huruf()
tulis "kata(5)     :", acak.kata(5)
tulis "antara      :", acak.antara(1, 10)

# ============ file & json ============
tulis "\n=== file & json ==="
impor file
impor json
buat jalur = file.gabung_jalur("contoh_tmp", "data.json")
file.buat_folder("contoh_tmp")
# `tulis`/`hapus` adalah keyword → pakai alias tulis_file/hapus_file
json.tulis_file(jalur, {"nama": "Budi", "nilai": [1, 2, 3]})
tulis "file.ada       :", file.ada(jalur)
tulis "file.ekstensi  :", file.ekstensi(jalur)
tulis "file.ukuran    :", file.ukuran(jalur), "bytes"
buat data = json.baca(jalur)
tulis "json.baca.nama :", data["nama"]
tulis "json.valid     :", json.valid('{"ok": true}')
file.hapus_file(jalur)
file.hapus_folder("contoh_tmp")

# ============ sistem & proses ============
tulis "\n=== sistem & proses ==="
impor sistem
impor proses
tulis "sistem.jumlah_cpu:", sistem.jumlah_cpu()
tulis "sistem.memori    :", sistem.memori()
tulis "proses.proses_id :", proses.proses_id()
buat hasil = proses.jalankan_list(["echo", "halo"])
tulis "proses.jalankan_list:", hasil.keluaran, "| kode", hasil.kode

# ============ catat ============
tulis "\n=== catat ==="
impor catat
catat.atur_level("info")
catat.sukses("Operasi selesai")
catat.catat("info", "pesan umum")

tulis "\nSemua fungsi library v7.1 berhasil!"
