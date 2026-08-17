# ============================================================
#  BroLang v8.1 — Game Dev Upgrade 🎮
#  Object Pooling · Save/Load · Dialog · AI · Tilemap · Quest
# ============================================================

impor kumpulan_objek
impor simpan_game
impor dialog
impor ai
impor tilemap
impor misi

tulis "============================================="
tulis "  BroLang v8.1 — Game Dev Upgrade"
tulis "============================================="

# ============ 1. Object Pooling ============
tulis ""
tulis "=== Object Pooling (kumpulan_objek) ==="

fungsi aktifkan_peluru(o, x, y)
    o["aktif"] = benar
    o["x"] = x
    o["y"] = y
selesai

fungsi nonaktifkan_peluru(o)
    o["aktif"] = salah
selesai

buat pool = kumpulan_objek.KumpulanObjek(
    lalu() {"aktif": salah, "x": 0, "y": 0},
    ukuran_awal=5,
    aktifkan=aktifkan_peluru,
    nonaktifkan=nonaktifkan_peluru)

buat p1 = pool.ambil(100, 200)
buat p2 = pool.ambil(300, 400)
tulis "aktif: " + teks(pool.jumlah_aktif()) + ", tersedia: " + teks(pool.jumlah_tersedia())
pool.kembalikan(p1)
buat p3 = pool.ambil(500, 600)
tulis "ambil ulang objek yang sama: " + teks(p3 is p1)
pool.kosongkan()
tulis "setelah kosongkan -> aktif: " + teks(pool.jumlah_aktif())

# ============ 2. Simpan/Muat Game ============
tulis ""
tulis "=== Simpan/Muat Game (simpan_game) ==="

buat progres = {"level": 3, "nyawa": 5, "kunci": ["emas", "perak"], "posisi": [120, 340]}
simpan_game.simpan("slot1", progres, label="Level 3")
buat muat = simpan_game.muat("slot1", default={"level": 1})
tulis "level tersimpan: " + teks(muat["level"]) + ", kunci: " + teks(panjang(muat["kunci"]))
buat info = simpan_game.info("slot1")
tulis "label: " + info["label"]
simpan_game.hapus("slot1")
tulis "save dihapus, ada? " + teks(simpan_game.ada("slot1"))

# ============ 3. Dialog ============
tulis ""
tulis "=== Dialog (dialog) ==="

buat d = dialog.Dialog(
    ["Halo, pengembara!", "Selamat datang di desa kami.", "Hati-hati di hutan!"],
    nama_pembicara="Kepala Desa",
    kecepatan=50)
d.tampilkan_semua()
tulis d.nama_pembicara + ": " + d.baris_sekarang()
buat habis = salah
untuk i dalam range(6) lakukan
    habis = d.lanjut()
selesai
tulis "dialog selesai: " + teks(habis)

buat d2 = dialog.Dialog(["Apa yang kamu cari?"])
d2.atur_pilihan(["Tempa pedang", "Belanja", "Keluar"])
buat (pilihan, selesai2) = d2.pilih(0)
tulis "pemain memilih: " + pilihan

# ============ 4. AI ============
tulis ""
tulis "=== AI Musuh (ai) ==="

fungsi update_jaga(dt)
    tulis "  [jaga] tidak ada yang mencurigakan..."
selesai

fungsi masuk_kejar()
    tulis "  [kejar] Awas! Musuh mengejar!"
selesai

buat mesin = ai.FSM("jaga")
mesin.tambah_status("jaga", update=update_jaga)
mesin.tambah_status("kejar", masuk=masuk_kejar)
mesin.update(0.016)
mesin.ganti_status("kejar")
tulis "status sekarang: " + mesin.status_sekarang()

buat (vx, vy) = ai.kejar(100, 100, 300, 100, 120)
tulis "steering kejar: (" + teks(vx) + ", " + teks(vy) + ")"
buat (vx2, vy2) = ai.tiba(280, 100, 300, 100, 120, radius=10)
tulis "steering tiba (dekat target): (" + teks(vx2) + ", " + teks(vy2) + ")"

# ============ 5. Tilemap Lanjutan ============
tulis ""
tulis "=== Tilemap: Platform Satu Arah & Bergerak (tilemap) ==="

buat tileset = tilemap.buat_tileset("ts", ukuran_tile=32)
tileset.tambah_tile(1, solid=benar)
tileset.atur_satu_arah(2)
buat lantai = tilemap.buat_peta(12, 10, ukuran_tile=32)
lantai.set_tileset(tileset)
lantai.atur(5, 6, 2)

# Karakter jatuh -> mendarat di platform satu arah
buat jatuh = lantai.cek_lantai_satu_arah(5 * 32 + 16, 5 * 32 + 31, kecepatan_y=150)
tulis "jatuh -> mendarat: " + teks(jatuh)
# Karakter melompat ke atas -> tembus
buat lompat = lantai.cek_lantai_satu_arah(5 * 32 + 16, 5 * 32 + 31, kecepatan_y=-150)
tulis "lompat ke atas -> tembus: " + teks(lompat)

buat plat = lantai.tambah_platform_bergerak(0, 300, 320, 300, kecepatan=80)
lantai.update(1.0)
tulis "platform bergerak setelah 1 dtk: x=" + teks(plat.x)
lantai.update(4.1)
tulis "platform sampai ujung lalu berbalik: x=" + teks(plat.x) + " (< 320: " + teks(plat.x < 320) + ")"

# ============ 6. Quest & Achievement ============
tulis ""
tulis "=== Quest & Achievement (misi) ==="

buat manajer = misi.ManajerMisi()
manajer.buat_misi("kalahkan_bos", "Kalahkan Bos", tujuan=3)
manajer.buat_pencapaian("pembunuh", "Pembunuh Pertama")

manajer.tambah_progres("kalahkan_bos", 1)
tulis "progres bos: " + teks(manajer.dapatkan("kalahkan_bos").progres()) + "/3"
manajer.tambah_progres("kalahkan_bos", 2)
tulis "quest selesai: " + teks(manajer.dapatkan("kalahkan_bos").selesai())
tulis "achievement terbuka: " + teks(manajer.buka_pencapaian("pembunuh"))

# Simpan status quest (gabung dengan simpan_game)
simpan_game.simpan("quests", manajer.ke_dict())
buat manajer2 = misi.ManajerMisi()
manajer2.muat(simpan_game.muat("quests", default={}))
tulis "status quest termuat: " + manajer2.dapatkan("kalahkan_bos").status()
simpan_game.hapus("quests")

tulis ""
tulis "Selesai! 🎮"
