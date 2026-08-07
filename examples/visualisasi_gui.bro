# ============================================================
# Contoh: Visualisasi Data GUI (jendela native ala game)
# Jalankan:  pip install pygame-ce        (sekali saja)
#            bro examples/visualisasi_gui.bro
#
# Akan terbuka jendela gelap dengan 5 chart.
# Navigasi: panah kiri/kanan = ganti chart
#           1-5              = lompat ke chart
#           F                = fullscreen
#           S                = screenshot (PNG)
#           H                = bantuan
#           ESC / Q          = tutup
# ============================================================

impor visualisasi

# ---------- Data contoh ----------
buat penjualan = {"Senin": 12, "Selasa": 45, "Rabu": 23, "Kamis": 67, "Jumat": 34}
buat tren = [3, 7, 2, 9, 5, 8, 4, 6]
buat pangsa = {"Pulsa": 30, "Data": 40, "SMS": 25, "Lainnya": 5}
buat nilai = [1, 1, 2, 2, 2, 3, 3, 3, 3, 4, 4, 5, 9, 9, 9, 9]

# ---------- Kumpulan chart untuk satu jendela ----------
buat chart1 = {"jenis": "batang", "data": penjualan, "judul": "Penjualan Mingguan", "warna": "#6366f1"}
buat chart2 = {"jenis": "garis", "data": tren, "judul": "Tren 8 Hari", "warna": "#10b981"}
buat chart3 = {"jenis": "kue", "data": pangsa, "judul": "Pendapatan Operator", "warna": ["#6366f1", "#10b981", "#f59e0b", "#ef4444"]}
buat chart4 = {"jenis": "histogram", "data": nilai, "jumlah_bin": 5, "judul": "Distribusi Nilai", "warna": "#06b6d4"}
buat chart5 = {"jenis": "sebar", "x": [1, 2, 3, 4, 5, 6, 7, 8], "y": [2, 5, 3, 8, 6, 9, 7, 10], "judul": "Tinggi vs Berat", "warna": "#f59e0b"}

tulis "Membuka jendela visualisasi... tutup dengan ESC."
tulis ""
tulis "Navigasi: panah kiri/kanan ganti chart, 1-5 lompat, F fullscreen,"
tulis "          S screenshot, H bantuan."

visualisasi.tampilkan_jendela([chart1, chart2, chart3, chart4, chart5], judul="Dashboard Penjualan BroLang")

tulis "Jendela ditutup. Sampai jumpa!"

# ---------- Bonus: simpan chart ke PNG tanpa buka jendela ----------
buat png = visualisasi.simpan_png("chart_penjualan.png", {"jenis": "batang", "data": penjualan, "judul": "Penjualan Mingguan"})
tulis "Chart PNG tersimpan: " + png
