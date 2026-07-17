# ============================================
# SPACE DEFENDER v2 - BroLang Space Shooter
# ============================================
# Kontrol:
#   WASD / Arrow Keys - Gerak
#   Auto-fire         - Tembak otomatis
#   ENTER             - Mulai / Restart
#   ESC               - Pause / Resume
#
# Menjalankan:
#   bro run games/space_defender.bro
# ============================================

impor random
impor input sebagai masukan
impor grafis
impor game

# --- Konfigurasi ---
buat LEBAR = 800
buat TINGGI = 600
buat SPEED_PLAYER = 300
buat COOLDOWN_TEMBAK = 0.22
buat COOLDOWN_RAPID = 0.08
buat NYAWA_AWAL = 5
buat SPEED_PELURU = 500
buat SPEED_PELURU_MUSUH = 200
buat SPAWN_AWAL = 1.6
buat SPAWN_MIN = 0.3
buat BOSS_HP_DASAR = 30
buat BOSS_SPEED = 90
buat BOSS_TEMBAK_CD = 0.7
buat POWERUP_SPEED = 80
buat POWERUP_DURASI = 6.0
buat POWERUP_CHANCE = 0.22
buat COMBO_TIMEOUT = 2.5
buat INVINCIBLE_DURASI = 1.5

# --- State Game ---
buat state = "menu"
buat skor = 0
buat high_score = 0
buat nyawa = NYAWA_AWAL
buat wave = 1
buat wave_sisa = 0
buat wave_spawn_t = 0.0
buat wave_cd = SPAWN_AWAL
buat wave_info_t = 0.0
buat total_kill = 0

# --- Player ---
buat px = LEBAR / 2
buat py = TINGGI - 70
buat tembak_t = 0.0
buat invincible_t = 0.0
buat shake_x = 0.0
buat shake_y = 0.0
buat shake_timer = 0.0

# --- Combo ---
buat combo = 0
buat combo_timer = 0.0
buat combo_multiplier = 1

# --- List Entity ---
buat peluru_list = []
buat peluru_musuh = []
buat musuh_list = []
buat powerup_list = []
buat ledakan_list = []
buat score_popup_list = []

# --- Boss ---
buat boss_aktif = salah
buat boss_x = LEBAR / 2
buat boss_y = -80.0
buat boss_hp = 0
buat boss_max = 0
buat boss_arah = 1
buat boss_tembak_t = 0.0
buat boss_fase = 1

# --- Power-Up ---
buat shield_aktif = salah
buat rapid_fire = salah
buat triple_shot = salah
buat bomb_ready = salah
buat score_multiplier = 1
buat powerup_t = 0.0

# --- Efek ---
buat flash_timer = 0.0
buat go_timer = 0.0
buat bomb_flash = 0.0

# --- Bintang ---
buat bintang1 = []
buat bintang2 = []
buat bintang3 = []

# =============================================
#  INISIALISASI
# =============================================

fungsi init_bintang()
    buat b1 = []
    buat b2 = []
    buat b3 = []
    untuk i dalam range(0, 60) lakukan
        b1 = b1 + [{"x": random.randint(0, LEBAR), "y": random.randint(0, TINGGI)}]
    selesai
    untuk i dalam range(0, 35) lakukan
        b2 = b2 + [{"x": random.randint(0, LEBAR), "y": random.randint(0, TINGGI)}]
    selesai
    untuk i dalam range(0, 18) lakukan
        b3 = b3 + [{"x": random.randint(0, LEBAR), "y": random.randint(0, TINGGI)}]
    selesai
    bintang1 = b1
    bintang2 = b2
    bintang3 = b3
selesai

fungsi reset_game()
    state = "play"
    skor = 0
    nyawa = NYAWA_AWAL
    wave = 1
    px = LEBAR / 2
    py = TINGGI - 70
    tembak_t = 0.0
    invincible_t = 0.0
    shake_x = 0.0
    shake_y = 0.0
    shake_timer = 0.0
    combo = 0
    combo_timer = 0.0
    combo_multiplier = 1
    total_kill = 0
    peluru_list = []
    peluru_musuh = []
    musuh_list = []
    powerup_list = []
    ledakan_list = []
    score_popup_list = []
    boss_aktif = salah
    boss_hp = 0
    boss_max = 0
    boss_x = LEBAR / 2
    boss_y = -80.0
    boss_tembak_t = 0.0
    boss_fase = 1
    shield_aktif = salah
    rapid_fire = salah
    triple_shot = salah
    bomb_ready = salah
    score_multiplier = 1
    powerup_t = 0.0
    wave_sisa = 5 + wave * 3
    wave_spawn_t = 0.0
    wave_cd = SPAWN_AWAL
    wave_info_t = 2.5
    flash_timer = 0.0
    go_timer = 0.0
    bomb_flash = 0.0
selesai

# =============================================
#  UTILITY
# =============================================

fungsi mulai_shake(durasi)
    shake_timer = durasi
selesai

fungsi tambah_combo()
    combo = combo + 1
    combo_timer = COMBO_TIMEOUT
    jika combo >= 5 maka
        combo_multiplier = 2
    selesai
    jika combo >= 15 maka
        combo_multiplier = 3
    selesai
    jika combo >= 30 maka
        combo_multiplier = 5
    selesai
selesai

fungsi buat_score_popup(ex, ey, jumlah, warna)
    buat p = {"x": ex, "y": ey, "teks": "+" + teks(jumlah), "warna": warna, "umur": 1.0, "max_umur": 1.0}
    score_popup_list = score_popup_list + [p]
selesai

# =============================================
#  UPDATE BINTANG
# =============================================

fungsi update_bintang(dt)
    buat new1 = []
    buat ny = 0.0
    buat b_val = kosong
    untuk b dalam bintang1 lakukan
        ny = b.y + 25 * dt
        jika ny > TINGGI + 5 maka
            b_val = {"x": random.randint(0, LEBAR), "y": -3}
        lainnya
            b_val = {"x": b.x, "y": ny}
        selesai
        new1 = new1 + [b_val]
    selesai
    bintang1 = new1

    buat new2 = []
    untuk b dalam bintang2 lakukan
        ny = b.y + 55 * dt
        jika ny > TINGGI + 5 maka
            b_val = {"x": random.randint(0, LEBAR), "y": -3}
        lainnya
            b_val = {"x": b.x, "y": ny}
        selesai
        new2 = new2 + [b_val]
    selesai
    bintang2 = new2

    buat new3 = []
    untuk b dalam bintang3 lakukan
        ny = b.y + 95 * dt
        jika ny > TINGGI + 5 maka
            b_val = {"x": random.randint(0, LEBAR), "y": -3}
        lainnya
            b_val = {"x": b.x, "y": ny}
        selesai
        new3 = new3 + [b_val]
    selesai
    bintang3 = new3
selesai

# =============================================
#  SPAWN
# =============================================

fungsi spawn_musuh()
    buat jenis_r = random.randint(0, 11)
    buat m = kosong
    buat spx = random.randint(30, LEBAR - 30)

    jika jenis_r < 4 maka
        # Scout - cepat, ringan
        m = {"x": spx, "y": -20.0, "vx": random.randint(-40, 40), "vy": 130 + wave * 8, "hp": 1, "max_hp": 1, "jenis": "scout", "ukuran": 10, "tembak_cd": 0.0, "arah_zigzag": 1}
    lainnya jika jenis_r < 7 maka
        # Cruiser - sedang
        m = {"x": spx, "y": -20.0, "vx": random.randint(-25, 25), "vy": 75 + wave * 5, "hp": 2, "max_hp": 2, "jenis": "cruiser", "ukuran": 16, "tembak_cd": 0.0, "arah_zigzag": 1}
    lainnya jika jenis_r < 9 maka
        # Dreadnought - berat, lambat
        m = {"x": spx, "y": -20.0, "vx": random.randint(-15, 15), "vy": 45 + wave * 3, "hp": 3 + wave / 3, "max_hp": 3 + wave / 3, "jenis": "dreadnought", "ukuran": 22, "tembak_cd": 0.0, "arah_zigzag": 1}
    lainnya jika jenis_r < 11 maka
        # Bomber - tembak ke player, zigzag
        m = {"x": spx, "y": -20.0, "vx": 0, "vy": 60 + wave * 4, "hp": 2, "max_hp": 2, "jenis": "bomber", "ukuran": 14, "tembak_cd": 1.5, "arah_zigzag": 1}
    lainnya
        # Phantom - zigzag cepat
        m = {"x": spx, "y": -20.0, "vx": 80, "vy": 100 + wave * 6, "hp": 1, "max_hp": 1, "jenis": "phantom", "ukuran": 8, "tembak_cd": 0.0, "arah_zigzag": 1}
    selesai
    musuh_list = musuh_list + [m]
selesai

fungsi spawn_boss()
    boss_aktif = benar
    boss_max = BOSS_HP_DASAR + wave * 5
    boss_hp = boss_max
    boss_x = LEBAR / 2
    boss_y = -60.0
    boss_arah = 1
    boss_tembak_t = 1.5
    boss_fase = 1
selesai

fungsi coba_spawn_powerup(ex, ey)
    buat r = random.random()
    jika r < POWERUP_CHANCE maka
        buat jr = random.randint(0, 3)
        buat pu = kosong
        jika jr == 0 maka
            pu = {"x": ex, "y": ey, "jenis": "shield"}
        lainnya jika jr == 1 maka
            pu = {"x": ex, "y": ey, "jenis": "rapid"}
        lainnya jika jr == 2 maka
            pu = {"x": ex, "y": ey, "jenis": "triple"}
        lainnya
            pu = {"x": ex, "y": ey, "jenis": "bomb"}
        selesai
        powerup_list = powerup_list + [pu]
    selesai
selesai

fungsi buat_ledakan(ex, ey, warna, jumlah)
    untuk i dalam range(0, jumlah) lakukan
        buat spd = random.randint(40, 160)
        buat rx = random.randint(-spd, spd)
        buat ry = random.randint(-spd, spd)
        buat p = {"x": ex, "y": ey, "vx": rx, "vy": ry, "umur": 0.6, "max_umur": 0.7, "warna": warna, "ukuran": random.randint(2, 5)}
        ledakan_list = ledakan_list + [p]
    selesai
selesai

# =============================================
#  TEMBAK PLAYER
# =============================================

fungsi tembak_player()
    buat p = {"x": px, "y": py - 20, "vy": -SPEED_PELURU, "vx": 0}
    peluru_list = peluru_list + [p]
    jika triple_shot maka
        buat p2 = {"x": px - 14, "y": py - 15, "vy": -SPEED_PELURU * 0.95, "vx": -70}
        buat p3 = {"x": px + 14, "y": py - 15, "vy": -SPEED_PELURU * 0.95, "vx": 70}
        peluru_list = peluru_list + [p2]
        peluru_list = peluru_list + [p3]
    selesai
selesai

# =============================================
#  BOMB
# =============================================

fungsi activate_bomb()
    bomb_flash = 0.5
    shake_timer = 0.4

    # Hancurkan semua musuh biasa
    buat new_musuh = []
    untuk m dalam musuh_list lakukan
        skor = skor + 15
        buat_ledakan(m.x, m.y, "emas", 10)
        buat_score_popup(m.x, m.y, 15, "emas")
    selesai
    musuh_list = []

    # Damage boss
    jika boss_aktif maka
        boss_hp = boss_hp - 10
        buat_ledakan(boss_x, boss_y, "emas", 20)
        buat_score_popup(boss_x, boss_y, 10, "emas")
        jika boss_hp <= 0 maka
            boss_aktif = salah
            skor = skor + 200 + wave * 20
            buat_ledakan(boss_x, boss_y, "emas", 30)
            buat_ledakan(boss_x - 30, boss_y - 20, "jingga", 15)
            buat_ledakan(boss_x + 30, boss_y + 20, "merah", 15)
        selesai
    selesai

    # Hancurkan semua peluru musuh
    peluru_musuh = []
    bomb_ready = salah
selesai

# =============================================
#  UPDATE PLAYER
# =============================================

fungsi update_player(dt)
    jika masukan.tombol_ditekan("a") atau masukan.tombol_ditekan("LEFT") maka
        px = px - SPEED_PLAYER * dt
    selesai
    jika masukan.tombol_ditekan("d") atau masukan.tombol_ditekan("RIGHT") maka
        px = px + SPEED_PLAYER * dt
    selesai
    jika masukan.tombol_ditekan("w") atau masukan.tombol_ditekan("UP") maka
        py = py - SPEED_PLAYER * dt
    selesai
    jika masukan.tombol_ditekan("s") atau masukan.tombol_ditekan("DOWN") maka
        py = py + SPEED_PLAYER * dt
    selesai

    jika px < 20 maka px = 20 selesai
    jika px > LEBAR - 20 maka px = LEBAR - 20 selesai
    jika py < 30 maka py = 30 selesai
    jika py > TINGGI - 30 maka py = TINGGI - 30 selesai

    tembak_t = tembak_t - dt
    jika tembak_t <= 0 maka
        tembak_player()
        jika rapid_fire maka
            tembak_t = COOLDOWN_RAPID
        lainnya
            tembak_t = COOLDOWN_TEMBAK
        selesai
    selesai
selesai

# =============================================
#  UPDATE PELURU
# =============================================

fungsi update_peluru(dt)
    buat baru = []
    buat ny = 0.0
    buat nx = 0.0
    buat np = kosong
    untuk p dalam peluru_list lakukan
        ny = p.y + p.vy * dt
        nx = p.x
        jika p.vx != 0 maka
            nx = p.x + p.vx * dt
        selesai
        np = {"x": nx, "y": ny, "vy": p.vy, "vx": p.vx}
        jika ny > -20 dan ny < TINGGI + 20 dan nx > -20 dan nx < LEBAR + 20 maka
            baru = baru + [np]
        selesai
    selesai
    peluru_list = baru

    buat baru2 = []
    untuk p dalam peluru_musuh lakukan
        ny = p.y + p.vy * dt
        nx = p.x
        jika p.vx != 0 maka
            nx = p.x + p.vx * dt
        selesai
        np = {"x": nx, "y": ny, "vy": p.vy, "vx": p.vx}
        jika ny > -20 dan ny < TINGGI + 20 maka
            baru2 = baru2 + [np]
        selesai
    selesai
    peluru_musuh = baru2
selesai

# =============================================
#  UPDATE MUSUH
# =============================================

fungsi update_musuh(dt)
    buat baru = []
    buat nx = 0.0
    buat ny = 0.0
    buat nvx = 0.0
    buat m2 = kosong
    buat waktu_sekarang = game.waktu_sekarang() / 1000.0

    untuk m dalam musuh_list lakukan
        nx = m.x + m.vx * dt
        ny = m.y + m.vy * dt
        nvx = m.vx

        # Zigzag untuk phantom dan bomber
        jika m.jenis == "phantom" maka
            nx = m.x + m.vx * dt * m.arah_zigzag
            ny = m.y + m.vy * dt
            nvx = m.vx
            buat new_zigzag = m.arah_zigzag
            jika nx < m.ukuran maka
                nx = m.ukuran
                new_zigzag = -1
            selesai
            jika nx > LEBAR - m.ukuran maka
                nx = LEBAR - m.ukuran
                new_zigzag = 1
            selesai
            m2 = {"x": nx, "y": ny, "vx": nvx, "vy": m.vy, "hp": m.hp, "max_hp": m.max_hp, "jenis": m.jenis, "ukuran": m.ukuran, "tembak_cd": m.tembak_cd, "arah_zigzag": new_zigzag}
            jika ny < TINGGI + 50 maka
                baru = baru + [m2]
            selesai
        selesai

        jika m.jenis == "bomber" maka
            nx = m.x + 50 * m.arah_zigzag * dt
            nvx = 50 * m.arah_zigzag
            jika nx < m.ukuran maka
                nx = m.ukuran
            selesai
            jika nx > LEBAR - m.ukuran maka
                nx = LEBAR - m.ukuran
            selesai

            # Bomber tembak ke player
            buat new_cd = m.tembak_cd - dt
            jika new_cd <= 0 dan m.y > 10 dan m.y < TINGGI - 100 maka
                buat bdx = px - m.x
                buat bdy = py - m.y
                buat bjkk = bdx * bdx + bdy * bdy
                jika bjkk > 0 maka
                    buat bjr = bjkk ** 0.5
                    buat bnx = bdx / bjr
                    buat bny = bdy / bjr
                    buat bp = {"x": m.x, "y": m.y + m.ukuran, "vx": bnx * 180, "vy": bny * 180}
                    peluru_musuh = peluru_musuh + [bp]
                selesai
                new_cd = 2.0
            selesai
            m2 = {"x": nx, "y": ny, "vx": nvx, "vy": m.vy, "hp": m.hp, "max_hp": m.max_hp, "jenis": m.jenis, "ukuran": m.ukuran, "tembak_cd": new_cd, "arah_zigzag": m.arah_zigzag}
            jika ny < TINGGI + 50 maka
                baru = baru + [m2]
            selesai
        selesai

        jika m.jenis != "phantom" dan m.jenis != "bomber" maka
            jika nx < m.ukuran maka
                nx = m.ukuran
                nvx = m.vx * -1
            selesai
            jika nx > LEBAR - m.ukuran maka
                nx = LEBAR - m.ukuran
                nvx = m.vx * -1
            selesai
            m2 = {"x": nx, "y": ny, "vx": nvx, "vy": m.vy, "hp": m.hp, "max_hp": m.max_hp, "jenis": m.jenis, "ukuran": m.ukuran, "tembak_cd": m.tembak_cd, "arah_zigzag": m.arah_zigzag}
            jika ny < TINGGI + 50 maka
                baru = baru + [m2]
            selesai
        selesai
    selesai
    musuh_list = baru
selesai

# =============================================
#  UPDATE BOSS
# =============================================

fungsi update_boss(dt)
    jika boss_aktif == salah maka
        kembali
    selesai

    jika boss_y < 60 maka
        boss_y = boss_y + 60 * dt
    lainnya
        boss_x = boss_x + BOSS_SPEED * boss_arah * dt
        jika boss_x > LEBAR - 60 maka
            boss_arah = -1
        selesai
        jika boss_x < 60 maka
            boss_arah = 1
        selesai

        # Update fase boss berdasarkan HP
        buat hp_ratio = boss_hp * 100 / boss_max
        jika hp_ratio < 30 maka
            boss_fase = 3
        lainnya jika hp_ratio < 60 maka
            boss_fase = 2
        lainnya
            boss_fase = 1
        selesai

        boss_tembak_t = boss_tembak_t - dt
        jika boss_tembak_t <= 0 maka
            # Fase 1: tembak lurus
            buat p1 = {"x": boss_x - 20, "y": boss_y + 30, "vy": SPEED_PELURU_MUSUH, "vx": 0}
            buat p2 = {"x": boss_x + 20, "y": boss_y + 30, "vy": SPEED_PELURU_MUSUH, "vx": 0}
            peluru_musuh = peluru_musuh + [p1]
            peluru_musuh = peluru_musuh + [p2]

            # Aimed shot ke player
            buat dx = px - boss_x
            buat dy = py - boss_y
            buat jk = dx * dx + dy * dy
            jika jk > 0 maka
                buat jr = jk ** 0.5
                buat nx2 = dx / jr
                buat ny2 = dy / jr
                buat p3 = {"x": boss_x, "y": boss_y + 30, "vx": nx2 * 160, "vy": ny2 * 160}
                peluru_musuh = peluru_musuh + [p3]
            selesai

            # Fase 2+: spread shot
            jika boss_fase >= 2 maka
                buat spread = 0.4
                untuk s dalam range(-2, 3) lakukan
                    buat sx = s * spread
                    buat p4 = {"x": boss_x, "y": boss_y + 30, "vx": sx * 100, "vy": SPEED_PELURU_MUSUH * 0.8}
                    peluru_musuh = peluru_musuh + [p4]
                selesai
            selesai

            # Fase 3+: additional spiral bullets
            jika boss_fase >= 3 maka
                buat sdx = boss_x - LEBAR / 2
                buat p5 = {"x": boss_x, "y": boss_y + 30, "vx": sdx * 0.5, "vy": SPEED_PELURU_MUSUH * 0.9}
                buat p6 = {"x": boss_x, "y": boss_y + 30, "vx": sdx * -0.5, "vy": SPEED_PELURU_MUSUH * 0.9}
                peluru_musuh = peluru_musuh + [p5]
                peluru_musuh = peluru_musuh + [p6]
            selesai

            boss_tembak_t = BOSS_TEMBAK_CD - boss_fase * 0.1
        selesai
    selesai
selesai

# =============================================
#  UPDATE POWER-UP
# =============================================

fungsi update_powerup(dt)
    buat baru = []
    buat ny = 0.0
    buat dx = 0.0
    buat dy = 0.0
    buat hit = salah
    buat np = kosong
    untuk pu dalam powerup_list lakukan
        ny = pu.y + POWERUP_SPEED * dt
        dx = pu.x - px
        dy = ny - py
        hit = dx * dx + dy * dy < 400

        jika hit maka
            jika pu.jenis == "shield" maka
                shield_aktif = benar
            lainnya jika pu.jenis == "rapid" maka
                rapid_fire = benar
                triple_shot = salah
            lainnya jika pu.jenis == "triple" maka
                triple_shot = benar
                rapid_fire = salah
            lainnya jika pu.jenis == "bomb" maka
                bomb_ready = benar
            selesai
            powerup_t = POWERUP_DURASI
            buat p = {"x": pu.x, "y": ny, "vx": 0, "vy": -30, "umur": 0.5, "max_umur": 0.5, "warna": "kuning", "ukuran": 3}
            ledakan_list = ledakan_list + [p]
        lainnya jika ny < TINGGI + 20 maka
            np = {"x": pu.x, "y": ny, "jenis": pu.jenis}
            baru = baru + [np]
        selesai
    selesai
    powerup_list = baru

    jika powerup_t > 0 maka
        powerup_t = powerup_t - dt
        jika powerup_t <= 0 maka
            shield_aktif = salah
            rapid_fire = salah
            triple_shot = salah
        selesai
    selesai
selesai

# =============================================
#  GAME OVER
# =============================================

fungsi game_over()
    state = "gameover"
    jika skor > high_score maka
        high_score = skor
    selesai
    go_timer = 0.0
    shake_timer = 0.6
selesai

# =============================================
#  TABRAKAN
# =============================================

fungsi cek_tabrakan()
    buat peluru_baru = []
    buat dx = 0.0
    buat dy = 0.0
    buat dist = 0.0
    buat tj = 0.0
    buat kena = salah
    buat musuh_baru = []
    buat mhp = 0
    buat skor_dapat = 0

    untuk p dalam peluru_list lakukan
        kena = salah
        musuh_baru = []
        untuk m dalam musuh_list lakukan
            dx = p.x - m.x
            dy = p.y - m.y
            dist = dx * dx + dy * dy
            tj = m.ukuran + 4
            jika dist < tj * tj maka
                kena = benar
                mhp = m.hp - 1
                # Hit flash
                buat p_hit = {"x": m.x, "y": m.y, "vx": 0, "vy": 0, "umur": 0.15, "max_umur": 0.15, "warna": "putih", "ukuran": m.ukuran}
                ledakan_list = ledakan_list + [p_hit]
                jika mhp <= 0 maka
                    tambah_combo()
                    skor_dapat = 0
                    jika m.jenis == "scout" maka
                        skor_dapat = 10 * combo_multiplier
                        skor = skor + skor_dapat
                        buat_ledakan(m.x, m.y, "hijau", 6)
                    lainnya jika m.jenis == "cruiser" maka
                        skor_dapat = 25 * combo_multiplier
                        skor = skor + skor_dapat
                        buat_ledakan(m.x, m.y, "jingga", 10)
                    lainnya jika m.jenis == "dreadnought" maka
                        skor_dapat = 50 * combo_multiplier
                        skor = skor + skor_dapat
                        buat_ledakan(m.x, m.y, "merah", 14)
                    lainnya jika m.jenis == "bomber" maka
                        skor_dapat = 35 * combo_multiplier
                        skor = skor + skor_dapat
                        buat_ledakan(m.x, m.y, "ungu", 10)
                    lainnya jika m.jenis == "phantom" maka
                        skor_dapat = 20 * combo_multiplier
                        skor = skor + skor_dapat
                        buat_ledakan(m.x, m.y, "langit", 8)
                    selesai
                    total_kill = total_kill + 1
                    buat_score_popup(m.x, m.y - 10, skor_dapat, "kuning")
                    coba_spawn_powerup(m.x, m.y)
                    mulai_shake(0.08)
                lainnya
                    musuh_baru = musuh_baru + [{"x": m.x, "y": m.y, "vx": m.vx, "vy": m.vy, "hp": mhp, "max_hp": m.max_hp, "jenis": m.jenis, "ukuran": m.ukuran, "tembak_cd": m.tembak_cd, "arah_zigzag": m.arah_zigzag}]
                selesai
            lainnya
                musuh_baru = musuh_baru + [m]
            selesai
        selesai
        musuh_list = musuh_baru
        jika kena == salah maka
            peluru_baru = peluru_baru + [p]
        selesai
    selesai
    peluru_list = peluru_baru

    # Peluru player vs boss
    jika boss_aktif maka
        buat pb2 = []
        untuk p dalam peluru_list lakukan
            dx = p.x - boss_x
            dy = p.y - boss_y
            dist = dx * dx + dy * dy
            jika dist < 3600 maka
                boss_hp = boss_hp - 1
                buat p_hit = {"x": p.x, "y": p.y, "vx": 0, "vy": 0, "umur": 0.2, "max_umur": 0.2, "warna": "kuning", "ukuran": 4}
                ledakan_list = ledakan_list + [p_hit]
                mulai_shake(0.05)
                jika boss_hp <= 0 maka
                    boss_aktif = salah
                    skor = skor + 200 + wave * 20
                    buat_ledakan(boss_x, boss_y, "emas", 30)
                    buat_ledakan(boss_x - 30, boss_y - 20, "jingga", 15)
                    buat_ledakan(boss_x + 30, boss_y + 20, "merah", 15)
                    shake_timer = 0.5
                    bomb_flash = 0.3
                selesai
            lainnya
                pb2 = pb2 + [p]
            selesai
        selesai
        peluru_list = pb2
    selesai

    # Peluru musuh vs player
    buat pmb = []
    untuk p dalam peluru_musuh lakukan
        dx = p.x - px
        dy = p.y - py
        dist = dx * dx + dy * dy
        jika dist < 400 maka
            jika invincible_t <= 0 maka
                jika shield_aktif maka
                    shield_aktif = salah
                    flash_timer = 0.3
                    invincible_t = 0.5
                    buat_ledakan(px, py, "biru", 8)
                    mulai_shake(0.15)
                lainnya
                    nyawa = nyawa - 1
                    flash_timer = 0.4
                    invincible_t = INVINCIBLE_DURASI
                    combo = 0
                    combo_multiplier = 1
                    buat_ledakan(px, py, "merah", 12)
                    mulai_shake(0.25)
                    jika nyawa <= 0 maka
                        game_over()
                    selesai
                selesai
            selesai
        lainnya
            pmb = pmb + [p]
        selesai
    selesai
    peluru_musuh = pmb

    # Musuh vs player
    buat mb2 = []
    untuk m dalam musuh_list lakukan
        dx = m.x - px
        dy = m.y - py
        dist = dx * dx + dy * dy
        tj = m.ukuran + 15
        jika dist < tj * tj maka
            jika invincible_t <= 0 maka
                jika shield_aktif maka
                    shield_aktif = salah
                    flash_timer = 0.3
                    invincible_t = 0.5
                    buat_ledakan(m.x, m.y, "putih", 6)
                    mulai_shake(0.15)
                lainnya
                    nyawa = nyawa - 1
                    flash_timer = 0.4
                    invincible_t = INVINCIBLE_DURASI
                    combo = 0
                    combo_multiplier = 1
                    buat_ledakan(px, py, "merah", 12)
                    mulai_shake(0.25)
                    jika nyawa <= 0 maka
                        game_over()
                    selesai
                selesai
            selesai
            buat_ledakan(m.x, m.y, "putih", 6)
        lainnya
            mb2 = mb2 + [m]
        selesai
    selesai
    musuh_list = mb2
selesai

# =============================================
#  UPDATE LEDAKAN & SCORE POPUP
# =============================================

fungsi update_ledakan(dt)
    buat baru = []
    buat nu = 0.0
    buat nx = 0.0
    buat ny = 0.0
    buat np = kosong
    untuk p dalam ledakan_list lakukan
        nu = p.umur - dt
        jika nu > 0 maka
            nx = p.x + p.vx * dt
            ny = p.y + p.vy * dt
            np = {"x": nx, "y": ny, "vx": p.vx, "vy": p.vy, "umur": nu, "max_umur": p.max_umur, "warna": p.warna, "ukuran": p.ukuran}
            baru = baru + [np]
        selesai
    selesai
    ledakan_list = baru
selesai

fungsi update_score_popup(dt)
    buat baru = []
    buat nu = 0.0
    buat np = kosong
    untuk sp dalam score_popup_list lakukan
        nu = sp.umur - dt
        jika nu > 0 maka
            np = {"x": sp.x, "y": sp.y - 40 * dt, "teks": sp.teks, "warna": sp.warna, "umur": nu, "max_umur": sp.max_umur}
            baru = baru + [np]
        selesai
    selesai
    score_popup_list = baru
selesai

# =============================================
#  WAVE MANAGEMENT
# =============================================

fungsi update_wave(dt)
    jika wave_info_t > 0 maka
        wave_info_t = wave_info_t - dt
    selesai

    # Boss wave
    jika wave % 5 == 0 dan boss_aktif == salah dan len(musuh_list) == 0 dan wave_sisa <= 0 maka
        spawn_boss()
        wave_info_t = 2.0
        kembali
    selesai

    jika boss_aktif maka
        kembali
    selesai

    jika wave_sisa > 0 maka
        wave_spawn_t = wave_spawn_t - dt
        jika wave_spawn_t <= 0 maka
            spawn_musuh()
            wave_sisa = wave_sisa - 1
            wave_spawn_t = wave_cd
        selesai
    lainnya jika len(musuh_list) == 0 maka
        wave = wave + 1
        wave_sisa = 5 + wave * 3
        wave_cd = SPAWN_AWAL - wave * 0.04
        jika wave_cd < SPAWN_MIN maka
            wave_cd = SPAWN_MIN
        selesai
        wave_spawn_t = 1.5
        wave_info_t = 2.0
    selesai
selesai

# =============================================
#  UPDATE UTAMA
# =============================================

fungsi update(dt)
    update_bintang(dt)

    jika state == "menu" maka
        jika masukan.tombol_baru_ditekan("ENTER") maka
            init_bintang()
            reset_game()
        selesai
    lainnya jika state == "play" maka
        # Pause
        jika masukan.tombol_baru_ditekan("ESC") maka
            state = "pause"
            kembali
        selesai

        # Bomb activation
        jika bomb_ready dan masukan.tombol_baru_ditekan("SPACE") maka
            activate_bomb()
        selesai

        # Invincibility timer
        jika invincible_t > 0 maka
            invincible_t = invincible_t - dt
        selesai

        # Shake timer
        jika shake_timer > 0 maka
            shake_timer = shake_timer - dt
            shake_x = random.randint(-4, 4)
            shake_y = random.randint(-4, 4)
        lainnya
            shake_x = 0.0
            shake_y = 0.0
        selesai

        # Bomb flash
        jika bomb_flash > 0 maka
            bomb_flash = bomb_flash - dt
        selesai

        # Combo timer
        jika combo_timer > 0 maka
            combo_timer = combo_timer - dt
            jika combo_timer <= 0 maka
                combo = 0
                combo_multiplier = 1
            selesai
        selesai

        update_player(dt)
        update_peluru(dt)
        update_musuh(dt)
        update_boss(dt)
        update_powerup(dt)
        cek_tabrakan()
        update_ledakan(dt)
        update_score_popup(dt)
        update_wave(dt)
        jika flash_timer > 0 maka
            flash_timer = flash_timer - dt
        selesai
    lainnya jika state == "pause" maka
        jika masukan.tombol_baru_ditekan("ESC") atau masukan.tombol_baru_ditekan("ENTER") maka
            state = "play"
        selesai
    lainnya jika state == "gameover" maka
        update_ledakan(dt)
        update_score_popup(dt)
        go_timer = go_timer + dt
        jika shake_timer > 0 maka
            shake_timer = shake_timer - dt
            shake_x = random.randint(-3, 3)
            shake_y = random.randint(-3, 3)
        lainnya
            shake_x = 0.0
            shake_y = 0.0
        selesai
        jika go_timer > 1.0 dan masukan.tombol_baru_ditekan("ENTER") maka
            state = "menu"
        selesai
    selesai
selesai

# =============================================
#  DRAW MENU
# =============================================

fungsi gambar_menu()
    grafis.tulis_teks("SPACE", LEBAR / 2 - 100, 150, "cyan", 72)
    grafis.tulis_teks("DEFENDER", LEBAR / 2 - 160, 220, "putih", 72)
    grafis.tulis_teks("v2", LEBAR / 2 + 130, 220, "abu-abu_terang", 36)
    jika high_score > 0 maka
        grafis.tulis_teks("High Score: " + teks(high_score), LEBAR / 2 - 80, 310, "emas", 28)
    selesai
    grafis.tulis_teks("Tekan ENTER untuk mulai", LEBAR / 2 - 130, 370, "hijau", 28)
    grafis.tulis_teks("WASD / Arrow Keys : Gerak", LEBAR / 2 - 140, 430, "abu-abu_terang", 20)
    grafis.tulis_teks("Auto-fire          : Tembak", LEBAR / 2 - 140, 455, "abu-abu_terang", 20)
    grafis.tulis_teks("ESC                : Pause", LEBAR / 2 - 140, 480, "abu-abu_terang", 20)
    grafis.tulis_teks("Kill combo = Skor lebih banyak!", LEBAR / 2 - 140, 510, "emas", 18)
    grafis.segitiga(LEBAR / 2, 100, LEBAR / 2 - 20, 130, LEBAR / 2 + 20, 130, "cyan")
    grafis.segi_panjang(LEBAR / 2 - 8, 130, 16, 8, "biru")
selesai

# =============================================
#  DRAW PLAYER
# =============================================

fungsi gambar_player()
    # Invincibility blink
    jika invincible_t > 0 maka
        buat blink = angka(invincible_t * 10) % 2
        jika blink == 0 maka
            kembali
        selesai
    selesai

    grafis.segitiga(px, py - 22, px - 18, py + 12, px + 18, py + 12, "cyan")
    grafis.segi_panjang(px - 5, py - 10, 10, 12, grafis.buat_warna(100, 200, 255))
    grafis.segitiga(px - 18, py + 12, px - 28, py + 18, px - 12, py + 18, "biru")
    grafis.segitiga(px + 18, py + 12, px + 28, py + 18, px + 12, py + 18, "biru")
    buat at = 5 + random.randint(0, 6)
    grafis.segi_panjang(px - 6, py + 12, 12, at, "kuning")
    grafis.segi_panjang(px - 3, py + 12 + at, 6, 3, "jingga")
selesai

# =============================================
#  DRAW GAME OVER
# =============================================

fungsi gambar_gameover()
    grafis.segi_panjang(0, TINGGI / 2 - 100, LEBAR, 200, grafis.buat_warna(0, 0, 0))
    grafis.tulis_teks("GAME OVER", LEBAR / 2 - 120, TINGGI / 2 - 70, "merah", 48)
    grafis.tulis_teks("Skor: " + teks(skor), LEBAR / 2 - 60, TINGGI / 2 - 15, "putih", 32)
    grafis.tulis_teks("Wave: " + teks(wave) + "  |  Kill: " + teks(total_kill), LEBAR / 2 - 100, TINGGI / 2 + 15, "abu-abu_terang", 22)
    jika combo_multiplier > 1 maka
        grafis.tulis_teks("Max Combo: x" + teks(combo_multiplier), LEBAR / 2 - 70, TINGGI / 2 + 40, "emas", 20)
    selesai
    jika skor >= high_score dan skor > 0 maka
        grafis.tulis_teks("NEW HIGH SCORE!", LEBAR / 2 - 100, TINGGI / 2 + 65, "emas", 24)
    selesai
    jika go_timer > 1.0 maka
        grafis.tulis_teks("Tekan ENTER untuk kembali", LEBAR / 2 - 150, TINGGI / 2 + 85, "hijau", 20)
    selesai
selesai

# =============================================
#  DRAW PAUSE
# =============================================

fungsi gambar_pause()
    grafis.segi_panjang(0, TINGGI / 2 - 60, LEBAR, 120, grafis.buat_warna(0, 0, 0))
    grafis.tulis_teks("PAUSED", LEBAR / 2 - 70, TINGGI / 2 - 35, "kuning", 48)
    grafis.tulis_teks("Tekan ESC atau ENTER untuk lanjut", LEBAR / 2 - 170, TINGGI / 2 + 20, "abu-abu_terang", 22)
selesai

# =============================================
#  DRAW PLAY
# =============================================

fungsi gambar_play()
    # Peluru player (dengan glow effect)
    untuk p dalam peluru_list lakukan
        grafis.segi_panjang(p.x - 3, p.y - 7, 6, 14, grafis.buat_warna(0, 100, 150))
        grafis.segi_panjang(p.x - 2, p.y - 6, 4, 12, "cyan")
        grafis.segi_panjang(p.x - 1, p.y - 8, 2, 4, "putih")
    selesai

    # Peluru musuh
    untuk p dalam peluru_musuh lakukan
        grafis.segi_panjang(p.x - 3, p.y - 5, 6, 10, grafis.buat_warna(150, 0, 0))
        grafis.segi_panjang(p.x - 2, p.y - 4, 4, 8, "merah")
    selesai

    # Power-up (dengan ikon lebih jelas)
    untuk pu dalam powerup_list lakukan
        # Glow effect
        grafis.lingkaran(pu.x, pu.y, 12, grafis.buat_warna(50, 50, 50))
        jika pu.jenis == "shield" maka
            grafis.lingkaran(pu.x, pu.y, 8, "biru")
            grafis.lingkaran(pu.x, pu.y, 4, grafis.buat_warna(150, 200, 255))
        selesai
        jika pu.jenis == "rapid" maka
            grafis.segi_panjang(pu.x - 6, pu.y - 6, 12, 12, "kuning")
            grafis.tulis_teks("R", pu.x - 4, pu.y - 5, "hitam", 12)
        selesai
        jika pu.jenis == "triple" maka
            grafis.segitiga(pu.x, pu.y - 8, pu.x - 8, pu.y + 6, pu.x + 8, pu.y + 6, "hijau")
        selesai
        jika pu.jenis == "bomb" maka
            grafis.lingkaran(pu.x, pu.y, 8, "jingga")
            grafis.lingkaran(pu.x, pu.y, 4, "merah")
            grafis.tulis_teks("!", pu.x - 3, pu.y - 5, "kuning", 14)
        selesai
    selesai

    # Musuh dengan variasi lebih bagus
    untuk m dalam musuh_list lakukan
        jika m.jenis == "scout" maka
            grafis.segi_panjang(m.x - m.ukuran, m.y - m.ukuran / 2, m.ukuran * 2, m.ukuran, "hijau")
            grafis.segi_panjang(m.x - 2, m.y - m.ukuran / 2 - 3, 4, 3, "hijau")
        selesai
        jika m.jenis == "cruiser" maka
            grafis.segi_panjang(m.x - m.ukuran, m.y - m.ukuran * 0.7, m.ukuran * 2, m.ukuran * 1.4, "jingga")
            grafis.segitiga(m.x, m.y - m.ukuran * 0.7, m.x - m.ukuran * 0.5, m.y - m.ukuran * 1.1, m.x + m.ukuran * 0.5, m.y - m.ukuran * 1.1, "kuning")
        selesai
        jika m.jenis == "dreadnought" maka
            grafis.segi_panjang(m.x - m.ukuran, m.y - m.ukuran * 0.8, m.ukuran * 2, m.ukuran * 1.6, "merah")
            grafis.segi_panjang(m.x - m.ukuran * 0.5, m.y - m.ukuran * 1.0, m.ukuran, m.ukuran * 0.4, "jingga")
        selesai
        jika m.jenis == "bomber" maka
            grafis.segitiga(m.x, m.y + m.ukuran, m.x - m.ukuran, m.y - m.ukuran * 0.5, m.x + m.ukuran, m.y - m.ukuran * 0.5, "ungu")
            grafis.lingkaran(m.x, m.y, 3, "merah")
        selesai
        jika m.jenis == "phantom" maka
            grafis.segitiga(m.x, m.y + m.ukuran, m.x - m.ukuran, m.y, m.x + m.ukuran, m.y, "langit")
        selesai

        # Health bar universal
        jika m.hp < m.max_hp maka
            buat hl = m.ukuran * 2
            buat hi = m.hp * hl / m.max_hp
            grafis.segi_panjang(m.x - m.ukuran, m.y - m.ukuran - 5, hl, 3, "abu-abu_gelap")
            grafis.segi_panjang(m.x - m.ukuran, m.y - m.ukuran - 5, hi, 3, "hijau")
        selesai
    selesai

    # Boss dengan visual lebih detail
    jika boss_aktif maka
        # Boss body
        grafis.segi_panjang(boss_x - 45, boss_y - 22, 90, 44, "merah_gelap")
        grafis.segi_panjang(boss_x - 35, boss_y - 17, 70, 34, "merah")
        grafis.segi_panjang(boss_x - 15, boss_y - 28, 30, 12, "jingga")
        # Boss wings
        grafis.segitiga(boss_x - 35, boss_y, boss_x - 55, boss_y + 15, boss_x - 35, boss_y + 15, "merah_gelap")
        grafis.segitiga(boss_x + 35, boss_y, boss_x + 55, boss_y + 15, boss_x + 35, boss_y + 15, "merah_gelap")
        # Boss eye
        grafis.lingkaran(boss_x, boss_y, 5, "kuning")

        # HP bar
        buat bhl = 140
        buat bhi = boss_hp * bhl / boss_max
        grafis.segi_panjang(LEBAR / 2 - bhl / 2 - 1, 7, bhl + 2, 10, "abu-abu_gelap")
        grafis.segi_panjang(LEBAR / 2 - bhl / 2, 8, bhi, 8, "merah")
        grafis.tulis_teks("BOSS  HP: " + teks(boss_hp) + "/" + teks(boss_max), LEBAR / 2 - 70, 20, "putih", 16)
        # Fase indicator
        jika boss_fase >= 2 maka
            grafis.tulis_teks("FASE " + teks(boss_fase), LEBAR / 2 - 25, 34, "jingga", 14)
        selesai
    selesai

    # Player
    gambar_player()

    # Ledakan
    untuk p dalam ledakan_list lakukan
        buat sk = p.umur / p.max_umur
        buat uk = p.ukuran * sk
        grafis.lingkaran(p.x, p.y, uk, p.warna)
        jika uk > 4 maka
            grafis.lingkaran(p.x, p.y, uk * 0.5, "putih")
        selesai
    selesai

    # Score popup
    untuk sp dalam score_popup_list lakukan
        buat alpha_sk = sp.umur / sp.max_umur
        grafis.tulis_teks(sp.teks, sp.x - 15, sp.y, sp.warna, angka(14 + alpha_sk * 6))
    selesai

    # Shield visual
    jika shield_aktif maka
        grafis.lingkaran(px, py, 28, grafis.buat_warna(50, 100, 255))
        grafis.lingkaran(px, py, 24, grafis.buat_warna(80, 150, 255))
    selesai

    # HUD
    grafis.tulis_teks("Skor: " + teks(skor), 10, 10, "putih", 24)

    # Nyawa (hati)
    untuk i dalam range(0, nyawa) lakukan
        buat hx = LEBAR - 30 - i * 30
        grafis.segitiga(hx, 25, hx - 8, 40, hx + 8, 40, "merah")
    selesai

    # Wave info
    grafis.tulis_teks("WAVE " + teks(wave), LEBAR / 2 - 40, 55, "abu-abu_terang", 20)

    # Combo
    jika combo >= 3 maka
        grafis.tulis_teks("COMBO x" + teks(combo_multiplier) + " (" + teks(combo) + ")", 10, 35, "emas", 22)
    selesai

    # Bomb indicator
    jika bomb_ready maka
        grafis.tulis_teks("[BOMB READY - Tekan SPACE]", LEBAR / 2 - 110, TINGGI - 55, "jingga", 18)
    selesai

    # Wave announcement
    jika wave_info_t > 0 maka
        buat st = wave_info_t
        jika st > 1.0 maka st = 1.0 selesai
        buat ut = 48 + st * 12
        jika wave % 5 == 0 dan boss_aktif == salah maka
            grafis.tulis_teks("WAVE " + teks(wave) + " - BOSS!", LEBAR / 2 - 120, TINGGI / 2 - 30, "merah", ut)
        lainnya
            grafis.tulis_teks("WAVE " + teks(wave), LEBAR / 2 - 60, TINGGI / 2 - 30, "putih", ut)
        selesai
    selesai

    # Power-up status
    jika powerup_t > 0 maka
        grafis.tulis_teks("Power-Up: " + teks(angka(powerup_t)) + "s", 10, TINGGI - 30, "kuning", 20)
    selesai

    # Kill counter
    grafis.tulis_teks("Kill: " + teks(total_kill), LEBAR - 100, TINGGI - 30, "abu-abu_terang", 18)

    # FPS
    grafis.tulis_teks("FPS: " + teks(angka(grafis.dapatkan_fps())), 10, TINGGI - 10, "abu-abu", 14)
selesai

# =============================================
#  DRAW UTAMA
# =============================================

fungsi gambar(screen)
    # Screen shake offset
    grafis.bersihkan(grafis.buat_warna(5, 5, 15))

    untuk b dalam bintang1 lakukan
        grafis.segi_panjang(b.x + shake_x, b.y + shake_y, 1, 1, grafis.buat_warna(50, 50, 80))
    selesai
    untuk b dalam bintang2 lakukan
        grafis.segi_panjang(b.x + shake_x, b.y + shake_y, 2, 2, grafis.buat_warna(80, 80, 120))
    selesai
    untuk b dalam bintang3 lakukan
        grafis.segi_panjang(b.x + shake_x, b.y + shake_y, 2, 3, grafis.buat_warna(120, 120, 180))
    selesai

    # Terapkan shake ke game objects
    grafis.segi_panjang(-10, -10, LEBAR + 20, TINGGI + 20, grafis.buat_warna(5, 5, 15))

    jika state == "menu" maka
        gambar_menu()
    lainnya jika state == "play" maka
        gambar_play()
    lainnya jika state == "pause" maka
        gambar_play()
        gambar_pause()
    lainnya jika state == "gameover" maka
        gambar_play()
        gambar_gameover()
    selesai

    # Flash effect
    jika flash_timer > 0 maka
        grafis.segi_panjang(0, 0, LEBAR, TINGGI, grafis.buat_warna(255, 50, 50))
    selesai

    # Bomb flash
    jika bomb_flash > 0 maka
        grafis.segi_panjang(0, 0, LEBAR, TINGGI, grafis.buat_warna(255, 255, 200))
    selesai

    grafis.perbarui()
    grafis.atur_fps(60)
selesai

# =============================================
#  SETUP & MULAI
# =============================================

init_bintang()
grafis.mulai_jendela(LEBAR, TINGGI, "Space Defender v2 - BroLang")
game.buat_jendela(LEBAR, TINGGI, "Space Defender v2 - BroLang")
game.tambah_scene("utama", update, gambar)
game.ganti_scene("utama")
game.mulai()
