"""
Modul Penampilan untuk BroLang
===============================

Pretty printing: tabel, pohon, format data, JSON indented.

Contoh:
    impor penampilan
    
    # Tabel
    buat data = [
        {"nama": "Budi", "umur": 25, "kota": "Jakarta"},
        {"nama": "Ani", "umur": 30, "kota": "Bandung"},
    ]
    tulis penampilan.tabel(data)
    
    # Pohon
    buat pohon = {"akar": {"anak1": {}, "anak2": {"cucu": {}}}}
    tulis penampilan.pohon(pohon)
    
    # Format angka
    tulis penampilan.angka(1234567)      # "1,234,567"
    tulis penampilan.angka_desimal(3.14) # "3.14"
    
    # Daftar bernomor
    tulis penampilan.bernomic(["apel", "mangga", "jeruk"])
    
    # Key-value pair
    tulis penampilan.kvp({"nama": "Budi", "umur": 25})
"""


def tabel(data, columns=None, padding=2):
    """Format list objek sebagai tabel ASCII.
    
    Args:
        data: list of dict
        columns: list nama kolom (default: semua kunci dari item pertama)
        padding: spasi antar kolom
    
    Returns:
        string tabel
    """
    if not data:
        return "(kosong)"
    
    if columns is None:
        columns = list(data[0].keys())
    
    # Hitung lebar kolom
    widths = {}
    for col in columns:
        widths[col] = len(str(col))
    for row in data:
        for col in columns:
            val = str(row.get(col, ""))
            if len(val) > widths[col]:
                widths[col] = len(val)
    
    pad = " " * padding
    
    # Header
    header = pad.join(str(col).ljust(widths[col]) for col in columns)
    separator = pad.join("-" * widths[col] for col in columns)
    
    lines = [header, separator]
    
    # Rows
    for row in data:
        line = pad.join(str(row.get(col, "")).ljust(widths[col]) for col in columns)
        lines.append(line)
    
    return "\n".join(lines)


def daftar(items, style="bullet", start=1):
    """Format list sebagai daftar terformat.
    
    Args:
        items: list nilai
        style: "bullet" (-), "number" (1.), "letter" (a.), "roman" (i.)
        start: nomor awal (untuk style number)
    
    Returns:
        string daftar
    """
    if not items:
        return "(kosong)"
    
    lines = []
    for i, item in enumerate(items):
        if style == "bullet":
            lines.append(f"  • {item}")
        elif style == "number":
            lines.append(f"  {start + i}. {item}")
        elif style == "letter":
            letter = chr(ord('a') + i)
            lines.append(f"  {letter}. {item}")
        elif style == "roman":
            lines.append(f"  {_to_roman(start + i)}. {item}")
        else:
            lines.append(f"  • {item}")
    
    return "\n".join(lines)


def _to_roman(num):
    """Konversi angka ke angka Romawi."""
    val = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
    syms = ['M', 'CM', 'D', 'CD', 'C', 'XC', 'L', 'XL', 'X', 'IX', 'V', 'IV', 'I']
    result = ''
    for i in range(len(val)):
        while num >= val[i]:
            result += syms[i]
            num -= val[i]
    return result


def pohon(data, indent=2, prefix=""):
    """Format dict/objek sebagai pohon (tree view).
    
    Args:
        data: dict atau objek
        indent: jumlah spasi per level
        prefix: prefix untuk baris terakhir
    
    Returns:
        string pohon
    """
    if not data:
        return "(kosong)"
    
    lines = []
    _pohon_rekursif(data, lines, "", indent)
    return "\n".join(lines)


def _pohon_rekursif(data, lines, current_prefix, indent):
    """Helper rekursif untuk pohon."""
    if isinstance(data, dict):
        keys = list(data.keys())
        for i, key in enumerate(keys):
            is_last = (i == len(keys) - 1)
            connector = "└── " if is_last else "├── "
            child_prefix = "    " if is_last else "│   "
            
            val = data[key]
            if isinstance(val, dict) and val:
                lines.append(f"{current_prefix}{connector}{key}")
                _pohon_rekursif(val, lines, current_prefix + child_prefix, indent)
            elif isinstance(val, list) and val:
                lines.append(f"{current_prefix}{connector}{key}")
                for j, item in enumerate(val):
                    item_last = (j == len(val) - 1)
                    item_connector = "└── " if item_last else "├── "
                    lines.append(f"{current_prefix}{child_prefix}{item_connector}{item}")
            else:
                lines.append(f"{current_prefix}{connector}{key}: {val}")
    elif isinstance(data, list):
        for i, item in enumerate(data):
            is_last = (i == len(data) - 1)
            connector = "└── " if is_last else "├── "
            lines.append(f"{current_prefix}{connector}{item}")


def angka(n, separator=","):
    """Format angka dengan separator ribuan.
    
    Contoh:
        penampilan.angka(1234567)     # "1,234,567"
        penampilan.angka(1234567, ".") # "1.234.567"
    """
    if not isinstance(n, (int, float)):
        return str(n)
    
    if isinstance(n, float):
        parts = f"{n:.10f}".rstrip("0").rstrip(".")
        int_part, _, dec_part = parts.partition(".")
    else:
        int_part = str(n)
        dec_part = ""
    
    # Add separator
    reversed_int = int_part[::-1]
    grouped = [reversed_int[i:i+3] for i in range(0, len(reversed_int), 3)]
    formatted_int = separator.join(grouped)[::-1]
    
    if dec_part:
        return f"{formatted_int}.{dec_part}"
    return formatted_int


def angka_desimal(n, desimals=2):
    """Format angka desimal dengan precision.
    
    Contoh:
        penampilan.angka_desimal(3.14159)  # "3.14"
        penampilan.angka_desimal(2.0, 0)   # "2"
    """
    if desimals == 0:
        return str(int(round(n)))
    return f"{n:.{desimals}f}"


def persen(n, desimals=1):
    """Format sebagai persentase.
    
    Contoh:
        penampilan.persen(0.75)      # "75.0%"
        penampilan.persen(0.756, 1)  # "75.6%"
    """
    return f"{n * 100:.{desimals}f}%"


def kvp(data, separator=": ", indent=2):
    """Format key-value pairs.
    
    Contoh:
        penampilan.kvp({"nama": "Budi", "umur": 25})
        # nama: Budi
        # umur: 25
    """
    if not data:
        return "(kosong)"
    
    max_key_len = max(len(str(k)) for k in data.keys()) if data else 0
    
    lines = []
    for key, val in data.items():
        key_str = str(key).ljust(max_key_len)
        lines.append(f"{key_str}{separator}{val}")
    
    return "\n".join(lines)


def bernomic(items, start=1):
    """Format list bernomor.
    
    Contoh:
        penampilan.bernomic(["apel", "mangga"])
        # 1. apel
        # 2. mangga
    """
    return daftar(items, style="number", start=start)


def json_indented(data, indent=2):
    """Format objek sebagai JSON indented (tanpa dependency json).
    
    Contoh:
        penampilan.json_indented({"nama": "Budi", "hobi": ["coding", "gaming"]})
    """
    return _format_value(data, indent, 0)


def _format_value(val, indent, level):
    """Helper untuk json_indented."""
    pad = " " * (indent * level)
    pad_inner = " " * (indent * (level + 1))
    
    if val is None:
        return "null"
    if isinstance(val, bool):
        return "true" if val else "false"
    if isinstance(val, (int, float)):
        return str(val)
    if isinstance(val, str):
        return f'"{val}"'
    if isinstance(val, list):
        if not val:
            return "[]"
        items = []
        for item in val:
            items.append(f"{pad_inner}{_format_value(item, indent, level + 1)}")
        return "[\n" + ",\n".join(items) + f"\n{pad}]"
    if isinstance(val, dict):
        if not val:
            return "{}"
        items = []
        for k, v in val.items():
            items.append(f'{pad_inner}"{k}": {_format_value(v, indent, level + 1)}')
        return "{\n" + ",\n".join(items) + f"\n{pad}}}"
    return str(val)


def horizontal(data, lebar=40):
    """Buat progress bar horizontal.
    
    Contoh:
        penampilan.horizontal(0.7)   # [██████████████░░░░░░░░░░░░░░░░░░░░░░░░░░] 70%
    """
    persen = min(1.0, max(0.0, data))
    terisi = int(persen * lebar)
    kosong = lebar - terisi
    bar = "█" * terisi + "░" * kosong
    return f"[{bar}] {persen * 100:.0f}%"
