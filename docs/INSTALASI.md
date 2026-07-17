# 🚀 Instalasi BroLang

> **Syarat:** Python 3.10 ke atas. Kalo versi kamu di bawah itu, upgrade dulu ya bos.

## 📥 Clone & Install

```bash
# 1. Clone repo-nya
git clone https://github.com/salzcill-cmd/BroLang.git
cd BroLang

# 2. Install (editable mode, biar kalo update ga perlu install ulang)
pip install -e .

# 3. Cek apakah udah ke-install
bro --help
```

Kalo muncul info kayak gini, berarti udah sukses ✅

## 🎮 Install Game Support (Opsional)

Kalo mau bikin game, install pygame-ce dulu:

```bash
pip install pygame-ce
```

## 🔧 Install Dev Dependencies (Buat Kontributor)

```bash
pip install -e ".[dev]"
```

## ❌ Troubleshooting

### "python: command not found"
Pastikan Python udah ke-install. Cek versinya:
```bash
python --version
# atau
python3 --version
```

### "pip: command not found"
Install pip dulu:
```bash
python -m ensurepip --upgrade
```

### "permission denied"
Tambahin `--user` atau pake `sudo`:
```bash
pip install --user -e .
```

### "bro: command not found" setelah install
Cek PATH Python scripts:
```bash
# Linux/Mac
export PATH="$HOME/.local/bin:$PATH"

# Windows
# Tambahin Python Scripts folder ke PATH
```
