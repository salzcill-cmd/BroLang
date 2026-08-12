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
  item (sebelumnya hanya elemen pertama), dan yield di dalam blok `jika`
  tidak lagi memotong sisa statement blok

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

__version__ = "6.9.0"
__author__ = "BroLang Team"
__license__ = "MIT"

from brolang.exceptions import BroLangError
