#!/usr/bin/env bash
# ============================================================
#  BroLang Installer v5.4
#  Otomatis install BroLang + setup PATH + dependensi game
# ============================================================

set -e

# --- Warna ---
MERAH='\033[0;31m'
HIJAU='\033[0;32m'
KUNING='\033[1;33m'
BIRU='\033[0;34m'
CYAN='\033[0;36m'
TEBAL='\033[1m'
NC='\033[0m'

info()  { echo -e "${BIRU}[INFO]${NC}  $1"; }
ok()    { echo -e "${HIJAU}[OK]${NC}    $1"; }
warn()  { echo -e "${KUNING}[WARN]${NC}  $1"; }
err()   { echo -e "${MERAH}[ERROR]${NC} $1"; }
header(){ echo -e "\n${CYAN}${TEBAL}=== $1 ===${NC}"; }

# --- Direktori ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
LOCAL_BIN="$HOME/.local/bin"
SHELL_RC=""

# --- Cari shell config file ---
find_shell_rc() {
    if [ -n "$ZSH_VERSION" ] || [ -f "$HOME/.zshrc" ] && [ -z "$BASH_VERSION" ]; then
        echo "$HOME/.zshrc"
    elif [ -f "$HOME/.bashrc" ]; then
        echo "$HOME/.bashrc"
    elif [ -f "$HOME/.bash_profile" ]; then
        echo "$HOME/.bash_profile"
    elif [ -f "$HOME/.profile" ]; then
        echo "$HOME/.profile"
    else
        echo "$HOME/.bashrc"
    fi
}

SHELL_RC=$(find_shell_rc)

# ============================================================
header "BroLang Installer v5.4"
echo -e "  ${TEBAL}Bahasa pemrograman profesional untuk game development${NC}"
echo ""
# ============================================================

# --- 1. Cek Python ---
header "1/5  Pemeriksaan Python"

if command -v python3 &>/dev/null; then
    PY=$(command -v python3)
elif command -v python &>/dev/null; then
    PY=$(command -v python)
else
    err "Python3 tidak ditemukan!"
    echo "  Install dulu: sudo pacman -S python   (Arch)"
    echo "                sudo apt install python3  (Debian/Ubuntu)"
    exit 1
fi

PY_VER=$($PY -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PY_VER_NUM=$($PY -c "import sys; print(sys.version_info.major * 100 + sys.version_info.minor)")

info "Python ditemukan: $PY ($PY_VER)"

if [ "$PY_VER_NUM" -lt 310 ]; then
    err "BroLang butuh Python 3.10+, tapi kamu pakai $PY_VER"
    exit 1
fi

ok "Python $PY_VER memenuhi syarat (>=3.10)"

# --- 2. Buat Virtual Environment ---
header "2/5  Virtual Environment"

if [ -d "$VENV_DIR" ]; then
    warn "Virtual environment sudah ada di $VENV_DIR"
    read -p "  Ingin reinstall? (y/N): " REINSTALL
    if [ "$REINSTALL" = "y" ] || [ "$REINSTALL" = "Y" ]; then
        info "Menghapus venv lama..."
        rm -rf "$VENV_DIR"
    else
        info "Melewati pembuatan venv..."
    fi
fi

if [ ! -d "$VENV_DIR" ]; then
    info "Membuat virtual environment di $VENV_DIR ..."
    $PY -m venv "$VENV_DIR"
    ok "Virtual environment dibuat"
fi

# --- 3. Install BroLang ---
header "3/5  Instalasi BroLang"

source "$VENV_DIR/bin/activate"

info "Installing BroLang dalam mode editable..."
pip install -e ".[dev,game]" --quiet --disable-pip-version-check 2>/dev/null || \
pip install -e ".[dev]" --quiet --disable-pip-version-check 2>/dev/null || \
pip install -e . --quiet --disable-pip-version-check

ok "BroLang v5.4 terinstall!"

# --- 4. Buat Wrapper Script ---
header "4/5  Setup Command 'bro'"

mkdir -p "$LOCAL_BIN"

# Wrapper: bro
cat > "$LOCAL_BIN/bro" <<WRAPPER
#!/usr/bin/env bash
# BroLang launcher
source "$VENV_DIR/bin/activate"
exec python -m brolang.cli "\$@"
WRAPPER
chmod +x "$LOCAL_BIN/bro"

# Wrapper: bropm
cat > "$LOCAL_BIN/bropm" <<WRAPPER
#!/usr/bin/env bash
source "$VENV_DIR/bin/activate"
exec python -m brolang.package_manager.manager "\$@"
WRAPPER
chmod +x "$LOCAL_BIN/bropm"

# Wrapper: bro-lsp
cat > "$LOCAL_BIN/bro-lsp" <<WRAPPER
#!/usr/bin/env bash
source "$VENV_DIR/bin/activate"
exec python -m brolang.lsp.server "\$@"
WRAPPER
chmod +x "$LOCAL_BIN/bro-lsp"

ok "Scripts terbuat di $LOCAL_BIN/"

# --- 5. Setup PATH ---
header "5/5  Konfigurasi PATH"

PATH_LINE="export PATH=\"$LOCAL_BIN:\$PATH\""

if grep -qF ".local/bin" "$SHELL_RC" 2>/dev/null; then
    warn "PATH ~/.local/bin sudah ada di $SHELL_RC"
else
    info "Menambahkan PATH ke $SHELL_RC ..."
    echo "" >> "$SHELL_RC"
    echo "# BroLang" >> "$SHELL_RC"
    echo "$PATH_LINE" >> "$SHELL_RC"
    ok "PATH ditambahkan ke $SHELL_RC"
fi

# ============================================================
header "Instalasi Selesai!"
# ============================================================

export PATH="$LOCAL_BIN:$PATH"

echo ""
echo -e "  ${HIJAU}${TEBAL}BroLang v5.4 berhasil terinstall!${NC}"
echo ""
echo -e "  ${TEBAL}Quick Start:${NC}"
echo -e "    ${CYAN}source $SHELL_RC${NC}              # muat PATH baru"
echo -e "    ${CYAN}bro halo.bro${NC}                  # jalankan program"
echo -e "    ${CYAN}bro repl${NC}                      # REPL interaktif"
echo -e "    ${CYAN}bro new-game mygame${NC}           # buat project game"
echo -e "    ${CYAN}bro --version${NC}                 # cek versi"
echo ""
echo -e "  ${TEBAL}Path:${NC}"
echo -e "    Venv    : $VENV_DIR"
echo -e "    Scripts : $LOCAL_BIN/"
echo -e "    Shell   : $SHELL_RC"
echo ""

# --- Opsional: Install Pygame ---
read -p "$(echo -e "${KUNING}Install pygame untuk game development? (Y/n): ${NC}")" INSTALL_PYGAME
if [ "$INSTALL_PYGAME" != "n" ] && [ "$INSTALL_PYGAME" != "N" ]; then
    info "Installing pygame..."
    pip install pygame-ce --quiet --disable-pip-version-check 2>/dev/null
    ok "Pygame terinstall!"
fi

echo ""
echo -e "${HIJAU}${TEBAL}Siap dipakai! Selamat coding!${NC}"
echo ""
