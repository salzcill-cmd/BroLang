# ============================================================
# BroLang v6.7 — Fitur Bahasa Baru
# -------------------------------------------
# 1. Rest parameter  : fungsi f(...sisa)
# 2. Spread call     : f(...daftar)
# 3. Spread list     : [...a, 1, 2]
# 4. Multiple return : kembali a, b
#
# Jalankan:  bro examples/fitur_v67.bro
# ============================================================

# ---------- 1. Rest parameter ----------
fungsi jumlahkan(...angka)
    buat total = 0
    untuk setiap n dalam angka lakukan
        total = total + n
    selesai
    kembali total
selesai

tulis "jumlahkan(1..5)      =", jumlahkan(1, 2, 3, 4, 5)   # 15

fungsi sapa(nama, ...sisanya)
    tulis "Halo", nama, "tambahan:", sisanya
selesai

sapa("Budi")                          # Halo Budi tambahan: []
sapa("Ani", 1, 2)                     # Halo Ani tambahan: [1, 2]

# ---------- 2. Spread call ----------
fungsi kali3(a, b, c)
    kembali a * b * c
selesai

buat nilai = [2, 3, 4]
tulis "kali3(...[2,3,4])     =", kali3(...nilai)            # 24
tulis "kali3(...[1,2], 3)    =", kali3(...[1, 2], 3)        # 6

# ---------- 3. Spread list ----------
buat dasar = [1, 2]
buat gabung = [...dasar, 3, 4]
tulis "gabung                =", gabung                    # [1, 2, 3, 4]

buat a = [1]
buat b = [5, 6]
tulis "campur                =", [...a, 2, 3, ...b]         # [1, 2, 3, 5, 6]

# ---------- 4. Multiple return ----------
fungsi bagi_dan_sisa(a, b)
    kembali a / b, a % b
selesai

buat [hasil, sisa] = bagi_dan_sisa(17, 5)
tulis "17 / 5, 17 % 5        =", hasil, sisa               # 3.4 2

fungsi statistik(data)
    buat total = 0
    buat terbesar = 0
    untuk setiap n, i dalam data lakukan
        total = total + n
        jika i == 0 atau n > terbesar maka
            terbesar = n
        selesai
    selesai
    kembali total, terbesar
selesai

buat [sum, maks] = statistik([4, 9, 2, 7])
tulis "total & terbesar      =", sum, maks                 # 22 9
