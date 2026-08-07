# Command Line Interface (CLI)

> **BroLang CLI powerful banget.** Compiler, formatter, REPL, package manager, benchmark - ada semua.

## Perintah Dasar

```bash
# Jalankan file .bro
bro main.bro

# REPL (Read-Eval-Print Loop)
bro

# Kompilasi ke .broc (bytecode)
bro --compile main.bro

# Kompilasi ke executable
bro --compile main.bro --output myapp

# Format kode otomatis
bro format main.bro
```

## Package Manager (BroPM) — v5.2

```bash
bro pkg init                    # Bikin project baru + manifest brolang.json
bro pkg install <nama|path|git-url>  # Install package
bro pkg remove <nama>           # Hapus package
bro pkg list                    # List package terinstall
bro pkg search <kata>           # Cari di registry
bro pkg publish                 # Publish ke registry lokal
bro pkg info <nama>             # Info package
bro pkg manifest                # Tampilkan manifest brolang.json
```

Package yang terinstall bisa langsung dipakai dari kode:
```
impor paket-ku
tulis paket-ku.fungsi_utama()
```

## Benchmark — v5.2

```bash
# Bandingkan Interpreter vs Transpiler vs Bytecode VM
bro benchmark main.bro
bro bench main.bro --repeat 5
```

```
Benchmark: main.bro
============================================================
Hasil (rata-rata dari 3 pengulangan):
  Transpiler        0.042 ms   (1.00x)
  Bytecode VM       3.821 ms   (91.02x)
  Interpreter       4.093 ms   (97.45x)

Transpiler 97.4x lebih cepat dari interpreter (0.04 ms vs 4.09 ms).
============================================================
```

## Debug Mode

```bash
# Debug verbose (trace execution)
bro main.bro --debug verbose
```

**Trace execution step-by-step:**

```
[DEBUG] === Mulai Eksekusi ===
[DEBUG] [TRACE] ASTAnalyzer: visit_DeclarationNode
[DEBUG] [TRACE] ASTAnalyzer: visit_WhileNode
[DEBUG] [TRACE] ASTAnalyzer: visit_IfNode
...
[DEBUG] === Selesai Eksekusi ===
```

## Optimasi Level

```bash
# Tanpa optimasi (default)
bro main.bro

# Optimasi ringan (eliminasi dead code)
bro main.bro --optimize

# Optimasi penuh (+ constant folding)
bro main.bro --optimize --optimize-full
```

---

## CLI Flags

| Flag | Fungsi |
|------|--------|
| (default) | Jalankan file |
| `--compile` | Kompilasi ke bytecode |
| `--output` | Nama output file |
| `--target` | Target kompilasi (wasm) |
| `--optimize` | Optimasi ringan |
| `--optimize-full` | Optimasi penuh |
| `--debug verbose` | Debug mode verbose |
| `format` | Format kode |
| `-h`, `--help` | Bantuan |
| `-v`, `--version` | Versi BroLang |
| `pkg` | Package manager (init/install/publish/dll) |
| `benchmark` / `bench` | Benchmark interpreter vs transpiler vs VM |
