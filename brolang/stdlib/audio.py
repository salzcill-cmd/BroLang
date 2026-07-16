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
)
