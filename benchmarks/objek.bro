# Benchmark: OOP — instansiasi kelas, method call, akses atribut
# Jalankan: bro benchmark benchmarks/objek.bro

kelas Karyawan
    fungsi __init__(nama, gaji)
        self.nama = nama
        self.gaji = gaji
    selesai

    fungsi naik_gaji(persen)
        self.gaji = self.gaji + self.gaji * persen / 100
        kembali self.gaji
    selesai
selesai

buat total_gaji = 0

untuk i dalam range(0, 5000) lakukan
    buat k = Karyawan("Karyawan-" + teks(i), 1000)
    total_gaji = total_gaji + k.naik_gaji(10)
selesai

tulis "total_gaji = " + teks(total_gaji)
