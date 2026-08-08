# Web API dengan BroLang v6.3
# ===========================
# Framework web bawaan: routing, JSON response, parameter dinamis,
# query string, dan CORS. Jalankan dengan:
#   bro run examples/web_api.bro
# Lalu buka http://127.0.0.1:8000 di browser.

impor web_server

# --- Data contoh (di memori) ---
buat daftar_pengguna = [
    {"id": 1, "nama": "Budi", "kota": "Jakarta"},
    {"id": 2, "nama": "Ani", "kota": "Bandung"},
    {"id": 3, "nama": "Citra", "kota": "Surabaya"}
]

# --- Handler ---
fungsi daftar(req)
    # Response JSON dengan helper kirim_json
    kembali req.kirim_json({"jumlah": daftar_pengguna.jumlah(), "data": daftar_pengguna})
selesai

fungsi detail(req)
    buat id = angka(req.parameter["id"])
    untuk p dalam daftar_pengguna lakukan
        jika p["id"] == id maka
            kembali req.kirim_json(p)
        selesai
    selesai
    kembali req.kirim_json({"error": "Pengguna tidak ditemukan"}, 404)
selesai

fungsi cari(req)
    # Query string: /cari?kota=Bandung
    buat kota = req.query.get("kota", "")
    buat hasil = []
    untuk p dalam daftar_pengguna lakukan
        jika p["kota"] == kota maka
            hasil.tambah(p)
        selesai
    selesai
    kembali req.kirim_json({"hasil": hasil})
selesai

fungsi tambah(req)
    # Body JSON: {"nama": "Dedi", "kota": "Medan"}
    buat data = req.json
    jika data == kosong maka
        kembali req.kirim_json({"error": "Body JSON diperlukan"}, 400)
    selesai
    buat baru = {"id": daftar_pengguna.jumlah() + 1, "nama": data["nama"], "kota": data["kota"]}
    daftar_pengguna.tambah(baru)
    kembali req.kirim_json(baru, 201)
selesai

fungsi halaman_utama(req)
    kembali req.kirim_html("""
    <html>
      <head><title>API BroLang</title></head>
      <body style="font-family: sans-serif; padding: 2rem">
        <h1>🚀 Web API BroLang v6.3</h1>
        <p>Coba endpoint ini:</p>
        <ul>
          <li><a href="/pengguna">GET /pengguna</a> — daftar semua</li>
          <li><a href="/pengguna/2">GET /pengguna/2</a> — detail by id</li>
          <li><a href="/cari?kota=Bandung">GET /cari?kota=Bandung</a> — cari by kota</li>
        </ul>
        <p>POST /pengguna dengan JSON untuk menambah pengguna.</p>
      </body>
    </html>
    """)
selesai

# --- Setup server ---
buat app = web_server.Buat()
app.atur_cors(benar)
app.get("/", halaman_utama)
app.get("/pengguna", daftar)
app.get("/pengguna/{id}", detail)
app.get("/cari", cari)
app.post("/pengguna", tambah)

tulis "API BroLang siap! Coba: http://127.0.0.1:8000/pengguna"
app.jalankan(8000)
