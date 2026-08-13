# Changelog

Semua perubahan penting pada BroLang akan didokumentasikan di file ini.

Format berdasarkan [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [7.2.0] - 2026-08-13

### Added — Fitur Bahasa Baru

- **List/dict/set comprehension** — sintaks `lalu` kini bekerja di semua
  konteks koleksi:
  ```bro
  buat kuadrat = [x * x lalu x dalam data]
  buat genap = {k: v lalu k dalam data jika k % 2 == 0}   # dict-comp
  buat unik = {x lalu x dalam daftar}                      # set-comp
  ```
  (Sebelumnya list-comp rusak/no-op di VM; dict & set-comp baru didukung.)
- **Walrus operator** `x := nilai` — assignment di dalam ekspresi/kondisi
  (sebelumnya rusak di VM):
  ```bro
  jika (buat_hasil := kirim()) != kosong { ... }
  ```
- **Null-safe indexing** `data?[0]` — mengembalikan `kosong` bila target
  kosong, mirror dari `a?.b` untuk atribut.
- **Dict comprehension** — `{k: v lalu k dalam sumber}` (dengan guard
  `jika`) sebagai ekspresi bernilai di semua mesin.

### Fixed — Konsistensi VM (semua sudah jalan di interpreter/transpiler)

- **Generator di VM** — `hasilkan`/`hasilkandari` (sebelumnya di-skip
  diam-diam): fungsi ber-yield dideteksi otomatis dari body, hasil
  dikumpulkan dan dikembalikan sebagai list.
- **`dengan` statement di VM** — konteks manager (`masuk`/`keluar`) kini
  dipanggil benar; mendukung objek BroLang (`obj.masuk()`) maupun Python
  (`.masuk`/`.keluar` atau `__enter__`/`__exit__`).
- **`dengan` di interpreter** — method konteks pada instance BroLang
  (`obj.get("masuk")`) kini dipanggil dengan `self` yang benar (bug
  pre-existing: `hasattr` gagal pada `BroLangInstance`).

### Added — Perluasan Library (v7.2)

- **`waktu`** — `waktu_iso()`, `timestamp()`, `milidetik()`, `zona_waktu()`,
  `dari_timestamp(ts)`, `hari_ini()`, `tambah_hari(tgl, n)`, `umur(tgl_lahir)`,
  `selisih_waktu(a, b)`, `detik_sejak(epoch)`.
- **`file`** — utilitas jalur (`gabung_jalur`, `absolute`, `nama_dasar`,
  `folder`, `ekstensi`), biner (`baca_biner`, `tulis_biner`, `salin_biner`),
  plus `ubah_nama`, `ubah_waktu`.
- **`dasar`** — koleksi: `urutkan`, `terbalik`, `unik`, `kunci`, `nilai`,
  `item`, `panjang`, `adalah_kosong`.
- **`acak`** — `pilih`, `pilih_beberapa`, `kocok`, `unik`, `kata`, `huruf`,
  `huruf_besar`, `antara`, `koin`, `dadu`.

### Fixed — Konsistensi Lintas Mesin (audit otomatis 73 fitur)

Audit otomatis (`tools/audit_konsistensi.py`) menjalankan 73 snippet fitur
bahasa di ketiga mesin (interpreter/transpiler/VM) dan membandingkan output.
Bug yang ditemukan & diperbaiki:

- **Slicing string & list** (`s[1:3]`, `a[::2]`) rusak di transpiler (di-emit
  sebagai string `"1 : 3"`) dan di VM (hanya PUSH_NONE placeholder). Kini
  slicing asli `target[start:stop:step]` di kedua mesin.
- **Method list/dict/str di VM** — `tambah`, `sisipkan`, `urutkan`, `balik`,
  `kunci`, `nilai`, `item`, `punya`, `ambil`, dll tidak dikenal di VM
  (hanya `VMInstance` yang didukung). Kini diterjemahkan ke method Python
  via `_vm_brolang_method` (konsisten dengan interpreter).
- **`d.kunci()`/`d.nilai()` di transpiler** — mengembalikan `dict_keys`/
  `dict_values` (view) bukan list; kini dibungkus `list()`.
- **`a.urutkan()` di transpiler** — mengembalikan `None` (Python `sort()`);
  kini mengembalikan list terurut (konsisten dengan interpreter).
- **Closure di VM** — variabel fungsi enclosing tidak terlihat (compiler
  tidak pernah mengisi `free_vars`; `_resolve_name` hanya tahu local/global).
  Kini scope enclosing dilacak dan `LOAD_DEREF` memakai slot lokal parent.
- **Multiple return unpack** — `buat a, b, c = f()` (satu tuple) gagal di
  interpreter (`(1,2,3) None None`) dan di VM; kini di-unpack otomatis ke
  target di ketiga mesin.
- **Index assignment dict** `d[kunci] = nilai` ditolak interpreter
  ("Hanya list yang bisa di-index assignment"); kini dict didukung
  (konsisten dengan transpiler/VM).
- **Urutan kunci dict di VM** — `MAKE_DICT` membalik urutan pasangan;
  kini dipertahankan.

### Notes

- 32 test baru di `tests/unit/test_v72_language.py` — total **1205 test passing**.
- Dokumentasi: `docs/FITUR_V72.md`, contoh `examples/fitur_v72.bro`,
  audit `tools/audit_konsistensi.py` (73 fitur, 69 konsisten).

## [7.1.0] - 2026-08-13

### Added — Perluasan Library

Modul stdlib yang sudah ada diperluas dengan fungsi-fungsi baru (tanpa
perubahan sintaks bahasa, versi tetap 7.1.0):

- **`matematika`** — statistik (`rata_rata`, `median`, `modus`, `varians`,
  `standar_deviasi`), teori bilangan (`fpb`, `kpk`, `prima`,
  `bilangan_prima`, `fibonacci`), utilitas (`maksimal`/`minimal` multi-arg,
  `clamp`, `hipotenusa`, konversi sudut, `kombinasi`, `permutasi`),
  plus `log2`/`log10`.
- **`teks`** — `balik`, `berulang`, `hapus_spasi`, `pad_kiri`/`pad_kanan`,
  `terpusat`, `jumlah`, `hitung_kata`, `pecah_baris`, dan regex
  (`regex_cari`, `regex_cari_semua`, `regex_ganti`, `regex_cocok`).
- **`tanggal`** — `nama_hari`, `nama_bulan` (Indonesia), `kabisat`,
  `akhir_bulan`, `tambah_bulan`, `tambah_tahun`, `selisih_jam`,
  `tanggal_baru`.
- **`acak`** — `boolean`, `huruf`, `huruf_besar`, `kata`, `antara`.
- **`angka`** — `genap`, `ganjil`, `fpb`, `kpk`, `prima`, `angka_prima`,
  `fibonacci`, `digit`, `jumlah_digit`, `terbalik`, konversi basis
  (`ke_biner`/`dari_biner`, `ke_oktal`/`dari_oktal`, `ke_heksa`/`dari_heksa`).
- **`dasar`** — `ke_angka`, `ke_teks`, `ke_boolean`, `jenis`, `panjang`,
  `kosong`.
- **`file`** — `salin`, `pindah`, `hapus_folder`, `nama_dasar`, `folder`,
  `ekstensi`, `gabung_jalur`, `absolute`.
- **`json`** — `valid`.
- **`jaringan`** — `muat`, `kirim_json`, `status`, `ip_local`, `hostname`.
- **`sistem`** — `jumlah_cpu`, `memori`, `memori_total`, `memori_bebas`,
  `arsitektur`.
- **`proses`** — `proses_id`, `jalankan_list` (tanpa shell, lebih aman).
- **`catat`** — `catat`, `sukses`, `level_saat_ini`.
- **Alias aman-keyword** — fungsi stdlib yang namanya bentrok dengan keyword
  bahasa tidak bisa dipanggil dari BroLang (`tulis`, `hapus`, `buat`,
  `tunggu`, `harusnya`). Kini tersedia alias: `file.tulis_file`/
  `file.hapus_file`, `json.tulis_file`, `csv.tulis_file`,
  `sejajar.tunggu_tugas`, `antrian.buat_antrian`, `tumpukan.buat_tumpukan`,
  `lingkungan.hapus_var`, `tes.harus`.
- **Fix import di transpiler** — `impor json`/`impor csv` dulu mengambil
  modul Python stdlib dengan nama sama (yang tidak punya fungsi BroLang);
  kini modul stdlib BroLang dicoba lebih dulu, fallback ke Python bila
  tidak ada.

### Added — Perluasan Modul Game

- **`fisika`** — `vektor_dari_sudut(sudut, panjang)` (buat vektor dari
  sudut radian + panjang), `gravitasi_bumi()` / `gravitasi_bulan()`
  (konstanta gravitasi standar dalam skala pixel).
- **`sprite`** — `Sprite`: `set_fps_animasi`, `daftar_animasi`, `cek_titik`,
  `di_dalam_bounds`, `arah_ke`, `jarak_ke`, `ke_awal`, `set_skala`,
  `set_rotasi`, `visibel`/`set_visibel`/`tampilkan`/`sembunyikan`,
  `ikuti_patroli`/`berhenti_patroli`/`patroli_aktif`, `rotasi_ke_titik`;
  `GrupSprite`: `hapus_tidak_aktif`, `apakah_kosong`, `kosongkan`,
  `dapatkan_semua`, `pertama` (plus alias Python `kosong`).
- **`ui`** — helper warna level modul: `warna(r, g, b, a)`, `warna_hex(kode)`,
  `acak_warna()`; `Label` kini punya `set_ukuran` & `set_warna`.
- **`visualisasi`** — `tabel(data)` (tabel ASCII berbingkai; menerima list of
  dict / list of list / dict tunggal, opsi `nomor` & `judul`), `tabel_svg(data)`
  (tabel HTML responsif beraksen warna), `area_svg(data)` (chart area dengan
  gradasi transparan; mendukung multi-seri, sumbu X kustom, legend).

### Fixed — VM & Transpiler (bug lama yang menghalangi modul game)

- **Keyword-argumen (`f(a, b=1)`) kini bekerja di VM** — sebelumnya
  compiler mendorong nilai kwargs tanpa dict nama (stack rusak) dan
  `_call_function` hanya memanggil `f(*args)`. Kini kwargs dibungkus
  marker `_vm_kwargs` (dict + nama) dan diikat berdasarkan nama
  parameter — untuk fungsi BroLang, method, maupun fungsi/modul Python.
- **Default parameter (`fungsi f(a, b=10)`) kini bekerja di VM** —
  sebelumnya nilai default didorong ke stack tanpa pernah dipakai (bug
  sejak awal; opcode `MAKE_FUNCTION` tidak terpakai). Kini `MAKE_FUNCTION`
  menggabungkan closure + daftar default, dan pemanggilan mengisi
  parameter yang tidak diberikan dengan default-nya.
- **Transpiler: method stdlib asli tidak lagi di-map ke method Python** —
  `grup.kosongkan()` (method `GrupSprite`) dulu diterjemahkan jadi
  `grup.clear()` yang tidak ada. Kini dipanggil method BroLang asli bila
  ada, fallback ke method Python (`list.clear`) bila tidak.

### Docs

- `docs/STDLIB.md`: bagian `matematika`, `teks`, `tanggal`, `acak`, `angka`,
  `dasar`, `file`, `json`, `jaringan`, `sistem`, `proses`, `catat` +
  Module List diperbarui; duplikat bagian `angka` dihapus.
- `docs/GAME.md`: bagian `fisika` (helper v7.1), `sprite` (metode baru),
  `ui` (helper warna), `visualisasi` (tabel & area).

### Notes

- 83 test baru (`tests/unit/test_v71_library.py`) + 14 test game
  (`tests/unit/test_visualisasi.py`) — total **1173 test passing**.

## [7.0.0] - 2026-08-12

### Added — Fitur Bahasa Modern

- **Multiple assignment** — deklarasi & reassignment berpasangan:
  ```bro
  buat a, b = 1, 2        # deklarasi ganda
  a, b = b, a             # swap (nilai kanan dievaluasi dulu, jadi aman)
  buat x, y, z = 1, 2, 3
  ```
  Bisa di dalam fungsi; nilai kanan yang kurang mengisi target dengan `kosong`.
- **Switch expression** — `cocokkan` kini bisa jadi ekspresi bernilai:
  ```bro
  buat status = cocokkan kode {
      1: "satu",
      2: "dua",
      _: "lainnya"          # default
  }
  ```
  Mendukung pola literal, binding (`{ "x": a, "y": b }: a + b`), dan wildcard.
- **Error propagation `?`** — buka Result/Option tanpa boilerplate:
  ```bro
  fungsi cari(id)
      kembali Benar("ditemukan") jika id == 1
      kembali Salah("tidak ada")
  selesai

  buat hasil = cari(1)?     # Benar(v)  -> v
  # Salah(e)? -> lempar e | Ada(v)? -> v | Kosong()? -> lempar error
  ```
  Nilai biasa (bukan Result/Option) diteruskan apa adanya (no-op).

### Added — Async/Await Sejati

`asinkron fungsi` kini benar-benar asinkron: pemanggilan mengembalikan
objek **`Tugas`** yang berjalan di background thread (daemon), dan
`tunggu` memblokir sampai selesai:

```bro
asinkron fungsi muat(url)
    event_loop.tidur(0.1)              # IO simulasi — tidak memblokir task lain
    kembali "data dari " + url
selesai

buat a = muat("api/1")
buat b = muat("api/2")
buat hasil = tunggu a                 # blokir sampai a selesai
tulis event_loop.tunggu_semua([a, b]) # tunggu semua → list hasil
```

- Eksekusi body task di-serialisasi dengan lock (interpreter tidak
  thread-safe) dan berjalan di **sub-interpreter terpisah** — program
  utama tidak terganggu, dan task dalam task (`tunggu` di dalam async)
  tidak deadlock (lock dilepas sambil menunggu).
- Modul stdlib baru **`event_loop`**: `tidur(detik)` (kooperatif — task
  lain maju saat tidur), `tunggu_semua([...])`, `tunggu_apa_saja([...])`,
  `jalankan(fn, ...)`, kelas `Tugas`.
- API `Tugas`: `selesai()` (tanpa blokir), `hasil(timeout=None)`,
  `tunggu(timeout=None)`, `batal()`.

### Fixed — VM Bytecode

- **try/catch di VM benar-benar bekerja** (bug pre-existing): `TRY_PUSH`
  hanya menaruh marker di stack tanpa pernah dipakai — exception menerobos
  keluar dan mematikan program. Kini `_execute` melakukan exception
  routing: stack dipotong sampai handler teratas, nilai exception didorong
  untuk di-bind `catch_var`, eksekusi lanjut dari handler (mendukung
  handler bertingkat).
- **`coba/tangkap` & `coba/kecuali` kini dikompilasi di VM** (sebelumnya
  `MultiExceptNode` di-skip diam-diam): klausa ber-tipe dicocokkan lewat
  `_vm_jenis` (cocok dengan nama tipe + subkelas), tidak cocok → re-raise.
- **`Kosong()` (Option) bisa diparse** — keyword `Kosong` terdaftar di
  lexer (sebelumnya `Ada(v)` berfungsi tapi `Kosong()` jatuh ke
  "fungsi tidak ditemukan").
- **`a, b = 1, 2` & `?` didukung VM** — `MultiAssignNode` (store terbalik
  agar swap aman) dan `ErrorPropagationNode` (helper `_vm_propagate`,
  aman untuk nilai primitif seperti `7?`).
- **`impor` di VM diperbaiki** — `_emit_import` memakai `.module` (bukan
  `.parts` yang tidak pernah ada), jadi `impor event_loop` berfungsi.
- **Switch expression didukung VM** — `cocokkan x { pola: ekspresi }`
  bernilai via `_vm_switch_match` + binding pola.
- **`asinkron fungsi` didukung VM & transpiler** — VM mengeksekusi body
  sinkron lalu membungkus hasil dalam objek `Tugas` (API konsisten);
  transpiler menjalankan body di background thread (helper
  `_brolang_async_run`) dengan hasil identik interpreter.
- **Escape string di transpiler** — `\n`/`\t`/`\r`/`\0` kini ditulis ulang
  dengan benar (dulu jadi newline literal → SyntaxError).
- **Panggilan fungsi modul stdlib di VM** — fungsi polos pada objek modul
  (`event_loop.tidur(d)`) tidak lagi dioper `obj` berlebih (regresi
  `method(obj, *args)` untuk callable non-bound).
- **Pola enum di `cocokkan` bisa diparse (bug lama)** — `Warna.MERAH` dulu
  gagal parse (identifier dianggap binding lalu token `.` ditolak); kini
  member access diparse sebagai ekspresi, termasuk guard
  (`Warna.HIJAU jika c`). Didukung interpreter, transpiler, dan VM.
- **`cocokkan` statement didukung VM** (sebelumnya di-skip diam-diam) —
  pola terstruktur (dict binding), literal/ekspresi, guard, dan default;
  `enum` & `struktur` di VM diperbaiki (`node.members`/`node.fields`,
  `__init__` otomatis + `__repr__`).

### Notes

- 60 test baru (`tests/unit/test_v70_language.py`) — total **1075 test passing**.
- Dokumentasi: `docs/FITUR_V70.md`, contoh `examples/fitur_v70.bro`.

## [6.9.0] - 2026-08-12

### Added — Guard Clause untuk Semua Statement

Guard clause (v6.8) diperluas dari `kembali`/`hentikan`/`lanjutkan` ke
**semua statement sederhana** — statement hanya dijalankan saat kondisi
benar:

```bro
fungsi cek(x)
    tulis x jika x > 0            # print bersyarat
    kembali x * 2 jika x > 0      # early return ber-guard (v6.8)
selesai

buat skor = 0
skor = 100 jika benar            # reassignment bersyarat
skor += 10 jika menang           # augmented bersyarat

kelas Akun
    fungsi beri_bonus(self, n)
        self.bonus += n jika n > 0   # atribut objek ber-guard
        kembali self.bonus
    selesai
selesai

buat data = [1, 2, 3]
data[1] += 10 jika benar          # index list ber-guard

lempar "stok habis" jika stok <= 0   # raise bersyarat
log(pesan) jika mode_debug           # panggilan fungsi bersyarat
hapus cache jika basi                # delete bersyarat

fungsi gen()
    hasilkan v jika v > 0            # yield bersyarat di generator
selesai
```

Statement yang didukung: `tulis`, `buat` (deklarasi + destructuring),
reassignment (`x = v`), augmented (`x += v`), atribut objek
(`self.x = v`), index list (`data[i] += v`), `lempar`, `hapus`,
pemanggilan fungsi, dan `hasilkan`/`hasilkandari`. Bekerja di dalam loop,
blok `jika`, dan single-line block.

- **Tidak ambigu dengan ternary** — `a jika b lainnya c` tetap ternary
  (`buat x = 5 jika benar lainnya 99` → `5`), `a jika b` di akhir
  statement adalah guard. Ternary di dalam kurung/panggilan tetap normal.
- **Nilai tidak dievaluasi saat guard salah** — konsisten di
  interpreter, transpiler, dan VM.
- **Desain**: statement ber-guard dibungkus menjadi `jika` biasa di level
  AST, sehingga semua mesin mendukungnya tanpa perubahan tambahan.

### Fixed — VM

- **Kompilasi ternary di bytecode VM rusak** — `_emit_expr(TernaryNode)`
  mengakses `node.body`/`node.else_body` (field yang tidak ada) sehingga
  `buat x = a jika b lainnya c` melempar `AttributeError` di `bro build`.
  Kini memakai `true_value`/`false_value` dan hasil konsisten dengan
  interpreter & transpiler.

### Fixed (pasca-rilis)

- **`hasilkandari` (yield from) di interpreter hanya menghasilkan elemen
  pertama** — `visit_YieldFromNode` memakai
  `for item in items: raise YieldException(item)`; raise pertama
  menghentikan loop sehingga elemen sisanya tidak pernah terlempar
  (terlihat saat `hasilkandari` berada di dalam blok `jika`/guard). Kini
  semua item ditambahkan langsung ke koleksi generator aktif (tracking
  `_active_generator`), dan eksekusi blok di sekitarnya tetap berlanjut
  — konsisten dengan transpiler (`yield from` Python).
- **Yield di dalam blok `jika`/guard memotong sisa blok** — `_collect_if`
  baru menangani statement if/elif/else per-statement seperti loop,
  sehingga `hasilkan` berurutan di dalam blok if kini semuanya dikoleksi
  (sebelumnya hanya yield pertama yang tercapai).
- **Yield di dalam blok `coba`/`tangkap` salah atau error** — `hasilkan`
  melempar `YieldException`, dan `visit_TryNode` menangkap `except
  Exception`, sehingga yield di dalam blok try (1) menghentikan blok dan
  memicu handler catch (output `[99]` alih-alih `[1, 2]`), atau (2) error
  runtime bila yield hanya ada di handler `tangkap` (fungsi tidak
  terdeteksi sebagai generator karena `_has_yield_in_body` tidak
  menjangkau `catch_body`). Kini `visit_YieldNode` menambahkan nilai
  langsung ke koleksi generator aktif (konsisten dengan `hasilkandari`),
  dan `_has_yield_in_body` menjangkau semua sub-block:
  `catch_body`/`finally_body` (TryNode), `elif_bodies` (IfNode),
  `except_clauses` (MultiExceptNode), dan `cases`/`default_case`
  (MatchNode/SwitchNode). Hasil konsisten dengan transpiler — mis.
  `coba: hasilkan 1, hasilkan 2, lempar; tangkap: hasilkan 99` →
  `[1, 2, 99]`, yield di `tangkap` → `[7, 8]`.

### Notes

- 47 test baru (`tests/unit/test_v69_language.py`) + 14 test regresi generator
  (`tests/unit/test_v5_language.py`) — total **1015 test passing**.
- Dokumentasi: `docs/FITUR_V69.md`, contoh `examples/fitur_v69.bro`.

## [6.8.0] - 2026-08-12

### Added — Fitur Bahasa Baru

- **Guard clause** — `kembali`, `hentikan`, dan `lanjutkan` kini bisa
  diberi kondisi: statement hanya dijalankan saat kondisi benar.
  ```bro
  fungsi cek(x)
      kembali "negatif" jika x < 0     # early return ber-guard
      kembali "nol" jika x == 0
      kembali "positif"
  selesai

  untuk i dari 1 sampai 10 lakukan
      lanjutkan jika i % 2 == 0         # skip genap
      hentikan jika i > 5               # break bersyarat
      tulis i
  selesai
  ```
  - `kembali jika x` (tanpa nilai) juga didukung.
  - Tidak ambigu dengan ternary: `kembali a jika b lainnya c` tetap
    ternary, `kembali a jika b` adalah guard.
- **Floor division `//`** — pembagian yang membulatkan ke bawah:
  `17 // 5` → `3`, `-17 // 5` → `-4`, `17.5 // 5` → `3.0`, plus operator
  augmented `//=` (`x //= 3`). Bekerja di interpreter, transpiler, VM
  bytecode, dan compiler lama (`bro build`).
- **Augmented assignment pada atribut & index** — `self.x += 1`,
  `data[i] += 10`, `skor[i] //= 2` kini berfungsi di ketiga mesin
  (sebelumnya: interpreter menolak dengan error, VM menimbun stack).

### Fixed — VM Bytecode

- **`x %= y` dan `x **= y` diam-diam rusak di VM** — compiler tidak
  punya opcode `AUG_MOD`/`AUG_POW`, sehingga `x %= y` dieksekusi sebagai
  `x = y`. Kini kedua opcode ditambahkan dan hasil konsisten dengan
  interpreter & transpiler.
- **Loop VM memotong body setelah `hentikan`** — kompilasi body loop
  berhenti di break pertama; guard `hentikan jika x` membuat statement
  setelahnya tidak pernah jalan saat kondisi salah. Kelima loop emitter
  (while/do-until/for/range-for/for-each) kini mengumpulkan semua marker
  BREAK dan mem-patch-nya di akhir loop.
- **Transpiler guard return** — `return x if c` (Python membutuhkan
  `else`) diganti `if c: return x`.

### Added — Game Dev

- **`audio` — BGM prosedural** (tanpa file eksternal):
  - `buat_bgm(pola, tempo, gelombang, volume)` — generator musik latar
    yang bisa di-loop; pola memakai nama not (`"C4"`, `"A#3"`, `"Bb2"`),
    frekuensi langsung, jeda (`0`), atau tuple `(nada, ketukan)`.
  - `mainkan_bgm(pola, ...)` — generate + putar sebagai musik loop
    pygame; `hentikan_bgm()` untuk menghentikan.
  - Pola siap pakai: `pola_arcade`, `pola_epik`, `pola_tenang`; helper
    `frekuensi_nada(nama)` untuk konversi nama not → Hz.

### Notes

- 55 test baru (`tests/unit/test_v68_language.py`) — total **954 test passing**.
- Dokumentasi: `docs/FITUR_V68.md`, contoh `examples/fitur_v68.bro`.

## [6.7.0] - 2026-08-12

### Added — Fitur Bahasa Baru

- **Rest parameter `...nama`** — fungsi, method, lambda, asinkron, dan
  generator kini bisa menampung sisa argumen:
  ```bro
  fungsi jumlahkan(...angka)
      buat total = 0
      untuk setiap n dalam angka lakukan
          total = total + n
      selesai
      kembali total
  selesai
  tulis jumlahkan(1, 2, 3, 4, 5)   # 15
  ```
  Bisa digabung dengan parameter biasa (`fungsi sapa(nama, ...lain)`),
  default parameter, dan keyword args.
- **Spread call `f(...args)`** — membongkar list saat memanggil fungsi:
  `kali3(...[2, 3, 4])` → `kali3(2, 3, 4)`. Berlaku juga untuk method
  (`obj.f(...list)`).
- **Spread list `[...a, 1]`** — menggabungkan list di literal:
  `buat gabung = [...dasar, 3, 4]`.
- **Multiple return `kembali a, b`** — fungsi bisa mengembalikan beberapa
  nilai yang langsung dibongkar dengan destructuring:
  ```bro
  fungsi bagi_dan_sisa(a, b)
      kembali a / b, a % b
  selesai
  buat [hasil, sisa] = bagi_dan_sisa(17, 5)   # 3.4, 2
  ```

### Changed — Bytecode VM kini lengkap

Fitur yang sebelumnya `NotImplementedError` / diam-diam dilewati di VM
bytecode (`bro build` / `bro benchmark --vm`) sekarang berfungsi penuh dan
konsisten dengan interpreter & transpiler:
- **Range for** (`untuk i dari A sampai B langkah S`) — inklusif, step
  default otomatis naik/turun, guard step 0.
- **Destructuring assignment** (`buat [a, b] = list` / `buat {x, y} = objek`)
  — opcode `DICT_GET` baru untuk unpack objek yang aman (kunci hilang → `kosong`).
- **Pipeline operator** (`nilai |> f`) — termasuk `peta`/`saring`/`kurangi`
  dan `f(nilai, args...)`.
- **For-each** (`untuk setiap item dalam iterable`) — dengan counter indeks
  manual saat `index_variable` dipakai.
- **Rest parameter di VM** — `rest_pos` di `CLOSURE`/`VMFunction`/method
  kelas, dan rest param didaftarkan sebagai local (sebelumnya nama yang
  bentrok dengan builtin, mis. `angka`, salah di-resolve).
- **`untuk setiap` di SemanticAnalyzer** — `visit_ForEachNode` baru, sehingga
  `bro run` tidak lagi error untuk program yang memakai for-each.

### Added — Game Dev

- **`efek.Guncangan` — screen shake**: model trauma (trauma berkurang
exponensial), `guncang(kekuatan)`, `offset()` per-frame (noise terarah
acak), `update(dt)`, `set_redaman` — testable tanpa pygame.
- **`audio` — synth procedural** (tanpa file eksternal, murni stdlib):
  `nada(frekuensi, durasi)` (sine fade in/out), `laser()` (sweep turun),
  `ledakan()` (noise + low-pass), `blip()` (square pendek) — semuanya
  mengembalikan bytes WAV yang siap disimpan/dimainkan.

### Fixed

- Optimizer `visit_FunctionNode` kehilangan `rest_param`/`param_types`/
  `return_type` saat rekonstruksi node — kini dipertahankan.
- Compiler VM method non-static dengan rest param: `total_params`/`rest_pos`
  kini dihitung dari slot local yang sebenarnya (`self._get_local_idx`),
  benar meski method menulis `self` eksplisit di daftar parameter.
- **Compiler VM: assignment `obj.atribut = value` / `lst[i] = v`** — value
  sebelumnya di-emit **dua kali** (`_emit_assignment` + `_get_assign_name`)
  dan sisa `STORE_ATTR` menumpuk di stack, sehingga loop `untuk setiap` di
  sekitar assignment (mis. `self.total = self.total + n` di dalam method
  dengan rest param) crash `FOR_ITER: 'int' object is not an iterator`.
  Kini value di-eval sekali dan stack dibersihkan setelah store.
- Compiler VM `_emit_for_each`: cleanup local hanya menghapus slot yang
  benar-benar ditambahkan loop (bukan jumlah tetap) — aman bila nama
  variabel loop sudah ada sebagai local/param dari luar.
- Compiler VM `_emit_range_for`: guard `langkah 0` sekarang benar-benar
  meng-raise error ramah (sebelumnya hanya komentar, runtime jatuh ke
  `ValueError` Python yang terbungkus).

### Notes

- 59 test baru (`tests/unit/test_v67_language.py`) — total **899 test passing**.
- Dokumentasi: `docs/FITUR_V67.md`.

## [6.6.0] - 2026-08-09

### Added — 2 Modul Baru

- **`jalur` — Pathfinding & Gerakan AI**: `cari_jalur(peta, mulai, tujuan)`
  (algoritma A* di grid tile), konversi tile→pixel, kelas `IkutiJalur`
  (mengikuti polyline, bisa loop) dan `Patroli` (mode `loop` / `bolak-balik` /
  `sekali`) untuk NPC & musuh.
- **`efek` — Efek Layar & Teks Melayang**: `Flash` (overlay layar penuh yang
  memudar), `Vignette` (pinggiran gelap), `TeksMelayang` (damage number naik
  lalu pudar), dan `Pulsa` (denyut sinus 0..1).
- **Parser: tuple destructuring `buat (x, y) = tikus.posisi()`** — sebelumnya
  hanya didokumentasikan tapi tidak diimplementasikan. Sekarang bekerja di
  interpreter, transpiler, compiler package, dan VM.

### Changed — Upgrade Modul Game Dev

- **`fisika`**: mode collider persegi (`set_persegi`), resolve campuran
  lingkaran/persegi, `raycast`, `cari_bodi_di_area`.
- **`partikel`**: gradien warna seumur hidup (`warna_awal`/`warna_akhir`),
  `gambar_tekstur`, emiter bantu `buat_trail`, `buat_asap`, `buat_bintang`.
- **`tilemap`**: tile animasi (`atur_animasi`), layer objek (`tambah_objek`,
  `cari_objek`, `hapus_objek`), `cek_lantai`.
- **`kamera`**: `set_lerp`, parallax (`screen_parallax`), deadzone follow
  (`set_target` dengan `deadzone`).
- **`game`**: `atur_fisika` (fixed timestep anti spiral-of-death),
  `tangkap_layar` (screenshot), `atur_ukuran_jendela` (resize runtime).
- **`grafis`**: `gradien_vertikal`/`gradien_horizontal`, `glow_lingkaran`,
  `tulis_teks` dengan alignment `tengah`/`kanan`, `gambar_gambar_alpha`.
- **`ui`**: `Tooltip`, `DaftarSkor` (highscore JSON), `navigasi_fokus`
  (navigasi keyboard), `Tombol` dengan gambar.
- **`sprite`**: `ikuti_patroli`, `rotasi_ke_titik`, `tampilkan`/`sembunyikan`.

### Fixed (pasca-rilis)

- **`fisika` — bodi statis (massa 0) di semua mode collider**: `resolve_collision`
  kini menangani lantai/tembok statis untuk persegi, lingkaran, dan campuran.
  Pemain/bola berhenti di lantai (`grounded = benar`), bodi statis tidak ikut
  bergeser, dan tidak ada `ZeroDivisionError` (sebelumnya lingkaran vs lingkaran
  statis langsung crash; lingkaran vs persegi statis menimbulkan jitter
  osilasi ±6.7 px/dtk yang tidak pernah berhenti).
- **`fisika` — impulse lingkaran-lingkaran dinamis**: guard pendeteksi arah
  mendekat/menjauh sebelumnya terbalik (`dvn > 0` = menjauh padahal normal
  menunjuk bodi1→bodi2), sehingga tabrakan kepala-ke-kepala dua lingkaran
  dinamis tidak pernah memindahkan momentum. Kini impulse standar diterapkan
  saat mendekat (`dvn > 0`).
- **`fisika` — urutan argumen `resolve_collision`**: bodi statis boleh jadi
  argumen pertama atau kedua, hasil tetap sama (sebelumnya hanya bekerja pada
  satu urutan tertentu).
- **`ui.Tombol`**: atribut `gambar` (v6.6) menimpa method `gambar()` sehingga
  tombol tidak bisa di-render — gambar latar kini disimpan di `gambar_latar`.
- **`kamera.set_target`**: menerima `Bodi` fisika (punya `.posisi` bukan `.x`)
  tanpa error "object has no attribute 'x'".
- **`game_v66.bro`**: tambah lantai fisika statis + `resolve_collision` +
  `check_bounds`; update tilemap/partikel dipindah ke `update_utama` agar FPS
  naik (24 → 36+).
- +4 test regresi lingkaran-statis (rest di atas, urutan argumen, impulse
  dinamis, pantulan samping) → total **838 test passing**.

### Notes

- Contoh lengkap: `examples/game_v66.bro`. Dokumentasi: `docs/GAME_V66.md`.
- 838 test passing.

## [6.5.0] - 2026-08-09

### Added
- **`konstanta` — variabel immutable**: nilai tidak bisa diubah setelah
  deklarasi. Reassignment (`PI = 3`) dan augmented assignment (`PI += 1`)
  ditolak dengan error ramah. Mendukung anotasi tipe
  (`konstanta umur: Angka = 25`) dan scope fungsi. Penegakan **dua lapis**
  (konsisten dengan type system v6.0): SemanticAnalyzer menolak statis
  (jadi `bro run` ikut menolak) + Interpreter menolak runtime.
- **`ulangi ... sampai` — do-until loop**: body dijalankan **minimal satu
  kali**, lalu kondisi dicek di akhir. Berhenti saat kondisi `benar`.
  Mendukung `hentikan`/`lanjutkan`, loop bersarang, dan generator.
  Konversi transpiler: `while True: body; if kond: break`.
- **`untuk i dari A sampai B` — range-based for loop** (inklusif):
  - `untuk i dari 1 sampai 10 lakukan ... selesai` → 1..10
  - `untuk i dari 3 sampai 1` → turun otomatis (3, 2, 1)
  - `untuk i dari 0 sampai 20 langkah 5` → 0, 5, 10, 15, 20
  - `untuk i dari 10 sampai 2 langkah -2` → 10, 8, 6, 4, 2
  - Else clause (`lainnya`) saat loop selesai normal, batas boleh ekspresi
  - `langkah 0` → error ramah; ekspresi start/end/step dievaluasi sekali
- **REPL**: blok `ulangi ... sampai` kini dikenali (multi-line) dengan
  `sampai kondisi` menutup blok.
- **LSP**: `konstanta` didukung go-to-definition / symbol declaration.
- **Saran pemula**: `const` → `konstanta`, `do` → `ulangi`,
  `until` → `sampai`, `range` → `dari ... sampai`.
- **Contoh baru**: `examples/fitur_bahasa.bro` dan docs `docs/FITUR_V65.md`
  (semua contoh tervalidasi lewat `bro run`).
- **`bro doc dasar` & `bro doc variabel`**: contoh konstanta, do-until,
  dan range for.

### Fixed
- **Bug dokumentasi**: `untuk i dari 1 sampai 100` (disebut di `bro doc`
  sejak v6.4) ternyata **belum pernah diimplementasikan** — keyword
  `sampai`/`langkah` tidak ada di lexer. Kini berfungsi penuh.
- **Optimizer**: `visit_AssignmentNode` kini mempertahankan `type_annotation`
  dan `is_const` (sebelumnya keduanya hilang setelah optimasi).

### Changed
- Versi di-bump dari `6.4.0` ke `6.5.0`.
- `langkah` sengaja menjadi **soft keyword** — hanya dikenali dalam konteks
  `untuk i dari A sampai B langkah S` — supaya program lama yang memakai
  `langkah` sebagai nama variabel/kelas tetap valid.
- 43 test baru (konstanta, do-until, range for, konsistensi
  interpreter↔transpiler, CLI) — total **747 test passing**.

## [6.4.0] - 2026-08-08

### Added
- **Modul `kripto` — Keamanan & Kriptografi** (hashlib/base64/secrets, tanpa
  dependency eksternal):
  - Hash hex: `md5`, `sha1`, `sha256`, `sha512`.
  - Base64: `base64_encode` / `base64_decode`.
  - Password aman: `hash_password` (PBKDF2-SHA256 + salt acak, format
    `pbkdf2_sha256$salt$hash`) dan `cek_password` (constant-time).
  - Token crypto-grade: `token(panjang)` & `bilangan_acak(batas)`.
- **Modul `arsip` — ZIP & Kompresi** (zipfile/zlib/base64, tanpa dependency):
  - ZIP: `buat_zip`, `tambah_ke_zip`, `ekstrak_zip`, `daftar_zip`.
  - Kompresi teks: `kompres` (zlib level 9 + Base64) & `dekompres`.
- **Modul `terminal` — UX CLI** (murni stdlib Python):
  - Warna ANSI: `merah`, `hijau`, `kuning`, `biru`, `magenta`, `cyan`,
    `putih`, `abu`, `warna(teks, nama)`.
  - Gaya teks: `tebal`, `miring`, `garis_bawah`, `terbalik`.
  - Pesan status: `sukses`, `info`, `peringatan`, `gagal`.
  - Progress bar: `bilah_progress` (string) & `cetak_progress` (inline \r).
  - Prompt interaktif: `tanya` (dengan default) & `tanya_ya`.
  - `banner(teks)` untuk header program.
- **Tooling CLI**:
  - `bro test --nama <filter>` — hanya jalankan file tes yang namanya
    mengandung filter; `bro test --detail` — status ✓/✗ + durasi per file;
    ringkasan total kini menyertakan waktu eksekusi.
  - `bro upgrade` — update BroLang dari GitHub (git pull + pip install -e),
    dengan validasi folder instalasi.
  - `bro doc` — topik baru: `kripto`, `arsip`, `terminal`, `web`.
- **Contoh baru**: `examples/kripto.bro`, `examples/arsip.bro`,
  `examples/terminal.bro`.

### Changed
- Versi di-bump dari `6.3.0` ke `6.4.0`.
- 26 test baru (kripto, arsip, terminal, CLI v6.4, proteksi zip-slip) — total **704 test passing**.

## [6.3.0] - 2026-08-08

### Added
- **Performance boost** (3 lapis optimasi + benchmark publik):
  - **Peephole optimizer di bytecode VM** (`apply_peephole`) — constant folding
    (`2 + 3 * 4` dikompilasi jadi satu konstanta), removal NOP, dan remap jump
    otomatis. Berlaku juga untuk body fungsi, method kelas/struct, dan lambda.
  - **Method cache di VM** — pencarian method di inheritance chain di-cache per
    (kelas, nama) dan di-invalidate saat monkey-patch; mempercepat pemanggilan
    method pada inheritance yang dalam.
  - **Fast path interpreter** — operator biner pada operan primitif tidak lagi
    mengecek operator overloading (hanya di-cek bila ada instance kelas BroLang).
  - **Benchmark suite publik** (`benchmarks/`): `fibonacci.bro`, `loop.bro`,
    `string.bro`, `objek.bro` — dijalankan dengan `bro benchmark <file> --repeat N`.
  - Docs baru `docs/PERFORMANCE.md` berisi arsitektur eksekusi, optimasi, dan
    benchmark resmi (transpiler 11x-151x lebih cepat dari VM per kasus).
- **Tooling proyek modern**:
  - `bro init <nama>` (alias `bro new`) — scaffolding proyek lengkap:
    `brolang.json` (manifest), `src/main.bro`, `tests/test_utama.bro`,
    `docs/README.md`, `README.md`, dan `.gitignore`.
  - `bro run` **tanpa argumen** — membaca `brolang.json` di folder proyek dan
    menjalankan entry point (`main`); error ramah bila tidak ada proyek.
- **Web framework** (modul baru `web_server`):
  - Server HTTP berbasis stdlib Python (tanpa dependency eksternal).
  - Routing metode + jalur: `app.rute("GET", "/", handler)` + shorthand
    `app.get` / `app.post` / `app.put` / `app.hapus`.
  - Parameter dinamis `/pengguna/{id}`, query string otomatis, body JSON otomatis
    untuk POST/PUT.
  - Helper response: `req.kirim_teks`, `kirim_json`, `kirim_html`, `kirim_status`,
    `kirim_file` (static files + MIME type).
  - `app.jalankan(port)` (blocking) dan `app.jalankan_async(port)` (thread) +
    `app.berhenti()`; CORS opsional via `app.atur_cors(benar)`.
  - Contoh lengkap: `examples/web_api.bro` (API CRUD + halaman HTML).

### Fixed
- **Lexer: string multi-baris & f-string multi-baris tidak pernah berfungsi**
  (bug offset deteksi triple-quote `"""`). Kini `"""..."""` dan
  `f"""...{expr}..."""` berfungsi dengan benar.
- **VM: binding parameter method class** — method non-static multi-parameter
  error "slot belum diinisialisasi"; kini `param_count` menghitung `self`.
- **Interpreter: lookup fungsi antar-scope** — fungsi yang direferensikan dari dalam
  fungsi lain (mis. callback) kini ditemukan via parent env (sebelumnya error
  "variabel tidak ditemukan").
- **CLI: exit code** — `python -m brolang.cli` kini `sys.exit(main())` sehingga
  exit code benar (mis. `bro run` di folder non-proyek mengembalikan 1).

### Changed
- Versi di-bump dari `6.2.0` ke `6.3.0`.
- 24 test baru (peephole, method cache, multi-line string, tooling, web_server) —
  total **678 test passing**.

## [6.2.0] - 2026-08-08

### Added
- **Scene Lifecycle lengkap** (modul `game`):
  - Scene kini punya siklus hidup penuh — callback `on_masuk` (dipanggil sekali saat scene aktif) dan `on_keluar` (saat scene diganti), cocok untuk setup/cleanup asset.
  - `tambah_scene(nama, update, gambar, on_masuk=..., on_keluar=...)` — kompatibel dengan API lama (parameter baru opsional).
- **Transisi antar scene** — pindah scene dengan efek fade:
  - `ganti_scene(nama, transisi="fade", durasi=0.5, warna="hitam")` — scene lama memudar ke warna, lalu scene baru muncul.
  - `transisi_aktif()` cek status, `progres_transisi()` (0.0..1.0) untuk animasi paralel.
  - Scene berganti tepat di titik paling gelap (tengah durasi) — transisi digambar sebagai overlay di atas scene aktif.
- **Tumpukan Scene / Overlay** — `dorong_scene(nama, ...)` / `pop_scene(...)`:
  - Tumpuk scene di atas scene lain — scene bawah **tetap digambar** tapi tidak di-update; sempurna untuk menu pause / dialog di atas gameplay.
  - `kedalaman_tumpukan()` untuk cek jumlah scene bertumpuk; `reset()` kini membersihkan tumpukan & transisi.
- **UI komponen baru** (modul `ui`):
  - **`KotakTeks`** — input teks satu baris: fokus via klik, kursor berkedip, placeholder, `maks_karakter`, `tambah_karakter`/`hapus_karakter`/`kosongkan`/`set_teks`, callback `on_ubah`/`on_fokus`/`on_keluar_fokus`.
  - **`Slider`** — slider horizontal dengan drag mouse: `nilai_sekarang`/`atur_nilai`/`persen`, opsi `langkah` (kelipatan), callback `on_ubah`/`on_selesai`.
  - **`KotakCentang`** — checkbox dengan label: `centang`/`hapus_centang`/`toggle`/`dicentang_sekarang`, callback `on_centang`/`on_hapus`/`on_ubah`.
  - **`DaftarPilih`** — dropdown: `buka`/`tutup`/`pilih`/`indeks_terpilih`/`opsi_terpilih`, hover item, auto-tutup setelah pilih, callback `on_ubah`/`on_buka`/`on_tutup`.
  - Semua komponen baru bersifat deklaratif — **logika berjalan tanpa pygame** (hanya render yang butuh pygame), konsisten dengan komponen lama.
- **5 modul stdlib baru** (dijanjikan `docs/STDLIB.md` tapi sebelumnya tidak ada — kini lengkap):
  - **`angka`** — matematika lanjut: `pi`/`e` sebagai nilai, `sqr`, `abs`, `min`/`max` (2+ angka atau satu list), `lantai`/`langit`/`bulat`, `pangkat`, `log`, `sin`/`cos`/`tan`, `faktorial`, `acak_antara`.
  - **`sistem`** — info sistem: `versi()` (versi BroLang), `platform()` (linux/windows/darwin), `nama`, `versi_os`, `prosesor`, `python`, `hostname`, `cwd`, `home`, `lingkungan`.
  - **`sistem_operasi`** — operasi OS: `list_dir`, `daftar_file`/`daftar_folder`, `ada`/`adalah_file`/`adalah_folder`, `buat_folder`, `hapus_file`/`hapus_folder`, `pindah`/`salin`, `ukuran`, `cwd`/`ganti_cwd`, manipulasi jalur (`nama_dasar`, `folder_induk`, `ekstensi`, `gabung_jalur`, `jalur_absolut`, `ubah_ekstensi`, dll).
  - **`web`** — HTTP client: `get`/`post`/`put`/`hapus_http`/`kirim` → objek respon (`teks`, `status`, `json`, `header`, `sukses`, `error`).
  - **`database`** — SQLite wrapper: `buka`/`buka_memori`, `eksekusi_sql` (param `?`), `query` → list objek, `query_satu`/`query_nilai`, `eksekusi_banyak`, `tabel`, `kolom`, `jumlah_baris`, `tutup`.
  - Nama fungsi yang tabrakan keyword BroLang dihindari: `eksekusi` → `eksekusi_sql`, `hapus` (DELETE) → `hapus_http`.

### Changed
- Versi di-bump dari `6.1.0` ke `6.2.0`.
- Game loop (`mulai()`) kini memproses transisi scene tiap frame dan menggambar overlay fade di paling atas.
- `docs/STDLIB.md` kini mendokumentasikan API asli semua modul (termasuk 5 modul baru yang sebelumnya hanya dijanjikan).
- 79 test baru (43 game dev + 36 modul stdlib baru) — total **654 test passing**.

## [6.1.0] - 2026-08-07

### Added
- **Mode Belajar `bro belajar`** 🎓 — tutorial interaktif untuk pemula & pelajar Indonesia:
  - 8 bab bertingkat: Halo Dunia → Variabel → Matematika → Percabangan → Perulangan → List → Fungsi → Proyek Mini Kalkulator
  - Materi singkat per bab + latihan soal yang **dicek otomatis** (dijalankan di interpreter, output dibandingkan)
  - Nilai akhir + pesan motivasi, perintah `petunjuk` / `jawaban` / `lewati` / `bantuan` / `keluar`
  - Perintah diproses langsung tanpa perlu baris kosong
- **Pesan error ramah pemula**:
  - Saran keyword Inggris → Indonesia: `print` → "mungkin maksudmu 'tulis'?", `null` → 'kosong', `def` → 'fungsi', `if` → 'jika', dll. (module `brolang/suggestions.py`, dipakai lexer/parser/analyzer/interpreter)
  - Hint `jika x = 5 maka` → "pakai '==' untuk membandingkan" (juga di `selama`)
  - Hint titik koma: "BroLang tidak memakai titik koma ';'"
- **REPL ditingkatkan** (ramah pemula):
  - Blok multi-baris (`jika ... maka`, `fungsi ...`) kini berfungsi benar — kedalaman blok dilacak dan dieksekusi otomatis saat `selesai`; blok kurung kurawal (`cocokkan ... {`, `enum`, `struktur`, literal objek multi-baris) ditutup otomatis oleh `}`
  - Deteksi blok presisi (token pertama/terakhir): variabel seperti `fungsiku = 5` tidak lagi memicu mode multi-baris, `selesai # komentar` tetap dihitung menutup blok
  - Ketik `keluar`/`batal` di tengah blok multi-baris = batalkan blok (tidak lagi menelan perintah)
  - Hasil ekspresi ditampilkan: `2 + 3` → `=> 5` (state variabel bertahan antar input)
  - Perintah `bantuan` (daftar fungsi + contoh), `tips`, `contoh`, `riwayat`, `bersih`
  - Pesan sambutan berisi contoh yang bisa dicoba + tip acak tiap 5 input
- **Anti-hang di mode belajar**: jawaban yang berjalan terlalu lama (mis. `selama true lakukan ... selesai` atau `waktu.tidur(30)`) dihentikan otomatis setelah 5 detik dengan pesan ramah — sesi belajar tidak bisa menggantung.

### Changed
- Versi di-bump dari `6.0.0` ke `6.1.0`.
- REPL kini memakai interpreter sebagai sumber state tunggal (sebelumnya campur transpiler/interpreter sehingga state tidak konsisten dan ekspresi tidak menampilkan hasil).
- 39 test baru (mode belajar, saran keyword, hint pemula, REPL) — total **575 test passing**.

## [6.0.0] - 2026-08-07

### Added
- **Type System lengkap** — anotasi tipe di variabel, parameter, dan return value:
  - `buat umur: Angka = 25`, `fungsi kali2(a: Angka) -> Angka`
  - Union type: `Angka | Teks` · Generik: `Daftar<Angka>` · Alias: `tipe ID = Angka`
  - Kelas user bisa dipakai sebagai tipe parameter (`fungsi info(m: Mobil)`)
  - Tipe bawaan: `Angka`, `Desimal`, `Teks`, `Boolean`, `Daftar`, `Objek`, `Tupel`, `Set`, `Kosong`, `ApaSaja`
  - **Enforcement dua lapis**: interpreter menolak mismatch saat runtime **dan** SemanticAnalyzer menolak mismatch statis (sehingga `bro run` ikut menolak `buat umur: Angka = "salah"`).
- **Pattern Matching Modern** — `cocokkan` kini punya pola destructuring:
  - Pola list: `[a, b]: ...` (bind elemen) · Pola objek: `{"nama": n, "umur": u}: ...`
  - Binding: `n: ...` (tangkap seluruh nilai) · Guard: `x jika x > 10: ...`
  - Konsisten di **interpreter** dan **transpiler** (binding via walrus `:=`).
- **Error Handling Profesional** — custom error class:
  - `kelas_error SaldoTidakCukup extends Kesalahan ... selesai` — kelas error dengan field sendiri
  - Hierarki error: `kecuali Induk sebagai e` menangkap turunannya
  - `kecuali lainnya sebagai e` sebagai fallback · `Kesalahan` tersedia sebagai kelas dasar bawaan
  - Konsisten di **interpreter** dan **transpiler** (`class Nama(Kesalahan)`)
  - **CLI error display profesional**: `bro run` menampilkan file/baris/kolom, baris sumber dengan penanda `^`, pesan + solusi, dan stack trace (v6.0).
- **Ekosistem Stdlib** — 6 modul baru:
  - `tanggal`: parse/format tanggal Indonesia, `selisih_hari`, `tambah_hari`, `komponen`, `parse`
  - `catat`: logging ber-level (`info`/`error`/...), `atur_level`, `atur_file`
  - `lingkungan`: env vars — `get`/`set`/`ada`/`hapus`
  - `proses`: jalankan subprocess — `jalankan(cmd)` → objek `hasil` (`keluaran`, `kode`)
  - `csv`: baca/tulis CSV — `baca(path)` → list objek, `tulis(path, data)`
  - `registri`: **package registry online** — server HTTP (`jalankan_async`) + publish/install/cari via `PackageManager`
- **SemanticAnalyzer v6.0**: dukungan `KelasErrorNode`, binding pattern match, dan cek anotasi tipe statis — semua fitur v6.0 jalan di pipeline penuh `bro run` (analyzer → optimizer → transpiler).

### Fixed
- **Parser**: fungsi yang dinamai keyword reserved (`fungsi cetak(...)` lalu `cetak(...)`) kini bisa dipanggil di statement level (sebelumnya "Token tidak terduga: 'cetak'").
- **Transpiler match pattern list**: binding `[a, b]` menghasilkan `NameError: b` karena precedence `and`/`or` Python men-short-circuit binding kedua — setiap kondisi binding kini dibungkus tanda kurung.
- **SemanticAnalyzer indexing**: `objek["kunci"]` (dict string-key) kini diterima — sebelumnya `bro run` menolak dengan "Indeks harus berupa angka" padahal interpreter mengizinkannya; index pada tipe tak dikenal juga tidak lagi false-positive.
- **SemanticAnalyzer type alias**: `tipe ID = Angka` tidak lagi salah lapor "Variabel 'Angka' belum didefinisikan" — nama tipe di definisi alias bukan variabel runtime.
- **Dokumentasi**: `docs/FITUR_V60.md` baru — panduan lengkap type system, pattern matching modern, kelas_error, stdlib baru, dan package registry online (semua contoh tervalidasi lewat `bro run`).

### Changed
- Versi di-bump dari `5.5.0` ke `6.0.0`.
- **Breaking**: pola identifier di `cocokkan` kini menjadi **binding** (`n: ...` menangkap nilai, selalu cocok) — di v5.x pola identifier dibandingkan sebagai nilai (`nilai == n`). Program lama yang memakai identifier sebagai pola perbandingan perlu diganti dengan literal/ekspresi.
- 45 test baru (type system, pattern matching modern, error handling, stdlib, package registry, pipeline CLI) — total **536 test passing**.

## [5.5.0] - 2026-08-07

### Added
- **Operator Overloading** — kelas BroLang kini bisa mendefinisikan perilaku operator sendiri:
  - Aritmatika: `_tambah_` (+), `_kurang_` (-), `_kali_` (*), `_bagi_` (/), `_modulo_` (%), `_pangkat_` (**)
  - Perbandingan: `_sama_` (==), `_tidak_sama_` (!=), `_kurang_dari_` (<), `_lebih_dari_` (>), `_kurang_sama_` (<=), `_lebih_sama_` (>=)
  - Unary: `_negasi_` (-), `_positif_` (+), `_bukan_` (bukan)
  - Lainnya: `_dalam_` (dalam), `_teks_` (konversi string/print), `_panjang_` (panjang()), `_index_`/`_index_set_` ([] / [] =)
  - Konsisten di **interpreter** dan **transpiler** (`_tambah_` → `__add__` Python), fallback `!=` = negasi `_sama_`.
- **Modul `sejajar` (baru) — Threading/Parallel**: jalankan fungsi di background thread supaya game loop/program tetap responsif.
  - `sejajar.jalankan(fungsi, *args)` → objek `Tugas` (`selesai()`, `hasil()`, `batal()`)
  - `sejajar.tunggu(tugas)` / `sejajar.tunggu_semua([...])` / `sejajar.peta_sejajar(fungsi, iterable)`
  - `sejajar.atur_thread(n)` / `sejajar.jumlah_thread()`
  - Aman: fungsi BroLang di-serialisasi otomatis (interpreter tidak thread-safe); callable Python murni jalan benar-benar paralel.
- **LSP upgrade** — auto-completion jauh lebih pintar:
  - Completion keyword + **semua builtin** + **simbol dokumen** (variabel/fungsi/kelas/modul impor) + **member setelah titik** (fungsi modul stdlib asli)
  - **Go-to-definition** beneran: lompat ke baris deklarasi variabel/fungsi/kelas
  - **Hover**: keyword/simbol/builtin/modul dengan info tipe & baris deklarasi
- **Parser**: assignment ke index `d[1] = 99` sekarang didukung (sebelumnya "Token tidak terduga '='") — dibutuhkan oleh `_index_set_`.

### Changed
- Versi di-bump dari `5.4.0` ke `5.5.0`.
- 16 test baru (operator overloading, sejajar, LSP) — total **491 test passing**.

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
