# Changelog

Semua perubahan penting pada BroLang akan didokumentasikan di file ini.

Format berdasarkan [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [5.1.0] - 2026-07-23

### Added
- **Output Consistency Tests**: 31 test cases yang memastikan transpiler dan interpreter menghasilkan output identik.
- **ForEachNode transpiler support**: `untuk setiap item dalam list` sekarang bisa di-transpile ke Python.
- **BroLang method name mapping**: Method seperti `urutkan()`, `balikkan()`, `panjang()`, `potong()`, dll. di-transpile ke nama Python yang sesuai.
- **FilterNode lambda fix**: `saring(list, lalu(x) kondisi)` sekarang di-transpile dengan benar tanpa double-nested lambda.

### Fixed
- **Interpreter `.get()` hijacking**: Method `.get()` user-defined tidak lagi di-intercept oleh built-in property accessor. Class method `get()` sekarang diprioritaskan.
- **ForEachNode silent failure**: Transpiler sebelumnya diam-diam melewati `untuk setiap` loop. Sekarang di-transpile dengan benar.
- **FilterNode double lambda**: `saring(angka, lalu(x) x % 2 == 0)` sebelumnya menghasilkan `lambda x: lambda x: ...` yang tidak berfungsi.

### Changed
- **REPL now uses transpiler**: REPL mencoba transpiler dulu (lebih cepat), fallback ke interpreter jika gagal. State tetap dipertahankan antar input.
- **Method name mapping strategy**: Transpiler hanya map method yang unambiguous (tidak bentrok dengan nama method user).

## [5.0.0] - 2026-07-20

### Added
- **Null Coalescing**: `x ?? default` — gunakan nilai default jika x null.
- **Optional Chaining**: `obj?.method()` — safe navigation untuk null.
- **Higher-Order Functions**: `peta()`, `saring()`, `kurangi()` — map, filter, reduce built-in.
- **Result Type**: `Benar(value)` / `Salah(error)` — error handling ala Rust.
- **Option Type**: `Ada(value)` / `Kosong()` — optional values.
- **Macros**: `makro Nama() ... selesai` — metaprogramming.
- **Namespaces**: `ruang nama Nama { ... }` + `pakai Nama`.
- **Interfaces**: `antarmuka Nama { ... }` — enforced at runtime.
- **Abstract Classes**: `abstrak kelas Nama { ... }` — tidak bisa diinstansiasi.
- **Access Modifiers**: `publik`, `privat`, `terlindungi` — enforced at runtime.
- **For-Each**: `untuk setiap item dalam list lakukan`.
- **Generators**: `hasilkan` keyword.
- **Iterator Protocol**: `__iter__`, `__next__`, `hentikan_iterasi()`.
- **Properties**: `_<nama>()` getter, `_<nama>_set(v)` setter.
- **Static Methods**: `statis fungsi`.
- **String Interpolation**: `$variable` dan `f"...{expr}..."`.
- **Type Checking**: `cek_tipe(val)` dan `pastikan(cond, msg)`.
- **Bytecode VM**: Compiler AST → bytecode + stack-based VM (1.2x lebih cepat).
- **Transpiler**: AST → Python source code (97x lebih cepat dari interpreter).
- **Class Inheritance**: `kelas Nama(Parent)` dan `kelas Nama : Parent`.

### Changed
- **Execution model**: `bro run` sekarang mencoba transpiler dulu, fallback ke interpreter.
- **REPL**: REPL mencoba transpiler dulu, fallback ke interpreter.

## [4.0.0] - 2026-07-19

### Added
- **Async/Await**: `asinkron fungsi`, `tunggu`.
- **Generators**: `hasilkan`.
- **Decorators**: `@dekorator`.
- **Typed Exceptions**: `kecuali tipe sebagai err`.
- **Context Manager**: `dengan...sebagai`.
- **Walrus Operator**: `:=`.
- **Star Import**: `dari module impor *`.
- **13 stdlib modules baru**: sprite, animasi, tilemap, kamera, fisika, tes, profil, debugger, pencocok, antrian, tumpukan, serialisasi, dasar.
- **20+ string methods**: `cocok`, `ganti`, `potong`, `strip`, `mulai`, dll.
- **Banyak builtins baru**: `boolean`, `zip`, `enumerate`, `min`, `max`, `urutkan`, `terbalik`, `ada`, `semua`, `isinstance`, `panjang`.

## [3.1.0] - 2026-07-17

### Added
- **Identity comparison**: `is` / `is bukan`.
- **Membership test**: `dalam` / `bukan dalam`.
- **Slicing**: `list[1:3]`, `list[:5]`, `list[::2]`.
- **Chained Comparisons**: `1 < x < 10`.
- **`pass`**: No-op placeholder.
- **`hapus`**: Delete variable atau element.
- **`pastikan`**: Runtime assertion.
- **Tuples**: `(1, 2, 3)`.
- **Sets**: `{1, 2, 3}`.
- **Closures**: Functions/lambda menangkap outer scope.
- **For-else / While-else**: Blok else pada loop.

## [3.0.0] - 2026-07-17

### Added
- **Augmented Assignment**: `x += 1`, `x -= 2`, dll.
- **Ternary Expression**: `a jika kondisi lainnya b`.
- **Global/Nonlocal**: Scope control.
- **Default Parameters**: Parameter dengan nilai default.
- **Raise/Finally**: Error handling lengkap.
- **List/Dict Methods**: `.tambah`, `.urutkan`, `.kunci`, dll.
- **Bitwise Operators**: `&`, `|`, `^`, `~`.
- **Space Defender Game**: Game Pygame.

## [2.0.0] - 2026-07-16

### Added
- **Lambda**: `lalu(x) expr`.
- **List Comprehension**: `[expr lalu var dalam iterable]`.
- **F-strings**: `f"...{expr}..."`.
- **Enum**: `enum Nama { A, B, C }`.
- **Struct**: `struktur Nama { x, y }`.
- **Match/Case**: `cocokkan expr { pattern: body }`.
- **Game Dev stdlib**: `vektor`, `grafis`, `audio`, `input`, `game`.

## [1.0.0] - 2026-07-16

### Added
- **Core language**: Variabel, fungsi, kelas, control flow.
- **Types**: angka, teks, boolean, list, objek, kosong.
- **Error handling**: `try...kecuali...selesai`, `lempar`.
- **Module system**: `muat` (import).
- **Standard library**: matematika, teks, waktu, file, json, jaringan, acak.
- **CLI**: `bro run`, `bro repl`, `bro fmt`, `bro lint`, `bro build`, `bro test`.
- **REPL**: Interactive mode.
- **Formatter & Linter**: Code formatting dan static analysis.
- **Tree-walking interpreter**: Visitor pattern.
