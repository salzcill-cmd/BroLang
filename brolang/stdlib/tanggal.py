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
    tulis tanggal.nama_hari("2026-08-07") # Jumat
"""

import datetime
from types import SimpleNamespace

_ISO = "%Y-%m-%d"
_ISO_DT = "%Y-%m-%d %H:%M:%S"

_NAMA_HARI = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
_NAMA_BULAN = ["Januari", "Februari", "Maret", "April", "Mei", "Juni",
               "Juli", "Agustus", "September", "Oktober", "November", "Desember"]


def _ke_tanggal(tanggal_iso: str) -> datetime.date:
    """Ubah string ISO ke objek date (terima datetime juga)."""
    if isinstance(tanggal_iso, datetime.datetime):
        return tanggal_iso.date()
    if isinstance(tanggal_iso, datetime.date):
        return tanggal_iso
    try:
        return datetime.date.fromisoformat(str(tanggal_iso)[:10])
    except ValueError:
        return datetime.datetime.strptime(str(tanggal_iso)[:19], _ISO_DT).date()


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
    (Nama hari/bulan Indonesia: gunakan komponen() atau nama_hari()/nama_bulan())
    """
    d = _ke_tanggal(tanggal_iso)
    return d.strftime(pola)


def komponen(tanggal_iso: str) -> dict:
    """Komponen tanggal: {tahun, bulan, hari, hari_dalam_minggu}."""
    d = _ke_tanggal(tanggal_iso)
    return {
        "tahun": d.year,
        "bulan": d.month,
        "hari": d.day,
        "nama_bulan": _NAMA_BULAN[d.month - 1],
        "hari_dalam_minggu": _NAMA_HARI[d.weekday()],
    }


def tambah_hari(tanggal_iso: str, n: int) -> str:
    """Tambahkan/kurangi n hari dari tanggal."""
    d = _ke_tanggal(tanggal_iso)
    return (d + datetime.timedelta(days=n)).isoformat()


def selisih_hari(tanggal_a: str, tanggal_b: str) -> int:
    """Selisih hari antara dua tanggal (a - b)."""
    da = _ke_tanggal(tanggal_a)
    db = _ke_tanggal(tanggal_b)
    return (da - db).days


def umur(tanggal_lahir: str) -> int:
    """Umur dalam tahun dari tanggal lahir."""
    lahir = _ke_tanggal(tanggal_lahir)
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


# ============= v7.1: Nama & kalender =============


def nama_hari(tanggal_iso: str) -> str:
    """Nama hari Indonesia: nama_hari("2026-08-07") -> "Jumat"."""
    d = _ke_tanggal(tanggal_iso)
    return _NAMA_HARI[d.weekday()]


def nama_bulan(tanggal_iso: str) -> str:
    """Nama bulan Indonesia: nama_bulan("2026-08-07") -> "Agustus"."""
    d = _ke_tanggal(tanggal_iso)
    return _NAMA_BULAN[d.month - 1]


def kabisat(tahun: int) -> bool:
    """Cek apakah tahun kabisat."""
    return datetime.date(tahun, 1, 1).year == tahun and (
        tahun % 4 == 0 and (tahun % 100 != 0 or tahun % 400 == 0))


def akhir_bulan(tanggal_iso: str) -> str:
    """Tanggal terakhir pada bulan dari tanggal tersebut."""
    d = _ke_tanggal(tanggal_iso)
    if d.month == 12:
        akhir = datetime.date(d.year + 1, 1, 1) - datetime.timedelta(days=1)
    else:
        akhir = datetime.date(d.year, d.month + 1, 1) - datetime.timedelta(days=1)
    return akhir.isoformat()


def tambah_bulan(tanggal_iso: str, n: int) -> str:
    """Tambahkan/kurangi n bulan (tanggal dibatasi ke akhir bulan bila perlu)."""
    d = _ke_tanggal(tanggal_iso)
    total = (d.year * 12 + (d.month - 1)) + n
    tahun = total // 12
    bulan = total % 12 + 1
    hari = min(d.day, _hari_dalam_bulan(tahun, bulan))
    return datetime.date(tahun, bulan, hari).isoformat()


def tambah_tahun(tanggal_iso: str, n: int) -> str:
    """Tambahkan/kurangi n tahun (29 Feb -> 28 Feb pada tahun non-kabisat)."""
    d = _ke_tanggal(tanggal_iso)
    hari = min(d.day, _hari_dalam_bulan(d.year + n, d.month))
    return datetime.date(d.year + n, d.month, hari).isoformat()


def selisih_jam(waktu_a: str, waktu_b: str) -> float:
    """Selisih jam antara dua datetime (a - b), terima juga 'YYYY-MM-DD'."""
    def _dt(s):
        if isinstance(s, datetime.datetime):
            return s
        s = str(s).strip()
        try:
            return datetime.datetime.fromisoformat(s)
        except ValueError:
            return datetime.datetime.combine(datetime.date.fromisoformat(s[:10]),
                                             datetime.time.min)
    return (_dt(waktu_a) - _dt(waktu_b)).total_seconds() / 3600.0


def tanggal_baru(tahun: int, bulan: int, hari: int) -> str:
    """Buat tanggal ISO dari komponen: tanggal_baru(2026, 8, 7) -> \"2026-08-07\"."""
    return datetime.date(tahun, bulan, hari).isoformat()


def _hari_dalam_bulan(tahun: int, bulan: int) -> int:
    """Jumlah hari dalam bulan tertentu (tangani tahun kabisat)."""
    if bulan == 12:
        return (datetime.date(tahun + 1, 1, 1) - datetime.date(tahun, 12, 1)).days
    return (datetime.date(tahun, bulan + 1, 1) - datetime.date(tahun, bulan, 1)).days


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
    # v7.1
    nama_hari=nama_hari,
    nama_bulan=nama_bulan,
    kabisat=kabisat,
    akhir_bulan=akhir_bulan,
    tambah_bulan=tambah_bulan,
    tambah_tahun=tambah_tahun,
    selisih_jam=selisih_jam,
    tanggal_baru=tanggal_baru,
)
