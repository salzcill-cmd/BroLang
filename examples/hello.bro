# ============================================================
#  BroLang v9.0 — Hello World & Selamat Datang!
#  Jalankan: bro examples/hello.bro
# ============================================================

tulis "============================================="
tulis "  Selamat Datang di BroLang v9.0!"
tulis "============================================="
tulis ""

# Variabel dasar
buat nama = "BroLang Programmer"
buat versi = 9.0
buat tahun = 2026

tulis "Halo Dunia!"
tulis "Selamat datang, " + nama + "!"
tulis "Versi BroLang: " + teks(versi)
tulis "Tahun: " + teks(tahun)
tulis ""

# Fungsi sederhana
fungsi sapa(nama)
    kembali "Halo, " + nama + "! Selamat belajar BroLang!"
selesai

tulis sapa("Developer")
tulis ""

# Loop sederhana
tulis "Hitung mundur:"
untuk i dalam range(5, 0, -1) lakukan
    tulis teks(i) + "..."
selesai
tulis "Lepas! 🚀"
tulis ""

# List comprehension (sintaks BroLang: [expr lalu var dalam iterable])
buat angka = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
buat genap = [x lalu x dalam angka jika x % 2 == 0]
tulis "Angka genap:", genap

# Dict
buat info = {
    "nama": "BroLang",
    "versi": teks(versi),
    "status": "aktif"
}
tulis "Info:", info

tulis ""
tulis "Siap petualangan BroLang! 🎮"
