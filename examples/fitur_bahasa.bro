# Contoh Fitur Bahasa v6.5
# ========================
# Fitur baru di BroLang v6.5:
#   1. konstanta         — variabel immutable
#   2. ulangi ... sampai — do-until loop (body jalan minimal sekali)
#   3. untuk i dari A sampai B langkah S — range for loop (inklusif)

# Jalankan dengan: bro examples/fitur_bahasa.bro

tulis "=== 1. Konstanta (immutable) ==="
konstanta NAMA = "BroLang"
konstanta PI = 3.14
konstanta MAKS_PERCUBAAN: Angka = 3

tulis "Nama bahasa : " + NAMA
tulis "Nilai PI    : " + teks(PI)

# Reassignment akan error:
# NAMA = "Python"   # ✗ konstanta tidak bisa diubah

tulis ""

tulis "=== 2. ulangi ... sampai (do-until) ==="
buat tebakan = 0
ulangi
    tebakan = tebakan + 1
    tulis "Percobaan ke-" + teks(tebakan)
sampai tebakan >= MAKS_PERCUBAAN

tulis ""

tulis "=== 3. untuk i dari A sampai B (range for) ==="
tulis "Naik (inklusif):"
untuk i dari 1 sampai 5 lakukan
    tulis "  " + teks(i)
selesai

tulis "Turun otomatis:"
untuk i dari 5 sampai 1 lakukan
    tulis "  " + teks(i)
selesai

tulis "Langkah positif:"
untuk i dari 0 sampai 20 langkah 5 lakukan
    tulis "  " + teks(i)
selesai

tulis "Langkah negatif:"
untuk i dari 10 sampai 2 langkah -2 lakukan
    tulis "  " + teks(i)
selesai

tulis ""

tulis "=== Kombinasi: konstanta + range for ==="
konstanta BATAS = 10
buat total = 0
untuk i dari 1 sampai BATAS lakukan
    total = total + i
selesai
tulis "Jumlah 1.." + teks(BATAS) + " = " + teks(total)
