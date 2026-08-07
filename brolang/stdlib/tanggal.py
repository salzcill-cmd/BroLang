"""
Modul Tanggal BroLang (v6.0)
============================

Operasi tanggal & waktu yang lengkap: parsing, format, aritmatika selisih,
dan komponen tanggal.

Contoh:
    impor tanggal

    tulis tanggal.hari_ini()              # 2026-08-07
    tulis tanggal.parse("2026-08-07")     # objek tanggal
    buat selisih = tanggal.selisih_hari("2026-08-07", "2026-08-01")   # 6
"""

import datetime
from types import SimpleNamespace

_ISO = "%Y-%m-%d"
_ISO_DT = "%Y-%m-%d %H:%M:%S"


def hari_ini() -> str:
    """Tanggal hari ini (YYYY-MM-DD)."""
    return datetime.date.today().isoformat()


def sekarang() -> str:
    """Tanggal & waktu sekarang (YYYY-MM-DD HH:MM:SS)."""
    return datetime.datetime.now().strftime(_ISO_DT)


def parse(teks_tanggal: str) -> str:
    """Parse string tanggal ke format baku (YYYY-MM-DD).

    Menerima berbagai format umum:
        parse("07/08/2026")      # DD/MM/YYYY
        parse("2026-08-07")      # ISO
        parse("7 Agustus 2026")  # nama bulan Indonesia
    """
    t = teks_tanggal.strip()
    for fmt in (_ISO, "%d/%m/%Y", "%Y/%m/%d", "%d-%m-%Y", "%d %B %Y",
                "%d %b %Y", "%B %d, %Y", "%d %B %Y", "%Y%m%d"):
        try:
            return datetime.datetime.strptime(t, fmt).date().isoformat()
        except ValueError:
            continue
    # Nama bulan Indonesia
    bulan_id = {
        "januari": 1, "februari": 2, "maret": 3, "april": 4, "mei": 5,
        "juni": 6, "juli": 7, "agustus": 8, "september": 9, "oktober": 10,
        "november": 11, "desember": 12,
    }
    parts = t.replace(",", "").split()
    if len(parts) == 3:
        try:
            hari = int(parts[0])
            bulan = bulan_id.get(parts[1].lower())
            tahun = int(parts[2])
            if bulan:
                return datetime.date(tahun, bulan, hari).isoformat()
        except (ValueError, IndexError):
            pass
    raise ValueError(f"Format tanggal tidak dikenal: '{teks_tanggal}'")


def format(tanggal_iso: str, pola: str = "%d %B %Y") -> str:
    """Format tanggal ISO ke pola tertentu (strftime Python).

    Contoh:
        format("2026-08-07", "%d %B %Y")      # 07 August 2026 (strftime)
        format("2026-08-07", "%Y-%m-%d")      # 2026-08-07
    (Nama hari/bulan Indonesia: gunakan komponen())
    """
    try:
        d = datetime.date.fromisoformat(tanggal_iso)
    except ValueError:
        d = datetime.datetime.strptime(tanggal_iso, _ISO).date()
    return d.strftime(pola)


def komponen(tanggal_iso: str) -> dict:
    """Komponen tanggal: {tahun, bulan, hari, hari_dalam_minggu}."""
    try:
        d = datetime.date.fromisoformat(tanggal_iso)
    except ValueError:
        d = datetime.datetime.strptime(tanggal_iso, _ISO).date()
    nama_hari = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
    nama_bulan = ["Januari", "Februari", "Maret", "April", "Mei", "Juni",
                  "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
    return {
        "tahun": d.year,
        "bulan": d.month,
        "hari": d.day,
        "nama_bulan": nama_bulan[d.month - 1],
        "hari_dalam_minggu": nama_hari[d.weekday()],
    }


def tambah_hari(tanggal_iso: str, n: int) -> str:
    """Tambahkan/kurangi n hari dari tanggal."""
    d = datetime.date.fromisoformat(tanggal_iso)
    return (d + datetime.timedelta(days=n)).isoformat()


def selisih_hari(tanggal_a: str, tanggal_b: str) -> int:
    """Selisih hari antara dua tanggal (a - b)."""
    da = datetime.date.fromisoformat(tanggal_a)
    db = datetime.date.fromisoformat(tanggal_b)
    return (da - db).days


def umur(tanggal_lahir: str) -> int:
    """Umur dalam tahun dari tanggal lahir."""
    lahir = datetime.date.fromisoformat(tanggal_lahir)
    hari_ini = datetime.date.today()
    return hari_ini.year - lahir.year - (
        (hari_ini.month, hari_ini.day) < (lahir.month, lahir.day))


def hari_besar(nama: str = "") -> str:
    """Tanggal hari besar nasional Indonesia (nama -> tanggal ISO)."""
    libur = {
        "tahun_baru": lambda y: f"{y}-01-01",
        "kemerdekaan": lambda y: f"{y}-08-17",
        "kartini": lambda y: f"{y}-04-21",
        "pahlawan": lambda y: f"{y}-11-10",
        "kartu": lambda y: f"{y}-02-14",
        "valentine": lambda y: f"{y}-02-14",
        "bumi": lambda y: f"{y}-04-22",
        "pendidikan": lambda y: f"{y}-05-02",
    }
    fn = libur.get(nama.lower())
    if not fn:
        raise ValueError(f"Hari besar '{nama}' tidak dikenal.")
    return fn(datetime.date.today().year)


module = SimpleNamespace(
    hari_ini=hari_ini,
    sekarang=sekarang,
    parse=parse,
    format=format,
    komponen=komponen,
    tambah_hari=tambah_hari,
    selisih_hari=selisih_hari,
    umur=umur,
    hari_besar=hari_besar,
)
