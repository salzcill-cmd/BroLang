# Contoh Game: Pong 2 Player
# ===========================
# Game Pong 2 pemain.
# Player 1: W/S, Player 2: UP/DOWN

impor game
impor grafis
impor input
impor vektor

# --- Setup ---
buat lebar = 800
buat tinggi = 600
buat paddle_w = 12
buat paddle_h = 80
buat bola_r = 8

# Player 1 (kiri)
buat p1_pos = vektor.Vec2(30, tinggi / 2 - paddle_h / 2)
buat p1_skor = 0

# Player 2 (kanan)
buat p2_pos = vektor.Vec2(lebar - 30 - paddle_w, tinggi / 2 - paddle_h / 2)
buat p2_skor = 0

# Bola
buat bola_pos = vektor.Vec2(lebar / 2, tinggi / 2)
buat bola_vel = vektor.Vec2(300.0, 200.0)
buat bola_speed_dasar = 300.0

buat paddle_kecepatan = 350.0
buat max_skor = 5

# --- Fungsi ---
fungsi reset_bola()
    global bola_pos, bola_vel
    bola_pos = vektor.Vec2(lebar / 2, tinggi / 2)
    bola_vel = vektor.Vec2(bola_speed_dasar, bola_speed_dasar * 0.7)
selesai

# --- Update ---
fungsi update(dt)
    global p1_pos, p2_pos, bola_pos, bola_vel
    global p1_skor, p2_skor

    # Paddle 1 (W/S)
    jika input.tombol_ditekan("w") maka
        p1_pos.y = p1_pos.y - paddle_kecepatan * dt
    selesai
    jika input.tombol_ditekan("s") maka
        p1_pos.y = p1_pos.y + paddle_kecepatan * dt
    selesai

    # Paddle 2 (UP/DOWN)
    jika input.tombol_ditekan("UP") maka
        p2_pos.y = p2_pos.y - paddle_kecepatan * dt
    selesai
    jika input.tombol_ditekan("DOWN") maka
        p2_pos.y = p2_pos.y + paddle_kecepatan * dt
    selesai

    # Batasi paddle
    jika p1_pos.y < 0 maka
        p1_pos.y = 0
    selesai
    jika p1_pos.y > tinggi - paddle_h maka
        p1_pos.y = tinggi - paddle_h
    selesai
    jika p2_pos.y < 0 maka
        p2_pos.y = 0
    selesai
    jika p2_pos.y > tinggi - paddle_h maka
        p2_pos.y = tinggi - paddle_h
    selesai

    # Gerak bola
    bola_pos.x = bola_pos.x + bola_vel.x * dt
    bola_pos.y = bola_pos.y + bola_vel.y * dt

    # Pantul atas/bawah
    jika bola_pos.y <= bola_r maka
        bola_pos.y = bola_r
        bola_vel.y = bola_vel.y * -1
    selesai
    jika bola_pos.y >= tinggi - bola_r maka
        bola_pos.y = tinggi - bola_r
        bola_vel.y = bola_vel.y * -1
    selesai

    # Tabrakan paddle 1 (kiri)
    jika (bola_vel.x < 0 dan
          bola_pos.x - bola_r <= p1_pos.x + paddle_w dan
          bola_pos.x + bola_r >= p1_pos.x dan
          bola_pos.y >= p1_pos.y dan
          bola_pos.y <= p1_pos.y + paddle_h) maka
        bola_vel.x = bola_vel.x * -1
        bola_pos.x = p1_pos.x + paddle_w + bola_r
    selesai

    # Tabrakan paddle 2 (kanan)
    jika (bola_vel.x > 0 dan
          bola_pos.x + bola_r >= p2_pos.x dan
          bola_pos.x - bola_r <= p2_pos.x + paddle_w dan
          bola_pos.y >= p2_pos.y dan
          bola_pos.y <= p2_pos.y + paddle_h) maka
        bola_vel.x = bola_vel.x * -1
        bola_pos.x = p2_pos.x - bola_r
    selesai

    # Poin untuk player 2 (bola keluar kiri)
    jika bola_pos.x < -bola_r maka
        p2_skor = p2_skor + 1
        reset_bola()
    selesai

    # Poin untuk player 1 (bola keluar kanan)
    jika bola_pos.x > lebar + bola_r maka
        p1_skor = p1_skor + 1
        reset_bola()
    selesai
selesai

# --- Gambar ---
fungsi gambar(screen)
    grafis.bersihkan((10, 10, 30))

    # Garis tengah
    untuk i dalam range(0, tinggi, 20) lakukan
        grafis.segi_panjang(lebar / 2 - 1, i, 2, 10, "abu-abu_gelap")
    selesai

    # Paddle
    grafis.segi_panjang(p1_pos.x, p1_pos.y, paddle_w, paddle_h, "biru")
    grafis.segi_panjang(p2_pos.x, p2_pos.y, paddle_w, paddle_h, "merah")

    # Bola
    grafis.lingkaran(bola_pos.x, bola_pos.y, bola_r, "putih")

    # Skor
    grafis.tulis_teks(teks(p1_skor), lebar / 2 - 60, 20, "biru", 48)
    grafis.tulis_teks(teks(p2_skor), lebar / 2 + 40, 20, "merah", 48)

    # Instruksi
    grafis.tulis_teks("W/S", 30, tinggi - 25, "biru", 18)
    grafis.tulis_teks("UP/DOWN", lebar - 80, tinggi - 25, "merah", 18)
selesai

# --- Main ---
game.buat_jendela(lebar, tinggi, "Pong 2P - BroLang")
game.tambah_scene("utama", update, gambar)
game.ganti_scene("utama")
game.mulai()
