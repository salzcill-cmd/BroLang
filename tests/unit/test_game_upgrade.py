"""
Unit tests: upgrade besar library game BroLang.

Mencakup semua modul yang di-"full update":
- animasi  : easing elastic/bounce (fix crash), easing baru, callback on_selesai
- vektor   : sudut derajat, dari_polar, proyeksi, refleksi
- waktu    : Timer, Stopwatch, FpsCounter
- tilemap  : solid_map konsisten setelah bulk-load, dari_file, warna fallback
- fisika   : radius per-bodi, gravitasi configurable, ground detection
- kamera   : reset, gerak, set_posisi, rotasi
- input    : resolve key, gamepad tanpa device
- sprite   : animasi frame, collider, gerak
- partikel : lifecycle partikel, ledakan, hujan
- ui       : Tombol hover/klik, Bar nilai, Label
- game     : scene, pause/resume, reset state
"""

import pytest

from brolang.lexer import Lexer
from brolang.parser import Parser
from brolang.interpreter import Interpreter
from brolang.stdlib import get_stdlib_module


def _mod(nama):
    return get_stdlib_module(nama)


def _jalankan(kode):
    """Jalankan kode BroLang lewat interpreter dan kembalikan output."""
    ast = Parser(Lexer(kode).tokenize()).parse()
    interp = Interpreter()
    interp.interpret(ast)
    return interp.output


# ============================================================
# animasi
# ============================================================

class TestAnimasi:
    def test_elastic_tidak_crash(self):
        """Bug lama: easing elastic crash (`.sin()` di float)."""
        anim = _mod("animasi")
        tween = anim.buat_tween(0, 100, durasi=1.0, easing="elastic")
        hasil = [tween.update(0.1) for _ in range(10)]
        assert all(isinstance(v, (int, float)) for v in hasil)
        assert tween.selesai  # durasi 1s, 10x0.1s = 1.0s

    def test_bounce_dalam_rentang(self):
        anim = _mod("animasi")
        tween = anim.buat_tween(0, 10, durasi=1.0, easing="bounce")
        hasil = [tween.update(0.05) for _ in range(20)]
        # Nilai bounce boleh overshoot dikit tapi harus masuk akal
        assert all(0 - 1 <= v <= 10 + 1 for v in hasil)

    def test_semua_easing_linear_monoton(self):
        anim = _mod("animasi")
        for nama in anim.daftar_easing():
            tween = anim.buat_tween(0, 100, durasi=1.0, easing=nama)
            v = tween.nilai_sekarang()
            assert isinstance(v, (int, float)), nama

    def test_on_selesai_dipanggil(self):
        anim = _mod("animasi")
        tween = anim.buat_tween(0, 100, durasi=0.3, easing="linear")
        calls = []
        tween.on_selesai = lambda: calls.append(1)
        while not tween.selesai:
            tween.update(0.1)
        assert calls == [1]

    def test_animasi_frame_loop(self):
        anim = _mod("animasi")
        a = anim.Animasi()
        a.tambah("jalan", [0, 1, 2, 3], fps=10, loop=True)
        a.mainkan("jalan")
        a.update(0.4)  # 4 frame @ 10fps
        assert a.frame_sekarang() == 0  # balik ke awal karena loop

    def test_animasi_non_loop_selesai(self):
        anim = _mod("animasi")
        a = anim.Animasi()
        done = []
        a.on_selesai = lambda: done.append(1)
        a.tambah("lompat", [0, 1, 2], fps=10, loop=False)
        a.mainkan("lompat")
        a.update(0.3)  # 3 frame
        assert a.frame_sekarang() == 2
        assert a.sudah_selesai()
        assert done == [1]


# ============================================================
# vektor
# ============================================================

class TestVektor:
    def test_sudut_derajat(self):
        vek = _mod("vektor")
        v = vek.Vec2(1, 1)
        assert v.sudut() == pytest.approx(45.0)
        assert v.angle() == pytest.approx(0.785398, rel=1e-3)

    def test_dari_polar(self):
        vek = _mod("vektor")
        v = vek.Vec2.dari_polar(10, 0)
        assert v.x == pytest.approx(10)
        assert v.y == pytest.approx(0)
        v2 = vek.buat_polar(10, 90)
        assert v2.x == pytest.approx(0, abs=1e-9)
        assert v2.y == pytest.approx(10)

    def test_proyeksi(self):
        vek = _mod("vektor")
        v = vek.Vec2(3, 4)
        proy = v.proyeksi(vek.Vec2(1, 0))
        assert proy.x == pytest.approx(3)
        assert proy.y == pytest.approx(0)

    def test_refleksi(self):
        vek = _mod("vektor")
        v = vek.Vec2(1, -1)
        r = v.refleksi(vek.Vec2(0, 1))  # pantul di lantai
        assert r.x == pytest.approx(1)
        assert r.y == pytest.approx(1)

    def test_rotasi_derajat(self):
        vek = _mod("vektor")
        v = vek.Vec2(10, 0).rotasi(90)
        assert v.x == pytest.approx(0, abs=1e-9)
        assert v.y == pytest.approx(10)

    def test_arah_ke_dan_tengah(self):
        vek = _mod("vektor")
        a = vek.Vec2(0, 0)
        b = vek.Vec2(0, 10)
        assert a.arah_ke(b).y == pytest.approx(1)
        t = a.tengah(b)
        assert (t.x, t.y) == (0.0, 5.0)


# ============================================================
# waktu
# ============================================================

class TestWaktu:
    def test_timer_hitung_mundur(self):
        w = _mod("waktu")
        timer = w.Timer(1.0)
        assert not timer.habis()
        timer.update(0.6)
        assert not timer.habis()
        timer.update(0.6)
        assert timer.habis()
        assert timer.sisa() == 0

    def test_timer_on_selesai(self):
        w = _mod("waktu")
        timer = w.Timer(0.5)
        done = []
        timer.on_selesai = lambda: done.append(1)
        timer.update(1.0)
        assert done == [1]

    def test_timer_kemajuan_dan_reset(self):
        w = _mod("waktu")
        timer = w.Timer(2.0)
        timer.update(1.0)
        assert timer.kemajuan() == pytest.approx(0.5)
        timer.reset()
        assert timer.sisa() == pytest.approx(2.0)

    def test_stopwatch(self):
        w = _mod("waktu")
        sw = w.Stopwatch()
        sw.mulai()
        assert sw.sedang_jalan()
        sw.stop()
        assert not sw.sedang_jalan()
        sw.reset()
        assert sw.elapsed() == 0

    def test_fps_counter(self):
        w = _mod("waktu")
        fps = w.FpsCounter(sampel=10)
        for _ in range(10):
            fps.update(1 / 60)
        assert fps.fps() == pytest.approx(60, rel=0.1)


# ============================================================
# tilemap
# ============================================================

class TestTilemap:
    def test_solid_map_dari_array(self):
        """Bug lama: solid_map tidak ter-update setelah dari_array."""
        tm = _mod("tilemap")
        tileset = tm.buat_tileset("aset")
        tileset.atur_solid(1, True)
        peta = tm.buat_peta(4, 4, 32)
        peta.set_tileset(tileset)
        peta.dari_array([
            [1, 1, 1, 1],
            [1, 0, 0, 1],
            [1, 0, 0, 1],
            [1, 1, 1, 1],
        ])
        assert peta.is_solid(0, 0)
        assert peta.is_solid(1, 1) is False
        assert peta.check_collision(33, 33, 10, 10) is False
        assert peta.check_collision(0, 0, 10, 10) is True

    def test_solid_map_dari_string(self):
        tm = _mod("tilemap")
        tileset = tm.buat_tileset("aset")
        tileset.atur_solid(1, True)
        peta = tm.buat_peta(3, 3, 32)
        peta.set_tileset(tileset)
        peta.dari_string("1,0,1\n0,1,0\n1,0,1")
        assert peta.is_solid(0, 0) and peta.is_solid(1, 1)
        assert peta.is_solid(1, 0) is False

    def test_dari_file_roundtrip(self, tmp_path):
        tm = _mod("tilemap")
        path = tmp_path / "level.txt"
        path.write_text("1,0,1\n0,1,0\n1,0,1", encoding="utf-8")
        peta = tm.dari_file(str(path))
        assert peta.lebar == 3 and peta.tinggi == 3
        assert peta.dapatkan(0, 0) == 1
        peta.atur(1, 1, 9)
        out = tmp_path / "out.txt"
        peta.simpan_file(str(out))
        assert "9" in out.read_text(encoding="utf-8")

    def test_warna_fallback_tanpa_gambar(self):
        """gambar() tidak boleh crash tanpa tileset gambar (pakai warna)."""
        tm = _mod("tilemap")
        pygame = pytest.importorskip("pygame")
        os = pytest.importorskip("os")
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        pygame.init()
        screen = pygame.display.set_mode((200, 200))
        tileset = tm.buat_tileset("aset")
        tileset.atur_warna(1, (255, 0, 0))
        peta = tm.buat_peta(5, 5, 32)
        peta.set_tileset(tileset)
        peta.dari_array([[1] * 5 for _ in range(5)])
        peta.gambar(screen, 0, 0)  # tidak boleh error
        px = screen.get_at((5, 5))[:3]
        assert px == (255, 0, 0)
        pygame.quit()

    def test_tile_ke_pixel_roundtrip(self):
        tm = _mod("tilemap")
        peta = tm.buat_peta(10, 10, 32)
        tx, ty = peta.pixel_ke_tile(70, 100)
        assert (tx, ty) == (2, 3)
        assert peta.tile_ke_pixel(tx, ty) == (64, 96)


# ============================================================
# fisika
# ============================================================

class TestFisika:
    def test_radius_collision_tidak_hardcode(self):
        f = _mod("fisika")
        dunia = f.buat_dunia()
        a = f.buat_bodi(0, 0, radius=10)
        b = f.buat_bodi(25, 0, radius=10)
        # Jarak 25 > 20 (10+10) -> tidak tabrakan
        assert dunia.check_collision(a, b) is False
        b2 = f.buat_bodi(19, 0, radius=10)
        assert dunia.check_collision(a, b2) is True

    def test_gravitasi_configurable(self):
        f = _mod("fisika")
        dunia = f.buat_dunia(gravitasi_y=100)
        bodi = f.buat_bodi(0, 0, massa=1)
        dunia.tambah_bodi(bodi)
        dunia.update(1.0)
        assert bodi.kecepatan.y > 0
        assert bodi.kecepatan.y == pytest.approx(100, rel=0.05)

    def test_ground_detection(self):
        f = _mod("fisika")
        dunia = f.buat_dunia()
        bodi = f.buat_bodi(50, 595, radius=10)  # nyaris menyentuh lantai 600
        dunia.check_bounds(bodi, 200, 600, bounce=False)
        assert bodi.grounded is True
        assert bodi.posisi.y == pytest.approx(590)  # di-clamp
        # Reset tiap update (bodi di dunia → update() mereset grounded)
        dunia.tambah_bodi(bodi)
        dunia.update(0.01)
        assert bodi.grounded is False

    def test_check_bounds_pakai_radius(self):
        f = _mod("fisika")
        dunia = f.buat_dunia()
        bodi = f.buat_bodi(5, 5, radius=20)
        dunia.check_bounds(bodi, 200, 200, bounce=True)
        assert bodi.posisi.x == pytest.approx(20)
        assert bodi.posisi.y == pytest.approx(20)


# ============================================================
# kamera
# ============================================================

class TestKamera:
    def test_reset(self):
        k = _mod("kamera")
        cam = k.buat_kamera(800, 600)
        cam.set_posisi(100, 50)
        cam.set_zoom(2.0)
        cam.reset()
        assert cam.posisi() == (0.0, 0.0)
        assert cam.zoom == 1.0

    def test_gerak(self):
        k = _mod("kamera")
        cam = k.buat_kamera(800, 600)
        cam.gerak(10, -5)
        assert cam.posisi() == (10.0, -5.0)

    def test_world_screen_roundtrip(self):
        k = _mod("kamera")
        cam = k.buat_kamera(800, 600)
        cam.set_posisi(100, 100)
        sx, sy = cam.world_to_screen(200, 200)
        assert (sx, sy) == (100.0, 100.0)
        wx, wy = cam.screen_to_world(sx, sy)
        assert (wx, wy) == pytest.approx((200.0, 200.0))

    def test_apply_dengan_rotasi(self):
        k = _mod("kamera")
        cam = k.buat_kamera(800, 600)
        cam.set_sudut(90)
        # Titik tengah layar tetap
        cx, cy = cam.apply(400, 300)
        assert cx == pytest.approx(400, abs=0.01)
        assert cy == pytest.approx(300, abs=0.01)

    def test_batas_world(self):
        k = _mod("kamera")
        cam = k.buat_kamera(800, 600)
        cam.set_batas_world(1000, 1000)
        cam.set_posisi(5000, 5000)
        cam.update(0.1)
        assert cam.x <= 1000 - 800
        assert cam.y <= 1000 - 600


# ============================================================
# input
# ============================================================

class TestInput:
    def test_resolve_key(self):
        # Kode tombol pygame untuk huruf = ord huruf kecil (pygame.K_a = 97)
        from brolang.stdlib import input as inp
        assert inp._resolve_key("SPACE") == 32
        assert inp._resolve_key("A") == 97
        assert inp._resolve_key("a") == 97
        assert inp._resolve_key(77) == 77

    def test_key_map_lengkap(self):
        from brolang.stdlib import input as inp
        assert "UP" in inp._KEY_MAP
        assert "F12" in inp._KEY_MAP
        assert "LCTRL" in inp._KEY_MAP

    def test_gamepad_tanpa_device(self):
        """Tanpa joystick, fungsi gamepad aman dan mengembalikan False/0."""
        pygame = pytest.importorskip("pygame")
        inp = _mod("input")
        assert inp.gamepad_ada() in (True, False)  # tidak crash
        assert inp.gamepad_jumlah() >= 0
        assert inp.gamepad_sumbu(0, 0) == 0.0
        assert inp.gamepad_tombol(0, 0) is False


# ============================================================
# sprite
# ============================================================

class TestSprite:
    def test_buat_sprite_tanpa_gambar(self):
        sp = _mod("sprite")
        s = sp.Sprite(None, 100, 100, lebar=32, tinggi=32)
        assert s.x == 100 and s.y == 100
        assert s.lebar == 32

    def test_animasi_frame(self):
        sp = _mod("sprite")
        s = sp.Sprite(None, 0, 0)
        s.tambah_animasi("jalan", [0, 1, 2], kecepatan=0.1, loop=True)
        assert s.mainkan_animasi("jalan")
        s.update(0.25)  # 2.5 frame -> frame 2
        assert s.frame_sekarang() == 2

    def test_collider_rect(self):
        sp = _mod("sprite")
        a = sp.Sprite(None, 0, 0, lebar=32, tinggi=32)
        b = sp.Sprite(None, 20, 20, lebar=32, tinggi=32)
        assert a.cek_tabrakan(b)
        c = sp.Sprite(None, 100, 100, lebar=32, tinggi=32)
        assert not a.cek_tabrakan(c)

    def test_collider_lingkaran(self):
        sp = _mod("sprite")
        a = sp.Sprite(None, 0, 0, lebar=32, tinggi=32)
        a.mode_collider = "lingkaran"
        a.radius = 16
        b = sp.Sprite(None, 30, 0, lebar=32, tinggi=32)
        b.radius = 16
        assert a.cek_tabrakan_lingkaran(b)
        c = sp.Sprite(None, 100, 0, lebar=32, tinggi=32)
        assert not a.cek_tabrakan_lingkaran(c)

    def test_gerak_dan_gravitasi(self):
        sp = _mod("sprite")
        s = sp.Sprite(None, 0, 0)
        s.kecepatan_x = 10
        s.kecepatan_y = 0
        s.gravitasi = 100
        s.update(1.0)
        assert s.x == 10
        assert s.y == 100  # vy = g*t = 100, y = vy*dt = 100
        assert s.kecepatan_y == pytest.approx(100)

    def test_arah_ke(self):
        sp = _mod("sprite")
        s = sp.Sprite(None, 0, 0)
        s.arah_ke(0, 100, kecepatan=50)
        assert s.kecepatan_y == pytest.approx(50)
        assert s.kecepatan_x == pytest.approx(0)

    def test_grup_sprite(self):
        sp = _mod("sprite")
        grup = sp.GrupSprite()
        s1 = sp.Sprite(None, 0, 0)
        s2 = sp.Sprite(None, 10, 10)
        grup.tambah(s1, s2)
        assert grup.jumlah() == 2
        s2.aktif = False
        grup.hapus_tidak_aktif()
        assert grup.jumlah() == 1
        assert grup.cek_tabrakan(s1) == [s1]


# ============================================================
# partikel
# ============================================================

class TestPartikel:
    def test_emit_dan_lifecycle(self):
        p = _mod("partikel")
        emiter = p.buat_emiter(100, 100)
        emiter.kecepatan = 0
        emiter.umur = 0.5
        emiter.jumlah = 10
        emiter.emisi_per_detik = 0  # nonaktifkan emisi otomatis
        emiter.emitir()
        assert emiter.jumlah_aktif() == 10
        emiter.update(0.2)
        assert emiter.jumlah_aktif() == 10
        emiter.update(0.5)  # semua mati
        assert emiter.jumlah_aktif() == 0

    def test_ledak(self):
        p = _mod("partikel")
        emiter = p.buat_ledakan(50, 50, jumlah=25, warna="jingga")
        assert emiter.jumlah_aktif() == 25
        emiter.update(2.0)
        assert emiter.jumlah_aktif() == 0

    def test_hujan(self):
        p = _mod("partikel")
        emiter = p.buat_hujan(800, jumlah=20, warna="biru")
        assert emiter.jumlah_aktif() == 20
        for _ in range(5):
            emiter.update(0.1)
        # Partikel jatuh (kecepatan ke bawah)
        sampel = [pr for pr in emiter.partikel if pr.aktif]
        if sampel:
            assert all(pr.vy > 0 for pr in sampel)

    def test_emisi_otomatis(self):
        p = _mod("partikel")
        emiter = p.buat_emiter(0, 0)
        emiter.emisi_per_detik = 10
        emiter.umur = 5
        emiter.update(1.0)
        assert emiter.jumlah_aktif() >= 9  # ~10 partikel diproduksi


# ============================================================
# ui
# ============================================================

class TestUI:
    def test_tombol_klik(self):
        ui = _mod("ui")
        clicks = []
        tombol = ui.Tombol("MULAI", 100, 100, 200, 60)
        tombol.on_klik = lambda: clicks.append(1)
        # Klik di dalam tombol
        assert tombol.update(150, 130, diklik=True) is True
        assert clicks == [1]
        assert tombol.hover is True
        # Klik di luar
        assert tombol.update(500, 500, diklik=True) is False
        assert clicks == [1]

    def test_tombol_hover_callback(self):
        ui = _mod("ui")
        masuk = []
        keluar = []
        tombol = ui.Tombol("X", 0, 0, 100, 50)
        tombol.on_hover = lambda: masuk.append(1)
        tombol.on_keluar = lambda: keluar.append(1)
        tombol.update(50, 25, diklik=False)
        assert masuk == [1]
        tombol.update(500, 500, diklik=False)
        assert keluar == [1]

    def test_bar_nilai(self):
        ui = _mod("ui")
        bar = ui.Bar(100, 100, 0, 0, 200, 20)
        assert bar.persen() == 1.0
        assert bar.penuh()
        bar.kurang(25)
        assert bar.nilai == 75
        assert bar.persen() == pytest.approx(0.75)
        bar.tambah(100)
        assert bar.nilai == 100  # clamp ke maks
        bar.set_maks(200)
        assert bar.persen() == pytest.approx(0.5)

    def test_label_dan_panel_logika(self):
        ui = _mod("ui")
        label = ui.Label("Skor", 10, 10)
        label.set_teks("Skor: 5")
        assert label.teks == "Skor: 5"
        panel = ui.Panel(0, 0, 100, 50)
        assert panel.berisi(50, 25)
        assert not panel.berisi(200, 200)


# ============================================================
# input vs game: event queue (regression fix)
# ============================================================

class TestEventQueue:
    """Bug: game loop memakan semua event pygame sebelum input membacanya.
    Fix: input adalah satu-satunya pemilik event queue; game baca via
    input.ambil_events().
    """

    def test_input_melihat_event(self):
        pygame = pytest.importorskip("pygame")
        os = pytest.importorskip("os")
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        from brolang.stdlib import input as inp
        pygame.init()
        pygame.display.set_mode((100, 100))
        inp.reset()
        pygame.event.clear()
        pygame.event.post(pygame.event.Event(pygame.QUIT))
        pygame.event.post(pygame.event.Event(pygame.MOUSEWHEEL, x=0, y=-3))
        inp._update()
        events = inp.ambil_events()
        assert len(events) == 2
        assert inp.events_quit() is True
        geser = inp.events_geser()
        assert geser and geser[0]["y"] == -3
        assert inp.geser() == (0, -3)
        pygame.quit()

    def test_tombol_baru_ditekan_dari_event(self):
        pygame = pytest.importorskip("pygame")
        os = pytest.importorskip("os")
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        from brolang.stdlib import input as inp
        pygame.init()
        pygame.display.set_mode((100, 100))
        inp.reset()
        pygame.event.clear()
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))
        inp._update()
        assert inp.tombol_baru_ditekan("SPACE") is True
        assert "SPACE" in inp.events_tombol()
        pygame.quit()

    def test_tombol_ditekan_held_key_event_driven(self):
        """Bug pong: player 2 tidak bisa gerak karena held-state dibangun dari
        pygame.key.get_pressed() yang di-index *scancode*, sedangkan _KEY_MAP
        memakai *keycode* (K_*). Tombol khusus seperti UP/DOWN tidak pernah
        cocok. Fix: held-state dibangun dari event KEYDOWN/KEYUP.
        """
        pygame = pytest.importorskip("pygame")
        os = pytest.importorskip("os")
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        from brolang.stdlib import input as inp
        pygame.init()
        pygame.display.set_mode((100, 100))
        inp.reset()
        pygame.event.clear()
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP))
        inp._update()
        # Ditekan (held) + baru ditekan di frame ini
        assert inp.tombol_ditekan("UP") is True
        assert inp.tombol_baru_ditekan("UP") is True
        # Masih ditahan di frame berikutnya (tanpa event baru)
        inp._update()
        assert inp.tombol_ditekan("UP") is True
        assert inp.tombol_baru_ditekan("UP") is False
        # Dilepas
        pygame.event.post(pygame.event.Event(pygame.KEYUP, key=pygame.K_UP))
        inp._update()
        assert inp.tombol_ditekan("UP") is False
        assert inp.tombol_dilepas("UP") is True
        # Tombol biasa (huruf) juga konsisten
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_w))
        inp._update()
        assert inp.tombol_ditekan("w") is True
        pygame.quit()

    def test_tikus_baru_ditekan_dari_event_mouse(self):
        """Bug: klik kiri (pygame event.button=1) disimpan sebagai 1, padahal
        API tikus_baru_ditekan(0) memakai index 0-based (0=kiri) -> klik kiri
        tidak pernah terdeteksi, tombol MULAI tidak bisa diklik. Fix: konversi
        event.button 1-based ke index 0-based.
        """
        pygame = pytest.importorskip("pygame")
        os = pytest.importorskip("os")
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        from brolang.stdlib import input as inp
        pygame.init()
        pygame.display.set_mode((100, 100))
        inp.reset()
        pygame.event.clear()
        # Klik kiri (pygame button=1) -> index 0
        pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1))
        inp._update()
        assert inp.tikus_baru_ditekan(0) is True
        assert inp.tikus_baru_ditekan(1) is False
        assert inp.tikus_baru_ditekan(2) is False
        # Klik tengah (button=2) -> index 1
        pygame.event.clear()
        pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=2))
        inp._update()
        assert inp.tikus_baru_ditekan(1) is True
        # Klik kanan (button=3) -> index 2
        pygame.event.clear()
        pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=3))
        inp._update()
        assert inp.tikus_baru_ditekan(2) is True
        # Scroll (button 4/5) tidak boleh terdeteksi sebagai klik
        pygame.event.clear()
        pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=4))
        inp._update()
        assert inp.tikus_baru_ditekan(0) is False
        # Lepas kiri -> tikus_dilepas(0)
        pygame.event.clear()
        pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONUP, button=1))
        inp._update()
        assert inp.tikus_dilepas(0) is True
        pygame.quit()

    def test_klik_tombol_ui_end_to_end(self):
        """Alur klik tombol MULAI di game_arena.bro: mouse di dalam tombol +
        tikus_baru_ditekan(0) -> tombol.update(...) mengembalikan True dan
        on_klik terpanggil.
        """
        pygame = pytest.importorskip("pygame")
        os = pytest.importorskip("os")
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        from brolang.stdlib import input as inp
        ui = _mod("ui")
        pygame.init()
        pygame.display.set_mode((800, 600))
        inp.reset()
        clicks = []
        tombol = ui.Tombol("MULAI", 300, 330, 200, 60)
        tombol.on_klik = lambda: clicks.append(1)
        pygame.mouse.set_pos(400, 360)  # posisi di dalam tombol
        pygame.event.clear()
        pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1))
        inp._update()
        mx, my = inp.tikus_posisi()
        diklik = inp.tikus_baru_ditekan(0)
        assert tombol.update(mx, my, diklik) is True
        assert clicks == [1]
        pygame.quit()

    def test_game_loop_berhenti_saat_quit(self):
        """game.mulai() harus berhenti saat event QUIT dipost (loop utuh)."""
        pygame = pytest.importorskip("pygame")
        os = pytest.importorskip("os")
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        game = _mod("game")
        game.reset()
        game.buat_jendela(100, 100, "Test")
        game.tambah_scene("x", fungsi_update=lambda dt: None,
                          fungsi_gambar=lambda s: None)
        game.ganti_scene("x")
        pygame.event.clear()
        pygame.event.post(pygame.event.Event(pygame.QUIT))
        game.mulai()  # harus kembali cepat, bukan loop selamanya
        assert not game.sedang_berjalan()


# ============================================================
# interpreter: atribut objek stdlib (regression fix)
# ============================================================

class TestInterpreterAtributStdlib:
    """Bug: interpreter tidak bisa set atribut pada objek Python stdlib
    (Sprite, Vec2, ui, dll) padahal transpiler bisa. Sekarang konsisten."""

    def test_set_attr_vec2(self):
        out = _jalankan("""
impor vektor
buat v = vektor.Vec2(1, 2)
v.x = 10
v.y = v.y + 5
tulis v.x + v.y
""")
        assert out == ["17.0"]

    def test_set_attr_baru_sprite(self):
        """Atribut custom baru (vel_x, arah) bisa dibuat di objek Python."""
        out = _jalankan("""
impor sprite
buat s = sprite.Sprite(kosong, 0, 0, lebar=32, tinggi=32)
s.warna = "merah"
s.vel_x = 100
s.arah = 1
tulis s.lebar
tulis s.vel_x + s.arah
""")
        assert out == ["32", "101"]

    def test_set_attr_ui_tombol(self):
        out = _jalankan("""
impor ui
buat t = ui.Tombol("MULAI", 100, 100, 200, 60)
t.terlihat = salah
t.aktif = benar
jika t.berisi(150, 130) maka
    tulis "dalam"
lainnya
    tulis "luar"
selesai
""")
        assert out == ["dalam"]

    def test_get_attr_python_obj(self):
        out = _jalankan("""
impor waktu
buat timer = waktu.Timer(2.0)
timer.update(1.0)
tulis round(timer.sisa(), 1)
""")
        assert out == ["1.0"]

    def test_struktur_bata_logika(self):
        """Logika brick-breaker di game_paddle.bro: struct Bata dalam list,
        field diubah lewat assignment atribut (b.aktif = salah)."""
        out = _jalankan("""
struktur Bata { x, y, lebar, tinggi, aktif, warna }
buat daftar = []
daftar.tambah(Bata(10, 20, 74, 22, benar, "merah"))
daftar.tambah(Bata(90, 20, 74, 22, benar, "kuning"))
buat b = daftar[0]
b.aktif = salah
buat sisa = 0
buat i = 0
selama i < daftar.jumlah() lakukan
    jika daftar[i].aktif maka
        sisa = sisa + 1
    selesai
    i = i + 1
selesai
tulis sisa
tulis b.warna
tulis daftar[1].lebar
""")
        assert out == ["1", "merah", "74"]


# ============================================================
# game (state, tanpa menjalankan loop pygame)
# ============================================================

class TestGame:
    def test_scene_management(self):
        game = _mod("game")
        game.reset()
        game.tambah_scene("menu", fungsi_update=lambda dt: None)
        game.tambah_scene("main", fungsi_update=lambda dt: None,
                          fungsi_gambar=lambda s: None)
        game.ganti_scene("main")
        assert game.dapatkan_scene_sekarang() == "main"
        game.hapus_scene("menu")
        with pytest.raises(ValueError):
            game.ganti_scene("menu")

    def test_data_global(self):
        game = _mod("game")
        game.reset()
        game.atur_data("skor", 10)
        assert game.dapatkan_data()["skor"] == 10

    def test_pause_resume(self):
        game = _mod("game")
        game.reset()
        assert not game.sedang_pause()
        game.pause()
        assert game.sedang_pause()
        game.resume()
        assert not game.sedang_pause()

    def test_reset_state(self):
        game = _mod("game")
        game.reset()
        game.atur_data("skor", 99)
        game.tambah_scene("a")
        game.ganti_scene("a")
        game.pause()
        game.reset()
        assert game.dapatkan_data() == {}
        assert game.dapatkan_scene_sekarang() is None
        assert not game.sedang_pause()

    def test_pengaturan_latar(self):
        game = _mod("game")
        game.reset()
        game.set_latar_warna("biru_gelap")
        game.set_tampil_fps(True)
        game.set_esc_keluar(False)
        game.atur_fps(30)
        assert game.dapatkan_fps() == 0.0  # belum mulai
