# ============================================================
# Demo Perluasan Modul Game — BroLang v7.1
# fisika, sprite, ui, visualisasi
# ============================================================

impor fisika
impor sprite
impor ui
impor visualisasi

tulis "=== FISIKA: helper baru ==="

# Vektor dari sudut (radian) + panjang
buat v = fisika.vektor_dari_sudut(0, panjang=10)
tulis "vektor_dari_sudut(0, 10) = (" + teks(v.x) + ", " + teks(v.y) + ")"

buat g_bumi = fisika.gravitasi_bumi()
tulis "gravitasi_bumi = (0, " + teks(g_bumi.y) + ")"

buat g_bulan = fisika.gravitasi_bulan()
tulis "gravitasi_bulan = (0, " + teks(g_bulan.y) + ")"

tulis ""
tulis "=== SPRITE: status & patroli ==="

buat pahlawan = sprite.Sprite(kosong, 0, 0, lebar=32, tinggi=32)
tulis "visibel awal: " + teks(pahlawan.visibel())
pahlawan.sembunyikan()
tulis "setelah sembunyikan: " + teks(pahlawan.visibel())
pahlawan.tampilkan()
tulis "setelah tampilkan: " + teks(pahlawan.visibel())

tulis "arah_ke -> jarak_ke(3, 4) = " + teks(pahlawan.jarak_ke(3, 4))
tulis "di_dalam_bounds(800, 600): " + teks(pahlawan.di_dalam_bounds(800, 600))

pahlawan.ikuti_patroli([(100, 100), (500, 100)], kecepatan=120)
tulis "patroli_aktif: " + teks(pahlawan.patroli_aktif())
pahlawan.berhenti_patroli()
tulis "setelah berhenti: " + teks(pahlawan.patroli_aktif())

buat grup = sprite.GrupSprite()
grup.tambah(pahlawan)
tulis "grup.jumlah(): " + teks(grup.jumlah())
tulis "grup.apakah_kosong(): " + teks(grup.apakah_kosong())
grup.kosongkan()
tulis "setelah kosongkan, apakah_kosong(): " + teks(grup.apakah_kosong())

tulis ""
tulis "=== UI: helper warna ==="

buat merah = ui.warna(255, 0, 0)
tulis "ui.warna(255, 0, 0) = " + teks(merah)

buat oranye = ui.warna_hex("#ff8800")
tulis "ui.warna_hex('#ff8800') = " + teks(oranye)

buat judul = ui.Label("PETUALANGAN", 400, 100, warna="emas", ukuran=40)
judul.set_warna(ui.warna_hex("#22d3ee"))
tulis "judul.warna: " + teks(judul.warna)

tulis ""
tulis "=== VISUALISASI: tabel & area ==="

buat skor = [
    {"nama": "Budi", "skor": 950, "level": 5},
    {"nama": "Siti", "skor": 870, "level": 5},
    {"nama": "Agus", "skor": 640, "level": 4},
]
tulis visualisasi.tabel(skor, judul="Papan Skor", nomor=benar)

buat svg_tabel = visualisasi.tabel_svg(skor, judul="Papan Skor")
tulis "tabel_svg: " + teks(panjang(svg_tabel)) + " karakter HTML"

buat area = visualisasi.area_svg([12, 45, 23, 67, 34, 89], judul="XP per Level")
tulis "area_svg: " + teks(panjang(area)) + " karakter SVG"
