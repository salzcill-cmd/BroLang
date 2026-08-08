# Performance BroLang v6.3

> BroLang punya **tiga backend eksekusi**: transpiler (tercepat), bytecode VM, dan
> interpreter tree-walking. `bro run` otomatis memakai transpiler sebagai fast path
> dan fallback ke interpreter bila ada fitur yang belum didukung transpiler.

## Arsitektur Eksekusi

```
Kode BroLang (.bro)
      │
      ▼
   Lexer ──► Parser ──► AST ──► Optimizer (constant folding AST)
      │                          │
      │                          ├──► Transpiler ──► Python (97-150x lebih cepat) ✅ fast path `bro run`
      │                          │
      │                          ├──► Compiler ──► Bytecode ──► VM (stack-based)
      │                          │
      │                          └──► Interpreter (tree-walking, fallback)
```

## Optimasi v6.3

### 1. Peephole Optimizer (bytecode VM)
Saat kompilasi ke bytecode, pass `apply_peephole` di `brolang/vm/compiler.py`:

- **Constant folding** — `PUSH_CONST a; PUSH_CONST b; ADD` → `PUSH_CONST (a+b)` untuk
  aritmatika, perbandingan, negasi, dan NOT pada konstanta murni.
- **NOP removal** — instruksi `pass` dihapus.
- **Jump remapping** — semua target jump di-remap otomatis karena index instruksi berubah.
- **Sub-bytecode folding** — body fungsi, method kelas/struct, dan lambda juga di-peephole.

### 2. Method Cache (VM)
Pencarian method di inheritance chain (`VM._find_method_on_class`) di-cache per
`(kelas, nama_method)` — menghindari traversal parent-chain berulang untuk pemanggilan
method yang panas. Cache di-invalidate saat method di-monkey-patch.

### 3. Fast Path Interpreter
Operator biner (`+`, `-`, `==`, dst.) kini hanya mengecek operator overloading bila
salah satu operan adalah instance kelas BroLang — operan primitif (angka, teks, list)
langsung memakai operator Python tanpa overhead lookup.

### 4. Fix: Binding Parameter Method (VM)
`param_count` method non-static kini menghitung slot `self` — memperbaiki pemanggilan
method class multi-parameter di VM yang sebelumnya error "slot belum diinisialisasi".

### 5. Fix: String Multi-baris (Lexer)
Deteksi `"""..."""` dan `f"""..."""` diperbaiki (sebelumnya tidak pernah bekerja) —
ternyata ini bug offset di lexer yang membuat string multi-baris selalu gagal.

## Benchmark Resmi

Dijalankan dengan `bro benchmark benchmarks/<file>.bro` pada mesin developer
(Linux, Python 3.12). Skala disesuaikan agar semua backend (termasuk interpreter
yang lambat) bisa selesai.

| Benchmark | Transpiler | Bytecode VM | Speedup Transpiler |
|-----------|-----------:|------------:|-------------------:|
| `fibonacci` (rekursif fib(20)) | 6 ms | 891 ms | **155x** |
| `loop` (150k iterasi aritmatika) | 29 ms | 1 568 ms | **55x** |
| `string` (concat + f-string) | 5 ms | 106 ms | **23x** |
| `objek` (5k instansiasi + method) | 17 ms | 1 026 ms | **62x** |

> **Catatan:** Interpreter tree-walking jauh lebih lambat (detik untuk benchmark di atas)
> dan hanya dipakai sebagai fallback. Untuk produksi, `bro run` selalu memakai transpiler.

## Menjalankan Benchmark

```bash
# Benchmark satu file (membandingkan interpreter vs transpiler vs VM)
bro benchmark benchmarks/fibonacci.bro --repeat 3

# Semua benchmark
for f in benchmarks/*.bro; do bro benchmark "$f" --repeat 3; done

# Profil interpreter (debugging hot path)
bro profile benchmarks/loop.bro
```

## Tips Performance

- `bro run` sudah otomatis memakai transpiler — tidak perlu flag.
- Hindari string concat `+` dalam loop besar (O(n²)); pakai list + `gabung`.
- Rekursi dalam (fibonacci) lambat di interpreter; gunakan iterasi bila memungkinkan.
- `bro build file.bro -o out.py` menghasilkan Python murni yang bisa dijalankan
  langsung dengan `python out.py` — tanpa overhead lexing/parsing sama sekali.
