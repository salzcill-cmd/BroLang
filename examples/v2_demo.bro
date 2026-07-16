# Contoh Fitur BroLang v2.0
# ==========================
# Demo semua fitur baru di v2: Lambda, Comprehension, F-String, Enum, Struct, Match

# --- Lambda ---
buat kuadrat = lalu(x) x ** 2
buat tambah = lalu(a, b) a + b

tulis "=== Lambda ==="
tulis kuadrat(5)      # 25
tulis tambah(3, 7)    # 10

# --- List Comprehension ---
tulis "\n=== List Comprehension ==="
buat angka = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# Kuadrat semua elemen
buat kuadrat_list = [x ** 2 lalu x dalam angka]
tulis kuadrat_list

# Filter genap saja
buat genap = [x lalu x dalam angka jika x % 2 == 0]
tulis genap

# Gabungkan lambda + comprehension
buat hasil = [kuadrat(x) lalu x dalam [1, 2, 3, 4, 5]]
tulis hasil  # [1, 4, 9, 16, 25]

# --- F-String ---
tulis "\n=== F-String ==="
buat nama = "Budi"
buat umur = 17
buat skor = 95.5

tulis f"Halo, nama saya {nama}"
tulis f"Umur: {umur} tahun"
tulis f"Skor: {skor}"
tulis f"2 + 3 = {2 + 3}"

# --- Enum ---
tulis "\n=== Enum ==="
enum Warna { MERAH, BIRU, HIJAU, KUNING }
enum Status { HIDUP, MATI, JALAN }

buat warna = Warna.BIRU
tulis warna  # Warna.BIRU

# --- Struct ---
tulis "\n=== Struct ==="
struktur Titik {
    x,
    y
}

buat p1 = Titik(10, 20)
buat p2 = Titik(100, 200)

tulis p1           # Titik(10, 20)
tulis p1.x         # 10
tulis p2.y         # 200

# Struct untuk data game
struktur Karakter {
    nama,
    hp,
    attack
}

buat hero = Karakter("Budi", 100, 25)
tulis f"{hero.nama} HP={hero.hp} ATK={hero.attack}"

# --- Match/Case ---
tulis "\n=== Match/Case ==="
buat hari = 3

cocokkan hari {
    1: tulis "Senin"
    2: tulis "Selasa"
    3: tulis "Rabu"
    4: tulis "Kamis"
    5: tulis "Jumat"
    _: tulis "Weekend"
}

# Match dengan enum
buat warna2 = Warna.HIJAU
cocokkan warna2 {
    Warna.MERAH: tulis "Panas!"
    Warna.BIRU: tulis "Dingin!"
    Warna.HIJAU: tulis "Sejuk!"
    _: tulis "Netral"
}

# --- Kombinasi Semua Fitur ---
tulis "\n=== Kombinasi ==="

# Gunakan lambda + comprehension + f-string
buat bilangan = range(1, 11)
buat genap_kuadrat = [kuadrat(x) lalu x dalam bilangan jika x % 2 == 0]
tulis f"Kuadrat genap: {genap_kuadrat}"

# Struct + Enum + Match
enum Aksi { SERANG, BERTAHAN, SEMBUH }

struktur Entity {
    nama,
    hp,
    aksi
}

buat musuh = Entity("Goblin", 50, Aksi.SERANG)
cocokkan musuh.aksi {
    Aksi.SERANG: tulis f"{musuh.nama} menyerang!"
    Aksi.BERTAHAN: tulis f"{musuh.nama} bertahan!"
    Aksi.SEMBUH: tulis f"{musuh.nama} menyembuhkan!"
    _: tulis "Aksi tidak dikenal"
}

tulis "\nSemua fitur v2 berhasil!"
