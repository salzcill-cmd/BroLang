# Contoh Game: Paddle & Ball
# ==========================
# Game sederhana dengan paddle, bola, dan skor.
# Menampilkan fitur game BroLang: grafis, input, vektor, game loop.

impor game
impor grafis
impor input
impor vektor

# --- Setup ---
buat lebar_layar = 800
buat tinggi_layar = 600

# Paddle
buat paddle_lebar = 100
buat paddle_tinggi = 15
buat paddle_pos = vektor.Vec2(lebar_layar / 2 - paddle_lebar / 2, tinggi_layar - 40)
buat paddle_kecepatan = 400.0

# Bola
buat bola_pos = vektor.Vec2(lebar_layar / 2, tinggi_layar / 2)
buat bola_radius = 10
buat bola_vel = vektor.Vec2(200.0, -200.0)

# Skor
buat skor = 0
buat nyawa = 3
buat game_over = benar
buat game_started = salah

# --- Fungsi ---
def reset_bola():
    global bola_pos, bola_vel
    bola_pos = vektor.Vec2(lebar_layar / 2, tinggi_layar / 2)
    bola_vel = vektor.Vec2(200.0, -200.0)

# --- Update ---
def update(dt):
    global paddle_pos, bola_pos, bola_vel, skor, nyawa, game_over, game_started

    jika game_over maka
        jika input.tombol_baru_ditekan("SPACE") maka
            game_over = salah
            game_started = benar
            skor = 0
            nyawa = 3
            reset_bola()
            paddle_pos.x = lebar_layar / 2 - paddle_lebar / 2
        selesai
        kembali
    selesai

    game_started = benar

    # Gerak paddle
    jika input.tombol_ditekan("LEFT") atau input.tombol_ditekan("a") maka
        paddle_pos.x = paddle_pos.x - paddle_kecepatan * dt
    selesai
    jika input.tombol_ditekan("RIGHT") || input.tombol_ditekan("d") maka
        paddle_pos.x = paddle_pos.x + paddle_kecepatan * dt
    selesai

    # Batasi paddle
    jika paddle_pos.x < 0 maka
        paddle_pos.x = 0
    selesai
    jika paddle_pos.x > lebar_layar - paddle_lebar maka
        paddle_pos.x = lebar_layar - paddle_lebar
    selesai

    # Gerak bola
    bola_pos.x = bola_pos.x + bola_vel.x * dt
    bola_pos.y = bola_pos.y + bola_vel.y * dt

    # Pantul dari dinding kiri/kanan
    jika bola_pos.x <= bola_radius maka
        bola_pos.x = bola_radius
        bola_vel.x = bola_vel.x * -1
    selesai
    jika bola_pos.x >= lebar_layar - bola_radius maka
        bola_pos.x = lebar_layar - bola_radius
        bola_vel.x = bola_vel.x * -1
    selesai

    # Pantul dari atas
    jika bola_pos.y <= bola_radius maka
        bola_pos.y = bola_radius
        bola_vel.y = bola_vel.y * -1
    selesai

    # Tabrakan dengan paddle
    jika (bola_pos.y + bola_radius >= paddle_pos.y dan
          bola_pos.x >= paddle_pos.x dan
          bola_pos.x <= paddle_pos.x + paddle_lebar) maka
        bola_vel.y = bola_vel.y * -1
        bola_pos.y = paddle_pos.y - bola_radius
        skor = skor + 1
    selesai

    # Bola jatuh ke bawah
    jika bola_pos.y > tinggi_layar + bola_radius maka
        nyawa = nyawa - 1
        jika nyawa <= 0 maka
            game_over = benar
        selesai
        reset_bola()
    selesai

# --- Gambar ---
def gambar(screen):
    grafis.bersihkan((20, 20, 40))

    jika game_over maka
        grafis.tulis_teks("GAME OVER", lebar_layar / 2 - 100, tinggi_layar / 2 - 40, "merah", 48)
        grafis.tulis_teks("Skor: " + teks(skor), lebar_layar / 2 - 50, tinggi_layar / 2 + 20, "putih", 32)
        grafis.tulis_teks("Tekan SPACE untuk mulai", lebar_layar / 2 - 140, tinggi_layar / 2 + 70, "kuning", 24)
    selesai
    jika game_started dan bukan game_over maka
        # Paddle
        grafis.segi_panjang(paddle_pos.x, paddle_pos.y, paddle_lebar, paddle_tinggi, "putih")

        # Bola
        grafis.lingkaran(bola_pos.x, bola_pos.y, bola_radius, "emas")

        # UI
        grafis.tulis_teks("Skor: " + teks(skor), 10, 10, "putih", 28)
        grafis.tulis_teks("Nyawa: " + teks(nyawa), lebar_layar - 120, 10, "merah", 28)
        grafis.tulis_teks("A/D atau LEFT/RIGHT untuk bergerak", 10, tinggi_layar - 30, "abu-abu", 18)
    selesai

# --- Main ---
game.buat_jendela(lebar_layar, tinggi_layar, "Paddle & Ball - BroLang Game")
game.tambah_scene("utama", update, gambar)
game.ganti_scene("utama")
game.mulai()
