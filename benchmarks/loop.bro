# Benchmark: Loop & aritmatika (hot path paling umum)
# Jalankan: bro benchmark benchmarks/loop.bro

buat total = 0

untuk i dalam range(1, 50000) lakukan
    total = total + i
selesai

buat genap = 0
untuk i dalam range(0, 25000) lakukan
    jika i % 2 == 0 maka
        genap = genap + 1
    selesai
selesai

tulis "total = " + teks(total)
tulis "genap = " + teks(genap)
