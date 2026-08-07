"""
Modul Input BroLang
===================

Menangani input keyboard, mouse, scroll, dan gamepad dari Pygame.

Modul ini adalah satu-satunya konsumen event queue pygame. Game loop
(`game.mulai()`) memanggil `input._update()` di awal frame, lalu membaca
event QUIT/ESC dari `input.ambil_events()` — sehingga event tidak
"dimakan" dua kali dan input selalu melihat event di dalam game loop.

Contoh:
    impor input

    input.tombol_ditekan("UP")
    input.tombol_baru_ditekan("SPACE")
    input.tikus_posisi()
    input.tikus_baru_ditekan(0)      # klik kiri baru saja
    input.geser()                    # scroll wheel
    input.gamepad_sumbu(0, 0)        # joystick kiri
"""

from types import SimpleNamespace

try:
    import pygame
except ImportError:
    pygame = None

# Event "fokus jendela hilang" (pygame 2+). Di-guard untuk versi lama.
_FOCUS_LOST_EVENT = getattr(pygame, "WINDOWFOCUSLOST", None)

_mouse_pos = (0, 0)
_mouse_rel = (0, 0)
_mouse_buttons = (False, False, False)
_mouse_just_pressed = set()
_mouse_just_released = set()
_scroll = (0, 0)
_events = []
_keys_pressed = set()
_keys_just_pressed = set()
_keys_just_released = set()
_joysticks = []
_joy_buttons = []
_joy_just_pressed = []
_joystick_init_done = False


def _ensure_init():
    if pygame is None:
        raise RuntimeError("Pygame tidak terinstal. Jalankan: pip install pygame")


def _init_joysticks():
    """Inisialisasi joystick/gamepad yang terhubung."""
    global _joystick_init_done
    _joystick_init_done = True
    _joysticks.clear()
    _joy_buttons.clear()
    _joy_just_pressed.clear()
    try:
        if not pygame.get_init():
            pygame.init()
        if not pygame.joystick.get_init():
            pygame.joystick.init()
        jumlah = pygame.joystick.get_count()
    except pygame.error:
        return
    for i in range(jumlah):
        try:
            joy = pygame.joystick.Joystick(i)
            joy.init()
            _joysticks.append(joy)
            _joy_buttons.append([False] * max(joy.get_numbuttons(), 1))
            _joy_just_pressed.append([False] * max(joy.get_numbuttons(), 1))
        except pygame.error:
            continue


def _update():
    """Update state input. Dipanggil setiap frame oleh game loop.

    Menguras event queue pygame SEKALI per frame, menyimpan event untuk
    game loop (`ambil_events`) dan memperbarui state keyboard/mouse/gamepad.
    """
    global _mouse_pos, _mouse_rel, _mouse_buttons, _events, _scroll
    global _keys_just_pressed, _keys_just_released
    global _mouse_just_pressed, _mouse_just_released

    _ensure_init()
    _events = pygame.event.get()
    _keys_just_pressed = set()
    _keys_just_released = set()
    _mouse_just_pressed = set()
    _mouse_just_released = set()
    _scroll = (0, 0)

    # --- Keyboard, mouse & scroll: semua dari event ---
    # PENTING: state "held" (tombol_ditekan) dibangun dari event KEYDOWN/KEYUP.
    # pygame.key.get_pressed() di-index dengan *scancode*, sedangkan _KEY_MAP
    # memakai *keycode* (K_*) — loop scancode lama membuat tombol khusus
    # (UP/DOWN/LEFT/RIGHT, F1-F12, modifier) TIDAK PERNAH terdeteksi sebagai
    # ditekan (bug: player 2 game pong tidak bisa gerak). event.key selalu
    # berupa keycode sehingga konsisten dengan _KEY_MAP.
    _mouse_pos = pygame.mouse.get_pos()
    _mouse_rel = pygame.mouse.get_rel()
    _mouse_buttons = pygame.mouse.get_pressed()

    for event in _events:
        if event.type == pygame.KEYDOWN:
            if event.key:
                _keys_just_pressed.add(event.key)
                _keys_pressed.add(event.key)
        elif event.type == pygame.KEYUP:
            if event.key:
                _keys_just_released.add(event.key)
                _keys_pressed.discard(event.key)
        elif event.type == _FOCUS_LOST_EVENT:
            # Fokus hilang: kosongkan held-state supaya tidak ada tombol macet
            _keys_pressed.clear()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # event.button 1-based (1=kiri, 2=tengah, 3=kanan) -> simpan
            # index 0-based supaya konsisten dengan tikus_tekanan() dan
            # tikus_baru_ditekan(0) == klik kiri. Button 4+ (scroll) diabaikan.
            if 1 <= event.button <= 3:
                _mouse_just_pressed.add(event.button - 1)
        elif event.type == pygame.MOUSEBUTTONUP:
            if 1 <= event.button <= 3:
                _mouse_just_released.add(event.button - 1)
        elif event.type == pygame.MOUSEWHEEL:
            _scroll = (event.x, event.y)

    # --- Gamepad ---
    if not _joystick_init_done:
        _init_joysticks()
    for j, joy in enumerate(_joysticks):
        try:
            n = max(joy.get_numbuttons(), 1)
            for b in range(n):
                pressed = joy.get_button(b)
                if pressed and not _joy_buttons[j][b]:
                    _joy_just_pressed[j][b] = True
                elif not pressed:
                    _joy_just_pressed[j][b] = False
                _joy_buttons[j][b] = pressed
        except pygame.error:
            continue


def ambil_events():
    """Mendapatkan daftar event pygame mentah frame ini (untuk game loop)."""
    return _events


def reset():
    """Reset seluruh state input (dipanggil saat game berhenti)."""
    global _keys_pressed, _joystick_init_done
    _keys_pressed.clear()
    _keys_just_pressed.clear()
    _keys_just_released.clear()
    _mouse_just_pressed.clear()
    _mouse_just_released.clear()
    _joysticks.clear()
    _joy_buttons.clear()
    _joy_just_pressed.clear()
    _joystick_init_done = False


# --- Keyboard ---

_KEY_MAP = {
    "UP": 1073741906, "DOWN": 1073741905,
    "LEFT": 1073741904, "RIGHT": 1073741903,
    "SPACE": 32, "ENTER": 13, "RETURN": 13,
    "ESCAPE": 27, "ESC": 27,
    "TAB": 9, "BACKSPACE": 8, "DELETE": 127,
    "LSHIFT": 1073742049, "RSHIFT": 1073742053,
    "LCTRL": 1073742048, "RCTRL": 1073742052,
    "LALT": 1073742050, "RALT": 1073742054,
    "HOME": 1073741898, "END": 1073741901,
    "PGUP": 1073741899, "PGDN": 1073741902,
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
    """Cek apakah tombol baru saja ditekan pada frame ini (satu kali).

    Contoh:
        input.tombol_baru_ditekan("SPACE")
    """
    _ensure_init()
    key = _resolve_key(nama)
    return key in _keys_just_pressed


def tombol_dilepas(nama) -> bool:
    """Cek apakah tombol baru saja dilepas pada frame ini."""
    _ensure_init()
    key = _resolve_key(nama)
    return key in _keys_just_released


def tombol_apa_saja_baru() -> str:
    """Nama tombol yang baru ditekan frame ini (atau None).

    Berguna untuk layar "tekan tombol apa saja".
    """
    _ensure_init()
    for key in _keys_just_pressed:
        name = pygame.key.name(key).upper()
        return name
    return None


# --- Mouse ---

def tikus_posisi() -> tuple:
    """Posisi mouse saat ini (x, y)."""
    _ensure_init()
    return _mouse_pos


def tikus_tekanan() -> tuple:
    """Status tombol mouse yang sedang ditekan: (kiri, tengah, kanan)."""
    _ensure_init()
    return _mouse_buttons


def tikus_tombol_ditekan(tombol: int = 0) -> bool:
    """Cek apakah tombol mouse sedang ditekan. 0=kiri, 1=tengah, 2=kanan."""
    _ensure_init()
    return _mouse_buttons[min(tombol, 2)]


def tikus_baru_ditekan(tombol: int = 0) -> bool:
    """Cek apakah tombol mouse baru ditekan pada frame ini.

    Contoh:
        jika input.tikus_baru_ditekan(0) maka
            # klik kiri sekali
        selesai
    """
    _ensure_init()
    return min(tombol, 3) in _mouse_just_pressed


def tikus_dilepas(tombol: int = 0) -> bool:
    """Cek apakah tombol mouse baru dilepas pada frame ini."""
    _ensure_init()
    return min(tombol, 3) in _mouse_just_released


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


def geser() -> tuple:
    """Scroll wheel pada frame ini: (dx, dy). y positif = scroll atas.

    Contoh:
        buat (sx, sy) = input.geser()
        jika sy != 0 maka
            tulis "scroll:", sy
        selesai
    """
    _ensure_init()
    return _scroll


# --- Gamepad / Joystick ---

def gamepad_ada() -> bool:
    """Cek apakah ada gamepad/joystick terhubung."""
    _ensure_init()
    if not _joystick_init_done:
        _init_joysticks()
    return len(_joysticks) > 0


def gamepad_jumlah() -> int:
    """Jumlah gamepad yang terhubung."""
    _ensure_init()
    if not _joystick_init_done:
        _init_joysticks()
    return len(_joysticks)


def gamepad_sumbu(index: int = 0, axis: int = 0) -> float:
    """Nilai sumbu gamepad (-1.0 .. 1.0). axis 0=x, 1=y.

    Contoh:
        buat vx = input.gamepad_sumbu(0, 0)
        buat vy = input.gamepad_sumbu(0, 1)
    """
    _ensure_init()
    if index >= len(_joysticks):
        return 0.0
    try:
        return float(_joysticks[index].get_axis(axis))
    except pygame.error:
        return 0.0


def gamepad_tombol(index: int = 0, button: int = 0) -> bool:
    """Cek apakah tombol gamepad sedang ditekan."""
    _ensure_init()
    if index >= len(_joy_buttons):
        return False
    if button >= len(_joy_buttons[index]):
        return False
    return _joy_buttons[index][button]


def gamepad_tombol_baru(index: int = 0, button: int = 0) -> bool:
    """Cek apakah tombol gamepad baru ditekan pada frame ini."""
    _ensure_init()
    if index >= len(_joy_just_pressed):
        return False
    if button >= len(_joy_just_pressed[index]):
        return False
    return _joy_just_pressed[index][button]


# --- Event ---

def _is_quit_event(event) -> bool:
    return event.type == pygame.QUIT


def events_quit() -> bool:
    """Cek apakah ada event quit (X jendela ditutup) pada frame ini."""
    _ensure_init()
    return any(_is_quit_event(e) for e in _events)


def events_tombol() -> list:
    """Mendapatkan semua nama tombol yang ditekan pada frame ini."""
    _ensure_init()
    result = []
    for event in _events:
        if event.type == pygame.KEYDOWN:
            name = pygame.key.name(event.key).upper()
            result.append(name)
    return result


def events_mouse() -> list:
    """Mendapatkan semua event mouse pada frame ini.

    Tiap event: {"tombol": button, "posisi": (x, y)}

    Catatan: `tombol` memakai numbering mentah pygame (1=kiri, 2=tengah,
    3=kanan) — beda dengan API just-pressed 0-based (`tikus_baru_ditekan`).
    """
    _ensure_init()
    result = []
    for event in _events:
        if event.type == pygame.MOUSEBUTTONDOWN:
            result.append({"tombol": event.button, "posisi": event.pos})
    return result


def events_geser() -> list:
    """Mendapatkan semua event scroll pada frame ini.

    Tiap event: {"x": dx, "y": dy}
    """
    _ensure_init()
    result = []
    for event in _events:
        if event.type == pygame.MOUSEWHEEL:
            result.append({"x": event.x, "y": event.y})
    return result


module = SimpleNamespace(
    tombol_ditekan=tombol_ditekan,
    tombol_baru_ditekan=tombol_baru_ditekan,
    tombol_dilepas=tombol_dilepas,
    tombol_apa_saja_baru=tombol_apa_saja_baru,
    tikus_posisi=tikus_posisi,
    tikus_tekanan=tikus_tekanan,
    tikus_tombol_ditekan=tikus_tombol_ditekan,
    tikus_baru_ditekan=tikus_baru_ditekan,
    tikus_dilepas=tikus_dilepas,
    tikus_gerakan=tikus_gerakan,
    tikus_set_posisi=tikus_set_posisi,
    tikus_tampil=tikus_tampil,
    geser=geser,
    gamepad_ada=gamepad_ada,
    gamepad_jumlah=gamepad_jumlah,
    gamepad_sumbu=gamepad_sumbu,
    gamepad_tombol=gamepad_tombol,
    gamepad_tombol_baru=gamepad_tombol_baru,
    events_quit=events_quit,
    events_tombol=events_tombol,
    events_mouse=events_mouse,
    events_geser=events_geser,
    _update=_update,
    _events=ambil_events,
    _reset=reset,
)
