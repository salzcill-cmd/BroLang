# Game Dev Upgrade v6.6 🎮

> Upgrade komprehensif library game: **2 modul baru** (`jalur`, `efek`) dan
> **8 modul ditingkatkan** (fisika, partikel, tilemap, kamera, game, grafis,
> ui, sprite).

```bash
pip install pygame-ce        # sekali saja — wajib untuk semua modul game
```

Contoh lengkap: `examples/game_v66.bro` — showcase semua fitur v6.6.

---

## 1. Pathfinding & Navigasi (`jalur`) 🆕

Modul baru untuk AI & navigasi: pathfinding A* di tilemap, mengikuti jalur,
dan patroli waypoint.

### A* Pathfinding

```bro
impor jalur

# Peta dari objek tilemap (punya is_solid) ATAU list 2D (0 = kosong)
buat denah = [[1, 1, 1, 1], [1, 0, 0, 1], [1, 0, 0, 1], [1, 1, 1, 1]]

buat rute = jalur.cari_jalur(denah, (1, 1), (2, 2))   # list tile, atau kosong
jika rute maka
    tulis jalur.panjang_jalur(rute)          # jumlah tile
    buat titik_pixel = jalur.jalur_ke_pixel(rute, 32)  # koordinat pixel
selesai
```

- `cari_jalur(peta, mulai, tujuan, diagonal=False)` — A*, terima objek
  tilemap (`peta.is_solid(tx, ty)`) atau list 2D
- `jalur_ke_pixel(jalur, ukuran_tile, tengah=True)` — tile → pixel (pusat tile)
- `panjang_jalur(jalur)` — jumlah tile (0 jika kosong)

### Mengikuti Jalur (`IkutiJalur`)

```bro
buat pengikut = jalur.IkutiJalur(titik_pixel, kecepatan=150, loop=False)
pengikut.on_selesai = fungsi_sampai_akhir
pengikut.update(dt)            # gerak menuju waypoint berikutnya
buat (px, py) = pengikut.posisi()
```

Metode: `posisi()`, `titik_sekarang()`, `sisa_jarak()`, `reset()`,
`tambah_titik(x, y)`. Callback: `on_selesai`, `on_titik(indeks)`.

### Patroli Waypoint (`Patroli`)

```bro
buat penjaga = jalur.Patroli([(100, 100), (500, 100), (500, 400)],
                             kecepatan=120, mode="bolak-balik")
penjaga.update(dt)
buat (gx, gy) = penjaga.posisi()
```

- `mode="loop"` (ulang), `"bolak-balik"` (ping-pong), `"sekali"` (berhenti)
- Metode: `posisi()`, `indeks_sekarang()`, `titik_tujuan()`, `reset()`
- Callback: `on_titik`, `on_selesai` (mode sekali)

---

## 2. Efek Layar (`efek`) 🆕

Efek visual instan: flash, vignette, teks melayang (damage number), pulsa.

### Flash — Kilatan Layar

```bro
impor efek
buat kilat = efek.buat_flash("putih", durasi=0.15, kekuatan=160)
kilat.update(dt)
kilat.gambar(screen)   # panggil TERAKHIR setelah scene digambar
```

Metode: `picu()` (nyalakan ulang), `aktif()`, `alpha()`.

### Vignette

```bro
buat vin = efek.Vignette(kekuatan=0.4)
vin.gambar(screen)     # tiap frame setelah scene digambar
vin.atur_kekuatan(0.6)
```

### Teks Melayang — Damage Number

```bro
buat dmg = efek.TeksMelayang("-25", musuh.x, musuh.y,
                             warna="merah", ukuran=28)
dmg.update(dt)
dmg.gambar(screen)
```

Metode: `selesai()`, `alpha()`. Atribut: `kecepatan_naik`, `durasi`,
`acak_x` (spread horizontal acak).

### Pulsa — Gelombang Cincin

```bro
buat gel = efek.Pulsa(400, 300, radius_akhir=100, durasi=0.5, warna="cyan")
gel.update(dt)
gel.gambar(screen)
```

---

## 3. Fisika — AABB & Raycast (`fisika`)

### Collider Persegi (AABB)

Bodi sekarang punya `mode_collider`: `"lingkaran"` (default) atau
`"persegi"`. Tabrakan campuran (lingkaran vs persegi) didukung.

```bro
impor fisika
buat kotak = fisika.buat_bodi(400, 300, massa=1).set_persegi(40, 40)
# posisi bodi = titik tengah; lebar/tinggi dipakai untuk tabrakan & bounds
```

- `set_persegi(lebar, tinggi)` — set ukuran + mode persegi
- `check_collision(a, b)` — otomatis deteksi mode (persegi/persegi,
  lingkaran/lingkaran, campuran)
- `resolve_collision(a, b)` — dorong sepanjang sumbu penetrasi terkecil
- `check_bounds(bodi, lebar, tinggi)` — pakai half-size sesuai mode

### Raycast

```bro
buat hasil = dunia.raycast(pemain.x, pemain.y, kursor_x, kursor_y)
jika hasil maka
    buat (bodi_kena, tx_hit, ty_hit) = hasil   # objek + titik tabrakan
selesai
```

### Query Area

```bro
buat musuh_dekat = dunia.cari_bodi_di_area(x, y, 100, 100)  # list bodi
buat bodi = dunia.bodi_di_posisi(mx, my)      # bodi di titik (support persegi)
```

---

## 4. Partikel — Gradien & Emiter Siap Pakai (`partikel`)

### Gradien Warna Seumur Hidup

```bro
buat api = partikel.buat_emiter(100, 500)
api.warna_awal = "kuning"
api.warna_akhir = "merah"     # warna berubah seiring umur partikel
api.gambar_tekstur = grafis.muat_gambar("assets/ember.png")  # atau path/Surface
```

### Emiter Bantu

```bro
buat jejak = partikel.buat_trail(400, 300, warna="cyan")   # jejak gerakan
buat asap   = partikel.buat_asap(100, 500)                  # naik & membesar
buat bintang = partikel.buat_bintang(200, 200, warna="emas") # percikan instan
```

---

## 5. Tilemap — Animasi & Layer Objek (`tilemap`)

### Tile Animasi

```bro
buat tileset = tilemap.buat_tileset("dunia", ukuran_tile=32)
tileset.atur_animasi(9, [9, 10, 11], kecepatan=0.2)  # air mengalir

# Tiap frame:
peta.update(dt)
peta.gambar(screen, cam.x, cam.y)   # frame animasi otomatis
```

### Layer Objek

```bro
peta.tambah_objek("spawn_pemain", 64, 64, tipe="spawn")
peta.tambah_objek("musuh", 300, 64, kecepatan=50)

buat spawn = peta.cari_objek("spawn_pemain")
buat semua_musuh = peta.cari_semua_objek("musuh")
peta.hapus_objek("musuh")       # hapus per nama, return jumlah terhapus
```

### Cek Lantai (Platformer)

```bro
jika peta.cek_lantai(pemain.x + 16, pemain.y + 40) maka
    # ada tile solid tepat di bawah kaki
selesai
```

---

## 6. Kamera — Parallax & Deadzone (`kamera`)

### Parallax Layers

```bro
buat cam = kamera.buat_kamera(800, 600)

# Di fungsi gambar — latar belakang dengan kecepatan berbeda:
buat (bx, by) = cam.screen_parallax(400, 300, 0.3)   # bukit belakang
grafis.gambar_gambar(latar_bukit, bx, by)
buat (px, py) = cam.screen_parallax(400, 300, 0.7)   # lapisan depan
```

Faktor: `1.0` = normal, `0.5` = setengah, `0.0` = statis, `2.0` = lebih cepat.

### Deadzone Follow

```bro
cam.set_target(pemain, deadzone=(120, 80))
# Kamera hanya bergerak saat pemain keluar dari area deadzone di tengah —
# gerakan jauh lebih stabil untuk game action.
cam.set_lerp(6.0)    # kekuatan smoothing follow
```

---

## 7. Game Loop — Fixed Timestep & Screenshot (`game`)

### Fixed Timestep Fisika

```bro
fungsi update_fisika(fdt)
    dunia.update(fdt)      # fdt SELALU 1/120 detik
selesai

game.atur_fisika(update_fisika, timestep=1/120)
# update_fisika dipanggil beberapa kali per frame sesuai akumulasi waktu —
# simulasi deterministik, tidak bergantung FPS rendering.
```

### Screenshot & Resize

```bro
game.tangkap_layar("foto.png")      # simpan screenshot layar
game.atur_ukuran_jendela(1280, 720) # ubah ukuran jendela
```

---

## 8. Grafis — Gradien & Glow (`grafis`)

```bro
# Gradien vertikal (langit) & horizontal
grafis.gradien_vertikal(0, 0, 800, 600, "langit", "biru_gelap")
grafis.gradien_horizontal(100, 400, 300, 50, "merah", "kuning")

# Glow
grafis.glow_lingkaran(400, 300, 40, "emas")

# Teks dengan perataan
grafis.tulis_teks("MENU", 400, 100, "putih", 40, tengah=True)
grafis.tulis_teks("KANAN", 800, 100, "putih", 24, kanan=True)

# Gambar dengan transparansi
grafis.gambar_gambar_alpha(logo, 100, 100, 128)
```

---

## 9. UI — Tooltip, Skor, Navigasi (`ui`)

### Tooltip

```bro
buat tip = ui.Tooltip("Klik untuk mulai!", warna="putih")

# Tiap frame:
tip.update(input.tikus_posisi()[0], input.tikus_posisi()[1],
           tombol.hover, dt)     # muncul setelah delay 0.4s hover
tip.gambar(screen)
```

### DaftarSkor — High Score Persisten

```bro
buat skor = ui.DaftarSkor("skor.json", maks_entri=10)
skor.tambah("Budi", 1200)            # otomatis simpan ke file
tulis skor.skor_tertinggi()          # 1200
tulis skor.peringkat("Budi")         # 0 (atau kosong jika tidak ada)
untuk entri dalam skor.tabel() lakukan   # [(nama, skor)] terurut turun
    tulis entri[0] + " - " + entri[1]
selesai
skor.bersihkan()
```

### Tombol Bergambar

```bro
buat mulai = ui.Tombol("MULAI", 300, 250, 200, 60,
                       gambar="assets/tombol.png")
```

### Navigasi Fokus Keyboard

```bro
# Saat panah/Enter ditekan di form:
buat baru = ui.navigasi_fokus(nama, "bawah", [nama, email, umur])
```

---

## 10. Sprite — Patroli & Utilitas (`sprite`)

```bro
# Patroli waypoint — sprite ikut bergerak
penjaga.ikuti_patroli([(400, 300), (700, 300), (700, 450)],
                      kecepatan=110, mode="bolak-balik")
jika penjaga.patroli_aktif() maka ... selesai
penjaga.berhenti_patroli()

# Putar menghadap titik
pemain.rotasi_ke_titik(musuh.x, musuh.y)

# Visibilitas
powerup.sembunyikan()
powerup.tampilkan()
```

---

## Bonus: Destructuring Tuple

Sintaks `buat (x, y) = fungsi()` yang selama ini ada di dokumentasi kini
benar-benar berfungsi (v6.6):

```bro
buat (mx, my) = input.tikus_posisi()
buat (gx, gy) = penjaga.posisi()
```
