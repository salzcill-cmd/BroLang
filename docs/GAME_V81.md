# Game Dev Upgrade v8.1 🎮

BroLang v8.1 menambah 6 fitur game development siap pakai:

1. **`kumpulan_objek`** — object pooling (hindari lag GC)
2. **`simpan_game`** — save/load progres game (slot, checkpoint, metadata)
3. **`dialog`** — sistem dialog RPG (mesin ketik + pilihan bercabang)
4. **`ai`** — AI musuh: FSM + steering behaviors
5. **`tilemap`** — platform satu arah & platform bergerak
6. **`misi`** — quest & achievement

Semua modul tersedia di interpreter, transpiler, dan VM (`impor <modul>`).

---

## 1. Object Pooling (`kumpulan_objek`) 🗃️

Pola industri game: **gunakan ulang** objek (bullet, partikel, damage
number) alih-alih membuat & membuang baru setiap frame — menghindari lag
akibat garbage collection.

```bro
impor kumpulan_objek

# Pool peluru: pabrik + reset state
buat pool = kumpulan_objek.KumpulanObjek(
    lalu() {"aktif": salah},      # pabrik objek
    ukuran_awal=20,               # pre-warm 20 objek
    aktifkan=lalu(o) o["aktif"] = benar,
    nonaktifkan=lalu(o) o["aktif"] = salah)

# Saat menembak:
buat peluru = pool.ambil()
peluru["x"] = pemain.x
peluru["aktif"] = benar

# Saat peluru keluar layar / kena target:
pool.kembalikan(peluru)

# Ganti scene — kembalikan semua sekaligus:
pool.kosongkan()
```

| Fungsi | Keterangan |
|--------|------------|
| `KumpulanObjek(buat, ukuran_awal?, aktifkan?, nonaktifkan?)` | Buat pool |
| `ambil(...)` | Pinjam objek (aktifkan dulu; buat baru bila kosong) |
| `kembalikan(obj)` | Kembalikan objek (nonaktifkan dulu) |
| `aktif()` / `jumlah_aktif()` / `jumlah_tersedia()` / `total()` | Status |
| `kosongkan()` | Kembalikan semua objek aktif |
| `hapus_semua()` | Buang semua objek |
| `buat_pool_flag(n)` | Pool ringan: dict `{"aktif": False}` |

> v8.1 juga memperbaiki VM: fungsi/lambda BroLang kini bisa dikirim sebagai
> **callback ke kode Python stdlib** (`VMFunction.__call__`) — diperlukan
> untuk `KumpulanObjek` dengan pabrik `lalu() ...`.

---

## 2. Simpan/Muat Game (`simpan_game`) 💾

Simpan progres game ke disk (JSON): slot save, checkpoint/auto-save, dan
metadata (waktu simpan, label, versi).

```bro
impor simpan_game

# Simpan ke slot (folder "tersimpan" dibuat otomatis)
simpan_game.simpan("slot1", {"level": 3, "nyawa": 5, "kunci": ["emas"]},
                   label="Level 3")

# Muat kembali (default bila belum ada)
buat data = simpan_game.muat("slot1", default={"level": 1})

# Checkpoint / auto-save di tengah permainan
simpan_game.checkpoint({"level": 4, "posisi": [100, 200]})

# Daftar semua save (terbaru dulu)
buat daftar = simpan_game.daftar()
untuk s dalam daftar lakukan
    tulis s["nama"] + " — " + s["label"]
selesai

# Metadata & pembersihan
buat info = simpan_game.info("slot1")       # {waktu, label, versi}
simpan_game.hapus("slot1")
simpan_game.bersihkan()                      # hapus semua
```

Data yang didukung: dict, list, angka, teks, bool, None. Kunci dict
dikonversi otomatis ke teks; tuple menjadi list (JSON).

---

## 3. Sistem Dialog (`dialog`) 💬

Kotak dialog RPG dengan **efek mesin ketik**, nama pembicara, dan
**pilihan bercabang**.

```bro
impor dialog

buat d = dialog.Dialog(
    ["Halo, pengembara!", "Selamat datang di desa kami."],
    nama_pembicara="Kepala Desa",
    kecepatan=40)                 # karakter per detik

# Tiap frame:
d.update(dt)                      # majukan mesin ketik
d.gambar(screen)                  # render (pygame)

# Saat pemain tekan tombol "lanjut":
buat habis = d.lanjut()
#  - masih mengetik  -> tampilkan baris penuh
#  - baris selesai   -> baris berikutnya
#  - baris terakhir  -> True (dialog selesai)

# Dialog bercabang:
buat d2 = dialog.Dialog(["Apa yang kamu cari?"], nama_pembicara="Penjaga")
d2.atur_pilihan(["Tempa pedang", "Belanja", "Keluar"])

# Navigasi pilihan (tombol atas/bawah):
d2.geser_pilihan(-1)              # atau +1

# Pemain memilih:
buat (teks, selesai) = d2.pilih(1)   # ("Belanja", selesai?)
```

| Fungsi | Keterangan |
|--------|------------|
| `Dialog(kalimat?, nama_pembicara?, kecepatan?, ukuran?, warna?, lebar?)` | Kotak dialog |
| `update(dt)` | Majukan efek mesin ketik |
| `lanjut()` | Selesaikan baris / maju; `True` bila dialog habis |
| `selesai_mengetik()` / `teks_terlihat()` / `tampilkan_semua()` | Kontrol typewriter |
| `atur_pilihan(list)` / `pilih(i)` / `pilihan_sekarang()` | Pilihan bercabang |
| `geser_pilihan(arah)` / `indeks_pilihan()` | Navigasi pilihan |
| `on_selesai(fungsi)` | Callback saat dialog selesai |
| `baris_sekarang()` / `indeks_baris()` / `jumlah_baris()` | Query |
| `reset()` / `tambah_baris(teks)` / `terlihat` | Utilitas |

---

## 4. AI Musuh: FSM + Steering (`ai`) 🤖

**Mesin status (FSM)** untuk perilaku musuh + **steering behaviors**
murni matematika (kejar, lari, tiba, jelajah, hindari) — tanpa
dependensi pygame, mudah diuji & dipakai dengan sprite/fisika apa pun.

```bro
impor ai

# --- FSM: penjaga yang mengejar pemain ---
fungsi update_jaga(dt, agen)
    jika agen.jarak_ke_pemain() < 120 maka
        mesin.ganti_status("kejar")
    selesai
selesai

fungsi update_kejar(dt, agen)
    buat (vx, vy) = ai.kejar(agen.x, agen.y, pemain.x, pemain.y, agen.kecepatan)
    agen.x += vx * dt
    agen.y += vy * dt
selesai

buat mesin = ai.FSM("jaga")
mesin.tambah_status("jaga", update=update_jaga)
mesin.tambah_status("kejar", masuk=fungsi() tulis "Mengejar!" selesai,
                             update=update_kejar)
# Tiap frame:
mesin.update(dt, agen)

# --- Steering langsung ---
buat (vx, vy) = ai.kejar(100, 100, 300, 300, 120)   # kejar penuh
buat (vx, vy) = ai.lari(100, 100, 300, 300, 120)    # lari menjauh
buat (vx, vy) = ai.tiba(100, 100, 300, 300, 120)    # tiba + melambat
buat (vx, vy, arah) = ai.jelajah(100, 100, arah, dt, 80)  # patroli acak

# --- Agen siap pakai ---
buat musuh = ai.Agen(100, 100, kecepatan_maks=120)
musuh.atur_target(pemain, mode="kejar")   # atau "lari"/"tiba"/"jelajah"
musuh.update(dt)
buat (x, y) = musuh.posisi()
```

| Fungsi | Keterangan |
|--------|------------|
| `FSM(awal?)` | Mesin status terbatas |
| `tambah_status(nama, masuk?, update?, keluar?)` | Daftarkan status + callback |
| `ganti_status(nama)` | Pindah status (keluar lama → masuk baru) |
| `update(dt, *args)` | Jalankan callback `update` status saat ini |
| `status_sekarang()` / `status_sebelumnya()` / `sudah_di(nama)` / `waktu_di_status()` | Query |
| `kejar(x, y, tx, ty, maks)` | Seek → `(vx, vy)` |
| `lari(x, y, tx, ty, maks)` | Flee → `(vx, vy)` |
| `tiba(..., radius?, radius_lambat?)` | Arrive (melambat mendekat, berhenti) |
| `jelajah(..., arah, dt, maks, ...)` | Wander → `(vx, vy, arah_baru)` |
| `hindari(x, y, rintangan, radius?)` | Dorong menjauh dari rintangan |
| `gabung(v1, v2, bobot?)` | Blending dua vektor steering |
| `Agen(x, y, kecepatan_maks?)` | Agen: posisi + mode steering + `update(dt)` |
| `jarak(...)` / `arah_ke(...)` | Utilitas vektor |

---

## 5. Tilemap Lanjutan — Platform Satu Arah & Bergerak (`tilemap`) 🧱

### Platform Satu Arah

Bisa dipijak saat **jatuh**, tapi **tembus saat melompat ke atas** —
esensial untuk platformer.

```bro
impor tilemap

buat tileset = tilemap.buat_tileset("ts", ukuran_tile=32)
tileset.atur_satu_arah(2)                 # tile id 2 = platform satu arah
buat peta = tilemap.buat_peta(20, 15, ukuran_tile=32)
peta.set_tileset(tileset)
peta.atur(5, 8, 2)                        # pasang platform satu arah

# Deteksi pijakan tiap frame (cek tile tepat di bawah kaki):
buat mendarat = peta.cek_lantai_satu_arah(pemain.x, pemain.y + pemain.tinggi,
                                          pemain.kecepatan_y)
jika mendarat maka
    pemain.kecepatan_y = 0
    pemain.y = peta.tile_ke_pixel(5, 8)[1] - pemain.tinggi
selesai
```

`cek_lantai_satu_arah(px, py, kecepatan_y)` otomatis mengembalikan `salah`
saat karakter melompat ke atas (`kecepatan_y < 0`) — tembus.

### Platform Bergerak

```bro
# Platform bolak-balik antara (0, 300) dan (320, 300)
buat plat = peta.tambah_platform_bergerak(0, 300, 320, 300,
                                          kecepatan=80, lebar=96, tinggi=16)

# Tiap frame:
peta.update(dt)          # platform bergerak otomatis bolak-balik

# Bawa pemain yang berdiri di atas platform:
peta.dorong_bodi(pemain, dt)
```

| Fungsi | Keterangan |
|--------|------------|
| `tileset.atur_satu_arah(id, satu_arah?)` | Tandai tile id sebagai satu arah |
| `peta.tandai_satu_arah(tx, ty)` / `cek_satu_arah(tx, ty)` | Tandai/cek manual per tile |
| `peta.cek_lantai_satu_arah(px, py, kecepatan_y)` | Pijakan satu arah (hanya saat jatuh) |
| `peta.tambah_platform_bergerak(x1, y1, x2, y2, kecepatan?, ...)` | Platform bolak-balik |
| `peta.dorong_bodi(bodi, dt)` | Bawa objek yang berdiri di atas platform |
| `PlatformBergerak` | Kelas platform (update, posisi, reset, aktif) |

---

## 6. Quest & Achievement (`misi`) 🏆

Quest dengan progres & status (aktif/selesai/gagal), achievement yang
terbuka, dan manajer untuk melacak semuanya — status bisa disimpan
(JSON-safe, cocok digabung dengan `simpan_game`).

```bro
impor misi

# Quest: kumpulkan 5 kunci
buat q = misi.Misi("cari_kunci", "Cari 5 Kunci",
                   deskripsi="Kumpulkan kunci di hutan gelap.", tujuan=5)
q.tambah_progres(2)      # 2/5 — False
q.tambah_progres(3)      # 5/5 — True (baru selesai)
q.status()               # "selesai"

# Achievement
buat a = misi.Pencapaian("pembunuh_pertama", "Pembunuh Pertama",
                         deskripsi="Kalahkan musuh pertamamu.")
a.buka_kunci()           # True (baru terbuka)

# Manajer — kelola banyak quest sekaligus
buat manajer = misi.ManajerMisi()
manajer.buat_misi("m1", "Misi 1", tujuan=3)
manajer.buat_pencapaian("a1", "Ach 1", tersembunyi=benar)
manajer.tambah_progres("m1", 3)
manajer.buka_pencapaian("a1")
manajer.selesai()        # quest yang selesai
manajer.aktif()          # quest yang masih jalan

# Simpan status (gabung dengan simpan_game):
simpan_game.simpan("quests", manajer.ke_dict())

# Muat:
buat manajer2 = misi.ManajerMisi()
manajer2.muat(simpan_game.muat("quests", default={}))
```

| Fungsi | Keterangan |
|--------|------------|
| `Misi(id, nama, deskripsi?, tujuan?, hadiah?)` | Satu quest |
| `tambah_progres(n?)` | Tambah progres; `True` bila baru selesai |
| `atur_progres(n)` / `progres()` / `sisa()` | Kontrol progres |
| `selesai()` / `gagal()` / `status()` | Status quest |
| `on_selesai` / `on_gagal` | Callback |
| `Pencapaian(id, nama, deskripsi?, tersembunyi?)` | Achievement |
| `buka_kunci()` / `terbuka()` / `on_buka` | Unlock achievement |
| `ManajerMisi()` | Kelola quest & achievement sekaligus |
| `buat_misi` / `tambah_misi` / `dapatkan(id)` / `semua()` / `aktif()` / `selesai()` / `gagal()` | Manajemen quest |
| `tambah_progres(id, n)` / `selesaikan(id)` / `gagalkan(id)` | Aksi quest |
| `buat_pencapaian` / `tambah_pencapaian` / `buka_pencapaian(id)` / `pencapaian_terbuka()` | Manajemen achievement |
| `ke_dict()` / `muat(data)` | Simpan & muat status |

---

## Catatan Konsistensi

- Semua modul v8.1 tersedia lewat `impor <modul>` di **interpreter,
  transpiler, dan VM** (output identik — diverifikasi test + audit).
- Modul `kumpulan_objek`, `simpan_game`, `dialog`, `ai`, `misi` murni
  logika — bisa diuji tanpa pygame.
- `tilemap` platform satu arah & bergerak melengkapi `cek_lantai` v6.6.

Contoh lengkap: `examples/fitur_v81.bro` · Tes: `tests/unit/test_v81_game.py`
