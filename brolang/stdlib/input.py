"""
Modul Input BroLang
===================

Menangani input keyboard dan mouse dari Pygame.

Contoh:
    impor input
    input.tombol_ditekan("UP")
    input.tikus_posisi()
"""

from types import SimpleNamespace

try:
    import pygame
except ImportError:
    pygame = None

_mouse_pos = (0, 0)
_mouse_rel = (0, 0)
_mouse_buttons = (False, False, False)
_events = []
_keys_pressed = set()
_keys_just_pressed = set()
_keys_just_released = set()


def _ensure_init():
    if pygame is None:
        raise RuntimeError("Pygame tidak terinstal. Jalankan: pip install pygame")


def _update():
    """Update state input. Dipanggil setiap frame oleh game loop."""
    global _mouse_pos, _mouse_rel, _mouse_buttons, _events
    global _keys_just_pressed, _keys_just_released

    _ensure_init()
    _events = pygame.event.get()
    _keys_just_pressed = set()
    _keys_just_released = set()

    keys_now = set()
    key_state = pygame.key.get_pressed()
    for i in range(512):
        if key_state[i]:
            keys_now.add(i)

    for key in keys_now:
        if key not in _keys_pressed:
            _keys_just_pressed.add(key)
    for key in _keys_pressed:
        if key not in keys_now:
            _keys_just_released.add(key)
    _keys_pressed.clear()
    _keys_pressed.update(keys_now)

    _mouse_pos = pygame.mouse.get_pos()
    _mouse_rel = pygame.mouse.get_rel()
    _mouse_buttons = pygame.mouse.get_pressed()


# --- Keyboard ---

_KEY_MAP = {
    "UP": 1073741906, "DOWN": 1073741905,
    "LEFT": 1073741904, "RIGHT": 1073741903,
    "SPACE": 32, "ENTER": 13, "RETURN": 13,
    "ESCAPE": 27, "ESC": 27,
    "TAB": 9, "BACKSPACE": 8, "DELETE": 127,
    "LSHIFT": 1073742049, "RSHIFT": 1073742053,
    "LCTRL": 1073742048, "RCTRL": 1073742052,
    "F1": 1073741882, "F2": 1073741883, "F3": 1073741884,
    "F4": 1073741885, "F5": 1073741886, "F6": 1073741887,
    "F7": 1073741888, "F8": 1073741889, "F9": 1073741890,
    "F10": 1073741891, "F11": 1073741892, "F12": 1073741893,
}

for _c in "abcdefghijklmnopqrstuvwxyz0123456789":
    _KEY_MAP[_c.upper()] = ord(_c)


def _resolve_key(nama):
    if isinstance(nama, int):
        return nama
    nama_upper = str(nama).upper()
    if nama_upper in _KEY_MAP:
        return _KEY_MAP[nama_upper]
    if len(nama_upper) == 1:
        return ord(nama_upper)
    raise ValueError(f"Tombol '{nama}' tidak dikenal.")


def tombol_ditekan(nama) -> bool:
    """Cek apakah tombol sedang ditekan (held down).

    Contoh:
        input.tombol_ditekan("UP")
        input.tombol_ditekan("a")
    """
    _ensure_init()
    key = _resolve_key(nama)
    return key in _keys_pressed


def tombol_baru_ditekan(nama) -> bool:
    """Cek apakah tombol baru saja ditekan (satu kali).

    Contoh:
        input.tombol_baru_ditekan("SPACE")
    """
    _ensure_init()
    key = _resolve_key(nama)
    return key in _keys_just_pressed


def tombol_dilepas(nama) -> bool:
    """Cek apakah tombol baru saja dilepas."""
    _ensure_init()
    key = _resolve_key(nama)
    return key in _keys_just_released


# --- Mouse ---

def tikus_posisi() -> tuple:
    """Posisi mouse saat ini (x, y)."""
    _ensure_init()
    return _mouse_pos


def tikus_tekanan() -> tuple:
    """Status tombol mouse: (kiri, tengah, kanan)."""
    _ensure_init()
    return _mouse_buttons


def tikus_tombol_ditekan(tombol: int = 0) -> bool:
    """Cek apakah tombol mouse ditekan. 0=kiri, 1=tengah, 2=kanan."""
    _ensure_init()
    return _mouse_buttons[min(tombol, 2)]


def tikus_gerakan() -> tuple:
    """Pergerakan mouse dari frame terakhir (dx, dy)."""
    _ensure_init()
    return _mouse_rel


def tikus_set_posisi(x: int, y: int):
    """Memindahkan mouse ke posisi tertentu."""
    _ensure_init()
    pygame.mouse.set_pos((int(x), int(y)))


def tikus_tampil(hide: bool = True):
    """Sembunyikan/tampilkan kursor mouse."""
    _ensure_init()
    pygame.mouse.set_visible(not hide)


# --- Event ---

def _is_quit_event(event) -> bool:
    return event.type == pygame.QUIT


def events_quit() -> bool:
    """Cek apakah ada event quit (X ditutup)."""
    _ensure_init()
    return any(_is_quit_event(e) for e in _events)


def events_tombol() -> list:
    """Mendapatkan semua event tombol yang ditekan pada frame ini."""
    _ensure_init()
    result = []
    for event in _events:
        if event.type == pygame.KEYDOWN:
            name = pygame.key.name(event.key).upper()
            result.append(name)
    return result


def events_mouse() -> list:
    """Mendapatkan semua event mouse pada frame ini."""
    _ensure_init()
    result = []
    for event in _events:
        if event.type == pygame.MOUSEBUTTONDOWN:
            result.append({"tombol": event.button, "posisi": event.pos})
    return result


module = SimpleNamespace(
    tombol_ditekan=tombol_ditekan,
    tombol_baru_ditekan=tombol_baru_ditekan,
    tombol_dilepas=tombol_dilepas,
    tikus_posisi=tikus_posisi,
    tikus_tekanan=tikus_tekanan,
    tikus_tombol_ditekan=tikus_tombol_ditekan,
    tikus_gerakan=tikus_gerakan,
    tikus_set_posisi=tikus_set_posisi,
    tikus_tampil=tikus_tampil,
    events_quit=events_quit,
    events_tombol=events_tombol,
    events_mouse=events_mouse,
    _update=_update,
)
