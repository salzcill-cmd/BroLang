# Benchmark: Manipulasi string & f-string
# Jalankan: bro benchmark benchmarks/string.bro

buat teks_hasil = ""

untuk i dalam range(0, 2000) lakukan
    teks_hasil = teks_hasil + "x"
selesai

buat panjang_total = 0
untuk i dalam range(0, 1000) lakukan
    buat pesan = f"nilai-{i}"
    panjang_total = panjang_total + panjang(pesan)
selesai

tulis "panjang = " + teks(panjang(teks_hasil))
tulis "total = " + teks(panjang_total)
