"""
Modul Visualisasi Data untuk BroLang
=====================================

Menyediakan berbagai macam chart/grafik untuk memvisualisasikan data,
baik dalam bentuk ASCII (langsung tampil di terminal) maupun SVG/HTML
(untuk laporan yang bisa dibuka di browser).

Contoh:
    impor visualisasi

    buat data = [12, 45, 23, 67, 34, 89, 56]

    # Chart ASCII langsung di terminal
    tulis visualisasi.batang(data, judul="Penjualan Mingguan")

    # Chart SVG + simpan ke file
    buat svg = visualisasi.batang_svg(data, judul="Penjualan Mingguan")
    visualisasi.simpan_svg("penjualan.svg", svg)

    # Laporan HTML berisi banyak chart sekaligus
    visualisasi.simpan_html("laporan.html", [svg, svg2], judul="Laporan Bulanan")

Fungsi yang tersedia:
    ASCII:  batang, garis, kue, sebar, histogram
    SVG:    batang_svg, garis_svg, kue_svg, sebar_svg, histogram_svg
    Export: simpan_svg, simpan_html, simpan_txt
    GUI:    tampilkan_jendela, tampilkan_batang, tampilkan_garis, tampilkan_kue,
            tampilkan_sebar, tampilkan_histogram, simpan_png

Contoh GUI (butuh pygame):
    pip install pygame-ce

    impor visualisasi
    buat chart1 = {"jenis": "batang", "data": [12, 45, 23, 67], "judul": "Penjualan"}
    buat chart2 = {"jenis": "kue", "data": {"A": 30, "B": 40}, "judul": "Pasar"}
    visualisasi.tampilkan_jendela([chart1, chart2], judul="Dashboard")

    # Atau langsung satu chart:
    visualisasi.tampilkan_batang([12, 45, 23], judul="Penjualan")

Format data yang didukung (semua fungsi):
    1. List nilai:        [12, 45, 23, 67]            + label opsional
    2. List pasangan:     [["Senin", 12], ["Selasa", 45]]
    3. Objek/dict:        {"Senin": 12, "Selasa": 45}
"""

import math
from types import SimpleNamespace

# =============================================================================
# Konstanta & helper dasar
# =============================================================================

_PALETTE = [
    "#6366f1",  # indigo
    "#10b981",  # emerald
    "#f59e0b",  # amber
    "#ef4444",  # red
    "#06b6d4",  # cyan
    "#8b5cf6",  # violet
    "#ec4899",  # pink
    "#84cc16",  # lime
    "#f97316",  # orange
    "#14b8a6",  # teal
]

# Karakter untuk setiap irisan pie ASCII
_PIE_CHARS = ["█", "▓", "▒", "░", "▄", "▌", "▐", "▀"]

# ANSI 256 color (untuk chart berwarna di terminal)
_ANSI = [
    "\x1b[38;5;39m",   # biru
    "\x1b[38;5;42m",   # hijau
    "\x1b[38;5;214m",  # kuning
    "\x1b[38;5;196m",  # merah
    "\x1b[38;5;45m",   # cyan
    "\x1b[38;5;141m",  # ungu
    "\x1b[38;5;206m",  # pink
    "\x1b[38;5;112m",  # lime
]
_ANSI_RESET = "\x1b[0m"

# Counter untuk membuat ID unik pada elemen SVG (mencegah bentrok id
# gradient saat beberapa chart disisipkan dalam satu dokumen HTML)
_UID_COUNTER = [0]


def _uid(prefix: str) -> str:
    _UID_COUNTER[0] += 1
    return f"{prefix}{_UID_COUNTER[0]}"


def _fmt(v) -> str:
    """Format angka dengan rapi: 12.0 -> '12', 12.5 -> '12.5'."""
    try:
        f = float(v)
    except (TypeError, ValueError):
        return str(v)
    if f == int(f) and abs(f) < 1e15:
        return str(int(f))
    return f"{f:.4f}".rstrip("0").rstrip(".")


def _norm(data, label=None):
    """Normalisasi input data menjadi (labels, values).

    Mendukung tiga bentuk input:
      1. [12, 45, 23]                    + label opsional
      2. [["Senin", 12], ["Selasa", 45]]
      3. {"Senin": 12, "Selasa": 45}
    """
    if isinstance(data, dict):
        items = list(data.items())
        labels = [str(k) for k, _ in items]
        values = [float(v) for _, v in items]
        return labels, values
    data = list(data)
    if data and isinstance(data[0], (list, tuple)) and len(data[0]) == 2:
        labels = [str(p[0]) for p in data]
        values = [float(p[1]) for p in data]
        return labels, values
    values = [float(v) for v in data]
    if label is None:
        labels = [str(i + 1) for i in range(len(values))]
    else:
        labels = [str(l) for l in label]
    return labels, values


def _nice_ticks(lo, hi, target=5):
    """Buat tick marks yang 'bulat' di antara lo dan hi."""
    if hi <= lo:
        hi = lo + 1.0
    span = hi - lo
    raw = span / max(1, target)
    mag = 10 ** math.floor(math.log10(raw))
    norm = raw / mag
    if norm <= 1:
        step = mag
    elif norm <= 2:
        step = 2 * mag
    elif norm <= 5:
        step = 5 * mag
    else:
        step = 10 * mag
    start = math.floor(lo / step) * step
    ticks = []
    v = start
    while v <= hi + step * 1e-6:
        ticks.append(round(v, 12))
        v += step
    return ticks


def _truncate(s, n=12):
    s = str(s)
    return s if len(s) <= n else s[: n - 1] + "…"


def _esc(s):
    """Escape teks untuk disisipkan ke SVG."""
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _svg_kosong(lebar, tinggi, judul):
    """SVG placeholder saat data kosong."""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{lebar}" height="{tinggi}" '
        f'viewBox="0 0 {lebar} {tinggi}">'
        f'<rect width="100%" height="100%" fill="#ffffff"/>'
        f'<text x="{lebar / 2}" y="{tinggi / 2}" text-anchor="middle" '
        f'font-family="Segoe UI, Arial, sans-serif" font-size="16" fill="#94a3b8">'
        f'{(judul + " — ") if judul else ""}tidak ada data</text></svg>'
    )


def _svg_header(lebar, tinggi):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{lebar}" height="{tinggi}" '
        f'viewBox="0 0 {lebar} {tinggi}" font-family="Segoe UI, Arial, sans-serif">'
    )


# =============================================================================
# Chart ASCII (tampil langsung di terminal)
# =============================================================================


def batang(data, label=None, judul="", lebar=40, satuan="", berwarna=False):
    """Chart batang horizontal (ASCII).

    Args:
        data: List nilai / list pasangan / dict.
        label: Label untuk tiap bar (opsional).
        judul: Judul chart.
        lebar: Panjang bar maksimum dalam karakter.
        satuan: Satuan yang ditampilkan setelah nilai (misal "unit", "Rp").
        berwarna: Aktifkan warna ANSI di terminal.
    """
    labels, values = _norm(data, label)
    if not values:
        return "(data kosong)"
    label_w = max(6, min(24, max(len(l) for l in labels)))
    vmax = max(values)
    if vmax <= 0:
        vmax = 1
    lines = []
    if judul:
        lines.append(str(judul))
    for i, v in enumerate(values):
        blocks = max(1, min(lebar, int(round(v / vmax * lebar))))
        bar = "█" * blocks
        if berwarna:
            bar = _ANSI[i % len(_ANSI)] + bar + _ANSI_RESET
        fmt = _fmt(v)
        if satuan:
            fmt += " " + str(satuan)
        lines.append(f"{labels[i]:<{label_w}} │ {bar} {fmt}")
    return "\n".join(lines)


def garis(data, label=None, judul="", tinggi=12, lebar=None, berwarna=False):
    """Chart garis (ASCII).

    Args:
        data: List nilai yang akan diplot.
        label: Label untuk sumbu X (opsional).
        judul: Judul chart.
        tinggi: Tinggi area plot dalam baris karakter.
        lebar: Lebar area plot dalam kolom (default menyesuaikan panjang data).
    """
    values = [float(v) for v in data]
    if not values:
        return "(data kosong)"
    n = len(values)
    lebar = lebar or max(20, min(60, n))
    H = max(8, int(tinggi))
    W = max(10, int(lebar))
    vmin, vmax = min(values), max(values)
    label_min, label_max = _fmt(vmin), _fmt(vmax)
    if vmax == vmin:
        vmax = vmin + 1
    # Peta nilai -> baris (baris 0 = atas / nilai maks)
    def row_of(v):
        return int(round((vmax - v) / (vmax - vmin) * (H - 1)))

    grid = [[" " for _ in range(W)] for _ in range(H)]
    # Gridline horizontal pada kuartil
    for q in (0.25, 0.5, 0.75):
        r = int(round(q * (H - 1)))
        for c in range(W):
            grid[r][c] = "-"
    # Kolom axis kiri
    for r in range(H):
        grid[r][0] = "│"
    for r in range(H):
        grid[r][0] = "┼" if grid[r][0] == "-" else "│"
    grid[H - 1][0] = "└"

    def bresenham(x0, y0, x1, y1):
        dx = abs(x1 - x0)
        sx = 1 if x0 < x1 else -1
        dy = -abs(y1 - y0)
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            if 0 <= y0 < H and 0 <= x0 < W:
                if grid[y0][x0] == " ":
                    grid[y0][x0] = "─"
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    xs = []
    for i, v in enumerate(values):
        x = int(round(i * (W - 1) / max(1, n - 1)))
        y = row_of(v)
        xs.append((x, y))
        grid[y][x] = "●"
    for i in range(len(xs) - 1):
        bresenham(xs[i][0], xs[i][1], xs[i + 1][0], xs[i + 1][1])

    lines = []
    if judul:
        lines.append(str(judul))
    lines.append(f"maks {label_max}")
    for r in range(H):
        row = "".join(grid[r])
        if berwarna:
            row = row.replace("●", _ANSI[0] + "●" + _ANSI_RESET)
            row = row.replace("─", _ANSI[0] + "─" + _ANSI_RESET)
        lines.append(row)
    lines.append(f"min  {label_min}")
    if label:
        # Label sumbu X disebar merata di bawah chart
        step = max(1, W // n)
        xlabels = ""
        for i, l in enumerate(label):
            pos = xs[i][0]
            piece = _truncate(l, 8)
            xlabels += " " * max(0, pos - len(xlabels))
            xlabels += piece
        lines.append(xlabels)
    return "\n".join(lines)


def kue(data, label=None, judul="", radius=8, satuan="", desimal=1):
    """Chart pie / donat (ASCII).

    Args:
        data: List nilai / list pasangan / dict.
        label: Label untuk tiap irisan (opsional).
        judul: Judul chart.
        radius: Radius donat dalam karakter.
        satuan: Satuan nilai.
        desimal: Jumlah digit desimal untuk persentase.
    """
    labels, values = _norm(data, label)
    if not values:
        return "(data kosong)"
    if any(v < 0 for v in values):
        return "(data tidak valid — chart pie tidak mendukung nilai negatif)"
    total = sum(values)
    if total <= 0:
        return "(data tidak valid — total harus > 0)"
    r = max(4, int(radius))
    size = 2 * r + 1
    # Sudut akhir kumulatif tiap irisan
    angles = []
    acc = 0.0
    for v in values:
        acc += (v / total) * 2 * math.pi
        angles.append(acc)
    inner = max(1, int(r * 0.38))
    rows = []
    for row in range(size):
        line = ""
        for col in range(size):
            x = col - r
            y = row - r
            dist = math.hypot(x, y)
            if dist > r + 0.4:
                line += " "
                continue
            if dist < inner - 0.4:
                line += " "
                continue
            angle = math.atan2(y, x)
            if angle < 0:
                angle += 2 * math.pi
            idx = 0
            for i, a in enumerate(angles):
                if angle <= a:
                    idx = i
                    break
            line += _PIE_CHARS[idx % len(_PIE_CHARS)]
        rows.append(line)
    lines = []
    if judul:
        lines.append(str(judul))
    lines.extend(rows)
    lines.append("")
    for i, v in enumerate(values):
        pct = v / total * 100
        label_str = labels[i] if i < len(labels) else str(i + 1)
        value_str = _fmt(v)
        if satuan:
            value_str += " " + str(satuan)
        lines.append(
            f"{_PIE_CHARS[i % len(_PIE_CHARS)]} {label_str} : {value_str} "
            f"({pct:.{desimal}f}%)"
        )
    return "\n".join(lines)


def sebar(x_data, y_data, judul="", tinggi=14, lebar=44, berwarna=False):
    """Scatter plot (ASCII).

    Args:
        x_data: List nilai sumbu X.
        y_data: List nilai sumbu Y.
        judul: Judul chart.
        tinggi: Tinggi area plot dalam baris.
        lebar: Lebar area plot dalam kolom.
    """
    pts = list(zip(list(x_data), list(y_data)))
    if not pts:
        return "(data kosong)"
    X = [float(p[0]) for p in pts]
    Y = [float(p[1]) for p in pts]
    H = max(8, int(tinggi))
    W = max(16, int(lebar))
    xmin, xmax = min(X), max(X)
    ymin, ymax = min(Y), max(Y)
    lab_xmin, lab_xmax = _fmt(xmin), _fmt(xmax)
    lab_ymin, lab_ymax = _fmt(ymin), _fmt(ymax)
    if xmax == xmin:
        xmax = xmin + 1
    if ymax == ymin:
        ymax = ymin + 1

    def col_of(x):
        return int(round((x - xmin) / (xmax - xmin) * (W - 1)))

    def row_of(y):
        return int(round((ymax - y) / (ymax - ymin) * (H - 1)))

    grid = [[" " for _ in range(W)] for _ in range(H)]
    # Border
    for c in range(W):
        grid[0][c] = "─"
        grid[H - 1][c] = "─"
    for r in range(H):
        grid[r][0] = "│"
    grid[0][0] = "┌"
    grid[0][W - 1] = "┐"
    grid[H - 1][0] = "└"
    grid[H - 1][W - 1] = "┘"

    # Plot titik (overlap -> angka)
    for x, y in pts:
        c, r = col_of(x), row_of(y)
        if grid[r][c] in " │─":
            grid[r][c] = "●"
        elif grid[r][c] != "●":
            grid[r][c] = "▓"

    lines = []
    if judul:
        lines.append(str(judul))
    lines.append(f"maks Y {lab_ymax}")
    for r in range(H):
        row = "".join(grid[r])
        if berwarna:
            row = row.replace("●", _ANSI[0] + "●" + _ANSI_RESET)
            row = row.replace("▓", _ANSI[1] + "▓" + _ANSI_RESET)
        lines.append(row)
    lines.append(f"min  Y {lab_ymin}")
    lines.append(f"X: {lab_xmin} .. {lab_xmax}")
    return "\n".join(lines)


def histogram(data, jumlah_bin=10, judul="", tinggi=12, satuan=""):
    """Histogram (ASCII, batang vertikal).

    Args:
        data: List nilai mentah yang akan dihitung frekuensinya.
        jumlah_bin: Jumlah bin/interval.
        judul: Judul chart.
        tinggi: Tinggi chart dalam baris.
    """
    values = [float(v) for v in data]
    if not values:
        return "(data kosong)"
    n_bins = max(1, int(jumlah_bin))
    lo, hi = min(values), max(values)
    if hi == lo:
        hi = lo + 1
    H = max(6, int(tinggi))
    counts = [0] * n_bins
    for v in values:
        idx = min(n_bins - 1, int((v - lo) / (hi - lo) * n_bins))
        counts[idx] += 1
    cmax = max(counts) or 1
    lines = []
    if judul:
        lines.append(str(judul))
    for level in range(H, 0, -1):
        row = ""
        for c in counts:
            bar_h = round(c / cmax * H)
            row += "█" if bar_h >= level else " "
            row += " "
        lines.append(row.rstrip())
    # Label rentang bin
    width = max(6, int(math.ceil((hi - lo) / n_bins / 10)) + 5)
    labels = []
    for i in range(n_bins):
        a = lo + i * (hi - lo) / n_bins
        b = lo + (i + 1) * (hi - lo) / n_bins
        labels.append(f"{_fmt(a)}-{_fmt(b)}")
    for i in range(n_bins):
        labels[i] = _truncate(labels[i], width)
    lines.append("".join(f"{l:<{width + 1}}" for l in labels).rstrip())
    total_str = f"n = {len(values)}"
    if satuan:
        total_str += " " + str(satuan)
    lines.append(total_str)
    return "\n".join(lines)


# =============================================================================
# Chart SVG
# =============================================================================


def batang_svg(data, label=None, judul="", warna=None, lebar=800, tinggi=430):
    """Chart batang vertikal (SVG).

    Args:
        data: List nilai / list pasangan / dict.
        label: Label untuk tiap bar.
        judul: Judul chart.
        warna: Warna hex tunggal atau list warna.
        lebar / tinggi: Ukuran kanvas SVG.
    """
    labels, values = _norm(data, label)
    if not values:
        return _svg_kosong(lebar, tinggi, judul)
    W, H = int(lebar), int(tinggi)
    L, R, T, B = 70, 30, 70, 60
    pw, ph = W - L - R, H - T - B
    colors = [warna] * len(values) if isinstance(warna, str) else (warna or _PALETTE)
    ticks = _nice_ticks(0, max(values), 4)
    ymax = ticks[-1] or 1

    def y(v):
        return T + ph - (v / ymax) * ph

    defs = []
    gids = []
    for c in colors:
        gid = _uid("bg")
        gids.append(gid)
        defs.append(
            f'<linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0%" stop-color="{c}"/>'
            f'<stop offset="100%" stop-color="{c}" stop-opacity="0.7"/>'
            f"</linearGradient>"
        )
    parts = [_svg_header(W, H), f'<rect width="100%" height="100%" fill="#ffffff"/>']
    if judul:
        parts.append(
            f'<text x="{W / 2}" y="32" text-anchor="middle" font-size="19" '
            f'font-weight="bold" fill="#0f172a">{_esc(judul)}</text>'
        )
    parts.append("<defs>" + "".join(defs) + "</defs>")
    # Gridline + label sumbu Y
    for t in ticks:
        parts.append(
            f'<line x1="{L}" y1="{y(t):.1f}" x2="{W - R}" y2="{y(t):.1f}" '
            f'stroke="#e2e8f0" stroke-width="1"/>'
        )
        parts.append(
            f'<text x="{L - 10}" y="{y(t) + 4:.1f}" text-anchor="end" font-size="12" '
            f'fill="#64748b">{_fmt(t)}</text>'
        )
    # Bar
    n = len(values)
    group_w = pw / n
    bar_w = min(58, group_w * 0.62)
    show_all_labels = n <= 20
    for i, v in enumerate(values):
        bx = L + i * group_w + (group_w - bar_w) / 2
        bh = max(1.0, ph - (y(v) - T)) if v > 0 else 0
        parts.append(
            f'<rect x="{bx:.1f}" y="{y(v):.1f}" width="{bar_w:.1f}" height="{bh:.1f}" '
            f'rx="6" fill="url(#{gids[i % len(gids)]})"/>'
        )
        parts.append(
            f'<text x="{bx + bar_w / 2:.1f}" y="{y(v) - 7:.1f}" text-anchor="middle" '
            f'font-size="12" font-weight="600" fill="#334155">{_fmt(v)}</text>'
        )
        if show_all_labels or i % 2 == 0:
            parts.append(
                f'<text x="{bx + bar_w / 2:.1f}" y="{H - B + 22}" text-anchor="middle" '
                f'font-size="11" fill="#64748b">{_esc(_truncate(labels[i], 12))}</text>'
            )
    # Sumbu dasar
    parts.append(
        f'<line x1="{L}" y1="{T + ph:.1f}" x2="{W - R}" y2="{T + ph:.1f}" '
        f'stroke="#cbd5e1" stroke-width="1.5"/>'
    )
    parts.append("</svg>")
    return "".join(parts)


def garis_svg(data, x=None, label=None, judul="", warna=None, lebar=800, tinggi=430):
    """Chart garis (SVG). Mendukung multi-seri.

    Args:
        data: List nilai, atau list berisi beberapa seri (list of lists).
        x: Nilai sumbu X (opsional; default 0,1,2,...).
        label: Nama seri (untuk legend).
        judul: Judul chart.
        warna: Warna hex tunggal atau list warna.
    """
    if data and isinstance(data[0], (list, tuple)):
        series = [list(s) for s in data]
        labels = list(label) if label else [f"Seri {i + 1}" for i in range(len(series))]
    else:
        series = [list(data)]
        labels = list(label) if label else [""]
    if not series or not series[0]:
        return _svg_kosong(lebar, tinggi, judul)
    W, H = int(lebar), int(tinggi)
    L, R, T, B = 70, 40, 70, 60
    pw, ph = W - L - R, H - T - B
    colors = [warna] * len(series) if isinstance(warna, str) else (warna or _PALETTE)

    n = len(series[0])
    if x is not None and len(x) != n:
        raise ValueError(f"Panjang 'x' ({len(x)}) harus sama dengan jumlah data ({n}).")
    for s in series:
        if len(s) != n:
            raise ValueError(f"Semua seri harus memiliki panjang yang sama ({n} titik).")
    if x is None:
        xs = list(range(n))
    else:
        xs = [float(v) for v in x]
    xs = [float(v) for v in xs]
    all_y = [float(v) for s in series for v in s]
    ymin, ymax = min(all_y), max(all_y)
    if ymax == ymin:
        ymax = ymin + 1
    ticks = _nice_ticks(ymin, ymax, 4)
    lo, hi = ticks[0], ticks[-1]

    def y(v):
        return T + ph - (v - lo) / (hi - lo) * ph

    def xpx(v):
        return L + (v - xs[0]) / (xs[-1] - xs[0]) * pw if xs[-1] != xs[0] else L + pw / 2

    parts = [_svg_header(W, H), f'<rect width="100%" height="100%" fill="#ffffff"/>']
    if judul:
        parts.append(
            f'<text x="{W / 2}" y="32" text-anchor="middle" font-size="19" '
            f'font-weight="bold" fill="#0f172a">{_esc(judul)}</text>'
        )
    # Legend (kanan atas)
    if len(series) > 1 and labels:
        ly = 55
        for i, name in enumerate(labels):
            parts.append(
                f'<rect x="{W - R - 130}" y="{ly - 11}" width="13" height="13" rx="3" '
                f'fill="{colors[i % len(colors)]}"/>'
            )
            parts.append(
                f'<text x="{W - R - 112}" y="{ly}" font-size="12" fill="#475569">'
                f"{_esc(name)}</text>"
            )
            ly += 20
    # Gridline + label sumbu Y
    for t in ticks:
        parts.append(
            f'<line x1="{L}" y1="{y(t):.1f}" x2="{W - R}" y2="{y(t):.1f}" '
            f'stroke="#e2e8f0" stroke-width="1"/>'
        )
        parts.append(
            f'<text x="{L - 10}" y="{y(t) + 4:.1f}" text-anchor="end" font-size="12" '
            f'fill="#64748b">{_fmt(t)}</text>'
        )
    # Label sumbu X (jika diberikan)
    if x is not None and n <= 30:
        step = max(1, n // 30)
        for i in range(0, n, step):
            parts.append(
                f'<text x="{xpx(xs[i]):.1f}" y="{H - B + 22}" text-anchor="middle" '
                f'font-size="11" fill="#64748b">{_esc(_truncate(x[i], 10))}</text>'
            )
    # Seri
    for si, s in enumerate(series):
        c = colors[si % len(colors)]
        pts = " ".join(f"{xpx(xs[i]):.1f},{y(float(v)):.1f}" for i, v in enumerate(s))
        # Area fill
        area = (
            f'M {xpx(xs[0]):.1f},{T + ph:.1f} L ' + " L ".join(
                f"{xpx(xs[i]):.1f},{y(float(v)):.1f}" for i, v in enumerate(s)
            ) + f" L {xpx(xs[-1]):.1f},{T + ph:.1f} Z"
        )
        parts.append(
            f'<path d="{area}" fill="{c}" opacity="0.08"/>'
        )
        parts.append(
            f'<polyline points="{pts}" fill="none" stroke="{c}" stroke-width="3" '
            f'stroke-linejoin="round" stroke-linecap="round"/>'
        )
        for i, v in enumerate(s):
            parts.append(
                f'<circle cx="{xpx(xs[i]):.1f}" cy="{y(float(v)):.1f}" r="4.5" '
                f'fill="#ffffff" stroke="{c}" stroke-width="2.5"/>'
            )
    parts.append("</svg>")
    return "".join(parts)


def kue_svg(data, label=None, judul="", warna=None, lebar=780, tinggi=440):
    """Chart pie / donat (SVG).

    Args:
        data: List nilai / list pasangan / dict.
        label: Label untuk tiap irisan.
        judul: Judul chart.
        warna: Warna hex tunggal atau list warna.
    """
    labels, values = _norm(data, label)
    if not values:
        return _svg_kosong(lebar, tinggi, judul)
    if any(v < 0 for v in values):
        raise ValueError("Chart pie tidak mendukung nilai negatif.")
    total = sum(values)
    if total <= 0:
        return _svg_kosong(lebar, tinggi, judul)
    W, H = int(lebar), int(tinggi)
    colors = [warna] * len(values) if isinstance(warna, str) else (warna or _PALETTE)
    cx, cy, r_out, r_in = 250, 235, 135, 62

    def arc(a0, a1, ro, ri):
        large = 1 if (a1 - a0) > math.pi else 0
        x0o, y0o = cx + ro * math.cos(a0), cy + ro * math.sin(a0)
        x1o, y1o = cx + ro * math.cos(a1), cy + ro * math.sin(a1)
        x0i, y0i = cx + ri * math.cos(a1), cy + ri * math.sin(a1)
        x1i, y1i = cx + ri * math.cos(a0), cy + ri * math.sin(a0)
        return (
            f"M {x0o:.2f},{y0o:.2f} A {ro:.2f},{ro:.2f} 0 {large} 1 {x1o:.2f},{y1o:.2f} "
            f"L {x0i:.2f},{y0i:.2f} A {ri:.2f},{ri:.2f} 0 {large} 0 {x1i:.2f},{y1i:.2f} Z"
        )

    parts = [_svg_header(W, H), f'<rect width="100%" height="100%" fill="#ffffff"/>']
    if judul:
        parts.append(
            f'<text x="{W / 2}" y="34" text-anchor="middle" font-size="19" '
            f'font-weight="bold" fill="#0f172a">{_esc(judul)}</text>'
        )
    # Irisan
    start = -math.pi / 2
    labels_pos = []
    for i, v in enumerate(values):
        frac = v / total
        end = start + frac * 2 * math.pi
        c = colors[i % len(colors)]
        parts.append(
            f'<path d="{arc(start, end, r_out, r_in)}" fill="{c}" stroke="#ffffff" '
            f'stroke-width="2.5"/>'
        )
        mid = (start + end) / 2
        if frac >= 0.07:
            lx = cx + (r_out + r_in) / 2 * math.cos(mid)
            ly = cy + (r_out + r_in) / 2 * math.sin(mid)
            parts.append(
                f'<text x="{lx:.1f}" y="{ly + 4:.1f}" text-anchor="middle" font-size="13" '
                f'font-weight="bold" fill="#ffffff">{frac * 100:.1f}%</text>'
            )
        labels_pos.append((c, labels[i] if i < len(labels) else str(i + 1), v, frac))
        start = end
    # Legend
    ly = 78
    for c, name, v, frac in labels_pos:
        parts.append(
            f'<rect x="{W - 220}" y="{ly - 12}" width="14" height="14" rx="3" fill="{c}"/>'
        )
        parts.append(
            f'<text x="{W - 198}" y="{ly}" font-size="13" fill="#1e293b" font-weight="600">'
            f"{_esc(_truncate(name, 16))}</text>"
        )
        parts.append(
            f'<text x="{W - 220}" y="{ly + 17}" font-size="12" fill="#64748b">'
            f"{_fmt(v)} · {frac * 100:.1f}%</text>"
        )
        ly += 36
    # Total di tengah donat
    parts.append(
        f'<text x="{cx}" y="{cy - 6}" text-anchor="middle" font-size="13" fill="#64748b">'
        f"total</text>"
    )
    parts.append(
        f'<text x="{cx}" y="{cy + 16}" text-anchor="middle" font-size="20" '
        f'font-weight="bold" fill="#0f172a">{_fmt(total)}</text>'
    )
    parts.append("</svg>")
    return "".join(parts)


def sebar_svg(x_data, y_data, judul="", label_x="X", label_y="Y", warna="#6366f1",
              lebar=800, tinggi=430):
    """Scatter plot (SVG).

    Args:
        x_data: List nilai sumbu X.
        y_data: List nilai sumbu Y.
        judul: Judul chart.
        label_x / label_y: Nama sumbu.
        warna: Warna titik.
    """
    pts = list(zip(list(x_data), list(y_data)))
    if not pts:
        return _svg_kosong(lebar, tinggi, judul)
    W, H = int(lebar), int(tinggi)
    L, R, T, B = 70, 40, 70, 60
    pw, ph = W - L - R, H - T - B
    X = [float(p[0]) for p in pts]
    Y = [float(p[1]) for p in pts]
    xmin, xmax = min(X), max(X)
    ymin, ymax = min(Y), max(Y)
    if xmax == xmin:
        xmax = xmin + 1
    if ymax == ymin:
        ymax = ymin + 1
    x_ticks = _nice_ticks(xmin, xmax, 5)
    y_ticks = _nice_ticks(ymin, ymax, 5)
    y_lo, y_hi = y_ticks[0], y_ticks[-1]
    x_lo, x_hi = x_ticks[0], x_ticks[-1]

    def y(v):
        return T + ph - (v - y_lo) / (y_hi - y_lo) * ph

    def xpx(v):
        return L + (v - x_lo) / (x_hi - x_lo) * pw

    parts = [_svg_header(W, H), f'<rect width="100%" height="100%" fill="#ffffff"/>']
    if judul:
        parts.append(
            f'<text x="{W / 2}" y="32" text-anchor="middle" font-size="19" '
            f'font-weight="bold" fill="#0f172a">{_esc(judul)}</text>'
        )
    for t in y_ticks:
        parts.append(
            f'<line x1="{L}" y1="{y(t):.1f}" x2="{W - R}" y2="{y(t):.1f}" '
            f'stroke="#e2e8f0" stroke-width="1"/>'
        )
        parts.append(
            f'<text x="{L - 10}" y="{y(t) + 4:.1f}" text-anchor="end" font-size="12" '
            f'fill="#64748b">{_fmt(t)}</text>'
        )
    for t in x_ticks:
        parts.append(
            f'<line x1="{xpx(t):.1f}" y1="{T}" x2="{xpx(t):.1f}" y2="{T + ph}" '
            f'stroke="#e2e8f0" stroke-width="1"/>'
        )
        parts.append(
            f'<text x="{xpx(t):.1f}" y="{H - B + 20}" text-anchor="middle" font-size="12" '
            f'fill="#64748b">{_fmt(t)}</text>'
        )
    # Label sumbu
    parts.append(
        f'<text x="{L + pw / 2}" y="{H - 8}" text-anchor="middle" font-size="13" '
        f'font-weight="600" fill="#334155">{_esc(label_x)}</text>'
    )
    parts.append(
        f'<text x="22" y="{T + ph / 2}" text-anchor="middle" font-size="13" '
        f'font-weight="600" fill="#334155" transform="rotate(-90 22 {T + ph / 2})">'
        f"{_esc(label_y)}</text>"
    )
    for px, py in pts:
        parts.append(
            f'<circle cx="{xpx(float(px)):.1f}" cy="{y(float(py)):.1f}" r="6" '
            f'fill="{warna}" opacity="0.75"/>'
        )
    parts.append("</svg>")
    return "".join(parts)


def histogram_svg(data, jumlah_bin=10, judul="", warna="#6366f1", lebar=800, tinggi=430):
    """Histogram (SVG).

    Args:
        data: List nilai mentah.
        jumlah_bin: Jumlah bin.
        judul: Judul chart.
        warna: Warna bar.
    """
    values = [float(v) for v in data]
    if not values:
        return _svg_kosong(lebar, tinggi, judul)
    W, H = int(lebar), int(tinggi)
    L, R, T, B = 70, 30, 70, 60
    pw, ph = W - L - R, H - T - B
    n_bins = max(1, int(jumlah_bin))
    lo, hi = min(values), max(values)
    if hi == lo:
        hi = lo + 1
    counts = [0] * n_bins
    for v in values:
        idx = min(n_bins - 1, int((v - lo) / (hi - lo) * n_bins))
        counts[idx] += 1
    cmax = max(counts) or 1
    ticks = _nice_ticks(0, cmax, 4)
    ymax = ticks[-1] or 1

    def y(c):
        return T + ph - (c / ymax) * ph

    parts = [_svg_header(W, H), f'<rect width="100%" height="100%" fill="#ffffff"/>']
    if judul:
        parts.append(
            f'<text x="{W / 2}" y="32" text-anchor="middle" font-size="19" '
            f'font-weight="bold" fill="#0f172a">{_esc(judul)}</text>'
        )
    hgid = _uid("hgrad")
    parts.append(
        f'<defs><linearGradient id="{hgid}" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0%" stop-color="{warna}"/>'
        f'<stop offset="100%" stop-color="{warna}" stop-opacity="0.7"/>'
        f"</linearGradient></defs>"
    )
    for t in ticks:
        parts.append(
            f'<line x1="{L}" y1="{y(t):.1f}" x2="{W - R}" y2="{y(t):.1f}" '
            f'stroke="#e2e8f0" stroke-width="1"/>'
        )
        parts.append(
            f'<text x="{L - 10}" y="{y(t) + 4:.1f}" text-anchor="end" font-size="12" '
            f'fill="#64748b">{_fmt(t)}</text>'
        )
    group_w = pw / n_bins
    bar_w = min(58, group_w * 0.68)
    show_all = n_bins <= 24
    for i, c in enumerate(counts):
        bx = L + i * group_w + (group_w - bar_w) / 2
        bh = max(1.0, ph - (y(c) - T)) if c > 0 else 0
        parts.append(
            f'<rect x="{bx:.1f}" y="{y(c):.1f}" width="{bar_w:.1f}" height="{bh:.1f}" '
            f'rx="5" fill="url(#{hgid})"/>'
        )
        if c > 0:
            parts.append(
                f'<text x="{bx + bar_w / 2:.1f}" y="{y(c) - 7:.1f}" text-anchor="middle" '
                f'font-size="11" font-weight="600" fill="#334155">{c}</text>'
            )
        if show_all or i % 2 == 0:
            a = lo + i * (hi - lo) / n_bins
            b = lo + (i + 1) * (hi - lo) / n_bins
            parts.append(
                f'<text x="{bx + bar_w / 2:.1f}" y="{H - B + 22}" text-anchor="middle" '
                f'font-size="10" fill="#64748b">{_esc(_truncate(f"{_fmt(a)}-{_fmt(b)}", 10))}</text>'
            )
    parts.append("</svg>")
    return "".join(parts)


# =============================================================================
# Export ke file
# =============================================================================


def simpan_svg(nama_file, svg):
    """Simpan string SVG ke file. Mengembalikan nama file."""
    with open(nama_file, "w", encoding="utf-8") as f:
        f.write(svg)
    return nama_file


def simpan_txt(nama_file, teks):
    """Simpan teks (chart ASCII) ke file. Mengembalikan nama file."""
    with open(nama_file, "w", encoding="utf-8") as f:
        f.write(str(teks))
    return nama_file


def simpan_html(nama_file, svg_list, judul="Laporan Data BroLang"):
    """Simpan satu atau beberapa chart SVG ke halaman HTML yang rapi.

    Args:
        nama_file: Path file HTML tujuan.
        svg_list: Satu string SVG, atau list berisi beberapa SVG.
        judul: Judul halaman.
    """
    if isinstance(svg_list, str):
        svg_list = [svg_list]
    cards = "\n".join(f'<div class="kartu">{s}</div>' for s in svg_list)
    html = f"""<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{_esc(judul)}</title>
<style>
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; padding: 40px 16px; background: #f1f5f9;
          font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; }}
  h1 {{ text-align: center; color: #0f172a; font-size: 28px; margin: 0 0 8px; }}
  .sub {{ text-align: center; color: #94a3b8; font-size: 14px; margin-bottom: 28px; }}
  .kartu {{ background: #ffffff; border-radius: 16px; max-width: 920px;
            margin: 22px auto; padding: 18px;
            box-shadow: 0 4px 24px rgba(15, 23, 42, 0.08); }}
  .kartu svg {{ width: 100%; height: auto; display: block; }}
  footer {{ text-align: center; color: #94a3b8; font-size: 13px; margin-top: 34px; }}
</style>
</head>
<body>
<h1>{_esc(judul)}</h1>
<div class="sub">Dibuat dengan BroLang &mdash; modul <code>visualisasi</code></div>
{cards}
<footer>📊 BroLang &bull; data visualization</footer>
</body>
</html>"""
    with open(nama_file, "w", encoding="utf-8") as f:
        f.write(html)
    return nama_file


# =============================================================================
# GUI (Pygame) — tampilkan chart di jendela native seperti game
# =============================================================================

try:
    import pygame as _pygame
except ImportError:
    _pygame = None

_GUI_INSTALL_HINT = "Jalankan: pip install pygame-ce"

# Warna tema gelap ala game
_BG = (13, 18, 32)
_CARD = (24, 32, 54)
_GRID = (42, 54, 82)
_TEXT = (226, 232, 240)
_MUTED = (148, 163, 184)
_LINE = (100, 116, 139)
_ACCENT = (99, 102, 241)

_JUDUL_BY_JENIS = {
    "batang": "Chart Batang",
    "garis": "Chart Garis",
    "kue": "Chart Pie",
    "sebar": "Scatter Plot",
    "histogram": "Histogram",
}

_PG_CHAR_MAP = {
    "…": "...", "—": "-", "─": "-", "│": "|", "┌": "+", "┐": "+",
    "└": "+", "┘": "+", "●": "o", "█": "#", "▓": "#", "▒": "#",
    "░": ".", "▄": "#", "▌": "#", "▐": "#", "▀": "#", "✓": "OK",
    "✔": "OK", "✗": "X", "•": "-", "°": " deg", "±": "+/-", "×": "x",
    "÷": "/", "→": "->", "←": "<-", "↑": "^", "↓": "v",
    "“": '"', "”": '"', "‘": "'", "’": "'",
    "é": "e", "è": "e", "ê": "e", "à": "a", "á": "a", "â": "a",
    "ü": "u", "ö": "o", "ñ": "n", "ç": "c", "í": "i", "ó": "o",
}


def _pygame_safe(text) -> str:
    """Ganti karakter non-ASCII agar bisa dirender font bawaan pygame."""
    if not isinstance(text, str):
        text = str(text)
    out = []
    for ch in text:
        if ord(ch) < 128:
            out.append(ch)
        else:
            out.append(_PG_CHAR_MAP.get(ch, "?"))
    return "".join(out)


def _butuh_pygame():
    if _pygame is None:
        raise RuntimeError(
            f"Tampilan GUI visualisasi butuh pygame. {_GUI_INSTALL_HINT}"
        )
    return _pygame


def _hex_color(c, fallback="#6366f1"):
    """Konversi warna hex '#rrggbb' atau tuple (r, g, b) ke tuple RGB."""
    if isinstance(c, (list, tuple)) and len(c) >= 3:
        try:
            return (int(c[0]) % 256, int(c[1]) % 256, int(c[2]) % 256)
        except (TypeError, ValueError):
            pass
    if isinstance(c, str) and len(c) == 7 and c.startswith("#"):
        try:
            return tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))
        except ValueError:
            pass
    return _hex_color(fallback)


def _colors_for(n, warna):
    """Kembalikan list berisi n warna RGB dari warna tunggal / list / palet."""
    n = max(1, int(n))
    if warna is None:
        pal = [_hex_color(p) for p in _PALETTE]
        return [pal[i % len(pal)] for i in range(n)]
    # tuple RGB tunggal (mis. (255, 0, 0)) vs list warna (mis. ["#f00", "#0f0"])
    is_rgb_triple = (isinstance(warna, (list, tuple)) and len(warna) == 3
                     and all(isinstance(c, (int, float)) for c in warna))
    if isinstance(warna, (list, tuple)) and not is_rgb_triple:
        resolved = [_hex_color(c) for c in warna] or [_hex_color(_PALETTE[0])]
        return [resolved[i % len(resolved)] for i in range(n)]
    c = _hex_color(warna)
    return [c] * n


def _norm_spec(spec):
    """Validasi spec chart dict -> (jenis, spec)."""
    if not isinstance(spec, dict):
        raise ValueError("Spec chart harus berupa objek {jenis, data, ...}.")
    jenis = spec.get("jenis") or spec.get("tipe")
    if jenis not in ("batang", "garis", "kue", "sebar", "histogram"):
        raise ValueError(
            f"Jenis chart tidak dikenal: '{jenis}'. "
            "Pilih: batang, garis, kue, sebar, histogram."
        )
    if jenis != "sebar" and "data" not in spec:
        raise ValueError(f"Spec chart '{jenis}' butuh kunci 'data'.")
    return jenis, spec


# --- Geometry murni (bisa di-test tanpa pygame) ---


def _batang_geom(values, labels, rect, warna):
    """Hitung geometri bar chart -> dict primitif drawing."""
    x0, y0, w, h = rect
    ticks = _nice_ticks(0, max(values), 4)
    ymax = ticks[-1] or 1

    def Y(v):
        return y0 + h - (v / ymax) * h

    n = len(values)
    group = w / n
    bw = min(56, group * 0.62)
    colors = _colors_for(n, warna)
    bars = []
    for i, v in enumerate(values):
        bx = x0 + i * group + (group - bw) / 2
        bh = max(1.0, h - (Y(v) - y0)) if v > 0 else 0
        bars.append({
            "rect": (bx, Y(v), bw, bh),
            "value": v,
            "label": labels[i] if i < len(labels) else str(i + 1),
            "color": colors[i % len(colors)],
        })
    return {"bars": bars, "ticks": [(Y(t), t) for t in ticks], "baseline": y0 + h}


def _garis_geom(series, xs, labels, rect, warna):
    """Hitung geometri line chart (multi-seri) -> dict primitif drawing."""
    x0, y0, w, h = rect
    labels = labels or []
    n = len(series[0])
    for s in series:
        if len(s) != n:
            raise ValueError("Semua seri harus memiliki panjang yang sama.")
    all_y = [float(v) for s in series for v in s]
    vmin, vmax = min(all_y), max(all_y)
    if vmax == vmin:
        vmax = vmin + 1
    ticks = _nice_ticks(vmin, vmax, 4)
    lo, hi = ticks[0], ticks[-1]

    def X(v):
        return x0 + (v - xs[0]) / (xs[-1] - xs[0]) * w if xs[-1] != xs[0] else x0 + w / 2

    def Y(v):
        return y0 + h - (v - lo) / (hi - lo) * h

    colors = _colors_for(len(series), warna)
    out = []
    for si, s in enumerate(series):
        pts = [(X(float(xs[i])), Y(float(v)), float(v)) for i, v in enumerate(s)]
        out.append({
            "points": pts,
            "color": colors[si % len(colors)],
            "label": labels[si] if si < len(labels) else f"Seri {si + 1}",
        })
    return {"series": out, "ticks": [(Y(t), t) for t in ticks], "baseline": y0 + h}


def _kue_geom(values, labels, rect, warna):
    """Hitung geometri pie/donut -> dict primitif drawing."""
    if any(v < 0 for v in values):
        raise ValueError("Chart pie tidak mendukung nilai negatif.")
    total = sum(values)
    if total <= 0:
        raise ValueError("Chart pie butuh total nilai lebih dari 0.")
    cx = rect[0] + rect[2] / 2
    cy = rect[1] + rect[3] / 2
    r_out = min(rect[2], rect[3]) / 2 - 12
    r_in = max(10.0, r_out * 0.42)
    colors = _colors_for(len(values), warna)
    slices = []
    start = -math.pi / 2
    for i, v in enumerate(values):
        frac = v / total
        end = start + frac * 2 * math.pi
        slices.append({
            "start": start, "end": end, "frac": frac, "value": v,
            "color": colors[i % len(colors)],
            "label": labels[i] if i < len(labels) else str(i + 1),
        })
        start = end
    return {"cx": cx, "cy": cy, "r_out": r_out, "r_in": r_in,
            "slices": slices, "total": total}


def _sebar_geom(xs, ys, rect, warna):
    """Hitung geometri scatter plot -> dict primitif drawing."""
    x0, y0, w, h = rect
    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)
    if xmax == xmin:
        xmax = xmin + 1
    if ymax == ymin:
        ymax = ymin + 1
    xt = _nice_ticks(xmin, xmax, 5)
    yt = _nice_ticks(ymin, ymax, 5)
    x_lo, x_hi = xt[0], xt[-1]
    y_lo, y_hi = yt[0], yt[-1]

    def X(v):
        return x0 + (v - x_lo) / (x_hi - x_lo) * w

    def Y(v):
        return y0 + h - (v - y_lo) / (y_hi - y_lo) * h

    color = _hex_color(warna)
    pts = [(X(xs[i]), Y(ys[i]), float(xs[i]), float(ys[i])) for i in range(len(xs))]
    return {"points": pts, "color": color,
            "x_ticks": [(X(t), t) for t in xt], "y_ticks": [(Y(t), t) for t in yt]}


def _hist_geom(counts, bin_labels, rect, warna):
    """Hitung geometri histogram -> dict primitif drawing."""
    x0, y0, w, h = rect
    cmax = max(counts) or 1
    ticks = _nice_ticks(0, cmax, 4)
    ymax = ticks[-1] or 1

    def Y(c):
        return y0 + h - (c / ymax) * h

    n = len(counts)
    group = w / n
    bw = min(54, group * 0.68)
    color = _hex_color(warna)
    bars = []
    for i, c in enumerate(counts):
        bx = x0 + i * group + (group - bw) / 2
        bh = max(1.0, h - (Y(c) - y0)) if c > 0 else 0
        bars.append({"rect": (bx, Y(c), bw, bh), "count": c,
                     "label": bin_labels[i] if i < len(bin_labels) else str(i + 1)})
    return {"bars": bars, "color": color,
            "ticks": [(Y(t), t) for t in ticks], "baseline": y0 + h}


def _bin_data(values, n_bins):
    """Binning data mentah -> (counts, label_bins)."""
    n_bins = max(1, int(n_bins))
    lo, hi = min(values), max(values)
    if hi == lo:
        hi = lo + 1
    counts = [0] * n_bins
    for v in values:
        idx = min(n_bins - 1, int((v - lo) / (hi - lo) * n_bins))
        counts[idx] += 1
    labels = []
    for i in range(n_bins):
        a = lo + i * (hi - lo) / n_bins
        b = lo + (i + 1) * (hi - lo) / n_bins
        labels.append(f"{_fmt(a)}-{_fmt(b)}")
    return counts, labels


# --- Rendering pygame ---


def _tooltip_pg(pg, screen, fonts, x, y, text):
    """Gambar kotak tooltip kecil di dekat posisi (x, y)."""
    surf = fonts[13].render(_pygame_safe(text), True, (255, 255, 255))
    bw, bh = surf.get_width() + 14, surf.get_height() + 8
    bx = max(4, min(x + 12, screen.get_width() - bw - 4))
    by = max(4, y - bh - 10)
    box = pg.Surface((bw, bh), pg.SRCALPHA)
    box.fill((15, 23, 42, 235))
    screen.blit(box, (bx, by))
    pg.draw.rect(screen, _ACCENT, (bx, by, bw, bh), 1)
    screen.blit(surf, (bx + 7, by + 4))


def _draw_axis_pg(pg, screen, fonts, rect, ticks, axis="y"):
    """Gambar gridline + label sumbu."""
    x0, y0, w, h = rect
    for pos, val in ticks:
        if axis == "y":
            pg.draw.line(screen, _GRID, (x0, pos), (x0 + w, pos), 1)
            s = fonts[13].render(_fmt(val), True, _MUTED)
            screen.blit(s, (x0 - s.get_width() - 6, pos - s.get_height() // 2))
        else:
            pg.draw.line(screen, _GRID, (pos, y0), (pos, y0 + h), 1)
            s = fonts[13].render(_fmt(val), True, _MUTED)
            screen.blit(s, (pos - s.get_width() // 2, y0 + h + 4))


def _draw_legend_pg(pg, screen, fonts, items, x, y, max_w, line_h=22):
    """Gambar legend berisi (warna, label, extra) dengan wrapping."""
    cx, cy = x, y
    for color, label, extra in items:
        sw = fonts[13].size(f" {_pygame_safe(label)} {_pygame_safe(extra)}")[0] + 20
        if cx + sw > x + max_w and cx > x:
            cx = x
            cy += line_h
        pg.draw.rect(screen, color, (int(cx), int(cy - 9), 12, 12), border_radius=3)
        s = fonts[13].render(_pygame_safe(f"{label} {extra}"), True, _MUTED)
        screen.blit(s, (int(cx + 17), int(cy - s.get_height() // 2)))
        cx += sw + 8


def _draw_batang_pg(pg, screen, fonts, rect, geom, t, mouse):
    x0, y0, w, h = rect
    _draw_axis_pg(pg, screen, fonts, rect, geom["ticks"], "y")
    pg.draw.line(screen, _LINE, (x0, geom["baseline"]), (x0 + w, geom["baseline"]), 1)
    hover = None
    for b in geom["bars"]:
        bx, by, bw, bh = b["rect"]
        bh2 = max(0.0, bh * t)
        y2 = geom["baseline"] - bh2
        if bh2 > 0:
            pg.draw.rect(screen, b["color"], (int(bx), int(y2), int(bw), int(bh2)), border_radius=5)
        if t > 0.5:
            s = fonts[15].render(_fmt(b["value"]), True, _TEXT)
            screen.blit(s, (int(bx + bw / 2 - s.get_width() / 2), int(y2 - s.get_height() - 3)))
        s = fonts[13].render(_pygame_safe(_truncate(b["label"], 12)), True, _MUTED)
        screen.blit(s, (int(bx + bw / 2 - s.get_width() / 2), int(geom["baseline"] + 6)))
        if mouse and bx <= mouse[0] <= bx + bw and y2 <= mouse[1] <= geom["baseline"]:
            hover = (int(mouse[0]), int(mouse[1] - 16), f"{b['label']} : {_fmt(b['value'])}")
    if hover:
        _tooltip_pg(pg, screen, fonts, hover[0], hover[1], hover[2])


def _draw_garis_pg(pg, screen, fonts, rect, geom, t, mouse):
    x0, y0, w, h = rect
    _draw_axis_pg(pg, screen, fonts, rect, geom["ticks"], "y")
    hover = None
    for si, ser in enumerate(geom["series"]):
        pts = ser["points"]
        color = ser["color"]
        n_full = max(1, int(len(pts) * t))
        visible = pts[:n_full]
        if len(visible) >= 2:
            alpha_surf = pg.Surface((w, h), pg.SRCALPHA)
            base = geom["baseline"] - y0
            poly = ([(int(pts[0][0] - x0), int(base))]
                    + [(int(p[0] - x0), int(p[1] - y0)) for p in visible]
                    + [(int(visible[-1][0] - x0), int(base))])
            pg.draw.polygon(alpha_surf, (*color, 26), poly)
            screen.blit(alpha_surf, (x0, y0))
            pg.draw.lines(screen, color, False,
                          [(int(p[0]), int(p[1])) for p in visible], 3)
        for i, p in enumerate(visible):
            r = 5 if i == n_full - 1 else 3
            pg.draw.circle(screen, color, (int(p[0]), int(p[1])), r)
            pg.draw.circle(screen, _BG, (int(p[0]), int(p[1])), r, 1)
        if mouse:
            for p in pts:
                dx = mouse[0] - p[0]
                dy = mouse[1] - p[1]
                if dx * dx + dy * dy <= 169:
                    hover = (int(p[0]), int(p[1] - 16),
                             f"{ser['label']} : {_fmt(p[2])}")
                    break
        if hover:
            break
    if hover:
        _tooltip_pg(pg, screen, fonts, hover[0], hover[1], hover[2])


def _draw_kue_pg(pg, screen, fonts, rect, geom, t, mouse):
    cx, cy = int(geom["cx"]), int(geom["cy"])
    r_out, r_in = geom["r_out"], geom["r_in"]
    ring_rect = (cx - r_out, cy - r_out, 2 * r_out, 2 * r_out)
    width = max(4, int(r_out - r_in))
    hover = None
    for sl in geom["slices"]:
        end_angle = sl["start"] + (sl["end"] - sl["start"]) * t
        pg.draw.arc(screen, sl["color"], ring_rect, sl["start"], end_angle, width)
        if mouse and hover is None:
            dx = mouse[0] - cx
            dy = mouse[1] - cy
            dist = math.hypot(dx, dy)
            if r_in <= dist <= r_out + 2:
                rel = (math.atan2(dy, dx) + math.pi / 2) % (2 * math.pi)
                span = (end_angle - sl["start"]) % (2 * math.pi)
                if rel <= span + 0.01:
                    hover = (mouse[0], mouse[1] - 16,
                             f"{sl['label']} : {_fmt(sl['value'])} ({sl['frac'] * 100:.1f}%)")
    s = fonts[18].render("Total", True, _MUTED)
    screen.blit(s, (cx - s.get_width() // 2, cy - 18))
    s = fonts[26].render(_fmt(geom["total"]), True, _TEXT)
    screen.blit(s, (cx - s.get_width() // 2, cy + 4))
    items = [(sl["color"], sl["label"], f"{_fmt(sl['value'])} ({sl['frac'] * 100:.1f}%)")
             for sl in geom["slices"]]
    _draw_legend_pg(pg, screen, fonts, items, rect[0] + 6, rect[1] + rect[3] - 36,
                    rect[2] - 12)
    if hover:
        _tooltip_pg(pg, screen, fonts, hover[0], hover[1], hover[2])


def _draw_sebar_pg(pg, screen, fonts, rect, geom, t, mouse):
    _draw_axis_pg(pg, screen, fonts, rect, geom["y_ticks"], "y")
    _draw_axis_pg(pg, screen, fonts, rect, geom["x_ticks"], "x")
    hover = None
    for px, py, vx, vy in geom["points"]:
        r = max(2.0, 6.0 * t)
        pg.draw.circle(screen, geom["color"], (int(px), int(py)), int(r))
        if mouse and hover is None:
            dx = mouse[0] - px
            dy = mouse[1] - py
            if dx * dx + dy * dy <= 100:
                hover = (int(px), int(py - 16), f"({_fmt(vx)}, {_fmt(vy)})")
    if hover:
        _tooltip_pg(pg, screen, fonts, hover[0], hover[1], hover[2])


def _draw_hist_pg(pg, screen, fonts, rect, geom, t, mouse):
    x0, y0, w, h = rect
    _draw_axis_pg(pg, screen, fonts, rect, geom["ticks"], "y")
    pg.draw.line(screen, _LINE, (x0, geom["baseline"]), (x0 + w, geom["baseline"]), 1)
    hover = None
    for b in geom["bars"]:
        bx, by, bw, bh = b["rect"]
        bh2 = max(0.0, bh * t)
        y2 = geom["baseline"] - bh2
        if bh2 > 0:
            pg.draw.rect(screen, geom["color"], (int(bx), int(y2), int(bw), int(bh2)),
                         border_radius=4)
        if b["count"] > 0 and t > 0.5:
            s = fonts[15].render(str(b["count"]), True, _TEXT)
            screen.blit(s, (int(bx + bw / 2 - s.get_width() / 2), int(y2 - s.get_height() - 3)))
        s = fonts[11].render(_pygame_safe(_truncate(b["label"], 10)), True, _MUTED)
        screen.blit(s, (int(bx + bw / 2 - s.get_width() / 2), int(geom["baseline"] + 6)))
        if mouse and bx <= mouse[0] <= bx + bw and y2 <= mouse[1] <= geom["baseline"]:
            hover = (int(mouse[0]), int(mouse[1] - 16),
                     f"{b['label']} : {b['count']}")
    if hover:
        _tooltip_pg(pg, screen, fonts, hover[0], hover[1], hover[2])


def _chart_inner_rect(card):
    x, y, w, h = card
    return (x + 64, y + 44, w - 92, h - 92)


def _draw_chart_pg(pg, screen, fonts, card, jenis, spec, t, mouse):
    inner = _chart_inner_rect(card)
    if jenis == "batang":
        labels, values = _norm(spec.get("data", []), spec.get("label"))
        if not values:
            return
        _draw_batang_pg(pg, screen, fonts, inner, _batang_geom(values, labels, inner, spec.get("warna")), t, mouse)
    elif jenis == "garis":
        data = spec.get("data", [])
        if data and isinstance(data[0], (list, tuple)):
            series = [list(s) for s in data]
        else:
            series = [list(data)]
        if not series or not series[0]:
            return
        xv = spec.get("x")
        xs = list(xv) if xv is not None else list(range(len(series[0])))
        if xv is not None and len(xs) != len(series[0]):
            raise ValueError("Panjang 'x' harus sama dengan jumlah data.")
        _draw_garis_pg(pg, screen, fonts, inner,
                       _garis_geom(series, xs, spec.get("label"), inner, spec.get("warna")),
                       t, mouse)
    elif jenis == "kue":
        labels, values = _norm(spec.get("data", []), spec.get("label"))
        if not values:
            return
        _draw_kue_pg(pg, screen, fonts, inner, _kue_geom(values, labels, inner, spec.get("warna")), t, mouse)
    elif jenis == "sebar":
        data = spec.get("data")
        if data and isinstance(data[0], (list, tuple)) and len(data[0]) == 2:
            pairs = list(data)
            xs = [float(p[0]) for p in pairs]
            ys = [float(p[1]) for p in pairs]
        else:
            xs = [float(v) for v in (spec.get("x") or [])]
            ys = [float(v) for v in (spec.get("y") or [])]
        if not xs:
            return
        if len(xs) != len(ys):
            raise ValueError("Scatter butuh 'x' dan 'y' dengan panjang sama.")
        _draw_sebar_pg(pg, screen, fonts, inner, _sebar_geom(xs, ys, inner, spec.get("warna")), t, mouse)
    elif jenis == "histogram":
        data = [float(v) for v in spec.get("data", [])]
        if not data:
            return
        counts, bin_labels = _bin_data(data, spec.get("jumlah_bin", 10))
        _draw_hist_pg(pg, screen, fonts, inner, _hist_geom(counts, bin_labels, inner, spec.get("warna")), t, mouse)


def _help_overlay_pg(pg, screen, fonts):
    w, h = screen.get_size()
    overlay = pg.Surface((w, h), pg.SRCALPHA)
    overlay.fill((8, 12, 24, 225))
    screen.blit(overlay, (0, 0))
    lines = [
        "NAVIGASI",
        "  Panah kiri/kanan   : ganti chart",
        "  Tombol 1-9         : lompat ke chart tertentu",
        "  F                  : fullscreen",
        "  S                  : simpan screenshot (PNG)",
        "  H                  : sembunyikan bantuan ini",
        "  ESC / Q            : tutup jendela",
        "",
        "Tips: arahkan mouse ke chart untuk melihat nilai detail.",
    ]
    y = int(h * 0.22)
    for line in lines:
        bold = line == lines[0]
        s = fonts[26 if bold else 15].render(line, True, _TEXT if bold else _MUTED)
        screen.blit(s, (w // 2 - s.get_width() // 2, y))
        y += 30 if not bold else 40


def tampilkan_jendela(charts, judul="Visualisasi Data", lebar=1100, tinggi=700,
                      layar_penuh=False):
    """Tampilkan satu atau beberapa chart di jendela pygame (blokir sampai ditutup).

    Args:
        charts: Spec chart tunggal, atau list spec chart.
                Spec: {"jenis": "batang|garis|kue|sebar|histogram", "data": ...,
                        "label": ..., "judul": ..., "warna": ...}
        judul: Judul jendela.
        lebar / tinggi: Ukuran jendela.
        layar_penuh: Mulai dalam mode fullscreen.

    Kontrol:
        Panah kiri/kanan  : ganti chart
        Tombol 1-9        : lompat ke chart
        F                 : fullscreen
        S                 : screenshot PNG
        H                 : bantuan
        ESC / Q           : tutup
    """
    pg = _butuh_pygame()
    if isinstance(charts, dict):
        charts = [charts]
    elif not isinstance(charts, (list, tuple)):
        raise ValueError("charts harus berupa spec chart atau list spec chart.")
    if not charts:
        raise ValueError("Minimal satu chart untuk ditampilkan.")
    specs = [_norm_spec(c) for c in charts]

    pg.init()
    flags = pg.FULLSCREEN | pg.SCALED if layar_penuh else 0
    screen = pg.display.set_mode((int(lebar), int(tinggi)), flags)
    pg.display.set_caption(f"BroLang — {_pygame_safe(judul)}")
    fonts = _make_fonts(pg)

    idx = 0
    show_time = pg.time.get_ticks()
    try:
        _run_gui_loop(pg, screen, fonts, specs, judul, lebar, tinggi, idx, show_time,
                      layar_penuh)
    finally:
        pg.quit()


_FONT_SIZES = (11, 13, 15, 18, 22, 26, 28)


def _make_fonts(pg):
    """Buat dict font pygame untuk semua ukuran yang dipakai."""
    return {sz: pg.font.Font(None, sz) for sz in _FONT_SIZES}


def _draw_frame(pg, screen, fonts, specs, judul, lebar, tinggi, idx, now, show_time,
                mouse, show_help):
    """Gambar satu frame penuh: header, kartu chart, footer, help overlay."""
    screen.fill(_BG)
    # Header
    s = fonts[28].render(_pygame_safe(str(judul)), True, _TEXT)
    screen.blit(s, (24, 14))
    s = fonts[15].render(
        _pygame_safe(f"{idx + 1}/{len(specs)}  -  {specs[idx][0].upper()}"),
        True, _MUTED,
    )
    screen.blit(s, (lebar - s.get_width() - 24, 22))
    pg.draw.line(screen, _GRID, (24, 62), (lebar - 24, 62), 1)
    # Kartu chart
    card = (24, 74, lebar - 48, tinggi - 74 - 46)
    pg.draw.rect(screen, _CARD, card, border_radius=14)
    jenis, spec = specs[idx]
    t_title = str(spec.get("judul") or _JUDUL_BY_JENIS[jenis])
    s = fonts[22].render(_pygame_safe(t_title), True, _TEXT)
    screen.blit(s, (card[0] + 20, card[1] + 10))
    t = min(1.0, (now - show_time) / 900)
    t = t * t * (3 - 2 * t)  # smoothstep
    _draw_chart_pg(pg, screen, fonts, card, jenis, spec, t, mouse)
    # Footer hints
    hints = _pygame_safe("<-> chart    1-9 lompat    F fullscreen    S screenshot    H bantuan    ESC tutup")
    s = fonts[13].render(hints, True, _LINE)
    screen.blit(s, (24, tinggi - 24))
    if show_help:
        _help_overlay_pg(pg, screen, fonts)


def _run_gui_loop(pg, screen, fonts, specs, judul, lebar, tinggi, idx, show_time,
                  layar_penuh=False):
    """Loop utama jendela GUI (dipisah agar cleanup dengan try/finally rapi)."""
    clock = pg.time.Clock()
    show_help = False
    fullscreen = bool(layar_penuh)
    running = True
    while running:
        now = pg.time.get_ticks()
        mouse = pg.mouse.get_pos()
        for ev in pg.event.get():
            if ev.type == pg.QUIT:
                running = False
            elif ev.type == pg.KEYDOWN:
                if ev.key in (pg.K_ESCAPE, pg.K_q):
                    running = False
                elif ev.key == pg.K_RIGHT and idx < len(specs) - 1:
                    idx += 1
                    show_time = now
                elif ev.key == pg.K_LEFT and idx > 0:
                    idx -= 1
                    show_time = now
                elif pg.K_1 <= ev.key <= pg.K_9:
                    n = ev.key - pg.K_0
                    if 1 <= n <= len(specs):
                        idx = n - 1
                        show_time = now
                elif ev.key == pg.K_h:
                    show_help = not show_help
                elif ev.key == pg.K_f:
                    fullscreen = not fullscreen
                    screen = pg.display.set_mode(
                        (int(lebar), int(tinggi)),
                        pg.FULLSCREEN | pg.SCALED if fullscreen else 0,
                    )
                elif ev.key == pg.K_s:
                    fn = f"visualisasi_chart_{idx + 1}.png"
                    pg.image.save(screen, fn)
                    print(f"[visualisasi] Screenshot disimpan: {fn}")

        _draw_frame(pg, screen, fonts, specs, judul, lebar, tinggi, idx, now,
                    show_time, mouse, show_help)
        pg.display.flip()
        clock.tick(60)


# --- Convenience: tampilkan satu chart langsung ---


def tampilkan_batang(data, label=None, judul="", warna=None, satuan="", lebar=1100, tinggi=700):
    """Tampilkan chart batang di jendela pygame."""
    return tampilkan_jendela(
        [{"jenis": "batang", "data": data, "label": label, "judul": judul,
          "warna": warna, "satuan": satuan}],
        judul=judul or "Chart Batang", lebar=lebar, tinggi=tinggi,
    )


def tampilkan_garis(data, x=None, label=None, judul="", warna=None, lebar=1100, tinggi=700):
    """Tampilkan chart garis di jendela pygame (mendukung multi-seri)."""
    return tampilkan_jendela(
        [{"jenis": "garis", "data": data, "x": x, "label": label,
          "judul": judul, "warna": warna}],
        judul=judul or "Chart Garis", lebar=lebar, tinggi=tinggi,
    )


def tampilkan_kue(data, label=None, judul="", warna=None, lebar=1100, tinggi=700):
    """Tampilkan chart pie/donat di jendela pygame."""
    return tampilkan_jendela(
        [{"jenis": "kue", "data": data, "label": label, "judul": judul,
          "warna": warna}],
        judul=judul or "Chart Pie", lebar=lebar, tinggi=tinggi,
    )


def tampilkan_sebar(x_data, y_data, judul="", warna=None, lebar=1100, tinggi=700):
    """Tampilkan scatter plot di jendela pygame."""
    return tampilkan_jendela(
        [{"jenis": "sebar", "x": list(x_data), "y": list(y_data),
          "judul": judul, "warna": warna}],
        judul=judul or "Scatter Plot", lebar=lebar, tinggi=tinggi,
    )


def tampilkan_histogram(data, jumlah_bin=10, judul="", warna=None, lebar=1100, tinggi=700):
    """Tampilkan histogram di jendela pygame."""
    return tampilkan_jendela(
        [{"jenis": "histogram", "data": list(data), "jumlah_bin": jumlah_bin,
          "judul": judul, "warna": warna}],
        judul=judul or "Histogram", lebar=lebar, tinggi=tinggi,
    )


# --- Render chart ke PNG tanpa membuka jendela ---


def simpan_png(nama_file, spec, lebar=1100, tinggi=700):
    """Render satu chart ke file PNG (tanpa membuka jendela).

    Args:
        nama_file: Path file PNG tujuan.
        spec: Spec chart dict, misal {"jenis": "batang", "data": [1, 2, 3]}.
        lebar / tinggi: Ukuran gambar.
    """
    pg = _butuh_pygame()
    jenis, s = _norm_spec(spec)
    pg.init()
    try:
        screen = pg.Surface((int(lebar), int(tinggi)))
        fonts = _make_fonts(pg)
        screen.fill(_BG)
        title = str(s.get("judul") or _JUDUL_BY_JENIS[jenis])
        surf = fonts[28].render(_pygame_safe(title), True, _TEXT)
        screen.blit(surf, ((lebar - surf.get_width()) // 2, 16))
        card = (24, 66, lebar - 48, tinggi - 66 - 32)
        pg.draw.rect(screen, _CARD, card, border_radius=14)
        _draw_chart_pg(pg, screen, fonts, card, jenis, s, 1.0, None)
        pg.image.save(screen, nama_file)
    finally:
        pg.quit()
    return nama_file


# =============================================================================
# Module exports
# =============================================================================

module = SimpleNamespace(
    # ASCII
    batang=batang,
    garis=garis,
    kue=kue,
    sebar=sebar,
    histogram=histogram,
    # SVG
    batang_svg=batang_svg,
    garis_svg=garis_svg,
    kue_svg=kue_svg,
    sebar_svg=sebar_svg,
    histogram_svg=histogram_svg,
    # Export
    simpan_svg=simpan_svg,
    simpan_html=simpan_html,
    simpan_txt=simpan_txt,
    # GUI (Pygame)
    tampilkan_jendela=tampilkan_jendela,
    tampilkan_batang=tampilkan_batang,
    tampilkan_garis=tampilkan_garis,
    tampilkan_kue=tampilkan_kue,
    tampilkan_sebar=tampilkan_sebar,
    tampilkan_histogram=tampilkan_histogram,
    simpan_png=simpan_png,
)
