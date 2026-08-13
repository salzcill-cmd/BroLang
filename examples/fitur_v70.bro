# Contoh Fitur BroLang v7.0
# ==========================
# Demo fitur bahasa modern + async/await sejati + perbaikan VM.
#
# Jalankan:  bro examples/fitur_v70.bro

# ============ 1. Multiple Assignment ============
tulis "=== Multiple Assignment ==="

buat a, b = 1, 2            # deklarasi ganda
tulis "a=", a, " b=", b     # a=1 b=2

buat x, y, z = 1, 2, 3
tulis "x, y, z =", x, y, z  # 1 2 3

a, b = b, a                 # swap aman
tulis "setelah swap: a=", a, " b=", b    # a=2 b=1

buat p = 5
buat q = 10
p, q = q, p + q             # nilai kanan dievaluasi dulu semua
tulis "p, q =", p, q        # 10 15

fungsi tukar(m, n)
    m, n = n, m
    kembali m, n
selesai
tulis "tukar(1, 2) =", tukar(1, 2)   # (2, 1)

# ============ 2. Switch Expression ============
tulis "\n=== Switch Expression ==="

buat kode = 2
buat nama = cocokkan kode {
    1: "satu",
    2: "dua",
    _: "lainnya"
}
tulis "kode 2 ->", nama        # dua

buat fallback = cocokkan 99 { 1: "satu", _: "lainnya" }
tulis "kode 99 ->", fallback   # lainnya

buat data = { "x": 10, "y": 20 }
buat jumlah = cocokkan data {
    { "x": vx, "y": vy }: vx + vy,
    _: 0
}
tulis "x + y =", jumlah        # 30

# ============ 3. Error Propagation '?' ============
tulis "\n=== Error Propagation ==="

fungsi cari(id)
    jika id == 1 maka
        kembali Benar("ditemukan")
    lainnya
        kembali Salah("tidak ada")
    selesai
selesai

tulis "cari(1)? =", cari(1)?          # ditemukan
tulis "Ada(7)? =", Ada(7)?            # 7

coba
    tulis cari(2)?                    # Salah -> lempar error
tangkap e
    tulis "error tertangkap:", e
selesai

coba
    tulis Kosong()?                   # Kosong -> lempar error
tangkap e
    tulis "kosong tertangkap:", e
selesai

# Nilai biasa: no-op
tulis "7? =", 7?

# ============ 4. Async/Await Sejati ============
tulis "\n=== Async/Await Sejati ==="
impor event_loop

asinkron fungsi muat(url)
    event_loop.tidur(0.1)          # simulasi IO — tidak memblokir task lain
    kembali "data dari " + url
selesai

buat t1 = muat("api/1")
buat t2 = muat("api/2")
tulis "task dibuat, belum selesai:", bukan t1.selesai()
tulis tunggu t1                    # blokir sampai t1 selesai

asinkron fungsi kerja(n)
    event_loop.tidur(0.15)
    kembali n * 10
selesai

buat k1 = kerja(1)
buat k2 = kerja(2)
buat k3 = kerja(3)
tulis "tunggu_semua:", event_loop.tunggu_semua([k1, k2, k3])   # [10, 20, 30]

asinkron fungsi tugas_dalam()
    kembali "dalam"
selesai

asinkron fungsi luar()
    buat d = tugas_dalam()         # task dalam task — tidak deadlock
    buat r = tunggu d
    kembali "luar + " + r
selesai
tulis tunggu luar()                # luar + dalam

coba
    asinkron fungsi gagal()
        lempar "boom"
    selesai
    buat g = gagal()
    buat r = tunggu g              # error task dilempar di sini
tangkap e
    tulis "error task:", e
selesai

tulis "\nSemua fitur v7.0 berhasil!"
