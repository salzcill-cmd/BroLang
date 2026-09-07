# ============================================================
#  BroLang v9.0 — Fungsi: Closure, Decorator, Generator
#  Jalankan: bro examples/fungsi.bro
# ============================================================

tulis "============================================="
tulis "  BroLang v9.0 — Fungsi Lanjutan"
tulis "============================================="
tulis ""

# ============ 1. Fungsi Dasar ============
tulis "=== Fungsi Dasar ==="

fungsi tambah(a, b)
    kembali a + b
selesai

fungsi kali(a, b)
    kembali a * b
selesai

tulis "3 + 5 =", tambah(3, 5)
tulis "4 * 7 =", kali(4, 7)
tulis ""

# ============ 2. Closure (Fungsi dalam Fungsi) ============
tulis "=== Closure ==="

fungsi buat_pengali(n)
    # Closure: fungsi inner mengakses variabel outer
    fungsi pengali(x)
        kembali x * n
    selesai
    kembali pengali
selesai

buat kali_dua = buat_pengali(2)
buat kali_lima = buat_pengali(5)

tulis "3 * 2 =", kali_dua(3)
tulis "3 * 5 =", kali_lima(3)
tulis ""

# Counter closure
fungsi buat_counter(start)
    buat nilai = start
    fungsi increment()
        nilai = nilai + 1
        kembali nilai
    selesai
    kembali increment
selesai

buat counter = buat_counter(0)
tulis "Counter:", counter()
tulis "Counter:", counter()
tulis "Counter:", counter()
tulis ""

# ============ 3. Lambda (Fungsi Anonim) ============
tulis "=== Lambda ==="

# Sintaks lambda: lalu(params) expr
buat kuadrat = lalu(x) x * x
tulis "kuadrat(5):", kuadrat(5)

buat tambah_tiga = lalu(x) x + 3
tulis "tambah_tiga(7):", tambah_tiga(7)

buat kali_dua_lambda = lalu(x) x * 2
tulis "kali_dua(6):", kali_dua_lambda(6)
tulis ""

# ============ 4. Higher-Order Functions ============
tulis "=== Higher-Order Functions ==="

fungsi apply(f, x)
    kembali f(x)
selesai

tulis "apply(kuadrat, 4):", apply(kuadrat, 4)

buat angka = [1, 2, 3, 4, 5]

# Map
buat kuadrat_list = []
untuk x dalam angka lakukan
    kuadrat_list = [...kuadrat_list, kuadrat(x)]
selesai
tulis "kuadrat:", kuadrat_list

# Filter
buat genap = []
untuk x dalam angka lakukan
    jika x % 2 == 0 maka
        genap = [...genap, x]
    selesai
selesai
tulis "genap:", genap
tulis ""

# ============ 5. Default Arguments ============
tulis "=== Default Arguments ==="

fungsi sapa(nama, sapaan="Halo")
    kembali sapaan + ", " + nama + "!"
selesai

tulis sapa("Budi")
tulis sapa("Ani", "Selamat pagi")
tulis ""

# ============ 6. Rest Arguments ============
tulis "=== Rest Arguments ==="

# Sintaks rest: ...nama parameter
fungsi jumlah_semua(...args)
    buat total = 0
    untuk x dalam args lakukan
        total = total + x
    selesai
    kembali total
selesai

tulis "jumlah(1,2,3):", jumlah_semua(1, 2, 3)
tulis "jumlah(10,20,30,40):", jumlah_semua(10, 20, 30, 40)
tulis ""

# ============ 7. Generator (Lazy Evaluation) ============
tulis "=== Generator ==="

fungsi fibonacci(n)
    buat a, b = 0, 1
    untuk i dalam range(n) lakukan
        hasilkan a
        buat temp = b
        b = a + b
        a = temp
    selesai
selesai

buat fib = fibonacci(8)
tulis "Fibonacci 8:", fib
# Output: [0, 1, 1, 2, 3, 5, 8, 13]

# Generator dengan yield
fungsi genap_sampai(n)
    buat i = 0
    selama i <= n lakukan
        jika i % 2 == 0 maka
            hasilkan i
        selesai
        i = i + 1
    selesai
selesai

buat gen = genap_sampai(10)
tulis "Genap sampai 10:", gen
# Output: [0, 2, 4, 6, 8, 10]
tulis ""

# ============ 8. Recursive Functions ============
tulis "=== Recursive Functions ==="

fungsi faktorial(n)
    jika n <= 1 maka
        kembali 1
    selesai
    kembali n * faktorial(n - 1)
selesai

tulis "faktorial(5):", faktorial(5)

fungsi fib_recursive(n)
    jika n <= 1 maka
        kembali n
    selesai
    kembali fib_recursive(n - 1) + fib_recursive(n - 2)
selesai

tulis "fib(7):", fib_recursive(7)
tulis ""

# ============ 9. Bitwise Operations ============
tulis "=== Bitwise Operations ==="

buat a = 12   # 1100
buat b = 10   # 1010

tulis "12 & 10 =", a & b     # 8  (1000)
tulis "12 | 10 =", a | b     # 14 (1110)
tulis "12 ^ 10 =", a ^ b     # 6  (0110)
tulis "~12 =", ~a             # -13
tulis "12 << 2 =", a << 2    # 48 (110000)
tulis "12 >> 2 =", a >> 2    # 3  (11)
tulis ""

tulis "Selesai! 🎉"
