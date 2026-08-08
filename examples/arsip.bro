# Arsip — ZIP & Kompresi
# ======================
# Contoh penggunaan modul `arsip` (v6.4):
#   - Membuat arsip ZIP dari file
#   - Menambah file ke arsip yang sudah ada
#   - Mendaftar & mengekstrak isi arsip
#   - Kompresi teks (zlib + Base64)
#
# Jalankan: bro run examples/arsip.bro

impor arsip
impor file
impor teks

# Siapkan file contoh
file.tulis("catatan_a.txt", "Isi catatan A")
file.tulis("catatan_b.txt", "Isi catatan B")

tulis "=== Membuat arsip ZIP ==="
buat ok = arsip.buat_zip("backup.zip", ["catatan_a.txt", "catatan_b.txt"])
tulis f"Backup dibuat : {ok}"

tulis ""
tulis "=== Daftar isi arsip ==="
tulis arsip.daftar_zip("backup.zip")

tulis ""
tulis "=== Tambah file ke arsip ==="
file.tulis("catatan_baru.txt", "Isi catatan baru")
tulis arsip.tambah_ke_zip("backup.zip", "catatan_baru.txt")
tulis arsip.daftar_zip("backup.zip")

tulis ""
tulis "=== Ekstrak arsip ==="
tulis arsip.ekstrak_zip("backup.zip", "hasil_ekstrak/")

tulis ""
tulis "=== Kompresi teks ==="
buat teks_panjang = "BroLang keren! " * 50
buat padat = arsip.kompres(teks_panjang)
tulis f"Asli : {teks.panjang(teks_panjang)} karakter"
tulis f"Padat: {teks.panjang(padat)} karakter"
tulis f"Hasil dekompres sama? {arsip.dekompres(padat) == teks_panjang}"
