"""
Modul Kripto BroLang
====================

Keamanan & kriptografi sederhana: hashing, Base64, hashing password,
dan token acak — berbasis stdlib Python (hashlib, base64, secrets).

Fitur:
- Hash: md5, sha1, sha256, sha512
- Base64: encode / decode
- Password: hash_password (dengan salt acak) & cek_password
- Token acak aman (crypto-grade) untuk session/API key

Contoh:
    impor kripto

    tulis kripto.sha256("halo dunia")     # hex digest 64 karakter
    tulis kripto.base64_encode("bro")     # YnJv

    buat hash = kripto.hash_password("rahasia123")
    tulis kripto.cek_password("rahasia123", hash)   # True
    tulis kripto.cek_password("salah", hash)        # False

    buat api_key = kripto.token(32)
"""

import base64 as _base64
import hashlib as _hashlib
import secrets as _secrets
from types import SimpleNamespace

# --- Hash (hex digest) ---


def md5(teks: str) -> str:
    """Hash MD5 (32 karakter hex).

    Contoh:
        tulis kripto.md5("halo")    # 2b63f... (32 char)
    """
    return _hashlib.md5(str(teks).encode("utf-8")).hexdigest()


def sha1(teks: str) -> str:
    """Hash SHA-1 (40 karakter hex)."""
    return _hashlib.sha1(str(teks).encode("utf-8")).hexdigest()


def sha256(teks: str) -> str:
    """Hash SHA-256 (64 karakter hex) — standar untuk checksum & integritas."""
    return _hashlib.sha256(str(teks).encode("utf-8")).hexdigest()


def sha512(teks: str) -> str:
    """Hash SHA-512 (128 karakter hex) — lebih kuat dari SHA-256."""
    return _hashlib.sha512(str(teks).encode("utf-8")).hexdigest()


# --- Base64 ---


def base64_encode(teks: str) -> str:
    """Encode teks ke Base64 (aman untuk teks/URL tanpa spasi).

    Contoh:
        tulis kripto.base64_encode("BroLang")   # QnJvTGFuZw==
    """
    return _base64.b64encode(str(teks).encode("utf-8")).decode("ascii")


def base64_decode(teks: str) -> str:
    """Decode teks Base64 kembali ke bentuk aslinya.

    Contoh:
        tulis kripto.base64_decode("QnJvTGFuZw==")   # BroLang
    """
    return _base64.b64decode(str(teks)).decode("utf-8")


# --- Password hashing (PBKDF2 + salt acak) ---

_ITERASI = 100_000


def hash_password(kata_sandi: str) -> str:
    """Hash kata sandi dengan salt acak (PBKDF2-SHA256).

    Format hasil: "pbkdf2_sha256$<salt>$<hash>".
    Salt berbeda setiap pemanggilan — dua hash dari password yang sama
    tidak akan pernah identik (aman untuk disimpan di database).

    Contoh:
        buat hash = kripto.hash_password("rahasia123")
        tulis kripto.cek_password("rahasia123", hash)   # True
    """
    salt = _secrets.token_hex(16)
    digest = _hashlib.pbkdf2_hmac(
        "sha256", str(kata_sandi).encode("utf-8"), salt.encode("utf-8"), _ITERASI
    ).hex()
    return f"pbkdf2_sha256${salt}${digest}"


def cek_password(kata_sandi: str, tersimpan: str) -> bool:
    """Verifikasi kata sandi terhadap hash yang dihasilkan hash_password.

    Contoh:
        buat hash = kripto.hash_password("rahasia")
        tulis kripto.cek_password("rahasia", hash)   # True
        tulis kripto.cek_password("salah", hash)     # False
    """
    try:
        algo, salt, digest = str(tersimpan).split("$")
        if algo != "pbkdf2_sha256":
            return False
        hitung = _hashlib.pbkdf2_hmac(
            "sha256", str(kata_sandi).encode("utf-8"), salt.encode("utf-8"), _ITERASI
        ).hex()
        return _secrets.compare_digest(hitung, digest)
    except (ValueError, AttributeError):
        return False


# --- Token & kunci acak (crypto-grade) ---


def token(panjang: int = 32) -> str:
    """Token hex acak aman (mis. untuk session ID / API key).

    Contoh:
        buat key = kripto.token(32)      # 64 karakter hex
        buat pendek = kripto.token(8)    # 16 karakter hex
    """
    n = max(1, int(panjang))
    return _secrets.token_hex((n + 1) // 2)[:n]


def bilangan_acak(batas: int = 100) -> int:
    """Bilangan acak aman (cryptographically secure) dari 0 sampai batas-1."""
    return _secrets.randbelow(max(1, int(batas)))


module = SimpleNamespace(
    md5=md5,
    sha1=sha1,
    sha256=sha256,
    sha512=sha512,
    base64_encode=base64_encode,
    base64_decode=base64_decode,
    hash_password=hash_password,
    cek_password=cek_password,
    token=token,
    bilangan_acak=bilangan_acak,
)
