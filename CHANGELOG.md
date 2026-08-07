# Changelog

Semua perubahan penting pada BroLang akan didokumentasikan di file ini.

Format berdasarkan [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [5.4.0] - 2026-08-07

### Added
- **Full Upgrade Library Game** — 14 modul game untuk game development 2D.
- **Modul `partikel` (baru)**: particle system lengkap — `buat_emiter`, `buat_ledakan`, `buat_hujan`, emisi otomatis per detik, gravitasi/gesekan partikel, variasi kecepatan/umur/ukuran.
- **Modul `ui` (baru)**: `Tombol` (hover, klik, callback on_klik/on_hover/on_keluar), `Label` (termasuk tengah), `Panel` (transparan + rounded), `Bar` (health/progress, tambah/kurang/persen).
- **`sprite` ditulis ulang total**: sebelumnya SyntaxError sehingga `impor sprite` selalu gagal. Kini: gambar/`surface`, sprite sheet, animasi frame dengan callback on_selesai, rotasi derajat, flip, alpha, tint, z-order, collider kotak/lingkaran, gerak+gravitasi, `GrupSprite` dengan cek tabrakan antar grup.
- **`animasi`**: 26 jenis easing (linear, quad, cubic, quart, expo, back, elastic, bounce, sine — in/out/in-out) + alias lama `bounce`/`elastic` yang kini benar, callback `on_selesai`/`on_siklus`, `daftar_easing()`.
- **`waktu`**: `Timer` (hitung mundur + `on_selesai`), `Stopwatch`, `FpsCounter`, dan `delta()` otomatis.
- **`game`**: pause/resume (`pause`/`resume`/`sedang_pause`), dt-clamp 0.05s anti-lag, FPS display (`set_tampil_fps`), background color (`set_latar_warna`), `reset()`, `dapatkan_fps()`.
- **`input`**: fix konflik event dengan game loop (input kini satu-satunya pemilik event queue, game baca via `ambil_events()`), `tikus_baru_ditekan`/`tikus_dilepas`, `geser()` scroll wheel, `events_geser()`, dukungan gamepad/joystick (`gamepad_ada`, `gamepad_sumbu`, `gamepad_tombol`, dll).
- **`grafis`**: `segi_panjang_bulat`, `poligon`, `lingkaran_garis`, `elips`, `titik`, `tulis_teks_multi`, `buat_surface`/`gambar_surface` (offscreen canvas).
- **`vektor`**: `sudut()` derajat, `rotasi(deg)`, `Vec2.dari_polar`/`buat_polar`, `proyeksi`, `refleksi`, `arah_ke`, `tengah`.
- **`kamera`**: `reset()`, `set_posisi`/`posisi`, `gerak`, `set_batas_world`, `set_sudut` (rotasi view), `buat_layar_penuh`.
- **`tilemap`**: fix `solid_map` tidak sinkron setelah `dari_array`/`dari_string`, `dari_file`/`simpan_file`, `atur_solid` convenience, rendering warna fallback (tanpa gambar), `resize`, `banyak_tile`, alias `tabrakan`/`is_solid_at`.
- **`fisika`**: radius per-bodi (bukan hardcode 16), `set_radius`/`set_ukuran`, gravitasi configurable (`buat_dunia(gravitasi_y)`/`set_gravitasi`), ground detection per-frame, koreksi posisi tabrakan, `bodi_di_posisi`.
- **Interpreter**: atribut objek Python stdlib kini bisa di-*set* (`pemain.warna = "merah"`) — konsisten dengan transpiler. Sebelumnya hanya `BroLangInstance` yang mendukung assignment atribut.
- **Contoh `examples/game_arena.bro`**: platformer showcase semua fitur — tilemap solid, sprite, patroli musuh, tembakan, ledakan partikel, health bar, tombol menu, kamera shake, pause, stopwatch, FPS.
- **`docs/GAME.md` ditulis ulang** sesuai API baru (sebelumnya mendokumentasikan API lama yang tidak ada).

### Fixed
- `sprite.py` SyntaxError → modul tidak bisa di-import sama sekali.
- `animasi.py` easing `elastic` crash (`(float).sin()`) dan formula `bounce` salah.
- `input` vs `game` konflik event: game loop memakan semua event sebelum input sempat membacanya.
- **`input.tombol_ditekan()` tidak pernah mendeteksi tombol khusus** (UP/DOWN/LEFT/RIGHT, F1-F12, modifier): held-state dibangun dari `pygame.key.get_pressed()` yang di-index *scancode*, sedangkan `_KEY_MAP` memakai *keycode* → player 2 di `game_pong.bro` tidak bisa bergerak. Kini held-state dibangun dari event `KEYDOWN`/`KEYUP` (keycode) + auto-clear saat fokus jendela hilang.
- **Klik mouse tidak pernah terdeteksi** (`tikus_baru_ditekan`/`tikus_dilepas`): event `MOUSEBUTTONDOWN` punya `button` 1-based (1=kiri, 2=tengah, 3=kanan) tapi disimpan mentah, sedangkan API BroLang memakai index 0-based (`tikus_baru_ditekan(0)` = klik kiri) → tombol MULAI di `game_arena.bro` tidak bisa diklik. Kini `event.button` dikonversi ke index 0-based (button 4+/scroll diabaikan, ditangani `MOUSEWHEEL`).
- `tilemap` solid_map tidak ter-update setelah bulk-load → collision salah.
- `fisika` radius collision hardcode 16.
- Nama fungsi stdlib yang tabrakan keyword BroLang: `buat` → `buat_peta`/`buat_kamera`/`buat_emiter`, `Timer.selesai()` → `habis()`, `GrupSprite.hapus` → `hapus_sprite`, `GrupSprite.kosong` → `apakah_kosong`, `Bar.kosong` → `habis`, `Animasi.lanjutkan` → `teruskan` (alias Python tetap ada).

### Changed
- Versi di-bump dari `5.3.0` ke `5.4.0`.
- **`examples/game_paddle.bro`** di-upgrade menjadi **Brick Breaker**: 8×4 bata berwarna penambah skor (+10/bata, warna per baris), percepatan bola bertahap (cap 600 px/s anti-tunneling), kondisi **KAMU MENANG!** saat semua bata hancur, restart dengan SPACE.

## [5.3.0] - 2026-08-07

### Added
- **Modul `visualisasi` — Data Visualization**: library chart/grafik untuk memvisualisasikan data langsung dari BroLang.
  - Chart ASCII (tampil langsung di terminal): `batang`, `garis`, `kue` (pie/donat), `sebar` (scatter), `histogram`.
  - Chart SVG (untuk laporan): `batang_svg`, `garis_svg`, `kue_svg`, `sebar_svg`, `histogram_svg`.
  - Export: `simpan_svg`, `simpan_html` (laporan multi-chart), `simpan_txt`.
  - Mendukung 3 bentuk input: list nilai, list pasangan `[label, nilai]`, dan objek `{label: nilai}`.
  - `garis_svg` mendukung multi-seri dengan legend.
- **GUI Chart (Pygame)**: tampilkan chart di jendela native ala game (`pip install pygame-ce`).
  - `tampilkan_jendela(charts, judul=, lebar=, tinggi=, layar_penuh=)` — jendela berisi 1+ chart dengan animasi masuk, hover tooltip, dan kontrol keyboard (panah ganti chart, `1-9` lompat, `F` fullscreen, `S` screenshot, `H` bantuan, `ESC` tutup).
  - `tampilkan_batang`, `tampilkan_garis`, `tampilkan_kue`, `tampilkan_sebar`, `tampilkan_histogram` — buka jendela satu chart langsung.
  - `simpan_png(nama_file, spec)` — render chart ke PNG tanpa membuka jendela (bisa dipakai di server/CI).
  - Error jelas & sopan kalau pygame belum terinstall.

### Changed
- Versi di-bump dari `5.2.0` ke `5.3.0`.
- `pyproject.toml`: dependensi `pygame-ce` tersedia via extra `[game]` (sudah ada sebelumnya, kini dipakai juga oleh modul visualisasi).

### Fixed
- **Lexer bracket-aware**: ekspresi multi-baris di dalam `( )`, `[ ]`, `{ }` tidak lagi dianggap blok indentasi baru. Ini memperbaiki kondisi `jika (...)` yang ditulis beberapa baris — sebelumnya error "Indentasi tidak konsisten".
- **Contoh game diperbaiki**: `examples/game_pong.bro` & `game_paddle.bro` (sintaks `fungsi`/`selesai`/`dan`), keduanya kini lex, parse, dan jalan sampai game loop.
- **Parser `tipe(...)`**: `tipe(nilai)` kini valid sebagai pemanggilan builtin (sebelumnya `tipe` selalu dianggap keyword type-alias → "Token tidak terduga").
- **Parser comprehension filter**: `[x lalu x dalam data jika kondisi]` — `jika` di comprehension tidak lagi salah di-parse sebagai ternary ("Ternary membutuhkan 'lainnya'").
- **SemanticAnalyzer & MultiExceptNode**: `coba/tangkap` dan `coba/kecuali` kini mendefinisikan variabel exception di analyzer, sehingga `bro run` tidak lagi melaporkan "Variabel 'error' belum didefinisikan" untuk program dengan try/catch.
- **Modul `grafis` & `game` terintegrasi**: fungsi gambar `grafis.*` kini memakai display pygame aktif sebagai fallback, sehingga bisa menggambar di window yang dibuat `game.buat_jendela()` (sebelumnya error "Jendela belum dibuat").
- **Transpiler builtin `tipe`**: `tipe(...)` kini di-map ke helper yang mengembalikan nama tipe BroLang (`angka`, `teks`, dll).
- **Transpiler import stdlib**: `impor matematika` dll. kini fallback ke `get_stdlib_module` — `bro run` tidak lagi jatuh ke interpreter (yang membuat output berlipat dua) untuk program yang pakai stdlib.
- **Transpiler method-map lebih pintar**: pemetaan method (mis. `potong` → `split`) tidak lagi diterapkan ke atribut modul hasil import (mis. `teks.potong(...)`), dan `potong` diperbaiki dari `strip` ke `split` sesuai semantik interpreter.
- **29 test baru** (parser multi-baris, regresi analyzer, transpiler, integrasi grafis-game) — total **410 test passing**.

## [5.2.0] - 2026-08-07

### Added
- **Keyword Arguments**: `sapa(nama="Budi", umur=25)` — argumen bernama untuk fungsi, method, lambda, dan constructor kelas.
- **Pipeline Operator**: `nilai |> fungsi` atau `[1,2,3] |> peta(lalu(x) x + 1)` — komposisi fungsi ala Elixir/F#.
- **Destructuring Assignment**: `buat [a, b] = list` dan `buat {x, y} = objek` — unpacking seperti Python/JS.
- **Package Manager (BroPM)**: `bro pkg init/install/remove/list/search/publish/info` — manifest `brolang.json`, install dari folder lokal, git URL, atau registry; publish ke registry lokal.
- **Package Import**: `impor <paket>` sekarang bisa memuat package BroLang yang terinstall via `bro pkg install`.
- **Benchmark Command**: `bro benchmark <file>` / `bro bench <file>` — membandingkan Interpreter vs Transpiler vs Bytecode VM.
- **VM Optimasi**: builtin cache (fast path LOAD_GLOBAL/CALL_BUILTIN) + perbaikan stack discipline STORE_LOCAL/STORE_GLOBAL.

### Fixed
- **VM stack bug**: `STORE_LOCAL` dan `STORE_GLOBAL` tidak mem-pop stack, menyebabkan akumulasi nilai di stack pada for-loop & assignment. VM sekarang berperilaku benar.
- **VM for-loop**: urutan `GET_ITER`/`STORE_LOCAL` diperbaiki sehingga loop di VM tidak lagi error.
- **VM builtin cache invalidation**: cache builtin tidak di-invalidate saat user menimpa nama builtin (`buat panjang = 5` setelah `panjang()` sebelumnya). Sekarang `STORE_GLOBAL`/`DEFINE_GLOBAL` menghapus cache.
- **Optimizer menghilangkan kwargs**: `visit_CallNode` di optimizer merekonstruksi `CallNode` tanpa `kwargs`, sehingga keyword arguments hilang saat lewat `bro run`. Sudah diperbaiki.
- **SemanticAnalyzer & node baru**: `PipelineNode` dan `DestructuringAssignmentNode` sekarang punya visitor di analyzer, sehingga `bro run` tidak lagi salah melaporkan "Variabel belum didefinisikan" untuk destructuring.
- **Transpiler default parameters**: `fungsi sapa(nama, umur=0)` sebelumnya ditranspile menjadi `def sapa(nama, umur)` tanpa default value — sekarang default parameters diteruskan dengan benar (fungsi & generator).
- **Transpiler**: dukungan pipeline, destructuring, dan keyword arguments.

### Changed
- Versi di-bump dari `5.0.0` ke `5.2.0`.

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
