# Contoh Fitur BroLang v7.2
# ==========================
# Demo fitur bahasa baru + konsistensi VM + perluasan library.
#
# Jalankan:  bro examples/fitur_v72.bro

impor teks
impor waktu
impor file
impor dasar
impor acak

# ============ 1. List Comprehension ============
tulis "=== List Comprehension ==="
buat data = [1, 2, 3, 4, 5, 6]
buat kuadrat = [x * x lalu x dalam data]
tulis "kuadrat =", kuadrat                 # [1, 4, 9, 16, 25, 36]

buat genap = [x lalu x dalam data jika x % 2 == 0]
tulis "genap =", genap                     # [2, 4, 6]

# ============ 2. Dict Comprehension ============
tulis "=== Dict Comprehension ==="
buat nama = ["andi", "budi", "citra"]
buat panjang = {n: teks.panjang(n) lalu n dalam nama}
tulis "panjang nama =", panjang            # {andi: 4, budi: 4, citra: 5}

buat genap_map = {x: x * 2 lalu x dalam data jika x % 2 == 0}
tulis "genap_map =", genap_map             # {2: 4, 4: 8, 6: 12}

# ============ 3. Set Comprehension ============
tulis "=== Set Comprehension ==="
buat duplikat = [1, 1, 2, 3, 3, 3, 4]
buat unik = {x lalu x dalam duplikat}
tulis "unik =", unik                      # {1, 2, 3, 4}

buat huruf = ["a", "b", "a", "c", "b"]
buat huruf_unik = {h lalu h dalam huruf}
tulis "huruf_unik =", huruf_unik          # {a, b, c}

# ============ 4. Walrus Operator ============
tulis "=== Walrus Operator (:=) ==="
buat total = 0
jika (n := 10) > 5 maka
    total = total + n
selesai
tulis "total =", total                     # 10

buat s = "hello world"
buat cari = 0
untuk i dari 0 sampai teks.panjang(s) - 1 lakukan
    jika (ch := s[i]) == "l" maka
        cari = cari + 1
    selesai
selesai
tulis "jumlah 'l' =", cari                 # 3

# ============ 5. Null-Safe Indexing ============
tulis "=== Null-Safe Indexing (?[ ]) ==="
buat kosong_arr = kosong
buat hasil1 = kosong_arr?[0]
tulis "kosong?[0] =", hasil1               # kosong

buat arr = [10, 20, 30]
buat hasil2 = arr?[1]
tulis "arr?[1] =", hasil2                  # 20

buat obj = { "nama": "budi", "umur": 25 }
buat nama_orang = obj?["nama"]
tulis "obj?[\"nama\"] =", nama_orang        # budi

# ============ 6. Generator di VM ============
tulis "=== Generator (hasilkan) ==="
fungsi hitung_mundur(n)
    selama n > 0 lakukan
        hasilkan n
        n = n - 1
    selesai
selesai

buat hasil_gen = hitung_mundur(4)
tulis "hitung_mundur(4) =", hasil_gen      # [4, 3, 2, 1]

fungsi gabung_generator(a, b)
    hasilkandari a
    hasilkandari b
selesai
tulis "gabung_generator =", gabung_generator([1, 2], [3, 4])   # [1, 2, 3, 4]

# ============ 7. dengan Statement (VM) ============
tulis "=== dengan Statement ==="
kelas Konteks
    fungsi masuk(self)
        tulis "masuk konteks"
    selesai
    fungsi keluar(self)
        tulis "keluar konteks"
    selesai
selesai

buat obj2 = Konteks()
dengan obj2 sebagai k
    tulis "di dalam dengan"
selesai
tulis "selesai dengan"

# ============ 8. Library Baru ============
tulis "=== Library Baru ==="
tulis "waktu.waktu_iso() =", waktu.waktu_iso()
tulis "waktu.timestamp() =", waktu.timestamp()
tulis "waktu.tambah_hari('2026-01-01', 10) =", waktu.tambah_hari("2026-01-01", 10)

tulis "waktu.hari_ini() =", waktu.hari_ini()
tulis "waktu.milidetik() =", waktu.milidetik()

tulis "file.gabung_jalur('a', 'b', 'c.bro') =", file.gabung_jalur("a", "b", "c.bro")
tulis "file.nama_dasar('/tmp/data.txt') =", file.nama_dasar("/tmp/data.txt")
tulis "file.ekstensi('gambar.png') =", file.ekstensi("gambar.png")

buat angka = [5, 2, 8, 1, 9]
tulis "dasar.urutkan(angka) =", dasar.urutkan(angka)
tulis "dasar.terbalik(angka) =", dasar.terbalik(angka)
tulis "dasar.unik([1, 1, 2, 2, 3]) =", dasar.unik([1, 1, 2, 2, 3])
tulis "dasar.kunci(obj) =", dasar.kunci(obj)
tulis "dasar.nilai(obj) =", dasar.nilai(obj)

tulis "acak.pilih_beberapa([1, 2, 3, 4, 5], 2) =", acak.pilih_beberapa([1, 2, 3, 4, 5], 2)
tulis "acak.kata(6) =", acak.kata(6)
tulis "acak.huruf() =", acak.huruf()

tulis ""
tulis "v7.2 selesai!"
