"""
Modul Simpan Game untuk BroLang Game Development
=================================================

Simpan & muat progres game ke disk (JSON): slot save, checkpoint,
auto-save, metadata (waktu simpan, label, versi).

Data yang bisa disimpan: dict, list, angka, teks, bool, None — kunci
dict dikonversi otomatis ke teks (JSON).

Contoh:
    impor simpan_game

    # Simpan progres pemain ke slot "slot1"
    buat progres = {"level": 3, "nyawa": 5, "kunci": ["emas", "perak"]}
    simpan_game.simpan("slot1", progres, label="Level 3")

    # Muat kembali (default bila belum ada)
    buat data = simpan_game.muat("slot1", default={"level": 1})

    # Auto-save / checkpoint di tengah permainan
    simpan_game.checkpoint({"level": 4, "posisi": [100, 200]})

    # Daftar semua save (terbaru dulu)
    buat daftar = simpan_game.daftar()
"""

import json
import os
import time

from types import SimpleNamespace


def _bersihkan(obj):
    """Konversi data ke bentuk JSON-safe: kunci dict -> teks, tuple -> list."""
    if isinstance(obj, dict):
        return {str(k): _bersihkan(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_bersihkan(v) for v in obj]
    if isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    # Objek lain (SimpleNamespace, dsb.): coba ambil __dict__-nya
    if hasattr(obj, "__dict__"):
        return _bersihkan(vars(obj))
    return str(obj)


def _jalur(nama, folder):
    """Path lengkap file save (menambahkan .json bila belum ada)."""
    if not nama.endswith(".json"):
        nama = nama + ".json"
    return os.path.join(folder, nama)


def simpan(nama, data, folder="tersimpan", label="", versi=1):
    """Simpan data ke file JSON di folder (dibuat otomatis).

    Args:
        nama: Nama save (tanpa ekstensi boleh; `.json` ditambahkan).
        data: Data yang disimpan (dict/list/angka/teks/bool/None).
        folder: Folder penyimpanan (default "tersimpan").
        label: Label opsional (mis. "Level 3").
        versi: Nomor versi save untuk migrasi.

    Returns:
        Path lengkap file yang ditulis.
    """
    os.makedirs(folder, exist_ok=True)
    payload = {
        "_meta": {
            "waktu": time.time(),
            "label": str(label),
            "versi": int(versi),
        },
        "data": _bersihkan(data),
    }
    path = _jalur(nama, folder)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return path


def muat(nama, default=None, folder="tersimpan"):
    """Muat data dari file save.

    Returns:
        Data yang disimpan, atau `default` bila file belum ada / rusak.
    """
    path = _jalur(nama, folder)
    if not os.path.exists(path):
        return default
    try:
        with open(path, encoding="utf-8") as f:
            payload = json.load(f)
        return payload.get("data", default)
    except (json.JSONDecodeError, OSError, ValueError):
        return default


def ada(nama, folder="tersimpan"):
    """Apakah file save dengan nama itu ada?"""
    return os.path.exists(_jalur(nama, folder))


def hapus(nama, folder="tersimpan"):
    """Hapus file save. Kembalikan True bila terhapus."""
    path = _jalur(nama, folder)
    if os.path.exists(path):
        os.remove(path)
        return True
    return False


def daftar(folder="tersimpan"):
    """Daftar semua save di folder, terbaru dulu.

    Returns:
        List dict: {nama, waktu, label, versi} — tanpa ekstensi .json.
    """
    hasil = []
    if not os.path.isdir(folder):
        return hasil
    for fname in sorted(os.listdir(folder)):
        if not fname.endswith(".json"):
            continue
        path = os.path.join(folder, fname)
        try:
            with open(path, encoding="utf-8") as f:
                payload = json.load(f)
        except (json.JSONDecodeError, OSError, ValueError):
            continue
        meta = payload.get("_meta", {})
        hasil.append({
            "nama": fname[:-5],
            "waktu": meta.get("waktu", 0),
            "label": meta.get("label", ""),
            "versi": meta.get("versi", 1),
        })
    hasil.sort(key=lambda s: s["waktu"], reverse=True)
    return hasil


def checkpoint(data, folder="tersimpan", nama="checkpoint", label="auto"):
    """Auto-save / checkpoint — simpan cepat di tengah permainan."""
    return simpan(nama, data, folder=folder, label=label)


def muat_checkpoint(default=None, folder="tersimpan", nama="checkpoint"):
    """Muat checkpoint terakhir."""
    return muat(nama, default=default, folder=folder)


def bersihkan(folder="tersimpan"):
    """Hapus semua file save di folder. Kembalikan jumlah terhapus."""
    if not os.path.isdir(folder):
        return 0
    n = 0
    for fname in list(os.listdir(folder)):
        if fname.endswith(".json"):
            try:
                os.remove(os.path.join(folder, fname))
                n += 1
            except OSError:
                pass
    return n


def info(nama, folder="tersimpan"):
    """Metadata file save (waktu, label, versi), atau None bila tak ada."""
    path = _jalur(nama, folder)
    if not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8") as f:
            payload = json.load(f)
    except (json.JSONDecodeError, OSError, ValueError):
        return None
    return payload.get("_meta")


module = SimpleNamespace(
    simpan=simpan,
    muat=muat,
    ada=ada,
    hapus=hapus,
    daftar=daftar,
    checkpoint=checkpoint,
    muat_checkpoint=muat_checkpoint,
    bersihkan=bersihkan,
    info=info,
)
