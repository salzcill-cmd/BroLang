"""
Unit tests: BroLang v6.2 — game dev upgrade.

Mencakup:
- game    : scene lifecycle (on_masuk/on_keluar), transisi fade antar scene,
            tumpukan scene (overlay) via dorong_scene/pop_scene
- ui      : komponen baru — KotakTeks (input teks), Slider, KotakCentang,
            DaftarPilih (dropdown)
"""

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
# game: scene lifecycle
# ============================================================


class TestSceneLifecycle:
    def test_on_masuk_dan_on_keluar(self):
        """on_masuk dipanggil saat scene aktif, on_keluar saat diganti."""
        game = _mod("game")
        game.reset()
        riwayat = []

        def masuk_menu():
            riwayat.append("masuk:menu")

        def keluar_menu():
            riwayat.append("keluar:menu")

        def masuk_main():
            riwayat.append("masuk:main")

        game.tambah_scene("menu", on_masuk=masuk_menu, on_keluar=keluar_menu)
        game.tambah_scene("main", on_masuk=masuk_main)
        game.ganti_scene("menu")
        assert riwayat == ["masuk:menu"]
        game.ganti_scene("main")
        assert riwayat == ["masuk:menu", "keluar:menu", "masuk:main"]

    def test_on_keluar_tidak_dipanggil_sebelum_scene_pertama(self):
        game = _mod("game")
        game.reset()
        keluar = []
        game.tambah_scene("a", on_keluar=lambda: keluar.append(1))
        game.ganti_scene("a")
        assert keluar == []

    def test_ganti_scene_tanpa_transisi_langsung(self):
        game = _mod("game")
        game.reset()
        game.tambah_scene("a")
        game.tambah_scene("b")
        game.ganti_scene("a", transisi=None)
        assert game.dapatkan_scene_sekarang() == "a"
        assert not game.transisi_aktif()

    def test_ganti_scene_error_tidak_ditemukan(self):
        game = _mod("game")
        game.reset()
        with pytest.raises(ValueError):
            game.ganti_scene("gaada")


# ============================================================
# game: transisi fade
# ============================================================


class TestTransisi:
    def test_transisi_fade_mengganti_scene_di_tengah(self):
        """Saat fade setengah jalan (paling gelap), scene harus sudah berganti."""
        game = _mod("game")
        game.reset()
        game.tambah_scene("a")
        game.tambah_scene("b")
        game.ganti_scene("a")
        game.ganti_scene("b", transisi="fade", durasi=1.0)
        # Masih scene lama di awal transisi
        assert game.dapatkan_scene_sekarang() == "a"
        assert game.transisi_aktif()
        # Update 0.6s (> 0.5 setengah durasi) → scene berganti di titik gelap
        game._update_transisi(0.6)
        assert game.dapatkan_scene_sekarang() == "b"
        assert game.transisi_aktif()
        # Lanjut sampai selesai
        game._update_transisi(0.6)
        assert not game.transisi_aktif()
        assert game.dapatkan_scene_sekarang() == "b"

    def test_alpha_transisi_naik_lalu_turun(self):
        game = _mod("game")
        game.reset()
        game.tambah_scene("a")
        game.tambah_scene("b")
        game.ganti_scene("a")
        game.ganti_scene("b", transisi="fade", durasi=2.0)
        # Fase gelap: alpha naik ke 255
        game._update_transisi(0.5)  # waktu 0.5, setengah durasi = 1.0
        a1 = game._alpha_transisi()
        assert 0 < a1 < 255
        game._update_transisi(0.6)  # lewat setengah → ganti scene, alpha puncak
        assert game._alpha_transisi() == 255
        # Fase terang: alpha turun
        game._update_transisi(0.5)
        a2 = game._alpha_transisi()
        assert a2 < 255
        game._update_transisi(1.0)
        assert not game.transisi_aktif()

    def test_transisi_warna_kustom(self):
        from brolang.stdlib import game as game_mod

        game = _mod("game")
        game.reset()
        game.tambah_scene("a")
        game.tambah_scene("b")
        game.ganti_scene("a")
        game.ganti_scene("b", transisi="fade", durasi=1.0, warna="putih")
        assert game_mod._state.transisi["warna"] == "putih"

    def test_progres_transisi(self):
        game = _mod("game")
        game.reset()
        game.tambah_scene("a")
        game.tambah_scene("b")
        game.ganti_scene("a")
        assert game.progres_transisi() == 1.0  # tidak ada transisi
        game.ganti_scene("b", transisi="fade", durasi=2.0)
        game._update_transisi(1.0)
        assert 0 < game.progres_transisi() <= 1.0

    def test_ganti_scene_langsung_tetap_jalan_setelah_transisi(self):
        """Setelah transisi selesai, ganti scene biasa (tanpa transisi) tetap normal."""
        game = _mod("game")
        game.reset()
        game.tambah_scene("a")
        game.tambah_scene("b")
        game.ganti_scene("a")
        game.ganti_scene("b", transisi="fade", durasi=1.0)
        game._update_transisi(0.6)
        game._update_transisi(0.6)
        game.ganti_scene("a")
        assert game.dapatkan_scene_sekarang() == "a"
        assert not game.transisi_aktif()

    def test_ganti_langsung_saat_transisi_aktif_membatalkan_transisi(self):
        """Bug review: ganti_scene langsung saat transisi berjalan harus
        membatalkan transisi agar tidak ada switch tertunda yang menimpa scene."""
        game = _mod("game")
        game.reset()
        game.tambah_scene("a")
        game.tambah_scene("b")
        game.tambah_scene("c")
        game.ganti_scene("a")
        game.ganti_scene("b", transisi="fade", durasi=4.0)  # transisi panjang
        assert game.transisi_aktif()
        # Ganti langsung ke c di tengah transisi
        game.ganti_scene("c")
        assert game.dapatkan_scene_sekarang() == "c"
        assert not game.transisi_aktif()
        # Lanjutkan waktu — tidak boleh ada switch ke 'b'
        game._update_transisi(2.0)
        assert game.dapatkan_scene_sekarang() == "c"

    def test_transisi_baru_saat_transisi_aktif_menyelesaikan_yang_lama(self):
        """Transisi baru saat transisi lama berjalan: scene tujuan lama
        diterapkan dulu, lalu transisi baru berjalan normal."""
        game = _mod("game")
        game.reset()
        riwayat = []

        def masuk(nama):
            return lambda: riwayat.append(f"masuk:{nama}")

        def keluar(nama):
            return lambda: riwayat.append(f"keluar:{nama}")

        game.tambah_scene("a", on_masuk=masuk("a"), on_keluar=keluar("a"))
        game.tambah_scene("b", on_masuk=masuk("b"), on_keluar=keluar("b"))
        game.tambah_scene("c", on_masuk=masuk("c"), on_keluar=keluar("c"))
        game.ganti_scene("a")
        game.ganti_scene("b", transisi="fade", durasi=4.0)
        # Transisi baru ke c saat transisi ke b masih berjalan
        game.ganti_scene("c", transisi="fade", durasi=1.0)
        # Transisi lama ke 'b' harus diselesaikan dulu (masuk b), lalu
        # transisi baru ke 'c' berjalan dari scene 'b'.
        assert riwayat == ["masuk:a", "keluar:a", "masuk:b"]
        assert game.dapatkan_scene_sekarang() == "b"
        assert game.transisi_aktif()
        game._update_transisi(0.6)  # lewat setengah durasi transisi c
        assert game.dapatkan_scene_sekarang() == "c"
        game._update_transisi(0.6)
        assert not game.transisi_aktif()

    def test_jenis_transisi_tidak_dikenal_jadi_langsung(self):
        """transisi tak dikenal (mis. "iris") tidak boleh dianggap fade —
        ganti scene langsung."""
        game = _mod("game")
        game.reset()
        game.tambah_scene("a")
        game.tambah_scene("b")
        game.ganti_scene("a")
        game.ganti_scene("b", transisi="iris", durasi=1.0)
        assert game.dapatkan_scene_sekarang() == "b"
        assert not game.transisi_aktif()


# ============================================================
# game: tumpukan scene (overlay)
# ============================================================


class TestSceneStack:
    def test_dorong_dan_pop(self):
        game = _mod("game")
        game.reset()
        game.tambah_scene("utama")
        game.tambah_scene("pause")
        game.ganti_scene("utama")
        game.dorong_scene("pause")
        assert game.dapatkan_scene_sekarang() == "pause"
        assert game.kedalaman_tumpukan() == 1
        game.pop_scene()
        assert game.dapatkan_scene_sekarang() == "utama"
        assert game.kedalaman_tumpukan() == 0

    def test_pop_kosong_error(self):
        game = _mod("game")
        game.reset()
        with pytest.raises(ValueError):
            game.pop_scene()

    def test_dorong_tumpukan_berlapis(self):
        game = _mod("game")
        game.reset()
        game.tambah_scene("a")
        game.tambah_scene("b")
        game.tambah_scene("c")
        game.ganti_scene("a")
        game.dorong_scene("b")
        game.dorong_scene("c")
        assert game.kedalaman_tumpukan() == 2
        game.pop_scene()
        assert game.dapatkan_scene_sekarang() == "b"
        game.pop_scene()
        assert game.dapatkan_scene_sekarang() == "a"
        assert game.kedalaman_tumpukan() == 0

    def test_reset_membersihkan_tumpukan_dan_transisi(self):
        game = _mod("game")
        game.reset()
        game.tambah_scene("a")
        game.tambah_scene("b")
        game.ganti_scene("a")
        game.dorong_scene("b", transisi="fade", durasi=1.0)
        assert game.transisi_aktif()
        game.reset()
        assert game.kedalaman_tumpukan() == 0
        assert not game.transisi_aktif()
        assert game.dapatkan_scene_sekarang() is None

    def test_scene_bawah_tetap_digambar_saat_overlay(self):
        """Scene di tumpukan harus tetap di-gambar (di bawah scene aktif)."""
        pygame = pytest.importorskip("pygame")
        os = pytest.importorskip("os")
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        from brolang.stdlib import game as game_mod

        game = _mod("game")
        game.reset()
        gambar_utama = []
        gambar_pause = []

        def g_utama(s):
            gambar_utama.append(1)

        def g_pause(s):
            gambar_pause.append(1)

        game.buat_jendela(200, 200, "Test")
        game.tambah_scene("utama", fungsi_gambar=g_utama)
        game.tambah_scene("pause", fungsi_gambar=g_pause)
        game.ganti_scene("utama")
        game.dorong_scene("pause")
        screen = pygame.display.get_surface()
        screen.fill((0, 0, 0))
        # Simulasikan bagian gambar dari game loop
        for nama in list(game_mod._state.scene_stack):
            sc = game_mod._state.scenes.get(nama)
            if sc and sc["gambar"]:
                sc["gambar"](screen)
        sc = game_mod._state.scenes.get(game_mod._state.current_scene)
        if sc and sc["gambar"]:
            sc["gambar"](screen)
        assert len(gambar_utama) == 1
        assert len(gambar_pause) == 1
        pygame.quit()


# ============================================================
# ui: KotakTeks
# ============================================================


class TestKotakTeks:
    def test_tambah_dan_hapus_karakter(self):
        ui = _mod("ui")
        kotak = ui.KotakTeks(100, 100, 200, 40)
        kotak.fokus_set(True)
        kotak.tambah_karakter("B")
        kotak.tambah_karakter("u")
        kotak.tambah_karakter("d")
        assert kotak.teks_sekarang() == "Bud"
        kotak.hapus_karakter()
        assert kotak.teks_sekarang() == "Bu"

    def test_tidak_mengetik_tanpa_fokus(self):
        ui = _mod("ui")
        kotak = ui.KotakTeks(100, 100, 200, 40)
        kotak.tambah_karakter("X")
        assert kotak.teks_sekarang() == ""

    def test_fokus_via_klik(self):
        ui = _mod("ui")
        kotak = ui.KotakTeks(100, 100, 200, 40)
        assert kotak.update(150, 120, diklik=True) is True
        assert kotak.fokus is True
        # Klik di luar → fokus hilang
        kotak.update(500, 500, diklik=True)
        assert kotak.fokus is False

    def test_placeholder_dan_set_teks(self):
        ui = _mod("ui")
        kotak = ui.KotakTeks(100, 100, 200, 40, placeholder="Nama")
        assert kotak.placeholder == "Nama"
        kotak.set_teks("Ani")
        assert kotak.teks_sekarang() == "Ani"
        kotak.kosongkan()
        assert kotak.habis()
        assert kotak.apakah_kosong()

    def test_maks_karakter(self):
        ui = _mod("ui")
        kotak = ui.KotakTeks(100, 100, 200, 40, maks_karakter=3)
        kotak.fokus_set(True)
        for ch in "abcdef":
            kotak.tambah_karakter(ch)
        assert kotak.teks_sekarang() == "abc"

    def test_callback_on_ubah(self):
        ui = _mod("ui")
        kotak = ui.KotakTeks(100, 100, 200, 40)
        calls = []
        kotak.on_ubah = lambda: calls.append(1)
        kotak.fokus_set(True)
        kotak.tambah_karakter("A")
        kotak.hapus_karakter()
        assert len(calls) == 2

    def test_enter_callback(self):
        """enter() memanggil on_enter hanya saat fokus."""
        ui = _mod("ui")
        kotak = ui.KotakTeks(100, 100, 200, 40)
        enter = []
        kotak.on_enter = lambda: enter.append(1)
        kotak.enter()  # tidak fokus → tidak dipanggil
        assert enter == []
        kotak.fokus_set(True)
        kotak.enter()
        assert enter == [1]


# ============================================================
# ui: Slider
# ============================================================


class TestSlider:
    def test_nilai_awal_dan_clamp(self):
        ui = _mod("ui")
        s = ui.Slider(100, 100, 200, nilai=50, min=0, maks=100)
        assert s.nilai_sekarang() == 50
        s.atur_nilai(500)
        assert s.nilai_sekarang() == 100
        s.atur_nilai(-50)
        assert s.nilai_sekarang() == 0

    def test_drag_mouse(self):
        ui = _mod("ui")
        s = ui.Slider(100, 100, 200, nilai=0, min=0, maks=100)
        # Tekan di tengah track → nilai setengah (karena handle ikut posisi mouse)
        s.update(200, 100, ditekan=True)
        assert s.nilai_sekarang() == pytest.approx(50, abs=1)
        # Geser ke kanan
        s.update(300, 100, ditekan=True)
        assert s.nilai_sekarang() == pytest.approx(100, abs=1)
        # Lepas → drag selesai
        s.update(300, 100, ditekan=False)
        assert s._drag is False

    def test_persen(self):
        ui = _mod("ui")
        s = ui.Slider(100, 100, 200, nilai=25, min=0, maks=100)
        assert s.persen() == pytest.approx(0.25)
        s.atur_nilai(75)
        assert s.persen() == pytest.approx(0.75)

    def test_langkah(self):
        ui = _mod("ui")
        s = ui.Slider(100, 100, 200, nilai=0, min=0, maks=100, langkah=10)
        s.atur_nilai(37)
        assert s.nilai_sekarang() == pytest.approx(40)

    def test_callback_on_ubah(self):
        ui = _mod("ui")
        s = ui.Slider(100, 100, 200, nilai=0, min=0, maks=100)
        calls = []
        s.on_ubah = lambda: calls.append(1)
        s.atur_nilai(10)
        s.atur_nilai(10)  # nilai sama → tidak boleh callback lagi
        assert len(calls) == 1


# ============================================================
# ui: KotakCentang
# ============================================================


class TestKotakCentang:
    def test_toggle_via_klik(self):
        ui = _mod("ui")
        cb = ui.KotakCentang(100, 100, label="Musik", dicentang=False)
        hasil = cb.update(110, 110, diklik=True)
        assert hasil is True
        assert cb.dicentang_sekarang()
        hasil = cb.update(110, 110, diklik=True)
        assert hasil is False
        assert not cb.dicentang_sekarang()

    def test_centang_dan_hapus(self):
        ui = _mod("ui")
        cb = ui.KotakCentang(100, 100)
        cb.centang()
        assert cb.dicentang_sekarang()
        cb.hapus_centang()
        assert not cb.dicentang_sekarang()
        cb.toggle()
        assert cb.dicentang_sekarang()

    def test_callback_peristiwa(self):
        ui = _mod("ui")
        cb = ui.KotakCentang(100, 100)
        centang = []
        hapus = []
        ubah = []
        cb.on_centang = lambda: centang.append(1)
        cb.on_hapus = lambda: hapus.append(1)
        cb.on_ubah = lambda: ubah.append(1)
        cb.centang()
        cb.hapus_centang()
        assert centang == [1] and hapus == [1] and len(ubah) == 2

    def test_klik_di_luar_tidak_mengubah(self):
        ui = _mod("ui")
        cb = ui.KotakCentang(100, 100, dicentang=True)
        cb.update(500, 500, diklik=True)
        assert cb.dicentang_sekarang()


# ============================================================
# ui: DaftarPilih (dropdown)
# ============================================================


class TestDaftarPilih:
    def test_pilihan_awal(self):
        ui = _mod("ui")
        dp = ui.DaftarPilih(100, 100, 200, opsi=["Mudah", "Sedang", "Sulit"], terpilih=1)
        assert dp.opsi_terpilih() == "Sedang"
        assert dp.indeks_terpilih() == 1
        assert dp.jumlah_opsi() == 3

    def test_buka_pilih_dan_tutup(self):
        ui = _mod("ui")
        dp = ui.DaftarPilih(100, 100, 200, opsi=["A", "B", "C"], terpilih=0)
        # Klik kotak → terbuka
        dp.update(150, 115, diklik=True)
        assert dp.terbuka
        # Klik item kedua (y di bawah kotak utama: baris 2 = y + tinggi*(1+1))
        dp.update(150, 100 + 32 * 2, diklik=True)
        assert dp.indeks_terpilih() == 1
        assert not dp.terbuka  # otomatis tertutup setelah pilih

    def test_buka_tutup_manual(self):
        ui = _mod("ui")
        dp = ui.DaftarPilih(100, 100, 200, opsi=["A", "B"])
        dp.buka()
        assert dp.terbuka
        dp.tutup()
        assert not dp.terbuka

    def test_pilih_index_di_luar_rentang_aman(self):
        ui = _mod("ui")
        dp = ui.DaftarPilih(100, 100, 200, opsi=["A", "B"], terpilih=0)
        dp.pilih(99)
        assert dp.indeks_terpilih() == 0
        dp.pilih(1)
        assert dp.indeks_terpilih() == 1

    def test_callback_on_ubah(self):
        ui = _mod("ui")
        dp = ui.DaftarPilih(100, 100, 200, opsi=["A", "B", "C"], terpilih=0)
        calls = []
        dp.on_ubah = lambda: calls.append(1)
        dp.update(150, 115, diklik=True)  # buka
        dp.update(150, 100 + 32 * 2, diklik=True)  # pilih item 2
        assert calls == [1]

    def test_pilih_index_sama_tidak_fire_callback(self):
        """pilih(index) dengan index yang sama tidak boleh memicu on_ubah."""
        ui = _mod("ui")
        dp = ui.DaftarPilih(100, 100, 200, opsi=["A", "B"], terpilih=1)
        calls = []
        dp.on_ubah = lambda: calls.append(1)
        dp.pilih(1)  # sama → tidak ada callback
        assert calls == []
        dp.pilih(0)  # berubah → callback
        assert calls == [1]


# ============================================================
# integrasi: interpreter BroLang
# ============================================================


class TestIntegrasiV62:
    def test_kotak_teks_dari_brolang(self):
        out = _jalankan("""
impor ui
buat nama = ui.KotakTeks(200, 150, 250, 40, placeholder="Nama")
nama.fokus_set(benar)
nama.tambah_karakter("B")
nama.tambah_karakter("u")
jika nama.teks_sekarang() == "Bu" maka
    tulis "ok"
lainnya
    tulis "gagal"
selesai
""")
        assert out == ["ok"]

    def test_slider_dan_centang_dari_brolang(self):
        out = _jalankan("""
impor ui
buat vol = ui.Slider(200, 300, 250, nilai=50, min=0, maks=100)
vol.atur_nilai(80)
buat cb = ui.KotakCentang(100, 100, label="Musik", dicentang=salah)
cb.centang()
tulis vol.nilai_sekarang()
tulis cb.dicentang_sekarang()
""")
        assert out == ["80.0", "True"]

    def test_daftar_pilih_dari_brolang(self):
        out = _jalankan("""
impor ui
buat dp = ui.DaftarPilih(100, 100, 200, opsi=["Mudah", "Sedang", "Sulit"], terpilih=0)
dp.pilih(2)
tulis dp.opsi_terpilih()
""")
        assert out == ["Sulit"]

    def test_scene_lifecycle_dari_brolang(self):
        out = _jalankan("""
impor game
game.reset()
buat riwayat = []
fungsi masuk_main()
    riwayat.tambah("masuk")
selesai
fungsi keluar_main()
    riwayat.tambah("keluar")
selesai
game.tambah_scene("main", on_masuk=masuk_main, on_keluar=keluar_main)
game.ganti_scene("main")
game.ganti_scene("main")
tulis riwayat
""")
        # masuk sekali, lalu keluar+masuk lagi
        assert out == ["['masuk', 'keluar', 'masuk']"]
