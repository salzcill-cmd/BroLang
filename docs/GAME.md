# Game Development

> **Bikin game pake BroLang? Bisa banget!** BroLang punya 14 modul game
> lengkap: game loop, grafis, input, audio, sprite, animasi, fisika, tilemap,
> kamera, partikel, UI, vektor, dan waktu.

```bash
pip install pygame-ce        # sekali saja — wajib untuk semua modul game
```

---

## 1. Game Loop (`game`)

### Window Dasar

```bro
impor game
impor grafis

game.buat_jendela(800, 600, "Game Pertamaku")
game.set_latar_warna("biru_gelap")     # warna latar (nama / (r,g,b))
game.atur_fps(60)
game.set_tampil_fps(True)              # tampilkan FPS di pojok

fungsi update_main(dt)
    # logika game tiap frame
selesai

fungsi gambar_main(screen)
    grafis.segi_panjang(400, 300, 50, 50, "merah")
selesai

game.tambah_scene("utama", update_main, gambar_main)
game.ganti_scene("utama")
game.mulai()   # block sampai game ditutup
```

### Scene Management

```bro
game.tambah_scene("menu", update_menu, gambar_menu)
game.tambah_scene("main", update_main, gambar_main)
game.ganti_scene("main")               # pindah scene
game.dapatkan_scene_sekarang()         # nama scene aktif
game.hapus_scene("menu")
```

### Scene Lifecycle (v6.2) 🆕

Scene punya siklus hidup lengkap: callback `on_masuk` dipanggil sekali saat
scene aktif, `on_keluar` saat scene diganti. Cocok untuk setup/cleanup
(muat asset, reset skor, dll).

```bro
game.tambah_scene("main", update_main, gambar_main,
                   on_masuk=mulai_main, on_keluar=bersihkan_main)
```

### Transisi Antar Scene (v6.2) 🆕

Pindah scene dengan efek fade — scene lama memudar ke warna, lalu scene baru
muncul. `transisi="fade"`, `durasi` dalam detik, `warna` overlay (nama warna
atau tuple RGB).

```bro
game.ganti_scene("main", transisi="fade", durasi=1.0, warna="hitam")
game.ganti_scene("menu", transisi="fade", durasi=0.5, warna="putih")
```

- `game.transisi_aktif()` → cek apakah sedang transisi
- `game.progres_transisi()` → progres 0.0..1.0 (buat animasi paralel)

### Tumpukan Scene / Overlay (v6.2) 🆕

Tumpuk scene di atas scene lain — scene bawah **tetap digambar** tapi tidak
di-update. Sempurna untuk menu pause / dialog di atas gameplay.

```bro
game.dorong_scene("pause", transisi="fade")   # pause di atas scene utama
game.pop_scene(transisi="fade")               # kembali ke scene bawah
```

- `game.kedalaman_tumpukan()` → jumlah scene yang sedang ditumpuk

### Pause & Data Global

```bro
game.pause()          # pause game (loop tetap jalan)
game.resume()         # lanjutkan
game.sedang_pause()   # cek status

game.atur_data("skor", 0)              # simpan data global
game.dapatkan_data()["skor"] += 10
```

| Fungsi | Keterangan |
|--------|------------|
| `buat_jendela(lebar, tinggi, judul?)` | Buat window game |
| `mulai()` / `berhenti()` | Jalankan / hentikan game loop |
| `tambah_scene(nama, update?, gambar?)` | Daftarkan scene |
| `ganti_scene(nama)` / `hapus_scene(nama)` | Pindah / hapus scene |
| `pause()` / `resume()` / `sedang_pause()` | Pause / resume |
| `dapatkan_data()` / `atur_data(kunci, nilai)` | Data global game |
| `atur_fps(fps)` / `dapatkan_fps()` | Target & FPS aktual |
| `set_latar_warna(warna)` | Warna latar layar |
| `set_tampil_fps(True)` | Tampilkan FPS di pojok |
| `set_esc_keluar(True/False)` | ESC menutup game (default True) |
| `reset()` | Reset semua scene/data/pause |

> Catatan: `dt` yang masuk ke fungsi update sudah **di-clamp maks 0.05s**
> supaya fisika tidak meledak saat jendela tidak fokus.

---

## 2. Grafis (`grafis`)

Wrapper lengkap Pygame untuk rendering 2D. **Window bisa dibuat lewat
`game.buat_jendela()`** — `grafis` otomatis memakai display yang aktif.

### Bentuk Dasar

```bro
impor grafis

grafis.bersihkan("hitam")
grafis.segi_panjang(100, 100, 50, 50, "biru")
grafis.segi_panjang_bulat(200, 100, 100, 50, 15, "ungu")
grafis.lingkaran(400, 300, 40, "kuning")
grafis.lingkaran_garis(400, 300, 45, "putih", 2)
grafis.garis(0, 0, 800, 600, "hijau", 3)
grafis.segitiga(100, 400, 200, 300, 300, 400, "jingga")
grafis.poligon([(400, 400), (500, 350), (600, 400), (550, 500)], "cyan")
grafis.elips(50, 50, 120, 60, "merah")
grafis.titik(10, 10, "putih", 3)
grafis.busur(400, 100, 60, 0, 180, "cyan", 4)
grafis.perbarui()   # flip layar
```

### Teks

```bro
grafis.tulis_teks("Skor: 100", 10, 10, "kuning", 32)
grafis.tulis_teks_multi("Baris 1\nBaris 2\nBaris 3", 50, 200, "putih", 24)
grafis.dapatkan_ukuran_teks("Halo", 24)   # -> (lebar, tinggi)
```

### Gambar & Surface

```bro
buat img = grafis.muat_gambar("assets/player.png")
grafis.gambar_gambar(img, 100, 200)
grafis.gambar_gambar_putar(img, 400, 300, 45)      # rotasi derajat
grafis.gambar_gambar_scala(img, 100, 300, 2.0, 2.0) # skala

# Surface offscreen (canvas)
buat canvas = grafis.buat_surface(200, 100)
grafis.gambar_surface(canvas, 100, 100)
```

### Deteksi Tabrakan

```bro
grafis.tabrakan_segi_panjang(px, py, 32, 32, ex, ey, 32, 32)
grafis.tabrakan_lingkaran(x1, y1, r1, x2, y2, r2)
grafis.tabrakan_titik_segi_panjang(mx, my, rx, ry, rw, rh)
```

---

## 3. Input (`input`)

**Modul input adalah satu-satunya pemilik event queue** — game loop membacanya
lewat `game.mulai()` secara otomatis. Kamu tinggal baca state-nya.

### Keyboard

```bro
impor input

jika input.tombol_baru_ditekan("SPACE") maka   # baru ditekan (sekali)
    tulis "Lompat!"
selesai

jika input.tombol_ditekan("UP") maka           # sedang ditahan
    pemain.kecepatan_y = -200
selesai

input.tombol_dilepas("SPACE")                  # baru dilepas
input.tombol_apa_saja_baru()                   # nama tombol (atau None)
```

### Mouse & Scroll

```bro
buat (mx, my) = input.tikus_posisi()
buat (dx, dy) = input.tikus_gerakan()
input.tikus_tombol_ditekan(0)                  # tombol kiri ditahan
input.tikus_baru_ditekan(0)                    # klik kiri baru (sekali)
input.tikus_dilepas(0)
buat (sx, sy) = input.geser()                  # scroll wheel
input.tikus_set_posisi(400, 300)
input.tikus_tampil(False)                      # sembunyikan kursor
```

### Gamepad

```bro
jika input.gamepad_ada() maka
    buat vx = input.gamepad_sumbu(0, 0)        # -1..1 sumbu kiri
    buat vy = input.gamepad_sumbu(0, 1)
    jika input.gamepad_tombol_baru(0, 0) maka  # tombol A baru ditekan
        tulis "Tombol A!"
    selesai
selesai
```

---

## 4. Sprite (`sprite`)

Sprite dengan gambar, sprite sheet, animasi frame, rotasi, skala, alpha,
collider, dan z-order.

```bro
impor sprite

# Sprite dari gambar
buat pemain = sprite.Sprite("assets/player.png", 100, 100)
pemain.tambah_animasi("jalan", [0, 1, 2, 3], kecepatan=0.1)  # grid sprite sheet
pemain.mainkan_animasi("jalan")

# Sprite tanpa gambar (kotak berwarna)
buat musuh = sprite.Sprite(None, 400, 100, lebar=40, tinggi=40)
musuh.warna = "merah"

# Setiap frame:
pemain.update(dt)
pemain.gambar(screen)

# Atribut sprite
pemain.kecepatan_x = 150
pemain.gravitasi = 300
pemain.sudut = 45        # derajat
pemain.alpha = 128       # transparansi
pemain.flip_x = True
pemain.z = 5             # urutan gambar
pemain.batasan = (lebar_layar, tinggi_layar)   # clamp di dalam area

# Collision
jika pemain.cek_tabrakan(musuh) maka
    tulis "Tabrakan!"
selesai
pemain.cek_tabrakan_lingkaran(musuh)   # mode lingkaran
pemain.cek_titik(mx, my)               # titik di dalam sprite
```

### Grup Sprite

```bro
buat grup = sprite.GrupSprite()
grup.tambah(pemain, musuh)
grup.update(dt)                  # update semua
grup.gambar(screen)              # gambar semua (urut z)
grup.cek_tabrakan(pemain)        # list sprite yang bertabrakan
grup.hapus_tidak_aktif()         # buang sprite mati
```

---

## 5. Animasi (`animasi`)

Animasi frame + **tween dengan 26 jenis easing** (linear, ease_in/out,
back, elastic, bounce, sine, expo, dll).

```bro
impor animasi

# Animasi frame
buat anim = animasi.Animasi()
anim.tambah("lari", [0, 1, 2, 3], fps=10, loop=True)
anim.tambah("lompat", [4, 5, 6], fps=8, loop=False)
anim.mainkan("lompat")
anim.on_selesai = fungsi_saat_selesai   # callback non-loop
anim.update(dt)
anim.frame_sekarang()

# Tween: ubah nilai secara gradual
buat tween = animasi.buat_tween(0, 100, durasi=1.0, easing="ease_out_back")
tween.berulang = True
tween.on_siklus = fungsi_per_siklus
buat nilai = tween.update(dt)

# Sequence: tween berurutan
buat seq = animasi.buat_sequence()
seq.tambah_tween(0, 100, 0.5, "ease_out")
seq.tambah_tween(100, 0, 0.5, "ease_in")
seq.update(dt)

animasi.daftar_easing()   # daftar semua easing
```

---

## 6. Fisika (`fisika`)

Simulasi fisika: bodi dengan massa, gravitasi, tabrakan lingkaran,
dan batas layar.

```bro
impor fisika

buat dunia = fisika.buat_dunia(gravitasi_y=490)
buat bola = fisika.buat_bodi(400, 100, massa=5, radius=20)

dunia.tambah_bodi(bola)
dunia.set_gravitasi(0, 300)   # ubah gravitasi kapan saja

# Setiap frame:
dunia.update(dt)
dunia.check_bounds(bola, 800, 600, bounce=True)
dunia.resolve_collision(bola, bola2)
dunia.bodi_di_posisi(mx, my)   # cari bodi yang disentuh mouse

bola.tambah_gaya(0, -500)      # dorongan ke atas (lompat)
bola.apply_impulse(100, 0)     # impulse instan
bola.grounded                  # True saat menyentuh lantai
```

---

## 7. Tilemap (`tilemap`)

Peta tile 2D dari array, string, atau file — dengan deteksi tabrakan
dan rendering (gambar tileset **atau warna fallback**).

```bro
impor tilemap

buat tileset = tilemap.buat_tileset("aset", ukuran_tile=32)
tileset.atur_solid(1, benar)              # tile 1 = dinding
tileset.atur_warna(1, "coklat")           # warna fallback
tileset.atur_warna(2, "hijau")            # rumput

# Catatan: variabel tidak boleh bernama 'peta' (keyword BroLang),
# pakai nama lain seperti 'lantai' atau 'tile_peta'.
buat tile_peta = tilemap.buat_peta(20, 15, 32)
tile_peta.set_tileset(tileset)
tile_peta.dari_array([
    [1, 1, 1, 1, 1],
    [1, 0, 0, 0, 1],
    [1, 0, 2, 0, 1],
    [1, 1, 1, 1, 1],
])
# atau dari file:
# tile_peta.dari_file("level1.txt")
# atau langsung: buat peta2 = tilemap.dari_file("level1.txt")

tile_peta.is_solid(0, 0)                  # benar
tile_peta.check_collision(px, py, 32, 32) # tabrakan pixel
tile_peta.atur(x, y, tile_id)
tile_peta.gambar(screen, kamera_x, kamera_y)
tile_peta.simpan_file("level1.txt")
```

---

## 8. Kamera (`kamera`)

Kamera 2D dengan follow-target, smoothing, zoom, screen shake, dan bounds.

```bro
impor kamera

buat cam = kamera.buat_kamera(800, 600)
cam.set_target(pemain)          # ikuti objek
cam.set_zoom(1.5)
cam.set_batas_world(2000, 1500) # batas otomatis
cam.update(dt)

cam.shake(8, 0.3)               # screen shake
cam.gerak(10, 0)                # pan manual
cam.set_posisi(100, 100)
cam.reset()

# Konversi koordinat
buat (sx, sy) = cam.world_to_screen(wx, wy)
buat (wx, wy) = cam.screen_to_world(sx, sy)
cam.apply(x, y)                 # dengan rotasi (cam.set_sudut(deg))
cam.is_visible(x, y, lebar, tinggi)

# Varian
buat top = kamera.buat_top_down(800, 600)
buat side = kamera.buat_side_scroll(800, 600)
```

---

## 9. Partikel (`partikel`)

Sistem partikel untuk efek: ledakan, asap, hujan, semburan.

```bro
impor partikel

# Ledakan instan di posisi musuh mati
buat ledakan = partikel.buat_ledakan(400, 300, jumlah=40, warna="jingga", kecepatan=250)
ledakan.update(dt)
ledakan.gambar(screen)

# Emiter terus-menerus (api / asap)
buat api = partikel.buat_emiter(100, 500)
api.emisi_per_detik = 30
api.kecepatan = 50
api.umur = 1.2
api.warna = "kuning"
api.gravitasi = -50            # naik ke atas
api.update(dt)
api.gambar(screen)

# Hujan
buat hujan = partikel.buat_hujan(800, jumlah=60, warna="biru")
```

| Atribut emiter | Keterangan |
|----------------|------------|
| `jumlah` | Partikel per emisi / ledakan |
| `kecepatan`, `kecepatan_bervariasi` | Kecepatan awal & acak |
| `umur`, `umur_bervariasi` | Umur partikel |
| `ukuran`, `ukuran_bervariasi` | Ukuran partikel |
| `warna` | Warna partikel |
| `gravitasi`, `gesekan` | Fisika partikel |
| `sudut_mulai`, `sudut_rentang` | Arah emisi (derajat) |
| `emisi_per_detik` | Emisi otomatis per detik |

---

## 10. UI (`ui`)

Komponen antarmuka: Tombol, Label, Panel, Bar (health/progress), plus
komponen baru v6.2: **KotakTeks** (input teks), **Slider**, **KotakCentang**
(checkbox), dan **DaftarPilih** (dropdown).

```bro
impor ui
impor input

buat tombol_mulai = ui.Tombol("MULAI", 300, 250, 200, 60)
tombol_mulai.on_klik = fungsi_mulai

buat hp = ui.Bar(100, 100, 20, 20, 200, 20, warna_isi="hijau", warna_latar="merah_gelap")
buat judul = ui.Label("PETUALANGAN", 400, 100, warna="emas", ukuran=40, tengah=True)
buat panel = ui.Panel(280, 230, 240, 100, warna="abu-abu_gelap", radius=12)

# Setiap frame:
jika tombol_mulai.update(input.tikus_posisi()[0], input.tikus_posisi()[1],
                         input.tikus_baru_ditekan(0)) maka
    tulis "Game dimulai!"
selesai
hp.kurang(10)          # kena serangan

# Di fungsi gambar:
judul.gambar(screen)
panel.gambar(screen)
tombol_mulai.gambar(screen)
hp.gambar(screen)
```

### KotakTeks — Input Teks (v6.2) 🆕

Input teks satu baris dengan fokus (klik), kursor berkedip, placeholder,
dan batas panjang karakter. Input keyboard dilakukan manual di kode game
melalui `input.events_tombol()`.

```bro
buat nama = ui.KotakTeks(200, 150, 250, 40, placeholder="Nama pemain",
                         maks_karakter=12)

# Setiap frame:
nama.update(input.tikus_posisi()[0], input.tikus_posisi()[1],
            input.tikus_baru_ditekan(0))

jika nama.fokus maka
    untuk ev dalam input.events_tombol() lakukan
        nama.tambah_karakter(ev)          # terima karakter yang diketik
    selesai
    jika input.tombol_baru_ditekan("BACKSPACE") maka
        nama.hapus_karakter()
    selesai
selesai

nama.gambar(screen)
tulis nama.teks_sekarang()
```

Metode: `tambah_karakter(c)`, `hapus_karakter()` (backspace), `kosongkan()`,
`set_teks(t)`, `teks_sekarang()`, `habis()`/`apakah_kosong()`,
`fokus_set(True/False)`, `enter()` (pemicu tombol Enter). Callback:
`on_ubah`, `on_enter`, `on_fokus`, `on_keluar_fokus`.

### Slider (v6.2) 🆕

Slider horizontal — geser nilai dengan drag mouse. Cocok untuk volume,
kecerahan, kecepatan, dll.

```bro
buat volume = ui.Slider(200, 300, 250, nilai=50, min=0, maks=100,
                        langkah=5)          # langkah opsional (kelipatan)

# Setiap frame:
volume.update(input.tikus_posisi()[0], input.tikus_posisi()[1],
              input.tikus_tekanan()[0])    # true selama tombol kiri ditekan

audio.atur_volume_musik(volume.nilai_sekarang() / 100)
volume.gambar(screen)
```

Metode: `nilai_sekarang()`, `atur_nilai(v)`, `persen()` (0.0..1.0),
`atur_dari_posisi(x)`. Callback: `on_ubah`, `on_selesai` (saat drag selesai).

### KotakCentang — Checkbox (v6.2) 🆕

Checkbox dengan label — toggle saat diklik.

```bro
buat musik = ui.KotakCentang(200, 400, label="Aktifkan musik",
                             dicentang=True)

# Setiap frame:
musik.update(input.tikus_posisi()[0], input.tikus_posisi()[1],
             input.tikus_baru_ditekan(0))

jika musik.dicentang_sekarang() maka
    audio.mainkan_musik()
selesai
musik.gambar(screen)
```

Metode: `centang()`, `hapus_centang()`, `toggle()`, `dicentang_sekarang()`.
Callback: `on_ubah`, `on_centang`, `on_hapus`.

### DaftarPilih — Dropdown (v6.2) 🆕

Dropdown untuk memilih satu opsi dari daftar.

```bro
buat level = ui.DaftarPilih(200, 500, 200,
                            opsi=["Mudah", "Sedang", "Sulit"],
                            terpilih=1)     # default "Sedang"

# Setiap frame:
level.update(input.tikus_posisi()[0], input.tikus_posisi()[1],
             input.tikus_baru_ditekan(0))

tulis level.opsi_terpilih()   # nama opsi aktif
level.gambar(screen)
```

Metode: `buka()`, `tutup()`, `pilih(indeks)`, `indeks_terpilih()`,
`opsi_terpilih()`, `jumlah_opsi()`. Callback: `on_ubah`, `on_buka`, `on_tutup`.

---

## 11. Vektor (`vektor`)

Vektor 2D/3D untuk gerakan dan fisika.

```bro
impor vektor

buat posisi = vektor.Vec2(100, 200)
buat kecepatan = vektor.Vec2(150, 0)
posisi = posisi + kecepatan * dt

# Helper baru v6
buat v = vektor.Vec2.dari_polar(10, 45)   # panjang 10, arah 45 derajat
buat v2 = vektor.buat_polar(10, 90)
v.sudut()                 # sudut derajat
v.rotasi(90)              # rotasi derajat
v.proyeksi(lain)          # proyeksi ke vektor lain
v.refleksi(normal)        # pantulan (bouncing)
v.arah_ke(titik)          # vektor satuan menuju titik
v.tengah(lain)            # titik tengah
v.clamp_panjang(100)      # batasi kecepatan maks
```

---

## 12. Waktu (`waktu`)

Timer, stopwatch, FPS counter, dan fungsi waktu.

```bro
impor waktu

# Timer hitung mundur
buat timer = waktu.buat_timer(3.0)
timer.update(dt)
jika timer.habis() maka
    tulis "Waktu habis!"
selesai

# Stopwatch
buat sw = waktu.buat_stopwatch()
sw.mulai()
sw.elapsed()

# FPS counter
buat fps = waktu.buat_fps()
fps.update(dt)
fps.fps()

buat dt = waktu.delta()   # delta otomatis antar panggilan
```

---

## 13. Audio (`audio`)

```bro
impor audio

audio.muat_musik("assets/bgm.ogg")
audio.mainkan_musik(loops=-1)     # loop terus
audio.atur_volume_musik(0.5)

buat suara_lompat = audio.muat_suara("assets/jump.wav")
audio.mainkan_suara(suara_lompat)
```

---

## Contoh Game Lengkap

Lihat `examples/game_arena.bro` — game arena lengkap yang memakai hampir
semua modul di atas: sprite, fisika, partikel ledakan, UI health bar,
kamera shake, timer, FPS, dan input keyboard.

```bash
bro examples/game_arena.bro
```
