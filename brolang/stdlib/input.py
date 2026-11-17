"""
Modul Input BroLang (v11 Upgrade)
==================================

Input keyboard, mouse, scroll, gamepad/joystick dengan sistem mapping aksi.

Fitur v11:
- Pemetaan tombol ke aksi (input.atur_peta_aksi("lompat", "SPACE", "UP")).
- Cek aksi: input.aksi_tekan("lompat"), input.aksi_baru_tekan("lompat").
- Gamepad/joystick dengan dukungan sumbu, tombol, dan getaran (rumble).
- Posisi, gerak relatif, scroll wheel, klik baru / dilepas.
- Gestur sederhana (swipe kiri/kanan/atas/bawah).
- Fokus jendela (hilang/kembali).
- Reset state antar frame (dipanggil oleh game loop).

Contoh:
    impor input
    input.atur_peta_aksi("lompat", "SPACE", "UP")
    input.atur_peta_aksi("gerak_kiri", "a", "LEFT")
    jika input.aksi_baru_tekan("lompat") maka
        tulis "Lompat!"
    selesai
    buat (ax, ay) = input.gamepad_sumbu(0, 0)   # joystick kiri pemain 1
    input.gamepad_getar(0, 0.5, 0.5, 0.2)      # getar 0.2 detik
"""

from types import SimpleNamespace

try:
    import pygame
except ImportError:
    pygame = None

_FOCUS_LOST_EVENT = getattr(pygame, "WINDOWFOCUSLOST", None) if pygame else None

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
_joy_just_released = []
_joy_axes = []
_joystick_init_done = False

# Pemetaan nama tombol -> kód pygame (untuk kompatibilitas tes v66)
_KEY_MAP = {
    "SPACE": pygame.K_SPACE if pygame else 32,
    "UP": pygame.K_UP if pygame else 273,
    "DOWN": pygame.K_DOWN if pygame else 274,
    "LEFT": pygame.K_LEFT if pygame else 276,
    "RIGHT": pygame.K_RIGHT if pygame else 275,
    "W": pygame.K_w if pygame else 119,
    "A": pygame.K_a if pygame else 97,
    "S": pygame.K_s if pygame else 115,
    "D": pygame.K_d if pygame else 100,
    "ENTER": pygame.K_RETURN if pygame else 13,
    "ESC": pygame.K_ESCAPE if pygame else 27,
    "SHIFT": pygame.K_LSHIFT if pygame else 306,
    "CTRL": pygame.K_LCTRL if pygame else 305,
    "LCTRL": pygame.K_LCTRL if pygame else 305,
    "RCTRL": pygame.K_RCTRL if pygame else 307,
    "ALT": pygame.K_LALT if pygame else 308,
    "TAB": pygame.K_TAB if pygame else 9,
    "BACKSPACE": pygame.K_BACKSPACE if pygame else 8,
    "DELETE": pygame.K_DELETE if pygame else 127,
    "F1": pygame.K_F1 if pygame else 282,
    "F2": pygame.K_F2 if pygame else 283,
    "F3": pygame.K_F3 if pygame else 284,
    "F4": pygame.K_F4 if pygame else 285,
    "F5": pygame.K_F5 if pygame else 286,
    "F6": pygame.K_F6 if pygame else 287,
    "F7": pygame.K_F7 if pygame else 288,
    "F8": pygame.K_F8 if pygame else 289,
    "F9": pygame.K_F9 if pygame else 290,
    "F10": pygame.K_F10 if pygame else 291,
    "F11": pygame.K_F11 if pygame else 292,
    "F12": pygame.K_F12 if pygame else 293,
}

# Event tracking tambahan untuk kueri antrian event
_events_quit = False
_events_geser = []   # list dict {"x":.., "y":..}
_events_tombol = set()  # set nama tombol yang baru ditekan frame ini


def _resolve_key(kunci):
    """Resolve kunci (nama string atau int) ke kód tombol pygame.

    Contoh:
        _resolve_key("SPACE") == 32   # pygame.K_SPACE
        _resolve_key("A") == 97       # pygame.K_a
        _resolve_key("a") == 97
        _resolve_key(77) == 77        # int langsung
    """
    if isinstance(kunci, int):
        return kunci
    if pygame is None:
        return None
    return _tombol_dari_string(str(kunci))


def _nama_dari_key(key_code):
    """Balik: kód pygame -> nama string (mis. 32 -> "SPACE")."""
    for nama, kode in _KEY_MAP.items():
        if kode == key_code:
            return nama
    return None


# Pemetaan aksi -> daftar tombol / kunci input
_action_map = {}
_action_reverse = {}  # tombol -> daftar aksi
_gestur_swipe_threshold = 40
_gestur_start = None
_gestur_start_time = None


def _ensure_init():
    if pygame is None:
        raise RuntimeError("Pygame tidak terinstal. Jalankan: pip install pygame")


def _init_joysticks():
    global _joystick_init_done, _joysticks, _joy_buttons, _joy_just_pressed
    global _joy_just_released, _joy_axes
    _joystick_init_done = True
    _joysticks.clear()
    _joy_buttons.clear()
    _joy_just_pressed.clear()
    _joy_just_released.clear()
    _joy_axes.clear()
    if pygame is None:
        return
    try:
        pygame.joystick.init()
        for i in range(pygame.joystick.get_count()):
            joy = pygame.joystick.Joystick(i)
            joy.init()
            _joysticks.append(joy)
            _joy_buttons.append([False] * joy.get_numbuttons())
            _joy_just_pressed.append(set())
            _joy_just_released.append(set())
            _joy_axes.append([0.0] * joy.get_numaxes())
    except (pygame.error, Exception):
        pass


def reset():
    """Reset state input (dipanggil game loop awal dan akhir frame)."""
    global _mouse_just_pressed, _mouse_just_released
    global _keys_just_pressed, _keys_just_released
    global _joy_just_pressed, _joy_just_released, _scroll, _mouse_rel
    global _events, _events_quit, _events_geser, _events_tombol
    _mouse_just_pressed = set()
    _mouse_just_released = set()
    _keys_just_pressed = set()
    _keys_just_released = set()
    _joy_just_pressed = [set() for _ in _joysticks]
    _joy_just_released = [set() for _ in _joysticks]
    _scroll = (0, 0)
    _mouse_rel = (0, 0)
    _events = []
    _events_quit = False
    _events_geser = []
    _events_tombol = set()


def _update():
    """Kuras event pygame (dipanggil game loop awal frame)."""
    global _mouse_pos, _mouse_rel, _mouse_buttons
    global _keys_pressed, _scroll, _events
    global _events_quit, _events_geser, _events_tombol
    global _mouse_just_pressed, _mouse_just_released
    global _keys_just_pressed, _keys_just_released
    if pygame is None:
        return
    if not _joystick_init_done:
        _init_joysticks()
    prev_mouse = _mouse_pos
    _mouse_rel = (0, 0)
    _scroll = (0, 0)
    _events = pygame.event.get()
    _events_quit = False
    _events_geser = []
    _events_tombol = set()
    # Reset tombol baru ditekan/dilepas setiap frame
    _mouse_just_pressed = set()
    _mouse_just_released = set()
    _keys_just_pressed = set()
    _keys_just_released = set()
    for event in _events:
        if event.type == pygame.QUIT:
            _events_quit = True
        elif event.type == pygame.MOUSEMOTION:
            _mouse_pos = event.pos
            _mouse_rel = event.rel
        elif event.type == pygame.MOUSEBUTTONDOWN:
            _mouse_just_pressed.add(event.button)
            btns = list(_mouse_buttons)
            if event.button <= 3:
                btns[event.button - 1] = True
            _mouse_buttons = tuple(btns)
        elif event.type == pygame.MOUSEBUTTONUP:
            _mouse_just_released.add(event.button)
            btns = list(_mouse_buttons)
            if event.button <= 3:
                btns[event.button - 1] = False
            _mouse_buttons = tuple(btns)
        elif event.type == pygame.MOUSEWHEEL:
            _scroll = (event.x, event.y)
            _events_geser.append({"x": event.x, "y": event.y})
        elif event.type == pygame.KEYDOWN:
            _keys_just_pressed.add(event.key)
            _keys_pressed.add(event.key)
            nama = _nama_dari_key(event.key)
            if nama:
                _events_tombol.add(nama)
        elif event.type == pygame.KEYUP:
            _keys_just_released.add(event.key)
            _keys_pressed.discard(event.key)
        elif event.type == pygame.JOYBUTTONDOWN:
            jid = event.joy
            if jid < len(_joy_buttons):
                _joy_just_pressed[jid].add(event.button)
                _joy_buttons[jid][event.button] = True
        elif event.type == pygame.JOYBUTTONUP:
            jid = event.joy
            if jid < len(_joy_buttons):
                _joy_just_released[jid].add(event.button)
                _joy_buttons[jid][event.button] = False
        elif event.type == pygame.JOYAXISMOTION:
            jid = event.joy
            if jid < len(_joy_axes) and event.axis < len(_joy_axes[jid]):
                _joy_axes[jid][event.axis] = round(event.value, 3)


def ambil_events():
    return list(_events)


# --- Keyboard ---


def tombol_ditekan(kunci) -> bool:
    """Cek apakah tombol sedang ditekan. Menerima nama string ("SPACE") atau kód int."""
    kode = _resolve_key(kunci)
    if kode is not None and kode in _keys_pressed:
        return True
    for nama_aksi, tombol_list in _action_map.items():
        if kunci in tombol_list and aksi_ditekan(nama_aksi):
            return True
    return False


def tombol_baru_ditekan(kunci) -> bool:
    """Cek apakah tombol baru ditekan frame ini. Menerima nama string atau kód int."""
    kode = _resolve_key(kunci)
    if kode is not None and kode in _keys_just_pressed:
        return True
    return kunci in _keys_just_pressed


def tombol_baru_dilepas(kunci) -> bool:
    """Cek apakah tombol baru dilepas frame ini. Menerima nama string atau kód int."""
    kode = _resolve_key(kunci)
    if kode is not None and kode in _keys_just_released:
        return True
    return kunci in _keys_just_released


def tombol_dilepas(kunci) -> bool:
    """Alias tombol_baru_dilepas."""
    return tombol_baru_dilepas(kunci)


def semua_tombol_ditekan():
    return set(_keys_pressed)


# --- Event queue queries ---


def events_quit() -> bool:
    """Apakah ada event QUIT di antrian frame ini."""
    return _events_quit


def events_geser():
    """Daftar event scroll wheel frame ini: list dict {"x":.., "y":..}."""
    return list(_events_geser)


def events_tombol():
    """Set nama tombol yang baru ditekan frame ini."""
    return set(_events_tombol)


# --- Mouse ---


def tikus_posisi() -> tuple:
    if pygame is not None:
        return pygame.mouse.get_pos()
    return _mouse_pos


def tikus_gerak_rel() -> tuple:
    return _mouse_rel


def tikus_ditekan(tombol=0) -> bool:
    return tombol < len(_mouse_buttons) and _mouse_buttons[tombol]


def tikus_baru_ditekan(tombol=0) -> bool:
    return (tombol + 1) in _mouse_just_pressed


def tikus_baru_dilepas(tombol=0) -> bool:
    return (tombol + 1) in _mouse_just_released


def tikus_dilepas(tombol=0) -> bool:
    """Alias tikus_baru_dilepas."""
    return tikus_baru_dilepas(tombol)


def geser() -> tuple:
    return _scroll


# --- Action Mapping ---


def atur_peta_aksi(nama_aksi, *kunci):
    """Peta satu atau lebih tombol ke nama aksi.

    Contoh: input.atur_peta_aksi("lompat", "SPACE", "UP")
    """
    _action_map[nama_aksi] = list(kunci)
    for k in kunci:
        _action_reverse.setdefault(k, []).append(nama_aksi)


def hapus_peta_aksi(nama_aksi):
    if nama_aksi in _action_map:
        for k in _action_map.pop(nama_aksi):
            lst = _action_reverse.get(k)
            if lst:
                lst.remove(nama_aksi)
                if not lst:
                    _action_reverse.pop(k, None)


def daftar_aksi():
    return list(_action_map.keys())


def _tombol_dari_string(nama):
    if pygame is None:
        return None
    nama = nama.upper()
    tabel = {
        "SPACE": pygame.K_SPACE, "UP": pygame.K_UP, "DOWN": pygame.K_DOWN,
        "LEFT": pygame.K_LEFT, "RIGHT": pygame.K_RIGHT,
        "W": pygame.K_w, "A": pygame.K_a, "S": pygame.K_s, "D": pygame.K_d,
        "ENTER": pygame.K_RETURN, "ESC": pygame.K_ESCAPE,
        "SHIFT": pygame.K_LSHIFT, "CTRL": pygame.K_LCTRL,
        "ALT": pygame.K_LALT, "TAB": pygame.K_TAB,
        "BACKSPACE": pygame.K_BACKSPACE, "DELETE": pygame.K_DELETE,
    }
    if nama in tabel:
        return tabel[nama]
    # Coba atribut pygame.K_*
    return getattr(pygame, "K_" + nama.lower(), None)


def _resolve_key(kunci):
    """Resolve kunci (nama string atau int) ke kód tombol pygame.

    Contoh:
        _resolve_key("SPACE") == 32   # pygame.K_SPACE
        _resolve_key("A") == 97       # pygame.K_a
        _resolve_key("a") == 97
        _resolve_key(77) == 77        # int langsung
    """
    if isinstance(kunci, int):
        return kunci
    if pygame is None:
        return None
    return _tombol_dari_string(str(kunci))


def aksi_ditekan(nama_aksi) -> bool:
    for k in _action_map.get(nama_aksi, []):
        tk = _tombol_dari_string(k)
        if tk is not None and tk in _keys_pressed:
            return True
        # Jika kunci adalah nama tombol mouse (mis. "mouse_left")
        if k == "mouse_left" and _mouse_buttons[:1] == (True,):
            return True
        if k == "mouse_right" and len(_mouse_buttons) > 1 and _mouse_buttons[1]:
            return True
    return False


def aksi_baru_tekan(nama_aksi) -> bool:
    for k in _action_map.get(nama_aksi, []):
        tk = _tombol_dari_string(k)
        if tk is not None and tk in _keys_just_pressed:
            return True
        if k == "mouse_left" and (1 in _mouse_just_pressed):
            return True
        if k == "mouse_right" and (3 in _mouse_just_pressed):
            return True
    return False


def aksi_baru_dilepas(nama_aksi) -> bool:
    for k in _action_map.get(nama_aksi, []):
        tk = _tombol_dari_string(k)
        if tk is not None and tk in _keys_just_released:
            return True
    return False


# --- Gamepad / Joystick ---


def jumlah_gamepad() -> int:
    return len(_joysticks)


def gamepad_ditekan(pemain, tombol) -> bool:
    if pemain < 0 or pemain >= len(_joy_buttons):
        return False
    return tombol < len(_joy_buttons[pemain]) and _joy_buttons[pemain][tombol]


def gamepad_baru_ditekan(pemain, tombol) -> bool:
    if pemain < 0 or pemain >= len(_joy_just_pressed):
        return False
    return tombol in _joy_just_pressed[pemain]


def gamepad_sumbu(pemain, sumbu) -> float:
    if pemain < 0 or pemain >= len(_joy_axes):
        return 0.0
    if sumbu < 0 or sumbu >= len(_joy_axes[pemain]):
        return 0.0
    return _joy_axes[pemain][sumbu]


def gamepad_getar(pemain, kecepatan_kecil, kecepatan_besar, durasi=0.0):
    """Getar gamepad (rumble). Hanya bekerja jika driver mendukung."""
    if pygame is None:
        return
    if pemain < 0 or pemain >= len(_joysticks):
        return
    try:
        joy = _joysticks[pemain]
        if hasattr(joy, "rumble"):
            joy.rumble(kecepatan_kecil, kecepatan_besar, int(durasi * 1000))
    except (pygame.error, Exception):
        pass


def gamepad_ada() -> bool:
    """Apakah ada setidaknya satu gamepad terhubung."""
    return len(_joysticks) > 0


def gamepad_jumlah() -> int:
    """Jumlah gamepad terhubung (alias jumlah_gamepad)."""
    return len(_joysticks)


def gamepad_tombol(pemain, tombol) -> bool:
    """Alias gamepad_ditekan."""
    return gamepad_ditekan(pemain, tombol)


# --- Gestur ---


def set_ambang_swipe(pixel: int = 40):
    _gestur_swipe_threshold = int(pixel)


def deteksi_swipe() -> str:
    """Deteksi gestur swipe berdasarkan gerak mouse dalam satu frame.
    Kembalikan: "kiri", "kanan", "atas", "bawah", atau "".
    """
    dx, dy = _mouse_rel
    if abs(dx) > abs(dy):
        if abs(dx) >= _gestur_swipe_threshold:
            return "kanan" if dx > 0 else "kiri"
    else:
        if abs(dy) >= _gestur_swipe_threshold:
            return "bawah" if dy > 0 else "atas"
    return ""


# --- Fokus ---


def fokus_hilang() -> bool:
    return any(e.type == _FOCUS_LOST_EVENT for e in _events) if _FOCUS_LOST_EVENT else False


module = SimpleNamespace(
    reset=reset,
    _update=_update,
    ambil_events=ambil_events,
    tombol_ditekan=tombol_ditekan,
    tombol_baru_ditekan=tombol_baru_ditekan,
    tombol_baru_dilepas=tombol_baru_dilepas,
    tombol_dilepas=tombol_dilepas,
    semua_tombol_ditekan=semua_tombol_ditekan,
    tikus_posisi=tikus_posisi,
    tikus_gerak_rel=tikus_gerak_rel,
    tikus_ditekan=tikus_ditekan,
    tikus_baru_ditekan=tikus_baru_ditekan,
    tikus_baru_dilepas=tikus_baru_dilepas,
    tikus_dilepas=tikus_dilepas,
    geser=geser,
    events_quit=events_quit,
    events_geser=events_geser,
    events_tombol=events_tombol,
    atur_peta_aksi=atur_peta_aksi,
    hapus_peta_aksi=hapus_peta_aksi,
    daftar_aksi=daftar_aksi,
    aksi_ditekan=aksi_ditekan,
    aksi_baru_tekan=aksi_baru_tekan,
    aksi_baru_dilepas=aksi_baru_dilepas,
    jumlah_gamepad=jumlah_gamepad,
    gamepad_ada=gamepad_ada,
    gamepad_jumlah=gamepad_jumlah,
    gamepad_ditekan=gamepad_ditekan,
    gamepad_tombol=gamepad_tombol,
    gamepad_baru_ditekan=gamepad_baru_ditekan,
    gamepad_sumbu=gamepad_sumbu,
    gamepad_getar=gamepad_getar,
    set_ambang_swipe=set_ambang_swipe,
    deteksi_swipe=deteksi_swipe,
    fokus_hilang=fokus_hilang,
    # untuk tes v66
    _KEY_MAP=_KEY_MAP,
    _resolve_key=_resolve_key,
)
