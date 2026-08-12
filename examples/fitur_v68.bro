# ============================================================
# BroLang v6.8 — Fitur Bahasa Baru
# -------------------------------------------
# 1. Guard clause      : kembali x jika c, hentikan/lanjutkan jika c
# 2. Floor division    : 17 // 5, x //= 3
# 3. Augmented atribut : self.x += 1, data[i] += 10
# 4. BGM prosedural    : audio.buat_bgm(...) / mainkan_bgm
#
# Jalankan:  bro examples/fitur_v68.bro
# ============================================================

# ---------- 1. Guard clause ----------
fungsi cek(x)
    kembali "negatif" jika x < 0
    kembali "nol" jika x == 0
    kembali "positif"
selesai

tulis "cek(-5, 0, 7)        =", cek(-5), cek(0), cek(7)   # negatif nol positif

# Guard di dalam loop: lanjutkan/hentikan bersyarat
buat total = 0
untuk i dari 1 sampai 10 lakukan
    lanjutkan jika i % 2 == 0      # skip angka genap
    hentikan jika i > 5            # berhenti setelah 5
    total = total + i
selesai
tulis "jumlah ganjil s/d 5   =", total                     # 1 + 3 + 5 = 9

# Early return dari dalam loop
fungsi cari(daftar, target)
    untuk setiap nilai dalam daftar lakukan
        kembali nilai jika nilai == target
    selesai
    kembali -1
selesai
tulis "cari 9 / 100          =", cari([1, 5, 9], 9), cari([1, 5, 9], 100)  # 9 -1

# ---------- 2. Floor division ----------
tulis "17 // 5               =", 17 // 5                   # 3
tulis "-17 // 5              =", -17 // 5                  # -4
tulis "17.5 // 5             =", 17.5 // 5                 # 3.0

buat skor = 10
skor //= 3
tulis "skor //= 3            =", skor                      # 3

# ---------- 3. Augmented pada atribut & index ----------
kelas Akun
    fungsi __init__(self)
        self.total = 0
    selesai
    fungsi naik(self, n)
        self.total += n            # atribut objek
        self.total *= 2
        kembali self.total
    selesai
selesai

buat ak = Akun()
tulis "ak.naik(5)             =", ak.naik(5)               # 10

buat data = [1, 2, 3]
data[1] += 10                        # index list
tulis "data[1] += 10          =", data                     # [1, 12, 3]

buat skor_pemain = [0, 0, 0]
untuk i dari 0 sampai 2 lakukan
    skor_pemain[i] += 10             # augmented di dalam loop
selesai
tulis "skor_pemain            =", skor_pemain              # [10, 10, 10]

# ---------- 4. BGM prosedural (audio) ----------
impor audio

# Buat WAV musik latar dari pola nada (nama not / frekuensi / jeda 0)
buat bgm = audio.buat_bgm(audio.pola_arcade, tempo=120)
audio.simpan_wav(bgm, "bgm_arcade.wav")
tulis "bgm_arcade.wav dibuat! (", panjang(bgm), "bytes )"

# Pola custom: nama not + durasi tuple + jeda
buat melodi = audio.buat_bgm(
    [("C4", 1), ("E4", 1), ("G4", 1), 0, ("A4", 2), ("G4", 1), ("E4", 1), ("C4", 2)],
    tempo=100, gelombang="segitiga", volume=0.5,
)
audio.simpan_wav(melodi, "bgm_melodi.wav")

# Konversi nama not -> frekuensi Hz
tulis "C4 =", audio.frekuensi_nada("C4"), "Hz | A4 =", audio.frekuensi_nada("A4"), "Hz"

# Putar langsung sebagai musik loop (butuh pygame: pip install pygame-ce)
# audio.mainkan_bgm(audio.pola_epik, 120)
# audio.hentikan_bgm()
