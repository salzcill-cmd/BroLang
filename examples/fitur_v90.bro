# ============================================================
#  BroLang v9.0 — Comprehensive Features Demo
#  Jalankan: bro examples/fitur_v90.bro
# ============================================================

impor waktu

tulis "============================================="
tulis "  BroLang v9.0 — Comprehensive Demo"
tulis "============================================="
tulis ""

# ============ 1. Closure by Reference ============
tulis "=== 1. Closure by Reference ==="

fungsi buat_counter()
    buat count = 0
    fungsi increment()
        count = count + 1
        kembali count
    selesai
    fungsi get_count()
        kembali count
    selesai
    kembali {"increment": increment, "get": get_count}
selesai

buat counter = buat_counter()
tulis "Pertama:", counter["increment"]()
tulis "Kedua:", counter["increment"]()
tulis "Ketiga:", counter["increment"]()
tulis "Total:", counter["get"]()
tulis ""

# ============ 2. Global & Nonlocal ============
tulis "=== 2. Global & Nonlocal ==="

buat nilai_global = 10

fungsi update_global()
    global nilai_global
    nilai_global = nilai_global + 5
selesai

tulis "Global awal:", nilai_global
update_global()
tulis "Global setelah update:", nilai_global
tulis ""

# ============ 3. Lazy Generators ============
tulis "=== 3. Lazy Generators ==="

fungsi fibonacci()
    buat a, b = 0, 1
    selama benar lakukan
        hasilkan a
        buat temp = b
        b = a + b
        a = temp
    selesai
selesai

buat fib = fibonacci()
tulis "5 angka Fibonacci pertama:", [fib(), fib(), fib(), fib(), fib()]

fungsi ganjil_sampai(n)
    buat i = 1
    selama i <= n lakukan
        hasilkan i
        i = i + 2
    selesai
selesai

buat ganjil = ganjil_sampai(10)
tulis "Bilangan ganjil sampai 10:", ganjil
tulis ""

# ============ 4. Bitwise Operations ============
tulis "=== 4. Bitwise Operations ==="

buat a = 12   # 0b1100
buat b = 10   # 0b1010

tulis "a =", a
tulis "b =", b
tulis "a & b =", a & b
tulis "a | b =", a | b
tulis "a ^ b =", a ^ b
tulis "~a =", ~a
tulis "a << 2 =", a << 2
tulis "a >> 2 =", a >> 2
tulis ""

# ============ 5. List/Dict Comprehension ============
tulis "=== 5. Comprehension ==="

buat angka = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# List comprehension (sintaks BroLang: [expr lalu var dalam iterable])
buat kuadrat = [x * x lalu x dalam angka]
tulis "Kuadrat:", kuadrat

buat genap = [x lalu x dalam angka jika x % 2 == 0]
tulis "Genap:", genap

buat ganjil_kuadrat = [x * x lalu x dalam angka jika x % 2 != 0]
tulis "Ganjil kuadrat:", ganjil_kuadrat

# Dict comprehension
buat indeks = {teks(i): i lalu i dalam range(5)}
tulis "Indeks:", indeks

buat pangkat = {x: x * x lalu x dalam range(6)}
tulis "Pangkat:", pangkat
tulis ""

# ============ 6. Pattern Matching ============
tulis "=== 6. Pattern Matching ==="

fungsi describe(value)
    jika value == 0 maka
        kembali "nol"
    selesai
    jika value == 1 atau value == 2 atau value == 3 maka
        kembali "kecil: " + teks(value)
    selesai
    jika value > 0 dan value < 100 maka
        kembali "sedang: " + teks(value)
    selesai
    kembali "besar: " + teks(value)
selesai

tulis "describe(0):", describe(0)
tulis "describe(2):", describe(2)
tulis "describe(50):", describe(50)
tulis "describe(150):", describe(150)
tulis ""

# ============ 7. Array/Dict Destructuring ============
tulis "=== 7. Destructuring ==="

buat [a2, b2, c2] = [10, 20, 30]
tulis "Destructuring list:", a2, b2, c2

buat {nama, umur} = {"nama": "Budi", "umur": 17, "kota": "Jakarta"}
tulis "Destructuring dict:", nama, umur
tulis ""

# ============ 8. Switch Statement (match) ============
tulis "=== 8. Switch Statement ==="

buat hari = "Senin"
jika hari == "Senin" atau hari == "Selasa" atau hari == "Rabu" atau hari == "Kamis" atau hari == "Jumat" maka
    tulis hari, "→ Hari kerja"
lainnya jika hari == "Sabtu" atau hari == "Minggu" maka
    tulis hari, "→ Akhir pekan"
lainnya
    tulis hari, "→ Tidak dikenal"
selesai
tulis ""

# ============ 9. Enhanced String Interpolation ============
tulis "=== 9. String Interpolation ==="

buat nama2 = "BroLang"
buat versi = 9.0
buat tahun = 2026

tulis "Framework: " + nama2 + " v" + teks(versi)
tulis "Release: " + teks(tahun)
tulis "Calculation: 2 + 3 = " + teks(2 + 3)
tulis ""

# ============ 10. Spread Operator ============
tulis "=== 10. Spread Operator ==="

buat list1 = [1, 2, 3]
buat list2 = [4, 5, 6]
buat gabungan = [...list1, ...list2, 7, 8]
tulis "Gabungan:", gabungan

buat dict1 = {"a": 1, "b": 2}
buat dict2 = {"c": 3, "d": 4}
buat gabungan_dict = {...dict1, ...dict2, "e": 5}
tulis "Gabungan dict:", gabungan_dict
tulis ""

# ============ 11. Nilai Default & Rest Args ============
tulis "=== 11. Default & Rest Args ==="

fungsi buat_profil(nama, umur=17, ...hobi)
    kembali {
        "nama": nama,
        "umur": umur,
        "hobi": hobi
    }
selesai

tulis "Profil 1:", buat_profil("Budi")
tulis "Profil 2:", buat_profil("Ani", 20, "coding", "gaming")
tulis ""

# ============ 12. Ternary Operator ============
tulis "=== 12. Ternary Operator ==="

buat angka2 = 42
buat status = "genap" jika angka2 % 2 == 0 lainnya "ganjil"
tulis angka2, "adalah", status

buat x = 5
buat hasil = "besar" jika x > 10 lainnya "sedang" jika x > 3 lainnya "kecil"
tulis "x =", x, "→", hasil
tulis ""

# ============ 13. Error Handling ============
tulis "=== 13. Error Handling ==="

fungsi bagi(a, b)
    jika b == 0 maka
        lempar "Tidak bisa bagi nol!"
    selesai
    kembali a / b
selesai

coba
    tulis "10 / 2 =", bagi(10, 2)
    tulis "10 / 0 =", bagi(10, 0)
kecuali sebagai e
    tulis "Error:", e
selesai
tulis ""

# ============ 14. Async/Await ============
tulis "=== 14. Async/Await ==="

asinkron fungsi ambil_data()
    tunggu waktu.tidur(0.01)
    kembali "Data dari server"
selesai

asinkron fungsi proses()
    buat data = tunggu ambil_data()
    kembali "Diproses: " + data
selesai

buat hasil2 = tunggu proses()
tulis hasil2
tulis ""

tulis "============================================="
tulis "  Semua fitur v9.0 berhasil!"
tulis "============================================="
