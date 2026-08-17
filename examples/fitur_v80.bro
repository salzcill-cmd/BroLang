# ============================================================
# BroLang v8.0 — Fitur Bahasa Modern + Performa VM
# Jalankan: bro examples/fitur_v80.bro
# ============================================================

tulis "============================================="
tulis "  BroLang v8.0 — Spread Objek, ??=, Multi-kecuali"
tulis "============================================="

# ---------- 1. Spread Objek {...a, "b": 1} ----------
tulis "\n=== Spread Objek ==="

buat pengaturan = {"suara": 80, "bahasa": "id", "lvl": 3}
buat pemain = {...pengaturan, "nama": "Budi"}
tulis pemain
# {'suara': 80, 'bahasa': 'id', 'lvl': 3, 'nama': 'Budi'}

buat a = {"x": 1, "y": 2}
buat b = {...a, "y": 99}      # kunci item belakang menimpa
tulis b                       # {'x': 1, 'y': 99}

buat c = {"awal": 0, ...a, "z": 5}
tulis c                       # {'awal': 0, 'x': 1, 'y': 2, 'z': 5}

buat d1 = {"nama": "Ani"}
buat d2 = {"umur": 25}
buat gabung = {...d1, ...d2}
tulis gabung                  # {'nama': 'Ani', 'umur': 25}

# ---------- 2. Null-Coalescing Assignment ??= ----------
tulis "\n=== Null-Coalescing Assignment (??=) ==="

buat nama = kosong
nama ??= "Anonim"
tulis nama                    # Anonim

buat skor = 100
skor ??= 0                    # sudah terisi → tidak berubah
tulis skor                    # 100

buat x = 0
x ??= 99                      # 0 BUKAN kosong → tetap 0
tulis x                       # 0

kelas Akun
    fungsi __init__(self)
        self.nama = kosong
    selesai
selesai

buat akun = Akun()
akun.nama ??= "Budi"          # atribut objek
tulis akun.nama               # Budi

buat cache = [kosong, kosong]
cache[0] ??= 42               # index list
tulis cache                   # [42, kosong]

# Short-circuit: f() tidak dipanggil bila sudah terisi
buat hitung = [0]
fungsi f()
    hitung[0] = hitung[0] + 1
    kembali 5
selesai

buat terisi = 10
terisi ??= f()
tulis "hitung setelah ??= (terisi): " + teks(hitung[0])   # 0

buat kosong2 = kosong
kosong2 ??= f()
tulis "hitung setelah ??= (kosong): " + teks(hitung[0])   # 1

# ---------- 3. kecuali Multi-Tipe ----------
tulis "\n=== kecuali Multi-Tipe (A, B) ==="

coba
    buat hasil = 100 / 0
kecuali (TypeError, ZeroDivisionError) sebagai e
    tulis "tertangkap ZeroDivisionError"
selesai

kelas_error ValidasiGagal extends Kesalahan
    fungsi __init__(pesan)
        self.pesan = pesan
    selesai
selesai

coba
    lempar ValidasiGagal("email kosong")
kecuali (ValidasiGagal, KeyError) sebagai e
    tulis "tertangkap kelas_error kustom: " + e.pesan
selesai

coba
    buat arr = [1, 2]
    buat o = arr[10]
kecuali (IndexError, KeyError) sebagai e
    tulis "tertangkap IndexError"
selesai

tulis "\nSelesai! 🎉"
