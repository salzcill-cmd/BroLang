# ============================================================
# BroLang v6.9 — Guard Clause untuk Semua Statement
# ------------------------------------------------------------
# Statement apa pun kini bisa diberi kondisi `jika c`:
#   1. tulis x jika c
#   2. buat x = v jika c | x = v jika c | x += v jika c
#   3. self.x = v jika c | data[i] += v jika c
#   4. lempar e jika c | f() jika c | hasilkan x jika c
#   5. Ternary tetap ternary: a jika b lainnya c
#
# Jalankan:  bro examples/fitur_v69.bro
# ============================================================

# ---------- 1. tulis ber-guard ----------
buat x = 10
tulis "x > 5   =>", x jika x > 5          # muncul: 10
tulis "x > 100 =>", x jika x > 100        # tidak muncul

# Guard di dalam loop — hanya cetak angka ganjil
untuk i dari 1 sampai 5 lakukan
    tulis "ganjil:", i jika i % 2 == 1
selesai

# ---------- 2. Assignment ber-guard ----------
buat skor = 0
skor = 100 jika benar
tulis "skor = 100 jika benar =>", skor    # 100
skor = 0 jika salah
tulis "skor = 0 jika salah   =>", skor    # 100 (guard salah, tidak berubah)

buat total = 1
total += 9 jika benar
tulis "total += 9 jika benar =>", total   # 10

# ---------- 3. Atribut & index ber-guard ----------
kelas Akun
    fungsi __init__(self)
        self.bonus = 0
    selesai
    fungsi beri_bonus(self, n)
        self.bonus += n jika n > 0        # guard di dalam method
        kembali self.bonus
    selesai
selesai
buat ak = Akun()
tulis "beri_bonus(5)         =>", ak.beri_bonus(5)     # 5
tulis "beri_bonus(-999)      =>", ak.beri_bonus(-999)  # 5 (guard salah)

buat data = [1, 2, 3]
data[1] += 10 jika benar
tulis "data[1] += 10          =>", data                # [1, 12, 3]

# ---------- 4. lempar / panggilan / yield ber-guard ----------
coba
    lempar "boom" jika salah
    tulis "coba/tangkap: aman"             # muncul (guard salah, tidak melempar)
tangkap error
    tulis "tertangkap!"
selesai

fungsi cetak_pesan(p)
    tulis "pesan:", p
selesai
cetak_pesan("dipanggil") jika benar        # pesan: dipanggil
cetak_pesan("tidak") jika salah           # tidak muncul

fungsi gen()
    hasilkan "a"
    hasilkan "b" jika salah
    hasilkan "c" jika benar
selesai
buat g = gen()
tulis "gen:"
untuk v dalam g lakukan
    tulis v                               # a c (b dilewati guard)
selesai

# ---------- 5. Ternary tetap ternary ----------
buat a = 5 jika benar lainnya 99
buat b = 5 jika salah lainnya 99
tulis "ternary a / b          =>", a, b   # 5 99
