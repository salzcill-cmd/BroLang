# Fungsi (Function)
# ------------------

fungsi sapa(nama)
    kembali "Halo " + nama + "!"
selesai

fungsi tambah(a, b)
    kembali a + b
selesai

fungsi hitung_rata_rata(angka1, angka2)
    buat hasil = (angka1 + angka2) / 2
    kembali hasil
selesai

# Panggil fungsi
tulis sapa("Budi")
tulis "5 + 3 =", tambah(5, 3)
tulis "Rata-rata:", hitung_rata_rata(10, 20)
