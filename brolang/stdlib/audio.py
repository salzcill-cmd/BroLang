"""
Modul Audio BroLang
===================

Wrapper Pygame untuk audio: sound effects dan musik.

Contoh:
    impor audio
    audio.muat_musik("musik/bgm.mp3")
    audio.mainkan_musik()
"""

from types import SimpleNamespace

try:
    import pygame
except ImportError:
    pygame = None

_sound_cache = {}
_music_loaded = False


def _ensure_mixer():
    if pygame is None:
        raise RuntimeError("Pygame tidak terinstal. Jalankan: pip install pygame")
    if not pygame.mixer.get_init():
        pygame.mixer.init()


# --- Musik Latar ---

def muat_musik(path: str):
    """Memuat file musik untuk diputar sebagai background.

    Contoh:
        audio.muat_musik("musik/bgm.mp3")
    """
    global _music_loaded
    _ensure_mixer()
    pygame.mixer.music.load(path)
    _music_loaded = True


def mainkan_musik(loops: int = -1):
    """Memutar musik. loops=-1 artinya loop selamanya.

    Contoh:
        audio.mainkan_musik()        # loop forever
        audio.mainkan_musik(3)       # loop 3 kali
    """
    _ensure_mixer()
    pygame.mixer.music.play(loops)


def hentikan_musik():
    """Menghentikan musik."""
    _ensure_mixer()
    pygame.mixer.music.stop()


def jeda_musik():
    """Menjeda musik."""
    _ensure_mixer()
    pygame.mixer.music.pause()


def lanjutkan_musik():
    """Melanjutkan musik yang dijeda."""
    _ensure_mixer()
    pygame.mixer.music.unpause()


def atur_volume_musik(volume: float):
    """Mengatur volume musik (0.0 - 1.0).

    Contoh:
        audio.atur_volume_musik(0.5)
    """
    _ensure_mixer()
    pygame.mixer.music.set_volume(max(0.0, min(1.0, float(volume))))


def sedang_memutar_musik() -> bool:
    """Cek apakah musik sedang diputar."""
    _ensure_mixer()
    return pygame.mixer.music.get_busy()


# --- Sound Effects ---

def muat_suara(path: str):
    """Memuat file sound effect.

    Contoh:
        buat tembak_sfx = audio.muat_suara("suara/tembak.wav")
    """
    _ensure_mixer()
    if path not in _sound_cache:
        _sound_cache[path] = pygame.mixer.Sound(path)
    return _sound_cache[path]


def mainkan_suara(suara, volume: float = 1.0):
    """Memutar sound effect.

    Contoh:
        buat tembak = audio.muat_suara("tembak.wav")
        audio.mainkan_suara(tembak)
        audio.mainkan_suara(tembak, 0.5)
    """
    _ensure_mixer()
    suara.set_volume(max(0.0, min(1.0, float(volume))))
    suara.play()


def atur_volume_semua(volume: float):
    """Mengatur volume semua sound effect (0.0 - 1.0)."""
    _ensure_mixer()
    for snd in _sound_cache.values():
        snd.set_volume(max(0.0, min(1.0, float(volume))))


# ============================================================
# v6.7: Synth Audio — buat efek suara prosedural (tanpa file!)
# ============================================================
# Membuat WAV bytes secara matematis: nada, laser, ledakan, "blip".
# Logika murni stdlib Python (math/struct/io/wave) — bisa dipakai
# tanpa pygame untuk testing, lalu diputar via pygame bila ada.

_SAMPLE_RATE = 22050  # cukup untuk SFX, hemat memori


def _buat_wav_bytes(sampel):
    """Encode list sampel (-1.0..1.0) menjadi bytes WAV 16-bit mono."""
    import io
    import struct
    import wave

    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(_SAMPLE_RATE)
        frames = b"".join(
            struct.pack("<h", int(max(-1.0, min(1.0, s)) * 32767)) for s in sampel
        )
        w.writeframes(frames)
    return buf.getvalue()


def nada(frekuensi=440.0, durasi=0.2, volume=0.6, gelombang="sinus"):
    """Buat WAV nada sederhana — blip/lonceng/pip (v6.7).

    Args:
        frekuensi: Frekuensi nada dalam Hz.
        durasi: Durasi dalam detik.
        volume: Volume 0.0..1.0.
        gelombang: "sinus" | "kotak" | "segitiga" | "gergaji".

    Returns:
        bytes WAV yang bisa diputar `audio.mainkan_wav(...)` atau
        disimpan ke file.

    Contoh:
        buat sfx = audio.nada(880, 0.1)      # blip tinggi
        audio.mainkan_wav(sfx)
    """
    import math

    n = max(1, int(durasi * _SAMPLE_RATE))
    sampel = []
    for i in range(n):
        t = i / _SAMPLE_RATE
        fasa = 2 * math.pi * frekuensi * t
        if gelombang == "kotak":
            v = 1.0 if math.sin(fasa) >= 0 else -1.0
        elif gelombang == "segitiga":
            v = 2.0 * math.asin(math.sin(fasa)) / math.pi
        elif gelombang == "gergaji":
            v = 2.0 * ((frekuensi * t) % 1.0) - 1.0
        else:
            v = math.sin(fasa)
        # Envelope: serangan cepat, lalu decay eksponensial (hindari klik)
        env = math.exp(-3.0 * t / max(durasi, 0.001))
        sampel.append(v * env * volume)
    return _buat_wav_bytes(sampel)


def laser(durasi=0.15, volume=0.5):
    """WAV efek laser sci-fi — sweep frekuensi naik cepat (v6.7)."""
    import math

    n = max(1, int(durasi * _SAMPLE_RATE))
    f0, f1 = 900.0, 220.0  # turun seperti laser pew pew
    sampel = []
    for i in range(n):
        t = i / _SAMPLE_RATE
        p = i / max(n - 1, 1)
        f = f0 + (f1 - f0) * (p ** 2)  # sweep non-linear
        fasa = 2 * math.pi * f * t
        v = math.sin(fasa)
        env = (1.0 - p) ** 1.5  # decay halus
        sampel.append(v * env * volume)
    return _buat_wav_bytes(sampel)


def ledakan(durasi=0.6, volume=0.8):
    """WAV ledakan — noise dengan lowpass sederhana + decay (v6.7)."""
    import math
    import random

    n = max(1, int(durasi * _SAMPLE_RATE))
    random.seed(42)  # deterministik supaya hasil test stabil
    sampel = []
    sebelumnya = 0.0
    for i in range(n):
        t = i / _SAMPLE_RATE
        p = i / max(n - 1, 1)
        # White noise dengan lowpass sederhana (rata-rata dengan sampel lalu)
        noise = random.uniform(-1.0, 1.0)
        sebelumnya = 0.8 * sebelumnya + 0.2 * noise
        # Getar sub-bass di awal
        bass = math.sin(2 * math.pi * (90 - 60 * p) * t)
        v = 0.7 * bass + 0.3 * sebelumnya
        env = math.exp(-2.5 * p)
        sampel.append(v * env * volume)
    return _buat_wav_bytes(sampel)


def blip(frekuensi=660.0, durasi=0.06, volume=0.5):
    """WAV blip pendek untuk UI/skor (v6.7)."""
    return nada(frekuensi, durasi, volume, gelombang="kotak")


def _wav_ke_suara(wav_bytes):
    """Konversi WAV bytes ke pygame.mixer.Sound (butuh pygame)."""
    _ensure_mixer()
    import io
    return pygame.mixer.Sound(file=io.BytesIO(wav_bytes))


def mainkan_wav(wav_bytes, volume=1.0):
    """Putar WAV bytes yang dibuat synth (v6.7).

    Contoh:
        audio.mainkan_wav(audio.laser())
    """
    if pygame is None:
        return False
    snd = _wav_ke_suara(wav_bytes)
    snd.set_volume(max(0.0, min(1.0, float(volume))))
    snd.play()
    return True


def mainkan_nada(frekuensi=440.0, durasi=0.2, volume=0.6, gelombang="sinus"):
    """Buat & putar nada langsung (v6.7)."""
    return mainkan_wav(nada(frekuensi, durasi, volume, gelombang), volume)


def mainkan_laser(volume=0.5):
    """Buat & putar efek laser langsung (v6.7)."""
    return mainkan_wav(laser(volume=volume), volume)


def mainkan_ledakan(volume=0.8):
    """Buat & putar efek ledakan langsung (v6.7)."""
    return mainkan_wav(ledakan(volume=volume), volume)


def simpan_wav(wav_bytes, path):
    """Simpan WAV bytes ke file (v6.7)."""
    with open(path, "wb") as f:
        f.write(wav_bytes)
    return path


# ============================================================
# v6.8: BGM Prosedural — generator musik latar (tanpa file!)
# ============================================================
# Membuat melodi yang bisa di-loop sebagai WAV bytes dari pola nada.
# Pola bisa memakai nama not ("C4", "A#3", "Bb2") atau frekuensi
# langsung, dengan dukungan jeda (0) dan durasi lebih dari 1 ketuk.

_NOTA_SEMITON = {
    "C": 0, "C#": 1, "DB": 1, "D": 2, "D#": 3, "EB": 3, "E": 4, "F": 5,
    "F#": 6, "GB": 6, "G": 7, "G#": 8, "AB": 8, "A": 9, "A#": 10,
    "BB": 10, "B": 11,
}


def _frekuensi_nada(nama):
    """Konversi nama not (mis. 'C4', 'A#3', 'Bb2') ke frekuensi Hz."""
    if isinstance(nama, (int, float)):
        return float(nama)
    s = str(nama).strip().upper()
    if not s:
        return 0.0
    if s[0] not in "ABCDEFG":
        return 0.0
    i = 1
    while i < len(s) and s[i] in "#B":
        i += 1
    huruf = s[:i]
    oktaf = int(s[i:]) if i < len(s) else 4
    semiton = _NOTA_SEMITON.get(huruf, 0)
    midi = (oktaf + 1) * 12 + semiton
    return 440.0 * (2.0 ** ((midi - 69) / 12.0))


def buat_bgm(pola, tempo=120, gelombang="sinus", volume=0.4):
    """Buat WAV musik latar yang bisa di-loop (v6.8).

    Args:
        pola: daftar nada — tiap elemen bisa:
            - "C4" / "A#3" / "Bb2" : nama not (oktaf 0-8)
            - 440.0                : frekuensi langsung (Hz)
            - (nada, ketukan)      : nada dengan durasi > 1 ketuk
            - 0                    : jeda (diam)
        tempo: ketukan per menit (default 120).
        gelombang: "sinus" | "kotak" | "segitiga" | "gergaji".
        volume: 0.0..1.0.

    Returns:
        bytes WAV yang siap di-loop (simpan atau mainkan).

    Contoh:
        buat bgm = audio.buat_bgm(audio.pola_arcade)
        audio.mainkan_wav(bgm)
    """
    import math

    ketukan = 60.0 / max(float(tempo), 1.0)
    sampel_total = []
    for item in pola:
        if isinstance(item, (tuple, list)):
            nada_ = item[0]
            ketuk = float(item[1]) if len(item) > 1 else 1.0
        else:
            nada_ = item
            ketuk = 1.0
        frek = _frekuensi_nada(nada_)
        durasi = ketukan * ketuk
        if frek <= 0:
            n = max(1, int(durasi * _SAMPLE_RATE))
            sampel_total.extend([0.0] * n)
            continue
        # 90% durasi nada + 10% jeda kecil supaya not tidak menumpuk
        n = max(1, int(durasi * 0.9 * _SAMPLE_RATE))
        for i in range(n):
            t = i / _SAMPLE_RATE
            fasa = 2 * math.pi * frek * t
            if gelombang == "kotak":
                v = 1.0 if math.sin(fasa) >= 0 else -1.0
            elif gelombang == "segitiga":
                v = 2.0 * math.asin(math.sin(fasa)) / math.pi
            elif gelombang == "gergaji":
                v = 2.0 * ((frek * t) % 1.0) - 1.0
            else:
                v = math.sin(fasa)
            env = math.exp(-2.5 * t / max(durasi, 0.001))
            sampel_total.append(v * env * volume)
        n_gap = max(0, int(durasi * 0.1 * _SAMPLE_RATE))
        sampel_total.extend([0.0] * n_gap)
    return _buat_wav_bytes(sampel_total)


# Pola BGM siap pakai (v6.8)
pola_arcade = ["C5", "E5", "G5", 0, "C5", "E5", "G5", 0,
               "A4", "C5", "E5", 0, "G4", "B4", "D5", 0]

pola_epik = ["A3", "A3", "C4", "D4", "E4", "D4", "C4", "A3",
             "E4", "E4", "G4", "A4", "G4", "E4", "D4", "C4"]

pola_tenang = ["C4", "E4", "G4", "E4", "A4", "G4", "E4", "D4",
               "C4", "E4", "G4", "B4", "C5", "B4", "G4", "E4"]


def mainkan_bgm(pola, tempo=120, gelombang="sinus", volume=0.4, loops=-1):
    """Generate & putar BGM prosedural sebagai musik loop (v6.8).

    Butuh pygame — mengembalikan False bila pygame tidak tersedia.

    Contoh:
        audio.mainkan_bgm(audio.pola_arcade, 120)
        audio.hentikan_bgm()
    """
    if pygame is None:
        return False
    _ensure_mixer()
    import os
    import tempfile
    wav = buat_bgm(pola, tempo=tempo, gelombang=gelombang, volume=volume)
    path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(wav)
            path = f.name
        pygame.mixer.music.load(path)  # dimuat penuh ke memori
        pygame.mixer.music.play(loops)
    finally:
        if path is not None:
            try:
                os.unlink(path)
            except OSError:
                pass
    return True


def hentikan_bgm():
    """Menghentikan musik latar prosedural (v6.8)."""
    _ensure_mixer()
    pygame.mixer.music.stop()


module = SimpleNamespace(
    muat_musik=muat_musik,
    mainkan_musik=mainkan_musik,
    hentikan_musik=hentikan_musik,
    jeda_musik=jeda_musik,
    lanjutkan_musik=lanjutkan_musik,
    atur_volume_musik=atur_volume_musik,
    sedang_memutar_musik=sedang_memutar_musik,
    muat_suara=muat_suara,
    mainkan_suara=mainkan_suara,
    atur_volume_semua=atur_volume_semua,
    # v6.7 synth audio
    nada=nada,
    laser=laser,
    ledakan=ledakan,
    blip=blip,
    mainkan_wav=mainkan_wav,
    mainkan_nada=mainkan_nada,
    mainkan_laser=mainkan_laser,
    mainkan_ledakan=mainkan_ledakan,
    simpan_wav=simpan_wav,
    # v6.8 BGM prosedural
    buat_bgm=buat_bgm,
    mainkan_bgm=mainkan_bgm,
    hentikan_bgm=hentikan_bgm,
    frekuensi_nada=_frekuensi_nada,
    pola_arcade=pola_arcade,
    pola_epik=pola_epik,
    pola_tenang=pola_tenang,
)
