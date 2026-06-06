# Kelas (Object-Oriented Programming)
# ------------------------------------

kelas Manusia

    fungsi __init__(nama, umur)
        buat self.nama = nama
        buat self.umur = umur
    selesai

    fungsi sapa()
        kembali "Halo, nama saya " + self.nama
    selesai

    fungsi info()
        kembali self.nama + " (" + teks(self.umur) + " tahun)"
    selesai

selesai

# Buat objek
buat orang1 = Manusia("Budi", 17)
buat orang2 = Manusia("Ani", 16)

tulis orang1.sapa()
tulis orang2.info()
