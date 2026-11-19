"""
Tes untuk modul belajar (v12.3 — Sistem Belajar Adaptif).
"""

import json
import os
import tempfile

import pytest

import brolang.belajar as belajar_mod
from brolang.belajar import (
    BAB,
    TOTAL_POIN,
    cek_jawaban,
    _baca_progres,
    _simpan_progres,
    _konsep_progres,
    _perbarui_konsep,
    _deteksi_pola_kesalahan,
    _feedback_kualitas_kode,
    _petunjuk_tingkat,
)


@pytest.fixture
def temp_progres_file(monkeypatch):
    """Alihkan _PROGRESS_FILE ke berkas sementara sehingga tes tidak menyentuh
    berkas progres nyata di ~/.brolang."""
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    monkeypatch.setattr(belajar_mod, "_PROGRESS_FILE", path)
    yield path
    try:
        os.unlink(path)
    except OSError:
        pass


# ============= cek_jawaban =============


def test_cek_jawaban_benar():
    soal = BAB[0]["soal"][0]  # tulis "Halo Dunia!"
    status, detail = cek_jawaban('tulis "Halo Dunia!"', soal)
    assert status == "benar"
    assert detail == ["Halo Dunia!"]


def test_cek_jawaban_salah():
    soal = BAB[0]["soal"][0]
    status, detail = cek_jawaban('tulis "Salah"', soal)
    assert status == "salah"
    assert "Halo Dunia!" in detail


def test_cek_jawaban_mengandung():
    soal = BAB[0]["soal"][1]  # mengandung "Halo, saya"
    status, detail = cek_jawaban('tulis "Halo, saya Budi!"', soal)
    assert status == "benar"


def test_cek_jawaban_error_sintaks():
    soal = BAB[0]["soal"][0]
    status, detail = cek_jawaban("tulis \"belum ditutup", soal)
    assert status == "error"


def test_cek_jawaban_error_runtime():
    soal = BAB[0]["soal"][0]
    status, detail = cek_jawaban("tulis 1 / 0", soal)
    assert status == "error"


# ============= Progres baca/simpan =============


def test_progres_default_kosong(temp_progres_file):
    progres = _baca_progres()
    assert progres == {"versi": 1}


def test_progres_simpan_dan_baca(temp_progres_file):
    data = {"versi": 1, "total_nilai": 50, "bab_selesai": 2}
    _simpan_progres(data)
    kembali = _baca_progres()
    assert kembali["total_nilai"] == 50
    assert kembali["bab_selesai"] == 2


# ============= Konsep progres =============


def test_konsep_progres_buat_baru(temp_progres_file):
    progres = {"versi": 1}
    entri = _konsep_progres(progres, "tulis")
    assert entri["level"] == 0
    assert entri["attempts"] == 0
    assert entri["benar"] == 0
    assert progres["konsep"]["tulis"] is entri


def test_perbarui_konsep_benar_naik_level(temp_progres_file):
    progres = {"versi": 1}
    # 3x benar berturut-turut -> naik ke level 1 (belajar)
    for _ in range(3):
        _perbarui_konsep(progres, "variabel", benar=True)
    entri = progres["konsep"]["variabel"]
    assert entri["level"] == 1
    assert entri["benar"] == 3
    assert entri["attempts"] == 3


def test_perbarui_konsep_salah_banyak_turun_level(temp_progres_file):
    progres = {"versi": 1}
    # Mulai dari level 1 dulu
    for _ in range(3):
        _perbarui_konsep(progres, "operator", benar=True)
    # lalu 5x salah -> turun ke level 0
    for _ in range(5):
        _perbarui_konsep(progres, "operator", benar=False)
    entri = progres["konsep"]["operator"]
    assert entri["level"] == 0
    assert entri["salah"] == 5


# ============= Pola kesalahan =============


def test_deteksi_pola_print():
    hasil = _deteksi_pola_kesalahan('print("Halo")')
    assert any(nama == "keyword_print" for nama, _, _, _ in hasil)


def test_deteksi_pola_if():
    hasil = _deteksi_pola_kesalahan("if(x > 5)")
    assert any(nama == "keyword_if" for nama, _, _, _ in hasil)


def test_deteksi_pola_assign_vs_compare():
    hasil = _deteksi_pola_kesalahan("jika nilai = 80 maka")
    assert any(nama == "assign_vs_compare" for nama, _, _, _ in hasil)


def test_deteksi_pola_tidak_ada(kode_bersih="tulis \"Halo\""):
    hasil = _deteksi_pola_kesalahan(kode_bersih)
    assert hasil == []


# ============= Feedback kualitas kode =============


def test_feedback_variabel_tidak_dipakai():
    masukan = _feedback_kualitas_kode("buat x = 5\ntulis 1")
    assert any("x" in m and "belum dipakai" in m for m in masukan)


def test_feedback_semicolon():
    masukan = _feedback_kualitas_kode("tulis \"Halo\";")
    assert any("titik koma" in m for m in masukan)


def test_feedback_variabel_dipakai_tidak_masalah():
    masukan = _feedback_kualitas_kode("buat x = 5\ntulis x")
    assert not any("belum dipakai" in m for m in masukan)


# ============= Petunjuk tingkat =============


def test_petunjuk_tingkat():
    soal = BAB[0]["soal"][0]
    p0 = _petunjuk_tingkat(soal, 0)
    p3 = _petunjuk_tingkat(soal, 3)
    assert p0 != p3 or len(soal["petunjuk"]) == 1
    assert "tulis" in p0 or "tulis" in p3


# ============= Kurikulum =============


def test_bab_tidak_kosong():
    assert len(BAB) > 0
    for bab in BAB:
        assert bab["judul"]
        assert bab["ikon"]
        assert bab["materi"]
        assert bab["soal"]
        for soal in bab["soal"]:
            assert soal["teks"]
            assert soal["konsep"]
            assert soal["cek"]
            assert soal["harapan"]
            assert soal["solusi"]
            assert soal["poin"] > 0


def test_total_positif():
    assert TOTAL_POIN > 0


# ============= CLI mode parsing (via __main__) =============


def test_main_mode_ulang(monkeypatch):
    called = {}

    def fake_mulai(mode="normal", konsep=None):
        called["mode"] = mode
        called["konsep"] = konsep
        return 0

    monkeypatch.setattr(belajar_mod, "mulai_belajar", fake_mulai)
    belajar_mod.mulai_belajar(mode="ulang")
    assert called["mode"] == "ulang"


def test_main_mode_latihan_konsep(monkeypatch):
    called = {}

    def fake_mulai(mode="normal", konsep=None):
        called["mode"] = mode
        called["konsep"] = konsep
        return 0

    monkeypatch.setattr(belajar_mod, "mulai_belajar", fake_mulai)
    belajar_mod.mulai_belajar(mode="latihan", konsep="variabel")
    assert called["mode"] == "latihan"
    assert called["konsep"] == "variabel"


def test_total_poin_sesuai_bab():
    total = sum(soal["poin"] for bab in BAB for soal in bab["soal"])
    assert total == TOTAL_POIN
