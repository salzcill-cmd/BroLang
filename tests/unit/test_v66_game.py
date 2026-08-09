"""
Test BroLang v6.6 — Upgrade Library Game Komprehensif
======================================================

Mencakup:
1. `jalur` — pathfinding A*, IkutiJalur (follow waypoint), Patroli (3 mode)
2. `efek`  — Flash, Vignette, TeksMelayang (damage number), Pulsa
3. `fisika` — collider persegi (AABB), resolve campuran, raycast, cari_bodi_di_area
4. `partikel` — gradien warna seumur hidup, emiter trail/asap/bintang
5. `tilemap` — tile animasi, layer objek, cek_lantai
6. `kamera` — set_lerp, screen_parallax, deadzone follow
7. `game` — atur_fisika (fixed timestep), tangkap_layar, atur_ukuran_jendela
8. `grafis` — gradien, glow, perataan teks, gambar alpha
9. `ui` — Tooltip, Tombol bergambar, DaftarSkor, navigasi_fokus
10. `sprite` — ikuti_patroli, rotasi_ke_titik, tampilkan/sembunyikan
"""

import json
import os

import pytest

from brolang.interpreter import Interpreter
from brolang.lexer import Lexer
from brolang.parser import Parser
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
# 1. jalur — pathfinding & navigasi
# ============================================================


class TestJalurAstar:
    def test_cari_jalur_sederhana(self):
        jalur = _mod("jalur")
        peta = [
            [1, 1, 1, 1, 1],
            [1, 0, 0, 0, 1],
            [1, 0, 1, 0, 1],
            [1, 0, 1, 0, 1],
            [1, 1, 1, 1, 1],
        ]
        hasil = jalur.cari_jalur(peta, (1, 1), (3, 3))
        assert hasil is not None
        assert hasil[0] == (1, 1)
        assert hasil[-1] == (3, 3)
        # Semua tile di tengah jalur harus bisa dilalui
        for tx, ty in hasil[1:-1]:
            assert peta[ty][tx] == 0

    def test_tidak_ada_jalur(self):
        jalur = _mod("jalur")
        blok = [
            [0, 0, 0],
            [1, 1, 1],
            [0, 0, 0],
        ]
        assert jalur.cari_jalur(blok, (0, 0), (0, 2)) is None

    def test_mulai_sama_dengan_tujuan(self):
        jalur = _mod("jalur")
        assert jalur.cari_jalur([[0, 0], [0, 0]], (1, 1), (1, 1)) == [(1, 1)]

    def test_tile_solid_tidak_bisa_jadi_titik(self):
        jalur = _mod("jalur")
        peta = [[1, 0], [0, 0]]
        assert jalur.cari_jalur(peta, (0, 0), (1, 1)) is None

    def test_dengan_objek_tilemap(self):
        jalur = _mod("jalur")
        tilemap = _mod("tilemap")
        peta = tilemap.buat_peta(6, 6, 32)
        ts = tilemap.buat_tileset("t", 32)
        ts.atur_solid(1, True)
        peta.set_tileset(ts)
        peta.dari_array([
            [1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 1],
            [1, 0, 1, 0, 0, 1],
            [1, 0, 1, 0, 0, 1],
            [1, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1],
        ])
        hasil = jalur.cari_jalur(peta, (1, 1), (4, 4))
        assert hasil is not None and hasil[-1] == (4, 4)

    def test_jalur_ke_pixel(self):
        jalur = _mod("jalur")
        px = jalur.jalur_ke_pixel([(1, 2), (2, 2)], ukuran_tile=32, tengah=True)
        assert px == [(48.0, 80.0), (80.0, 80.0)]
        assert jalur.panjang_jalur(None) == 0
        assert jalur.panjang_jalur([(1, 1)]) == 1

    def test_diagonal_tanpa_menembus_dinding(self):
        jalur = _mod("jalur")
        peta = [
            [0, 0, 0],
            [0, 1, 0],
            [0, 0, 0],
        ]
        # Diagonal melewati pojok dinding harus diblokir
        hasil = jalur.cari_jalur(peta, (0, 0), (2, 2), diagonal=True)
        # Jalur alternatif mengitari dinding tetap tersedia
        assert hasil is not None


class TestIkutiJalur:
    def test_follow_waypoint(self):
        jalur = _mod("jalur")
        f = jalur.IkutiJalur([(0, 0), (100, 0), (100, 100)], kecepatan=300)
        for _ in range(100):
            f.update(0.1)
        assert f.posisi() == (100.0, 100.0)
        assert f.selesai

    def test_callback_on_selesai(self):
        jalur = _mod("jalur")
        f = jalur.IkutiJalur([(0, 0), (50, 0)], kecepatan=1000)
        selesai = []
        f.on_selesai = lambda: selesai.append(1)
        f.update(0.1)
        assert selesai == [1]

    def test_loop_tidak_macet(self):
        """Regresi: loop dengan posisi tepat di waypoint tidak boleh infinite."""
        jalur = _mod("jalur")
        f = jalur.IkutiJalur([(0, 0), (100, 0)], kecepatan=200, loop=True)
        for _ in range(1000):
            f.update(0.1)
        assert f.posisi() == (100.0, 0.0)

    def test_reset_dan_tambah_titik(self):
        jalur = _mod("jalur")
        f = jalur.IkutiJalur([(0, 0), (100, 0)], kecepatan=200)
        f.tambah_titik(100, 100)
        assert len(f.titik) == 3
        f.reset()
        assert f.posisi() == (0.0, 0.0)
        assert not f.selesai


class TestPatroli:
    def test_mode_loop(self):
        jalur = _mod("jalur")
        p = jalur.Patroli([(0, 0), (100, 0)], kecepatan=200)
        p.update(0.6)  # 120px: 100 ke WP1 + 20 balik
        assert p.posisi() == (80.0, 0.0)
        p.update(0.6)  # 120px: 80 balik ke 0 + 40 ke depan
        assert p.posisi() == (40.0, 0.0)

    def test_mode_bolak_balik(self):
        jalur = _mod("jalur")
        p = jalur.Patroli([(0, 0), (100, 0), (100, 100)], kecepatan=1000,
                          mode="bolak-balik")
        p.update(0.35)
        # 350px: 0→(100,0)→(100,100)→balik→(100,0)→50 ke arah (0,0)
        assert p.posisi() == (50.0, 0.0)

    def test_mode_sekali(self):
        jalur = _mod("jalur")
        p = jalur.Patroli([(0, 0), (50, 0)], kecepatan=1000, mode="sekali")
        selesai = []
        p.on_selesai = lambda: selesai.append(1)
        p.update(0.1)
        assert p.selesai
        assert p.posisi() == (50.0, 0.0)
        assert selesai == [1]
        # update setelah selesai → tidak bergerak
        p.update(0.1)
        assert p.posisi() == (50.0, 0.0)

    def test_reset(self):
        jalur = _mod("jalur")
        p = jalur.Patroli([(0, 0), (100, 0)], kecepatan=1000)
        p.update(0.2)
        p.reset()
        assert p.posisi() == (0.0, 0.0)


# ============================================================
# 2. efek
# ============================================================


class TestEfek:
    def test_flash_lifecycle(self):
        efek = _mod("efek")
        fl = efek.Flash("putih", durasi=0.2, kekuatan=200)
        assert fl.aktif()
        assert fl.alpha() == 200
        fl.update(0.1)
        assert fl.aktif()
        assert 0 < fl.alpha() < 200
        fl.update(0.2)
        assert not fl.aktif()
        assert fl.alpha() == 0

    def test_flash_picu_ulang(self):
        efek = _mod("efek")
        fl = efek.Flash("merah", durasi=0.1)
        fl.update(0.2)
        assert not fl.aktif()
        fl.picu()
        assert fl.aktif()

    def test_teks_melayang(self):
        efek = _mod("efek")
        tm = efek.TeksMelayang("-25", 100, 100, warna="merah", kecepatan_naik=50)
        y_awal = tm.y
        tm.update(0.1)
        assert tm.y < y_awal  # naik
        assert not tm.selesai()
        tm.update(2.0)
        assert tm.selesai()

    def test_pulsa_radius(self):
        efek = _mod("efek")
        pu = efek.Pulsa(0, 0, radius_akhir=80, durasi=0.5)
        pu.update(0.25)
        assert 0 < pu.radius_sekarang() < 80
        pu.update(0.5)
        assert pu.selesai()
        assert pu.radius_sekarang() == pytest.approx(80.0)

    def test_helper_buat(self):
        efek = _mod("efek")
        assert efek.buat_flash("putih", 0.1).aktif()
        assert efek.buat_pulsa(10, 10, 50, 0.3, "cyan").selesai() is False


# ============================================================
# 3. fisika — AABB, raycast, query
# ============================================================


class TestFisikaAABB:
    def test_mode_persegi(self):
        fisika = _mod("fisika")
        b = fisika.buat_bodi(100, 100, massa=1).set_persegi(40, 40)
        assert b.mode_collider == "persegi"
        assert b.lebar == 40 and b.tinggi == 40
        # set_radius kembali ke lingkaran
        b.set_radius(10)
        assert b.mode_collider == "lingkaran"

    def test_tabrakan_persegi_dan_resolve(self):
        fisika = _mod("fisika")
        w = fisika.buat_dunia(gravitasi_y=0)
        a = fisika.buat_bodi(100, 100, massa=1).set_persegi(40, 40)
        b = fisika.buat_bodi(115, 100, massa=1).set_persegi(40, 40)
        assert w.check_collision(a, b)
        w.resolve_collision(a, b)
        assert not w.check_collision(a, b)

    def test_tabrakan_campuran_lingkaran_persegi(self):
        fisika = _mod("fisika")
        w = fisika.buat_dunia(gravitasi_y=0)
        kotak = fisika.buat_bodi(100, 100, massa=1).set_persegi(40, 40)
        bola = fisika.buat_bodi(100, 100, radius=10)
        assert w.check_collision(kotak, bola)
        bola_jauh = fisika.buat_bodi(300, 300, radius=10)
        assert not w.check_collision(kotak, bola_jauh)

    def test_bounds_pakai_half_size_persegi(self):
        fisika = _mod("fisika")
        w = fisika.buat_dunia(0)
        b = fisika.buat_bodi(5, 100, massa=1).set_persegi(40, 40)
        w.check_bounds(b, 800, 600, bounce=False)
        assert b.posisi.x == 20.0  # setengah lebar

    def test_raycast_persegi(self):
        fisika = _mod("fisika")
        w = fisika.buat_dunia(0)
        target = fisika.buat_bodi(300, 100, massa=1).set_persegi(40, 40)
        w.tambah_bodi(target)
        hit = w.raycast(0, 100, 500, 100)
        assert hit is not None
        bodi, x_hit, y_hit = hit
        assert bodi is target
        assert 279 <= x_hit <= 281

    def test_raycast_lingkaran_dan_miss(self):
        fisika = _mod("fisika")
        w = fisika.buat_dunia(0)
        bola = fisika.buat_bodi(200, 200, radius=20)
        w.tambah_bodi(bola)
        hit = w.raycast(0, 200, 400, 200)
        assert hit is not None and hit[0] is bola
        assert abs(hit[1] - 180.0) < 0.01
        # Miss
        w2 = fisika.buat_dunia(0)
        w2.tambah_bodi(fisika.buat_bodi(200, 500, radius=10))
        assert w2.raycast(0, 0, 400, 0) is None

    def test_cari_bodi_di_area(self):
        fisika = _mod("fisika")
        w = fisika.buat_dunia(0)
        p1 = fisika.buat_bodi(50, 50, radius=10)
        p2 = fisika.buat_bodi(500, 500, radius=10)
        w.tambah_bodi(p1)
        w.tambah_bodi(p2)
        area = w.cari_bodi_di_area(0, 0, 100, 100)
        assert p1 in area and p2 not in area

    def test_bodi_di_posisi_persegi(self):
        fisika = _mod("fisika")
        w = fisika.buat_dunia(0)
        pr = fisika.buat_bodi(100, 100, massa=1).set_persegi(40, 40)
        w.tambah_bodi(pr)
        assert w.bodi_di_posisi(100, 100) is pr
        assert w.bodi_di_posisi(130, 100) is None


# ============================================================
# 4. partikel — gradien & emiter bantu
# ============================================================


class TestPartikelV66:
    def test_gradien_warna_seumur_hidup(self):
        partikel = _mod("partikel")
        e = partikel.PartikelEmiter(0, 0)
        e.warna_awal = (255, 0, 0)
        e.warna_akhir = (0, 0, 255)
        e.emisi_per_detik = 0
        e.ledak(0, 0, 5)
        p = e.partikel[0]
        assert p.warna_sekarang() == (255, 0, 0)
        p.umur = p.umur_max / 2
        tengah = p.warna_sekarang()
        assert tengah[0] < 255 and tengah[2] > 0
        p.umur = p.umur_max
        assert p.warna_sekarang() == (0, 0, 255)

    def test_buat_trail(self):
        partikel = _mod("partikel")
        t = partikel.buat_trail(100, 100, warna="cyan")
        t.update(0.1)
        assert t.jumlah_aktif() > 0

    def test_buat_asap(self):
        partikel = _mod("partikel")
        a = partikel.buat_asap(50, 50)
        a.update(0.1)
        assert a.jumlah_aktif() > 0
        assert a.warna_awal == (170, 170, 170)
        assert a.warna_akhir == (90, 90, 90)

    def test_buat_bintang(self):
        partikel = _mod("partikel")
        b = partikel.buat_bintang(200, 200, warna="emas")
        assert b.jumlah_aktif() == 12


# ============================================================
# 5. tilemap — animasi, objek, cek_lantai
# ============================================================


class TestTilemapV66:
    def _peta(self):
        tilemap = _mod("tilemap")
        p = tilemap.buat_peta(10, 10, 32)
        ts = tilemap.buat_tileset("t", 32)
        ts.atur_solid(1, True)
        p.set_tileset(ts)
        return p, ts

    def test_tile_animasi(self):
        p, ts = self._peta()
        ts.atur_animasi(9, [9, 10, 11], kecepatan=0.2)
        p.update(0.2)
        assert p._frame_tile(9) == 10
        p.update(0.2)
        assert p._frame_tile(9) == 11
        p.update(0.2)
        assert p._frame_tile(9) == 9

    def test_tile_tanpa_animasi_tidak_berubah(self):
        p, _ = self._peta()
        assert p._frame_tile(3) == 3

    def test_cek_lantai(self):
        p, _ = self._peta()
        p.atur(2, 5, 1)
        # Titik di tile (2,4): ada tile solid tepat di bawahnya
        assert p.cek_lantai(2 * 32 + 16, 4 * 32)
        assert not p.cek_lantai(0, 0)

    def test_layer_objek(self):
        p, _ = self._peta()
        obj = p.tambah_objek("pemain", 64, 64, tipe="spawn")
        p.tambah_objek("musuh", 300, 64, kecepatan=50)
        p.tambah_objek("musuh", 400, 64, kecepatan=80)
        assert obj.nama == "pemain" and obj.x == 64.0 and obj.tipe == "spawn"
        assert p.cari_objek("pemain") is obj
        assert len(p.cari_semua_objek("musuh")) == 2
        assert p.hapus_objek("musuh") == 2
        assert p.cari_objek("musuh") is None
        p.bersihkan_objek()
        assert len(p.objek) == 0


# ============================================================
# 6. kamera — parallax, lerp, deadzone
# ============================================================


class TestKameraV66:
    def test_set_lerp(self):
        kamera = _mod("kamera")
        cam = kamera.buat_kamera(800, 600)
        cam.set_lerp(3.0)
        assert cam.kecepatan_smooth == 3.0

    def test_parallax(self):
        kamera = _mod("kamera")
        cam = kamera.buat_kamera(800, 600)
        cam.set_posisi(100, 50)
        # faktor 0 = statis
        assert cam.screen_parallax(500, 300, 0.0) == (500.0, 300.0)
        # faktor 1 = normal
        px1, _ = cam.screen_parallax(500, 300, 1.0)
        assert px1 == pytest.approx(400.0)
        # faktor 0.5 = setengah
        px2, _ = cam.screen_parallax(500, 300, 0.5)
        assert px2 == pytest.approx(450.0)

    def test_deadzone_diam_lalu_kejar(self):
        import types

        kamera = _mod("kamera")
        target = types.SimpleNamespace(x=20.0, y=10.0)
        cam = kamera.buat_kamera(800, 600)
        cam.set_target(target, deadzone=(100, 60))
        cam.deadzone_lerp = 1000.0
        cam.update(0.1)
        assert cam.x == 0.0 and cam.y == 0.0  # target dalam deadzone
        target.x = 400.0  # keluar deadzone
        cam.update(0.5)
        assert cam.x > 300.0

    def test_follow_tanpa_deadzone_tetap_normal(self):
        import types

        kamera = _mod("kamera")
        target = types.SimpleNamespace(x=200.0, y=100.0)
        cam = kamera.buat_kamera(800, 600)
        cam.kecepatan_smooth = 10.0
        cam.set_target(target)
        cam.update(0.1)
        assert cam.x > 0.0


# ============================================================
# 7. game — fixed timestep, screenshot, resize
# ============================================================


class TestGameV66:
    @pytest.fixture(autouse=True)
    def _reset(self):
        _mod("game").reset()

    def test_atur_fisika_fixed_timestep(self):
        from brolang.stdlib.game import _state

        game = _mod("game")
        langkah = []

        def step(dt):
            langkah.append(dt)

        game.atur_fisika(step, timestep=1 / 60)
        # Simulasikan akumulasi frame 0.1s (loop game)
        _state.fisika_akumulator = 0.1
        while (_state.fisika_akumulator >= _state.fisika_timestep
               and len(langkah) < _state.fisika_maks_langkah):
            step(_state.fisika_timestep)
            _state.fisika_akumulator -= _state.fisika_timestep
        # 0.1s / (1/60) = 6 langkah tapi dibatasi maks 5 (anti spiral-of-death)
        assert len(langkah) == 5
        assert all(abs(dt - 1 / 60) < 1e-9 for dt in langkah)

    def test_tangkap_layar(self, tmp_path):
        pytest.importorskip("pygame")
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        import pygame

        pygame.init()
        pygame.display.set_mode((200, 200))
        game = _mod("game")
        path = str(tmp_path / "shot.png")
        game.tangkap_layar(path)
        assert os.path.exists(path)
        pygame.quit()

    def test_atur_ukuran_jendela(self):
        pytest.importorskip("pygame")
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        import pygame

        pygame.init()
        pygame.display.set_mode((200, 200))
        game = _mod("game")
        game.atur_ukuran_jendela(640, 480)
        assert pygame.display.get_surface().get_size() == (640, 480)
        pygame.quit()


# ============================================================
# 8. grafis — gradien & teks (butuh pygame dummy)
# ============================================================


class TestGrafisV66:
    @pytest.fixture(autouse=True)
    def _pygame(self):
        pygame = pytest.importorskip("pygame")
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        pygame.init()
        self._screen = pygame.display.set_mode((320, 240))
        yield
        pygame.quit()

    def test_gradien_tidak_crash(self):
        grafis = _mod("grafis")
        grafis.gradien_vertikal(0, 0, 100, 100, "langit", "biru_gelap")
        grafis.gradien_horizontal(0, 0, 100, 50, (255, 0, 0), (0, 0, 255))

    def test_glow_dan_alpha(self):
        grafis = _mod("grafis")
        grafis.glow_lingkaran(160, 120, 30, "emas")
        surf = grafis.buat_surface(50, 50, transparan=True)
        grafis.gambar_gambar_alpha(surf, 10, 10, 128)
        grafis.gambar_gambar_alpha(surf, 10, 60, 255)  # alpha penuh → blit langsung

    def test_tulis_teks_perataan(self):
        grafis = _mod("grafis")
        grafis.tulis_teks("X", 160, 50, tengah=True)
        grafis.tulis_teks("Y", 320, 80, kanan=True)
        grafis.tulis_teks("Z", 10, 10)  # default kiri


# ============================================================
# 9. ui — Tooltip, DaftarSkor, navigasi fokus, tombol gambar
# ============================================================


class TestTooltip:
    def test_muncul_setelah_delay(self):
        ui = _mod("ui")
        tip = ui.Tooltip("Halo", delay=0.4)
        assert not tip.update(10, 10, hover=True, dt=0.2)
        assert tip.update(10, 10, hover=True, dt=0.3)
        assert tip.aktif()

    def test_hilang_saat_tidak_hover(self):
        ui = _mod("ui")
        tip = ui.Tooltip("Halo", delay=0.1)
        tip.update(10, 10, hover=True, dt=0.2)
        assert tip.aktif()
        tip.update(10, 10, hover=False, dt=0.1)
        assert not tip.aktif()

    def test_ikut_mouse_dan_set_teks(self):
        ui = _mod("ui")
        tip = ui.Tooltip("A", delay=0)
        tip.update(50, 60, hover=True, dt=0.05)
        assert tip.x == 50 + 16 and tip.y == 60 + 22
        tip.set_teks("B")
        assert tip.teks == "B"


class TestDaftarSkor:
    def test_tambah_dan_urut(self, tmp_path):
        ui = _mod("ui")
        ds = ui.DaftarSkor(str(tmp_path / "skor.json"), maks_entri=3)
        ds.tambah("Budi", 1200)
        ds.tambah("Siti", 900)
        ds.tambah("Amin", 1500)
        assert ds.skor_tertinggi() == 1500
        assert ds.peringkat("Budi") == 1
        assert ds.tabel()[0] == ("Amin", 1500)

    def test_pemangkasan_entri(self, tmp_path):
        ui = _mod("ui")
        ds = ui.DaftarSkor(str(tmp_path / "s.json"), maks_entri=3)
        for nama, skor in [("A", 10), ("B", 20), ("C", 30), ("D", 5)]:
            ds.tambah(nama, skor)
        assert ds.jumlah() == 3
        assert ds.peringkat("D") is None

    def test_persist_ke_file(self, tmp_path):
        ui = _mod("ui")
        path = str(tmp_path / "skor.json")
        ds = ui.DaftarSkor(path)
        ds.tambah("Budi", 1200)
        ds2 = ui.DaftarSkor(path)
        assert ds2.skor_tertinggi() == 1200

    def test_bersihkan(self, tmp_path):
        ui = _mod("ui")
        ds = ui.DaftarSkor(str(tmp_path / "s.json"))
        ds.tambah("A", 10)
        ds.bersihkan()
        assert ds.jumlah() == 0


class TestNavigasiFokus:
    def test_pindah_bawah_dan_atas(self):
        ui = _mod("ui")
        k1 = ui.KotakTeks(0, 0, 100)
        k2 = ui.KotakTeks(0, 50, 100)
        k3 = ui.KotakTeks(0, 100, 100)
        k1.fokus = True
        baru = ui.navigasi_fokus(k1, "bawah", [k1, k2, k3])
        assert baru is k2
        assert k2.fokus and not k1.fokus
        assert ui.navigasi_fokus(k2, "atas", [k1, k2, k3]) is k1

    def test_putar_dan_kosong(self):
        ui = _mod("ui")
        k1 = ui.KotakTeks(0, 0, 100)
        k2 = ui.KotakTeks(0, 50, 100)
        # Dari elemen terakhir turun → putar ke pertama
        k2.fokus = True
        assert ui.navigasi_fokus(k2, "bawah", [k1, k2]) is k1
        # Komponen None → elemen pertama
        assert ui.navigasi_fokus(None, "bawah", [k1, k2]) is k1
        # Daftar kosong → kembalikan komponen
        assert ui.navigasi_fokus(k1, "bawah", []) is k1


class TestTombolGambar:
    def test_gambar_tidak_ada_fallback_tidak_crash(self):
        ui = _mod("ui")
        tb = ui.Tombol("MULAI", 10, 10, 100, 40, gambar="/tmp/ga_ada.png")
        assert tb.update(50, 30, diklik=True)
        assert tb.ditekan


# ============================================================
# 10. sprite — patroli, rotasi, visibilitas
# ============================================================


class TestSpriteV66:
    def test_ikuti_patroli(self):
        sprite = _mod("sprite")
        s = sprite.Sprite(None, 0, 0, lebar=32, tinggi=32)
        s.ikuti_patroli([(0, 0), (100, 0)], kecepatan=200)
        assert s.patroli_aktif()
        s.update(0.6)
        assert s.x == 80.0 and s.y == 0.0
        s.berhenti_patroli()
        assert not s.patroli_aktif()
        s.update(0.1)
        assert s.x == 80.0  # tidak bergerak setelah berhenti

    def test_rotasi_ke_titik(self):
        sprite = _mod("sprite")
        s = sprite.Sprite(None, 0, 0, lebar=32, tinggi=32)
        s.rotasi_ke_titik(0, 100)
        assert s.sudut == pytest.approx(90.0, abs=0.01)
        s.rotasi_ke_titik(100, 0)
        assert s.sudut == pytest.approx(0.0, abs=0.01)

    def test_tampil_dan_sembunyi(self):
        sprite = _mod("sprite")
        s = sprite.Sprite(None, 0, 0, lebar=32, tinggi=32)
        s.sembunyikan()
        assert not s.terlihat
        s.tampilkan()
        assert s.terlihat


# ============================================================
# 11. Compiler package — bro build (regresi v6.6)
# ============================================================


class TestCompilerV66:
    def _kompilasi(self, kode):
        """Kompilasi BroLang → Python via compiler package, lalu eksekusi."""
        from brolang.compiler import compile_source

        py = compile_source(kode)
        hasil = {}
        exec(compile(py, "<bro>", "exec"), {}, hasil)
        return py, hasil

    def test_tuple_destructuring_build(self):
        """Regresi: `buat (x, y) = ...` sekarang berfungsi di bro build."""
        _, hasil = self._kompilasi(
            "buat (x, y) = (30, 40)\nz = x + y\n"
        )
        assert hasil["z"] == 70

    def test_array_destructuring_build(self):
        _, hasil = self._kompilasi(
            "buat [a, b] = [5, 7]\nc = a * b\n"
        )
        assert hasil["c"] == 35

    def test_tuple_dan_set_literal_build(self):
        """Regresi bug lama: visit_TupleNode/SetNode memanggil _emit_line yang
        tidak ada sehingga bro build gagal untuk tuple/set literal."""
        _, hasil = self._kompilasi(
            "buat t = (1, 2, 3)\na = t[0]\nbuat s = {1, 2, 3}\nb = len(s)\n"
        )
        assert hasil["a"] == 1
        assert hasil["b"] == 3

    def test_tulis_hasil_build(self):
        """tulis tetap berfungsi di hasil kompilasi."""
        py, _ = self._kompilasi("tulis \"halo v6.6\"\n")
        assert "print" in py


# ============================================================
# Integrasi dari kode BroLang
# ============================================================


class TestIntegrasiV66:
    def test_jalur_dari_brolang(self):
        out = _jalankan("""
impor jalur
buat denah = [[1, 1, 1, 1], [1, 0, 0, 1], [1, 0, 0, 1], [1, 1, 1, 1]]
buat rute = jalur.cari_jalur(denah, (1, 1), (2, 2))
tulis jalur.panjang_jalur(rute)
tulis jalur.jalur_ke_pixel(rute, 32)
""")
        assert out[0] == "3"  # (1,1) -> (1,2) -> (2,2)
        assert "(48.0" in out[1]  # koordinat pixel pusat tile

    def test_patroli_dari_brolang(self):
        out = _jalankan("""
impor jalur
buat penjaga = jalur.Patroli([(0, 0), (100, 0)], kecepatan=200)
penjaga.update(0.5)
buat [gx, gy] = penjaga.posisi()
tulis gx
tulis gy
""")
        assert out == ["100.0", "0.0"]

    def test_destructuring_tuple_dari_brolang(self):
        """Regresi doc: `buat (x, y) = ...` yang dipromosikan docs/GAME.md
        sekarang benar-benar berfungsi (v6.6)."""
        out = _jalankan("""
impor jalur
buat penjaga = jalur.Patroli([(0, 0), (100, 0)], kecepatan=200)
penjaga.update(0.5)
buat (gx, gy) = penjaga.posisi()
tulis gx + gy
""")
        assert out == ["100.0"]

    def test_efek_dan_kamera_dari_brolang(self):
        out = _jalankan("""
impor efek
buat kilat = efek.buat_flash("putih", durasi=0.1)
kilat.update(0.05)
jika kilat.aktif() maka
    tulis "nyala"
lainnya
    tulis "mati"
selesai

impor kamera
buat cam = kamera.buat_kamera(800, 600)
cam.set_posisi(100, 0)
buat (sx, sy) = cam.screen_parallax(300, 200, 0.5)
tulis sx
""")
        assert out == ["nyala", "250.0"]

    def test_ui_dan_sprite_dari_brolang(self):
        out = _jalankan("""
impor ui
buat skor = ui.DaftarSkor("/tmp/bro_v66_test_skor.json", maks_entri=5)
skor.tambah("Budi", 1200)
tulis skor.skor_tertinggi()

impor sprite
buat pemain = sprite.Sprite(kosong, 0, 0, lebar=32, tinggi=32)
pemain.sembunyikan()
tulis pemain.terlihat
""")
        assert out == ["1200", "False"]

    def test_tilemap_objek_dari_brolang(self):
        out = _jalankan("""
impor tilemap
buat p = tilemap.buat_peta(5, 5, 32)
buat o = p.tambah_objek("pemain", 64, 64, tipe="spawn")
tulis o.nama
tulis p.cari_objek("pemain").tipe
""")
        assert out == ["pemain", "spawn"]
