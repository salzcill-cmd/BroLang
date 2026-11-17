"""
Modul Aktor (Actor Model) untuk BroLang
=========================================

Model konkurensi berbasis passing pesan (actor model) — setiap aktor memiliki
state sendiri yang terisolasi, berkomunikasi hanya lewat pesan, dan tidak ada
state bersama. Akibatnya TIDAK ADA race condition dan tidak perlu lock manual.

Cocok untuk game loop, server, dan aplikasi yang butuh banyak tugas bersamaan
tanpa risiko data korupsi.

Contoh:
    impor aktor

    # Buat aktor penghitung dengan state terisolasi
    buat hitung = aktor.buat("hitung", lalu(state, pesan)
        jika pesan == "tambah" maka
            kembali state + 1, kosong
        selesai
        jika pesan == "ambil" maka
            kembali state, state
        selesai
        kembali state, kosong
    selesai, 0)  # state awal = 0

    # Kirim pesan (non-blokir)
    aktor.kirim(hitung, "tambah")
    aktor.kirim(hitung, "tambah")

    # Tanya + tunggu balasan (blokir)
    buat nilai = aktor.tanya(hitung, "ambil")   # 2
    tulis nilai

    aktor.hentikan(hitung)

API:
- aktor.buat(nama, perilaku, state_awal=kosong) -> Aktor
- aktor.kirim(aktor, pesan)                     # kirim pesan, tidak tunggu balasan
- aktor.tanya(aktor, pesan, timeout=None)       # kirim + tunggu balasan
- aktor.hentikan(aktor)                         # matikan aktor
- aktor.daftar()                                # daftar semua aktor aktif
- aktor.jumlah()                                # jumlah aktor aktif
- aktor.tutup_semua()                           # hentikan semua aktor
"""

import threading
import uuid
from collections import deque
from types import SimpleNamespace

_aktors = {}
_lock = threading.RLock()


class _Aktor:
    """Aktor tunggal: state terisolasi + kotak masuk pesan + thread pemroses."""

    def __init__(self, nama, perilaku, state_awal):
        self.nama = nama
        self.perilaku = perilaku
        self.state = state_awal
        self._kotak_masuk = deque()
        self._balasan = {}          # id_pesan -> hasil
        self._menunggu = {}         # id_pesan -> threading.Event
        self._running = True
        self._thread = threading.Thread(target=self._jalan, daemon=True, name=f"aktor-{nama}")
        self._thread.start()

    def _jalan(self):
        while self._running:
            try:
                pesan = self._kotak_masuk.popleft()
            except IndexError:
                threading.Event().wait(0.01)
                continue

            id_pesan = pesan.get("id")
            isi = pesan["isi"]
            butuh_balasan = pesan.get("butuh_balasan", False)

            try:
                hasil = self.perilaku(self.state, isi)
                if isinstance(hasil, tuple) and len(hasil) == 2:
                    self.state, balasan = hasil
                else:
                    self.state = hasil
                    balasan = None

                if butuh_balasan and id_pesan:
                    with _lock:
                        self._balasan[id_pesan] = balasan
                        event = self._menunggu.pop(id_pesan, None)
                    if event is not None:
                        event.set()
            except Exception as e:
                if butuh_balasan and id_pesan:
                    with _lock:
                        self._balasan[id_pesan] = e
                        event = self._menunggu.pop(id_pesan, None)
                    if event is not None:
                        event.set()

    def kirim(self, pesan, butuh_balasan=False):
        id_pesan = str(uuid.uuid4())
        event = threading.Event() if butuh_balasan else None
        with _lock:
            self._kotak_masuk.append({"id": id_pesan, "isi": pesan, "butuh_balasan": butuh_balasan})
            if butuh_balasan:
                self._menunggu[id_pesan] = event
        return id_pesan, event

    def tanya(self, pesan, timeout=None):
        id_pesan, event = self.kirim(pesan, butuh_balasan=True)
        if not event.wait(timeout):
            with _lock:
                self._menunggu.pop(id_pesan, None)
            raise TimeoutError(f"Aktor '{self.nama}' tidak membalas dalam waktu {timeout} detik.")
        with _lock:
            hasil = self._balasan.pop(id_pesan, None)
        if isinstance(hasil, Exception):
            raise hasil
        return hasil


def buat(nama, perilaku, state_awal=None):
    """Buat aktor baru dengan state terisolasi.

    Args:
        nama: Nama unik untuk aktor.
        perilaku: Fungsi(state, pesan) -> state_baru atau (state_baru, balasan).
        state_awal: State awal aktor (default kosong).

    Returns:
        Objek Aktor yang dapat dipakai dengan aktor.kirim / aktor.tanya.
    """
    with _lock:
        if nama in _aktors:
            raise ValueError(f"Aktor dengan nama '{nama}' sudah ada.")
        a = _Aktor(nama, perilaku, state_awal)
        _aktors[nama] = a
    return a


def kirim(aktor_obj, pesan):
    """Kirim pesan ke aktor (non-blokir, tidak menunggu balasan)."""
    aktor_obj.kirim(pesan)


def tanya(aktor_obj, pesan, timeout=None):
    """Kirim pesan dan tunggu balasan dari aktor (blokir sampai balas atau timeout)."""
    return aktor_obj.tanya(pesan, timeout)


def hentikan(aktor_obj):
    """Matikan aktor (thread akan berhenti setelah pemrosesan selesai)."""
    aktor_obj._running = False


def daftar():
    """Daftar nama semua aktor yang masih aktif."""
    with _lock:
        return sorted(list(_aktors.keys()))


def jumlah():
    """Jumlah aktor aktif."""
    with _lock:
        return len(_aktors)


def tutup_semua():
    """Hentikan semua aktor (digunakan saat program selesai)."""
    with _lock:
        for a in list(_aktors.values()):
            a._running = False
        _aktors.clear()


module = SimpleNamespace(
    buat=buat,
    kirim=kirim,
    tanya=tanya,
    hentikan=hentikan,
    daftar=daftar,
    jumlah=jumlah,
    tutup_semua=tutup_semua,
)
