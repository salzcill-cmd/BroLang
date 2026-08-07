# Contoh Game: Arena Platformer
# =============================
# Game showcase fitur library game BroLang v6:
#   game (scene, pause, FPS) · grafis (bentuk + teks multi-baris)
#   input (keyboard + mouse) · sprite (animasi, collider, flip)
#   tilemap (peta solid + warna) · kamera (screen shake)
#   partikel (ledakan + hujan) · ui (Tombol, Label, Bar)
#   waktu (Timer, Stopwatch) · vektor · acak
#
# Kontrol:  ← → gerak   ↑ lompat   SPACE tembak   P pause
#           ESC keluar   (di menu: klik tombol MULAI dengan mouse)

impor game
impor grafis
impor input
impor sprite
impor ui
impor partikel
impor kamera
impor tilemap
impor waktu
impor vektor
impor acak

buat lebar_layar = 800
buat tinggi_layar = 600

# ===== Status Game =====
buat skor = 0
buat nyawa = 100.0
buat keadaan = "menu"     # menu / main / gameover
buat mulai_ditekan = salah

# ===== Pemain =====
buat pemain = sprite.Sprite(kosong, 100, 300, lebar=34, tinggi=40)
pemain.warna = "langit"
pemain.vel_x = 0.0
pemain.vel_y = 0.0
pemain.bumi = salah
buat kecepatan_gerak = 220.0
buat gravitasi_pemain = 700.0
buat kekuatan_lompat = -330.0

# ===== Peta Tile =====
buat tileset = tilemap.buat_tileset("arena", ukuran_tile=40)
tileset.atur_solid(1, benar)
tileset.atur_warna(1, "coklat")
tileset.atur_solid(2, benar)
tileset.atur_warna(2, "hijau_gelap")
buat tile_peta = tilemap.buat_peta(20, 15, 40)
tile_peta.set_tileset(tileset)

# Gambar peta: lantai bawah + platform
buat i = 0
selama i < 20 lakukan
    tile_peta.atur(i, 14, 1)
    i = i + 1
selesai
i = 3
selama i <= 7 lakukan
    tile_peta.atur(i, 10, 2)
    i = i + 1
selesai
i = 12
selama i <= 16 lakukan
    tile_peta.atur(i, 7, 2)
    i = i + 1
selesai
i = 2
selama i <= 4 lakukan
    tile_peta.atur(i, 4, 2)
    i = i + 1
selesai

# ===== Kamera (screen shake) =====
buat cam = kamera.buat_kamera(lebar_layar, tinggi_layar)

# ===== Grup Sprite =====
buat peluru_grup = sprite.GrupSprite()
buat musuh_grup = sprite.GrupSprite()

# ===== Efek Partikel =====
buat efek = partikel.buat_emiter(0, 0)
efek.kecepatan = 220
efek.warna = "jingga"
efek.umur = 0.8

# ===== UI =====
buat label_skor = ui.Label("Skor: 0", 10, 10, "kuning", 26)
buat label_pause = ui.Label("PAUSE - tekan P untuk lanjut", 400, 280, "putih", 28, tengah=benar)
buat bar_nyawa = ui.Bar(nyawa, 100.0, 10, 42, 220, 18,
                        warna_isi="hijau", warna_latar="merah_gelap",
                        tampil_teks=salah)
buat label_menu = ui.Label("ARENA PLATFORMER", 400, 170, "emas", 46, tengah=benar)
buat label_info = ui.Label("←→ gerak   ↑ lompat   SPACE tembak   P pause",
                           400, 240, "putih", 20, tengah=benar)
buat label_info2 = ui.Label("Klik tombol MULAI dengan mouse", 400, 290, "abu-abu", 18, tengah=benar)
buat tombol_mulai = ui.Tombol("MULAI", 300, 330, 200, 60,
                              warna="biru", warna_hover="hijau")
buat label_gameover = ui.Label("GAME OVER", 400, 220, "merah", 48, tengah=benar)
buat label_skor_akhir = ui.Label("Skor: 0", 400, 280, "putih", 28, tengah=benar)
buat label_coba_lagi = ui.Label("Tekan SPACE untuk coba lagi", 400, 320, "kuning", 20, tengah=benar)

# ===== Timer & Stopwatch =====
buat spawn_timer = waktu.Timer(1.5)
buat stopwatch = waktu.Stopwatch()
buat fps_counter = waktu.FpsCounter()

# ===== Logika Peta (tabrakan pemain vs tile) =====
fungsi resolve_tabrakan_peta(obj, dt)
    global tile_peta
    buat langkah = 0
    # Gerak horizontal (dengan guard agar tidak loop tak terbatas)
    obj.x = obj.x + obj.vel_x * dt
    jika tile_peta.check_collision(obj.x, obj.y, obj.lebar, obj.tinggi) maka
        langkah = 0
        selama tile_peta.check_collision(obj.x, obj.y, obj.lebar, obj.tinggi) dan langkah < 80 lakukan
            jika obj.vel_x > 0 maka
                obj.x = obj.x - 1
            lainnya
                obj.x = obj.x + 1
            selesai
            langkah = langkah + 1
        selesai
        obj.vel_x = 0
    selesai
    # Gerak vertikal
    obj.y = obj.y + obj.vel_y * dt
    jika tile_peta.check_collision(obj.x, obj.y, obj.lebar, obj.tinggi) maka
        langkah = 0
        selama tile_peta.check_collision(obj.x, obj.y, obj.lebar, obj.tinggi) dan langkah < 80 lakukan
            jika obj.vel_y > 0 maka
                obj.y = obj.y - 1
            lainnya
                obj.y = obj.y + 1
            selesai
            langkah = langkah + 1
        selesai
        jika obj.vel_y > 0 maka
            obj.bumi = benar
        selesai
        obj.vel_y = 0
    lainnya
        obj.bumi = salah
    selesai
selesai

# ===== Mulai / Reset Game =====
fungsi mulai_game()
    global skor, nyawa, keadaan, pemain
    keadaan = "main"
    skor = 0
    nyawa = 100.0
    pemain.ke_awal(100, 300)
    pemain.vel_x = 0
    pemain.vel_y = 0
    peluru_grup.kosongkan()
    musuh_grup.kosongkan()
    efek.kosongkan()
    spawn_timer.reset(1.5)
    stopwatch.reset()
    stopwatch.mulai()
selesai

# ===== Spawn Musuh =====
fungsi spawn_musuh()
    global musuh_grup
    buat m = sprite.Sprite(kosong, acak.bulat(80, 700), 10, lebar=30, tinggi=30)
    m.warna = "merah"
    m.vel_x = 0.0
    m.vel_y = 0.0
    jika acak.bulat(0, 1) == 0 maka
        m.arah = 1
    lainnya
        m.arah = -1
    selesai
    musuh_grup.tambah(m)
selesai

# ===== Update Pemain =====
fungsi update_pemain(dt)
    global pemain
    pemain.vel_x = 0
    jika input.tombol_ditekan("LEFT") atau input.tombol_ditekan("a") maka
        pemain.vel_x = 0 - kecepatan_gerak
        pemain.flip_x = benar
    selesai
    jika input.tombol_ditekan("RIGHT") atau input.tombol_ditekan("d") maka
        pemain.vel_x = kecepatan_gerak
        pemain.flip_x = salah
    selesai
    jika input.tombol_baru_ditekan("UP") dan pemain.bumi maka
        pemain.vel_y = kekuatan_lompat
        pemain.bumi = salah
    selesai
    pemain.vel_y = pemain.vel_y + gravitasi_pemain * dt
    resolve_tabrakan_peta(pemain, dt)
selesai

# ===== Tembak Peluru =====
fungsi tembak()
    global peluru_grup
    buat peluru = sprite.Sprite(kosong, pemain.x + 34, pemain.y + 16, lebar=14, tinggi=6)
    peluru.warna = "kuning"
    peluru.kecepatan_x = 480
    peluru.kecepatan_y = 0
    peluru_grup.tambah(peluru)
selesai

# ===== Update Musuh =====
fungsi update_musuh(dt)
    global musuh_grup, tile_peta
    # Semua musuh: patroli + jatuh ke lantai (fisika manual)
    buat daftar = musuh_grup.dapatkan_semua()
    buat i = 0
    selama i < panjang(daftar) lakukan
        buat m = daftar[i]
        m.vel_y = m.vel_y + 500 * dt
        m.vel_x = m.arah * 70
        resolve_tabrakan_peta(m, dt)
        # Belok jika ada dinding di depan
        jika tile_peta.check_collision(m.x + m.lebar * m.arah + 2, m.y, m.lebar, m.tinggi) maka
            m.arah = m.arah * -1
        selesai
        # Belok jika di tepi platform (tidak ada tile di bawah depan)
        buat tile_bawah = tile_peta.dapatkan(m.x + m.lebar * m.arah, m.y + m.tinggi + 6)
        jika tile_bawah == 0 atau tile_bawah == -1 maka
            m.arah = m.arah * -1
        selesai
        i = i + 1
    selesai
selesai

# ===== Update Peluru =====
fungsi update_peluru(dt)
    global peluru_grup
    peluru_grup.update(dt)
    buat daftar = peluru_grup.dapatkan_semua()
    buat i = 0
    selama i < panjang(daftar) lakukan
        buat p = daftar[i]
        jika p.x > lebar_layar + 60 atau p.x < -60 maka
            p.aktif = salah
        selesai
        i = i + 1
    selesai
    peluru_grup.hapus_tidak_aktif()
selesai

# ===== Tabrakan Peluru-Musuh & Musuh-Pemain =====
fungsi cek_tabrakan()
    global skor, nyawa, keadaan
    # Peluru mengenai musuh
    buat daftar_peluru = peluru_grup.dapatkan_semua()
    buat i = 0
    selama i < panjang(daftar_peluru) lakukan
        buat pel = daftar_peluru[i]
        buat korban = musuh_grup.cek_tabrakan(pel)
        jika panjang(korban) > 0 maka
            buat musuh_mati = korban[0]
            musuh_mati.aktif = salah
            pel.aktif = salah
            skor = skor + 10
            efek.kecepatan = 200
            efek.warna = "jingga"
            efek.ledak(musuh_mati.x + 15, musuh_mati.y + 15, 28)
        selesai
        i = i + 1
    selesai
    peluru_grup.hapus_tidak_aktif()
    musuh_grup.hapus_tidak_aktif()

    # Musuh menyentuh pemain
    buat penyerang = musuh_grup.cek_tabrakan(pemain)
    jika panjang(penyerang) > 0 maka
        buat musuh_kena = penyerang[0]
        nyawa = nyawa - 15
        bar_nyawa.kurang(15)
        cam.shake(8, 0.3)
        pemain.vel_y = -220
        musuh_kena.aktif = salah
        efek.kecepatan = 120
        efek.warna = "merah"
        efek.ledak(pemain.x + 17, pemain.y + 20, 20)
        jika nyawa <= 0 maka
            nyawa = 0
            keadaan = "gameover"
            stopwatch.stop()
            label_skor_akhir.set_teks("Skor: " + teks(skor) + "   Waktu: " + teks(round(stopwatch.elapsed(), 1)) + " dtk")
        selesai
    selesai
    musuh_grup.hapus_tidak_aktif()
selesai

# ===== Update Utama =====
fungsi update(dt)
    global keadaan, nyawa

    jika keadaan == "menu" maka
        buat [mx, my] = input.tikus_posisi()
        buat diklik = input.tikus_baru_ditekan(0)
        jika tombol_mulai.update(mx, my, diklik) maka
            mulai_game()
        selesai
        efek.update(dt)
        kembali
    selesai

    jika keadaan == "gameover" maka
        jika input.tombol_baru_ditekan("SPACE") maka
            mulai_game()
        selesai
        kembali
    selesai

    # ===== Main =====
    jika input.tombol_baru_ditekan("P") maka
        game.set_pause(bukan game.sedang_pause())
    selesai
    jika game.sedang_pause() maka
        kembali
    selesai

    jika input.tombol_baru_ditekan("SPACE") maka
        tembak()
    selesai

    update_pemain(dt)
    update_musuh(dt)
    update_peluru(dt)
    cek_tabrakan()

    spawn_timer.update(dt)
    jika spawn_timer.habis() maka
        spawn_musuh()
        spawn_timer.reset(acak.angka(1.2, 2.5))
    selesai

    efek.update(dt)
    cam.update(dt)
    fps_counter.update(dt)

    label_skor.set_teks("Skor: " + teks(skor))
    bar_nyawa.set_nilai(nyawa)
selesai

# ===== Gambar =====
fungsi gambar(screen)
    global keadaan
    grafis.bersihkan((15, 20, 40))

    buat [kx, ky] = cam.world_to_screen(0, 0)

    tile_peta.gambar(screen, kx, ky)
    pemain.gambar(screen, kamera=cam)
    musuh_grup.gambar(screen, kamera=cam)
    peluru_grup.gambar(screen, kamera=cam)
    efek.gambar(screen, kamera=cam)

    jika keadaan == "menu" maka
        label_menu.gambar(screen)
        label_info.gambar(screen)
        label_info2.gambar(screen)
        tombol_mulai.gambar(screen)
        grafis.tulis_teks("Scroll: " + teks(input.geser()[1]), 10, tinggi_layar - 25, "abu-abu", 16)
        grafis.tulis_teks_multi("Fitur: sprite · fisika · partikel · UI · tilemap · kamera",
                                10, tinggi_layar - 70, "abu-abu", 16)
    selesai

    jika keadaan == "main" maka
        label_skor.gambar(screen)
        bar_nyawa.gambar(screen)
        grafis.tulis_teks("FPS: " + teks(round(fps_counter.fps(), 0)), lebar_layar - 90, 10, "putih", 16)
        jika game.sedang_pause() maka
            label_pause.gambar(screen)
        selesai
    selesai

    jika keadaan == "gameover" maka
        label_gameover.gambar(screen)
        label_skor_akhir.gambar(screen)
        label_coba_lagi.gambar(screen)
    selesai
selesai

# ===== Main =====
game.buat_jendela(lebar_layar, tinggi_layar, "Arena Platformer - BroLang")
game.set_tampil_fps(salah)
game.atur_fps(60)
game.tambah_scene("utama", update, gambar)
game.ganti_scene("utama")
game.mulai()
