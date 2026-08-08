# Terminal — UX untuk Program CLI
# ================================
# Contoh penggunaan modul `terminal` (v6.4):
#   - Warna & gaya teks (ANSI)
#   - Pesan status: sukses, peringatan, gagal, info
#   - Progress bar (bilah & cetak langsung)
#   - Banner dekoratif
#
# Jalankan: bro run examples/terminal.bro

impor terminal

tulis terminal.banner("Aplikasi BroLang")

tulis ""
tulis "=== Warna & Gaya Teks ==="
tulis terminal.merah("ini merah")
tulis terminal.hijau("ini hijau")
tulis terminal.kuning("ini kuning")
tulis terminal.biru("ini biru")
tulis terminal.magenta("ini magenta")
tulis terminal.cyan("ini cyan")
tulis terminal.abu("ini abu-abu")
tulis terminal.tebal("ini tebal")
tulis terminal.garis_bawah("ini garis bawah")
tulis terminal.miring("ini miring")
tulis terminal.warna("ini warna custom", "kuning")

tulis ""
tulis "=== Pesan Status ==="
terminal.sukses("Deploy berhasil!")
terminal.info("Server jalan di port 8000")
terminal.peringatan("Disk hampir penuh")
terminal.gagal("Koneksi terputus")

tulis ""
tulis "=== Progress Bar ==="
tulis terminal.bilah_progress(0, 10)
tulis terminal.bilah_progress(5, 10)
tulis terminal.bilah_progress(10, 10)

tulis ""
tulis "=== Bilah Progress Langsung (loop) ==="
buat total = 20
untuk i dalam range(1, total + 1) lakukan
    terminal.cetak_progress(i, total, 25)
selesai

tulis ""
tulis "Selesai! 🎉"
