# ============================================================
#  BroLang v9.0 — Standard Library Showcase
#  Jalankan: bro examples/stdlib.bro
# ============================================================

tulis "============================================="
tulis "  BroLang v9.0 — Standard Library"
tulis "============================================="
tulis ""

# ============ 1. Matematika ============
tulis "=== Matematika ==="
impor matematika

tulis "Akar dari 25:", matematika.akar(25)
tulis "Pi:", matematika.pi()
tulis "Sin(π/2):", matematika.sin(matematika.pi() / 2)
tulis "Cos(0):", matematika.cos(0)
tulis "abs(-42):", matematika.abs(-42)
tulis ""

# ============ 2. Teks ============
tulis "=== Teks ==="
impor teks

buat pesan = "Halo Dunia BroLang!"
tulis "upper:", teks.upper(pesan)
tulis "lower:", teks.lower(pesan)
tulis "kapital:", teks.kapital("selamat belajar")
tulis "panjang:", teks.panjang(pesan)
tulis "potong:", teks.potong(pesan, 0, 5)
tulis "ganti:", teks.ganti(pesan, "Dunia", "BroLang")
tulis ""

# ============ 3. Acak ============
tulis "=== Acak ==="
impor acak

tulis "Angka acak (1-100):", acak.bulat(1, 100)
tulis "AcakFloat:", teks(acak.acak_float())
buat buah = ["apel", "pisang", "jeruk", "mangga"]
tulis "Pilihan acak:", acak.pilih(buah)
tulis "Acak:", acak.acak(buah)
tulis ""

# ============ 4. Iterasi (v9.0) ============
tulis "=== Iterasi (v9.0) ==="
impor iterasi

buat angka = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

tulis "chunk(3):", iterasi.chunk(angka, 3)
tulis "flatten:", iterasi.flatten([[1, 2], [3, 4], [5]])
tulis "chain:", iterasi.chain([1, 2], [3, 4], [5])
tulis "product:", iterasi.product([1, 2], ["a", "b"])
tulis "kombinasi(3):", iterasi.kombinasi([1, 2, 3, 4], 2)
tulis "permutasi(3):", iterasi.permutasi([1, 2, 3], 2)
tulis "accumulate:", iterasi.accumulate([1, 2, 3, 4])
tulis "take_while(<5):", iterasi.take_while(angka, lalu(x) x < 5)
tulis "drop_while(<5):", iterasi.drop_while(angka, lalu(x) x < 5)
tulis "group_by(ganjil/genap):", iterasi.group_by(angka, lalu(x) x % 2 == 0 ? "genap" : "ganjil")
tulis "interleave:", iterasi.interleave(["a", "b", "c"], [1, 2, 3])
tulis "repeat(3):", iterasi.repeat("x", 3)
tulis ""

# ============ 5. Fungsi (v9.0) ============
tulis "=== Fungsi (v9.0) ==="
impor fungsi

fungsi tambah(a, b)
    kembali a + b
selesai

buat tambah_5 = fungsi.parsial(tambah, 5)
tulis "parsial(tambah, 5)(10):", tambah_5(10)

fungsi kuadrat(x)
    kembali x * x
selesai

buat kuadrat_cached = fungsi.cache(kuadrat)
tulis "cache(kuadrat)(3):", kuadrat_cached(3)

fungsi kurang(a, b)
    kembali a - b
selesai

buat komposisi = fungsi.compose(kuadrat, fungsi.parsial(kurang, 1))
tulis "compose(kuadrat, kurang_1)(5):", komposisi(5)

tulis "clamp(15, 0, 10):", fungsi.clamp(15, 0, 10)
tulis "clamp(-5, 0, 10):", fungsi.clamp(-5, 0, 10)
tulis ""

# ============ 6. Koleksi (v9.0) ============
tulis "=== Koleksi (v9.0) ==="
impor koleksi

buat huruf = ["a", "b", "a", "c", "a", "b"]
tulis "Counter:", koleksi.Counter(huruf)

buat data = {"a": 1, "b": {"c": 2, "d": 3}, "e": 4}
tulis "flatten_dict:", koleksi.flatten_dict(data)

buat flat = {"x.y": 1, "x.z": 2, "w": 3}
tulis "unflatten_dict:", koleksi.unflatten_dict(flat)

buat angka2 = [10, 5, 8, 3, 9]
tulis "top_n(3):", koleksi.top_n(angka2, 3)
tulis "top_n(3, asc):", koleksi.top_n(angka2, 3, lalu(x) -x)
tulis ""

# ============ 7. Catatan Level (v9.0) ============
tulis "=== Catatan Level (v9.0) ==="
impor catatan_level

catatan_level.set_level("DEBUG")
catatan_level.info("Server dimulai")
catatan_level.warning("Disk space rendah")
catatan_level.debug("Variabel x = 42")
catatan_level.error("Koneksi gagal")
tulis ""

# ============ 8. Regex (v9.0) ============
tulis "=== Regex (v9.0) ==="
impor regex

buat teks2 = "Email: budi@example.com, HP: 08123456789"
buat email = regex.cari("[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}", teks2)
tulis "Email ditemukan:", email

buat hp = regex.cari("08[0-9]{9,}", teks2)
tulis "HP ditemukan:", hp

buat hasil = regex.ganti("[0-9]", "*", "12345")
tulis "ganti angka:", hasil
tulis ""

# ============ 9. Encoding (v9.0) ============
tulis "=== Encoding (v9.0) ==="
impor encoding

buat data_asli = "Halo BroLang!"
buat terenkripsi = encoding.base64_encode(data_asli)
tulis "Base64:", terenkripsi

buat terdekripsi = encoding.base64_decode(terenkripsi)
tulis "Didekode:", terdekripsi

buat url_encoded = encoding.url_encode("Halo Dunia! Aku di sini")
tulis "URL encode:", url_encoded
tulis ""

# ============ 10. JSON ============
tulis "=== JSON ==="
impor json

buat data_json = {"nama": "Budi", "umur": 17, "hobi": ["coding", "gaming"]}
buat json_str = json.stringify(data_json)
tulis "JSON:", json_str

buat parsed = json.parse(json_str)
tulis "Parsed:", parsed
tulis "Nama:", parsed["nama"]
tulis ""

tulis "Selesai! 🎉"
