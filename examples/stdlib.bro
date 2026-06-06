# Standard Library BroLang
# -------------------------

impor matematika
impor teks
impor acak

# Matematika
tulis "Akar dari 25:", matematika.akar(25)
tulis "Sin 90:", matematika.sin(3.14159 / 2)
tulis "Pi:", matematika.pi()

# Manipulasi Teks
tulis teks.upper("halo dunia")
tulis teks.kapital("selamat belajar")

# Random
tulis "Angka acak (1-100):", acak.bulat(1, 100)

buat pilihan = acak.pilih(["apel", "pisang", "jeruk"])
tulis "Pilihan acak:", pilihan
