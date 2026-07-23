# Instalasi BroLang

> **Syarat:** Python 3.10 ke atas. Kalo versi kamu di bawah itu, upgrade dulu ya bos.

## Cara 1: Install dengan Script (Recommended)

Paling gampang, tinggal clone terus jalanin script:

```bash
git clone https://github.com/salzcill-cmd/BroLang.git
cd BroLang
chmod +x install.sh
./install.sh
```

Script-nya bakal:
1. Cek Python udah sesuai versi belum
2. Bikin virtual environment otomatis
3. Install BroLang + dependensi dev
4. Bikin command `bro` di `~/.local/bin/`
5. Setup PATH di shell kamu

Abis install, jalanin:
```bash
source ~/.bashrc    # atau ~/.zshrc
bro --version       # BroLang 5.0.0
```

## Cara 2: Install Manual

Kalo mau atur sendiri:

```bash
git clone https://github.com/salzcill-cmd/BroLang.git
cd BroLang
pip install -e .
```

Abis itu `bro` langsung bisa dipake.

## Cara 3: Install Langsung dari GitHub

Ga perlu clone, langsung install:

```bash
pip install git+https://github.com/salzcill-cmd/BroLang.git
```

## Install Game Support (Opsional)

Kalo mau bikin game, install pygame-ce dulu:

```bash
pip install pygame-ce
```

Atau pas install pertama kali pake script, bakal ditanya mau install pygame juga.

## Install Dev Dependencies (Buat Kontributor)

```bash
pip install -e ".[dev]"
```

## Uninstall

Pake script uninstall:

```bash
cd BroLang
chmod +x uninstall.sh
./uninstall.sh
```

Atau manual:
```bash
pip uninstall brolang
rm ~/.local/bin/bro
```

## Troubleshooting

### "bro: command not found" setelah install

Cek apakah `~/.local/bin` ada di PATH:
```bash
echo $PATH | grep local
```

Kalo ga ada, tambahin:
```bash
export PATH="$HOME/.local/bin:$PATH"
```

Terus save ke shell rc:
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### "python: command not found"

Pastikan Python udah ke-install. Cek versinya:
```bash
python3 --version
```

### "pip: command not found"

Install pip dulu:
```bash
python3 -m ensurepip --upgrade
```

### "permission denied"

Tambahin `--user` atau pake `sudo`:
```bash
pip install --user -e .
```
