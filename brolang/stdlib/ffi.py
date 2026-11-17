"""
Modul FFI (Foreign Function Interface) BroLang
===============================================

Muat pustaka C bersama (`.so` di Linux, `.dll` di Windows, `.dylib` di macOS)
dan panggil fungsi C langsung dari BroLang via `ctypes` (stdlib Python).
Ini memberi akses ke seluruh ekosistem C tanpa menulis wrapper Python manual.

Contoh:
    impor ffi

    # Muat libc sistem
    buat libc = ffi.muat("libc.so.6")

    # Panggil puts("teks") -> int
    buat n = ffi.panggil(libc, "puts", ["teks"], "int", "Halo dari C!")
    tulis n        # panjang string yang dicetak

    # Buat buffer mentah dan baca pointer
    buat buf = ffi.cipta_buffer(64)
    ffi.panggil(libc, "memset", ["pointer", "int", "int"], "pointer", buf, 0, 64)

API:
- ffi.muat(path) -> LibHandle
- ffi.panggil(handle, nama, arg_types, restype, *args) -> hasil
- ffi.cipta_buffer(ukuran) -> buffer object (c_char_array)
- ffi.baca_pointer(ptr) -> nilai integer alamat memori
- ffi.tipe(nama) -> tipe ctypes (untuk penggunaan lanjut)

Tipe yang didukung:
  "int", "uint", "int8", "uint8", "int16", "uint16",
  "int32", "uint32", "int64", "uint64",
  "float", "double",
  "teks" (char*), "void", "pointer"/"ptr" (void*), "size_t"
"""

import ctypes
from types import SimpleNamespace

_LIBRARIES = {}

_CTYPES_MAP = {
    "int": ctypes.c_int,
    "uint": ctypes.c_uint,
    "int8": ctypes.c_int8,
    "uint8": ctypes.c_uint8,
    "int16": ctypes.c_int16,
    "uint16": ctypes.c_uint16,
    "int32": ctypes.c_int32,
    "uint32": ctypes.c_uint32,
    "int64": ctypes.c_int64,
    "uint64": ctypes.c_uint64,
    "float": ctypes.c_float,
    "double": ctypes.c_double,
    "teks": ctypes.c_char_p,
    "string": ctypes.c_char_p,
    "void": None,
    "pointer": ctypes.c_void_p,
    "ptr": ctypes.c_void_p,
    "size_t": ctypes.c_size_t,
    "ssize_t": ctypes.c_ssize_t,
    "char": ctypes.c_char,
    "uchar": ctypes.c_ubyte,
    "bool": ctypes.c_bool,
    "long": ctypes.c_long,
    "ulong": ctypes.c_ulong,
    "longlong": ctypes.c_longlong,
    "ulonglong": ctypes.c_ulonglong,
}


def _tipe(nama: str):
    """Resolve nama tipe ke ctypes type."""
    if nama in _CTYPES_MAP:
        return _CTYPES_MAP[nama]
    raise ValueError(f"Tipe FFI tidak dikenal: '{nama}'. Tipe: {', '.join(sorted(_CTYPES_MAP))}")


def muat(path: str):
    """Muat pustaka C bersama dari `path`. Kembalikan LibHandle (ctypes CDLL)."""
    try:
        lib = ctypes.CDLL(path)
    except OSError as e:
        raise OSError(f"Gagal memuat pustaka C '{path}': {e}")
    _LIBRARIES[path] = lib
    return lib


def panggil(handle, nama: str, arg_types, restype: str, *args):
    """Panggil fungsi C `nama` di pustaka `handle`.

    Args:
        handle: hasil ffi.muat(...)
        nama: nama fungsi C
        arg_types: list nama tipe argumen, mis. ["teks", "int"]
        restype: nama tipe nilai kembali, mis. "int" atau "void"
        *args: nilai argumen yang akan diteruskan

    Returns:
        Hasil pemanggilan fungsi C.
    """
    if not hasattr(handle, nama):
        raise AttributeError(f"Fungsi '{nama}' tidak ditemukan di pustaka C.")
    try:
        c_arg_types = [_tipe(t) for t in arg_types]
        c_restype = _tipe(restype)
    except ValueError:
        raise
    func = getattr(handle, nama)
    func.argtypes = c_arg_types
    func.restype = c_restype

    # Konversi argumen BroLang/Python ke ctypes saat perlu
    c_args = []
    for arg, c_type in zip(args, c_arg_types):
        if c_type is ctypes.c_char_p and isinstance(arg, str):
            c_args.append(arg.encode("utf-8"))
        elif c_type is None:
            c_args.append(arg)
        else:
            c_args.append(arg)
    return func(*c_args)


def cipta_buffer(ukuran: int):
    """Buat buffer mentah sebesar `ukuran` byte (c_char_array)."""
    return ctypes.create_string_buffer(ukuran)


def baca_pointer(ptr) -> int:
    """Baca alamat memori integer dari objek pointer/buffer."""
    return ctypes.cast(ptr, ctypes.c_void_p).value


def alamat(obj) -> int:
    """Kembalikan alamat memori objek Python sebagai integer."""
    return ctypes.addressof(obj) if hasattr(obj, "_buffer_") else id(obj)


def tipe(nama: str):
    """Kembalikan ctypes type untuk nama tipe (digunakan advanced)."""
    return _tipe(nama)


def daftar_lib():
    """Daftar path pustaka C yang sudah dimuat."""
    return sorted(list(_LIBRARIES.keys()))


def tutup_semua():
    """Tutup semua pustaka yang dimuat (best-effort)."""
    _LIBRARIES.clear()


module = SimpleNamespace(
    muat=muat,
    panggil=panggil,
    cipta_buffer=cipta_buffer,
    baca_pointer=baca_pointer,
    alamat=alamat,
    tipe=tipe,
    daftar_lib=daftar_lib,
    tutup_semua=tutup_semua,
)
