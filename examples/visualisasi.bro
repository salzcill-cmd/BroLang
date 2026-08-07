# ============================================================
# Contoh: Visualisasi Data dengan BroLang — Tur Lengkap
# Jalankan:  bro examples/visualisasi.bro
#
# Menampilkan 3 cara memvisualisasikan data:
#   1) Chart ASCII    -> langsung tampil di terminal
#   2) Laporan HTML   -> laporan.html + .svg (buka di browser)
#   3) Jendela GUI    -> window chart interaktif ala game
#                        (butuh pygame-ce, install sekali saja:
#                        pip install pygame-ce)
# ============================================================

impor visualisasi

# ---------- Data contoh ----------
buat penjualan = {"Senin": 12, "Selasa": 45, "Rabu": 23, "Kamis": 67, "Jumat": 34}
buat tren = [3, 7, 2, 9, 5, 8, 4, 6]
buat pangsa = [30, 40, 25, 5]
buat sebaran = [1, 1, 2, 2, 2, 3, 3, 3, 3, 4, 4, 5, 9, 9, 9, 9]

# ============================================================
# 1) CHART ASCII — langsung tampil di terminal
# ============================================================
tulis "========== 1) CHART ASCII (terminal) =========="
tulis ""
tulis visualisasi.batang(penjualan, judul="Penjualan Mingguan", satuan="unit")
tulis ""
tulis visualisasi.garis(tren, label=["H1", "H2", "H3", "H4", "H5", "H6", "H7", "H8"], judul="Tren 8 Hari")
tulis ""
tulis visualisasi.kue(pangsa, label=["Pulsa", "Data", "SMS", "Lainnya"], judul="Pendapatan Operator")
tulis ""
tulis visualisasi.histogram(sebaran, jumlah_bin=4, judul="Distribusi Nilai Test")
tulis ""
tulis visualisasi.sebar([1, 2, 3, 4, 5, 6, 7, 8], [2, 5, 3, 8, 6, 9, 7, 10], judul="Tinggi vs Berat")

# ============================================================
# 2) LAPORAN HTML & SVG — buka di browser
# ============================================================
tulis ""
tulis "========== 2) LAPORAN HTML & SVG =========="
buat svg1 = visualisasi.batang_svg(penjualan, judul="Penjualan Mingguan")
buat svg2 = visualisasi.garis_svg(tren, judul="Tren 8 Hari")
buat svg3 = visualisasi.kue_svg(pangsa, label=["Pulsa", "Data", "SMS", "Lainnya"], judul="Pendapatan Operator")

visualisasi.simpan_svg("laporan_penjualan.svg", svg1)
visualisasi.simpan_html("laporan.html", [svg1, svg2, svg3], judul="Laporan Penjualan BroLang")
tulis "File laporan_penjualan.svg dan laporan.html berhasil dibuat!"
tulis "Buka laporan.html di browser untuk lihat chart-nya."

# ============================================================
# 3) JENDELA GUI — chart interaktif ala game (butuh pygame-ce)
# ============================================================
tulis ""
tulis "========== 3) JENDELA GUI (pygame) =========="
tulis "Membuka jendela chart interaktif... tutup dengan ESC."
tulis "Navigasi: panah kiri/kanan ganti chart, 1-5 lompat,"
tulis "          F fullscreen, S screenshot, H bantuan."

buat chart1 = {"jenis": "batang", "data": penjualan, "judul": "Penjualan Mingguan", "warna": "#6366f1"}
buat chart2 = {"jenis": "garis", "data": tren, "judul": "Tren 8 Hari", "warna": "#10b981"}
buat chart3 = {"jenis": "kue", "data": pangsa, "label": ["Pulsa", "Data", "SMS", "Lainnya"], "judul": "Pendapatan Operator", "warna": ["#6366f1", "#10b981", "#f59e0b", "#ef4444"]}
buat chart4 = {"jenis": "histogram", "data": sebaran, "jumlah_bin": 4, "judul": "Distribusi Nilai Test", "warna": "#06b6d4"}
buat chart5 = {"jenis": "sebar", "x": [1, 2, 3, 4, 5, 6, 7, 8], "y": [2, 5, 3, 8, 6, 9, 7, 10], "judul": "Tinggi vs Berat", "warna": "#f59e0b"}

visualisasi.tampilkan_jendela([chart1, chart2, chart3, chart4, chart5], judul="Dashboard Penjualan BroLang")

tulis "Jendela ditutup. Semua mode visualisasi selesai!"
tulis "Ingin langsung buka GUI saja? Jalankan: bro examples/visualisasi_gui.bro"
