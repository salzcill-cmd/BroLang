# Kripto — Keamanan & Kriptografi
# ===============================
# Contoh penggunaan modul `kripto` (v6.4):
#   - Hashing (md5, sha1, sha256, sha512)
#   - Base64 encode/decode
#   - Hash password dengan salt acak + verifikasi
#   - Token acak aman untuk session/API key
#
# Jalankan: bro run examples/kripto.bro

impor kripto
impor teks

tulis "=== Hash ==="
tulis kripto.md5("halo dunia")
tulis kripto.sha1("halo dunia")
tulis kripto.sha256("halo dunia")       # standar checksum
tulis kripto.sha512("halo dunia")       # lebih kuat

tulis ""
tulis "=== Base64 ==="
buat kode = kripto.base64_encode("BroLang")
tulis kode
tulis kripto.base64_decode(kode)

tulis ""
tulis "=== Password (PBKDF2 + salt acak) ==="
buat hash = kripto.hash_password("rahasia123")
tulis hash
tulis f"Cek password benar : {kripto.cek_password('rahasia123', hash)}"
tulis f"Cek password salah : {kripto.cek_password('tebakan', hash)}"

tulis ""
tulis "=== Token acak (API key / session) ==="
buat key = kripto.token(32)
tulis f"API key : {key}"
tulis f"Panjang : {teks.panjang(key)}"
