"""
Test BroLang v8.1 — Upgrade Game Development 🎮
================================================

Fitur baru:
1. `kumpulan_objek` — object pooling (reuse objek, hindari lag GC)
2. `simpan_game`  — save/load progres game (slot, checkpoint, metadata)
3. `dialog`       — kotak dialog dengan efek mesin ketik & pilihan bercabang
4. `ai`           — FSM (state machine) + steering behaviors (kejar/lari/tiba/jelajah)
5. `tilemap`      — platform satu arah & platform bergerak
6. `misi`         — quest & achievement (progres, status, simpan/muat)
"""

import os

import pytest

from brolang.stdlib import get_stdlib_module


def _mod(nama):
    return get_stdlib_module(nama)


# ============================================================
# 1. kumpulan_objek — object pooling
# ============================================================


class TestKumpulanObjek:
    def test_ambil_dan_kembalikan(self):
        ko = _mod("kumpulan_objek")
        pool = ko.KumpulanObjek(lambda: {"aktif": False}, ukuran_awal=3)
        assert pool.jumlah_tersedia() == 3
        obj = pool.ambil()
        assert pool.jumlah_aktif() == 1
        assert pool.jumlah_tersedia() == 2
        pool.kembalikan(obj)
        assert pool.jumlah_aktif() == 0
        assert pool.jumlah_tersedia() == 3

    def test_reuse_objek_yang_sama(self):
        ko = _mod("kumpulan_objek")
        dibuat = []
        pool = ko.KumpulanObjek(lambda: dibuat.append(1) or {"n": len(dibuat)})
        a = pool.ambil()
        b = pool.ambil()
        pool.kembalikan(a)
        c = pool.ambil()
        # c harus MENGAMBIL ULANG objek a (bukan membuat baru)
        assert c is a
        assert len(dibuat) == 2

    def test_callback_aktifkan_nonaktifkan(self):
        ko = _mod("kumpulan_objek")
        pool = ko.KumpulanObjek(
            lambda: {"aktif": False},
            ukuran_awal=2,
            aktifkan=lambda o, x=0: o.update({"aktif": True, "x": x}),
            nonaktifkan=lambda o: o.update({"aktif": False}),
        )
        obj = pool.ambil(42)
        assert obj["aktif"] is True and obj["x"] == 42
        pool.kembalikan(obj)
        assert obj["aktif"] is False

    def test_kosongkan_kembalikan_semua(self):
        ko = _mod("kumpulan_objek")
        pool = ko.KumpulanObjek(lambda: {"aktif": False}, ukuran_awal=2)
        a = pool.ambil()
        b = pool.ambil()
        assert pool.jumlah_aktif() == 2
        pool.kosongkan()
        assert pool.jumlah_aktif() == 0
        assert pool.jumlah_tersedia() == 2

    def test_buat_pool_flag(self):
        ko = _mod("kumpulan_objek")
        pool = ko.buat_pool_flag(4)
        assert pool.total() == 4
        obj = pool.ambil()
        assert obj["aktif"] is False
        pool.kembalikan(obj)

    def test_dari_kode_brolang(self):
        from brolang.interpreter import Interpreter
        from brolang.lexer import Lexer
        from brolang.parser import Parser

        kode = ('impor kumpulan_objek\n'
                'buat pool = kumpulan_objek.KumpulanObjek(lalu() {"aktif": salah}, ukuran_awal=2)\n'
                'buat p = pool.ambil()\n'
                'p["aktif"] = benar\n'
                'tulis teks(pool.jumlah_aktif())\n'
                'tulis teks(p["aktif"])\n')
        ast = Parser(Lexer(kode).tokenize()).parse()
        interp = Interpreter()
        interp.interpret(ast)
        assert interp.output == ["1", "True"]


# ============================================================
# 2. simpan_game — save/load progres
# ============================================================


class TestSimpanGame:
    def test_simpan_muat_roundtrip(self, tmp_path):
        sg = _mod("simpan_game")
        data = {"level": 3, "nyawa": 5, "kunci": ["emas", "perak"], "posisi": (10, 20)}
        folder = str(tmp_path)
        path = sg.simpan("slot1", data, folder=folder, label="Level 3")
        assert os.path.exists(path)
        muat = sg.muat("slot1", folder=folder)
        assert muat["level"] == 3
        assert muat["kunci"] == ["emas", "perak"]
        assert muat["posisi"] == [10, 20]  # tuple -> list (JSON)

    def test_muat_default_bila_tak_ada(self, tmp_path):
        sg = _mod("simpan_game")
        assert sg.muat("kosong", default={"level": 1}, folder=str(tmp_path)) == {"level": 1}

    def test_ada_dan_hapus(self, tmp_path):
        sg = _mod("simpan_game")
        folder = str(tmp_path)
        sg.simpan("a", {"x": 1}, folder=folder)
        assert sg.ada("a", folder=folder)
        assert sg.hapus("a", folder=folder) is True
        assert not sg.ada("a", folder=folder)

    def test_checkpoint(self, tmp_path):
        sg = _mod("simpan_game")
        folder = str(tmp_path)
        sg.checkpoint({"level": 4, "posisi": [100, 200]}, folder=folder)
        assert sg.muat_checkpoint(folder=folder) == {"level": 4, "posisi": [100, 200]}

    def test_daftar_terbaru_dulu(self, tmp_path):
        sg = _mod("simpan_game")
        folder = str(tmp_path)
        sg.simpan("lama", {"x": 1}, folder=folder, label="Lama")
        sg.simpan("baru", {"x": 2}, folder=folder, label="Baru")
        daftar = sg.daftar(folder=folder)
        assert len(daftar) == 2
        assert daftar[0]["nama"] == "baru"  # terbaru dulu
        assert daftar[0]["label"] == "Baru"

    def test_info_metadata(self, tmp_path):
        sg = _mod("simpan_game")
        folder = str(tmp_path)
        sg.simpan("s", {"x": 1}, folder=folder, label="Lv3", versi=2)
        info = sg.info("s", folder=folder)
        assert info is not None
        assert info["label"] == "Lv3"
        assert info["versi"] == 2
        assert info["waktu"] > 0
        assert sg.info("tidak_ada", folder=folder) is None

    def test_bersihkan(self, tmp_path):
        sg = _mod("simpan_game")
        folder = str(tmp_path)
        sg.simpan("a", {"x": 1}, folder=folder)
        sg.simpan("b", {"x": 2}, folder=folder)
        assert sg.bersihkan(folder=folder) == 2
        assert sg.daftar(folder=folder) == []


# ============================================================
# 3. dialog — efek mesin ketik & pilihan bercabang
# ============================================================


class TestDialog:
    def test_mesin_ketik(self):
        dl = _mod("dialog")
        d = dl.Dialog(["Halo dunia!"], kecepatan=10)  # 10 karakter/detik
        d.update(0.3)
        assert d.teks_terlihat() == "Hal"          # 3 karakter
        assert not d.selesai_mengetik()
        d.update(1.0)
        assert d.selesai_mengetik()
        assert d.teks_terlihat() == "Halo dunia!"

    def test_lanjut_ke_baris_berikutnya(self):
        dl = _mod("dialog")
        d = dl.Dialog(["Baris 1", "Baris 2"], kecepatan=100)
        d.tampilkan_semua()          # baris 1 penuh
        assert d.indeks_baris() == 0
        d.lanjut()                   # ke baris 2
        assert d.indeks_baris() == 1
        d.tampilkan_semua()
        assert not d.selesai()
        d.lanjut()                   # habis
        assert d.selesai()

    def test_lanjut_selesaikan_ketik_dulu(self):
        dl = _mod("dialog")
        d = dl.Dialog(["Panjang sekali teks ini"], kecepatan=5)
        d.update(0.1)                # baru 0 karakter (0.5 dibulatkan)
        assert not d.selesai_mengetik()
        d.lanjut()                   # selesaikan baris, TIDAK maju
        assert d.selesai_mengetik()
        assert d.indeks_baris() == 0

    def test_pilihan_bercabang(self):
        dl = _mod("dialog")
        d = dl.Dialog(["Apa yang kamu cari?"])
        d.atur_pilihan(["Tempa", "Belanja", "Keluar"])
        assert d.pilihan_sekarang() == ["Tempa", "Belanja", "Keluar"]
        # lanjut() tidak maju saat ada pilihan
        d.lanjut()
        assert d.indeks_baris() == 0
        teks, selesai = d.pilih(1)
        assert teks == "Belanja"
        assert selesai is True
        assert d.pilihan_terpilih() == "Belanja"

    def test_geser_pilihan(self):
        dl = _mod("dialog")
        d = dl.Dialog(["Pilih"])
        d.atur_pilihan(["A", "B", "C"])
        d.geser_pilihan(1)
        assert d.indeks_pilihan() == 1
        d.geser_pilihan(1)
        assert d.indeks_pilihan() == 2
        d.geser_pilihan(1)           # membungkus
        assert d.indeks_pilihan() == 0

    def test_callback_on_selesai(self):
        dl = _mod("dialog")
        d = dl.Dialog(["Satu baris"])
        hasil = []
        d.on_selesai(lambda: hasil.append("selesai"))
        d.tampilkan_semua()
        d.lanjut()
        assert hasil == ["selesai"]

    def test_reset(self):
        dl = _mod("dialog")
        d = dl.Dialog(["A", "B"])
        d.tampilkan_semua()
        d.lanjut()
        d.tampilkan_semua()
        d.lanjut()
        assert d.selesai()
        d.reset()
        assert not d.selesai()
        assert d.indeks_baris() == 0

    def test_nama_pembicara(self):
        dl = _mod("dialog")
        d = dl.Dialog(["Halo"], nama_pembicara="Kades")
        assert d.nama_pembicara == "Kades"


# ============================================================
# 4. ai — FSM & steering behaviors
# ============================================================


class TestAI:
    def test_fsm_ganti_status(self):
        ai = _mod("ai")
        urutan = []
        mesin = ai.FSM("jaga")
        mesin.tambah_status("jaga", update=lambda dt: urutan.append("u-jaga"),
                            keluar=lambda: urutan.append("k-jaga"))
        mesin.tambah_status("kejar", masuk=lambda: urutan.append("m-kejar"))
        mesin.update(0.016)
        assert mesin.ganti_status("kejar") is True
        assert mesin.status_sekarang() == "kejar"
        assert mesin.status_sebelumnya() == "jaga"
        assert urutan == ["u-jaga", "k-jaga", "m-kejar"]

    def test_fsm_status_tidak_dikenal(self):
        ai = _mod("ai")
        mesin = ai.FSM("a")
        assert mesin.ganti_status("tidak_ada") is False
        assert mesin.status_sekarang() == "a"

    def test_fsm_sudah_di_dan_waktu(self):
        ai = _mod("ai")
        mesin = ai.FSM("diam")
        mesin.update(0.5)
        mesin.update(0.5)
        assert mesin.sudah_di("diam")
        assert abs(mesin.waktu_di_status() - 1.0) < 0.001

    def test_kejar(self):
        ai = _mod("ai")
        vx, vy = ai.kejar(0, 0, 100, 0, 50)
        assert abs(vx - 50) < 0.001
        assert abs(vy) < 0.001

    def test_lari(self):
        ai = _mod("ai")
        vx, vy = ai.lari(0, 0, 100, 0, 50)
        assert abs(vx + 50) < 0.001
        assert abs(vy) < 0.001

    def test_tiba_berhenti_di_radius(self):
        ai = _mod("ai")
        vx, vy = ai.tiba(0, 0, 10, 0, 50, radius=16)
        assert vx == 0 and vy == 0

    def test_jelajah(self):
        ai = _mod("ai")
        vx, vy, arah = ai.jelajah(0, 0, 0.0, 0.016, 30, acak=lambda: 0.5)
        assert abs(vx) <= 30.001 and abs(vy) <= 30.001
        assert isinstance(arah, float)

    def test_hindari(self):
        ai = _mod("ai")
        vx, vy = ai.hindari(0, 0, [(0, 0)], radius=20)
        # dorong menjauh dari rintangan di (0,0) — ke atas
        assert vy < 0

    def test_agen_kejar(self):
        ai = _mod("ai")
        agen = ai.Agen(100, 100, kecepatan_maks=120)
        agen.atur_target((200, 100), mode="kejar")
        agen.update(1.0)
        assert abs(agen.x - 220) < 0.01
        assert abs(agen.y - 100) < 0.01

    def test_agen_jelajah_mode(self):
        ai = _mod("ai")
        agen = ai.Agen(50, 50, kecepatan_maks=60)
        agen.atur_mode("jelajah")
        agen.update(0.1)
        assert agen.x != 50 or agen.y != 50  # bergerak

    def test_jarak_dan_arah(self):
        ai = _mod("ai")
        assert ai.jarak(0, 0, 3, 4) == 5.0
        import math
        assert abs(ai.arah_ke(0, 0, 1, 0) - 0.0) < 0.001


# ============================================================
# 5. tilemap — platform satu arah & platform bergerak
# ============================================================


class TestTilemapLanjutan:
    def _peta(self):
        tm = _mod("tilemap")
        peta = tm.buat_peta(10, 10, ukuran_tile=32)
        ts = tm.buat_tileset("ts", ukuran_tile=32)
        ts.tambah_tile(1, solid=True)
        ts.atur_satu_arah(2)
        peta.set_tileset(ts)
        return tm, peta

    def test_satu_arah_dari_tileset(self):
        tm, peta = self._peta()
        peta.atur(1, 5, 2)
        assert peta.cek_satu_arah(1, 5) is True
        assert peta.is_solid(1, 5) is True   # tetap solid

    def test_cek_lantai_satu_arah_jatuh(self):
        tm, peta = self._peta()
        peta.atur(1, 5, 2)
        # Kaki di tile (1,4), platform satu arah di (1,5) — jatuh -> mendarat
        assert peta.cek_lantai_satu_arah(1 * 32 + 16, 4 * 32 + 31, kecepatan_y=100) is True

    def test_cek_lantai_satu_arah_lompat(self):
        tm, peta = self._peta()
        peta.atur(1, 5, 2)
        # Melompat ke atas (kecepatan_y < 0) -> tembus
        assert peta.cek_lantai_satu_arah(1 * 32 + 16, 4 * 32 + 31, kecepatan_y=-100) is False

    def test_tandai_manual(self):
        tm, peta = self._peta()
        peta.tandai_satu_arah(3, 3)
        assert peta.cek_satu_arah(3, 3) is True
        peta.tandai_satu_arah(3, 3, satu_arah=False)
        assert peta.cek_satu_arah(3, 3) is False

    def test_platform_bergerak_horizontal(self):
        tm, peta = self._peta()
        p = peta.tambah_platform_bergerak(0, 100, 320, 100, kecepatan=100)
        assert p.x == 0 and p.y == 100
        peta.update(1.0)
        assert abs(p.x - 100) < 0.01          # 100 px/detik
        peta.update(2.2)                       # mencapai ujung & berbalik
        assert abs(p.x - 320) < 0.01
        peta.update(0.1)                       # sudah berbalik arah
        assert p.x < 320

    def test_platform_bergerak_vertikal(self):
        tm, peta = self._peta()
        p = peta.tambah_platform_bergerak(50, 0, 50, 200, kecepatan=100)
        peta.update(1.0)
        assert abs(p.y - 100) < 0.01
        peta.update(1.0)
        assert p.y <= 200

    def test_platform_bergerak_reset(self):
        tm, peta = self._peta()
        p = peta.tambah_platform_bergerak(0, 0, 100, 0, kecepatan=50)
        peta.update(1.0)
        p.reset()
        assert p.x == 0 and p.y == 0

    def test_platform_bergerak_bawa_bodi(self):
        tm, peta = self._peta()
        p = peta.tambah_platform_bergerak(0, 116, 320, 116, kecepatan=60)
        # Bodi berdiri di atas platform (kaki menyentuh y=116)
        class Bodi:
            pass
        bodi = Bodi()
        bodi.x, bodi.y, bodi.lebar, bodi.tinggi = 40, 100, 32, 16
        peta.update(1.0)                       # platform bergerak ke kanan
        peta.dorong_bodi(bodi, 1.0)
        assert bodi.x > 40                     # ikut terbawa


# ============================================================
# 6. misi — quest & achievement
# ============================================================


class TestMisi:
    def test_progres_dan_selesai(self):
        mi = _mod("misi")
        q = mi.Misi("cari_kunci", "Cari 5 Kunci", tujuan=5)
        assert q.status() == "aktif"
        assert q.progres() == 0
        assert q.tambah_progres(2) is False
        assert q.progres() == 2
        assert q.selesai() is False
        assert q.tambah_progres(3) is True    # baru selesai
        assert q.selesai() is True
        assert q.status() == "selesai"
        # progres tambahan setelah selesai tidak mengubah apa pun
        assert q.tambah_progres(5) is False

    def test_gagal(self):
        mi = _mod("misi")
        q = mi.Misi("g", "Gagalkan", tujuan=1)
        assert q.gagal() is True
        assert q.status() == "gagal"
        assert q.gagal() is False             # sudah gagal

    def test_sisa(self):
        mi = _mod("misi")
        q = mi.Misi("s", "Sisa", tujuan=10)
        q.tambah_progres(3)
        assert q.sisa() == 7

    def test_callback_on_selesai(self):
        mi = _mod("misi")
        q = mi.Misi("c", "Callback", tujuan=2)
        hasil = []
        q.on_selesai = lambda: hasil.append("done")
        q.tambah_progres(2)
        assert hasil == ["done"]

    def test_pencapaian(self):
        mi = _mod("misi")
        a = mi.Pencapaian("pembunuh", "Pembunuh Pertama", tersembunyi=True)
        assert not a.terbuka()
        assert a.buka_kunci() is True         # baru terbuka
        assert a.terbuka() is True
        assert a.buka_kunci() is False        # sudah terbuka

    def test_manajer_misi(self):
        mi = _mod("misi")
        m = mi.ManajerMisi()
        m.buat_misi("m1", "Misi 1", tujuan=3)
        m.buat_misi("m2", "Misi 2", tujuan=1)
        m.tambah_progres("m1", 3)
        assert len(m.selesai()) == 1
        assert len(m.aktif()) == 1
        assert m.aktif()[0].id == "m2"
        m.gagalkan("m2")
        assert len(m.gagal()) == 1

    def test_manajer_simpan_muat(self):
        mi = _mod("misi")
        m = mi.ManajerMisi()
        m.buat_misi("m1", "Misi 1", tujuan=3)
        m.buat_pencapaian("a1", "Ach 1")
        m.tambah_progres("m1", 3)
        m.buka_pencapaian("a1")
        data = m.ke_dict()
        m2 = mi.ManajerMisi()
        m2.muat(data)
        assert m2.dapatkan("m1").selesai() is True
        assert m2.dapatkan_pencapaian("a1").terbuka() is True
        assert m2.dapatkan("m1").status() == "selesai"

    def test_manajer_ke_dict_json_safe(self):
        import json
        mi = _mod("misi")
        m = mi.ManajerMisi()
        m.buat_misi("m1", "Misi 1", tujuan=2)
        m.tambah_progres("m1", 1)
        # Harus bisa di-serialize JSON (untuk disimpan lewat simpan_game)
        json.dumps(m.ke_dict())
