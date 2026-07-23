#!/usr/bin/env bash
# ============================================================
#  BroLang Uninstaller
# ============================================================

set -e

MERAH='\033[0;31m'
HIJAU='\033[0;32m'
KUNING='\033[1;33m'
CYAN='\033[0;36m'
TEBAL='\033[1m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
LOCAL_BIN="$HOME/.local/bin"

echo -e "${CYAN}${TEBAL}=== BroLang Uninstaller ===${NC}"
echo ""

read -p "$(echo -e "${KUNING}Hapus virtual environment? (y/N): ${NC}")" DEL_VENV
if [ "$DEL_VENV" = "y" ] || [ "$DEL_VENV" = "Y" ]; then
    if [ -d "$VENV_DIR" ]; then
        rm -rf "$VENV_DIR"
        echo -e "${HIJAU}✓${NC} Virtual environment dihapus"
    else
        echo -e "${KUNING}!${NC} Virtual environment tidak ditemukan"
    fi
else
    echo -e "${KUNING}!${NC} Virtual environment dipertahankan"
fi

read -p "$(echo -e "${KUNING}Hapus scripts (bro, bropm, bro-lsp)? (y/N): ${NC}")" DEL_SCRIPTS
if [ "$DEL_SCRIPTS" = "y" ] || [ "$DEL_SCRIPTS" = "Y" ]; then
    for cmd in bro bropm bro-lsp; do
        if [ -f "$LOCAL_BIN/$cmd" ]; then
            rm -f "$LOCAL_BIN/$cmd"
            echo -e "${HIJAU}✓${NC} $cmd dihapus"
        fi
    done
else
    echo -e "${KUNING}!${NC} Scripts dipertahankan"
fi

# Hapus PATH dari shell rc
for rc in "$HOME/.bashrc" "$HOME/.zshrc" "$HOME/.bash_profile" "$HOME/.profile"; do
    if [ -f "$rc" ] && grep -qF "# BroLang" "$rc" 2>/dev/null; then
        read -p "$(echo -e "${KUNING}Hapus PATH BroLang dari $(basename $rc)? (y/N): ${NC}")" DEL_PATH
        if [ "$DEL_PATH" = "y" ] || [ "$DEL_PATH" = "Y" ]; then
            sed -i '/# BroLang/,+1d' "$rc"
            echo -e "${HIJAU}✓${NC} PATH dihapus dari $(basename $rc)"
        fi
    fi
done

echo ""
echo -e "${HIJAU}${TEBAL}BroLang sudah di-uninstall.${NC}"
echo -e "  Jalankan: ${CYAN}source ~/.bashrc${NC} untuk memperbarui shell"
echo ""
