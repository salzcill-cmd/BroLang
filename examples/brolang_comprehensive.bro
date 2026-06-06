# ==========================================
# BroLang Comprehensive Example
# ==========================================
# Menampilkan semua fitur bahasa BroLang
# ==========================================

# ==========================================
# 1. OUTPUT & INPUT
# ==========================================
tulis "Selamat datang di BroLang!"
tulis "Belajar coding semudah membaca bahasa manusia."

# ==========================================
# 2. VARIABEL & TIPE DATA
# ==========================================
buat nama = "Budi"
buat umur = 17
buat tinggi = 170.5
buat siswa = benar
buat nilai = kosong
buat phi = 3.14159

tulis "Nama:", nama
tulis "Tipe:", tipe(nama), tipe(umur), tipe(tinggi)
tulis "Siswa:", siswa

# ==========================================
# 3. OPERATOR ARITMATIKA
# ==========================================
buat a = 10
buat b = 3

tulis "Tambah:", a + b
tulis "Kurang:", a - b
tulis "Kali:", a * b
tulis "Bagi:", a / b
tulis "Modulo:", a % b
tulis "Pangkat:", a ** b

# ==========================================
# 4. OPERATOR PERBANDINGAN
# ==========================================
tulis "==", a == b
tulis "!=", a != b
tulis ">", a > b
tulis "<", a < b
tulis ">=", a >= b
tulis "<=", a <= b

# ==========================================
# 5. OPERATOR LOGIKA
# ==========================================
buat x = benar
buat y = salah

tulis "dan:", x dan y
tulis "atau:", x atau y
tulis "bukan:", bukan x

# ==========================================
# 6. PERCABANGAN (IF-ELIF-ELSE)
# ==========================================
buat nilai_ujian = 85

jika nilai_ujian >= 90 maka
    tulis "Grade A - Luar biasa!"
lainnya jika nilai_ujian >= 80 maka
    tulis "Grade B - Bagus!"
lainnya jika nilai_ujian >= 70 maka
    tulis "Grade C - Cukup!"
lainnya
    tulis "Grade D - Belajar lagi!"
selesai

# ==========================================
# 7. PERULANGAN (FOR)
# ==========================================
tulis "Menghitung 1-5:"
untuk i dalam range(1, 6) lakukan
    tulis i
selesai

buat buah = ["apel", "pisang", "jeruk", "mangga"]
tulis "Daftar buah:"
untuk item dalam buah lakukan
    tulis "-", item
selesai

# ==========================================
# 8. PERULANGAN (WHILE)
# ==========================================
buat counter = 1
selama counter <= 3 lakukan
    tulis "Perulangan while ke-", counter
    counter = counter + 1
selesai

# ==========================================
# 9. FUNGSI
# ==========================================
fungsi sapa(nama)
    kembali "Halo " + nama + "! Selamat belajar BroLang."
selesai

fungsi tambah(a, b)
    kembali a + b
selesai

fungsi faktorial(n)
    jika n <= 1 maka
        kembali 1
    lainnya
        kembali n * faktorial(n - 1)
    selesai
selesai

tulis sapa("Budi")
tulis "5 + 3 =", tambah(5, 3)
tulis "Faktorial 5 =", faktorial(5)

# ==========================================
# 10. CLASS (OOP)
# ==========================================
kelas Mahasiswa

    fungsi __init__(nama, jurusan)
        buat self.nama = nama
        buat self.jurusan = jurusan
        buat self.nilai = []
    selesai

    fungsi tambah_nilai(n)
        self.nilai = self.nilai + [n]
    selesai

    fungsi rata_rata()
        buat total = 0
        untuk n dalam self.nilai lakukan
            total = total + n
        selesai
        kembali total / len(self.nilai)
    selesai

    fungsi info()
        kembali self.nama + " (" + self.jurusan + ")"
    selesai

selesai

buat mhs = Mahasiswa("Ani", "Informatika")
mhs.tambah_nilai(85)
mhs.tambah_nilai(90)
mhs.tambah_nilai(78)

tulis "Mahasiswa:", mhs.info()
tulis "Nilai:", mhs.nilai
tulis "Rata-rata:", mhs.rata_rata()

# ==========================================
# 11. LIST & INDEXING
# ==========================================
buat angka = [1, 2, 3, 4, 5]
tulis "List:", angka
tulis "Elemen pertama:", angka[0]
tulis "Elemen terakhir:", angka[4]
tulis "Panjang list:", len(angka)

# ==========================================
# 12. ERROR HANDLING
# ==========================================
coba
    buat hasil = 10 / 0
    tulis hasil
tangkap error
    tulis "Terjadi error:", error
selesai

coba
    buat data = [1, 2, 3]
    tulis data[10]
tangkap error
    tulis "Error indeks:", error
selesai

# ==========================================
# 13. STANDARD LIBRARY
# ==========================================
impor matematika
impor teks
impor acak

tulis "Akar 25:", matematika.akar(25)
tulis "Pi:", matematika.pi()
tulis "Sin 90:", matematika.sin(3.14159 / 2)
tulis "Upper:", teks.upper("halo dunia")
tulis "Kapital:", teks.kapital("belajar pemrograman")
tulis "Acak 1-10:", acak.bulat(1, 10)

# ==========================================
# 14. OPERASI STRING
# ==========================================
buat pesan = "Halo Dunia"
tulis "Panjang:", len(pesan)
tulis teks.potong(pesan, " ")

# ==========================================
# SELESAI
# ==========================================
tulis ""
tulis "=== BroLang 1.0 ==="
tulis "Selamat! Kamu sudah melihat semua fitur BroLang."
