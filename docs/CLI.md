# Command Line Interface (CLI)

> **BroLang CLI powerful banget.** Compiler, formatter, REPL, debug mode - ada semua.

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
