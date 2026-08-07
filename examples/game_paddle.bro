# Contoh Game: Brick Breaker (Paddle & Ball)
# ===========================================
# Game paddle + bola + bata penambah skor.
# Hancurkan semua bata untuk MENANG!
# Kontrol: A/D atau LEFT/RIGHT untuk bergerak.

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

# Skor & status
buat skor = 0
buat nyawa = 3
buat game_over = benar
buat menang = salah
buat game_started = salah

# Bata (brick-breaker)
struktur Bata { x, y, lebar, tinggi, aktif, warna }
buat bata_list = []
buat bata_kolom = 8
buat bata_baris = 4
buat bata_lebar = 74
buat bata_tinggi = 22
buat bata_gap = 6
buat bata_atas = 70
buat warna_bata = ["merah", "jingga", "kuning", "hijau", "biru"]

# --- Fungsi ---
fungsi buat_semua_bata()
    global bata_list
    bata_list = []
    buat lebar_total = bata_kolom * bata_lebar + (bata_kolom - 1) * bata_gap
    buat x_mulai = (lebar_layar - lebar_total) / 2
    buat i = 0
    selama i < bata_baris lakukan
        buat j = 0
        selama j < bata_kolom lakukan
            buat bx = x_mulai + j * (bata_lebar + bata_gap)
            buat by = bata_atas + i * (bata_tinggi + bata_gap)
            buat warna_b = warna_bata[i]
            bata_list.tambah(Bata(bx, by, bata_lebar, bata_tinggi, benar, warna_b))
            j = j + 1
        selesai
        i = i + 1
    selesai
selesai

fungsi reset_bola()
    global bola_pos, bola_vel
    bola_pos = vektor.Vec2(lebar_layar / 2, tinggi_layar / 2)
    bola_vel = vektor.Vec2(200.0, -200.0)
selesai

fungsi mulai_ulang()
    global game_over, menang, game_started, skor, nyawa, paddle_pos
    game_over = salah
    menang = salah
    game_started = benar
    skor = 0
    nyawa = 3
    buat_semua_bata()
    reset_bola()
    paddle_pos.x = lebar_layar / 2 - paddle_lebar / 2
selesai

fungsi percepat_bola()
    global bola_vel
    bola_vel.x = bola_vel.x * 1.05
    bola_vel.y = bola_vel.y * 1.05
    # Jaga kecepatan maksimal supaya bola tidak menembus bata (anti-tunneling)
    jika bola_vel.x > 600 maka
        bola_vel.x = 600
    selesai
    jika bola_vel.x < -600 maka
        bola_vel.x = -600
    selesai
    jika bola_vel.y > 600 maka
        bola_vel.y = 600
    selesai
    jika bola_vel.y < -600 maka
        bola_vel.y = -600
    selesai
selesai

# --- Update ---
fungsi update(dt)
    global paddle_pos, bola_pos, bola_vel, skor, nyawa
    global game_over, menang, game_started

    jika game_over maka
        jika input.tombol_baru_ditekan("SPACE") maka
            mulai_ulang()
        selesai
        kembali
    selesai

    jika menang maka
        jika input.tombol_baru_ditekan("SPACE") maka
            mulai_ulang()
        selesai
        kembali
    selesai

    game_started = benar

    # Gerak paddle
    jika input.tombol_ditekan("LEFT") atau input.tombol_ditekan("a") maka
        paddle_pos.x = paddle_pos.x - paddle_kecepatan * dt
    selesai
    jika input.tombol_ditekan("RIGHT") atau input.tombol_ditekan("d") maka
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

    # Tabrakan dengan bata (+10 skor per bata)
    buat i = 0
    selama i < bata_list.jumlah() lakukan
        buat b = bata_list[i]
        jika b.aktif maka
            jika (bola_pos.x + bola_radius >= b.x dan
                  bola_pos.x - bola_radius <= b.x + b.lebar dan
                  bola_pos.y + bola_radius >= b.y dan
                  bola_pos.y - bola_radius <= b.y + b.tinggi) maka
                b.aktif = salah
                skor = skor + 10
                # Simplifikasi: selalu pantulkan sumbu Y (sebagian besar tabrakan
                # terjadi dari bawah karena bata di atas). Dorong bola keluar dari
                # bata agar tidak dihitung dua kali.
                bola_vel.y = bola_vel.y * -1
                # Dorong bola keluar dari bata agar tidak kena dua kali
                jika bola_vel.y > 0 maka
                    bola_pos.y = b.y + b.tinggi + bola_radius
                lainnya
                    bola_pos.y = b.y - bola_radius
                selesai
                percepat_bola()
            selesai
        selesai
        i = i + 1
    selesai

    # Cek kemenangan: semua bata hancur
    buat sisa = 0
    buat j = 0
    selama j < bata_list.jumlah() lakukan
        jika bata_list[j].aktif maka
            sisa = sisa + 1
        selesai
        j = j + 1
    selesai
    jika sisa == 0 maka
        menang = benar
    selesai

    # Bola jatuh ke bawah
    jika bola_pos.y > tinggi_layar + bola_radius maka
        nyawa = nyawa - 1
        jika nyawa <= 0 maka
            game_over = benar
        selesai
        reset_bola()
    selesai
selesai

# --- Gambar ---
fungsi gambar(screen)
    grafis.bersihkan((20, 20, 40))

    jika game_over maka
        grafis.tulis_teks("GAME OVER", lebar_layar / 2 - 100, tinggi_layar / 2 - 40, "merah", 48)
        grafis.tulis_teks("Skor: " + teks(skor), lebar_layar / 2 - 50, tinggi_layar / 2 + 20, "putih", 32)
        grafis.tulis_teks("Tekan SPACE untuk mulai", lebar_layar / 2 - 140, tinggi_layar / 2 + 70, "kuning", 24)
    selesai
    jika menang maka
        grafis.tulis_teks("KAMU MENANG!", lebar_layar / 2 - 140, tinggi_layar / 2 - 60, "hijau", 48)
        grafis.tulis_teks("Skor: " + teks(skor), lebar_layar / 2 - 50, tinggi_layar / 2 + 10, "putih", 32)
        grafis.tulis_teks("Tekan SPACE untuk main lagi", lebar_layar / 2 - 160, tinggi_layar / 2 + 60, "kuning", 24)
    selesai
    jika game_started dan bukan game_over dan bukan menang maka
        # Bata
        buat i = 0
        selama i < bata_list.jumlah() lakukan
            buat b = bata_list[i]
            jika b.aktif maka
                grafis.segi_panjang(b.x, b.y, b.lebar, b.tinggi, b.warna)
            selesai
            i = i + 1
        selesai

        # Paddle
        grafis.segi_panjang(paddle_pos.x, paddle_pos.y, paddle_lebar, paddle_tinggi, "putih")

        # Bola
        grafis.lingkaran(bola_pos.x, bola_pos.y, bola_radius, "emas")

        # UI
        grafis.tulis_teks("Skor: " + teks(skor), 10, 10, "putih", 28)
        grafis.tulis_teks("Nyawa: " + teks(nyawa), lebar_layar - 120, 10, "merah", 28)
        grafis.tulis_teks("A/D atau LEFT/RIGHT untuk bergerak", 10, tinggi_layar - 30, "abu-abu", 18)
    selesai
selesai

# --- Main ---
game.buat_jendela(lebar_layar, tinggi_layar, "Brick Breaker - BroLang Game")
game.tambah_scene("utama", update, gambar)
game.ganti_scene("utama")
game.mulai()
