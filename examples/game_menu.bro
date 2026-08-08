# ============================================================
# game_menu.bro — showcase fitur v6.2: scene lifecycle, transisi,
# tumpukan scene (overlay), dan UI komponen baru.
#
# Jalankan:
#   pip install pygame-ce
#   bro examples/game_menu.bro
#
# Kontrol:
#   - Klik tombol MULAI untuk masuk ke scene main (transisi fade)
#   - Ketik nama di KotakTeks (klik dulu untuk fokus, BACKSPACE hapus)
#   - Geser Slider volume, centang KotakCentang, pilih level di DaftarPilih
#   - Tekan ESC di scene main untuk membuka overlay pause (dorong_scene)
# ============================================================

impor game
impor ui
impor input
impor grafis

# Helper: tulis teks rata tengah (tulis_teks belum dukung tengah)
fungsi tulis_tengah(teks, y, warna, ukuran)
    buat [lebar, _] = grafis.dapatkan_ukuran_teks(teks, ukuran)
    grafis.tulis_teks(teks, (800 - lebar) / 2, y, warna, ukuran)
selesai

# ------------------------------------------------------------
# Scene MENU: setup profil pemain pakai UI komponen baru
# ------------------------------------------------------------

buat nama_kotak = kosong
buat volume_slider = kosong
buat musik_centang = kosong
buat level_pilih = kosong

fungsi on_masuk_menu()
    tulis "=== MENU: masuk ==="
    nama_kotak = ui.KotakTeks(260, 180, 280, 40, placeholder="Nama pemain", maks_karakter=12)
    volume_slider = ui.Slider(260, 260, 280, nilai=60, min=0, maks=100, langkah=5)
    musik_centang = ui.KotakCentang(260, 320, label="Aktifkan musik", dicentang=benar)
    level_pilih = ui.DaftarPilih(260, 380, 280, opsi=["Mudah", "Sedang", "Sulit"], terpilih=1)
selesai

fungsi on_keluar_menu()
    tulis "=== MENU: keluar ==="
selesai

fungsi update_menu(dt)
    buat [mx, my] = input.tikus_posisi()
    buat klik = input.tikus_baru_ditekan(0)
    buat tahan = input.tikus_tekanan()[0]

    nama_kotak.update(mx, my, klik)
    volume_slider.update(mx, my, tahan)
    musik_centang.update(mx, my, klik)
    level_pilih.update(mx, my, klik)

    jika nama_kotak.fokus maka
        untuk ev dalam input.events_tombol() lakukan
            nama_kotak.tambah_karakter(ev)
        selesai
        jika input.tombol_baru_ditekan("BACKSPACE") maka
            nama_kotak.hapus_karakter()
        selesai
    selesai

    # Tombol MULAI di tengah-tengah kanan bawah
    buat mulai_btn = ui.Tombol("MULAI", 310, 480, 180, 60)
    jika mulai_btn.update(mx, my, klik) maka
        # Simpan konfigurasi ke data global
        game.atur_data("nama", nama_kotak.teks_sekarang())
        game.atur_data("volume", volume_slider.nilai_sekarang())
        game.atur_data("musik", musik_centang.dicentang_sekarang())
        game.atur_data("level", level_pilih.opsi_terpilih())
        game.ganti_scene("main", transisi="fade", durasi=0.8)
    selesai
selesai

fungsi gambar_menu(screen)
    tulis_tengah("SETUP PERMAINAN", 90, "emas", 36)
    grafis.tulis_teks("Nama:", 180, 190, "putih", 22)
    grafis.tulis_teks("Volume:", 180, 270, "putih", 22)
    grafis.tulis_teks("Level:", 180, 390, "putih", 22)
    nama_kotak.gambar(screen)
    volume_slider.gambar(screen)
    musik_centang.gambar(screen)
    level_pilih.gambar(screen)
    tulis_tengah("Tekan ESC di game untuk menu pause", 560, "abu-abu", 16)
selesai

# ------------------------------------------------------------
# Scene MAIN: gameplay dengan overlay pause
# ------------------------------------------------------------

buat skor = 0
buat detik = 0.0

fungsi on_masuk_main()
    tulis "=== MAIN: masuk ==="
    skor = 0
    detik = 0.0
selesai

fungsi on_keluar_main()
    tulis "=== MAIN: keluar ==="
selesai

fungsi update_main(dt)
    detik = detik + dt
    jika input.tombol_baru_ditekan("SPACE") maka
        skor = skor + 10
    selesai
    # Buka menu pause sebagai OVERLAY (scene main tetap digambar di bawah)
    jika input.tombol_baru_ditekan("ESCAPE") maka
        game.dorong_scene("pause", transisi="fade", durasi=0.4)
    selesai
selesai

fungsi gambar_main(screen)
    tulis_tengah("GAME BERJALAN...", 150, "hijau", 40)
    tulis_tengah("Tekan SPACE untuk +10 skor", 210, "putih", 20)
    tulis_tengah("Skor: " + teks(skor), 260, "kuning", 28)
    tulis_tengah("Waktu: " + teks(round(detik, 1)) + "s", 300, "putih", 20)
    tulis_tengah("Nama: " + game.dapatkan_data()["nama"], 350, "cyan", 20)
    tulis_tengah("Level: " + game.dapatkan_data()["level"], 380, "pink", 20)
    tulis_tengah("ESC = pause", 500, "abu-abu", 16)
selesai

# ------------------------------------------------------------
# Scene PAUSE: overlay di atas scene main
# ------------------------------------------------------------

fungsi on_masuk_pause()
    tulis "=== PAUSE: masuk (overlay) ==="
selesai

fungsi update_pause(dt)
    buat [mx, my] = input.tikus_posisi()
    buat klik = input.tikus_baru_ditekan(0)
    buat lanjut_btn = ui.Tombol("LANJUT", 310, 300, 180, 60)
    jika lanjut_btn.update(mx, my, klik) maka
        game.pop_scene(transisi="fade", durasi=0.4)
    selesai
    jika input.tombol_baru_ditekan("ESCAPE") maka
        game.pop_scene(transisi="fade", durasi=0.4)
    selesai
selesai

fungsi gambar_pause(screen)
    grafis.segi_panjang(200, 180, 400, 240, "biru_gelap")   # panel gelap
    tulis_tengah("PAUSE", 210, "kuning", 40)
    tulis_tengah("Skor kamu: " + teks(skor), 270, "putih", 22)
    buat lanjut_btn = ui.Tombol("LANJUT", 310, 300, 180, 60)
    lanjut_btn.gambar(screen)
selesai

# ------------------------------------------------------------
# Setup game
# ------------------------------------------------------------

game.buat_jendela(800, 600, "BroLang v6.2 - Scene & UI")
game.set_latar_warna("biru_gelap")
game.atur_fps(60)
game.set_tampil_fps(benar)

game.tambah_scene("menu", update_menu, gambar_menu,
                  on_masuk=on_masuk_menu, on_keluar=on_keluar_menu)
game.tambah_scene("main", update_main, gambar_main,
                  on_masuk=on_masuk_main, on_keluar=on_keluar_main)
game.tambah_scene("pause", update_pause, gambar_pause,
                  on_masuk=on_masuk_pause)

game.ganti_scene("menu")
game.mulai()
