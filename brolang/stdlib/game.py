"""
Modul Game BroLang
==================

Game loop, scene management, dan utilitas game.

Game loop menggunakan modul `input` sebagai satu-satunya konsumen event
queue pygame. Di awal tiap frame: `input._update()` menguras event,
lalu game loop membaca event QUIT/ESC/on_event dari `input.ambil_events()`.
Dengan begitu modul input dan game loop tidak berebut event.

Contoh:
    impor game
    game.buat_jendela(800, 600, "Gameku")
    game.tambah_scene("utama", update_utama, gambar_utama)
    game.ganti_scene("utama")
    game.mulai()
"""

from types import SimpleNamespace

try:
    import pygame
except ImportError:
    pygame = None


# --- Game State ---


class _GameState:
    def __init__(self):
        self.running = False
        self.paused = False
        self.scenes = {}
        self.current_scene = None
        self.scene_stack = []  # tumpukan scene untuk overlay (menu pause, dll)
        self.transisi = None  # state transisi scene aktif (dict) atau None
        self.data = {}
        self.lebar = 800
        self.tinggi = 600
        self.judul = "BroLang Game"
        self.fps = 60
        self.latar_warna = (0, 0, 0)
        self.tampil_fps = False
        self.esc_keluar = True
        self.on_init = None
        self.on_event = None
        self.on_pause = None
        self.on_resume = None
        self.on_exit = None
        # v6.6: fixed timestep fisika
        self.fisika_fungsi = None
        self.fisika_timestep = 1.0 / 60.0
        self.fisika_akumulator = 0.0
        self.fisika_maks_langkah = 5


_state = _GameState()


# --- Jendela ---


def atur_fps(fps: int):
    """Mengatur target FPS.

    Contoh:
        game.atur_fps(60)
    """
    _state.fps = int(fps)


def dapatkan_data() -> dict:
    """Akses data global game (untuk menyimpan skor, status, dll).

    Contoh:
        game.dapatkan_data()["skor"] = 0
    """
    return _state.data


def set_latar_warna(warna):
    """Mengatur warna latar layar.

    Contoh:
        game.set_latar_warna("biru_gelap")
        game.set_latar_warna((10, 10, 30))
    """
    _state.latar_warna = _resolve_warna(warna)


def _resolve_warna(warna):
    if isinstance(warna, str):
        _COLORS = {
            "putih": (255, 255, 255),
            "hitam": (0, 0, 0),
            "merah": (255, 0, 0),
            "hijau": (0, 255, 0),
            "biru": (0, 0, 255),
            "kuning": (255, 255, 0),
            "cyan": (0, 255, 255),
            "magenta": (255, 0, 255),
            "abu-abu": (128, 128, 128),
            "jingga": (255, 165, 0),
            "ungu": (128, 0, 128),
            "pink": (255, 192, 203),
            "biru_gelap": (0, 0, 128),
            "hijau_gelap": (0, 128, 0),
            "langit": (135, 206, 235),
        }
        return _COLORS.get(warna, (0, 0, 0))
    return tuple(warna)


def set_tampil_fps(aktif: bool = True):
    """Tampilkan FPS di pojok layar.

    Contoh:
        game.set_tampil_fps(True)
    """
    _state.tampil_fps = bool(aktif)


def set_esc_keluar(aktif: bool = True):
    """ESC langsung menutup game (default True)."""
    _state.esc_keluar = bool(aktif)


def atur_fisika(fungsi, timestep=1.0 / 60.0):
    """Set fungsi fisika dengan fixed timestep — v6.6.

    `fungsi` dipanggil dengan dt TETAP (mis. 1/120 detik) beberapa kali
    per frame sesuai akumulasi waktu — membuat simulasi fisika deterministik
    dan tidak bergantung pada FPS rendering.

    Args:
        fungsi: Callback `fungsi(fisika_dt)` yang dipanggil tiap langkah.
        timestep: Interval fisika dalam detik (default 1/60).

    Contoh:
        game.atur_fisika(update_fisika, timestep=1/120)
    """
    _state.fisika_fungsi = fungsi
    _state.fisika_timestep = max(0.0001, float(timestep))
    _state.fisika_akumulator = 0.0


# --- Scene Management ---


def tambah_scene(nama: str, fungsi_update=None, fungsi_gambar=None, on_masuk=None, on_keluar=None):
    """Menambah scene baru.

    Scene punya lifecycle penuh:
    - on_masuk : dipanggil sekali saat scene menjadi aktif
    - on_keluar: dipanggil sekali saat scene diganti
    - fungsi_update: dipanggil tiap frame (logika)
    - fungsi_gambar: dipanggil tiap frame (render)

    Contoh:
        game.tambah_scene("menu", update_menu, gambar_menu,
                          on_masuk=mulai_menu, on_keluar=bersihkan_menu)
        game.tambah_scene("main", update_main, gambar_main)
    """
    _state.scenes[nama] = {
        "update": fungsi_update,
        "gambar": fungsi_gambar,
        "on_masuk": on_masuk,
        "on_keluar": on_keluar,
    }


def _ganti_scene_langsung(nama: str):
    """Ganti scene seketika + panggil callback lifecycle."""
    lama = _state.current_scene
    if lama and lama in _state.scenes:
        cb = _state.scenes[lama].get("on_keluar")
        if cb:
            cb()
    _state.current_scene = nama
    baru = _state.scenes.get(nama)
    if baru and baru.get("on_masuk"):
        baru["on_masuk"]()


_TRANSISI_DIDUKUNG = ("fade",)


def ganti_scene(nama: str, transisi=None, durasi: float = 0.5, warna="hitam"):
    """Beralih ke scene lain, dengan transisi opsional.

    Args:
        nama: Nama scene tujuan.
        transisi: Jenis transisi. Saat ini mendukung "fade" (fade ke warna
            lalu masuk scene baru). None/kosong/jenis tak dikenal = langsung
            ganti tanpa transisi.
        durasi: Durasi total transisi dalam detik (default 0.5s).
        warna: Warna overlay transisi (default "hitam").

    Contoh:
        game.ganti_scene("main")
        game.ganti_scene("main", transisi="fade", durasi=1.0, warna="hitam")
    """
    if nama not in _state.scenes:
        raise ValueError(f"Scene '{nama}' tidak ditemukan.")
    if transisi and transisi in _TRANSISI_DIDUKUNG:
        # Jika ada transisi lain yang sedang berjalan, selesaikan dulu
        # (terapkan scene tujuannya) supaya tidak ada switch tersisa.
        if _state.transisi is not None:
            _ganti_scene_langsung(_state.transisi["tujuan"])
        _state.transisi = {
            "jenis": transisi,
            "durasi": max(0.01, float(durasi)),
            "waktu": 0.0,
            "arah": "gelap",  # fase 1: fade ke warna
            "tujuan": nama,
            "warna": warna,
        }
    else:
        # Ganti langsung — batalkan transisi yang sedang berjalan agar
        # tidak ada switch tertunda yang menimpa scene yang baru di-set.
        _state.transisi = None
        _ganti_scene_langsung(nama)


def _update_transisi(dt: float) -> bool:
    """Memajukan state transisi scene. Dipanggil tiap frame oleh game loop.

    Returns:
        True jika transisi masih berjalan, False jika sudah selesai.
    """
    t = _state.transisi
    if t is None:
        return False
    t["waktu"] += dt
    setengah = t["durasi"] / 2.0
    if t["arah"] == "gelap" and t["waktu"] >= setengah:
        # Paling gelap — ganti scene sekarang
        _ganti_scene_langsung(t["tujuan"])
        t["arah"] = "terang"
        t["waktu"] = setengah
    if t["arah"] == "terang" and t["waktu"] >= t["durasi"]:
        _state.transisi = None
        return False
    return True


def _alpha_transisi() -> int:
    """Alpha overlay transisi saat ini (0 = transparan, 255 = pekat)."""
    t = _state.transisi
    if t is None:
        return 0
    setengah = t["durasi"] / 2.0
    if t["arah"] == "gelap":
        p = min(t["waktu"] / setengah, 1.0)
    else:
        p = max(0.0, 1.0 - (t["waktu"] - setengah) / setengah)
    return int(255 * p)


def _gambar_transisi(screen):
    """Menggambar overlay transisi (fade) di atas scene."""
    if pygame is None or _state.transisi is None:
        return
    alpha = _alpha_transisi()
    if alpha <= 0:
        return
    try:
        warna = _resolve_warna(_state.transisi["warna"])
        lebar, tinggi = screen.get_size()
        overlay = pygame.Surface((lebar, tinggi), pygame.SRCALPHA)
        overlay.fill((*warna, alpha))
        screen.blit(overlay, (0, 0))
    except (pygame.error, ValueError, TypeError):
        pass


def transisi_aktif() -> bool:
    """Cek apakah scene sedang dalam transisi."""
    return _state.transisi is not None


def progres_transisi() -> float:
    """Progres transisi 0.0 .. 1.0 (0 = belum mulai, 1 = selesai).

    Berguna untuk animasi paralel (mis. zoom kamera selama fade).
    """
    t = _state.transisi
    if t is None:
        return 1.0
    return min(t["waktu"] / t["durasi"], 1.0)


def dapatkan_scene_sekarang() -> str:
    """Mendapatkan nama scene aktif."""
    return _state.current_scene


def hapus_scene(nama: str):
    """Menghapus scene."""
    _state.scenes.pop(nama, None)


# --- Scene Stack (overlay) ---


def dorong_scene(nama: str, transisi=None, durasi: float = 0.5, warna="hitam"):
    """Menumpuk scene baru di atas scene sekarang (overlay).

    Scene di bawah tetap digambar tapi tidak di-update — cocok untuk
    menu pause / dialog di atas gameplay.

    Contoh:
        game.dorong_scene("pause", transisi="fade")
        game.pop_scene(transisi="fade")
    """
    if nama not in _state.scenes:
        raise ValueError(f"Scene '{nama}' tidak ditemukan.")
    _state.scene_stack.append(_state.current_scene)
    ganti_scene(nama, transisi, durasi, warna)


def pop_scene(transisi=None, durasi: float = 0.5, warna="hitam"):
    """Kembali ke scene sebelumnya di tumpukan (menutup overlay).

    Contoh:
        game.pop_scene(transisi="fade")
    """
    if not _state.scene_stack:
        raise ValueError("Tumpukan scene kosong — tidak ada scene untuk kembali.")
    tujuan = _state.scene_stack.pop()
    ganti_scene(tujuan, transisi, durasi, warna)


def kedalaman_tumpukan() -> int:
    """Jumlah scene yang sedang ditumpuk (0 = tidak ada overlay)."""
    return len(_state.scene_stack)


# --- Pause / Resume ---


def pause():
    """Pause game loop (update & gambar di-skip, loop tetap hidup)."""
    if not _state.paused:
        _state.paused = True
        if _state.on_pause:
            _state.on_pause()


def resume():
    """Lanjutkan game loop setelah pause."""
    if _state.paused:
        _state.paused = False
        if _state.on_resume:
            _state.on_resume()


def set_pause(nilai: bool):
    """Set status pause."""
    if nilai:
        pause()
    else:
        resume()


def sedang_pause() -> bool:
    """Cek apakah game sedang pause."""
    return _state.paused


# --- Game Loop ---


def buat_jendela(lebar: int, tinggi: int, judul: str = "BroLang Game"):
    """Setup jendela game.

    Contoh:
        game.buat_jendela(800, 600, "Gameku")
    """
    _state.lebar = lebar
    _state.tinggi = tinggi
    _state.judul = judul

    if pygame is None:
        raise RuntimeError("Pygame tidak terinstal. Jalankan: pip install pygame")

    pygame.init()
    pygame.display.set_mode((lebar, tinggi))
    pygame.display.set_caption(judul)


_clock = None


def mulai():
    """Memulai game loop. Block sampai game selesai.

    Contoh:
        game.buat_jendela(800, 600, "Gameku")
        game.tambah_scene("main", update_main, gambar_main)
        game.ganti_scene("main")
        game.mulai()
    """
    global _clock
    if pygame is None:
        raise RuntimeError("Pygame tidak terinstal. Jalankan: pip install pygame")

    from brolang.stdlib import input as input_mod

    input_mod.reset()

    clock = pygame.time.Clock()
    _clock = clock
    _state.running = True
    _state.paused = False

    if _state.on_init:
        _state.on_init()

    fps_font = None
    if _state.tampil_fps:
        fps_font = pygame.font.SysFont(None, 24)

    while _state.running:
        # Input adalah pemilik event queue — kuras duluan
        input_mod._update()
        events = input_mod.ambil_events()

        # Proses event quit / escape / custom dari event yang sudah dikuras
        for event in events:
            if event.type == pygame.QUIT:
                _state.running = False
                break
            if _state.esc_keluar and event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                _state.running = False
                break
            if _state.on_event:
                _state.on_event(event)

        if not _state.running:
            break

        # dt dalam detik, di-clamp agar tidak meledak saat tab tidak fokus
        dt = clock.get_time() / 1000.0
        dt = min(dt, 0.05)

        screen = pygame.display.get_surface()

        if not _state.paused:
            # Update transisi scene dulu (bisa mengganti scene di tengah fade)
            _update_transisi(dt)
            # Update current scene
            scene = _state.scenes.get(_state.current_scene)
            if scene and scene["update"]:
                scene["update"](dt)
            # Fixed timestep fisika (v6.6): akumulasi dt lalu langkah tetap
            if _state.fisika_fungsi:
                _state.fisika_akumulator += dt
                langkah_fisika = 0
                while (_state.fisika_akumulator >= _state.fisika_timestep
                       and langkah_fisika < _state.fisika_maks_langkah):
                    _state.fisika_fungsi(_state.fisika_timestep)
                    _state.fisika_akumulator -= _state.fisika_timestep
                    langkah_fisika += 1
                if langkah_fisika >= _state.fisika_maks_langkah:
                    _state.fisika_akumulator = 0.0

        # Gambar: scene bertumpuk (dari bawah ke atas), lalu scene aktif
        screen.fill(_state.latar_warna)
        for nama in list(_state.scene_stack):
            sc = _state.scenes.get(nama)
            if sc and sc["gambar"]:
                sc["gambar"](screen)
        scene = _state.scenes.get(_state.current_scene)
        if scene and scene["gambar"]:
            scene["gambar"](screen)
        # Overlay transisi (fade) di paling atas
        _gambar_transisi(screen)

        if _state.tampil_fps and fps_font is not None:
            try:
                fps_surf = fps_font.render(f"FPS: {clock.get_fps():.0f}", True, (255, 255, 0))
                screen.blit(fps_surf, (8, 8))
            except Exception:
                pass

        pygame.display.flip()
        clock.tick(_state.fps)

    if _state.on_exit:
        _state.on_exit()

    input_mod.reset()
    pygame.quit()


def berhenti():
    """Menghentikan game loop."""
    _state.running = False


def sedang_berjalan() -> bool:
    """Cek apakah game sedang berjalan."""
    return _state.running


def reset():
    """Reset seluruh state game (scene, data, pause, tumpukan)."""
    _state.scenes = {}
    _state.current_scene = None
    _state.scene_stack = []
    _state.transisi = None
    _state.data = {}
    _state.paused = False
    _state.running = False


# --- Utilitas Game ---


def delta_time() -> float:
    """Waktu frame terakhir dalam detik (ter-clamp 0.05s)."""
    if pygame is None:
        return 0.0
    return min(pygame.time.get_time() / 1000.0, 0.05)


def waktu_sekarang() -> float:
    """Waktu dalam milidetik sejak pygame.init()."""
    if pygame is None:
        return 0.0
    return pygame.time.get_ticks()


def dapatkan_fps() -> float:
    """FPS aktual game loop (0 sebelum mulai)."""
    global _clock
    if _clock is None:
        return 0.0
    return _clock.get_fps()


def atur_data(kunci, nilai):
    """Set satu kunci di data global game."""
    _state.data[kunci] = nilai


def dapatkan_ukuran() -> tuple:
    """Ukuran jendela (lebar, tinggi)."""
    return (_state.lebar, _state.tinggi)


def atur_ukuran_jendela(lebar: int, tinggi: int):
    """Ubah ukuran jendela game — v6.6.

    Contoh:
        game.atur_ukuran_jendela(1280, 720)
    """
    _state.lebar = int(lebar)
    _state.tinggi = int(tinggi)
    if pygame is not None:
        try:
            pygame.display.set_mode((_state.lebar, _state.tinggi))
        except (pygame.error, TypeError):
            pass


def tangkap_layar(path="screenshot.png"):
    """Simpan screenshot layar saat ini ke file — v6.6.

    Contoh:
        game.tangkap_layar("skor_tinggi.png")
    """
    if pygame is None:
        raise RuntimeError("Pygame tidak terinstal. Jalankan: pip install pygame")
    screen = pygame.display.get_surface()
    if screen is None:
        raise RuntimeError("Jendela belum dibuat.")
    pygame.image.save(screen, str(path))
    return path


module = SimpleNamespace(
    buat_jendela=buat_jendela,
    mulai=mulai,
    berhenti=berhenti,
    sedang_berjalan=sedang_berjalan,
    reset=reset,
    tambah_scene=tambah_scene,
    ganti_scene=ganti_scene,
    dorong_scene=dorong_scene,
    pop_scene=pop_scene,
    kedalaman_tumpukan=kedalaman_tumpukan,
    transisi_aktif=transisi_aktif,
    progres_transisi=progres_transisi,
    dapatkan_scene_sekarang=dapatkan_scene_sekarang,
    hapus_scene=hapus_scene,
    dapatkan_data=dapatkan_data,
    atur_data=atur_data,
    atur_fps=atur_fps,
    set_latar_warna=set_latar_warna,
    set_tampil_fps=set_tampil_fps,
    set_esc_keluar=set_esc_keluar,
    pause=pause,
    resume=resume,
    set_pause=set_pause,
    sedang_pause=sedang_pause,
    delta_time=delta_time,
    waktu_sekarang=waktu_sekarang,
    dapatkan_fps=dapatkan_fps,
    dapatkan_ukuran=dapatkan_ukuran,
    atur_fisika=atur_fisika,
    atur_ukuran_jendela=atur_ukuran_jendela,
    tangkap_layar=tangkap_layar,
    _update_transisi=_update_transisi,
    _alpha_transisi=_alpha_transisi,
    _ganti_scene_langsung=_ganti_scene_langsung,
)
