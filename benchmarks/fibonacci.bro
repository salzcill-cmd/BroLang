# Benchmark: Fibonacci rekursif (pemanggilan fungsi + aritmatika)
# Jalankan: bro benchmark benchmarks/fibonacci.bro

fungsi fib(n)
    jika n < 2 maka
        kembali n
    selesai
    kembali fib(n - 1) + fib(n - 2)
selesai

buat hasil = fib(20)
tulis "fib(20) = " + teks(hasil)
