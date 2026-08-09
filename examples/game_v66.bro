# Contoh Game: Showcase v6.6 — Upgrade Library Game
# ==================================================
# Fitur baru yang ditunjukkan:
#   jalur (A* pathfinding + Patroli) · efek (Flash, TeksMelayang, Pulsa)
#   fisika (bodi persegi/AABB + raycast) · partikel (trail, asap)
#   tilemap (tile animasi + layer objek) · kamera (parallax + deadzone)
#   game (atur_fisika fixed-timestep, tangkap_layar) · grafis (gradien)
#   ui (Tooltip, DaftarSkor) · sprite (ikuti_patroli, rotasi_ke_titik)
#
# Kontrol:  klik kiri = bidik & tembak  ·  P = foto layar (screenshot)
#           ESC keluar  ·  mouse = kontrol kursor

impor game
impor grafis
impor input
impor sprite
impor partikel
impor efek
impor fisika
impor tilemap
impor kamera
impor jalur
impor ui
impor acak
impor waktu

buat lebar_layar = 960
buat tinggi_layar = 600

game.buat_jendela(lebar_layar, tinggi_layar, "BroLang v6.6 — Showcase")
game.atur_fps(60)
game.set_esc_keluar(benar)

# ===== Dunia Fisika (fixed timestep via game.atur_fisika) =====
buat dunia = fisika.buat_dunia(gravitasi_y=900)
buat pemain = sprite.Sprite(kosong, 100, 100, lebar=34, tinggi=44)
pemain.warna = "langit"
buat bodi_pemain = fisika.buat_bodi(100, 100, massa=1).set_persegi(30, 40)
bodi_pemain.gesekan = 0.85
dunia.tambah_bodi(bodi_pemain)

# Patroli musuh: sprite ikut bergerak antar waypoint (bolak-balik)
buat musuh = sprite.Sprite(kosong, 400, 300, lebar=36, tinggi=36)
musuh.warna = "merah"
musuh.ikuti_patroli([(400, 300), (700, 300), (700, 450), (400, 450)],
                    kecepatan=110, mode="bolak-balik")
buat bodi_musuh = fisika.buat_bodi(400, 300, massa=1).set_persegi(36, 36)
dunia.tambah_bodi(bodi_musuh)

# ===== Tilemap: lantai + dinding + tile air animasi + objek =====
buat tileset = tilemap.buat_tileset("arena", ukuran_tile=40)
tileset.atur_solid(1, benar)
tileset.atur_warna(1, "coklat")
tileset.atur_warna(2, "hijau_gelap")
tileset.atur_warna(3, "biru")
tileset.atur_animasi(9, [9, 10, 11], kecepatan=0.2)   # air mengalir
buat peta_tile = tilemap.buat_peta(24, 15, 40)
peta_tile.set_tileset(tileset)

buat i = 0
selama i < 24 lakukan
    peta_tile.atur(i, 14, 1)      # lantai
    peta_tile.atur(i, 13, 1)      # tebal
    i = i + 1
selesai
peta_tile.atur(5, 9, 1)           # dinding uji raycast
peta_tile.atur(5, 10, 1)
peta_tile.atur(5, 11, 1)
peta_tile.atur(5, 12, 1)
buat k = 3
selama k <= 8 lakukan
    peta_tile.atur(k, 11, 9)      # air animasi di atas lantai
    k = k + 1
selesai

# Layer objek: spawn point & item
peta_tile.tambah_objek("spawn_pemain", 100, 400, tipe="spawn")
peta_tile.tambah_objek("spawn_musuh", 400, 300, tipe="spawn")

# ===== Kamera: parallax + deadzone follow =====
buat cam = kamera.buat_kamera(lebar_layar, tinggi_layar)
cam.set_lerp(6.0)
cam.set_target(bodi_pemain, deadzone=(120, 80))
cam.set_batas_world(960, 640)

# ===== Efek & Partikel =====
buat kilat = efek.buat_flash("putih", durasi=0.12, kekuatan=160)
buat teks_damage = efek.TeksMelayang("", 0, 0, warna="kuning")
buat pulsa_klik = efek.Pulsa(0, 0, radius_akhir=60, durasi=0.4, warna="cyan")
buat api = partikel.buat_trail(0, 0, warna="jingga", umur=0.35)
buat asap = partikel.buat_asap(0, 0)
buat bintang = partikel.buat_bintang(0, 0, warna="emas")

# ===== UI: Tooltip + DaftarSkor =====
buat tip = ui.Tooltip("Klik kiri untuk menembak!", warna="putih")
buat skor_tinggi = ui.DaftarSkor("skor_v66.json", maks_entri=10)
skor_tinggi.tambah("Pemain", 1000)

buat skor = 0
buat tembakan = 0
buat kursor_x = 0.0
buat kursor_y = 0.0
buat hover_bidik = salah

# ===== Pathfinding: cari jalur dari pemain ke kursor =====
buat rute = jalur.cari_jalur(peta_tile, (2, 12), (18, 12))
buat pengikut = jalur.IkutiJalur([], kecepatan=200)

# ===== Fixed timestep fisika =====
fungsi update_fisika(fdt)
    bodi_pemain.tambah_gaya(0, 0)   # gravitasi dunia otomatis
    dunia.update(fdt)
    # Pemain mengikuti bodi fisik
    pemain.x = bodi_pemain.posisi.x - pemain.lebar / 2
    pemain.y = bodi_pemain.posisi.y - pemain.tinggi
    # Musuh sprite mengikuti patroli; bodi mengikuti sprite
    musuh.update(fdt)
    bodi_musuh.set_posisi(musuh.x + 18, musuh.y + 18)
    # Tilemap animasi + emiter mengikuti pemain
    peta_tile.update(fdt)
    api.x = pemain.x + 17
    api.y = pemain.y + 44
    asap.x = musuh.x + 18
    asap.y = musuh.y + 18
    api.update(fdt)
    asap.update(fdt)
selesai

game.atur_fisika(update_fisika, timestep=1/120)

# ===== Update per frame =====
fungsi update_utama(dt)
    buat (mx, my) = input.tikus_posisi()
    buat kursor = cam.screen_to_world(mx, my)
    kursor_x = kursor[0]
    kursor_y = kursor[1]
    hover_bidik = peta_tile.is_solid_at(kursor_x, kursor_y)

    # Kamera
    cam.update(dt)

    # Kontrol pemain (A/D + Space lompat)
    jika input.tombol_ditekan("LEFT") atau input.tombol_ditekan("A") maka
        bodi_pemain.kecepatan.x = bodi_pemain.kecepatan.x - 15
    selesai
    jika input.tombol_ditekan("RIGHT") atau input.tombol_ditekan("D") maka
        bodi_pemain.kecepatan.x = bodi_pemain.kecepatan.x + 15
    selesai
    jika input.tombol_baru_ditekan("SPACE") dan bodi_pemain.grounded maka
        bodi_pemain.apply_impulse(0, -2600)
        kilat.picu()
    selesai

    # Raycast ke kursor: deteksi dinding
    buat hasil = dunia.raycast(bodi_pemain.posisi.x, bodi_pemain.posisi.y,
                               kursor_x, kursor_y)
    jika hasil maka
        buat (bodi_kena, tx_hit, ty_hit) = hasil
        bintang.x = tx_hit
        bintang.y = ty_hit
        bintang.ledak(tx_hit, ty_hit, 6)
        jika tembakan % 5 == 0 maka
            skor = skor + 10
            teks_damage.teks = "+10"
            teks_damage.x = tx_hit
            teks_damage.y = ty_hit
            teks_damage.waktu = 0.0
        selesai
    selesai

    # Klik kiri = tembak (screenshot di P)
    jika input.tikus_baru_ditekan(0) maka
        tembakan = tembakan + 1
        pulsa_klik.x = kursor_x
        pulsa_klik.y = kursor_y
        pulsa_klik.waktu = 0.0
        api.ledak(kursor_x, kursor_y, 8)
    selesai
    jika input.tombol_baru_ditekan("P") maka
        game.tangkap_layar("screenshot_v66.png")
        tulis "Screenshot disimpan!"
    selesai

    # Update efek
    kilat.update(dt)
    teks_damage.update(dt)
    pulsa_klik.update(dt)
    bintang.update(dt)
    tip.update(mx, my, hover_bidik, dt)
selesai

# ===== Gambar per frame =====
fungsi gambar_utama(screen)
    # Latar gradien langit
    grafis.gradien_vertikal(0, 0, lebar_layar, tinggi_layar, "langit", "biru_gelap")

    # Parallax: bukit di belakang
    buat (bx, by) = cam.screen_parallax(300, 500, 0.3)
    grafis.segi_panjang(bx - 200, by - 60, 700, 120, "hijau_gelap")

    # Tilemap (dengan tile air animasi)
    peta_tile.gambar(screen, cam.x, cam.y)

    # Pathfinding preview (jika ada rute)
    jika rute maka
        buat r = 0
        selama r < jalur.panjang_jalur(rute) - 1 lakukan
            buat (x1, y1) = rute[r]
            buat (x2, y2) = rute[r + 1]
            grafis.garis(x1 * 40 + 20 - cam.x, y1 * 40 + 20 - cam.y,
                         x2 * 40 + 20 - cam.x, y2 * 40 + 20 - cam.y,
                         "hijau", 2)
            r = r + 1
        selesai
    selesai

    # Sprite pemain & musuh (melalui kamera)
    pemain.gambar(screen, kamera=cam)
    musuh.gambar(screen, kamera=cam)

    # Partikel
    api.gambar(screen, kamera=cam)
    asap.gambar(screen, kamera=cam)
    bintang.gambar(screen, kamera=cam)

    # Efek layar
    pulsa_klik.gambar(screen)
    teks_damage.gambar(screen)

    # UI
    grafis.tulis_teks("Skor: " + teks(skor), 12, 10, "putih", 26)
    grafis.tulis_teks("Tembakan: " + teks(tembakan), 12, 44, "kuning", 20)
    grafis.tulis_teks("Skor tertinggi: " + teks(skor_tinggi.skor_tertinggi()),
                      12, 72, "emas", 18)
    tip.gambar(screen)
    kilat.gambar(screen)
selesai

game.tambah_scene("utama", update_utama, gambar_utama)
game.ganti_scene("utama")
game.mulai()
