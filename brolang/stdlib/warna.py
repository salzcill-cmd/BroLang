"""
Modul Warna untuk BroLang
==========================

Utilitas warna terminal ANSI, konversi hex/RGB, dan styling teks.

Contoh:
    impor warna
    
    # Teks berwarna langsung
    tulis warna.merah("Error!")
    tulis warna.hijau("Sukses!")
    tulis warna.kuning("Peringatan")
    tulis warna.biru("Info")
    
    # Kustom warna
    tulis warna.ansi("Halo", latar="hitam", huruf="putih", tebal=benar)
    
    # RGB & Hex
    tulis warna.rgb_to_hex(255, 128, 0)  # "#ff8000"
    tulis warna.hex_to_rgb("#ff8000")     # (255, 128, 0)
    
    # Gradient
    tulis warna.gradient("Halo Dunia!", (255, 0, 0), (0, 0, 255))
    
    # Block/box
    tulis warna.kotak("Halo!", warna="merah")
    tulis warna.bingkai("Penting", style="ganda")
"""


# ANSI escape codes
_RESET = "\033[0m"
_BOLD = "\033[1m"
_DIM = "\033[2m"
_ITALIC = "\033[3m"
_UNDERLINE = "\033[4m"
_STRIKETHROUGH = "\033[9m"

# Foreground colors
_FG = {
    "hitam": "\033[30m",
    "merah": "\033[31m",
    "hijau": "\033[32m",
    "kuning": "\033[33m",
    "biru": "\033[34m",
    "ungu": "\033[35m",
    "cyan": "\033[36m",
    "putih": "\033[37m",
    "abu": "\033[90m",
    "merah_terang": "\033[91m",
    "hijau_terang": "\033[92m",
    "kuning_terang": "\033[93m",
    "biru_terang": "\033[94m",
    "ungu_terang": "\033[95m",
    "cyan_terang": "\033[96m",
    "putih_terang": "\033[97m",
}

# Background colors
_BG = {
    "hitam": "\033[40m",
    "merah": "\033[41m",
    "hijau": "\033[42m",
    "kuning": "\033[43m",
    "biru": "\033[44m",
    "ungu": "\033[45m",
    "cyan": "\033[46m",
    "putih": "\033[47m",
    "abu": "\033[100m",
    "merah_terang": "\033[101m",
    "hijau_terang": "\033[102m",
    "kuning_terang": "\033[103m",
    "biru_terang": "\033[104m",
    "ungu_terang": "\033[105m",
    "cyan_terang": "\033[106m",
    "putih_terang": "\033[107m",
}

# Named colors (16 color palette)
NAMA_WARNA = {
    "merah": (255, 0, 0),
    "hijau": (0, 255, 0),
    "biru": (0, 0, 255),
    "kuning": (255, 255, 0),
    "cyan": (0, 255, 255),
    "ungu": (255, 0, 255),
    "putih": (255, 255, 255),
    "hitam": (0, 0, 0),
    "abu": (128, 128, 128),
    "orange": (255, 165, 0),
    "pink": (255, 192, 203),
    "coklat": (139, 69, 19),
    "emas": (255, 215, 0),
    "perak": (192, 192, 192),
    "navy": (0, 0, 128),
    "teal": (0, 128, 128),
}


def ansi(teks, huruf=None, latar=None, tebal= False, miring=False, garis_bawah=False):
    """Teks dengan gaya ANSI kustom.
    
    Args:
        teks: string yang akan distyle
        huruf: warna huruf (nama atau hex/rgb tuple)
        latar: warna latar belakang
        tebal: bold
        miring: italic
        garis_bawah: underline
    
    Returns:
        string dengan ANSI codes
    """
    codes = []
    
    if tebal:
        codes.append(_BOLD)
    if miring:
        codes.append(_ITALIC)
    if garis_bawah:
        codes.append(_UNDERLINE)
    
    # Foreground
    if huruf:
        if isinstance(huruf, tuple):
            r, g, b = huruf
            codes.append(f"\033[38;2;{r};{g};{b}m")
        elif isinstance(huruf, str):
            if huruf.startswith("#"):
                r, g, b = hex_to_rgb(huruf)
                codes.append(f"\033[38;2;{r};{g};{b}m")
            elif huruf in _FG:
                codes.append(_FG[huruf])
    
    # Background
    if latar:
        if isinstance(latar, tuple):
            r, g, b = latar
            codes.append(f"\033[48;2;{r};{g};{b}m")
        elif isinstance(latar, str):
            if latar.startswith("#"):
                r, g, b = hex_to_rgb(latar)
                codes.append(f"\033[48;2;{r};{g};{b}m")
            elif latar in _BG:
                codes.append(_BG[latar])
    
    if not codes:
        return str(teks)
    
    return "".join(codes) + str(teks) + _RESET


def merah(teks):
    """Teks merah."""
    return ansi(teks, huruf="merah")

def hijau(teks):
    """Teks hijau."""
    return ansi(teks, huruf="hijau")

def kuning(teks):
    """Teks kuning."""
    return ansi(teks, huruf="kuning")

def biru(teks):
    """Teks biru."""
    return ansi(teks, huruf="biru")

def ungu(teks):
    """Teks ungu."""
    return ansi(teks, huruf="ungu")

def cyan(teks):
    """Teks cyan."""
    return ansi(teks, huruf="cyan")

def putih(teks):
    """Teks putih."""
    return ansi(teks, huruf="putih")

def abu(teks):
    """Teks abu-abu."""
    return ansi(teks, huruf="abu")

def merah_terang(teks):
    """Teks merah terang."""
    return ansi(teks, huruf="merah_terang")

def hijau_terang(teks):
    """Teks hijau terang."""
    return ansi(teks, huruf="hijau_terang")

def kuning_terang(teks):
    """Teks kuning terang."""
    return ansi(teks, huruf="kuning_terang")

def biru_terang(teks):
    """Teks biru terang."""
    return ansi(teks, huruf="biru_terang")


def tebal(teks):
    """Teks tebal (bold)."""
    return ansi(teks, tebal=True)

def miring(teks):
    """Teks miring (italic)."""
    return ansi(teks, miring=True)

def garis_bawah(teks):
    """Teks dengan garis bawah."""
    return ansi(teks, garis_bawah=True)

def dim(teks):
    """Teks redup (dim)."""
    return f"{_DIM}{teks}{_RESET}"


# ============= Konversi Warna =============

def rgb_to_hex(r, g, b):
    """Konversi RGB ke hex string.
    
    Contoh:
        warna.rgb_to_hex(255, 128, 0)  # "#ff8000"
    """
    return f"#{r:02x}{g:02x}{b:02x}"


def hex_to_rgb(hex_str):
    """Konversi hex string ke tuple RGB.
    
    Contoh:
        warna.hex_to_rgb("#ff8000")  # (255, 128, 0)
    """
    h = hex_str.lstrip("#")
    if len(h) == 3:
        h = h[0]*2 + h[1]*2 + h[2]*2
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def rgb_to_ansi(r, g, b, latar=False):
    """Konversi RGB ke ANSI 24-bit escape code.
    
    Args:
        r, g, b: 0-255
        latar: True untuk background, False untuk foreground
    """
    prefix = "48" if latar else "38"
    return f"\033[{prefix};2;{r};{g};{b}m"


def gradient(teks, warna_awal, warna_akhir):
    """Gradient teks dari warna awal ke warna akhir (per karakter).
    
    Args:
        teks: string
        warna_awal: tuple (r, g, b) atau hex string
        warna_akhir: tuple (r, g, b) atau hex string
    
    Contoh:
        warna.gradient("Halo!", (255, 0, 0), (0, 0, 255))
    """
    if isinstance(warna_awal, str):
        warna_awal = hex_to_rgb(warna_awal)
    if isinstance(warna_akhir, str):
        warna_akhir = hex_to_rgb(warna_akhir)
    
    n = len(teks)
    if n == 0:
        return ""
    
    parts = []
    for i, char in enumerate(teks):
        t = i / max(1, n - 1)
        r = int(warna_awal[0] + (warna_akhir[0] - warna_awal[0]) * t)
        g = int(warna_awal[1] + (warna_akhir[1] - warna_awal[1]) * t)
        b = int(warna_awal[2] + (warna_akhir[2] - warna_awal[2]) * t)
        parts.append(f"\033[38;2;{r};{g};{b}m{char}")
    
    return "".join(parts) + _RESET


def rainbow(teks):
    """Teks dengan warna pelangi (per karakter)."""
    colors = [
        (255, 0, 0), (255, 127, 0), (255, 255, 0),
        (0, 255, 0), (0, 0, 255), (75, 0, 130), (148, 0, 211),
    ]
    parts = []
    for i, char in enumerate(teks):
        r, g, b = colors[i % len(colors)]
        parts.append(f"\033[38;2;{r};{g};{b}m{char}")
    return "".join(parts) + _RESET


# ============= Block & Box =============

def kotak(teks, warna="putih", style="sederhana"):
    """Bungkus teks dalam kotak.
    
    Args:
        teks: string
        warna: warna border (nama warna ANSI)
        style: "sederhana" (-), "ganda" (=), "tebal" (#), "bulat" (~)
    
    Contoh:
        warna.kotak("Halo!", warna="merah")
    """
    lines = str(teks).split("\n")
    max_len = max(len(line) for line in lines) if lines else 0
    
    styles = {
        "sederhana": ("┌", "┐", "└", "┘", "─", "│"),
        "ganda": ("╔", "╗", "╚", "╝", "═", "║"),
        "tebal": ("┏", "┓", "┗", "┛", "━", "┃"),
        "bulat": ("╭", "╮", "╰", "╯", "─", "│"),
    }
    
    tl, tr, bl, br, h, v = styles.get(style, styles["sederhana"])
    
    border_color = _FG.get(warna, "")
    reset = _RESET if border_color else ""
    
    top = f"{border_color}{tl}{h * (max_len + 2)}{tr}{reset}"
    bottom = f"{border_color}{bl}{h * (max_len + 2)}{br}{reset}"
    
    result = [top]
    for line in lines:
        result.append(f"{border_color}{v}{reset} {line.ljust(max_len)} {border_color}{v}{reset}")
    result.append(bottom)
    
    return "\n".join(result)


def bingkai(teks, style="sederhana"):
    """Alias untuk kotak dengan style default."""
    return kotak(teks, style=style)


def garis(lebar=40, char="─"):
    """Buat garis horizontal.
    
    Contoh:
        warna.garis(50)     # ──────────────────────────────────────────
        warna.garis(20, "=")  # ====================
    """
    return char * lebar


def judul(teks, level=1):
    """Format judul dengan dekorasi.
    
    Contoh:
        warna.judul("Chapter 1")   # ═══════ Chapter 1 ═══════
        warna.judul("Section", 2)  # ── Section ──
    """
    lebar = 40
    if level == 1:
        sisa = (lebar - len(teks) - 2) // 2
        return f"{'═' * sisa} {teks} {'═' * sisa}"
    elif level == 2:
        sisa = (lebar - len(teks) - 2) // 2
        return f"{'─' * sisa} {teks} {'─' * sisa}"
    else:
        return f"{'·' * 3} {teks} {'·' * 3}"
