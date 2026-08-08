"""
Modul Database BroLang
======================

Wrapper SQLite untuk penyimpanan data lokal. Menyediakan koneksi database
dengan query, eksekusi SQL, dan manajemen tabel.

Contoh:
    impor database

    buat db = database.buka("data.db")
    db.eksekusi_sql("CREATE TABLE IF NOT EXISTS pengguna (id INTEGER, nama TEXT)")
    db.eksekusi_sql("INSERT INTO pengguna (id, nama) VALUES (?, ?)", 1, "Budi")

    buat semua = db.query("SELECT * FROM pengguna")
    untuk row dalam semua lakukan
        tulis row["nama"]
    selesai

    db.tutup()
"""

import re
import sqlite3
from types import SimpleNamespace

# Nama tabel/kolom hanya boleh alfanumerik + underscore (anti SQL injection)
_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


class Database:
    """Koneksi ke database SQLite."""

    def __init__(self, path=":memory:"):
        self.path = path
        self._conn = sqlite3.connect(path)
        self._conn.row_factory = sqlite3.Row

    def eksekusi_sql(self, sql: str, *params) -> int:
        """Jalankan SQL yang mengubah data (INSERT/UPDATE/DELETE/DDL).

        Nama 'eksekusi' tidak dipakai karena tabrakan keyword BroLang.

        Returns:
            Jumlah baris yang terpengaruh (rowcount).
        """
        cur = self._conn.cursor()
        if params:
            cur.execute(sql, params)
        else:
            cur.execute(sql)
        self._conn.commit()
        return cur.rowcount

    def query(self, sql: str, *params) -> list:
        """Jalankan SELECT dan kembalikan semua baris sebagai list objek.

        Contoh:
            buat semua = db.query("SELECT * FROM pengguna")
            untuk row dalam semua lakukan
                tulis row["nama"]
            selesai
        """
        cur = self._conn.cursor()
        if params:
            cur.execute(sql, params)
        else:
            cur.execute(sql)
        return [dict(row) for row in cur.fetchall()]

    def query_satu(self, sql: str, *params):
        """Jalankan SELECT dan kembalikan baris pertama (atau kosong)."""
        rows = self.query(sql, *params)
        return rows[0] if rows else None

    def query_nilai(self, sql: str, *params):
        """Jalankan SELECT dan kembalikan nilai kolom pertama baris pertama."""
        row = self.query_satu(sql, *params)
        if row is None:
            return None
        values = list(row.values())
        return values[0] if values else None

    def tabel(self) -> list:
        """Daftar nama tabel di database (selain tabel sistem)."""
        cur = self._conn.cursor()
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' "
            "AND name NOT LIKE 'sqlite_%' ORDER BY name"
        )
        return [row[0] for row in cur.fetchall()]

    def _ident_aman(self, nama: str) -> str:
        """Validasi nama tabel/kolom; raise ValueError bila bukan identifier valid."""
        if not isinstance(nama, str) or not _IDENTIFIER_RE.match(nama):
            raise ValueError(f"Nama tabel/kolom tidak valid: {nama!r}")
        return nama

    def kolom(self, nama_tabel: str) -> list:
        """Daftar nama kolom sebuah tabel."""
        cur = self._conn.cursor()
        try:
            cur.execute(f"PRAGMA table_info({self._ident_aman(nama_tabel)})")
            return [row[1] for row in cur.fetchall()]
        except (sqlite3.Error, ValueError):
            return []

    def jumlah_baris(self, nama_tabel: str) -> int:
        """Jumlah baris di sebuah tabel."""
        cur = self._conn.cursor()
        try:
            cur.execute(f"SELECT COUNT(*) FROM {self._ident_aman(nama_tabel)}")
            return cur.fetchone()[0]
        except (sqlite3.Error, ValueError):
            return 0

    def eksekusi_banyak(self, sql: str, daftar_baris: list) -> int:
        """Jalankan SQL yang sama untuk banyak baris (insert bulk)."""
        cur = self._conn.cursor()
        cur.executemany(sql, daftar_baris)
        self._conn.commit()
        return cur.rowcount

    def tutup(self) -> None:
        """Tutup koneksi database."""
        try:
            self._conn.close()
        except sqlite3.Error:
            pass

    def tersambung(self) -> bool:
        """Cek apakah koneksi masih terbuka."""
        try:
            self._conn.execute("SELECT 1")
            return True
        except sqlite3.Error:
            return False


def buka(path: str = ":memory:") -> Database:
    """Buka (atau buat) database SQLite di path. `:memory:` untuk di memori.

    Contoh:
        buat db = database.buka("data.db")
    """
    return Database(path)


def buka_memori() -> Database:
    """Buka database sementara di memori (tidak disimpan ke file)."""
    return Database(":memory:")


module = SimpleNamespace(
    Database=Database,
    buka=buka,
    buka_memori=buka_memori,
)
