"""
BroLang - Bahasa Pemrograman Profesional untuk Game Development
================================================

BroLang adalah bahasa pemrograman modern yang dirancang untuk:
- Kemudahan belajar dengan sintaks Bahasa Indonesia
- Arsitektur profesional dan scalable
- Cocok untuk pendidikan dan produksi
- Game development dengan fitur lengkap

Filosofi:
    "Belajar coding harus semudah membaca bahasa manusia."

Fitur v6.9 (Fitur Bahasa):
- Guard clause diperluas ke SEMUA statement sederhana: `tulis x jika c`,
  `buat x = v jika c`, `x = 99 jika c`, `x += 5 jika c`, `self.x = v jika c`,
  `data[i] += v jika c`, `lempar e jika c`, `hapus x jika c`, `f() jika c`,
  `hasilkan x jika c` — statement hanya dijalankan saat kondisi benar
- Tidak ambigu dengan ternary: `a jika b lainnya c` tetap ternary
- Nilai statement tidak dievaluasi saat guard salah (konsisten antar mesin)
- Perbaikan VM: kompilasi ternary (TernaryNode) kini benar di bytecode VM
- Perbaikan generator: `hasilkandari` (yield from) kini menghasilkan SEMUA
  item (sebelumnya hanya elemen pertama), yield di dalam blok `jika`
  tidak lagi memotong sisa statement blok, dan yield di dalam blok
  `coba`/`tangkap`/`akhirnya` kini berfungsi & konsisten dengan transpiler
  (sebelumnya yield di try memicu handler catch; yield hanya di `tangkap`
  error karena fungsi tidak terdeteksi sebagai generator)

Fitur v8.1 (Game Dev Upgrade):
- `kumpulan_objek` — object pooling: gunakan ulang bullet/partikel/musuh
  (hindari lag GC); callback fungsi/lambda BroLang kini bisa dipanggil dari
  kode Python stdlib di VM (`VMFunction.__call__`)
- `simpan_game` — simpan/muat progres game ke JSON: slot save, checkpoint,
  auto-save, metadata (waktu/label/versi), daftar, info
- `dialog` — sistem dialog RPG: efek mesin ketik, nama pembicara, pilihan
  bercabang (branching choices), callback on_selesai
- `ai` — AI musuh: FSM (mesin status) + steering behaviors murni matematika
  (kejar/lari/tiba/jelajah/hindari) + kelas Agen siap pakai
- `tilemap` — platform satu arah (mendarat saat jatuh, tembus saat lompat)
  & platform bergerak bolak-balik yang bisa membawa pemain (`dorong_bodi`)
- `misi` — quest & achievement: Misi (progres/status), Pencapaian,
  ManajerMisi dengan simpan/muat status (JSON-safe)
- Perbaikan parser: `obj.hapus(...)` kini valid (kata kunci `hapus` di
  posisi nama atribut) — mis. `simpan_game.hapus`, `file.hapus`

Fitur v8.0 (Fitur Bahasa Modern + Performa VM):
- Spread objek: `{...a, "b": 1}` — campur spread dengan pasangan kunci-nilai
  dalam urutan apa pun; kunci item belakang menimpa item depan (konsisten
  interpreter/transpiler/VM, urutan sumber dipertahankan via `order`)
- Null-coalescing assignment: `x ??= v`, `self.x ??= v`, `d[i] ??= v` —
  hanya diisi bila nilai saat ini kosong; nilai kanan TIDAK dievaluasi
  saat tidak perlu (short-circuit)
- `kecuali (TipeA, TipeB) sebagai e` — multi-tipe exception (cocok bila
  salah satu tipe cocok; selain itu re-raise) — konsisten di ketiga mesin
- Perbaikan VM: `kelas_error` kustom kini berfungsi penuh di VM —
  `lempar ValidasiGagal("x")` + `kecuali ValidasiGagal` (termasuk hierarki
  induk, `e.pesan`) konsisten dengan interpreter & transpiler (sebelumnya
  deklarasi kelas error dibuang diam-diam di VM)
- Performa VM: fast path `_execute` tanpa try/except bila bytecode tak punya
  handler; alokasi frame sesuai `local_count` (bukan selalu 64); fast path
  `_call_function` (tanpa kwargs/default/rest); LOAD_GLOBAL satu dict op +
  tanpa invalidasi cache per STORE_GLOBAL — Fibonacci ~15% lebih cepat

Fitur v7.2.1 (Konsistensi Output Object):
- `tulis k.x` (method object) → `<method K.x>` di interpreter/transpiler/VM
  (sebelumnya repr masing-masing berisi alamat memori acak)
- `tulis gen(3)` (generator) → `[1, 2, 3]` di ketiga mesin (sebelumnya
  interpreter/transpiler mengembalikan objek generator, hanya VM yang list)

Fitur v7.2 (Fitur Bahasa + Konsistensi VM + Library):
- List/dict/set comprehension: `[x lalu x dalam data]`, `{k: v lalu ...}`, `{x lalu ...}`
  (sebelumnya list-comp rusak/no-op di VM; dict & set-comp kini didukung semua mesin)
- Walrus operator: `x := nilai` di ekspresi & kondisi (sebelumnya rusak di VM)
- Generator di VM: `hasilkan`/`hasilkandari` (sebelumnya no-op di VM)
- `dengan` statement di VM: konteks manager `masuk`/`keluar` (sebelumnya di-skip VM)
- Null-safe indexing: `data?[0]` -> `kosong` jika target kosong (mirror `a?.b`)
- Library diperluas: `waktu` (waktu_iso, timestamp, umur, selisih), `file` (jalur_*,
  baca_biner/tulis_biner, ukuran_file), `dasar` (urutkan, balikkan, gabung,
  unik, gabungkan, bentuk_objek, kunci_objek, nilai_objek, salin), `acak` (pilih,
  acak_huruf, acak_hex, acak_suku_kata)

Fitur v7.0 (Fitur Bahasa Modern + Async + Perbaikan VM):
- Multiple assignment: `a, b = 1, 2`, swap `a, b = b, a`, `buat a, b = ...`
- Switch expression: `cocokkan nilai { pola: ekspresi }` sebagai ekspresi bernilai
- Error propagation `?`: buka Result (Benar/Salah) & Option (Ada/Kosong), lempar error otomatis
- Async/Await sejati: `asinkron fungsi` -> Tugas background thread, `tunggu` memblokir,
  modul stdlib baru `event_loop` (tidur kooperatif, tunggu_semua, tunggu_apa_saja)
- Perbaikan VM: try/catch kini benar-benar bekerja (exception routing), `coba/kecuali`
  ber-tipe didukung, `Kosong()` (Option) kini bisa diparse

Fitur v6.8 (Fitur Bahasa + Bug Fix + Game Dev):
- Guard clause: `kembali x jika c`, `hentikan jika c`, `lanjutkan jika c`
- Floor division: `//` dan `//=` (17 // 5 = 3, -17 // 5 = -4)
- Augmented assignment pada atribut & index: `self.x += 1`, `data[i] //= 2`
- Perbaikan VM: `%=` dan `**=` (sebelumnya diam-diam menjadi `x = y`)
- BGM prosedural di `audio`: `buat_bgm`/`mainkan_bgm` + pola siap pakai (arcade/epik/tenang)

Fitur v6.7 (Fitur Bahasa + Bug Fix + Game Dev):
- Rest parameter: `fungsi f(a, ...sisa)` + spread call `f(...args)` + spread list `[...a, 1]`
- Multiple return: `kembali a, b` (destructuring otomatis)
- Bytecode VM kini mendukung range-for, destructuring, pipeline, for-each (sebelumnya NotImplementedError / silent skip)
- Efek baru `Guncangan` (screen shake) + synth audio procedural di `audio` (nada/laser/ledakan tanpa file eksternal)

Fitur v6.6 (Upgrade Game Dev):
- Modul baru `jalur` (pathfinding A* + patroli waypoint)
- Modul baru `efek` (flash, vignette, teks melayang, pulsa)
- Fisika AABB (persegi), raycast, query area
- Partikel gradien warna + emiter trail/asap/bintang
- Tilemap tile animasi + layer objek
- Kamera parallax + deadzone follow
- Game fixed timestep + screenshot
- UI Tooltip, DaftarSkor, navigasi fokus

Fitur v6.5 (Fitur Bahasa):
- Konstanta: variabel immutable `konstanta PI = 3.14`
- Do-until loop: `ulangi ... sampai kondisi` (body jalan minimal sekali)
- Range for loop: `untuk i dari 1 sampai 10 langkah 2` (inklusif)

Fitur v6.2 (Game Dev Upgrade):
- Scene lifecycle: on_masuk/on_keluar + transisi fade antar scene
- Tumpukan scene (overlay): dorong_scene/pop_scene untuk menu pause
- UI baru: KotakTeks (input teks), Slider, KotakCentang, DaftarPilih

Fitur v6.0:
- Type System lengkap: `buat x: Angka = 5`, `fungsi f(a: Angka) -> Teks`,
  union (`Angka | Teks`), generik (`Daftar<Angka>`), alias tipe
- Pattern Matching Modern: pola list/objek, binding, guard
- Error Handling Profesional: `kelas_error` (custom error class)
- Ekosistem stdlib: tanggal, catat, lingkungan, proses, csv, registri
- Package Registry Online (publish/install via HTTP)

Fitur v5.0:
- Type System (tipe data dengan anotasi)
- Interfaces/Antarmuka
- Abstract Classes (kelas abstrak)
- Higher-Order Functions (peta, saring, kurangi)
- Result/Option Types (penanganan error)
- Macros (metaprogramming)
- Module System (ruang nama)
- Access Modifiers (publik, privat, terlindungi)
- Null Coalescing (??)
- Optional Chaining (?.)
- Chained Comparisons (0 < x < 10)
- For Each with Index
- 25+ modul standard library
- Sprite, Animasi, Tilemap, Kamera, Fisika

Penggunaan:
    from brolang.interpreter import Interpreter
    from brolang.lexer import Lexer
    from brolang.parser import Parser

    lexer = Lexer(source_code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    interpreter = Interpreter()
    interpreter.interpret(ast)
"""

__version__ = "8.1.0"
__author__ = "BroLang Team"
__license__ = "MIT"

from brolang.exceptions import BroLangError
